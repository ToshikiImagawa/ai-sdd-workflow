"""laws_drafting.py - Deterministic helpers for drafting Bend laws from a spec.

Single source of truth for the laws-drafting conventions (laws-drafting_spec.md):
the spec section hash behind ``# source:`` comments (FR-003), the static checks
on drafted law files (FR-006, 3.1.3) and on differential pytest files (3.1.3-9),
source-drift detection shared by the proof gate and the post-tool-use hook
(FR-011 / FR-013), the approval validity verdict that gates the ``model`` stage
(FR-007), the point-assertion test (FR-014) and the implementation-location
resolution (FR-015 / 3.1.5). Everything is stdlib-only and
needs no ``bend`` (NFR-001 / NFR-002).

Approval and content-hash rules stay in laws_header.py; this module reuses them
and adds nothing to the law-body hash.
"""

import hashlib
import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

from fm_parser import parse_front_matter, split_front_matter
from laws_header import (
    APPROVED_RE,
    HEADER_RE,
    LAW_DECL_RE,
    MODEL_FILE,
    file_disallowed_imports,
    header_end,
    law_body_hash,
    read_header,
    read_lines,
    valid_approval,
)

HASH_LEN = 12

HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.*?)\s*#*\s*$")
SECTION_NUMBER_RE = re.compile(r"^(?P<num>\d+(?:\.\d+)*)(?:\.(?=\s|$)|(?=\s|$))")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SOURCE_RE = re.compile(
    r"^(?P<spec_id>\S+)\s+§(?P<section>\d+(?:\.\d+)*)\s+sha256:(?P<digest>[0-9a-f]{12})$"
)
LAW_NAME_RE = re.compile(r"^\s*law\s+(?P<name>[A-Za-z_][\w]*)\s*:?")
MODEL_API_RE = re.compile(r"^Model\.(?P<fn>[A-Za-z_]\w*)\s*\(")
MODEL_REF_RE = re.compile(r"\bModel\.([A-Za-z_]\w*)")
# A spec declares the model API with plain ``model-api: Model.<fn>(...) -> T`` lines
# (no leading ``#``, so the ``# model-api:`` examples of a law file are not picked up).
SPEC_MODEL_API_RE = re.compile(r"^\s*(?:[-*]\s+)?model-api:\s*Model\.(?P<fn>[A-Za-z_]\w*)\s*\((?P<rest>.*)$")
# A spec declares where the implementation lives with plain ``impl-of: <project-relative path>``
# lines (spec 3.1.5; same shape as ``model-api:``). A trailing ``# comment`` is ignored.
SPEC_IMPL_OF_RE = re.compile(r"^\s*(?:[-*]\s+)?impl-of:\s*(?P<path>[^\s#]+)\s*(?:#.*)?$")
# ``for x: T`` declarations of a law body (one or several variables; the multi-variable form is
# a syntax error in Bend but still counts as a quantifier here).
FOR_DECL_RE = re.compile(r"\bfor\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*:")
# ``def test_*`` of a pytest file (module level or inside a class).
TEST_DEF_RE = re.compile(r"^\s*def\s+(?P<name>test_\w*)\s*\(")
PROSE_SUFFIXES = (".md",)
# ``def`` of main.bend: optionally indented, optional type parameters (``def f<T>(...)``).
MAIN_DEF_RE = re.compile(r"^\s*def\s+(?P<fn>[A-Za-z_]\w*)\s*(?:<[^>]*>)?\s*\((?P<rest>.*)$")
# ``for a: Nat`` and the comma form ``for a, b: Nat``.
NAT_VAR_RE = re.compile(r"\bfor\s+(?P<vars>[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*:\s*Nat\b")
# Bend takes one variable per ``for``: ``for a b: T``, ``for a, b: T`` and ``for a: T, b: T``
# are syntax errors. The type of the typed form may hold commas inside ``<...>``.
MULTI_FOR_RE = re.compile(
    r"\bfor\s+(?P<vars>[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*|\s+[A-Za-z_]\w*)+)\s*:"
    r"|\bfor\s+(?P<typed>[A-Za-z_]\w*\s*:\s*(?:[^,{}<]|<[^>]*>)+?\s*,\s*[A-Za-z_]\w*)\s*:")
# A constant Nat expression (after whitespace removal): literals joined by + / *, parenthesised.
NAT_CONST_RE = re.compile(r"[()+*]*\d+n(?:[()+*]+\d+n)*[()]*")
MODEL_CALL_RE = re.compile(r"\bModel\.[A-Za-z_]\w*\(")

