"""naming.py - Single source of truth for AI-SDD file naming conventions.

The AI-SDD naming rule:
- requirement/: plain ``.md`` files; a ``_spec`` / ``_design`` suffix is forbidden.
- specification/: files require a ``_spec.md`` or ``_design.md`` suffix.

Consumed by the pre-tool-use hook (write-time validation via ``validate_naming``)
and the recommend-front-matter skill (document classification via
``determine_type``), so the rule is defined exactly once.
"""

from pathlib import Path

SPEC_SUFFIXES = ("_spec", "_design")


def has_spec_suffix(stem: str) -> bool:
    """Return True if ``stem`` ends with a ``_spec`` / ``_design`` suffix."""
    return stem.endswith(SPEC_SUFFIXES)


def validate_naming(rel_path: str, requirement_prefix: str, specification_prefix: str) -> str:
    """Return an error message if rel_path violates naming conventions, else ''.

    ``requirement_prefix`` / ``specification_prefix`` are project-relative
    directory paths (e.g. ``.sdd/requirement``).
    """
    rel = Path(rel_path)
    if rel.suffix != ".md":
        return ""
    stem = rel.stem

    if rel.is_relative_to(requirement_prefix):
        if has_spec_suffix(stem):
            return (
                f"[AI-SDD] Naming violation: '{rel_path}'. "
                f"Files under {requirement_prefix}/ must not have a _spec/_design suffix "
                "(e.g. user-login.md, index.md)."
            )
    elif rel.is_relative_to(specification_prefix):
        if not has_spec_suffix(stem):
            return (
                f"[AI-SDD] Naming violation: '{rel_path}'. "
                f"Files under {specification_prefix}/ require a _spec.md or _design.md suffix "
                "(e.g. user-login_spec.md, index_design.md)."
            )
    return ""


def determine_type(
    filepath: str,
    basename: str,
    requirement_dir: str,
    specification_dir: str,
    task_dir: str,
) -> str:
    """Classify a document type from its path and naming convention.

    ``basename`` is the file name without the ``.md`` extension.
    """
    if f"/{requirement_dir}/" in filepath:
        return "prd"
    if f"/{specification_dir}/" in filepath:
        if basename.endswith("_spec"):
            return "spec"
        if basename.endswith("_design"):
            return "design"
        return "unknown"
    if f"/{task_dir}/" in filepath:
        if "implementation_log" in basename or "impl_log" in basename:
            return "implementation-log"
        return "task"
    return "unknown"
