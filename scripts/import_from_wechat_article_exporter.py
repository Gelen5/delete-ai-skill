#!/usr/bin/env python3
"""
Import WeChat public-account articles through a wechat-article-exporter instance,
save them as markdown files, then build a style DNA file from the exported folder.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from build_style_dna_from_folder import collect_text
from extract_style_dna import extract_style_dna


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"


def api_get_json(base_url: str, path: str, query: dict[str, str | int], auth_key: str | None = None) -> dict:
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if auth_key:
        request.add_header("X-Auth-Key", auth_key)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8", errors="ignore"))


def api_get_text(base_url: str, path: str, query: dict[str, str | int], auth_key: str | None = None) -> str:
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if auth_key:
        request.add_header("X-Auth-Key", auth_key)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="ignore")


def normalize_name(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def source_match_score(nickname: str, alias: str, target_name: str) -> float:
    target = normalize_name(target_name)
    candidates = [normalize_name(nickname), normalize_name(alias)]
    best = 0.0
    for candidate in candidates:
        if not candidate:
            continue
        if candidate == target:
            return 1.0
        if target and target in candidate:
            best = max(best, 0.8)
        elif candidate in target:
            best = max(best, 0.7)
        else:
            overlap = len(set(candidate) & set(target))
            base = max(len(set(target)), 1)
            best = max(best, round(overlap / base, 2))
    return best


def choose_account(accounts: list[dict], account_name: str) -> dict:
    scored = sorted(
        accounts,
        key=lambda item: source_match_score(item.get("nickname", ""), item.get("alias", ""), account_name),
        reverse=True,
    )
    if not scored:
        raise RuntimeError("No account results were returned by the exporter API.")
    best = scored[0]
    score = source_match_score(best.get("nickname", ""), best.get("alias", ""), account_name)
    if score < 0.5:
        raise RuntimeError(f"No confident account match was found for '{account_name}'.")
    return best


def sanitize_filename(name: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:120] or "article"


def fetch_all_articles(base_url: str, auth_key: str, fakeid: str, batch_size: int, max_articles: int) -> list[dict]:
    articles: list[dict] = []
    begin = 0
    while len(articles) < max_articles:
        payload = api_get_json(
            base_url,
            "/api/public/v1/article",
            {"fakeid": fakeid, "begin": begin, "size": batch_size},
            auth_key=auth_key,
        )
        if payload.get("base_resp", {}).get("ret") != 0:
            raise RuntimeError(payload.get("base_resp", {}).get("err_msg", "Failed to fetch article list."))
        batch = payload.get("articles", [])
        if not batch:
            break
        articles.extend(batch)
        begin += batch_size
        if len(batch) < batch_size:
            break
    return articles[:max_articles]


def filter_articles(articles: list[dict], keyword: str | None) -> list[dict]:
    if not keyword:
        return articles
    key = keyword.lower().strip()
    return [
        item
        for item in articles
        if key in (item.get("title") or "").lower()
        or key in (item.get("author_name") or "").lower()
        or key in (item.get("digest") or "").lower()
    ]


def export_markdown_articles(base_url: str, articles: list[dict], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    for index, article in enumerate(articles, start=1):
        title = article.get("title") or f"article-{index}"
        link = article.get("link")
        if not link:
            continue
        markdown = api_get_text(
            base_url,
            "/api/public/v1/download",
            {"url": link, "format": "markdown"},
        )
        filename = f"{index:03d}-{sanitize_filename(title)}.md"
        path = output_dir / filename
        path.write_text(markdown, encoding="utf-8")
        exported.append(path)
    return exported


def build_style_dna_from_exports(export_dir: Path, output_path: Path, author_label: str) -> None:
    text, source_count = collect_text(export_dir)
    if not text.strip():
        raise RuntimeError("No markdown/text content was exported, so style DNA could not be built.")
    payload = extract_style_dna(text, author_label)
    payload["identity"]["source_count"] = source_count
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import markdown articles from a wechat-article-exporter instance and build style DNA.")
    parser.add_argument("--base-url", default="https://down.mptext.top", help="Base URL of a wechat-article-exporter instance")
    parser.add_argument("--auth-key", required=True, help="Auth key from the exporter site")
    parser.add_argument("--account-name", required=True, help="Public-account name or keyword to search")
    parser.add_argument("--keyword", help="Optional article keyword filter applied after article discovery")
    parser.add_argument("--output-dir", required=True, help="Directory to save exported markdown files")
    parser.add_argument("--style-dna-output", required=True, help="Output path for the style DNA JSON")
    parser.add_argument("--max-articles", type=int, default=30, help="Maximum number of articles to export")
    parser.add_argument("--batch-size", type=int, default=20, help="Article page size for each list request")
    parser.add_argument("--author-label", help="Author label to store in the style DNA JSON")
    parser.add_argument("--account-meta-output", help="Optional output path for the matched account JSON")
    args = parser.parse_args()

    account_payload = api_get_json(
        args.base_url,
        "/api/public/v1/account",
        {"keyword": args.account_name, "begin": 0, "size": 20},
        auth_key=args.auth_key,
    )
    if account_payload.get("base_resp", {}).get("ret") != 0:
        raise RuntimeError(account_payload.get("base_resp", {}).get("err_msg", "Failed to search account list."))

    matched_account = choose_account(account_payload.get("list", []), args.account_name)
    if args.account_meta_output:
        meta_path = Path(args.account_meta_output)
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(matched_account, ensure_ascii=False, indent=2), encoding="utf-8")

    articles = fetch_all_articles(
        args.base_url,
        auth_key=args.auth_key,
        fakeid=matched_account["fakeid"],
        batch_size=args.batch_size,
        max_articles=args.max_articles,
    )
    filtered_articles = filter_articles(articles, args.keyword)
    exported = export_markdown_articles(args.base_url, filtered_articles, Path(args.output_dir))
    if not exported:
        raise RuntimeError("No markdown files were exported.")

    build_style_dna_from_exports(
        export_dir=Path(args.output_dir),
        output_path=Path(args.style_dna_output),
        author_label=args.author_label or matched_account.get("nickname") or args.account_name,
    )

    print(f"Matched account: {matched_account.get('nickname')} ({matched_account.get('fakeid')})")
    print(f"Exported markdown files: {len(exported)}")
    print(f"Style DNA written to: {args.style_dna_output}")


if __name__ == "__main__":
    main()
