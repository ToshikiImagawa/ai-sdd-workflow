#!/usr/bin/env python3
"""
draft_laws.py
Deterministic helper for the /draft-laws skill (laws-drafting_spec.md).

The LLM only extracts law candidates; everything checkable lives here so the
skill's ``allowed-tools`` can pre-approve one scoped Bash invocation and the
results do not depend on the model (NFR-002 / NFR-003). The script never calls
``bend`` and never writes a file; it prints JSON on stdout.

Subcommands:
  status <feature> [--overwrite]   spec / laws-dir state, approval verdict, write_target, max_laws,
                                   implementation location (``impl``, FR-015) and ``tests_target``
  hash <spec> <section>            section hash for a ``# source:`` comment
  rank --max N [FILE|-]            deterministic order + cut-off of law candidates (NFR-005);
                                   point assertions go to ``to_tests`` (FR-014)
  check [<laws-file>] [--spec SPEC] [--tests FILE]
                                   static checks (FR-006); ``propose_drafted`` is false on errors.
                                   ``--tests`` checks the ``# source:`` lines of a pytest file (3.1.3-9)
  model-api <feature>              fixed model API and its source (spec > main.bend > unfixed)
  migrate <feature>                read-only classification of an existing LAWS.bend into
                                   keep / to_tests / prose_delete (FR-016)
  compare <generated> <reference> [--judgement FILE]  two-stage acceptance (spec section 11)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# skills/draft-laws/scripts/ -> plugins/sdd-workflow/scripts/ (shared modules)
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from fm_parser import parse_front_matter, split_front_matter  # noqa: E402
from hook_common import (  # noqa: E402
    load_sdd_paths,
    read_sdd_config_json,
    resolve_project_root,
)
from laws_drafting import (  # noqa: E402
    FOR_DECL_RE,
    Finding,
    approval_status,
    check_test_sources,
    fixed_model_api,
    is_point_assertion,
    model_constants,
    has_errors,
    parse_laws,
    resolve_impl,
    section_hash_of_file,
    spec_id_of,
    spec_model_api_duplicates,
    static_check,
)
from laws_header import LAWS_FILE, MODEL_FILE, PROOF_FILE  # noqa: E402

DRAFT_FILE = "LAWS.draft.bend"
MAX_LAWS_DEFAULT = 10
TESTS_DIR_DEFAULT = "tests/laws"
# Candidate ``kind`` values taken first inside one priority (spec 3.1.2): the basic algebraic
# properties of an aggregation / merge rule.
BASIC_KINDS = ("commutative", "associative", "identity", "empty", "singleton")
# Kinds that stay in Bend even without a ``for`` quantifier (spec FR-014): the base cases of
# the universal aggregation laws.
POINT_EXEMPT_KINDS = ("empty", "singleton", "identity")
# An empty-input law is recognisable syntactically (``migrate`` guesses ``kind: empty`` from it).
EMPTY_INPUT_RE = re.compile(r"Nil\s*\{\s*\}|\[\s*\]")


def load_max_laws(raw: dict) -> Tuple[int, Optional[str]]:
    """``laws.max_laws`` from .sdd-config.json: an int >= 1, else 10 plus a warning."""
    section = raw.get("laws")
    if not isinstance(section, dict) or "max_laws" not in section:
        return MAX_LAWS_DEFAULT, None
    value = section["max_laws"]
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return MAX_LAWS_DEFAULT, (
            f"laws.max_laws={value!r} is invalid (need an integer >= 1); "
            f"using the default {MAX_LAWS_DEFAULT}")
    return value, None


def load_tests_dir(raw: dict) -> Tuple[str, Optional[str]]:
    """``laws.tests_dir`` from .sdd-config.json (spec 4.1): a relative path without ``..``,
    else ``tests/laws`` plus a warning."""
    section = raw.get("laws")
    if not isinstance(section, dict) or "tests_dir" not in section:
        return TESTS_DIR_DEFAULT, None
    value = section["tests_dir"]
    bad = (not isinstance(value, str) or not value.strip() or value.startswith(("/", "\\"))
           or ".." in Path(value).parts or (len(value) > 1 and value[1] == ":"))
    if bad:
        return TESTS_DIR_DEFAULT, (
            f"laws.tests_dir={value!r} is invalid (need a relative path without '..'); "
            f"using the default {TESTS_DIR_DEFAULT!r}")
    return value.strip().strip("/"), None


def tests_target_for(tests_dir: str, feature: str) -> str:
    """``<tests_dir>/test_<feature>.py`` with ``/`` and ``-`` of the feature turned into ``_``."""
    return f"{tests_dir}/test_{feature.strip('/').replace('/', '_').replace('-', '_')}.py"


def is_point_candidate(c: Dict[str, Any]) -> bool:
    """FR-014: a candidate whose body has no ``for`` and whose ``kind`` is not an exempt base
    case goes to the differential tests instead of ``LAWS.bend``."""
    return (is_point_assertion(" ".join(str(c.get("body") or "").split()))
            and c.get("kind") not in POINT_EXEMPT_KINDS)


def section_key(section: str) -> Tuple[int, ...]:
    """Numeric sort key of a section number ("3.1.10" sorts after "3.1.2")."""
    return tuple(int(p) for p in re.findall(r"\d+", str(section))) or (10 ** 9,)


def rank_candidates(candidates: List[Dict[str, Any]], max_laws: int) -> Dict[str, Any]:
    """Order candidates and cut them off at ``max_laws`` (spec 3.1.2, NFR-005).

    Candidate keys: ``name``, ``section``, ``priority`` (1-4, the extraction-rule
    row), ``body`` (proposition text, used for duplicate detection), and the
    optional ``trivial`` flag set by the extractor. ``level == "binary"`` marks a
    property written on a binary operation although the fixed API has an aggregate
    function; any other value is ignored. ``rank`` does not read the API, so a
    missing ``level`` is not detected here.

    Order: priority first, then within one priority (1) a candidate whose ``kind``
    is a basic property (``BASIC_KINDS``), so a cut-off never drops commutativity /
    associativity / identity / empty-input / single-element laws before narrower
    ones, (2) the other candidates, (3) ``level == "binary"`` candidates last; then
    section number and name. Trivial candidates and repeated bodies are not adopted;
    the rest is adopted up to ``max_laws`` and the overflow is listed with a reason.

    Point assertions (FR-014: no ``for`` in the body, ``kind`` not in
    ``POINT_EXEMPT_KINDS``) are returned separately in ``to_tests`` with reason
    ``point_assertion``: they become differential pytest cases, do not count against
    ``max_laws`` and are judged after ``trivial`` / ``unbounded`` but before duplicates.
    """
    def norm(body: Any) -> str:
        return " ".join(str(body or "").split())

    ordered = sorted(
        candidates,
        key=lambda c: (int(c.get("priority", 9)),
                       2 if c.get("level") == "binary" else (0 if c.get("kind") in BASIC_KINDS else 1),
                       section_key(c.get("section", "")), str(c.get("name", ""))))
    adopted: List[Dict[str, Any]] = []
    not_adopted: List[Dict[str, Any]] = []
    to_tests: List[Dict[str, Any]] = []
    seen: Dict[str, str] = {}
    for c in ordered:
        body = norm(c.get("body"))
        if c.get("trivial"):
            not_adopted.append({**c, "reason": "trivial"})
        elif c.get("unbounded"):
            not_adopted.append({**c, "reason": "unbounded_nat"})
        elif is_point_candidate(c):
            to_tests.append({**c, "reason": "point_assertion",
                             "suggested_test": f"test_{c.get('name', '')}"})
        elif body and body in seen:
            not_adopted.append({**c, "reason": "duplicate", "duplicate_of": seen[body]})
        elif len(adopted) >= max_laws:
            not_adopted.append({**c, "reason": "limit"})
        else:
            adopted.append(c)
            if body:
                seen[body] = str(c.get("name", ""))
    return {"max_laws": max_laws, "adopted": adopted, "not_adopted": not_adopted,
            "to_tests": to_tests}


def find_spec(project_root: Path, spec_dir: str, feature: str) -> Optional[Path]:
    base = project_root / spec_dir
    for candidate in (base / f"{feature}_spec.md", base / f"{feature}.md",
                      base / feature / "index_spec.md", base / feature / "index.md"):
        if candidate.is_file():
            return candidate
    return None


def draft_write_target(approval_state: str, overwrite: bool) -> Tuple[str, Optional[str]]:
    """``(file to write, refusal reason)`` for ``draft`` (spec 3.1.0, FR-008).

    ``LAWS.bend`` is written only when it does not exist, or exists without any
    approval line and ``--overwrite`` was given. A ``LAWS.bend`` with an approval
    line (valid, expired or malformed) is never written, even with ``--overwrite``
    (the refusal reason says so); the proposal then goes to ``LAWS.draft.bend``,
    which is always replaceable.
    """
    if approval_state == "no_file":
        return LAWS_FILE, None
    if approval_state == "missing":
        return (LAWS_FILE, None) if overwrite else (DRAFT_FILE, None)
    reason = ("--overwrite refused: LAWS.bend has an approval line and is never overwritten "
              "(proposal goes to LAWS.draft.bend)") if overwrite else None
    return DRAFT_FILE, reason


def cmd_status(ns: argparse.Namespace) -> Dict[str, Any]:
    root = Path(resolve_project_root(ns.project_root))
    raw = read_sdd_config_json(str(root))
    paths = load_sdd_paths(str(root), raw)
    max_laws, max_warning = load_max_laws(raw)
    tests_dir, tests_warning = load_tests_dir(raw)
    warnings = [w for w in (max_warning, tests_warning) if w]
    feature = ns.feature.strip("/")
    out: Dict[str, Any] = {"feature": feature, "max_laws": max_laws, "warnings": warnings,
                           "tests_dir": tests_dir, "tests_target": tests_target_for(tests_dir, feature),
                           "spec": None, "spec_id": "", "ok": False}

    spec = find_spec(root, paths.specification_prefix, feature)
    if spec is None:
        out["error"] = f"spec not found for feature '{feature}' under {paths.specification_prefix}"
        return out
    text = spec.read_text(encoding="utf-8", errors="replace")
    spec_id = spec_id_of(text)
    fm_text, _ = split_front_matter(text)
    fm = parse_front_matter(fm_text) if fm_text else {}
    out.update(spec=str(spec.relative_to(root)), spec_id=spec_id)
    if not spec_id:
        out["error"] = "spec has no front matter 'id': '# spec:' cannot be written"
        return out
    out["ok"] = True

    laws_rel = f"{paths.laws_dir}/{feature}"
    laws_dir = root / paths.laws_prefix / feature
    laws_file = laws_dir / LAWS_FILE
    status = approval_status(laws_file)
    state = {"no_file": "none", "missing": "drafted", "valid": "approved"}.get(
        status.state, status.state)  # malformed / mismatch keep their names
    listed = fm.get("laws", [])
    listed = [listed] if isinstance(listed, str) else list(listed or [])
    laws_status = str(fm.get("laws-status", "") or "")
    if status.state == "valid" and laws_status not in ("approved", "proven"):
        warnings.append(f"approval line is valid but spec laws-status is '{laws_status or 'unset'}' "
                        "(a human updates it to approved)")
    if status.state != "no_file" and laws_rel not in [x.strip("/") for x in listed]:
        warnings.append(f"spec 'laws:' does not list '{laws_rel}': the proof gate reports orphan "
                        "laws (FAIL, table row #4) until a human adds it")
    impl = resolve_impl(text, laws_dir)
    if impl["source"] == "none":
        warnings.append("impl_undeclared: the spec has no 'impl-of:' line and main.bend has no "
                        "'# model-of:'; add 'impl-of: <path>' to the spec so the model and the "
                        "differential tests point at the implementation (spec 3.1.5)")
    out["impl"] = impl
    out.update(
        laws_dir=str(laws_dir.relative_to(root)),
        laws_dir_sdd_relative=laws_rel,
        laws_state=state,
        approval_state=status.state,
        current_hash=status.current_hash,
        approval=status.approval,
        laws_status=laws_status,
        has_draft_file=(laws_dir / DRAFT_FILE).is_file(),
        has_model=(laws_dir / MODEL_FILE).is_file(),
        has_proof=(laws_dir / PROOF_FILE).is_file(),
        model_allowed=(status.state == "valid"),
    )
    target, refusal = draft_write_target(status.state, ns.overwrite)
    out["write_target"] = target
    if refusal:
        out["overwrite_refused"] = refusal
    if status.state != "valid":
        out["model_refusal"] = {
            "no_file": "LAWS.bend does not exist",
            "missing": "LAWS.bend has no approval line",
            "malformed": "the approval line is malformed",
            "mismatch": "the approval line does not match the current law text (approval expired)",
        }[status.state]
        # FR-009: how a human approves (the skill never writes this line itself).
        out["approval_format"] = ("# approved: YYYY-MM-DD <approver> "
                                  f"sha256:{status.current_hash}") if status.current_hash else None
    return out


def cmd_model_api(ns: argparse.Namespace) -> Dict[str, Any]:
    """Which model API ``draft`` must use: the spec declaration, else ``main.bend``, else none."""
    root = Path(resolve_project_root(ns.project_root))
    paths = load_sdd_paths(str(root), read_sdd_config_json(str(root)))
    feature = ns.feature.strip("/")
    spec = find_spec(root, paths.specification_prefix, feature)
    text = spec.read_text(encoding="utf-8", errors="replace") if spec else None
    source, api = fixed_model_api(text, root / paths.laws_prefix / feature)
    out: Dict[str, Any] = {"feature": feature, "source": source, "fixed": source in ("spec", "main.bend"),
                           "functions": [{"name": f"Model.{k}", "signature": v} for k, v in api.items()]}
    if source == "main.bend-unreadable":
        out["warning"] = ("main.bend exists but no 'def' could be read from it: the model API is "
                          "not fixed and the fixed-API check is off; fix main.bend or declare "
                          "'model-api:' in the spec")
    if source == "unfixed":
        out["note"] = ("no spec declaration and no main.bend: propose the API yourself and mark it "
                       "'unfixed - needs confirmation' in the report")
    return out


def cmd_hash(ns: argparse.Namespace) -> Dict[str, Any]:
    digest = section_hash_of_file(Path(ns.spec), ns.section)
    return {"spec": ns.spec, "section": ns.section.lstrip("§"), "hash": digest,
            "ok": digest is not None}


def cmd_rank(ns: argparse.Namespace) -> Dict[str, Any]:
    data = json.load(sys.stdin if ns.file in (None, "-") else open(ns.file, encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("candidates", [])
    if not isinstance(data, list):
        raise SystemExit("candidates must be a JSON array")
    return rank_candidates(data, ns.max)


def cmd_check(ns: argparse.Namespace) -> Dict[str, Any]:
    """Static checks. ``--feature`` (with ``--project-root``) resolves the fixed model API the
    way ``model-api`` does (the spec found for the feature, ``main.bend`` of its laws
    directory), so a file kept outside the laws directory is still checked against it. The
    result states the API source; when it is not fixed, ``notes`` says check 6 did not run."""
    spec_path = Path(ns.spec) if ns.spec else None
    model_dir: Optional[Path] = None
    if ns.feature:
        root = Path(resolve_project_root(ns.project_root))
        paths = load_sdd_paths(str(root), read_sdd_config_json(str(root)))
        feature = ns.feature.strip("/")
        model_dir = root / paths.laws_prefix / feature
        if spec_path is None:
            spec_path = find_spec(root, paths.specification_prefix, feature)
    tests = getattr(ns, "tests", "")
    if not ns.laws_file:
        if not tests:
            raise SystemExit("check: give a laws file, --tests <pytest file>, or both")
        findings = check_test_sources(Path(tests), spec_path)
        errs = [f for f in findings if f.severity == "error"]
        return {"tests_file": tests, "findings": [f._asdict() for f in findings],
                "errors": len(errs), "warnings": len(findings) - len(errs),
                "propose_drafted": not has_errors(findings)}
    laws = Path(ns.laws_file)
    spec_text = spec_path.read_text(encoding="utf-8", errors="replace") if spec_path else None
    source, api = fixed_model_api(spec_text, model_dir or laws.parent)
    findings = static_check(laws, spec_path, tolerate_missing_model=not ns.require_model,
                            fixed_api=api, model_dir=model_dir)
    if source == "main.bend-unreadable":
        findings.append(Finding(
            "model_api_source_unreadable", "warning", "",
            "main.bend exists but no 'def' could be read from it: check 6 did not run"))
    for fn in spec_model_api_duplicates(spec_text or ""):
        findings.append(Finding(
            "model_api_duplicate", "warning", "",
            f"the spec declares Model.{fn} in more than one 'model-api:' line; the first is used"))
    if tests:
        findings.extend(check_test_sources(Path(tests), spec_path))
    errs = [f for f in findings if f.severity == "error"]
    out: Dict[str, Any] = {
        "laws_file": ns.laws_file, "tests_file": tests or None,
        "findings": [f._asdict() for f in findings],
        "errors": len(errs), "warnings": len(findings) - len(errs),
        "propose_drafted": not has_errors(findings),
        "model_api": {"source": source, "fixed": source in ("spec", "main.bend"),
                      "functions": sorted(api)}}
    if not out["model_api"]["fixed"]:
        out["notes"] = ["the model API is not fixed (no spec 'model-api:' line and no readable "
                        "main.bend): check 6 (fixed-API names) did not run; pass --feature "
                        "[--project-root] when the file is outside the laws directory"]
    return out


def cmd_migrate(ns: argparse.Namespace) -> Dict[str, Any]:
    """FR-016: classify the laws of an existing ``LAWS.bend`` for the human-run migration.
    Read-only. ``prose_delete`` when the implementation is prose (3.1.5); otherwise a law with
    no ``for`` is ``to_tests`` (FR-014) and the rest ``keep``. Existing laws carry no ``kind``,
    so an empty-input / single-element / identity law that landed in ``to_tests`` is moved back
    to ``keep`` by the human (the report says so)."""
    root = Path(resolve_project_root(ns.project_root))
    raw = read_sdd_config_json(str(root))
    paths = load_sdd_paths(str(root), raw)
    tests_dir, _ = load_tests_dir(raw)
    feature = ns.feature.strip("/")
    laws_dir = root / paths.laws_prefix / feature
    laws_file = laws_dir / LAWS_FILE
    spec = find_spec(root, paths.specification_prefix, feature)
    text = spec.read_text(encoding="utf-8", errors="replace") if spec else None
    impl = resolve_impl(text, laws_dir)
    out: Dict[str, Any] = {"feature": feature, "spec": str(spec.relative_to(root)) if spec else None,
                           "laws_file": str(laws_file.relative_to(root)), "impl": impl,
                           "tests_target": tests_target_for(tests_dir, feature),
                           "approval_state": approval_status(laws_file).state,
                           "laws": [], "keep": 0, "to_tests": 0, "prose_delete": 0, "ok": False}
    if not laws_file.is_file():
        out["error"] = f"{LAWS_FILE} not found: {laws_file}"
        return out
    out["ok"] = True
    for law in parse_laws(laws_file):
        kind_guess = "empty" if EMPTY_INPUT_RE.search(law.body) else None
        if not impl["lawifiable"]:
            cls = "prose_delete"
        elif is_point_assertion(law.body) and kind_guess is None:
            cls = "to_tests"
        else:
            cls = "keep"
        entry: Dict[str, Any] = {"law": law.name, "line": law.line, "classification": cls,
                                 "section": law.source.section if law.source else None,
                                 "has_for": FOR_DECL_RE.search(law.body) is not None,
                                 "kind_guess": kind_guess}
        if cls == "to_tests":
            entry["suggested_test"] = f"test_{law.name}"
        out["laws"].append(entry)
        out[cls] += 1
    out["human_review_note"] = (
        "existing laws carry no 'kind': an empty-input law is recognised by 'Nil{}' / '[]' in its "
        "body (kind_guess) and kept; a single-element / identity law without 'for' that landed "
        "under to_tests stays in Bend (FR-014 exemption) and the human moves it back to keep")
    return out


def normalise_proposition(body: str, constants: Dict[str, str]) -> str:
    """Comparison form of a law body (spec section 11 stage 1): the ``for`` variables are renamed
    by order of declaration (alpha equivalence), ``Model.<fn>()`` of a constant ``def`` of
    ``main.bend`` is replaced by its literal (``Model.rank_fail()`` and ``4n`` agree) and the
    empty-list sugar ``[]`` reads as ``Nil{}``."""
    names: List[str] = []
    for m in FOR_DECL_RE.finditer(body):
        names.extend(n.strip() for n in m.group(1).split(","))
    renames = {n: f"_v{i}" for i, n in enumerate(dict.fromkeys(names))}
    if renames:
        body = re.sub(r"(?<![\w.])(" + "|".join(map(re.escape, renames)) + r")(?!\w)",
                      lambda m: renames[m.group(1)], body)
    for fn, lit in constants.items():
        body = re.sub(rf"\bModel\.{re.escape(fn)}\(\s*\)", lit, body)
    return " ".join(body.replace("[]", "Nil{}").split())


def _propositions(path: Path, constants: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """law name -> comment-free whitespace-normalised body (``# source:`` and
    ``# model-api:`` lines are comments and never part of a body). With ``constants`` the body
    is the comparison form (``normalise_proposition``)."""
    if constants is None:
        return {law.name: law.body for law in parse_laws(path)}
    return {law.name: normalise_proposition(law.body, constants) for law in parse_laws(path)}


JUDGEMENTS = ("equivalent", "weak", "none")


def _load_json_object(path: str, what: str) -> Dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"{what}: cannot read {path} as JSON ({exc})")
    if not isinstance(data, dict):
        raise SystemExit(f"{what}: {path} must contain a JSON object")
    return data


def _normalise_judgements(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """``{law: "equivalent"}`` or ``{law: {"verdict": ..., "generated_name": ..., "note": ...}}``
    -> ``{law: {"verdict", "generated_name", "note"}}``; anything else exits with a message."""
    out: Dict[str, Dict[str, Any]] = {}
    for law, value in raw.items():
        entry = value if isinstance(value, dict) else {"verdict": value}
        verdict = entry.get("verdict")
        if verdict not in JUDGEMENTS:
            raise SystemExit(f"judgement for '{law}': verdict must be one of {JUDGEMENTS}, got {verdict!r}")
        out[law] = {"verdict": verdict, "generated_name": entry.get("generated_name"),
                    "note": entry.get("note")}
    return out


def cmd_compare(ns: argparse.Namespace) -> Dict[str, Any]:
    """Two-stage acceptance (spec section 11). Stage 1 is mechanical: every reference law
    must appear (same name and body, or the same body under another name) in the comparison
    form of ``normalise_proposition`` (variable names, constant ``Model.rank_*()`` calls and
    ``[]`` / ``Nil{}`` do not matter). Stage 2 covers
    the mechanical misses only: a human records ``equivalent`` / ``weak`` / ``none`` per law
    in the ``--judgement`` JSON (a judgement on a mechanically matched law is ignored and
    listed in ``ignored_judgements``). ``passed`` needs every law matched or ``equivalent``;
    ``weak`` and ``none`` fail. A reference with no laws, or a ``--check-result`` (the JSON
    printed by ``check``) with errors, never passes."""
    model = Path(getattr(ns, "model", "") or Path(ns.reference).parent / MODEL_FILE)
    constants = model_constants(model)
    generated = _propositions(Path(ns.generated), constants)
    reference = _propositions(Path(ns.reference), constants)
    judgements = _normalise_judgements(_load_json_object(ns.judgement, "--judgement")) \
        if ns.judgement else {}
    check_errors = 0
    if getattr(ns, "check_result", ""):
        check_errors = int(_load_json_object(ns.check_result, "--check-result").get("errors", 0))
    by_body = {body: name for name, body in generated.items()}
    rows = []
    for name, body in reference.items():
        if generated.get(name) == body:
            row = {"law": name, "match": "exact", "generated_name": name}
        elif body in by_body:
            row = {"law": name, "match": "proposition", "generated_name": by_body[body]}
        else:
            j = judgements.get(name)
            row = {"law": name, "match": "none", "reference_body": body,
                   "same_name_body": generated.get(name),
                   "human_judgement": j["verdict"] if j else None}
            if j:
                row.update(judged_generated_name=j["generated_name"], judgement_note=j["note"])
        rows.append(row)
    extra = sorted(set(generated) - {r["generated_name"] for r in rows if r["match"] != "none"})
    mechanical = bool(rows) and all(r["match"] != "none" for r in rows)
    matched = {r["law"] for r in rows if r["match"] != "none"}
    out: Dict[str, Any] = {
        "results": rows, "extra_generated": extra, "passed_mechanical": mechanical,
        "pending_judgement": [r["law"] for r in rows if r["match"] == "none" and r["human_judgement"] is None],
        "ignored_judgements": sorted(matched & set(judgements)),
        "unknown_judgements": sorted(set(judgements) - set(reference)),
        "check_errors": check_errors,
    }
    out["passed"] = bool(rows) and check_errors == 0 and all(
        r["match"] != "none" or r["human_judgement"] == "equivalent" for r in rows)
    if not rows:
        out["error"] = f"reference has no laws: {ns.reference}"
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="draft_laws.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("feature")
    s.add_argument("--project-root", default="")
    s.add_argument("--overwrite", action="store_true",
                   help="allow replacing an unapproved LAWS.bend (never one with an approval line)")
    s.set_defaults(fn=cmd_status)
    m = sub.add_parser("model-api")
    m.add_argument("feature")
    m.add_argument("--project-root", default="")
    m.set_defaults(fn=cmd_model_api)
    h = sub.add_parser("hash")
    h.add_argument("spec")
    h.add_argument("section")
    h.set_defaults(fn=cmd_hash)
    r = sub.add_parser("rank")
    r.add_argument("--max", type=int, default=MAX_LAWS_DEFAULT)
    r.add_argument("file", nargs="?")
    r.set_defaults(fn=cmd_rank)
    c = sub.add_parser("check")
    c.add_argument("laws_file", nargs="?", default="")
    c.add_argument("--spec", default="")
    c.add_argument("--tests", default="",
                   help="differential pytest file: check its '# source:' lines (3.1.3 check 9)")
    c.add_argument("--feature", default="",
                   help="resolve the fixed model API from this feature's spec / laws dir")
    c.add_argument("--project-root", default="")
    c.add_argument("--require-model", action="store_true",
                   help="main.bend must exist (use after the model stage)")
    c.set_defaults(fn=cmd_check)
    g = sub.add_parser("migrate")
    g.add_argument("feature")
    g.add_argument("--project-root", default="")
    g.set_defaults(fn=cmd_migrate)
    k = sub.add_parser("compare")
    k.add_argument("generated")
    k.add_argument("reference")
    k.add_argument("--model", default="",
                   help="main.bend whose constant defs (rank_*) read as literals; default: beside the reference")
    k.add_argument("--check-result", default="",
                   help="JSON printed by `check` for the generated file; errors > 0 forces passed=false")
    k.add_argument("--judgement", default="",
                   help="JSON {law: equivalent|weak|none}: human judgement of the mechanical misses")
    k.set_defaults(fn=cmd_compare)
    return p


def main() -> None:
    ns = build_parser().parse_args()
    result = ns.fn(ns)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if (ns.cmd in ("status", "migrate") and not result.get("ok")) or (ns.cmd == "compare" and "error" in result):
        sys.exit(1)


if __name__ == "__main__":
    main()
