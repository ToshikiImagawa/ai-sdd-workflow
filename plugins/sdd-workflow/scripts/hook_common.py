"""hook_common.py - Shared helpers for hook scripts.

Provides stdin JSON parsing, project root resolution,
.sdd-config.json loading, and hook output emission.
"""

import json
import os
import sys
from typing import Any, Dict, Tuple


def read_stdin_json() -> Dict[str, Any]:
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def get_project_root(payload: Dict[str, Any]) -> str:
    cwd = payload.get("cwd", "")
    if cwd and os.path.isdir(cwd):
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
    config_path = os.path.join(project_root, ".sdd-config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, encoding="utf-8") as f:
                raw = json.load(f)
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
    abs_path = os.path.abspath(file_path)
    abs_root = os.path.abspath(project_root)
    if not abs_path.startswith(abs_root + os.sep):
        return ""
    return os.path.relpath(abs_path, abs_root)
