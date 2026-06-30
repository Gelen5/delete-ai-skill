---
name: delete-ai-skill
description: Turn Chinese AI-heavy drafts into more personal, less templated long-form writing for self-media, blogs, tutorials, and marketing content by combining style DNA, pre-writing constraints, and a post-write QA pass.
---

# Delete AI Skill

This skill helps users produce Chinese long-form writing that feels more personal and less templated by using:

1. a style profile derived from real writing samples
2. clear generation constraints before drafting
3. a QA pass after drafting

This skill is for self-media, blog, tutorial, and marketing writing only.

## Refuse these cases

Do not use this skill for:

- academic papers or thesis writing
- legal, medical, or government documents
- news reporting or factual impersonation
- claims of guaranteed detector bypass

## Inputs

Collect these before writing:

- writing goal: new draft or rewrite
- content topic
- target platform: WeChat, Xiaohongshu, blog, newsletter, script, other
- target reader level: beginner, general, expert
- target point of view: first person, third person, dialogue
- sample articles from the target author, if available
- style DNA file, if available

If the user wants to learn from a WeChat public account, use the workflow in `references/wechat-article-exporter-adapter.md` first.

## Workflow

### Step 1: Confirm the writing target

Clarify:

- what the content is trying to achieve
- who it is for
- what platform it will be published on
- whether the user wants a fresh draft or a rewrite

### Step 2: Build or load style DNA

If the user provides real samples:

- extract stable style signals
- summarize them into a reusable style DNA

If the user does not provide samples:

- use a scenario template from `references/scenario-templates.md`

If the user gives a WeChat public-account name:

- import markdown articles through `scripts/import_from_wechat_article_exporter.py`
- build style DNA from the exported article folder with `scripts/build_style_dna_from_folder.py`

Read the style structure in `references/style-dna-template.md`.

### Step 3: Draft with constraints before generation

Apply these constraints before writing:

- avoid mechanical outline transitions
- vary sentence length and paragraph size
- include concrete observations, not only abstractions
- keep the target author's viewpoint density
- keep the platform format in mind

### Step 4: Run QA

Read `references/humanization-qa-checklist.md` and revise the draft until it passes the checklist.

### Step 5: Deliver

Output:

- the final article
- a short note describing the chosen tone and platform fit

Do not claim guaranteed detector outcomes. If asked, say the goal is to reduce templated AI signals and strengthen personal style, but platform algorithms can change.

## Writing rules

- prefer semantic transitions over mechanical connectors
- mix short and long sentences
- add subjective judgment when appropriate
- add concrete images, examples, or actions
- keep paragraph lengths uneven
- do not overdo slang or exaggerated colloquial fillers

## Rewrite mode

When the user gives an AI-heavy draft:

1. identify repetitive transitions and flattening patterns
2. rebuild paragraph rhythm
3. replace vague abstractions with concrete detail
4. inject the target style DNA
5. run QA and revise

## Output guardrail

The skill improves style naturalness. It does not certify originality, factuality, or detector performance.
