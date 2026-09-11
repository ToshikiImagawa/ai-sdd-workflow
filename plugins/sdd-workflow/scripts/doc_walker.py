"""doc_walker.py - Shared AI-SDD document discovery.

Single source of truth for the target-selection rule that was duplicated between
sdd_index.iter_target_files and scan-documents.collect_documents:

- requirement/: every ``.md`` file
- specification/: every ``.md`` file (the ``_spec``/``_design`` suffix is optional
  since specification/ is a single-type directory identified by directory alone;
  see naming.py)
- adr/: every ``.md`` file (single-type directory, same as specification/; the
  ``-decisions`` suffix is optional)
- task/: every ``.md`` file

Also hosts find_spec_doc / find_legacy_design_doc (used by the post-tool-use
hook). All traversal is pathlib-based for cross-platform behavior.
"""

import glob
from pathlib import Path
from typing import List, Tuple, Union

from naming import DESIGN_SUFFIX, SPEC_SUFFIX

PathLike = Union[str, Path]


def iter_requirement_docs(req_path: PathLike) -> List[Path]:
    """Every ``.md`` file under a requirement directory, sorted."""
    p = Path(req_path)
    return sorted(p.rglob("*.md")) if p.is_dir() else []


def iter_specification_docs(spec_path: PathLike) -> List[Path]:
    """Every ``.md`` file under a specification directory, sorted (suffix optional)."""
    p = Path(spec_path)
    return sorted(p.rglob("*.md")) if p.is_dir() else []


def iter_legacy_design_docs(spec_path: PathLike) -> List[Path]:
    """Every v4.x persisted ``*_design.md`` under a specification dir, sorted.

    These files stay valid and are read as supplementary input; the list is used
    to point at the adr/ migration, never to report a naming violation.
    """
    p = Path(spec_path)
    return sorted(p.rglob(f"*{DESIGN_SUFFIX}.md")) if p.is_dir() else []


def iter_all_markdown(path: PathLike) -> List[Path]:
    """Every ``.md`` file under a directory, sorted."""
    p = Path(path)
    return sorted(p.rglob("*.md")) if p.is_dir() else []


def iter_target_files(project_root: str, sdd_root: str, req_dir: str,
                      spec_dir: str, adr_dir: str) -> List[str]:
    """Indexer targets: requirement (all) + specification (all) + adr (all), globally sorted."""
    base = Path(project_root) / sdd_root
    files = (iter_requirement_docs(base / req_dir)
             + iter_specification_docs(base / spec_dir)
             + iter_all_markdown(base / adr_dir))
    return sorted(str(f) for f in files)


def collect_documents(sdd_dir: PathLike, requirement_dir: str, specification_dir: str,
                      task_dir: str, adr_dir: str) -> List[Path]:
    """Scan targets: requirement (all) + specification (all) + task (all) + adr (all).

    Returned in section order (requirement, then specification, then task, then
    adr), each section sorted internally.
    """
    base = Path(sdd_dir)
    docs = iter_requirement_docs(base / requirement_dir)
    docs += iter_specification_docs(base / specification_dir)
    docs += iter_all_markdown(base / task_dir)
    docs += iter_all_markdown(base / adr_dir)
    return docs


def find_spec_doc(spec_dir: PathLike, stem: str) -> str:
    """Return the path of the spec document matching ``stem`` under spec_dir, or ''.

    ``{stem}_design.md`` never matches: a v4.x persisted design doc is not a
    spec, so it is not a spec sync target. Use find_legacy_design_doc to locate
    those separately. When several files share a stem the lowest path string
    wins, so the result is deterministic.
    """
    base = Path(spec_dir)
    escaped_stem = glob.escape(stem)
    # Suffix-first so an explicit {stem}_spec.md wins over a bare {stem}.md.
    for suffix in (f"{SPEC_SUFFIX}.md", ".md"):
        found = min((str(p) for p in base.rglob(f"{escaped_stem}{suffix}")), default="")
        if found:
            return found
    return ""


def find_legacy_design_doc(spec_dir: PathLike, stem: str) -> str:
    """Return the path of a v4.x persisted design doc for ``stem``, or ''.

    ``specification/{stem}_design.md`` is a v4.x artifact. It remains valid and
    is read as supplementary input, but it is not a spec, so find_spec_doc never
    returns it. Kept as a separate lookup so a caller can tell the two apart and
    point at the adr/ migration instead of the spec sync reminder. When several
    files share a stem the lowest path string wins, so the result is
    deterministic.
    """
    base = Path(spec_dir)
    return min(
        (str(p) for p in base.rglob(f"{glob.escape(stem)}{DESIGN_SUFFIX}.md")),
        default="",
    )


def find_spec_or_legacy_design_doc(spec_dir: PathLike, stem: str) -> Tuple[str, str]:
    """Return ``(spec_path, legacy_design_path)`` for ``stem`` in a single directory walk.

    Equivalent to calling :func:`find_spec_doc` then, if it returns '',
    :func:`find_legacy_design_doc` -- but for a caller that always wants both
    (the post-tool-use spec-sync reminder), doing so walks specification/ up
    to three times (two suffix candidates inside find_spec_doc, plus one more
    inside find_legacy_design_doc) for a single source-file edit. This
    collects every ``{stem}*.md`` candidate once and classifies them in
    memory instead.
    """
    base = Path(spec_dir)
    candidates = [str(p) for p in base.rglob(f"{glob.escape(stem)}*.md")]
    spec_suffixed_name = f"{stem}{SPEC_SUFFIX}.md"
    spec_bare_name = f"{stem}.md"
    design_name = f"{stem}{DESIGN_SUFFIX}.md"

    spec_path = min(
        (c for c in candidates if Path(c).name == spec_suffixed_name), default="",
    )
    if not spec_path:
        spec_path = min(
            (c for c in candidates if Path(c).name == spec_bare_name), default="",
        )
    design_path = min(
        (c for c in candidates if Path(c).name == design_name), default="",
    )
    return spec_path, design_path
