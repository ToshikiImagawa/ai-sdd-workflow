"""hook_common.py - Shared helpers for hook scripts.

Provides stdin JSON parsing, project root resolution,
.sdd-config.json loading, and hook output emission.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


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


@dataclass(frozen=True)
class SddPaths:
    """Resolved ``.sdd`` directory names, plus their project-relative prefixes.

    Returned as an object rather than a tuple so adding a directory (``adr`` and
    ``task`` arrived after ``requirement``/``specification``) does not churn every
    call site. Keep the field names in sync with the ``directories`` keys written
    by sdd-init.
    """

    root: str = ".sdd"
    requirement_dir: str = "requirement"
    specification_dir: str = "specification"
    adr_dir: str = "adr"
    task_dir: str = "task"

    @property
    def requirement_prefix(self) -> str:
        return str(Path(self.root) / self.requirement_dir)

    @property
    def specification_prefix(self) -> str:
        return str(Path(self.root) / self.specification_dir)

    @property
    def adr_prefix(self) -> str:
        return str(Path(self.root) / self.adr_dir)

    @property
    def task_prefix(self) -> str:
        return str(Path(self.root) / self.task_dir)


# Field name -> .sdd-config.json "directories" key.
_DIR_FIELDS = {
    "requirement_dir": "requirement",
    "specification_dir": "specification",
    "adr_dir": "adr",
    "task_dir": "task",
}


def read_sdd_config_json(project_root: str) -> dict:
    """Read and parse .sdd-config.json, or {} if absent/invalid.

    Callers that need more than one config-derived value in the same
    invocation (e.g. both the directory layout and the naming ignore
    patterns) should read this once and pass it as the ``raw`` argument to
    :func:`load_sdd_paths` / :func:`load_naming_ignore_patterns` instead of
    letting each of them re-read and re-parse the file.
    """
    config_path = Path(project_root) / ".sdd-config.json"
    if not config_path.is_file():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def load_sdd_paths(project_root: str, raw: Optional[dict] = None) -> SddPaths:
    """Resolve the .sdd directory layout from .sdd-config.json, else defaults.

    Pass an already-parsed ``raw`` config dict to avoid re-reading the file.
    """
    if raw is None:
        raw = read_sdd_config_json(project_root)

    dirs = raw.get("directories") or {}
    resolved = {
        field: dirs[key] for field, key in _DIR_FIELDS.items() if dirs.get(key)
    }
    if raw.get("root"):
        resolved["root"] = raw["root"]
    return SddPaths(**resolved)


def resolve_lang_and_root(project_root: Path) -> Tuple[str, str]:
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


def load_naming_ignore_patterns(project_root: str, raw: Optional[dict] = None) -> Tuple[str, ...]:
    """Return the naming.ignore_patterns glob list from .sdd-config.json, or () if absent.

    Patterns are ``fnmatch`` globs (e.g. ``"*_test.md"``) matched against a
    file's basename by ``naming.validate_naming``. Pass an already-parsed
    ``raw`` config dict to avoid re-reading the file.
    """
    if raw is None:
        raw = read_sdd_config_json(project_root)
    patterns = raw.get("naming", {}).get("ignore_patterns", [])
    if not isinstance(patterns, list):
        return ()
    return tuple(p for p in patterns if isinstance(p, str))


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
