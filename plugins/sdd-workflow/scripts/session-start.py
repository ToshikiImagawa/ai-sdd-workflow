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
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class SddConfig:
    root: str = ".sdd"
    lang: str = "en"
    requirement_dir: str = "requirement"
    specification_dir: str = "specification"
    task_dir: str = "task"


def get_plugin_root():
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        print("[AI-SDD] Error: CLAUDE_PLUGIN_ROOT is not set. Aborting session-start.", file=sys.stderr)
        sys.exit(1)
    return plugin_root


def get_project_root():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        return project_dir
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.getcwd()


def load_or_create_config(config_path, default_lang):
    if not os.path.isfile(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        default_config = {
            "root": ".sdd",
            "lang": default_lang,
            "directories": {
                "requirement": "requirement",
                "specification": "specification",
                "task": "task",
            },
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("[AI-SDD] .sdd-config.json auto-generated.")
        return default_config

    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def build_sdd_config(raw, default_lang):
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
    return cfg


def ensure_sdd_directory(sdd_dir, docs_root):
    if not os.path.isdir(sdd_dir):
        os.makedirs(sdd_dir, exist_ok=True)
        print(f"[AI-SDD] {docs_root}/ directory created.")


def get_plugin_version(plugin_root):
    plugin_json_path = os.path.join(plugin_root, ".claude-plugin", "plugin.json")
    if not os.path.isfile(plugin_json_path):
        return ""
    try:
        with open(plugin_json_path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("version", "")
    except (json.JSONDecodeError, OSError):
        return ""


def sync_principles_file(plugin_root, sdd_dir, plugin_version):
    source = os.path.join(plugin_root, "AI-SDD-PRINCIPLES.source.md")
    target = os.path.join(sdd_dir, "AI-SDD-PRINCIPLES.md")

    if not os.path.isfile(source):
        print(f"[AI-SDD] Source file not found: {source}. Skipping auto-sync.", file=sys.stderr)
        return

    if plugin_version:
        try:
            with open(source, encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r"^version:.*$", f'version: "{plugin_version}"', content, flags=re.MULTILINE)
            tmp_path = target + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, target)
            print(f"[AI-SDD] AI-SDD-PRINCIPLES.md updated to v{plugin_version}.")
        except OSError:
            print("[AI-SDD] Warning: Failed to update version. Copying without version info.", file=sys.stderr)
            shutil.copy2(source, target)
    else:
        shutil.copy2(source, target)
        print("[AI-SDD] AI-SDD-PRINCIPLES.md copied (version unknown).")


def write_env_vars(cfg):
    env_file = os.environ.get("CLAUDE_ENV_FILE", "")
    if not env_file:
        return

    lines = []
    if os.path.isfile(env_file):
        with open(env_file, encoding="utf-8") as f:
            lines = [line for line in f.readlines() if not line.startswith("export SDD_")]

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

    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
        for entry in env_entries:
            f.write(entry + "\n")


def compare_major_minor(plugin_version, project_version):
    """Return True if project_version >= plugin_version (major.minor only)."""
    m_plugin = re.match(r"(\d+)\.(\d+)", plugin_version)
    m_project = re.match(r"(\d+)\.(\d+)", project_version)
    if not m_plugin or not m_project:
        return True
    plugin_tuple = (int(m_plugin.group(1)), int(m_plugin.group(2)))
    project_tuple = (int(m_project.group(1)), int(m_project.group(2)))
    return project_tuple >= plugin_tuple


def check_claude_md(project_root, sdd_dir, docs_root, plugin_version):
    if not os.path.isdir(sdd_dir):
        return

    claude_md = os.path.join(project_root, "CLAUDE.md")
    show_warning = False
    warning_reason = ""
    claude_version = ""

    if not os.path.isfile(claude_md):
        show_warning = True
        warning_reason = "missing"
    elif plugin_version:
        try:
            with open(claude_md, encoding="utf-8") as f:
                content = f.read()
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

    warning_file = os.path.join(sdd_dir, "UPDATE_REQUIRED.md")

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
        with open(warning_file, "w", encoding="utf-8") as f:
            f.write(warning_content)

        print("[AI-SDD] CLAUDE.md update required. Please run /sdd-init.", file=sys.stderr)
    else:
        if os.path.isfile(warning_file):
            os.remove(warning_file)


def main():
    parser = argparse.ArgumentParser(description="AI-SDD session start script")
    parser.add_argument("--default-lang", default="en", help="Default language (en/ja)")
    args = parser.parse_args()

    plugin_root = get_plugin_root()
    project_root = get_project_root()
    config_path = os.path.join(project_root, ".sdd-config.json")

    raw_config = load_or_create_config(config_path, args.default_lang)
    cfg = build_sdd_config(raw_config, args.default_lang)

    sdd_dir = os.path.join(project_root, cfg.root)
    ensure_sdd_directory(sdd_dir, cfg.root)

    plugin_version = get_plugin_version(plugin_root)
    sync_principles_file(plugin_root, sdd_dir, plugin_version)

    write_env_vars(cfg)

    check_claude_md(project_root, sdd_dir, cfg.root, plugin_version)


if __name__ == "__main__":
    main()
