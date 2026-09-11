#!/usr/bin/env python3
"""
find-spec-docs.py
Find specification documents and related files for /check-spec
Reduces Claude's Glob/Grep overhead by pre-scanning file structure

The comparison baseline is the abstract specification under specification/
(the ``_spec`` suffix is optional). Technical design documents live at
``task/{ticket-number}/design-draft.md`` and are deleted after implementation,
so they are collected as an *optional* auxiliary input: their absence is the
normal state, never a warning.

Design drafts are ticket-scoped. Several tickets may be in flight at once, so a
draft is only attached to the check when it can be tied to the run:
``--ticket <n>`` (or ``--ticket=<n>``) selects one ticket directory; otherwise a
draft's front matter ``depends-on`` is matched against the target specs' IDs.
When neither basis resolves and more than one draft exists, no draft is attached
and the drafts are reported as unscoped so the caller can re-run with
``--ticket``.

Decision logs under ``adr/`` are feature-scoped rather than ticket-scoped, so
they are attributed by name first (``adr/[{parent}/]{feature}.md`` and the legacy
``adr/[{parent}/]{feature}-decisions.md``, both still valid) and, when no such
file exists, by an adr's front matter ``depends-on`` referencing the spec's IDs —
the same ``depends-on`` basis used for drafts. They are collected so
``--full``'s spec <-> adr document review has its input; having no adr file is
the normal state for a feature whose decisions are not recorded yet, so an empty
result is never an error.
"""

import glob
import json
import sys
from pathlib import Path

# Shared modules live in plugins/sdd-workflow/scripts (three levels up + scripts).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from doc_walker import iter_all_markdown, iter_specification_docs  # noqa: E402
from env_export import rewrite_exports  # noqa: E402
from fm_parser import parse_front_matter, split_front_matter  # noqa: E402
from hook_common import SddPaths, load_sdd_paths, resolve_project_root  # noqa: E402
from naming import DESIGN_SUFFIX, SPEC_SUFFIX, feature_name, is_design_stem  # noqa: E402

# Design drafts are ticket-scoped with a fixed filename, so they cannot be
# matched to a spec by stem.
DESIGN_DRAFT_NAME = "design-draft.md"
TICKET_FLAG = "--ticket"
SPEC_ID_PREFIX = "spec-"
# adr/ is a single-type directory, so the suffix is optional: new decision logs
# are `{feature}.md` and existing `{feature}-decisions.md` files stay valid.
ADR_LEGACY_SUFFIX = "-decisions"


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[find-spec-docs] {message}", file=sys.stderr)


def read_config(project_root: Path) -> SddPaths:
    """Resolve the .sdd layout: .sdd-config.json if present, else defaults"""
    return load_sdd_paths(str(project_root))


def sorted_docs(paths) -> list:
    """Sorted unique file paths, excluding v4.x persisted design docs by name.

    A ``{feature}_design.md`` is a design doc, not a spec (see
    naming.is_design_stem), so it never enters the result. This filename-only
    check is safe for *any* file collection where "ends in ``_design``" is
    never a false positive -- e.g. ``task/{ticket}/design-draft.md`` (whose
    stem is ``design-draft``, not ``*_design``) passes through unaffected. For
    the specification/ document list specifically, where a legitimately named
    new spec can itself end in ``_design`` (e.g. ``api_design.md``), use
    :func:`sorted_spec_docs` instead -- it disambiguates via front matter
    ``type`` before falling back to this same filename heuristic.
    """
    return sorted({
        str(p) for p in paths if p.is_file() and not is_design_stem(p.stem)
    })


def sorted_spec_docs(paths) -> list:
    """Like :func:`sorted_docs`, but for the specification/ document list.

    The ``_spec`` suffix is optional under specification/, so a *new*,
    legitimately named spec can itself end in ``_design`` (e.g.
    ``api_design.md``) -- the filename heuristic alone cannot tell that apart
    from a v4.x persisted design doc. A file's own front matter ``type``
    overrides the heuristic when declared: ``type: spec`` keeps the file even
    though its stem ends in ``_design``, and ``type: design`` excludes it even
    when the stem does not. Files without a declared ``type`` (the common case
    for legacy v4.x design docs, which predate this field) fall back to the
    filename heuristic, same as :func:`sorted_docs`.
    """
    result = set()
    for p in paths:
        if not p.is_file():
            continue
        declared_type = read_front_matter(p).get("type", "")
        if declared_type == "spec":
            is_design = False
        elif declared_type == "design":
            is_design = True
        else:
            is_design = is_design_stem(p.stem)
        if not is_design:
            result.add(str(p))
    return sorted(result)


