# Installation Guide

This package is designed to be easy for non-technical buyers to use.

## Option 1: Use as a project package

1. Download or unzip the package.
2. Open the folder in Codex or your local editor.
3. Read `README.md`.
4. Put your own writing samples into a local folder.
5. Run the extraction script to create a style DNA file.
6. Use the workflow in `SKILL.md`.

## Option 2: Install as a Codex skill

1. Copy this folder into your Codex skills directory.
2. Keep the folder name stable, such as `delete-ai-skill`.
3. Restart Codex if needed.
4. Invoke the skill by name or follow your local skill-loading workflow.

## Requirements

- Python `3.9+`
- UTF-8 text files for best results

## Basic command

```powershell
python .\scripts\extract_style_dna.py --input .\examples\input-sample-1.md --output .\examples\style_dna.generated.json
```

## WeChat account workflow

The current public-account import path uses `wechat-article-exporter` as the upstream source.

Use:

1. `scripts/import_from_wechat_article_exporter.py`
2. `scripts/build_style_dna_from_folder.py`

Detailed steps:

- `references/wechat-article-exporter-adapter.md`
- `BUYER_QUICKSTART_CN.md`

## Recommended buyer workflow

1. collect `3-10` real articles written by the target author
2. merge them into one UTF-8 markdown or text file
3. run the extractor
4. use the generated JSON as the style contract
5. write or rewrite with `SKILL.md`
6. check the result against `references/humanization-qa-checklist.md`

## Delivery suggestions for sellers

- ship the repo as a zip package
- include one filled example
- include one short video or screenshot walkthrough
- keep the buyer promise focused on tone, style, and workflow quality
