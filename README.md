# Delete AI Skill

`Delete AI Skill` is a sellable Codex skill package for Chinese long-form writing that helps users:

- build a reusable personal writing style profile from real samples
- generate or rewrite drafts with a more personal, less templated tone
- run a lightweight QA pass for rhythm, specificity, and tone consistency

This package is designed for self-media, blog, tutorial, and marketing content. It does not promise detector bypass results and should not be used for academic misconduct, legal documents, medical documents, or news reporting.

## What is included

- `SKILL.md`: core skill workflow
- `references/`: reusable style and QA references
- `scripts/extract_style_dna.py`: local style profile extractor
- `examples/`: starter examples for demos and onboarding
- `INSTALL.md`: buyer installation guide
- `SELLING.md`: product positioning and sales copy guidance

## Recommended use case

This package is best sold as:

- personal style writing skill
- low-AI-tone rewriting toolkit
- author-style content workflow for self-media teams

Avoid selling it as a guaranteed detector bypass product. A safer and more durable promise is:

- stronger personal tone
- less templated AI writing
- better style consistency
- faster rewriting workflow

## Quick start

1. Put the skill folder into a Codex skills directory or keep it as a reusable project package.
2. Prepare `3-10` real writing samples from the target author.
3. Run:

```powershell
python .\scripts\extract_style_dna.py --input .\examples\input-sample-1.md --output .\examples\style_dna.generated.json
```

4. Use the generated style DNA with the instructions in `SKILL.md`.

## Package structure

```text
Delete AI Skill/
|- SKILL.md
|- INSTALL.md
|- SELLING.md
|- SALES_PAGE_CN.md
|- DEMO_SCRIPT_CN.md
|- FAQ_CN.md
|- DELIVERY_CHECKLIST_CN.md
|- references/
|- scripts/
`- examples/
```

## Delivery notes

This repo is intentionally simple for first-sale delivery:

- low setup cost
- works offline for the style extraction step
- easy to zip and send to buyers
- easy to extend later into a plugin or web tool

## Chinese sales assets

For selling and onboarding in Chinese, use:

- `SALES_PAGE_CN.md`
- `DEMO_SCRIPT_CN.md`
- `FAQ_CN.md`
- `DELIVERY_CHECKLIST_CN.md`