def write_lines(path: Path, lines: list) -> None:
    """Write lines to a file, one per line (mirrors `... > file`)"""
    content = "".join(f"{line}\n" for line in lines)
    path.write_text(content, encoding="utf-8")


def find_spec_documents(specification_path: Path, target: str) -> list:
    """Locate the spec documents to check, as sorted path strings.

    Both naming forms are matched because the ``_spec`` suffix is optional under
    specification/: ``{feature}_spec.md`` and ``{feature}.md``.
    """
    log("Scanning specification documents...")

    if not specification_path.is_dir():
        log(f"ERROR: Specification directory not found: {specification_path}")
        sys.exit(1)

    if not target:
        log("Searching for all specification documents...")
        specs = sorted_spec_docs(iter_specification_docs(specification_path))
        log(f"Found {len(specs)} specification documents")
        return specs

    log(f"Searching for feature: {target}")

    # Exact matches first: flat (both suffix forms), then a feature directory
    # (hierarchical structure, e.g. auth/index.md + auth/user-login_spec.md).
    specs = sorted_spec_docs([
        specification_path / f"{target}{SPEC_SUFFIX}.md",
        specification_path / f"{target}.md",
        *iter_all_markdown(specification_path / target),
    ])
    if specs:
        log(f"Found {len(specs)} specification file(s) for: {target}")
        return specs

    # Fall back to partial matches
    specs = sorted_spec_docs(specification_path.rglob(f"*{glob.escape(target)}*.md"))
    if specs:
        log(f"Found {len(specs)} matching specification file(s)")
    else:
        log(f"WARNING: No specification document found for: {target}")
    return specs


