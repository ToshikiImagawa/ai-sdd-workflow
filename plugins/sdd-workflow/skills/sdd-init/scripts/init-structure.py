#!/usr/bin/env python3
"""
init-structure.py
Static file operations for /sdd-init skill.
Performs directory creation and template copying to reduce Claude's tool call overhead.

Uses only the Python standard library (pathlib / json) so it runs cross-platform
without external tools (find / sed / jq / grep / awk).
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Shared modules live in plugins/sdd-workflow/scripts (three levels up + scripts).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from hook_common import resolve_project_root  # noqa: E402
from env_export import rewrite_exports  # noqa: E402


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[init-structure] {message}", file=sys.stderr)


def get_project_root() -> Path:
    """Get project root directory (CLAUDE_PROJECT_DIR > git root > cwd)"""
    return Path(resolve_project_root())


def get_plugin_root() -> Path:
    """Get plugin root directory (CLAUDE_PLUGIN_ROOT > script location fallback)"""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root)

    # Fallback: detect from script location (for development)
    # scripts/init-structure.py -> skills/sdd-init/scripts/init-structure.py
    # Go up 3 levels: scripts -> sdd-init -> skills -> sdd-workflow
    script_dir = Path(__file__).parent.resolve()
    return script_dir.parent.parent.parent


def read_config(config_file: Path) -> dict:
    """Read configuration from .sdd-config.json (must exist before running this script)"""
    if not config_file.is_file():
        log("ERROR: .sdd-config.json not found. This script requires configuration file.")
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


def copy_templates(sdd_dir: Path, plugin_root: Path, sdd_lang: str) -> None:
    """Copy base templates from other skills (existing files are never overwritten)"""
    log("Checking templates...")

    generate_prd_skill = plugin_root / "skills" / "generate-prd"
    generate_spec_skill = plugin_root / "skills" / "generate-spec"

    # Template mappings (target -> source)
    # Note: CONSTITUTION.md is NOT copied here - it should be generated via
    # /constitution init which customizes the template based on project context.
    templates = [
        (
            sdd_dir / "PRD_TEMPLATE.md",
            generate_prd_skill / "templates" / sdd_lang / "prd_template.md",
        ),
        (
            sdd_dir / "SPECIFICATION_TEMPLATE.md",
            generate_spec_skill / "templates" / sdd_lang / "spec_template.md",
        ),
        (
            sdd_dir / "DESIGN_DOC_TEMPLATE.md",
            generate_spec_skill / "templates" / sdd_lang / "design_template.md",
        ),
    ]

    copied_count = 0
    skipped_count = 0

    for target, source in templates:
        if target.exists():
            log(f"Skipped (exists): {target.name}")
            skipped_count += 1
        elif source.is_file():
            shutil.copy2(source, target)
            log(f"Copied: {target.name}")
            copied_count += 1
        else:
            log(f"WARNING: Source template not found: {source}")

    log(f"Templates copied: {copied_count}, skipped: {skipped_count}")


def export_env_vars(config: dict) -> None:
    """Export SDD_* environment variables to CLAUDE_ENV_FILE"""
    sdd_root = config["root"]
    requirement = config["requirement"]
    specification = config["specification"]
    task = config["task"]

    wrote = rewrite_exports("SDD_", [
        f'export SDD_ROOT="{sdd_root}"',
        f'export SDD_REQUIREMENT_DIR="{requirement}"',
        f'export SDD_SPECIFICATION_DIR="{specification}"',
        f'export SDD_TASK_DIR="{task}"',
        f'export SDD_REQUIREMENT_PATH="{sdd_root}/{requirement}"',
        f'export SDD_SPECIFICATION_PATH="{sdd_root}/{specification}"',
        f'export SDD_TASK_PATH="{sdd_root}/{task}"',
        f'export SDD_LANG="{config["lang"]}"',
    ])
    if wrote:
        log("Environment variables exported to CLAUDE_ENV_FILE")


def main() -> None:
    """Main execution"""
    project_root = get_project_root()
    plugin_root = get_plugin_root()

    config_file = project_root / ".sdd-config.json"
    config = read_config(config_file)

    sdd_root = config["root"]
    sdd_dir = project_root / sdd_root

    # --- Phase 1: Ensure .sdd root exists ---
    log(f"Ensuring {sdd_root}/ directory exists...")
    sdd_dir.mkdir(parents=True, exist_ok=True)
    log(f"Root directory ready: {sdd_root}/")
    log(
        f"Note: Subdirectories ({config['requirement']}, {config['specification']}, "
        f"{config['task']}) will be created automatically when files are generated"
    )

    # --- Phase 2: Copy templates (if not exist) ---
    copy_templates(sdd_dir, plugin_root, config["lang"])

    # --- Phase 3: Cleanup ---
    update_required_file = sdd_dir / "UPDATE_REQUIRED.md"
    if update_required_file.is_file():
        update_required_file.unlink()
        log("Deleted: UPDATE_REQUIRED.md")

    # --- Phase 4: Export environment variables to CLAUDE_ENV_FILE ---
    # Note: These variables are already set by session-start.py, but we ensure they're current
    export_env_vars(config)

    log("Completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
