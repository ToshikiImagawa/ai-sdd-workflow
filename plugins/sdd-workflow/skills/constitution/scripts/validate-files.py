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
from fm_parser import parse_front_matter, split_front_matter  # noqa: E402


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[validate-files] {message}", file=sys.stderr)


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(resolve_project_root())


def read_config(project_root: Path) -> dict:
    """Read .sdd-config.json (paths only).

    Deliberately hard-fails when the file is absent, unlike
    hook_common.resolve_lang_and_root's lenient fallback (used by e.g.
    generate-prd/generate-spec's prepare-*.py). Those commands proceed with a
    working default layout when the config is missing; this one exists
    specifically to validate that the project's setup is correct, so silently
    assuming defaults here would hide the very misconfiguration `/constitution
    validate` is meant to surface.
    """
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


def read_front_matter(path: Path) -> dict:
    """Parse a document's front matter, tolerating unreadable files."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    fm_text, _ = split_front_matter(text)
    if not fm_text:
        return {}
    return parse_front_matter(fm_text)


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
            # The `_spec` suffix is optional under specification/, so every
            # .md there is an abstract spec except a v4.x persistent design
            # doc (`*_design.md`), which is listed separately below. But that
            # filename heuristic alone cannot tell a legacy design doc apart
            # from a legitimately named *new* spec whose own stem happens to
            # end in `_design` (e.g. `api_design.md`) -- a file's own front
            # matter `type` overrides the heuristic when declared (`type:
            # spec` keeps it out of design_matches; `type: design` keeps a
            # non-`_design`-named file in it). Files without a declared `type`
            # (the common case for legacy v4.x docs, predating this field)
            # fall back to the filename heuristic below.
            all_md = sorted_matches(specification_path, "*.md")
            design_set = set()
            for m in sorted_matches(specification_path, "*_design.md"):
                declared_type = read_front_matter(Path(m)).get("type", "")
                if declared_type != "spec":
                    design_set.add(m)
            for m in all_md:
                if m in design_set:
                    continue
                if read_front_matter(Path(m)).get("type", "") == "design":
                    design_set.add(m)
            design_matches = sorted(design_set)
            spec_matches = [m for m in all_md if m not in design_set]
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
