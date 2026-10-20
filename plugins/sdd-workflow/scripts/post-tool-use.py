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
- Bend law file (.bend) edited under the laws directory: reminds to re-run the
  proof gate (and, for LAWS.bend, to get the laws re-approved).
- spec with a ``laws:`` front matter list edited: suggests re-running
  ``/draft-laws`` when a law's ``# source:`` section hash no longer matches
  (non-blocking; names the drifted laws when they can be determined cheaply).
- source file edited that a laws/**/main.bend names in a ``# model-of:`` line:
  reminds to review the reference model and the laws. Independent of the spec
  sync reminder, so both may be injected for one edit.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_common import (  # noqa: E402
    SOURCE_EXTENSIONS,
    SddPaths,
    emit_additional_context as _emit_json,
    get_project_root,
    load_sdd_paths,
    read_stdin_json,
    relative_to_project,
)
from doc_walker import find_spec_or_legacy_design_doc  # noqa: E402
from fm_parser import parse_front_matter, split_front_matter  # noqa: E402
from laws_header import LAWS_FILE, MODEL_FILE, read_header  # noqa: E402


_MESSAGES: list = []


def emit_additional_context(event_name: str, text: str) -> None:
    """Queue a reminder; flush_messages() prints them as ONE additionalContext JSON.

    Several reminders can apply to one edit (e.g. spec sync + laws re-draft), and
    a hook is expected to print a single JSON object on stdout.
    """
    _MESSAGES.append((event_name, text))


def flush_messages() -> None:
    if not _MESSAGES:
        return
    event_name = _MESSAGES[0][0]
    text = "\n\n".join(t for _, t in _MESSAGES)
    _MESSAGES.clear()
    _emit_json(event_name, text)


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
    if rel.suffix == ".bend" and rel.is_relative_to(paths.laws_prefix):
        _process_laws_file(rel, rel_path, project_root, paths)
        return True
    if rel.suffix == ".md":
        for prefix_attr, reindex, message in DOC_REMINDERS:
            if not rel.is_relative_to(getattr(paths, prefix_attr)):
                continue
            if reindex:
                try_update_index(project_root, rel_path)
            emit_additional_context(
                "PostToolUse", message.format(rel_path=rel_path),
            )
            if prefix_attr == "specification_prefix":
                _process_spec_laws(rel, rel_path, project_root, paths)
            return True
    # Any other .sdd/ file (CONSTITUTION.md, task/, templates): no reminder.
    return True


def _process_laws_file(rel: Path, rel_path: str, project_root: str,
                       paths: SddPaths) -> None:
    """Remind to re-run the proof gate after a law file edit (FR-007)."""
    laws_dir = rel.parent
    feature = laws_dir.relative_to(paths.laws_prefix).as_posix()
    spec_id = ""
    laws_file = Path(project_root) / laws_dir / LAWS_FILE
    if laws_file.is_file():
        values = read_header(laws_file).get("spec", [])
        spec_id = values[0] if values else ""
    owner = f" (laws of '{spec_id}')" if spec_id else ""
    message = (
        f"[AI-SDD] '{rel_path}' was updated{owner}. Re-run "
        f"/run-checklist {feature} {{ticket}} --category proof."
    )
    if rel.name == LAWS_FILE:
        message += (
            " An edited LAWS.bend needs re-approval: its content hash changed, so the "
            "existing '# approved:' line no longer applies (a human appends a new one; "
            "get the hash with run-verification.py proof --print-laws-hash)."
        )
    emit_additional_context("PostToolUse", message)


def _process_spec_laws(rel: Path, rel_path: str, project_root: str,
                       paths: SddPaths) -> None:
    """Suggest re-drafting laws after a spec with ``laws:`` changed (FR-011)."""
    spec_file = Path(project_root) / rel
    try:
        text = spec_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    fm_text, _ = split_front_matter(text)
    laws = parse_front_matter(fm_text).get("laws") if fm_text else None
    if isinstance(laws, str):
        laws = [laws]
    if not laws:
        return
    drifted = []
    for entry in laws:
        laws_file = Path(project_root) / paths.root / str(entry).strip().strip("/") / LAWS_FILE
        # An absolute .sdd-config.json root puts the laws outside the project (#151).
        if not relative_to_project(str(laws_file), project_root) or not laws_file.is_file():
            continue
        try:
            import laws_drafting
            for w in laws_drafting.source_drift(laws_file, spec_file):
                drifted.append(f"{w['law']} (§{w['source']}, {w['code']})")
        except Exception:  # noqa: BLE001 - a reminder must never fail the hook
            continue
    message = (
        f"[AI-SDD] '{rel_path}' declares laws ({', '.join(str(x) for x in laws)}). "
        "If the spec sections the laws were drafted from changed, consider re-running "
        "/draft-laws to re-extract them, then have a human re-approve."
    )
    if drifted:
        message += (" Laws whose '# source:' no longer matches the spec: "
                    + "; ".join(drifted) + ".")
    emit_additional_context("PostToolUse", message)


def _process_model_of(rel: Path, rel_path: str, project_root: str,
                      paths: SddPaths) -> None:
    """Remind to review laws whose reference model says it mirrors this file (FR-008)."""
    laws_root = Path(project_root) / paths.laws_prefix
    if not laws_root.is_dir():
        return
    target = rel.as_posix()
    for model in sorted(laws_root.rglob(MODEL_FILE)):
        try:
            mirrored = read_header(model).get("model-of", [])
        except OSError:
            continue
        if target not in (m.strip().replace("\\", "/") for m in mirrored):
            continue
        # An absolute .sdd-config.json root puts laws_root outside the project
        # (issue #151); such a model is out of scope, not an error.
        model_rel = relative_to_project(str(model), project_root)
        if not model_rel:
            continue
        model_rel = Path(model_rel).as_posix()
        feature = model.parent.relative_to(laws_root).as_posix()
        emit_additional_context(
            "PostToolUse",
            f"[AI-SDD] '{rel_path}' is modeled by '{model_rel}' (# model-of:). If its "
            "behavior changed, review the reference model and LAWS.bend, then re-run the "
            f"proof gate (/run-checklist {feature} {{ticket}} --category proof). A passing "
            "proof only covers the reference model, not this implementation.",
        )


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
    # With an absolute .sdd-config.json "root" the matched document lives
    # outside the project; relative_to_project returns '' instead of raising
    # (issue #151). Such documents are out of scope: skip the reminder rather
    # than fail the hook. session-start.py warns about the unsupported root.
    if spec_doc:
        spec_rel = relative_to_project(spec_doc, project_root)
        if not spec_rel:
            return
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

    design_rel = relative_to_project(design_doc, project_root)
    if not design_rel:
        return
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
                         paths: SddPaths, flush: bool = True) -> None:
    try:
        rel = Path(rel_path)
        if _process_sdd_doc(rel, rel_path, project_root, paths):
            return
        _process_source_file(rel, rel_path, project_root, paths)
        if rel.suffix in SOURCE_EXTENSIONS:
            _process_model_of(rel, rel_path, project_root, paths)
    finally:
        if flush:
            flush_messages()


def main() -> None:
    payload = read_stdin_json()
    file_paths = _extract_file_paths(payload)
    if not file_paths:
        return

    project_root = get_project_root(payload)
    paths = load_sdd_paths(project_root)

    for file_path in file_paths:
        # Files outside the project are out of scope (issue #151).
        rel_path = relative_to_project(file_path, project_root)
        if not rel_path:
            continue
        _process_single_file(rel_path, project_root, paths, flush=False)
    flush_messages()


if __name__ == "__main__":
    main()
