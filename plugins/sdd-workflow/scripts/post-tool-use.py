#!/usr/bin/env python3
"""post-tool-use.py - PostToolUse hook script (Write|Edit).

Detects potential document update omissions after a file edit:
- .sdd spec/PRD edited: reminds to check PRD <-> spec <-> adr consistency
- .sdd adr/ edited: reminds that decision logs are append-only and must stay
  consistent with the spec
- source file edited with a matching spec: reminds to keep the spec in sync.
  The sync target is the spec, not a design doc: new design docs are temporary
  drafts under task/{ticket-number}/ and are deleted after implementation.
- source file edited where only a v4.x persisted specification/{stem}_design.md
  matches: reminds to migrate that file's decisions into adr/ (a separate
  message, since the design doc is not a spec sync target).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_common import (  # noqa: E402
    SOURCE_EXTENSIONS,
    SddPaths,
    emit_additional_context,
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)
from doc_walker import find_spec_or_legacy_design_doc  # noqa: E402


def readme_pointer() -> str:
    """A path the agent can open for the "Migration from v4.x" README section.

    The reminder text is consumed by the AI agent, so it names a file rather
    than "the plugin README". Falls back to the ``${CLAUDE_PLUGIN_ROOT}`` token
    when the hook process did not inherit the variable, which is still
    resolvable in-session.
    """
    base = os.environ.get("CLAUDE_PLUGIN_ROOT", "") or "${CLAUDE_PLUGIN_ROOT}"
    return f"{base}/README.md"


def try_update_index(project_root: str, rel_path: str) -> None:
    try:
        import sdd_index
        sdd_index.update_one(project_root, rel_path)
    except Exception as e:  # noqa: BLE001
        print(f"[AI-SDD] Warning: index update failed for '{rel_path}': {e}",
              file=sys.stderr)


def _extract_file_paths(payload: dict) -> list:
    """Extract file paths from a Write/Edit tool_input.

    Falls back to a batch-edit payload shape (tool_input["edits"][].file_path)
    so a future batch-write tool needs no change here.
    """
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


# (SddPaths prefix attribute, reindex the document, reminder message).
# Order matters only within this table; the .sdd/ catch-all lives after the loop
# in _process_sdd_doc, so adding a directory here cannot be silently swallowed.
DOC_REMINDERS = (
    (
        "specification_prefix",
        True,
        "[AI-SDD] '{rel_path}' was updated. Verify consistency across "
        "PRD <-> spec <-> adr (requirement ID references, data models, "
        "API definitions). Consider running the doc-consistency-checker skill and "
        "/constitution validate to check for principle violations.",
    ),
    (
        "requirement_prefix",
        True,
        "[AI-SDD] '{rel_path}' (PRD) was updated. Verify that downstream "
        "spec documents reflect the change "
        "(new/changed UR/FR/NFR must propagate). Consider running the "
        "doc-consistency-checker skill and /constitution validate to check for "
        "principle violations.",
    ),
    (
        "adr_prefix",
        True,
        "[AI-SDD] '{rel_path}' (ADR) was updated. Decision logs are "
        "append-only: verify past entries were not rewritten, and that any "
        "decision changing the specification is reflected in the "
        "corresponding spec.",
    ),
)


def _process_sdd_doc(rel: Path, rel_path: str, project_root: str,
                     paths: SddPaths) -> bool:
    """Emit the reminder for a .sdd/ document. True if the path was handled."""
    if not rel.is_relative_to(paths.root):
        return False
    if rel.suffix == ".md":
        for prefix_attr, reindex, message in DOC_REMINDERS:
            if not rel.is_relative_to(getattr(paths, prefix_attr)):
                continue
            if reindex:
                try_update_index(project_root, rel_path)
            emit_additional_context(
                "PostToolUse", message.format(rel_path=rel_path),
            )
            return True
    # Any other .sdd/ file (CONSTITUTION.md, task/, templates): no reminder.
    return True


def _process_source_file(rel: Path, rel_path: str, project_root: str,
                         paths: SddPaths) -> None:
    """Remind to sync the matching spec after a source file edit."""
    if rel.suffix not in SOURCE_EXTENSIONS:
        return

    spec_dir = Path(project_root) / paths.specification_prefix
    if not spec_dir.is_dir():
        return

    # A single directory walk resolves both candidates instead of walking
    # specification/ up to three times (find_spec_doc alone tries two suffix
    # candidates, and find_legacy_design_doc would be a third walk).
    spec_doc, design_doc = find_spec_or_legacy_design_doc(str(spec_dir), rel.stem)
    if spec_doc:
        spec_rel = str(Path(spec_doc).relative_to(Path(project_root)))
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' was updated and a matching specification "
            f"'{spec_rel}' exists. If the public API, data model, or behavior "
            "changed, update the specification to keep it as the source of "
            "truth (/check-spec verifies spec <-> implementation consistency).",
        )
        return

    # No spec, but a v4.x persisted design doc may still describe this file.
    # It stays valid as supplementary input, so the reminder points at the adr/
    # migration rather than treating the design doc as a sync target.
    if not design_doc:
        return

    design_rel = str(Path(design_doc).relative_to(Path(project_root)))
    emit_additional_context(
        "PostToolUse",
        f"[AI-SDD] '{rel_path}' was updated and a v4.x design document "
        f"'{design_rel}' exists, but no specification matches it. Read the "
        "design doc as supplementary input (it stays valid, and it is not a "
        "naming violation). It may stay until the decisions it records have "
        f"been moved into '{paths.adr_prefix}/{{feature-name}}.md' - that "
        f"migration is human-paced; the steps are in '{readme_pointer()}', "
        "section \"Extracting Existing `*_design.md` Files into `adr/`\" under "
        "\"Migration from v4.x\". Keep the design doc until that is done.",
    )


def _process_single_file(rel_path: str, project_root: str,
                         paths: SddPaths) -> None:
    rel = Path(rel_path)
    if _process_sdd_doc(rel, rel_path, project_root, paths):
        return
    _process_source_file(rel, rel_path, project_root, paths)


def main() -> None:
    payload = read_stdin_json()
    file_paths = _extract_file_paths(payload)
    if not file_paths:
        return

    project_root = get_project_root(payload)
    paths = load_sdd_paths(project_root)

    for file_path in file_paths:
        rel_path = relative_to_project(file_path, project_root)
        if not rel_path:
            continue
        _process_single_file(rel_path, project_root, paths)


if __name__ == "__main__":
    main()
