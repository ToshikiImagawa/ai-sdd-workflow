#!/usr/bin/env python3
"""
prepare-spec.py
Prepare templates and references for /generate-spec skill
Reduces Claude's Read tool calls by pre-loading necessary files
"""

import os
import sys
import json
import shutil
from pathlib import Path


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[prepare-spec] {message}", file=sys.stderr)


def get_project_root() -> Path:
    """Get project root directory"""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir)

    # Try git root
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def read_config(project_root: Path) -> dict:
    """Read .sdd-config.json"""
    config_file = project_root / ".sdd-config.json"
    if not config_file.exists():
        log(f"ERROR: .sdd-config.json not found at {config_file}")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    return {
        "lang": config.get("lang", "en"),
        "root": config.get("root", ".sdd")
    }


def get_plugin_root() -> Path:
    """Get plugin root directory"""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root)

    # Fallback: calculate from script location
    # scripts/prepare-spec.py -> skills/generate-spec/scripts/prepare-spec.py
    script_dir = Path(__file__).parent.resolve()
    return script_dir.parent.parent.parent


def prepare_templates(
    project_root: Path,
    plugin_root: Path,
    sdd_root: str,
    sdd_lang: str,
    output_dir: Path
) -> None:
    """Prepare specification and design templates"""
    log("Preparing templates...")

    skill_dir = plugin_root / "skills" / "generate-spec"

    # Specification template
    project_spec_template = project_root / sdd_root / "SPECIFICATION_TEMPLATE.md"
    skill_spec_template = skill_dir / "templates" / sdd_lang / "spec_template.md"

    if project_spec_template.exists():
        shutil.copy2(project_spec_template, output_dir / "spec_template.md")
        log(f"Using project spec template: {sdd_root}/SPECIFICATION_TEMPLATE.md")
    elif skill_spec_template.exists():
        shutil.copy2(skill_spec_template, output_dir / "spec_template.md")
        log(f"Using skill spec template: templates/{sdd_lang}/spec_template.md")
    else:
        log("WARNING: No spec template found")

    # Design template
    project_design_template = project_root / sdd_root / "DESIGN_DOC_TEMPLATE.md"
    skill_design_template = skill_dir / "templates" / sdd_lang / "design_template.md"

    if project_design_template.exists():
        shutil.copy2(project_design_template, output_dir / "design_template.md")
        log(f"Using project design template: {sdd_root}/DESIGN_DOC_TEMPLATE.md")
    elif skill_design_template.exists():
        shutil.copy2(skill_design_template, output_dir / "design_template.md")
        log(f"Using skill design template: templates/{sdd_lang}/design_template.md")
    else:
        log("WARNING: No design template found")


def copy_references(plugin_root: Path, output_dir: Path) -> None:
    """Copy reference files"""
    log("Copying reference files...")

    skill_dir = plugin_root / "skills" / "generate-spec"
    references_dir = skill_dir / "references"

    if references_dir.exists():
        output_references = output_dir / "references"
        if output_references.exists():
            shutil.rmtree(output_references)
        shutil.copytree(references_dir, output_references)
        log("Reference files copied")


def export_env_vars(output_dir: Path) -> None:
    """Export metadata to CLAUDE_ENV_FILE"""
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if not env_file:
        return

    env_file_path = Path(env_file)

    # Remove existing GENERATE_SPEC_* variables
    if env_file_path.exists():
        with open(env_file_path, "r", encoding="utf-8") as f:
            lines = [line for line in f if not line.startswith("export GENERATE_SPEC_")]

        with open(env_file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # Write new metadata
    with open(env_file_path, "a", encoding="utf-8") as f:
        f.write(f'export GENERATE_SPEC_CACHE_DIR="{output_dir}"\n')
        f.write(f'export GENERATE_SPEC_SPEC_TEMPLATE="{output_dir / "spec_template.md"}"\n')
        f.write(f'export GENERATE_SPEC_DESIGN_TEMPLATE="{output_dir / "design_template.md"}"\n')
        f.write(f'export GENERATE_SPEC_REFERENCES="{output_dir / "references"}"\n')

    log("Environment variables exported to CLAUDE_ENV_FILE")


def main() -> None:
    """Main execution"""
    try:
        # Get directories
        project_root = get_project_root()
        plugin_root = get_plugin_root()

        # Read configuration
        config = read_config(project_root)
        sdd_lang = config["lang"]
        sdd_root = config["root"]

        # Create output directory
        output_dir = project_root / sdd_root / ".cache" / "generate-spec"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare templates and references
        prepare_templates(project_root, plugin_root, sdd_root, sdd_lang, output_dir)
        copy_references(plugin_root, output_dir)

        # Export environment variables
        export_env_vars(output_dir)

        log("Preparation complete")
        log(f"Cache location: {output_dir}")

    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
