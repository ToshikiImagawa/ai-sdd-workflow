"""laws_header.py - Shared parsing of Bend law-file conventions (proof gate).

Single source of truth for the leading-comment conventions (``# spec:`` /
``# approved:`` / ``# model-of:``), the law-body content hash that binds an
approval to the law text, the import allowlist, and the ``law`` declaration
check. Consumed by run-verification.py (proof category) and post-tool-use.py.

The conventions themselves are defined in proof-gate_spec.md (FR-004 / FR-005)
and design-draft §5.4; keep this module the only place that encodes them.
"""

import datetime
import hashlib
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

LAWS_FILE = "LAWS.bend"
PROOF_FILE = "PROOF.bend"
MODEL_FILE = "main.bend"

HEADER_RE = re.compile(r"^#\s*([A-Za-z][\w-]*):\s*(.*)$")
APPROVED_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<approver>\S+)\s+sha256:(?P<digest>[0-9a-f]{12})$"
)
IMPORT_LINE_RE = re.compile(r"^\s*(?:import|from)\b")
# Bend 2.0.37 only accepts `import Base` and `import <path>.bend as <Name>`; a local
# import without `as <Name>`, without the `.bend` extension or with a digit-leading
# <Name> is a syntax error there.
# Whole-line match: a trailing comment, a `from` form, a non-.bend path or a missing
# alias never matches and therefore fails the allowlist. Path segments exclude `.`,
# so `..` can never match (parent directories are not allowed).
LOCAL_IMPORT_RE = re.compile(
    r"^import\s+(?P<target>(?:\./)?(?:[A-Za-z0-9_\-]+/)*[A-Za-z0-9_\-]+\.bend)"
    r"\s+as\s+(?P<alias>[A-Za-z_][A-Za-z0-9_]*)$"
)
LAWS_IMPORT_RE = re.compile(r"^import\s+(?:\./)?LAWS\.bend\s+as\s+[A-Za-z_][A-Za-z0-9_]*$")
# Bend's bundled standard library: imported by bare name, never aliased, no file needed.
STDLIB_IMPORT_RE = re.compile(r"^import\s+Base$")
LAW_DECL_RE = re.compile(r"^\s*law\s+[A-Za-z_]")


def _read_lines(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if text.startswith("﻿"):
        text = text[1:]
    return text.splitlines()


def _header_end(lines: List[str]) -> int:
    """Index of the first line that is neither blank nor a ``#`` comment."""
    i = 0
    while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    return i


def read_lines(path: Path) -> List[str]:
    """Public alias of the BOM-stripping line reader (for sibling modules)."""
    return _read_lines(path)


def header_end(lines: List[str]) -> int:
    """Public alias of :func:`_header_end` (index of the first code line)."""
    return _header_end(lines)


def read_header(path: Path) -> Dict[str, List[str]]:
    """Parse leading ``# key: value`` comment lines; stop at the first code line.

    Every key is collected as a list (``model-of`` is legitimately repeated);
    callers read the keys they know (``spec`` / ``approved`` / ``model-of``)
    and ignore the rest.
    """
    header: Dict[str, List[str]] = {}
    lines = _read_lines(path)
    for raw in lines[:_header_end(lines)]:
        m = HEADER_RE.match(raw.strip())
        if m is not None:
            header.setdefault(m.group(1), []).append(m.group(2).strip())
    return header


def law_body_hash(path: Path) -> str:
    """SHA-256 (first 12 hex) of LAWS.bend minus its leading comment/blank header.

    Excluding the header is what lets a reviewer append ``# approved:`` (or a
    ``# spec:`` fix) without invalidating the approval; any change to the law
    text itself, whitespace included, changes the digest on purpose.
    """
    lines = _read_lines(path)
    body = "\n".join(lines[_header_end(lines):])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def valid_approval(header: Dict[str, List[str]], body_hash: str) -> Optional[str]:
    """Return the approval line whose digest matches the current law body, else None.

    Approval lines are append-only: any one well-formed line (valid calendar
    date, approver, 12-hex digest) that matches ``body_hash`` is enough.
    """
    for value in header.get("approved", []):
        m = APPROVED_RE.match(value)
        if m is None or m.group("digest") != body_hash:
            continue
        try:
            datetime.date.fromisoformat(m.group("date"))
        except ValueError:
            continue
        return value
    return None


def declares_laws(path: Path) -> bool:
    """True if LAWS.bend contains at least one ``law`` declaration."""
    return any(LAW_DECL_RE.match(line) for line in _read_lines(path))


def imports_laws(proof_path: Path) -> bool:
    """True if PROOF.bend imports LAWS (any accepted local spelling)."""
    return any(LAWS_IMPORT_RE.match(line.strip()) for line in _read_lines(proof_path))


def _local_import_exists(bend_file: Path, root: Path, target: str) -> bool:
    """True if ``target`` resolves inside ``root`` to an existing ``.bend`` file."""
    resolved = (bend_file.parent / target).resolve()
    if resolved != root and root not in resolved.parents:
        return False
    return resolved.is_file()


def file_disallowed_imports(
    bend_file: Path, root: Path, tolerate_missing: Iterable[str] = ()
) -> List[str]:
    """Import lines of one ``.bend`` file that fail the allowlist (the raw lines).

    ``root`` is the resolved laws directory local imports must stay inside.
    ``tolerate_missing`` lists import targets (as written, e.g. ``./main.bend``)
    that are allowed even though the file does not exist yet (a draft law file
    is written before its model).
    """
    tolerated = set(tolerate_missing)
    bad: List[str] = []
    for raw in _read_lines(bend_file):
        if not IMPORT_LINE_RE.match(raw):
            continue
        line = raw.strip()
        if STDLIB_IMPORT_RE.match(line):
            continue
        m = LOCAL_IMPORT_RE.match(line)
        if m is None:
            bad.append(line)
        elif m.group("target") not in tolerated and not _local_import_exists(
            bend_file, root, m.group("target")
        ):
            bad.append(line)
    return bad


def disallowed_imports(laws_dir: Path) -> List[str]:
    """Import lines that fail the allowlist, as ``"<relative file>: <line>"``.

    Allowed: the bundled standard library (``import Base``) and a relative
    ``import <path>.bend as <Name>`` of a file that exists inside ``laws_dir``
    (the form Bend 2.0.37 requires). Everything else fails: unknown forms
    (``from``, trailing comments), a local import without ``as <Name>``,
    absolute paths, Hub imports (``0x<hash>/...``, ``<name>@<ver>/...``), URLs,
    ``..`` paths, and files that do not exist in the directory.
    """
    if not laws_dir.is_dir():
        return []
    root = laws_dir.resolve()
    bad: List[str] = []
    for bend_file in sorted(laws_dir.rglob("*.bend")):
        rel = bend_file.relative_to(laws_dir)
        bad.extend(f"{rel}: {line}" for line in file_disallowed_imports(bend_file, root))
    return bad
