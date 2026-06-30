#!/usr/bin/env python3
"""
Build one style DNA file from a folder of extracted article markdown or text files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract_style_dna import extract_style_dna


def collect_text(folder: Path) -> tuple[str, int]:
    chunks: list[str] = []
    count = 0
    for path in sorted(folder.rglob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        chunks.append(path.read_text(encoding="utf-8", errors="ignore").strip())
        count += 1
    return "\n\n".join(chunk for chunk in chunks if chunk), count


def main() -> None:
    parser = argparse.ArgumentParser(description="Build style DNA from a folder of markdown/text article exports.")
    parser.add_argument("--input-folder", required=True, help="Folder containing .md or .txt article files")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--author-label", required=True, help="Author label to store in the JSON")
    args = parser.parse_args()

    input_folder = Path(args.input_folder)
    text, source_count = collect_text(input_folder)
    if not text.strip():
        raise SystemExit("No .md or .txt files with content were found in the input folder.")

    payload = extract_style_dna(text, args.author_label)
    payload["identity"]["source_count"] = source_count

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Folder style DNA written to: {output_path}")


if __name__ == "__main__":
    main()
