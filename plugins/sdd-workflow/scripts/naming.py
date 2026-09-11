"""naming.py - Single source of truth for AI-SDD file naming conventions.

The AI-SDD naming rule:
- requirement/: plain ``.md`` files; a ``_spec`` / ``_design`` suffix is forbidden
  (it must stay distinguishable from specification/ by name alone).
- specification/ and adr/: single-type directories (every file is an abstract
  spec / a decision log respectively), so a ``_spec``/``_design``/``-decisions``
  suffix is optional. Existing suffixed files remain valid; new files may omit it.

Consumed by the pre-tool-use hook (write-time validation via ``validate_naming``),
the recommend-front-matter skill (document classification via ``determine_type``),
doc_walker (spec lookup) and the check-spec skill helper, so the rule is defined
exactly once.
"""

import fnmatch
from pathlib import Path

SPEC_SUFFIX = "_spec"
DESIGN_SUFFIX = "_design"
SPEC_SUFFIXES = (SPEC_SUFFIX, DESIGN_SUFFIX)


def has_spec_suffix(stem: str) -> bool:
    """Return True if ``stem`` ends with a ``_spec`` / ``_design`` suffix."""
    return stem.endswith(SPEC_SUFFIXES)


def is_design_stem(stem: str) -> bool:
    """Return True if ``stem`` ends with ``_design``.

    Under specification/ such a file is a v4.x persisted design doc, not a spec:
    design docs now live at ``task/{ticket-number}/design-draft.md``.
    """
    return stem.endswith(DESIGN_SUFFIX)


def feature_name(stem: str) -> str:
    """Return ``stem`` with a ``_spec`` / ``_design`` suffix stripped (suffix optional)."""
    for suffix in SPEC_SUFFIXES:
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def validate_naming(
    rel_path: str,
    requirement_prefix: str,
    ignore_patterns=(),
) -> str:
    """Return an error message if rel_path violates naming conventions, else ''.

    ``requirement_prefix`` is a project-relative directory path (e.g.
    ``.sdd/requirement``). ``ignore_patterns`` are ``fnmatch`` glob patterns
    (e.g. ``"*_test.md"``) matched against the file's basename; a match skips
    the naming check entirely.

    Only requirement/ is validated here: specification/ and adr/ never reject
    a file based on suffix (see module docstring).
    """
    rel = Path(rel_path)
    if rel.suffix != ".md":
        return ""
    if any(fnmatch.fnmatch(rel.name, pat) for pat in ignore_patterns):
        return ""

    if rel.is_relative_to(requirement_prefix) and has_spec_suffix(rel.stem):
        return (
            f"[AI-SDD] Naming violation: '{rel_path}'. "
            f"Files under {requirement_prefix}/ must not have a _spec/_design suffix "
            "(e.g. user-login.md, index.md)."
        )
    return ""


def determine_type(
    filepath: str,
    basename: str,
    requirement_dir: str,
    specification_dir: str,
    task_dir: str,
    adr_dir: str,
) -> str:
    """Classify a document type from its path and naming convention.

    ``basename`` is the file name without the ``.md`` extension.
    """
    if f"/{requirement_dir}/" in filepath:
        return "prd"
    if f"/{specification_dir}/" in filepath:
        # specification/ is a single-type directory (abstract specs only); an
        # explicit _design suffix is still honored for pre-ADR-migration files,
        # but any other name (suffixed or not) is a spec.
        if is_design_stem(basename):
            return "design"
        return "spec"
    if f"/{adr_dir}/" in filepath:
        return "adr"
    if f"/{task_dir}/" in filepath:
        if basename == "design-draft":
            return "design"
        if "implementation_log" in basename or "impl_log" in basename:
            return "implementation-log"
        return "task"
    return "unknown"