def read_front_matter(path: Path) -> dict:
    """Parse a document's front matter, tolerating unreadable files."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    fm_text, _ = split_front_matter(text)
    if not fm_text:
        return {}
    return parse_front_matter(fm_text)


def spec_identifiers(specs: list, specification_path: Path) -> set:
    """Collect the IDs a design draft may reference for the target specs.

    Both the declared front matter ``id`` and the ID derived from the file's
    location (``spec-{feature}`` / ``spec-{parent}-{feature}``) are collected,
    so specs that predate front matter can still be matched.
    """
    identifiers = set()
    for spec_file in specs:
        spec_path = Path(spec_file)
        declared = read_front_matter(spec_path).get("id", "")
        if declared:
            identifiers.add(declared)

        basename = feature_name(spec_path.stem)
        identifiers.add(f"{SPEC_ID_PREFIX}{basename}")
        try:
            parent = spec_path.parent.relative_to(specification_path).parts
        except ValueError:
            parent = ()
        if parent:
            identifiers.add(
                SPEC_ID_PREFIX + "-".join([*parent, basename])
            )
    return identifiers


def find_design_drafts(task_path: Path) -> list:
    """Locate every design draft (``task/{ticket-number}/design-draft.md``).

    Optional auxiliary input: an empty result is the normal state once
    implementation completes, so it is logged without a warning. Which of these
    drafts actually belongs to the current check is decided by
    :func:`select_design_drafts`.
    """
    if not task_path.is_dir():
        log("No task directory; skipping design draft scan")
        return []

    drafts = sorted_docs(task_path.rglob(DESIGN_DRAFT_NAME))
    log(f"Found {len(drafts)} design draft(s) (optional auxiliary input)")
    return drafts


def select_design_drafts(
    drafts: list,
    ticket: str = "",
    spec_ids=frozenset(),
) -> tuple:
    """Narrow the design drafts down to the ones that belong to this check.

    Returns ``(selected, unscoped, scope)``:

    - ``selected`` — drafts to use as auxiliary input. An empty result is the
      normal state once implementation completes, so it is not a defect.
    - ``unscoped`` — drafts found but deliberately **not** attached because they
      could not be tied to this run (``scope == "unscoped"``).
    - ``scope`` — how the selection was made: ``none`` (no draft exists),
      ``ticket``, ``depends-on``, ``sole-draft``, or ``unscoped``.

    Attaching every draft in ``task/`` would mix another ticket's design into the
    check, so a draft is only used when the ticket argument or its front matter
    ``depends-on`` ties it to the target specs. A single draft is the one
    exception: with only one ticket in flight there is nothing to mix in. That
    exception does not apply to a draft whose ``depends-on`` names specs that
    exclude the target -- that is positive evidence it belongs to another
    feature, not merely an untagged draft that happens to be alone.
    """
    if not drafts:
        return [], [], "none"

    if ticket:
        scoped = [d for d in drafts if Path(d).parent.name == ticket]
        if scoped:
            log(f"Using {len(scoped)} design draft(s) for ticket: {ticket}")
        else:
            log(f"No design draft found for ticket: {ticket}")
        return scoped, [], "ticket"

    if spec_ids:
        depends_on = {d: set(read_front_matter(Path(d)).get("depends-on", []) or []) for d in drafts}
        linked = [d for d in drafts if depends_on[d] & set(spec_ids)]
        if linked:
            log(
                f"Using {len(linked)} design draft(s) linked to the target "
                "spec(s) via depends-on"
            )
            return linked, [], "depends-on"

        # A draft whose depends-on is non-empty but shares nothing with spec_ids
        # is positive evidence it belongs to another feature -- unlike a draft
        # with no depends-on at all, it must not fall through to the sole-draft
        # exception below even when it is the only draft on disk.
        conflicting = [d for d in drafts if depends_on[d]]
        candidates = [d for d in drafts if d not in conflicting]
        if conflicting and not candidates:
            log(
                f"WARNING: the only design draft found declares depends-on that "
                "does not match this check's spec(s); treating it as unscoped "
                "rather than the sole-draft exception"
            )
            return [], drafts, "unscoped"
        drafts = candidates

    if len(drafts) == 1:
        log("Using the single design draft found (only ticket in flight)")
        return drafts, [], "sole-draft"

    log(
        f"WARNING: {len(drafts)} design drafts found but none could be tied to "
        f"this check; none will be used. Re-run with {TICKET_FLAG} <number> to "
        "pick one, or add depends-on to the drafts' front matter"
    )
    return [], drafts, "unscoped"


def adr_candidates(
    adr_path: Path, spec_path: Path, specification_path: Path
) -> list:
    """Name-mirrored adr paths for a spec, in both naming forms.

    A spec's decision log sits at the same relative location under ``adr/`` as
    the spec does under ``specification/``, so a hierarchical
    ``specification/auth/user-login.md`` maps to ``adr/auth/user-login.md``.
    Both the suffix-free name and the legacy ``-decisions`` name are returned;
    either (or both) may exist.
    """
    basename = feature_name(spec_path.stem)
    try:
        parent = spec_path.parent.relative_to(specification_path)
    except ValueError:
        parent = Path(".")
    base_dir = adr_path / parent
    return [
        base_dir / f"{basename}.md",
        base_dir / f"{basename}{ADR_LEGACY_SUFFIX}.md",
    ]


def index_adr_docs(adr_path: Path) -> dict:
    """Map every adr document to the spec IDs its front matter depends on.

    Built once so the ``depends-on`` fallback below does not re-read the
    directory per spec. A missing ``adr/`` directory yields an empty index:
    unrecorded decisions are the normal state, not an error.
    """
    if not adr_path.is_dir():
        log("No adr directory; skipping decision log scan")
        return {}

    index = {
        str(p): set(read_front_matter(p).get("depends-on", []) or [])
        for p in iter_all_markdown(adr_path)
    }
    log(f"Found {len(index)} adr document(s) (optional input for --full)")
    return index


def select_adr_docs(
    spec_file: str,
    specification_path: Path,
    adr_path: Path,
    adr_index: dict,
) -> tuple:
    """Resolve the adr documents that record this spec's decisions.

    Returns ``(paths, basis)`` where ``basis`` is ``name`` (a name-mirrored adr
    file exists), ``depends-on`` (no name match, but an adr's front matter
    ``depends-on`` references one of the spec's IDs — this is how a renamed
    feature keeps its decision log attached), or ``none``.

    ``none`` is a normal outcome: a feature whose design decisions were never
    recorded has no adr file, so it is reported without a warning.
    """
    spec_path = Path(spec_file)
    named = sorted(
        str(c)
        for c in adr_candidates(adr_path, spec_path, specification_path)
        if c.is_file()
    )
    if named:
        return named, "name"

    if adr_index:
        spec_ids = spec_identifiers([spec_file], specification_path)
        linked = sorted(
            path for path, depends in adr_index.items() if depends & spec_ids
        )
        if linked:
            return linked, "depends-on"

    return [], "none"


def generate_mapping(
    specs: list,
    drafts: list,
    unscoped_drafts: list,
    scope: str,
    specification_path: Path,
    adr_path: Path,
    adr_index: dict,
    mapping_file: Path,
) -> list:
    """Build spec -> feature -> auxiliary design / adr mapping JSON.

    Returns the flat, de-duplicated list of adr documents attributed to the
    target specs, so the caller can write it out as one file list.
    """
    documents = []
    adr_files = set()

    for spec_file in specs:
        spec_path = Path(spec_file)
        basename = feature_name(spec_path.stem)

        # v4.x projects may still keep a sibling persisted design doc. Guard
        # against a spec whose own stem already ends in `_design` (kept in the
        # spec list by a `type: spec` front matter override in
        # sorted_spec_docs) -- feature_name() strips that suffix
        # unconditionally, so without this check the candidate path would
        # resolve back to the spec file itself.
        design_candidate = spec_path.parent / f"{basename}{DESIGN_SUFFIX}.md"
        design_file = (
            str(design_candidate)
            if design_candidate.is_file() and design_candidate != spec_path
            else ""
        )

        adr_docs, adr_basis = select_adr_docs(
            spec_file, specification_path, adr_path, adr_index
        )
        adr_files.update(adr_docs)

        documents.append(
            {
                "spec": spec_file,
                "feature_name": basename,
                "design": design_file,
                "adr": adr_docs,
                "adr_basis": adr_basis,
            }
        )

    mapping = {
        "spec_documents": documents,
        "design_drafts": drafts,
        "design_draft_scope": scope,
        "unscoped_design_drafts": unscoped_drafts,
        "adr_documents": sorted(adr_files),
    }
    mapping_file.write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    log("File mapping generated")
    return sorted(adr_files)


def export_env_vars(
    output_dir: Path,
    spec_files: Path,
    design_draft_files: Path,
    adr_files: Path,
    mapping_file: Path,
    scope: str,
) -> None:
    """Export metadata to CLAUDE_ENV_FILE"""
    wrote = rewrite_exports("CHECK_SPEC_", [
        f'export CHECK_SPEC_CACHE_DIR="{output_dir}"',
        f'export CHECK_SPEC_SPEC_FILES="{spec_files}"',
        f'export CHECK_SPEC_DESIGN_DRAFT_FILES="{design_draft_files}"',
        f'export CHECK_SPEC_DESIGN_DRAFT_SCOPE="{scope}"',
        f'export CHECK_SPEC_ADR_FILES="{adr_files}"',
        f'export CHECK_SPEC_MAPPING="{mapping_file}"',
    ])
    if wrote:
        log("Environment variables exported to CLAUDE_ENV_FILE")


def parse_args(argv: list) -> tuple:
    """Parse the CLI arguments into ``(target, ticket)``.

    Accepts both ``--ticket <number>`` and ``--ticket=<number>``. The first
    non-flag argument is the target feature name; any other flag (e.g.
    ``--full``, which the skill handles itself) is ignored so that it is never
    mistaken for a feature name.
    """
    target = ""
    ticket = ""
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == TICKET_FLAG:
            if i + 1 < len(argv):
                ticket = argv[i + 1]
                i += 1
            else:
                log(f"WARNING: {TICKET_FLAG} given without a number; ignoring")
        elif arg.startswith(f"{TICKET_FLAG}="):
            ticket = arg.split("=", 1)[1]
        elif arg.startswith("-"):
            pass
        elif not target:
            target = arg
        i += 1
    return target, ticket


def main() -> None:
    """Main execution"""
    try:
        project_root = Path(resolve_project_root())
        paths = read_config(project_root)

        sdd_dir = project_root / paths.root

        # Target feature name and ticket number (both optional)
        target, ticket = parse_args(sys.argv[1:])

        output_dir = sdd_dir / ".cache" / "check-spec"
        output_dir.mkdir(parents=True, exist_ok=True)

        spec_files = output_dir / "spec_files.txt"
        design_draft_files = output_dir / "design_draft_files.txt"
        adr_files = output_dir / "adr_files.txt"
        mapping_file = output_dir / "file_mapping.json"

        specification_path = sdd_dir / paths.specification_dir
        specs = find_spec_documents(specification_path, target)

        all_drafts = find_design_drafts(sdd_dir / paths.task_dir)
        # Spec IDs are only needed to link drafts, so resolve them lazily.
        spec_ids = (
            spec_identifiers(specs, specification_path)
            if all_drafts and not ticket
            else frozenset()
        )
        drafts, unscoped_drafts, scope = select_design_drafts(
            all_drafts, ticket, spec_ids
        )

        adr_path = sdd_dir / paths.adr_dir
        adr_index = index_adr_docs(adr_path)

        write_lines(spec_files, specs)
        write_lines(design_draft_files, drafts)
        attached_adrs = generate_mapping(
            specs,
            drafts,
            unscoped_drafts,
            scope,
            specification_path,
            adr_path,
            adr_index,
            mapping_file,
        )
        write_lines(adr_files, attached_adrs)
        log(
            f"Attached {len(attached_adrs)} adr document(s) to the target "
            "spec(s)"
        )
        export_env_vars(
            output_dir,
            spec_files,
            design_draft_files,
            adr_files,
            mapping_file,
            scope,
        )

        log("Scan complete")
        log(f"Cache location: {output_dir}")

    except SystemExit:
        raise
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
