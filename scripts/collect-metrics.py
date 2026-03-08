#!/usr/bin/env python3
"""collect-metrics.py

Claude Code の `--output-format stream-json` (JSONL) 出力をパースし、
フェーズごとのトークン集計 JSON を標準出力に出力するユーティリティ。

Usage:
    python3 collect-metrics.py <jsonl_file>
    echo '{"type":"assistant",...}' | python3 collect-metrics.py /dev/stdin
"""

import json
import sys


def collect_metrics(jsonl_path: str) -> dict:
    input_tokens = 0
    output_tokens = 0
    cache_read_input_tokens = 0
    cache_creation_input_tokens = 0
    num_turns = 0

    cost_usd = None
    duration_ms = None
    result_num_turns = None

    with open(jsonl_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            record_type = record.get("type")

            if record_type == "assistant":
                usage = record.get("message", {}).get("usage", {})
                input_tokens += usage.get("input_tokens", 0)
                output_tokens += usage.get("output_tokens", 0)
                cache_read_input_tokens += usage.get("cache_read_input_tokens", 0)
                cache_creation_input_tokens += usage.get(
                    "cache_creation_input_tokens", 0
                )
                num_turns += 1

            elif record_type == "result":
                cost_usd = record.get("cost_usd", cost_usd)
                duration_ms = record.get("duration_ms", duration_ms)
                result_num_turns = record.get("num_turns", result_num_turns)

    total_tokens = (
        input_tokens
        + output_tokens
        + cache_read_input_tokens
        + cache_creation_input_tokens
    )

    result = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_input_tokens": cache_read_input_tokens,
        "cache_creation_input_tokens": cache_creation_input_tokens,
        "total_tokens": total_tokens,
        "num_turns": result_num_turns if result_num_turns is not None else num_turns,
        "cost_usd": cost_usd,
        "duration_ms": duration_ms,
    }

    return result


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <jsonl_file>", file=sys.stderr)
        sys.exit(1)

    jsonl_path = sys.argv[1]
    metrics = collect_metrics(jsonl_path)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
