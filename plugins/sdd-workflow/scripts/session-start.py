#!/usr/bin/env python3
"""session-start.py - SessionStart hook script.

Loads .sdd-config.json at session start (generates if not exists)
and initializes environment variables.
"""

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env_export import rewrite_exports  # noqa: E402
from hook_common import resolve_project_root  # noqa: E402


@dataclass
class SddConfig:
    root: str = ".sdd"
    lang: str = "en"
    requirement_dir: str = "requirement"
    specification_dir: str = "specification"
    task_dir: str = "task"
    index: bool = True


def get_plugin_root() -> str:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        print("[AI-SDD] Error: CLAUDE_PLUGIN_ROOT is not set. Aborting session-start.", file=sys.stderr)
        sys.exit(1)
    return plugin_root


def get_project_root() -> str:
    return resolve_project_root()


def load_or_create_config(config_path: str, default_lang: str) -> Dict[str, Any]:
    path = Path(config_path)
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "root": ".sdd",
            "lang": default_lang,
            "directories": {
                "requirement": "requirement",
                "specification": "specification",
                "task": "task",
            },
            "index": True,
        }
        path.write_text(
            json.dumps(default_config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("[AI-SDD] .sdd-config.json auto-generated.")
        return default_config

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[AI-SDD] Warning: .sdd-config.json is invalid JSON ({e}). Using default values.", file=sys.stderr)
        return {}


def parse_index_flag(value: Any, default: bool = True) -> bool:
    """Normalize the .sdd-config.json "index" value to a boolean.

    The setting is boolean-only (true/false). An absent key falls back to the
    default (on). Any non-boolean value (e.g. a legacy "on"/"off" string) is
    rejected with a warning and treated as the default.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    print(
        "[AI-SDD] Warning: 'index' in .sdd-config.json must be a boolean "
        f"(true/false), got {value!r}. Using default (on).",
        file=sys.stderr,
    )
    return default


def build_sdd_config(raw: Dict[str, Any], default_lang: str) -> SddConfig:
    cfg = SddConfig(lang=default_lang)
    if raw.get("root"):
        cfg.root = raw["root"]
    if raw.get("lang"):
        cfg.lang = raw["lang"]
    dirs = raw.get("directories", {})
    if dirs.get("requirement"):
        cfg.requirement_dir = dirs["requirement"]
    if dirs.get("specification"):
        cfg.specification_dir = dirs["specification"]
    if dirs.get("task"):
        cfg.task_dir = dirs["task"]
    cfg.index = parse_index_flag(raw.get("index"))
    return cfg


def ensure_sdd_directory(sdd_dir: str, docs_root: str) -> None:
    path = Path(sdd_dir)
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        print(f"[AI-SDD] {docs_root}/ directory created.")


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


# The AI-SDD rules file is guidance for the AI agent, not a human-facing
# document, so it is intentionally single-language (English) regardless of
# SDD_LANG. This keeps exactly one path-scoped rule instead of one per language.
RULES_FILENAME = "ai-sdd-instructions.md"
# Per-language filename written by pre-release builds; cleaned up on sync so
# that only the single English rule loads for .sdd/** paths.
LEGACY_RULES_FILENAME = "ai-sdd-instructions-en.md"


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


def write_env_vars(cfg: SddConfig) -> None:
    env_entries = [
        f'export SDD_ROOT="{cfg.root}"',
        f'export SDD_REQUIREMENT_DIR="{cfg.requirement_dir}"',
        f'export SDD_SPECIFICATION_DIR="{cfg.specification_dir}"',
        f'export SDD_TASK_DIR="{cfg.task_dir}"',
        f'export SDD_REQUIREMENT_PATH="{cfg.root}/{cfg.requirement_dir}"',
        f'export SDD_SPECIFICATION_PATH="{cfg.root}/{cfg.specification_dir}"',
        f'export SDD_TASK_PATH="{cfg.root}/{cfg.task_dir}"',
        f'export SDD_LANG="{cfg.lang}"',
    ]

    if cfg.index:
        env_entries.append('export SDD_INDEX="on"')

    rewrite_exports("SDD_", env_entries)


def compare_major_minor(plugin_version: str, project_version: str) -> bool:
    """Return True if project_version >= plugin_version (major.minor only)."""
    m_plugin = re.match(r"(\d+)\.(\d+)", plugin_version)
    m_project = re.match(r"(\d+)\.(\d+)", project_version)
    if not m_plugin or not m_project:
        return True
    plugin_tuple = (int(m_plugin.group(1)), int(m_plugin.group(2)))
    project_tuple = (int(m_project.group(1)), int(m_project.group(2)))
    return project_tuple >= plugin_tuple


def check_claude_md(project_root: str, sdd_dir: str, plugin_version: str) -> None:
    if not Path(sdd_dir).is_dir():
        return

    claude_md = Path(project_root) / "CLAUDE.md"
    show_warning = False
    warning_reason = ""
    claude_version = ""

    if not claude_md.is_file():
        show_warning = True
        warning_reason = "missing"
    elif plugin_version:
        try:
            content = claude_md.read_text(encoding="utf-8")
        except OSError:
            return

        m = re.search(r"## AI-SDD Instructions \(v([\d.]+)", content)
        if not m:
            show_warning = True
            warning_reason = "no_version"
        else:
            claude_version = m.group(1)
            if not compare_major_minor(plugin_version, claude_version):
                show_warning = True
                warning_reason = "outdated"

    warning_file = Path(sdd_dir) / "UPDATE_REQUIRED.md"

    if show_warning:
        messages = {
            "missing": "CLAUDE.md not found. AI-SDD workflow configuration may be incomplete.",
            "no_version": "CLAUDE.md has no AI-SDD section. Old format CLAUDE.md detected.",
            "outdated": f"CLAUDE.md AI-SDD section is outdated. Plugin: v{plugin_version}, CLAUDE.md: v{claude_version}",
        }
        warning_message = messages.get(warning_reason, "")

        warning_content = f"""\
# AI-SDD Update Required

## Reason

{warning_message}

## How to Fix

Run the following command:

```
/sdd-init
```

This will update the AI-SDD section in CLAUDE.md.

---
This file will be automatically deleted after running /sdd-init.
"""
        warning_file.write_text(warning_content, encoding="utf-8")

        print("[AI-SDD] CLAUDE.md update required. Please run /sdd-init.", file=sys.stderr)
    else:
        if warning_file.is_file():
            warning_file.unlink()


def rebuild_index(project_root: str) -> None:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import sdd_index
        sdd_index.rebuild_all(project_root)
    except Exception as e:  # noqa: BLE001
        print(f"[AI-SDD] Warning: failed to rebuild .sdd index: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-SDD session start script")
    parser.add_argument("--default-lang", default="en", help="Default language (en/ja)")
    args = parser.parse_args()

    plugin_root = get_plugin_root()
    project_root = get_project_root()
    config_path = str(Path(project_root) / ".sdd-config.json")

    raw_config = load_or_create_config(config_path, args.default_lang)
    cfg = build_sdd_config(raw_config, args.default_lang)

    sdd_dir = str(Path(project_root) / cfg.root)
    ensure_sdd_directory(sdd_dir, cfg.root)

    plugin_version = get_plugin_version(plugin_root)
    sync_principles_file(plugin_root, sdd_dir, plugin_version)
    sync_rules_files(plugin_root, project_root, cfg.root, plugin_version)

    write_env_vars(cfg)

    if cfg.index:
        rebuild_index(project_root)

    check_claude_md(project_root, sdd_dir, plugin_version)


if __name__ == "__main__":
    main()
