"""Extract reviewable facts and compare old memory with current notes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol


MAX_STATEMENTS = 40


@dataclass(frozen=True)
class Statement:
    line: int
    text: str


class BatchScorer(Protocol):
    def score_many(self, pairs: list[tuple[str, str]]) -> list[dict[str, float]]: ...


def extract_statements(markdown: str) -> list[Statement]:
    statements: list[Statement] = []
    in_code = False
    for line_number, raw in enumerate(markdown.splitlines(), 1):
        text = raw.strip()
        if text.startswith("```") or text.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code or not text or text.startswith(("#", "|", ">", "<!--")):
            continue
        text = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+)", "", text)
        text = re.sub(r"^\[[ xX]\]\s+", "", text)
        text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
        text = text.replace("`", "").strip()
        if 12 <= len(text) <= 500 and any(ch.isalpha() for ch in text):
            statements.append(Statement(line_number, text))
    return statements


def compare(current: str, memory: str, scorer: BatchScorer, threshold: float = 0.70) -> dict:
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold must be between 0 and 1")
    current_lines = extract_statements(current)
    memory_lines = extract_statements(memory)
    if not current_lines or not memory_lines:
        raise ValueError("both documents need at least one factual line")
    if len(current_lines) > MAX_STATEMENTS or len(memory_lines) > MAX_STATEMENTS:
        raise ValueError(f"MVP limit: at most {MAX_STATEMENTS} factual lines per file; split large files")
    pairs = [(new.text, old.text) for old in memory_lines for new in current_lines]
    scores = scorer.score_many(pairs)
    if len(scores) != len(pairs):
        raise ValueError("model returned an unexpected number of scores")
    flags = []
    for index, result in enumerate(scores):
        if result["contradiction"] < threshold or result["contradiction"] <= result["entailment"]:
            continue
        old = memory_lines[index // len(current_lines)]
        new = current_lines[index % len(current_lines)]
        flags.append({
            "memory_line": old.line,
            "memory_text": old.text,
            "current_line": new.line,
            "current_text": new.text,
            "contradiction_signal": round(result["contradiction"], 4),
            "verdict": "possible_conflict_review_required",
        })
    flags.sort(key=lambda item: item["contradiction_signal"], reverse=True)
    return {
        "model": "cross-encoder/nli-MiniLM2-L6-H768",
        "checked_pairs": len(pairs),
        "possible_conflicts": flags,
        "disclaimer": "A flag is a model triage signal, not proof. Verify both documents and their dates before editing memory.",
    }