# Severities / finding codes (stable: consumed by the skill, the gate and the hook).
ERROR = "error"
WARNING = "warning"
SOURCE_DRIFT = "source_drift"
SOURCE_INVALID = "source_invalid"


class SourceRef(NamedTuple):
    """A parsed ``# source: <spec id> §<section> sha256:<digest>`` comment."""
    spec_id: str
    section: str
    digest: str


class LawDecl(NamedTuple):
    """One ``law`` declaration: its name, 1-based line, nearest source comment and body."""
    name: str
    line: int
    source_raw: Optional[str]   # text after "# source:" (None: no source comment)
    source: Optional[SourceRef]  # parsed form (None when absent or malformed)
    body: str                    # whitespace-normalised text after the ``law <name>`` word


class Finding(NamedTuple):
    """A static-check result. ``law`` is "" for file-level findings."""
    code: str
    severity: str
    law: str
    message: str


class ApprovalStatus(NamedTuple):
    """Verdict on a law file's approval line (spec FR-007 refusal reasons).

    ``state`` is one of ``valid`` / ``missing`` (no approval line) /
    ``malformed`` (approval lines exist, none well-formed) / ``mismatch``
    (well-formed but bound to different law text; ``current_hash`` is what to
    approve) / ``no_file``.
    """
    state: str
    current_hash: str
    approval: Optional[str]


# --- section hash ----------------------------------------------------------


