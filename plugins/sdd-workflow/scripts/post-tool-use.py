#!/usr/bin/env python3
"""post-tool-use.py - PostToolUse hook script (Write|Edit|MultiEdit).

Detects potential document update omissions after a file edit:
- .sdd document edited: reminds to check PRD <-> spec <-> design consistency
- source file edited with a matching *_design.md: reminds to keep the design doc in sync
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_common import (  # noqa: E402
    SOURCE_EXTENSIONS,
    emit_additional_context,
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)


def find_design_doc(spec_dir: str, stem: str) -> str:
    """Return the relative path of {stem}_design.md under spec_dir, or ''."""
    target = f"{stem}_design.md"
    for dirpath, _dirnames, filenames in os.walk(spec_dir):
        if target in filenames:
            return os.path.join(dirpath, target)
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

    if rel_path.startswith(specification_prefix + os.sep) and rel_path.endswith(".md"):
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' was updated. Verify consistency across "
            "PRD <-> *_spec.md <-> *_design.md (requirement ID references, data models, "
            "API definitions). Consider running the doc-consistency-checker skill.",
        )
        return

    if rel_path.startswith(requirement_prefix + os.sep) and rel_path.endswith(".md"):
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' (PRD) was updated. Verify that downstream "
            "*_spec.md / *_design.md documents reflect the change "
            "(new/changed UR/FR/NFR must propagate). Consider running the "
            "doc-consistency-checker skill.",
        )
        return

    if rel_path.startswith(sdd_root + os.sep):
        return

    _root, ext = os.path.splitext(rel_path)
    if ext not in SOURCE_EXTENSIONS:
        return

    spec_dir = os.path.join(project_root, specification_prefix)
    if not os.path.isdir(spec_dir):
        return

    stem = os.path.basename(rel_path)[: -len(ext)]
    design_doc = find_design_doc(spec_dir, stem)
    if design_doc:
        design_rel = os.path.relpath(design_doc, project_root)
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' was updated and a matching design document "
            f"'{design_rel}' exists. If the implementation behavior changed, "
            "update the design document to keep it as the source of truth.",
        )


if __name__ == "__main__":
    main()
