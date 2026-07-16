#!/usr/bin/env python3
"""post-tool-use.py - PostToolUse hook script (Write|Edit|MultiEdit).

Detects potential document update omissions after a file edit:
- .sdd document edited: reminds to check PRD <-> spec <-> design consistency
- source file edited with a matching *_design.md: reminds to keep the design doc in sync
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_common import (  # noqa: E402
    SOURCE_EXTENSIONS,
    emit_additional_context,
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)
from doc_walker import find_design_doc  # noqa: E402,F401


def try_update_index(project_root: str, rel_path: str) -> None:
    try:
        import sdd_index
        sdd_index.update_one(project_root, rel_path)
    except Exception as e:  # noqa: BLE001
        print(f"[AI-SDD] Warning: index update failed for '{rel_path}': {e}",
              file=sys.stderr)


def _extract_file_paths(payload: dict) -> list:
    """Extract file paths from Write, Edit, or MultiEdit tool_input."""
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if file_path:
        return [file_path]
    edits = tool_input.get("edits", [])
    seen: set = set()
    result = []
    for edit in edits:
        p = edit.get("file_path", "")
        if p and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _process_single_file(rel_path: str, project_root: str,
                         sdd_root: str, requirement_prefix: str,
                         specification_prefix: str) -> None:
    rel = Path(rel_path)
    if rel.is_relative_to(specification_prefix) and rel.suffix == ".md":
        try_update_index(project_root, rel_path)
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' was updated. Verify consistency across "
            "PRD <-> *_spec.md <-> *_design.md (requirement ID references, data models, "
            "API definitions). Consider running the doc-consistency-checker skill and "
            "/constitution validate to check for principle violations.",
        )
        return

    if rel.is_relative_to(requirement_prefix) and rel.suffix == ".md":
        try_update_index(project_root, rel_path)
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' (PRD) was updated. Verify that downstream "
            "*_spec.md / *_design.md documents reflect the change "
            "(new/changed UR/FR/NFR must propagate). Consider running the "
            "doc-consistency-checker skill and /constitution validate to check for "
            "principle violations.",
        )
        return

    if rel.is_relative_to(sdd_root):
        return

    if rel.suffix not in SOURCE_EXTENSIONS:
        return

    spec_dir = Path(project_root) / specification_prefix
    if not spec_dir.is_dir():
        return

    design_doc = find_design_doc(str(spec_dir), rel.stem)
    if design_doc:
        design_rel = str(Path(design_doc).relative_to(Path(project_root)))
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' was updated and a matching design document "
            f"'{design_rel}' exists. If the implementation behavior changed, "
            "update the design document to keep it as the source of truth.",
        )


def main() -> None:
    payload = read_stdin_json()
    file_paths = _extract_file_paths(payload)
    if not file_paths:
        return

    project_root = get_project_root(payload)
    sdd_root, requirement_dir, specification_dir = load_sdd_paths(project_root)
    requirement_prefix = str(Path(sdd_root) / requirement_dir)
    specification_prefix = str(Path(sdd_root) / specification_dir)

    for file_path in file_paths:
        rel_path = relative_to_project(file_path, project_root)
        if not rel_path:
            continue
        _process_single_file(
            rel_path, project_root, sdd_root,
            requirement_prefix, specification_prefix,
        )


if __name__ == "__main__":
    main()
