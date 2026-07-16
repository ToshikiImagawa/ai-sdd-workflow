#!/usr/bin/env python3
"""
scan-documents.py
Scan AI-SDD documents for Front Matter presence
Used by /recommend-front-matter skill

Python port of scan-documents.sh (removes find/grep/sed/jq dependencies for
cross-platform support). Behavior, output files, cache location and exported
environment variables are kept identical to the original shell script.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Shared modules live in plugins/sdd-workflow/scripts (three levels up + scripts).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from fm_parser import has_front_matter  # noqa: E402
from naming import determine_type  # noqa: E402,F401
from doc_walker import collect_documents  # noqa: E402
from hook_common import resolve_project_root  # noqa: E402
from env_export import rewrite_exports  # noqa: E402


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[scan-documents] {message}", file=sys.stderr)


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(resolve_project_root())


def read_config(project_root: Path) -> dict:
    """Read .sdd-config.json and resolve paths with defaults"""
    config_file = project_root / ".sdd-config.json"
    if not config_file.exists():
        log("ERROR: .sdd-config.json not found")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    directories = config.get("directories") or {}
    return {
        "root": config.get("root") or ".sdd",
        "requirement": directories.get("requirement") or "requirement",
        "specification": directories.get("specification") or "specification",
        "task": directories.get("task") or "task",
        "lang": config.get("lang") or "en",
    }


def read_lines(file: Path) -> list:
    """Read file as a list of lines (without trailing newlines)"""
    try:
        with open(file, "r", encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except OSError:
        return []


def extract_title(lines: list, basename: str) -> str:
    """Extract title from the first '# ' heading, skipping Front Matter.

    Falls back to the basename when no heading is found.
    """
    has_fm, closing_index = has_front_matter(lines)
    start = closing_index + 1 if has_fm else 0

    for line in lines[start:]:
        if re.match(r"^#\s", line):
            title = re.sub(r"^#\s*", "", line)
            if title:
                return title
            break

    return basename


def export_env_vars(scan_result: Path, output_dir: Path, sdd_lang: str) -> None:
    """Export metadata to CLAUDE_ENV_FILE"""
    # SDD_LANG is not RECOMMEND_FM_-prefixed, so it is appended (not deduped)
    # each run, matching the original behavior.
    wrote = rewrite_exports("RECOMMEND_FM_", [
        f'export RECOMMEND_FM_CACHE_DIR="{output_dir}"',
        f'export RECOMMEND_FM_SCAN_RESULT="{scan_result}"',
        f'export SDD_LANG="{sdd_lang}"',
    ])
    if wrote:
        log("Environment variables exported to CLAUDE_ENV_FILE")


def main() -> None:
    """Main execution"""
    try:
        project_root = get_project_root()
        config = read_config(project_root)

        sdd_dir = project_root / config["root"]
        output_dir = sdd_dir / ".cache" / "recommend-front-matter"
        output_dir.mkdir(parents=True, exist_ok=True)

        # --- Phase 1: Scan documents ---
        log("Scanning AI-SDD documents...")
        documents = collect_documents(
            sdd_dir, config["requirement"], config["specification"], config["task"],
        )
        total_count = len(documents)
        log(f"Found {total_count} total documents")

        # --- Phase 2: Analyze documents and build JSON ---
        with_fm_count = 0
        without_fm_count = 0
        entries = []

        for file in documents:
            lines = read_lines(file)
            basename = file.name[:-3]  # strip .md
            filepath = str(file)

            has_fm, _ = has_front_matter(lines)
            if has_fm:
                with_fm_count += 1
            else:
                without_fm_count += 1

            doc_type = determine_type(
                filepath,
                basename,
                config["requirement"],
                config["specification"],
                config["task"],
            )
            title = extract_title(lines, basename)

            try:
                relative_path = str(file.relative_to(sdd_dir))
            except ValueError:
                relative_path = filepath

            entries.append(
                {
                    "path": filepath,
                    "relative_path": relative_path,
                    "basename": basename,
                    "type": doc_type,
                    "has_front_matter": has_fm,
                    "title_line": title,
                }
            )

        result = {
            "scan_timestamp": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "total_documents": total_count,
            "documents_with_front_matter": with_fm_count,
            "documents_without_front_matter": without_fm_count,
            "documents": entries,
        }

        scan_result = output_dir / "scan_result.json"
        with open(scan_result, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write("\n")

        log("Scan complete")
        log(
            f"Total: {total_count}, With Front Matter: {with_fm_count}, "
            f"Without: {without_fm_count}"
        )

        # --- Phase 3: Export to CLAUDE_ENV_FILE ---
        export_env_vars(scan_result, output_dir, config["lang"])

        log(f"Results saved to: {scan_result}")

    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
