#!/usr/bin/env python3
"""
update-claude-md.py
Automatically update the minimal AI-SDD Instructions section in CLAUDE.md.
(The detailed .claude/rules/ai-sdd-instructions.md guide is managed by the
 SessionStart hook, session-start.py, not by this script.)

Uses only the Python standard library (pathlib / json / re) so it runs
cross-platform without external tools (sed / jq / grep / awk).
"""

import json
import os
import re
import sys
from pathlib import Path

# Shared modules live in plugins/sdd-workflow/scripts (three levels up + scripts).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from hook_common import resolve_project_root  # noqa: E402

SECTION_HEADING = "## AI-SDD Instructions"


def error_exit(message: str) -> None:
    """Print error to stderr and exit non-zero"""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def get_project_root() -> Path:
    """Get project root directory (CLAUDE_PROJECT_DIR > git root > cwd)"""
    return Path(resolve_project_root())


def get_plugin_root() -> Path:
    """Get plugin root directory (CLAUDE_PLUGIN_ROOT > script location fallback)"""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root)

    # Fallback: detect from script location (for development)
    # scripts/update-claude-md.py -> skills/sdd-init/scripts/update-claude-md.py
    # Go up 3 levels: scripts -> sdd-init -> skills -> sdd-workflow
    script_dir = Path(__file__).parent.resolve()
    return script_dir.parent.parent.parent


def resolve_lang_and_root(project_root: Path) -> tuple:
    """Read SDD_LANG and SDD_ROOT from .sdd-config.json (priority over environment variable).

    This ensures consistency with init-structure.py.
    """
    config_file = project_root / ".sdd-config.json"
    config_lang = ""
    config_root = ""
    if config_file.is_file():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            config_lang = config.get("lang") or ""
            config_root = config.get("root") or ""
        except (json.JSONDecodeError, OSError):
            config_lang = ""
            config_root = ""

    sdd_lang = config_lang or os.environ.get("SDD_LANG") or "en"
    sdd_root = config_root or os.environ.get("SDD_ROOT") or ".sdd"
    return sdd_lang, sdd_root


def extract_current_version(claude_md: str) -> str:
    """Extract the version from the first AI-SDD Instructions section title.

    Mirrors the shell pipeline:
        grep "## AI-SDD Instructions" | sed -n 's/.*v\\([0-9.]*\\).*/\\1/p' | head -n 1
    """
    for line in claude_md.splitlines():
        if SECTION_HEADING in line:
            # Greedy leading match finds the last 'v' followed by digits/dots.
            match = re.match(r".*v([0-9.]*)", line)
            if match:
                return match.group(1)
            # Line matched the heading but had no version -> treat as unknown.
            return "unknown"
    return "unknown"


def replace_section(claude_md: str, new_content: str) -> str:
    """Replace the AI-SDD Instructions section (heading to next '## ' or EOF).

    Mirrors the awk block in the original shell script: the new content is
    printed in place of the old section, everything else is preserved.
    """
    out_lines = []
    in_section = False
    content_lines = new_content.split("\n")

    for line in claude_md.splitlines():
        if line.startswith(SECTION_HEADING):
            if not in_section:
                in_section = True
                out_lines.extend(content_lines)
            # Skip the heading line itself (and stay in section otherwise).
            continue
        if line.startswith("## ") and in_section:
            in_section = False
        if not in_section:
            out_lines.append(line)

    return "\n".join(out_lines) + "\n"


def main() -> None:
    """Main execution"""
    project_root = get_project_root()
    plugin_root = get_plugin_root()
    sdd_lang, sdd_root = resolve_lang_and_root(project_root)

    # 1. Get plugin version
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if not plugin_json.is_file():
        error_exit(f"plugin.json not found at: {plugin_json}")

    try:
        with open(plugin_json, "r", encoding="utf-8") as f:
            plugin_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        error_exit(f"Failed to read plugin.json: {e}")

    plugin_version = plugin_data.get("version")
    if not plugin_version:
        error_exit("Failed to read version from plugin.json")

    # 2. Load CLAUDE.md template and replace placeholders
    claude_template = (
        plugin_root / "skills" / "sdd-init" / "templates" / sdd_lang / "claude_md_template.md"
    )
    if not claude_template.is_file():
        error_exit(f"Template file not found at: {claude_template}")

    # Substitute version and the configured SDD root. Strip trailing newlines to
    # mirror the shell command substitution behaviour.
    claude_content = claude_template.read_text(encoding="utf-8")
    claude_content = claude_content.replace("{PLUGIN_VERSION}", plugin_version)
    claude_content = claude_content.replace("{SDD_ROOT}", sdd_root)
    claude_content = claude_content.rstrip("\n")

    # 3. Update CLAUDE.md
    claude_md_path = project_root / "CLAUDE.md"

    if not claude_md_path.exists():
        # Case 1: Create new CLAUDE.md
        claude_md_path.write_text(claude_content + "\n", encoding="utf-8")
        print(f"✓ Created CLAUDE.md with AI-SDD Instructions (v{plugin_version})")
    else:
        existing = claude_md_path.read_text(encoding="utf-8")

        if SECTION_HEADING not in existing:
            # Case 2: Append section
            claude_md_path.write_text(
                existing + "\n" + claude_content + "\n", encoding="utf-8"
            )
            print(f"✓ Appended AI-SDD Instructions section (v{plugin_version})")
        else:
            # Case 3: Update existing section
            current_version = extract_current_version(existing)

            if current_version != plugin_version:
                updated = replace_section(existing, claude_content)
                claude_md_path.write_text(updated, encoding="utf-8")
                print(
                    f"✓ Updated AI-SDD Instructions section "
                    f"(v{current_version} → v{plugin_version})"
                )
            else:
                print(f"✓ AI-SDD Instructions section is up to date (v{plugin_version})")

    # Note: the detailed AI-SDD guide at .claude/rules/ai-sdd-instructions.md is
    # created and version-synced by the SessionStart hook (session-start.py),
    # so this script only manages the minimal CLAUDE.md section.
    sys.exit(0)


if __name__ == "__main__":
    main()
