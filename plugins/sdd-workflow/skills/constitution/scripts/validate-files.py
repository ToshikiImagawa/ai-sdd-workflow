#!/usr/bin/env python3
"""
validate-files.py
Scan specification and requirement files for /constitution validate
Reduces Claude's Glob/Grep overhead by pre-scanning file structure
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Shared modules live in plugins/sdd-workflow/scripts (three levels up + scripts).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from hook_common import resolve_project_root  # noqa: E402
from env_export import rewrite_exports  # noqa: E402


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[validate-files] {message}", file=sys.stderr)


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(resolve_project_root())


def read_config(project_root: Path) -> dict:
    """Read .sdd-config.json (paths only)"""
    config_file = project_root / ".sdd-config.json"
    if not config_file.exists():
        print("ERROR: .sdd-config.json not found", file=sys.stderr)
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    directories = config.get("directories", {})
    return {
        "root": config.get("root", ".sdd"),
        "requirement": directories.get("requirement", "requirement"),
        "specification": directories.get("specification", "specification"),
    }


def sorted_matches(base: Path, pattern: str) -> list:
    """Return regular files under base matching pattern, sorted by path string"""
    matches = [str(p) for p in base.rglob(pattern) if p.is_file()]
    matches.sort()
    return matches


def write_lines(path: Path, lines: list) -> None:
    """Write lines to a file, one per line (mirrors `... > file`)"""
    content = "".join(f"{line}\n" for line in lines)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    """Main execution"""
    try:
        project_root = get_project_root()
        config = read_config(project_root)

        requirement_path = (
            project_root / config["root"] / config["requirement"]
        )
        specification_path = (
            project_root / config["root"] / config["specification"]
        )

        output_dir = project_root / config["root"] / ".cache" / "constitution"
        output_dir.mkdir(parents=True, exist_ok=True)

        requirement_files = output_dir / "requirement_files.txt"
        spec_files = output_dir / "spec_files.txt"
        design_files = output_dir / "design_files.txt"
        summary_file = output_dir / "scan_summary.json"

        # --- Phase 1: Scan requirement files ---
        log("Scanning requirement files...")
        requirement_count = 0
        if requirement_path.is_dir():
            matches = sorted_matches(requirement_path, "*.md")
            write_lines(requirement_files, matches)
            requirement_count = len(matches)
            log(f"Found {requirement_count} requirement files")
        else:
            log(f"Requirement directory not found: {requirement_path}")

        # --- Phase 2: Scan specification files ---
        log("Scanning specification files...")
        spec_count = 0
        design_count = 0
        if specification_path.is_dir():
            spec_matches = sorted_matches(specification_path, "*_spec.md")
            design_matches = sorted_matches(specification_path, "*_design.md")
            write_lines(spec_files, spec_matches)
            write_lines(design_files, design_matches)
            spec_count = len(spec_matches)
            design_count = len(design_matches)
            log(f"Found {spec_count} specification files")
            log(f"Found {design_count} design files")
        else:
            log(f"Specification directory not found: {specification_path}")

        # --- Phase 3: Generate summary ---
        summary = {
            "scanned_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "requirement_files": requirement_count,
            "spec_files": spec_count,
            "design_files": design_count,
            "total_files": requirement_count + spec_count + design_count,
        }
        summary_file.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        log(f"Summary: {summary_file.read_text(encoding='utf-8').strip()}")

        # --- Phase 4: Export to CLAUDE_ENV_FILE ---
        wrote = rewrite_exports("CONSTITUTION_", [
            f'export CONSTITUTION_CACHE_DIR="{output_dir}"',
            f'export CONSTITUTION_REQUIREMENT_FILES="{requirement_files}"',
            f'export CONSTITUTION_SPEC_FILES="{spec_files}"',
            f'export CONSTITUTION_DESIGN_FILES="{design_files}"',
            f'export CONSTITUTION_SUMMARY="{summary_file}"',
        ])
        if wrote:
            log("Environment variables exported to CLAUDE_ENV_FILE")

        log("Scan complete")
        log(f"Cache location: {output_dir}")

    except SystemExit:
        raise
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
