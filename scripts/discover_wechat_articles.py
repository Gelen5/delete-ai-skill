#!/usr/bin/env python3
"""
Discover WeChat article results by public-account name through Sogou Weixin search.

This v1 script focuses on reliable discovery:
- input a public-account name
- search article results
- filter likely matches by source name
- resolve final mp.weixin.qq.com article URLs from Sogou jump pages
- export JSON/CSV/Markdown for the downstream style workflow

Full-text extraction is handled by a separate script because article pages may
require human verification on some requests.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
SEARCH_URL = "https://weixin.sogou.com/weixin"


@dataclass
class ArticleCandidate:
    title: str
    summary: str
    source_name: str
    published_at: str | None
    sogou_link: str
    final_url: str | None
    match_score: float


def build_opener() -> urllib.request.OpenerDirector:
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ("User-Agent", USER_AGENT),
        ("Referer", "https://weixin.sogou.com/"),
    ]
    return opener


def repair_console_text(text: str) -> str:
    """
    Best-effort fix for common Windows console mojibake where UTF-8 input gets
    decoded as GBK before Python sees it.
    """
    try:
        repaired = text.encode("gbk", errors="strict").decode("utf-8", errors="strict")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    if repaired and repaired != text:
        return repaired
    return text


def normalize_name(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def source_match_score(source_name: str, target_name: str) -> float:
    source = normalize_name(source_name)
    target = normalize_name(target_name)
    if source == target:
        return 1.0
    if target and target in source:
        return 0.8
    if source and source in target:
        return 0.7
    overlap = len(set(source) & set(target))
    base = max(len(set(target)), 1)
    return round(overlap / base, 2)


def strip_tags(raw_html: str) -> str:
    text = re.sub(r"<!--.*?-->", "", raw_html, flags=re.S)
    text = re.sub(r"<.*?>", "", text, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def epoch_to_iso(epoch_text: str | None) -> str | None:
    if not epoch_text:
        return None
    try:
        return datetime.fromtimestamp(int(epoch_text), tz=timezone.utc).astimezone().isoformat()
    except ValueError:
        return None


def search_articles(opener: urllib.request.OpenerDirector, account_name: str) -> str:
    params = urllib.parse.urlencode({"type": 2, "query": account_name})
    with opener.open(f"{SEARCH_URL}?{params}", timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_candidates(search_html: str, account_name: str, max_results: int) -> list[ArticleCandidate]:
    pattern = re.compile(
        r"<li id=\"sogou_vr_11002601_box_\d+\".*?>"
        r".*?<a[^>]+href=\"(?P<link>[^\"]+)\"[^>]+id=\"sogou_vr_11002601_title_\d+\"[^>]*>(?P<title>.*?)</a>"
        r".*?<p class=\"txt-info\"[^>]*>(?P<summary>.*?)</p>"
        r".*?<span class=\"all-time-y2\">(?P<source>.*?)</span>"
        r".*?timeConvert\('(?P<epoch>\d+)'\)",
        re.S,
    )

    candidates: list[ArticleCandidate] = []
    for match in pattern.finditer(search_html):
        source_name = strip_tags(match.group("source"))
        score = source_match_score(source_name, account_name)
        candidates.append(
            ArticleCandidate(
                title=strip_tags(match.group("title")),
                summary=strip_tags(match.group("summary")),
                source_name=source_name,
                published_at=epoch_to_iso(match.group("epoch")),
                sogou_link="https://weixin.sogou.com" + html.unescape(match.group("link")),
                final_url=None,
                match_score=score,
            )
        )
        if len(candidates) >= max_results:
            break
    return candidates


def extract_final_url(jump_html: str) -> str | None:
    parts = re.findall(r"url \+= '(.*?)';", jump_html)
    if not parts:
        return None
    url = "".join(parts)
    return url or None


def resolve_final_url(opener: urllib.request.OpenerDirector, sogou_link: str) -> str | None:
    with opener.open(sogou_link, timeout=20) as response:
        jump_html = response.read().decode("utf-8", errors="ignore")
    return extract_final_url(jump_html)


def filter_best_matches(candidates: list[ArticleCandidate], allow_fuzzy: bool) -> list[ArticleCandidate]:
    exact = [item for item in candidates if item.match_score >= 1.0]
    if exact:
        return exact
    if allow_fuzzy:
        return [item for item in candidates if item.match_score >= 0.5]
    return []


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[ArticleCandidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["title", "summary", "source_name", "published_at", "sogou_link", "final_url", "match_score"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_markdown(path: Path, account_name: str, rows: list[ArticleCandidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {account_name} 文章发现结果", ""]
    for index, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## {index}. {row.title}",
                f"- 来源公众号：{row.source_name}",
                f"- 发布时间：{row.published_at or 'unknown'}",
                f"- 匹配分数：{row.match_score}",
                f"- 搜狗跳转：{row.sogou_link}",
                f"- 微信链接：{row.final_url or 'unresolved'}",
                "",
                row.summary,
                "",
            ]
        )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover WeChat articles by public-account name.")
    parser.add_argument("--account-name", help="The public-account name to search")
    parser.add_argument("--account-name-file", help="UTF-8 text file containing the public-account name")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--max-results", type=int, default=20, help="Maximum search results to parse before filtering")
    parser.add_argument("--allow-fuzzy", action="store_true", help="Keep likely fuzzy source-name matches when exact matches are absent")
    parser.add_argument("--csv-output", help="Optional CSV export path")
    parser.add_argument("--markdown-output", help="Optional Markdown export path")
    parser.add_argument("--sleep-ms", type=int, default=250, help="Delay between jump-page resolutions")
    args = parser.parse_args()

    if not args.account_name and not args.account_name_file:
        raise SystemExit("Provide either --account-name or --account-name-file.")

    if args.account_name_file:
        account_name = Path(args.account_name_file).read_text(encoding="utf-8").strip()
    else:
        account_name = repair_console_text(args.account_name or "")
    opener = build_opener()
    search_html = search_articles(opener, account_name)
    parsed = parse_candidates(search_html, account_name, args.max_results)
    matched = filter_best_matches(parsed, allow_fuzzy=args.allow_fuzzy)

    for item in matched:
        item.final_url = resolve_final_url(opener, item.sogou_link)
        time.sleep(max(args.sleep_ms, 0) / 1000)

    payload = {
        "account_name": account_name,
        "fetched_at": datetime.now().astimezone().isoformat(),
        "match_mode": "exact_or_fuzzy" if args.allow_fuzzy else "exact_only",
        "total_parsed": len(parsed),
        "matched_count": len(matched),
        "articles": [asdict(item) for item in matched],
        "notes": [
            "The script resolves final mp.weixin.qq.com URLs from Sogou jump pages.",
            "Full-text extraction may still require human verification on some article pages.",
        ],
    }

    output_path = Path(args.output)
    write_json(output_path, payload)
    print(f"Discovery JSON written to: {output_path}")

    if args.csv_output:
        csv_path = Path(args.csv_output)
        write_csv(csv_path, matched)
        print(f"CSV written to: {csv_path}")

    if args.markdown_output:
        markdown_path = Path(args.markdown_output)
        write_markdown(markdown_path, args.account_name, matched)
        print(f"Markdown written to: {markdown_path}")


if __name__ == "__main__":
    main()
