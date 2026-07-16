#!/usr/bin/env python3
"""pre-tool-use.py - PreToolUse hook script (Write|Edit|MultiEdit).

Validates AI-SDD file naming conventions before writing to .sdd/ documents:
- requirement/: no _spec/_design suffix allowed
- specification/: _spec.md or _design.md suffix required

Blocks the tool call via JSON Decision Control (permissionDecision: "deny")
on violation.

When the write target is implementation source code, injects the project's
CONSTITUTION.md principles as additionalContext. To avoid context bloat:
- only source files inside the project are targeted
- injection happens at most once per session (marker file keyed by session_id)
- the injected text is truncated to CONSTITUTION_MAX_CHARS
"""

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_common import (  # noqa: E402
    SOURCE_EXTENSIONS,
    emit_additional_context,
    emit_permission_deny,
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)
from naming import validate_naming  # noqa: E402,F401

CONSTITUTION_MAX_CHARS = 3000


def session_marker_path(session_id: str) -> str:
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
    return str(Path(tempfile.gettempdir()) / f"sdd-constitution-injected-{safe_id}")


def load_constitution(project_root: str, sdd_root: str) -> str:
    """Return the CONSTITUTION.md content (truncated), or '' if absent."""
    path = Path(project_root) / sdd_root / "CONSTITUTION.md"
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if len(text) > CONSTITUTION_MAX_CHARS:
        text = text[:CONSTITUTION_MAX_CHARS] + "\n... (truncated; see the full file)"
    return text


def maybe_inject_constitution(rel_path: str, project_root: str, sdd_root: str, session_id: str) -> None:
    if Path(rel_path).suffix not in SOURCE_EXTENSIONS:
        return

    marker = ""
    if session_id:
        marker = session_marker_path(session_id)
        if Path(marker).exists():
            return

    text = load_constitution(project_root, sdd_root)
    if not text:
        return

    if marker:
        try:
            Path(marker).write_text(rel_path, encoding="utf-8")
        except OSError:
            pass

    constitution_rel = str(Path(sdd_root) / "CONSTITUTION.md")
    emit_additional_context(
        "PreToolUse",
        f"[AI-SDD] You are editing implementation code ('{rel_path}'). "
        f"Follow the project principles defined in '{constitution_rel}':\n\n{text}",
    )


def main() -> None:
    payload = read_stdin_json()
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return

    project_root = get_project_root(payload)
    rel_path = relative_to_project(file_path, project_root)
    if not rel_path:
        return

    sdd_root, requirement_dir, specification_dir = load_sdd_paths(project_root)
    requirement_prefix = str(Path(sdd_root) / requirement_dir)
    specification_prefix = str(Path(sdd_root) / specification_dir)

    error = validate_naming(rel_path, requirement_prefix, specification_prefix)
    if error:
        emit_permission_deny("PreToolUse", error)
        return

    if not Path(rel_path).is_relative_to(sdd_root):
        maybe_inject_constitution(rel_path, project_root, sdd_root, payload.get("session_id", ""))


if __name__ == "__main__":
    main()
