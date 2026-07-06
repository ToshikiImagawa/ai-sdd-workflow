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

import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_common import (  # noqa: E402
    SOURCE_EXTENSIONS,
    emit_additional_context,
    emit_permission_deny,
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)

CONSTITUTION_MAX_CHARS = 3000


def validate_naming(rel_path: str, requirement_prefix: str, specification_prefix: str) -> str:
    """Return an error message if rel_path violates naming conventions, else ''."""
    if not rel_path.endswith(".md"):
        return ""
    stem = os.path.basename(rel_path)[: -len(".md")]

    if rel_path.startswith(requirement_prefix + os.sep):
        if stem.endswith("_spec") or stem.endswith("_design"):
            return (
                f"[AI-SDD] Naming violation: '{rel_path}'. "
                "Files under requirement/ must not have a _spec/_design suffix "
                "(e.g. user-login.md, index.md)."
            )
    elif rel_path.startswith(specification_prefix + os.sep):
        if not (stem.endswith("_spec") or stem.endswith("_design")):
            return (
                f"[AI-SDD] Naming violation: '{rel_path}'. "
                "Files under specification/ require a _spec.md or _design.md suffix "
                "(e.g. user-login_spec.md, index_design.md)."
            )
    return ""


def session_marker_path(session_id: str) -> str:
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
    return os.path.join(tempfile.gettempdir(), f"sdd-constitution-injected-{safe_id}")


def load_constitution(project_root: str, sdd_root: str) -> str:
    """Return the CONSTITUTION.md content (truncated), or '' if absent."""
    path = os.path.join(project_root, sdd_root, "CONSTITUTION.md")
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
    except OSError:
        return ""
    if len(text) > CONSTITUTION_MAX_CHARS:
        text = text[:CONSTITUTION_MAX_CHARS] + "\n... (truncated; see the full file)"
    return text


def maybe_inject_constitution(rel_path: str, project_root: str, sdd_root: str, session_id: str) -> None:
    _stem, ext = os.path.splitext(rel_path)
    if ext not in SOURCE_EXTENSIONS:
        return

    marker = ""
    if session_id:
        marker = session_marker_path(session_id)
        if os.path.exists(marker):
            return

    text = load_constitution(project_root, sdd_root)
    if not text:
        return

    if marker:
        try:
            with open(marker, "w", encoding="utf-8") as f:
                f.write(rel_path)
        except OSError:
            pass

    constitution_rel = os.path.join(sdd_root, "CONSTITUTION.md")
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
    requirement_prefix = os.path.join(sdd_root, requirement_dir)
    specification_prefix = os.path.join(sdd_root, specification_dir)

    error = validate_naming(rel_path, requirement_prefix, specification_prefix)
    if error:
        emit_permission_deny("PreToolUse", error)
        return

    if not rel_path.startswith(sdd_root + os.sep):
        maybe_inject_constitution(rel_path, project_root, sdd_root, payload.get("session_id", ""))


if __name__ == "__main__":
    main()
