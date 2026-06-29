#!/usr/bin/env python3
"""
Minimal style DNA extractor for Chinese long-form writing samples.

This script is intentionally lightweight for first-sale delivery.
It extracts a few stable signals and writes a JSON summary that buyers
can reuse as a style contract inside the skill workflow.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


SENTENCE_SPLIT_RE = re.compile(r"[。！？!?；;]\s*")
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")
FIRST_PERSON = ("我", "我们", "咱", "咱们")
SECOND_PERSON = ("你", "你们")
THIRD_PERSON = ("他", "她", "他们", "她们", "它", "它们")
COLLOQUIAL_MARKERS = ("其实", "真的", "说实话", "吧", "呢", "啊", "哈", "啦")
EMOJI_MARKERS = ("😀", "😂", "🤣", "😊", "😅", "👍", "🔥", "✨", "😭", "💡", "[笑]", "[哭]")
QUESTION_MARKERS = ("？", "?")
EXCLAMATION_MARKERS = ("！", "!")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stddev(values: list[float]) -> float:
    if not values:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((v - avg) ** 2 for v in values) / len(values))


def count_occurrences(text: str, variants: tuple[str, ...]) -> int:
    return sum(text.count(item) for item in variants)


def detect_level(score: float, low: float, high: float) -> str:
    if score < low:
        return "low"
    if score < high:
        return "medium"
    return "high"


def build_summary(data: dict) -> str:
    return (
        f"The author profile shows {data['surface_style']['first_person_ratio']} first-person usage, "
        f"{data['surface_style']['sentence_length_average']} average sentence length, "
        f"{data['surface_style']['sentence_length_variance']} sentence variance, "
        f"and a {data['surface_style']['colloquial_level']} colloquial level. "
        f"Paragraph rhythm is {data['surface_style']['paragraph_length_pattern']}, "
        f"reader interaction is {data['reader_interaction']['interaction_frequency']}, "
        f"and emoji usage is {data['platform_fit']['emoji_usage']}."
    )


def extract_style_dna(text: str, author_label: str) -> dict:
    clean_text = text.strip()
    paragraphs = [p.strip() for p in PARAGRAPH_SPLIT_RE.split(clean_text) if p.strip()]
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(clean_text) if s.strip()]

    sentence_lengths = [len(s) for s in sentences]
    paragraph_lengths = [len(p) for p in paragraphs]

    total_chars = max(len(clean_text), 1)
    first_person_count = count_occurrences(clean_text, FIRST_PERSON)
    second_person_count = count_occurrences(clean_text, SECOND_PERSON)
    third_person_count = count_occurrences(clean_text, THIRD_PERSON)
    colloquial_count = count_occurrences(clean_text, COLLOQUIAL_MARKERS)
    question_count = count_occurrences(clean_text, QUESTION_MARKERS)
    exclamation_count = count_occurrences(clean_text, EXCLAMATION_MARKERS)
    emoji_count = count_occurrences(clean_text, EMOJI_MARKERS)

    first_ratio = round(first_person_count / total_chars, 4)
    second_ratio = round(second_person_count / total_chars, 4)
    third_ratio = round(third_person_count / total_chars, 4)
    sentence_avg = round(mean(sentence_lengths), 2)
    sentence_var = round(stddev(sentence_lengths), 2)
    paragraph_avg = round(mean(paragraph_lengths), 2)

    if paragraph_avg < 80:
        paragraph_pattern = "short"
    elif paragraph_avg < 180:
        paragraph_pattern = "mixed"
    else:
        paragraph_pattern = "long"

    colloquial_level = detect_level(colloquial_count / max(len(sentences), 1), 0.15, 0.45)
    interaction_level = detect_level(question_count / max(len(sentences), 1), 0.05, 0.2)
    emoji_level = detect_level(emoji_count / total_chars, 0.001, 0.003)
    exclamation_level = detect_level(exclamation_count / max(len(sentences), 1), 0.03, 0.15)

    data = {
        "identity": {
            "author_label": author_label,
            "source_count": 1,
            "sample_topic_range": "unknown",
            "platform_bias": "unknown",
        },
        "surface_style": {
            "first_person_ratio": first_ratio,
            "second_person_ratio": second_ratio,
            "third_person_ratio": third_ratio,
            "sentence_length_average": sentence_avg,
            "sentence_length_variance": sentence_var,
            "paragraph_length_pattern": paragraph_pattern,
            "terminology_density": "unknown",
            "colloquial_level": colloquial_level,
        },
        "rhetorical_habits": {
            "metaphor_density": "unknown",
            "rhetorical_question_density": interaction_level,
            "contrast_usage": "unknown",
            "parallelism_usage": "unknown",
            "self_deprecation_usage": "unknown",
        },
        "emotional_curve": {
            "emotional_baseline": "unknown",
            "emotional_peak_pattern": exclamation_level,
            "intensity_shift_style": "unknown",
        },
        "structure": {
            "opening_pattern": "unknown",
            "progression_pattern": "unknown",
            "ending_pattern": "unknown",
            "transition_style": "manual_review_needed",
        },
        "cognitive_pattern": {
            "argument_mode": "manual_review_needed",
            "abstraction_level": "manual_review_needed",
            "example_usage_style": "manual_review_needed",
            "explanation_preference": "manual_review_needed",
        },
        "rhythm": {
            "short_sentence_usage": round(sum(1 for x in sentence_lengths if x <= 12) / max(len(sentence_lengths), 1), 4),
            "long_sentence_usage": round(sum(1 for x in sentence_lengths if x >= 30) / max(len(sentence_lengths), 1), 4),
            "pause_pattern": "mixed",
            "compression_vs_expansion": "mixed",
        },
        "reader_interaction": {
            "direct_reader_address": second_ratio,
            "interaction_frequency": interaction_level,
            "intimacy_level": colloquial_level,
        },
        "platform_fit": {
            "line_break_style": paragraph_pattern,
            "emoji_usage": emoji_level,
            "network_slang_usage": "manual_review_needed",
            "headline_style": "manual_review_needed",
        },
        "guardrails": {
            "banned_patterns": [],
            "overuse_warnings": [
                "manual review required for formulaic transitions",
                "manual review required for excessive abstraction",
            ],
            "must_keep_features": [],
        },
    }
    data["one_paragraph_summary"] = build_summary(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a lightweight style DNA profile from a UTF-8 text sample.")
    parser.add_argument("--input", required=True, help="Path to the input .txt or .md file")
    parser.add_argument("--output", required=True, help="Path to the output JSON file")
    parser.add_argument("--author-label", default="sample_author", help="Author label to store in JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    text = input_path.read_text(encoding="utf-8")

    result = extract_style_dna(text, args.author_label)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Style DNA written to: {output_path}")


if __name__ == "__main__":
    main()
