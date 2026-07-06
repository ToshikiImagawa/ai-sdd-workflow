#!/usr/bin/env python3
"""pre-tool-use.py - PreToolUse hook script (Write|Edit|MultiEdit).

Validates AI-SDD file naming conventions before writing to .sdd/ documents:
- requirement/: no _spec/_design suffix allowed
- specification/: _spec.md or _design.md suffix required

Blocks the tool call (exit 2) on violation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_common import (  # noqa: E402
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)


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
        print(error, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
