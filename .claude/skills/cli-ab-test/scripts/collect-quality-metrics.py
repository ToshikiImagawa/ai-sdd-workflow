#!/usr/bin/env python3
"""collect-quality-metrics.py

Claude Code の `--output-format stream-json` (JSONL) 出力をパースし、
出力テキストの品質指標を JSON で標準出力に出力するユーティリティ。

Usage:
    python3 collect-quality-metrics.py <jsonl_file>
"""

import json
import re
import sys


def extract_text_from_jsonl(jsonl_path: str) -> str:
    """JSONL から type=text のエントリを抽出してテキストを結合する。"""
    texts = []
    with open(jsonl_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            if record.get("type") == "assistant":
                for block in record.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))

    return "\n".join(texts)


def compute_quality_metrics(text: str) -> dict:
    """テキストから品質指標を計算する。"""
    # セクション数: ## または ### 見出し
    section_count = len(re.findall(r"^#{2,3}\s+", text, re.MULTILINE))

    # テーブル数: |...|行のグループ数
    in_table = False
    table_count = 0
    for line in text.split("\n"):
        stripped = line.strip()
        is_table_line = stripped.startswith("|") and stripped.endswith("|")
        if is_table_line and not in_table:
            table_count += 1
            in_table = True
        elif not is_table_line:
            in_table = False

    # チェックリスト項目数
    checklist_count = len(re.findall(r"^[\s]*- \[[ xX]\]", text, re.MULTILINE))

    # 検出項目数（問題・エラー等のマーカー）
    issue_patterns = [
        r"❌",
        r"\bWARNING\b",
        r"\bERROR\b",
        r"\bError\b",
        r"問題",
        r"\bIssue\b",
        r"\bFAIL\b",
        r"不整合",
        r"違反",
    ]
    detected_issues = 0
    for pattern in issue_patterns:
        detected_issues += len(re.findall(pattern, text))

    return {
        "text_length": len(text),
        "section_count": section_count,
        "table_count": table_count,
        "checklist_count": checklist_count,
        "detected_issues": detected_issues,
    }


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <jsonl_file>", file=sys.stderr)
        sys.exit(1)

    jsonl_path = sys.argv[1]
    text = extract_text_from_jsonl(jsonl_path)
    metrics = compute_quality_metrics(text)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
