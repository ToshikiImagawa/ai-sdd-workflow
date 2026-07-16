#!/usr/bin/env python3
"""user-prompt-submit.py - UserPromptSubmit hook script.

Detects Vibe Coding signals (vague instructions) in the user prompt
and injects additional context prompting a vibe-detector style analysis.
Detection only; never blocks the prompt.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_common import emit_additional_context, read_stdin_json  # noqa: E402

# (label, regex) pairs based on the vibe-detector skill detection patterns
VAGUE_PATTERNS = [
    ("subjective expression", r"いい感じ|よしなに|なんとなく|それっぽく|うまいこと|うまくやって"),
    ("subjective expression", r"\bmake it (nice|work|pretty|look good)\b|\bsomehow\b"),
    ("unclear degree", r"とりあえず動|ざっくり|適当に|少し(速く|良く)|もうちょっと"),
    ("unclear degree", r"\broughly working\b|\ba bit (faster|better)\b"),
    ("ambiguous scope / implicit assumption", r"前と同じ|いつもの|例のやつ|例の(機能|あれ)|さっきの感じ"),
    ("ambiguous scope / implicit assumption", r"\bsame as (before|last time)\b|\bas usual\b|\bthe usual\b"),
    ("ambiguous priority", r"できれば|ついでに|時間があれば|余裕があれば"),
    ("ambiguous priority", r"\bif possible\b|\bwhile you're at it\b|\bwhen you have time\b"),
]


def detect_vague_expressions(prompt: str) -> list:
    matched = []
    for label, pattern in VAGUE_PATTERNS:
        m = re.search(pattern, prompt, re.IGNORECASE)
        if m:
            matched.append(f"{label}: \"{m.group(0)}\"")
    return matched


def main() -> None:
    payload = read_stdin_json()
    prompt = payload.get("prompt", "")
    if not prompt:
        return

    matched = detect_vague_expressions(prompt)
    if not matched:
        return

    findings = "\n".join(f"- {item}" for item in matched)
    emit_additional_context(
        "UserPromptSubmit",
        "[AI-SDD] Potential Vibe Coding signals detected in the user prompt:\n"
        f"{findings}\n"
        "Before implementing, follow the vibe-detector skill flow: assess the risk level, "
        "clarify ambiguous points with the user (or via the clarify skill), and check "
        "existing specifications under the SDD specification directory.",
    )


if __name__ == "__main__":
    main()
