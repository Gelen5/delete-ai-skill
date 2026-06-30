#!/usr/bin/env python3
"""
Extract article text from a WeChat article URL or from a browser-saved HTML file.

The network path is best-effort:
- direct fetch works when the article page is publicly accessible
- if WeChat returns a captcha or verification page, the script reports it
- the fallback is to save the article page as HTML in a normal browser and pass
  that file to this script with --html-input
"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"


def fetch_html(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Referer": "https://weixin.sogou.com/"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def looks_like_captcha(page_html: str) -> bool:
    markers = [
        "wappoc_appmsgcaptcha",
        "secitptpage",
        "人机验证",
        "验证码",
        "微信公众平台",
    ]
    return any(marker in page_html for marker in markers)


def extract_meta(page_html: str, pattern: str) -> str | None:
    match = re.search(pattern, page_html, re.S)
    return html.unescape(match.group(1).strip()) if match else None


def strip_html(raw_html: str) -> str:
    text = re.sub(r"<script.*?</script>", "", raw_html, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"</div\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<.*?>", "", text, flags=re.S)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_article(page_html: str) -> dict:
    title = (
        extract_meta(page_html, r"<meta[^>]+property=\"og:title\"[^>]+content=\"([^\"]+)\"")
        or extract_meta(page_html, r"<h1[^>]*id=\"activity-name\"[^>]*>(.*?)</h1>")
        or extract_meta(page_html, r"var msg_title = '([^']*)'")
        or "untitled"
    )
    author = (
        extract_meta(page_html, r"<meta[^>]+name=\"author\"[^>]+content=\"([^\"]+)\"")
        or extract_meta(page_html, r"var nickname = htmlDecode\(\"([^\"]*)\"\)")
        or extract_meta(page_html, r"var user_name = \"([^\"]*)\"")
    )
    publish_time = (
        extract_meta(page_html, r"var ct = \"?(\d{10})\"?")
        or extract_meta(page_html, r"<meta[^>]+property=\"article:published_time\"[^>]+content=\"([^\"]+)\"")
    )
    content_html = (
        extract_meta(page_html, r"<div[^>]+id=\"js_content\"[^>]*>(.*?)</div>\s*</div>")
        or extract_meta(page_html, r"<div[^>]+id=\"js_content\"[^>]*>(.*?)</div>")
        or ""
    )
    content_text = strip_html(content_html)

    return {
        "title": title,
        "author": author,
        "publish_time": publish_time,
        "content": content_text,
    }


def write_markdown(path: Path, article: dict, source_label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {article['title']}",
        "",
        f"- 来源：{source_label}",
        f"- 作者：{article.get('author') or 'unknown'}",
        f"- 发布时间：{article.get('publish_time') or 'unknown'}",
        "",
        article["content"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract WeChat article text from a URL or browser-saved HTML.")
    parser.add_argument("--url", help="WeChat article URL")
    parser.add_argument("--html-input", help="Browser-saved HTML file path")
    parser.add_argument("--json-output", required=True, help="Output JSON path")
    parser.add_argument("--markdown-output", help="Optional Markdown output path")
    args = parser.parse_args()

    if not args.url and not args.html_input:
        raise SystemExit("Provide either --url or --html-input.")

    source_label = args.url or args.html_input
    page_html = fetch_html(args.url) if args.url else Path(args.html_input).read_text(encoding="utf-8", errors="ignore")

    payload = {
        "source": source_label,
        "fetched_at": datetime.now().astimezone().isoformat(),
        "blocked_by_verification": looks_like_captcha(page_html),
    }

    if payload["blocked_by_verification"]:
        payload["message"] = "The article page requires human verification. Open it in a normal browser, save the HTML, and rerun this script with --html-input."
    else:
        payload["article"] = extract_article(page_html)

    output_path = Path(args.json_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Article JSON written to: {output_path}")

    if args.markdown_output and not payload["blocked_by_verification"]:
        markdown_path = Path(args.markdown_output)
        write_markdown(markdown_path, payload["article"], source_label)
        print(f"Article Markdown written to: {markdown_path}")


if __name__ == "__main__":
    main()
