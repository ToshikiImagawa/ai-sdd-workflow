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
from typing import Any, Dict, Optional


@dataclass
class CliConfig:
    enabled: Optional[bool] = None  # None = auto-detect mode
    repository: str = "https://github.com/ToshikiImagawa/ai-sdd-workflow-cli.git"


@dataclass
class CliResult:
    available: bool = False
    command: str = ""


@dataclass
class SddConfig:
    root: str = ".sdd"
    lang: str = "en"
    requirement_dir: str = "requirement"
    specification_dir: str = "specification"
    task_dir: str = "task"
    cli: Optional[CliConfig] = None

    def __post_init__(self) -> None:
        if self.cli is None:
            self.cli = CliConfig()


def get_plugin_root() -> str:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        print("[AI-SDD] Error: CLAUDE_PLUGIN_ROOT is not set. Aborting session-start.", file=sys.stderr)
        sys.exit(1)
    return plugin_root


def get_project_root() -> str:
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


def load_or_create_config(config_path: str, default_lang: str) -> Dict[str, Any]:
    if not os.path.isfile(config_path):
        parent = os.path.dirname(config_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
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
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[AI-SDD] Warning: .sdd-config.json is invalid JSON ({e}). Using default values.", file=sys.stderr)
            return {}


def load_local_config(project_root: str) -> Dict[str, Any]:
    local_path = os.path.join(project_root, ".sdd-config.local.json")
    if not os.path.isfile(local_path):
        return {}
    try:
        with open(local_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[AI-SDD] Warning: .sdd-config.local.json parse error ({e}). Ignoring.", file=sys.stderr)
        return {}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = {**result[key], **value}
        else:
            result[key] = value
    return result


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

    cli_raw = raw.get("cli", {})
    if isinstance(cli_raw, dict):
        cli_cfg = CliConfig()
        if "enabled" in cli_raw:
            cli_cfg.enabled = bool(cli_raw["enabled"])
        if cli_raw.get("repository"):
            cli_cfg.repository = cli_raw["repository"]
        cfg.cli = cli_cfg

    return cfg


def validate_repository_url(url: str) -> bool:
    """Validate that repository URL is a safe GitHub HTTPS URL.

    Only allows GitHub repositories in the format:
    https://github.com/{owner}/{repo}.git

    Where {owner} and {repo} contain only:
    - Alphanumeric characters (a-z, A-Z, 0-9)
    - Hyphens (-)
    - Underscores (_)
    - Dots (.) in repo name only

    This prevents command injection attacks via malicious repository URLs.

    Args:
        url: Repository URL to validate

    Returns:
        True if URL is safe, False otherwise
    """
    # Pattern: https://github.com/{owner}/{repo}.git
    # owner: alphanumeric, hyphens, underscores (GitHub username rules)
    # repo: alphanumeric, hyphens, underscores, dots
    pattern = r'^https://github\.com/[\w-]+/[\w\.-]+\.git$'

    if not re.match(pattern, url):
        return False

    # Additional safety checks: reject URLs with shell metacharacters
    dangerous_chars = [';', '|', '&', '$', '`', '(', ')', '<', '>', '\n', '\r', ' ']
    if any(char in url for char in dangerous_chars):
        return False

    return True


def detect_cli(cli_cfg: CliConfig) -> CliResult:
    # cli.enabled == False: skip detection entirely
    if cli_cfg.enabled is False:
        print("[AI-SDD] CLI integration disabled (cli.enabled=false)", file=sys.stderr)
        return CliResult(available=False)

    # Check if sdd-cli is on PATH
    if shutil.which("sdd-cli"):
        print("[AI-SDD] CLI available: sdd-cli found on PATH", file=sys.stderr)
        return CliResult(available=True, command="sdd-cli")

    # If cli.enabled is explicitly True, try uvx fallback
    if cli_cfg.enabled:
        if shutil.which("uvx"):
            # Validate repository URL before using it (security check)
            if not validate_repository_url(cli_cfg.repository):
                print(
                    f"[AI-SDD] Error: Invalid or potentially unsafe repository URL: {cli_cfg.repository}",
                    file=sys.stderr
                )
                print(
                    "[AI-SDD] Only GitHub HTTPS URLs are allowed (e.g., https://github.com/user/repo.git)",
                    file=sys.stderr
                )
                return CliResult(available=False)

            command = f"uvx --from git+{cli_cfg.repository} sdd-cli"
            print(f"[AI-SDD] CLI available via uvx: {command}", file=sys.stderr)
            return CliResult(available=True, command=command)
        else:
            print("[AI-SDD] Warning: cli.enabled is true but neither sdd-cli nor uvx found on PATH.", file=sys.stderr)
            return CliResult(available=False)

    # Auto-detect mode (enabled=None): sdd-cli not found, no fallback
    print("[AI-SDD] CLI not detected (auto-detect mode)", file=sys.stderr)
    return CliResult(available=False)


def ensure_sdd_directory(sdd_dir: str, docs_root: str) -> None:
    if not os.path.isdir(sdd_dir):
        os.makedirs(sdd_dir, exist_ok=True)
        print(f"[AI-SDD] {docs_root}/ directory created.")


def get_plugin_version(plugin_root: str) -> str:
    plugin_json_path = os.path.join(plugin_root, ".claude-plugin", "plugin.json")
    if not os.path.isfile(plugin_json_path):
        return ""
    try:
        with open(plugin_json_path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("version", "")
    except (json.JSONDecodeError, OSError):
        return ""


def sync_principles_file(plugin_root: str, sdd_dir: str, plugin_version: str) -> None:
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


def write_env_vars(cfg: SddConfig, cli_result: CliResult) -> None:
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
        f'export SDD_CLI_AVAILABLE="{"true" if cli_result.available else "false"}"',
    ]

    if cli_result.available and cli_result.command:
        env_entries.append(f'export SDD_CLI_COMMAND="{cli_result.command}"')

    tmp_path = env_file + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
        for entry in env_entries:
            f.write(entry + "\n")
    os.replace(tmp_path, env_file)


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


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-SDD session start script")
    parser.add_argument("--default-lang", default="en", help="Default language (en/ja)")
    args = parser.parse_args()

    plugin_root = get_plugin_root()
    project_root = get_project_root()
    config_path = os.path.join(project_root, ".sdd-config.json")

    raw_config = load_or_create_config(config_path, args.default_lang)
    local_config = load_local_config(project_root)
    merged_config = merge_configs(raw_config, local_config)
    cfg = build_sdd_config(merged_config, args.default_lang)

    sdd_dir = os.path.join(project_root, cfg.root)
    ensure_sdd_directory(sdd_dir, cfg.root)

    plugin_version = get_plugin_version(plugin_root)
    sync_principles_file(plugin_root, sdd_dir, plugin_version)

    cli_result = detect_cli(cfg.cli)
    write_env_vars(cfg, cli_result)

    check_claude_md(project_root, sdd_dir, plugin_version)


if __name__ == "__main__":
    main()
