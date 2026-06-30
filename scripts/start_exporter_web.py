#!/usr/bin/env python3
"""
Local web UI and proxy for exporting WeChat public-account articles through
wechat-article-exporter.

Why a local proxy exists:
- the upstream public API does not expose permissive CORS headers
- a browser-only page cannot call it directly from file:// or another origin
- this server makes the web page and the proxy share one local origin
"""

from __future__ import annotations

import io
import json
import tempfile
import urllib.parse
import zipfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build_style_dna_from_folder import collect_text
from extract_style_dna import extract_style_dna
from import_from_wechat_article_exporter import (
    api_get_json,
    api_get_text,
    choose_account,
    export_markdown_articles,
    fetch_all_articles,
    filter_articles,
    sanitize_filename,
    source_match_score,
)


ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"


def json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def build_style_dna_payload(markdown_items: list[dict], author_label: str) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = Path(temp_dir)
        for index, item in enumerate(markdown_items, start=1):
            name = f"{index:03d}-{sanitize_filename(item['title'])}.md"
            (folder / name).write_text(item["markdown"], encoding="utf-8")
        text, source_count = collect_text(folder)
    payload = extract_style_dna(text, author_label)
    payload["identity"]["source_count"] = source_count
    return payload


class ExporterHandler(BaseHTTPRequestHandler):
    server_version = "DeleteAISkillWeb/0.1"

    def _send_bytes(self, body: bytes, content_type: str, status: int = 200, extra_headers: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self._send_bytes(json_bytes(payload), "application/json; charset=utf-8", status=status)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _serve_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "Not found"}, status=404)
            return
        suffix = file_path.suffix.lower()
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
        }.get(suffix, "application/octet-stream")
        self._send_bytes(file_path.read_bytes(), content_type)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self._serve_file(WEB_ROOT / "index.html")
            return
        if path == "/app.js":
            self._serve_file(WEB_ROOT / "app.js")
            return
        if path == "/style.css":
            self._serve_file(WEB_ROOT / "style.css")
            return
        if path == "/api/health":
            self._send_json({"ok": True})
            return
        if path == "/api/search-account":
            try:
                base_url = query.get("base_url", ["https://down.mptext.top"])[0]
                auth_key = query.get("auth_key", [""])[0]
                account_name = query.get("account_name", [""])[0]
                if not auth_key or not account_name:
                    raise ValueError("auth_key and account_name are required")
                payload = api_get_json(
                    base_url,
                    "/api/public/v1/account",
                    {"keyword": account_name, "begin": 0, "size": 20},
                    auth_key=auth_key,
                )
                if payload.get("base_resp", {}).get("ret") != 0:
                    raise RuntimeError(payload.get("base_resp", {}).get("err_msg", "Account search failed"))
                enriched = []
                for item in payload.get("list", []):
                    enriched.append(
                        {
                            **item,
                            "match_score": source_match_score(item.get("nickname", ""), item.get("alias", ""), account_name),
                        }
                    )
                enriched.sort(key=lambda item: item["match_score"], reverse=True)
                selected = choose_account(enriched, account_name) if enriched else None
                self._send_json({"items": enriched, "selected": selected})
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=400)
            return
        if path == "/api/articles":
            try:
                base_url = query.get("base_url", ["https://down.mptext.top"])[0]
                auth_key = query.get("auth_key", [""])[0]
                fakeid = query.get("fakeid", [""])[0]
                keyword = query.get("keyword", [""])[0]
                max_articles = int(query.get("max_articles", ["30"])[0])
                if not auth_key or not fakeid:
                    raise ValueError("auth_key and fakeid are required")
                articles = fetch_all_articles(base_url, auth_key, fakeid, batch_size=20, max_articles=max_articles)
                articles = filter_articles(articles, keyword)
                self._send_json({"items": articles})
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/export-package":
            try:
                payload = self._read_json_body()
                base_url = payload.get("base_url", "https://down.mptext.top")
                selected = payload.get("articles", [])
                if not selected:
                    raise ValueError("No articles were selected")

                markdown_items: list[dict] = []
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    manifest = []
                    for index, item in enumerate(selected, start=1):
                        title = item.get("title") or f"article-{index}"
                        link = item.get("link")
                        if not link:
                            continue
                        markdown = api_get_text(
                            base_url,
                            "/api/public/v1/download",
                            {"url": link, "format": "markdown"},
                        )
                        filename = f"{index:03d}-{sanitize_filename(title)}.md"
                        zf.writestr(filename, markdown)
                        manifest.append(
                            {
                                "title": title,
                                "link": link,
                                "author_name": item.get("author_name"),
                                "update_time": item.get("update_time"),
                                "filename": filename,
                            }
                        )
                        markdown_items.append({"title": title, "markdown": markdown})

                    author_label = payload.get("author_label") or payload.get("account_name") or "wechat_account"
                    style_dna = build_style_dna_payload(markdown_items, author_label)
                    zf.writestr("style_dna.json", json.dumps(style_dna, ensure_ascii=False, indent=2))
                    zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

                filename = sanitize_filename(payload.get("account_name") or "wechat-export") + ".zip"
                self._send_bytes(
                    zip_buffer.getvalue(),
                    "application/zip",
                    extra_headers={"Content-Disposition": f'attachment; filename="{filename}"'},
                )
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"error": "Not found"}, status=404)


def main() -> None:
    host = "127.0.0.1"
    port = 8765
    server = ThreadingHTTPServer((host, port), ExporterHandler)
    print(f"Delete AI Skill exporter web is running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
