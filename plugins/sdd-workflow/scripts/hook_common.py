"""hook_common.py - Shared helpers for hook scripts.

Provides stdin JSON parsing, project root resolution,
.sdd-config.json loading, and hook output emission.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Tuple


def read_stdin_json() -> Dict[str, Any]:
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def resolve_project_root(preferred: str = "") -> str:
    """Resolve the project root: preferred value, else CLAUDE_PROJECT_DIR,
    else the git top-level, else the current working directory.

    Shared by CLI-style scripts (sdd_index, session-start, skill helpers) that
    need a git fallback. The hook path uses get_project_root() instead, which
    prefers the payload cwd.
    """
    if preferred:
        return preferred
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


def get_project_root(payload: Dict[str, Any]) -> str:
    cwd = payload.get("cwd", "")
    if cwd and Path(cwd).is_dir():
        return cwd
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        return project_dir
    return os.getcwd()


def load_sdd_paths(project_root: str) -> Tuple[str, str, str]:
    """Return (sdd_root, requirement_dir, specification_dir) names."""
    root = ".sdd"
    requirement_dir = "requirement"
    specification_dir = "specification"
    config_path = Path(project_root) / ".sdd-config.json"
    if config_path.is_file():
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
            if raw.get("root"):
                root = raw["root"]
            dirs = raw.get("directories", {})
            if dirs.get("requirement"):
                requirement_dir = dirs["requirement"]
            if dirs.get("specification"):
                specification_dir = dirs["specification"]
        except (json.JSONDecodeError, OSError):
            pass
    return root, requirement_dir, specification_dir


SOURCE_EXTENSIONS = (
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java",
    ".kt", ".swift", ".cs", ".rb", ".php", ".c", ".cc", ".cpp", ".h",
)


def emit_permission_deny(event_name: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }, ensure_ascii=False))


def emit_additional_context(event_name: str, text: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        },
    }, ensure_ascii=False))


def relative_to_project(file_path: str, project_root: str) -> str:
    """Return file_path relative to project_root, or '' if outside."""
    abs_path = Path(file_path).resolve()
    abs_root = Path(project_root).resolve()
    try:
        return str(abs_path.relative_to(abs_root))
    except ValueError:
        return ""