def normalize_section(text: str) -> str:
    """Normalise a section body: LF line ends, each line stripped, runs of blank
    lines collapsed to one, leading/trailing blank lines dropped."""
    out: List[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.strip()
        if not line and (not out or not out[-1]):
            continue
        out.append(line)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


def _headings(spec_text: str) -> List[Tuple[int, int, str, str]]:
    """``(line_index, level, number, title)`` for every heading outside the front
    matter and fenced code blocks. ``number`` is "" for an unnumbered heading.

    Only ATX headings (``# title``) are recognised: Setext (underlined) headings
    are not, and neither are HTML comments or indented code blocks, so a
    ``# `` line inside those would be read as a heading.
    """
    _, body = split_front_matter(spec_text)
    lines = body.replace("\r\n", "\n").splitlines()
    result: List[Tuple[int, int, str, str]] = []
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m is None:
            continue
        title = m.group("title")
        n = SECTION_NUMBER_RE.match(title)
        result.append((i, len(m.group("marks")), n.group("num") if n else "", title))
    return result


def find_section(spec_text: str, section: str) -> Optional[str]:
    """Raw body of the section numbered ``section`` (e.g. ``"3.1.1"``), else None.

    A section runs from the line after its heading to just before the next
    heading of the same or a higher level (child sections are included). The
    number is the heading's leading number, a trailing period ignored; the
    first heading with that number wins and unnumbered headings never match.
    """
    section = section.strip().lstrip("§").rstrip(".")
    if not section:
        return None
    _, body = split_front_matter(spec_text)
    lines = body.replace("\r\n", "\n").splitlines()
    headings = _headings(spec_text)
    for idx, (line_no, level, number, _title) in enumerate(headings):
        if number != section:
            continue
        end = len(lines)
        for next_line, next_level, _n, _t in headings[idx + 1:]:
            if next_level <= level:
                end = next_line
                break
        return "\n".join(lines[line_no + 1:end])
    return None


def section_hash(spec_text: str, section: str) -> Optional[str]:
    """sha256 (first 12 hex) of the normalised section body, None if no such section."""
    raw = find_section(spec_text, section)
    if raw is None:
        return None
    return hashlib.sha256(normalize_section(raw).encode("utf-8")).hexdigest()[:HASH_LEN]


def spec_id_of(spec_text: str) -> str:
    """The spec's front matter ``id`` ("" if absent)."""
    fm, _ = split_front_matter(spec_text)
    return str(parse_front_matter(fm).get("id", "")) if fm else ""


def _read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[1:] if text.startswith("﻿") else text


def section_hash_of_file(spec_path: Path, section: str) -> Optional[str]:
    """:func:`section_hash` of a spec file."""
    return section_hash(_read_text(spec_path), section)


# --- law file parsing ------------------------------------------------------


def parse_source(value: str) -> Optional[SourceRef]:
    """Parse the text after ``# source:``; None when it does not match the format."""
    m = SOURCE_RE.match(value.strip())
    if m is None:
        return None
    return SourceRef(m.group("spec_id"), m.group("section"), m.group("digest"))


def _law_body(lines: List[str], start: int) -> str:
    """Text of the law at ``lines[start]`` (without its name), whitespace-normalised.

    The law ends at the next non-blank line that starts in column 0. Comment
    lines are dropped so a ``# ... Model.x ...`` remark is never read as code.
    """
    first = LAW_NAME_RE.match(lines[start])
    parts = [lines[start][first.end():] if first else lines[start]]
    for line in lines[start + 1:]:
        if line.strip() and not line[0].isspace():
            break
        if not line.lstrip().startswith("#"):
            parts.append(line)
    return " ".join(" ".join(parts).split())


def parse_laws(path: Path) -> List[LawDecl]:
    """Every ``law`` declaration of a law file with its nearest ``# source:`` comment.

    The source comment is looked up through the blank and comment lines directly
    above the declaration; any code line stops the search.
    """
    lines = read_lines(path)
    laws: List[LawDecl] = []
    for i, line in enumerate(lines):
        if not LAW_DECL_RE.match(line):
            continue
        name = LAW_NAME_RE.match(line)
        source_raw: Optional[str] = None
        j = i - 1
        while j >= 0 and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
            m = HEADER_RE.match(lines[j].strip())
            if m is not None and m.group(1) == "source":
                source_raw = m.group(2).strip()
                break
            j -= 1
        laws.append(LawDecl(
            name.group("name") if name else "",
            i + 1,
            source_raw,
            parse_source(source_raw) if source_raw is not None else None,
            _law_body(lines, i),
        ))
    return laws


def model_api_functions(path: Path) -> Optional[List[str]]:
    """Function names declared by ``# model-api: Model.<fn>(...)`` lines in the law
    *body* (after the leading comment header, so the lines are hashed and approved).

    None when the body has no ``# model-api:`` line at all.
    """
    lines = read_lines(path)
    found: Optional[List[str]] = None
    for raw in lines[header_end(lines):]:
        m = HEADER_RE.match(raw.strip())
        if m is None or m.group(1) != "model-api":
            continue
        found = [] if found is None else found
        a = MODEL_API_RE.match(m.group(2).strip())
        if a is not None:
            found.append(a.group("fn"))
    return found


# --- fixed model API (spec 3.1.4: spec declaration > main.bend > LLM proposal) ---

def model_api_from_spec(spec_text: str) -> Dict[str, str]:
    """``{fn: signature}`` from ``model-api: Model.<fn>(...)`` lines of a spec (anywhere,
    fenced or not). Empty when the spec declares none. A function declared twice keeps its
    first line (``spec_model_api_duplicates`` lists the repeats)."""
    out: Dict[str, str] = {}
    for line in spec_text.splitlines():
        m = SPEC_MODEL_API_RE.match(line)
        if m is not None:
            out.setdefault(m.group("fn"), f"Model.{m.group('fn')}({m.group('rest').strip()}")
    return out


def impl_of_from_spec(spec_text: str) -> List[str]:
    """Project-relative implementation paths declared by ``impl-of:`` lines of a spec (spec
    3.1.5 priority 1), in declaration order, duplicates dropped. Empty when none."""
    out: List[str] = []
    for line in spec_text.splitlines():
        m = SPEC_IMPL_OF_RE.match(line)
        if m is not None and m.group("path") not in out:
            out.append(m.group("path"))
    return out


def impl_of_main(main_path: Path) -> List[str]:
    """``# model-of:`` paths of an existing ``main.bend`` header (spec 3.1.5 priority 2)."""
    if not main_path.is_file():
        return []
    out: List[str] = []
    for value in read_header(main_path).get("model-of", []):
        path = value.split("#", 1)[0].strip()
        if path and path not in out:
            out.append(path)
    return out


def resolve_impl(spec_text: Optional[str], laws_dir: Path) -> Dict[str, object]:
    """Where the implementation lives (spec 3.1.5 / FR-015): ``{"paths", "source", "lawifiable",
    "reason"}``. ``source`` is ``spec`` (``impl-of:`` lines), ``main.bend`` (its ``# model-of:``)
    or ``none``. ``lawifiable`` is False with ``reason: prose_implementation`` when every
    declared path is a Markdown file (SKILL.md / agent definition): laws over a prose
    implementation cannot be tied to code, so the spec is not lawified."""
    paths = impl_of_from_spec(spec_text) if spec_text else []
    source = "spec" if paths else "none"
    if not paths:
        paths = impl_of_main(laws_dir / MODEL_FILE)
        source = "main.bend" if paths else "none"
    prose = bool(paths) and all(p.lower().endswith(PROSE_SUFFIXES) for p in paths)
    return {"paths": paths, "source": source, "lawifiable": not prose,
            "reason": "prose_implementation" if prose else None}


def is_point_assertion(body: str) -> bool:
    """True for a law body with at least one ``{lhs == rhs : T}`` equation and no ``for``
    quantifier (spec FR-014): a fixed-input proposition, i.e. one row of a decision table. Such
    candidates go to the differential pytest instead of ``LAWS.bend`` unless their ``kind`` is
    ``empty`` / ``singleton`` / ``identity`` (decided by the caller)."""
    return FOR_DECL_RE.search(body) is None and bool(_top_level_equations(body))


def spec_model_api_duplicates(spec_text: str) -> List[str]:
    """Function names declared by more than one ``model-api:`` line of the spec."""
    seen: Dict[str, int] = {}
    for line in spec_text.splitlines():
        m = SPEC_MODEL_API_RE.match(line)
        if m is not None:
            seen[m.group("fn")] = seen.get(m.group("fn"), 0) + 1
    return sorted(fn for fn, n in seen.items() if n > 1)


def _split_signature(sig: str) -> Tuple[List[str], str]:
    """``(parameter types, return type)`` of ``Model.f(a: T, +b: U) -> R`` (annotations
    like ``+`` / ``&`` / comments dropped; a missing type is ``""``)."""
    sig = sig.split("#", 1)[0]
    start = sig.find("(")
    depth = 0
    end = -1
    for i in range(start, len(sig)):
        depth += (sig[i] == "(") - (sig[i] == ")")
        if depth == 0:
            end = i
            break
    inner = sig[start + 1:end if end > 0 else len(sig)]
    params: List[str] = []
    cur, depth = "", 0
    for ch in inner:
        depth += (ch in "(<[") - (ch in ")>]")
        if ch == "," and depth == 0:
            params.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        params.append(cur)
    types = ["".join(p.split(":", 1)[1].split()) if ":" in p else "" for p in params]
    ret = "".join(sig[end + 1:].split("->", 1)[1].split()) if end > 0 and "->" in sig[end + 1:] else ""
    return types, ret


def model_api_from_main(main_path: Path) -> Dict[str, str]:
    """``{fn: signature}`` of the ``def`` lines of an existing ``main.bend`` (indented and
    type-parameterised defs included; a signature continued over several lines is joined until
    its parentheses balance). The entry point ``main`` is not part of the model API."""
    out: Dict[str, str] = {}
    if not main_path.is_file():
        return out
    lines = read_lines(main_path)
    for i, line in enumerate(lines):
        m = MAIN_DEF_RE.match(line)
        if m is None or m.group("fn") == "main":
            continue
        text = "(" + m.group("rest")
        j = i
        while text.count("(") > text.count(")") and j + 1 < len(lines):
            j += 1
            text += " " + lines[j].strip()
        out[m.group("fn")] = f"Model.{m.group('fn')}{' '.join(text.rstrip(':').split())}"
    return out


def model_constants(main_path: Path) -> Dict[str, str]:
    """``{fn: literal}`` for the zero-argument ``def`` of ``main.bend`` whose body is a single
    Nat literal (``def rank_fail() -> Nat:`` / ``4n``, optionally ``return 4n``). Used to read
    ``Model.rank_fail()`` and ``4n`` as the same value."""
    out: Dict[str, str] = {}
    if not main_path.is_file():
        return out
    lines = read_lines(main_path)
    for i, line in enumerate(lines):
        m = MAIN_DEF_RE.match(line)
        if m is None or not m.group("rest").lstrip().startswith(")"):
            continue
        body = [ln.strip() for ln in lines[i + 1:] if ln.strip() and not ln.strip().startswith("#")][:1]
        lit = re.fullmatch(r"(?:return\s+)?(\d+n)", body[0]) if body else None
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if lit is not None and nxt[:1].isspace():
            out[m.group("fn")] = lit.group(1)
    return out


def fixed_model_api(spec_text: Optional[str], laws_dir: Path) -> Tuple[str, Dict[str, str]]:
    """``(source, {fn: signature})``. ``spec`` when the spec declares the API (``main.bend`` is
    then not consulted and not merged); else ``main.bend`` when it has ``def`` lines; else
    ``main.bend-unreadable`` when ``main.bend`` exists with content but yields none (a broken
    source, not a missing one: the fixed-API check cannot run); else ``unfixed`` (the LLM
    proposes; a human confirms)."""
    declared = model_api_from_spec(spec_text) if spec_text else {}
    if declared:
        return "spec", declared
    main = laws_dir / MODEL_FILE
    from_main = model_api_from_main(main)
    if from_main:
        return "main.bend", from_main
    if main.is_file() and any(ln.strip() for ln in read_lines(main)):
        return "main.bend-unreadable", {}
    return "unfixed", {}


# --- source drift (gate FR-013 / hook FR-011 / draft check #1) -------------


def _source_problem(law: LawDecl, spec_text: str, spec_id: str) -> Optional[Tuple[str, str]]:
    """``(kind, detail)`` if a law's source disagrees with the spec, else None.

    kind: ``invalid`` (malformed ``# source:``), ``spec`` (names another spec id),
    ``missing`` (section absent), ``hash`` (section changed).
    """
    if law.source_raw is None:
        return None
    ref = law.source
    if ref is None:
        return ("invalid", law.source_raw)
    if spec_id and ref.spec_id != spec_id:
        return ("spec", ref.spec_id)
    current = section_hash(spec_text, ref.section)
    if current is None:
        return ("missing", ref.section)
    if current != ref.digest:
        return ("hash", current)
    return None


def source_drift(laws_path: Path, spec_path: Path) -> List[Dict[str, str]]:
    """FR-013 warnings for ``run-verification.py proof`` and the FR-011 hook.

    One ``{"code": "source_drift"|"source_invalid", "law": <name>, "source":
    <section without §>}`` per law whose ``# source:`` no longer matches the
    spec (section gone, renumbered, changed, or naming another spec id) or is
    malformed. Laws without ``# source:`` (hand-written) are skipped. A malformed
    source carries the raw text in ``source``.
    """
    spec_text = _read_text(spec_path)
    spec_id = spec_id_of(spec_text)
    warnings: List[Dict[str, str]] = []
    for law in parse_laws(laws_path):
        problem = _source_problem(law, spec_text, spec_id)
        if problem is None:
            continue
        if problem[0] == "invalid":
            warnings.append({"code": SOURCE_INVALID, "law": law.name, "source": problem[1]})
        else:
            section = law.source.section if law.source else ""
            warnings.append({"code": SOURCE_DRIFT, "law": law.name, "source": section})
    return warnings


class TestRef(NamedTuple):
    """One ``def test_*`` of a differential pytest file with its nearest ``# source:`` comment."""
    name: str
    line: int
    source_raw: Optional[str]
    source: Optional[SourceRef]


def source_refs_of_file(path: Path) -> List[TestRef]:
    """Every ``def test_*`` of a pytest file bound to the ``# source:`` comment directly above
    it (spec 4.1 "differential test"). The lookup walks up through blank lines, comment lines
    and decorators (``@...``, part of the function); any other code line stops it, so a test
    without its own source comment reads as missing."""
    lines = read_lines(path)
    out: List[TestRef] = []
    for i, line in enumerate(lines):
        m = TEST_DEF_RE.match(line)
        if m is None:
            continue
        source_raw: Optional[str] = None
        j = i - 1
        while j >= 0:
            s = lines[j].strip()
            if s and not s.startswith("#") and not s.startswith("@"):
                break
            h = HEADER_RE.match(s)
            if h is not None and h.group(1) == "source":
                source_raw = h.group(2).strip()
                break
            j -= 1
        out.append(TestRef(m.group("name"), i + 1, source_raw,
                           parse_source(source_raw) if source_raw is not None else None))
    return out


def check_test_sources(tests_path: Path, spec_path: Optional[Path]) -> List[Finding]:
    """Static check 9 (spec 3.1.3) of a differential pytest file: every ``def test_*`` has a
    ``# source:`` comment (else error ``test_source_missing``) that names an existing section
    of the spec whose hash is current (else error ``test_source_drift``; malformed /
    other-spec / absent-section sources keep the law-file codes). Without ``spec_path`` only
    the presence check runs. The test body itself is not inspected (pytest judges it)."""
    findings: List[Finding] = []
    if not tests_path.is_file():
        return [Finding("tests_file_missing", ERROR, "", f"tests file not found: {tests_path}")]
    spec_text = _read_text(spec_path) if spec_path is not None else None
    spec_id = spec_id_of(spec_text) if spec_text is not None else ""
    for ref in source_refs_of_file(tests_path):
        if ref.source_raw is None:
            findings.append(Finding(
                "test_source_missing", ERROR, ref.name,
                f"test '{ref.name}' (line {ref.line}) has no '# source:' comment"))
            continue
        if spec_text is None:
            continue
        law = LawDecl(ref.name, ref.line, ref.source_raw, ref.source, "")
        problem = _source_problem(law, spec_text, spec_id)
        if problem is None:
            continue
        kind, detail = problem
        text = {
            "invalid": f"malformed '# source:' ({detail})",
            "spec": f"'# source:' names spec id '{detail}', not '{spec_id}'",
            "missing": f"section §{detail} does not exist in the spec",
            "hash": f"section hash differs from the spec (current sha256:{detail})",
        }[kind]
        code = {"invalid": SOURCE_INVALID, "spec": "source_spec_mismatch",
                "missing": "source_section_missing", "hash": "test_source_drift"}[kind]
        findings.append(Finding(code, ERROR, ref.name, f"test '{ref.name}': {text}"))
    return findings


# --- static checks (3.1.3) -------------------------------------------------


def _top_level_equations(body: str) -> List[Tuple[str, str]]:
    """``(lhs, rhs)`` of each ``{lhs == rhs : T}`` group opened at depth 0, with the
    ``: T`` annotation and whitespace removed. Groups without a depth-1 ``==`` are skipped."""
    pairs: List[Tuple[str, str]] = []
    depth = 0
    start = -1
    for i, ch in enumerate(body):
        if ch in "([{":
            if depth == 0 and ch == "{":
                start = i + 1
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
            if depth == 0 and ch == "}" and start >= 0:
                pair = _split_equation(body[start:i])
                if pair is not None:
                    pairs.append(pair)
                start = -1
    return pairs


def _split_equation(group: str) -> Optional[Tuple[str, str]]:
    depth = 0
    eq = -1
    colon = -1
    for i, ch in enumerate(group):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and group.startswith("==", i) and eq < 0:
            eq = i
        elif depth == 0 and ch == ":" and eq >= 0:
            colon = i
    if eq < 0:
        return None
    rhs_end = colon if colon > eq else len(group)
    squash = lambda s: "".join(s.split())  # noqa: E731
    return squash(group[:eq]), squash(group[eq + 2:rhs_end])


def static_check(
    laws_path: Path,
    spec_path: Optional[Path] = None,
    *,
    tolerate_missing_model: bool = True,
    fixed_api: Optional[Dict[str, str]] = None,
    model_dir: Optional[Path] = None,
) -> List[Finding]:
    """Static checks of a ``draft`` output (``LAWS.bend`` / ``LAWS.draft.bend``).

    ``bend`` is not needed. Applies only to drafted files (hand-written laws
    lack ``# source:`` by design). Errors: 2 missing ``# source:``; 1 section
    absent / section hash differs from the spec / source naming another spec
    id / malformed source; 5 disallowed import; ``# model-api:`` missing or
    out of step with the ``Model.*`` references. Warnings: 3 duplicate bodies;
    4 trivial (both sides identical) laws; ``unbounded_nat_literal``. Error ``multi_var_for``:
    several variables in one ``for``. Without ``spec_path`` the source checks (1) are skipped.
    ``fixed_api`` (default: the
    spec's ``model-api:`` lines, else ``main.bend`` beside the law file) turns a
    ``Model.*`` name outside it into an error. ``model_dir`` is where ``main.bend`` is looked
    up (default: the law file's directory; pass the feature's laws directory when the file
    lives elsewhere).
    """
    findings: List[Finding] = []
    laws = parse_laws(laws_path)
    spec_text = _read_text(spec_path) if spec_path is not None else None
    spec_id = spec_id_of(spec_text) if spec_text is not None else ""

    for law in laws:
        if law.source_raw is None:
            findings.append(Finding(
                "source_missing", ERROR, law.name, f"law '{law.name}' has no '# source:' comment"))
            continue
        if spec_text is None:
            continue
        problem = _source_problem(law, spec_text, spec_id)
        if problem is None:
            continue
        kind, detail = problem
        text = {
            "invalid": f"malformed '# source:' ({detail})",
            "spec": f"'# source:' names spec id '{detail}', not '{spec_id}'",
            "missing": f"section §{detail} does not exist in the spec",
            "hash": f"section hash differs from the spec (current sha256:{detail})",
        }[kind]
        code = {"invalid": SOURCE_INVALID, "spec": "source_spec_mismatch",
                "missing": "source_section_missing", "hash": SOURCE_DRIFT}[kind]
        findings.append(Finding(code, ERROR, law.name, f"law '{law.name}': {text}"))

    seen: Dict[str, str] = {}
    for law in laws:
        if law.body in seen:
            findings.append(Finding(
                "duplicate_law", WARNING, law.name,
                f"law '{law.name}' has the same body as '{seen[law.body]}'"))
        else:
            seen[law.body] = law.name
        if any(lhs == rhs for lhs, rhs in _top_level_equations(law.body)):
            findings.append(Finding(
                "trivial_law", WARNING, law.name,
                f"law '{law.name}' is trivially true (both sides of '==' are identical)"))

    root = laws_path.parent.resolve()
    tolerated = [f"./{MODEL_FILE}", MODEL_FILE] if tolerate_missing_model else []
    for line in file_disallowed_imports(laws_path, root, tolerated):
        findings.append(Finding("import_disallowed", ERROR, "", f"import not allowed: {line}"))

    findings.extend(_model_api_findings(laws_path, laws))
    findings.extend(_multi_var_for_findings(laws))
    findings.extend(_unbounded_nat_findings(laws))
    if fixed_api is None:
        source, fixed_api = fixed_model_api(spec_text, model_dir or laws_path.parent)
        if source == "main.bend-unreadable":
            findings.append(Finding(
                "model_api_source_unreadable", WARNING, "",
                f"{MODEL_FILE} exists but no 'def' could be read from it: the fixed-API check "
                "(check 6) is disabled; fix main.bend or declare 'model-api:' in the spec"))
        for fn in spec_model_api_duplicates(spec_text or ""):
            findings.append(Finding(
                "model_api_duplicate", WARNING, "",
                f"the spec declares Model.{fn} in more than one 'model-api:' line; the first is used"))
    if fixed_api:
        findings.extend(_fixed_api_findings(laws_path, laws, fixed_api))
    return findings


def _multi_var_for_findings(laws: List[LawDecl]) -> List[Finding]:
    """Error on a ``for`` declaring several variables (``for a b: T``, ``for a, b: T``): Bend
    accepts one variable per ``for`` (check 8). ``NAT_VAR_RE`` keeps reading the comma form so
    ``unbounded_nat_literal`` still sees every variable of such a law."""
    out: List[Finding] = []
    for law in laws:
        m = MULTI_FOR_RE.search(law.body)
        if m is not None:
            out.append(Finding(
                "multi_var_for", ERROR, law.name,
                f"law '{law.name}' declares several variables in one 'for' "
                f"('for {' '.join((m.group('vars') or m.group('typed')).replace(',', ' ').split())} ...'): "
                "Bend takes one variable per 'for'; write one 'for x: T' per line"))
    return out


def _nat_vars(body: str) -> set:
    return {v.strip() for m in NAT_VAR_RE.finditer(body) for v in m.group("vars").split(",")}


def _nonzero_const(expr: str) -> bool:
    """True for a constant Nat expression other than plain ``0n`` (parentheses allowed)."""
    if NAT_CONST_RE.fullmatch(expr) is None:
        return False
    return expr.replace("(", "").replace(")", "") != "0n"


def _unbounded_nat_findings(laws: List[LawDecl]) -> List[Finding]:
    """Warn on ``{Model.f(.. n ..) == <constant Nat expression>}`` (either side) where ``n`` is a
    ``for n: Nat`` variable: without a value-range premise such an equation (e.g. an
    absorption law ``worse(4n, a) == 4n``) is typically false for large ``n``. A heuristic:
    ``bend`` cannot run at draft time, so a human reviews the warning before approval.
    Limits (spec 3.1.3 check 7): the constant side is literals joined by ``+`` / ``*`` with
    parentheses; plain ``0n`` is exempt; a variable behind a nested non-``Model`` call or a
    comparison between two Model calls is not examined."""
    out: List[Finding] = []
    for law in laws:
        nat_vars = _nat_vars(law.body)
        if not nat_vars:
            continue
        for lhs, rhs in _top_level_equations(law.body):
            for lit, call in ((lhs, rhs), (rhs, lhs)):
                if not _nonzero_const(lit) or not MODEL_CALL_RE.search(call):
                    continue
                used = sorted(v for v in nat_vars if re.search(rf"\b{re.escape(v)}\b", call))
                if used:
                    out.append(Finding(
                        "unbounded_nat_literal", WARNING, law.name,
                        f"law '{law.name}' equates a Model call over unbounded Nat "
                        f"({', '.join(used)}) with the constant {lit}: false for large values unless "
                        "the range is restricted; review before approval"))
                    break
    return out


def model_api_signatures(path: Path) -> Dict[str, str]:
    """``{fn: signature}`` of the ``# model-api:`` lines in the law body."""
    out: Dict[str, str] = {}
    lines = read_lines(path)
    for raw in lines[header_end(lines):]:
        m = HEADER_RE.match(raw.strip())
        if m is not None and m.group(1) == "model-api":
            a = MODEL_API_RE.match(m.group(2).strip())
            if a is not None:
                out.setdefault(a.group("fn"), m.group(2).strip())
    return out


def _fixed_api_findings(laws_path: Path, laws: List[LawDecl], fixed: Dict[str, str]) -> List[Finding]:
    declared = set(model_api_functions(laws_path) or [])
    referenced = {fn for law in laws for fn in MODEL_REF_RE.findall(law.body)}
    out = [Finding(
        "model_api_not_fixed", ERROR, "",
        f"Model.{fn} is not in the fixed model API ({', '.join(sorted(fixed))}); "
        "use a fixed function or have the owner extend the API")
        for fn in sorted((referenced | declared) - set(fixed))]
    for fn, sig in sorted(model_api_signatures(laws_path).items()):
        if fn not in fixed:
            continue
        got, want = _split_signature(sig), _split_signature(fixed[fn])
        # compare only what the fixed side states (a missing type on either side is not a mismatch)
        same_arity = len(got[0]) == len(want[0])
        types_differ = same_arity and any(
            a and b and a != b for a, b in zip(got[0] + [got[1]], want[0] + [want[1]]))
        ret_differ = bool(got[1] and want[1] and got[1] != want[1])
        if not same_arity or types_differ or ret_differ:
            out.append(Finding(
                "model_api_signature_mismatch", WARNING, "",
                f"'# model-api:' for Model.{fn} differs from the fixed signature "
                f"({fixed[fn]}): argument count or types do not match"))
    return out


def _model_api_findings(laws_path: Path, laws: List[LawDecl]) -> List[Finding]:
    referenced = sorted({fn for law in laws for fn in MODEL_REF_RE.findall(law.body)})
    declared = model_api_functions(laws_path)
    if not referenced and declared is None:
        return []
    if declared is None:
        hint = ""
        if "model-api" in read_header(laws_path):
            hint = " (found only in the leading comment header, which is not hashed or approved)"
        return [Finding(
            "model_api_missing", ERROR, "",
            "laws reference Model." + ", Model.".join(referenced)
            + f" but the body has no '# model-api:' line{hint}")]
    out: List[Finding] = []
    for fn in sorted(set(referenced) - set(declared)):
        out.append(Finding(
            "model_api_mismatch", ERROR, "",
            f"Model.{fn} is referenced by a law but not declared in '# model-api:'"))
    for fn in sorted(set(declared) - set(referenced)):
        out.append(Finding(
            "model_api_mismatch", ERROR, "",
            f"Model.{fn} is declared in '# model-api:' but no law references it"))
    return out


def has_errors(findings: List[Finding]) -> bool:
    """True if any finding is an error (FR-006: then ``drafted`` is not proposed)."""
    return any(f.severity == ERROR for f in findings)


# --- approval validity (FR-007) --------------------------------------------


def approval_status(laws_path: Path) -> ApprovalStatus:
    """Is the approval line of ``laws_path`` valid for its current law body?

    Reuses ``law_body_hash`` / ``valid_approval`` (laws_header.py). ``mismatch``
    and ``current_hash`` give the ``model`` stage its refusal reason and the
    hash to show the approver.
    """
    if not laws_path.is_file():
        return ApprovalStatus("no_file", "", None)
    current = law_body_hash(laws_path)
    values = read_header(laws_path).get("approved", [])
    if not values:
        return ApprovalStatus("missing", current, None)
    valid = valid_approval({"approved": values}, current)
    if valid is not None:
        return ApprovalStatus("valid", current, valid)
    for value in values:
        m = APPROVED_RE.match(value)
        # Same line, bound to its own digest: only a malformed date is left to fail.
        if m is not None and valid_approval({"approved": [value]}, m.group("digest")):
            return ApprovalStatus("mismatch", current, value)
    return ApprovalStatus("malformed", current, None)

