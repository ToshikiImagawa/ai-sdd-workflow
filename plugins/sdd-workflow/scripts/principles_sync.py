#!/usr/bin/env python3
"""principles_sync.py - Regenerate the plugin-managed agent guidance files.

``.sdd/AI-SDD-PRINCIPLES.md`` and ``.claude/rules/ai-sdd-instructions.md`` are
generated from ``${CLAUDE_PLUGIN_ROOT}`` and are never hand-edited, so they must
always match the plugin version that is currently active.

The generation lives here (rather than in a single caller) because two entry
points need it: the SessionStart hook (``session-start.py``) and /sdd-init
(``skills/sdd-init/scripts/init-structure.py``). /sdd-init runs after
``/reload-plugins`` has already swapped the active plugin version without firing
a SessionStart event, which would otherwise leave both files on the previous
version until the next session.
"""

import json
import re
import shutil
import sys
from pathlib import Path

# The AI-SDD rules file is guidance for the AI agent, not a human-facing
# document, so it is intentionally single-language (English) regardless of
# SDD_LANG. This keeps exactly one path-scoped rule instead of one per language.
RULES_FILENAME = "ai-sdd-instructions.md"
# Per-language filename written by pre-release builds; cleaned up on sync so
# that only the single English rule loads for .sdd/** paths.
LEGACY_RULES_FILENAME = "ai-sdd-instructions-en.md"


def get_plugin_version(plugin_root: str) -> str:
    plugin_json_path = Path(plugin_root) / ".claude-plugin" / "plugin.json"
    if not plugin_json_path.is_file():
        return ""
    try:
        data = json.loads(plugin_json_path.read_text(encoding="utf-8"))
        return data.get("version", "")
    except (json.JSONDecodeError, OSError):
        return ""


def sync_principles_file(plugin_root: str, sdd_dir: str, plugin_version: str) -> None:
    source = Path(plugin_root) / "AI-SDD-PRINCIPLES.source.md"
    target = Path(sdd_dir) / "AI-SDD-PRINCIPLES.md"

    if not source.is_file():
        print(f"[AI-SDD] Source file not found: {source}. Skipping auto-sync.", file=sys.stderr)
        return

    if plugin_version:
        try:
            content = source.read_text(encoding="utf-8")
            content = re.sub(r"^version:.*$", f'version: "{plugin_version}"', content, flags=re.MULTILINE)
            tmp_path = target.with_name(target.name + ".tmp")
            tmp_path.write_text(content, encoding="utf-8")
            tmp_path.replace(target)
            print(f"[AI-SDD] AI-SDD-PRINCIPLES.md updated to v{plugin_version}.")
        except OSError:
            print("[AI-SDD] Warning: Failed to update version. Copying without version info.", file=sys.stderr)
            shutil.copy2(source, target)
    else:
        shutil.copy2(source, target)
        print("[AI-SDD] AI-SDD-PRINCIPLES.md copied (version unknown).")


def sync_rules_files(plugin_root: str, project_root: str, sdd_root: str, plugin_version: str) -> None:
    rules_dir = Path(project_root) / ".claude" / "rules"
    template_path = (
        Path(plugin_root) / "skills" / "sdd-init" / "templates" / "ai_sdd_instructions_rules.md"
    )
    target_path = rules_dir / RULES_FILENAME

    if not template_path.is_file():
        print(f"[AI-SDD] Warning: Template not found: {template_path}. Skipping rules sync.", file=sys.stderr)
        return

    rules_dir.mkdir(parents=True, exist_ok=True)

    try:
        content = template_path.read_text(encoding="utf-8")
        # Substitute the configured SDD root so the path-scoped rule's "paths:"
        # glob matches the project's actual root (which may be customized via
        # .sdd-config.json). The glob is consumed by the Claude Code rule loader,
        # so it must be the literal resolved root, not a "${SDD_ROOT}" env ref.
        content = content.replace("{SDD_ROOT}", sdd_root)
        if plugin_version:
            content = content.replace("{PLUGIN_VERSION}", plugin_version)
        else:
            print("[AI-SDD] Warning: Plugin version unknown; rules file keeps the {PLUGIN_VERSION} placeholder.", file=sys.stderr)
        tmp_path = target_path.with_name(target_path.name + ".tmp")
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(target_path)
        print(f"[AI-SDD] .claude/rules/{RULES_FILENAME} synced (v{plugin_version or 'unknown'}).")
    except OSError as e:
        print(f"[AI-SDD] Warning: Failed to sync rules file: {e}", file=sys.stderr)
        return

    # Remove the stale per-language rules file left by pre-release builds.
    legacy_path = rules_dir / LEGACY_RULES_FILENAME
    if legacy_path.is_file():
        try:
            legacy_path.unlink()
            print(f"[AI-SDD] Removed legacy rules file .claude/rules/{LEGACY_RULES_FILENAME}.")
        except OSError:
            pass


def sync_all(plugin_root: str, project_root: str, sdd_root: str, sdd_dir: str) -> str:
    """Regenerate both files from the active plugin; returns the plugin version.

    Wrapping the pair keeps the two entry points (SessionStart hook and
    /sdd-init) from drifting apart on which files get regenerated.
    """
    plugin_version = get_plugin_version(plugin_root)
    sync_principles_file(plugin_root, sdd_dir, plugin_version)
    sync_rules_files(plugin_root, project_root, sdd_root, plugin_version)
    return plugin_version
