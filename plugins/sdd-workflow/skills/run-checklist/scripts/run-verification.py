#!/usr/bin/env python3
"""
run-verification.py
Detect the project's toolchain and run one verification category
(test / lint / typecheck / security / proof) for the /run-checklist skill.

This script exists so the skill's `allowed-tools` can pre-approve a single
scoped Bash invocation (per this repo's Check 5.4 convention) instead of a
bare `Bash` grant. The category-to-command mapping mirrors
`references/verification_commands.md`; see that file for the full mapping
this script implements. Claude reads the JSON result on stdout — the script
owns command detection and execution, Claude only interprets the outcome.

The ``proof`` category (Bend proof gate, proof-gate_spec.md) takes options, so
``main()`` dispatches it to ``main_proof()`` before the legacy single-argument
path; the four original categories are unchanged. Its decision rows live in
pure functions (``precheck`` / ``orphan_reason`` / ``needs_plain_fallback`` /
``judge_run`` / ``aggregate``) so the table in spec 3.1.1 is unit-testable
without spawning ``bend``.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# skills/run-checklist/scripts/ -> plugins/sdd-workflow/scripts/ (shared modules)
# Imported eagerly on purpose: these are stdlib-only modules shipped in the same plugin
# tree, so loading them cannot fail independently of this script, and the proof functions
# below are called directly by tests (a lazy import would need threading through each).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from laws_drafting import source_drift  # noqa: E402
from doc_walker import iter_specification_docs  # noqa: E402
from fm_parser import parse_front_matter, split_front_matter  # noqa: E402
from hook_common import load_proof_config, load_sdd_paths  # noqa: E402
from laws_header import (  # noqa: E402
    LAWS_FILE,
    MODEL_FILE,
    PROOF_FILE,
    declares_laws,
    disallowed_imports,
    imports_laws,
    law_body_hash,
    read_header,
    valid_approval,
)

VALID_CATEGORIES = ("test", "lint", "typecheck", "security", "proof")

# (detection file, project type), checked in this order (see verification_commands.md
# "Detection Priority").
DETECTION_ORDER = (
    ("package.json", "node"),
    ("pyproject.toml", "python"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
    ("setup.py", "python"),
    ("requirements.txt", "python"),
    ("Gemfile", "ruby"),
)

# Candidate commands per (project_type, category), tried in order until one's
# executable is found. Each command's first token is checked with shutil.which
# semantics (via FileNotFoundError) so an unavailable tool falls through to
# the next candidate, or to SKIPPED if none are available.
COMMANDS = {
    "node": {
        "test": ["npm test"],
        "lint": ["npx eslint .", "eslint ."],
        "typecheck": ["npx tsc --noEmit", "tsc --noEmit"],
        "security": ["npm audit"],
    },
    "python": {
        "test": ["pytest"],
        "lint": ["ruff check ."],
        "typecheck": ["mypy ."],
        "security": ["pip-audit", "safety check"],
    },
    "rust": {
        "test": ["cargo test"],
        "lint": ["cargo clippy"],
        "typecheck": [],  # built into `cargo build`; no separate step
        "security": ["cargo audit"],
    },
    "go": {
        "test": ["go test ./..."],
        "lint": ["golangci-lint run"],
        "typecheck": [],  # built into `go build`; no separate step
        "security": ["govulncheck ./..."],
    },
    "ruby": {
        "test": ["bundle exec rspec"],
        "lint": ["bundle exec rubocop"],
        "typecheck": [],
        "security": ["bundle exec bundler-audit"],
    },
}

TIMEOUT_SECONDS = 300

# Non-zero exit codes that mean "there was nothing to verify" rather than
# "verification failed", keyed by the command's executable. A project that has
# no tests configured yet must not fail the quality gate — the checklist item
# should read SKIPPED, the same as an uninstalled tool.
NO_WORK_EXIT_CODES = {
    "pytest": (5,),  # pytest exits 5 when it collects no tests
}

# Output markers with the same meaning, for tools that reuse a generic exit
# code (e.g. `npm test` against a package.json that defines no "test" script).
NO_WORK_OUTPUT_MARKERS = ("missing script",)


def log(message: str) -> None:
    print(f"[run-verification] {message}", file=sys.stderr)


def detect_project_type(project_root: Path) -> Optional[str]:
    for filename, project_type in DETECTION_ORDER:
        if (project_root / filename).exists():
            return project_type
    # No manifest file present. Fall back to a directory-shape heuristic so
    # minimal projects (e.g. a `tests/` folder with no packaging metadata
    # yet) still get verified instead of silently skipped.
    for dirname in ("tests", "test"):
        test_dir = project_root / dirname
        if not test_dir.is_dir():
            continue
        # `Path.rglob()` returns a generator, which is truthy even when it
        # yields nothing — pull the first match explicitly so the pattern
        # actually decides the outcome rather than the generator's identity.
        if any(next(test_dir.rglob(pattern), None) is not None
               for pattern in ("test_*.py", "*_test.py")):
            return "python"
    return None


def nothing_to_verify(tool: str, result: subprocess.CompletedProcess) -> bool:
    """Return True if a non-zero exit means "nothing to check", not "failed"."""
    if result.returncode in NO_WORK_EXIT_CODES.get(tool, ()):
        return True
    combined = f"{result.stdout or ''}\n{result.stderr or ''}".lower()
    return any(marker in combined for marker in NO_WORK_OUTPUT_MARKERS)


def run_command(command: str, cwd: Path) -> dict:
    args = shlex.split(command)
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
            encoding="utf-8", errors="replace",
        )
        outcome = {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout[-8000:],
            "stderr": result.stderr[-4000:],
        }
        if result.returncode == 0:
            return {"status": "PASS", **outcome}
        if nothing_to_verify(args[0], result):
            return {
                "status": "SKIPPED",
                "reason": f"'{command}' ran but had nothing to verify (no tests "
                          "collected, or no such script defined). This is not a "
                          "verification failure.",
                **outcome,
            }
        return {"status": "FAIL", **outcome}
    except FileNotFoundError:
        return {"status": "TOOL_NOT_FOUND", "command": command}
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "command": command,
            "timeout_seconds": TIMEOUT_SECONDS,
        }


# --- proof category (Bend proof gate) ----------------------------------------
#
# Decision table: proof-gate_spec.md 3.1.1 (row numbers below refer to it).

BENDTT_INFRA_MARKER = "BendTT infrastructure"
ALL_PROOFS_CHECK = "ALL PROOFS CHECK"
# Aggregation order: the worst status of all laws directories wins.
SEVERITY = {"FAIL": 4, "TIMEOUT": 3, "TOOL_NOT_FOUND": 2, "SKIPPED": 1, "PASS": 0}
PASS_NOTE = ("PASS means the reference model (main.bend) satisfies the approved laws. "
             "It does not prove the project's implementation.")


def discover_laws_dirs(laws_root: Path) -> List[Path]:
    """Directories under laws_root that directly contain LAWS.bend or PROOF.bend.

    Intermediate directories of a hierarchical layout are not counted (they
    would otherwise each report SKIPPED).
    """
    if not laws_root.is_dir():
        return []
    found = {p.parent for name in (LAWS_FILE, PROOF_FILE) for p in laws_root.rglob(name)}
    return sorted(found)


def build_spec_registry(spec_root: Path) -> Dict[str, Dict[str, object]]:
    """id -> {"path": Path, "laws": [str]} for every spec under the specification dir.

    Reuses doc_walker / fm_parser (the same front matter rules the hooks and
    sdd_index apply) instead of a new id resolver. Built once per proof run and
    shared by every laws directory (row #4).
    """
    registry: Dict[str, Dict[str, object]] = {}
    for spec_file in iter_specification_docs(spec_root):
        try:
            text = spec_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm_text, _ = split_front_matter(text)
        fm = parse_front_matter(fm_text) if fm_text else {}
        spec_id = fm.get("id")
        if isinstance(spec_id, str) and spec_id:
            laws = fm.get("laws", [])
            registry[spec_id] = {
                "path": spec_file,
                "laws": [laws] if isinstance(laws, str) else list(laws or []),
            }
    return registry


def orphan_reason(spec_id: Optional[str], laws_dir_sdd_relative: str,
                  registry: Dict[str, Dict[str, object]]) -> Optional[str]:
    """Row #4. None means the laws dir is bound to a spec in both directions."""
    if spec_id is None:
        return (f"orphan laws: {LAWS_FILE} has no '# spec:' line, so the laws directory "
                "is not bound to any spec")
    entry = registry.get(spec_id)
    if entry is None:
        return (f"orphan laws: '# spec: {spec_id}' does not resolve to any spec under "
                "the specification directory")
    listed = [str(x).strip().strip("/") for x in entry["laws"]]  # type: ignore[index]
    if laws_dir_sdd_relative.strip("/") not in listed:
        return (f"orphan laws: {entry['path']} (id {spec_id}) does not list "
                f"'{laws_dir_sdd_relative}' in its laws: front matter")
    return None


def precheck(bend_found: bool, dir_exists: bool, has_laws: bool, orphan: Optional[str],
             approved: Optional[str], has_law_decl: bool, has_proof: bool,
             proof_imports_laws: bool, bad_imports: List[str]) -> Optional[Dict[str, str]]:
    """Rows #1-#8, evaluated in order. None means "run bend"."""
    if not bend_found:
        return {"status": "TOOL_NOT_FOUND", "reason": "bend is not installed (not on PATH)"}
    if not dir_exists:
        return {"status": "FAIL",
                "reason": "laws directory not found (check the spec's laws: entry)"}
    if not has_laws:
        return {"status": "SKIPPED", "reason": f"no {LAWS_FILE} in this laws directory"}
    if orphan is not None:
        return {"status": "FAIL", "reason": orphan}
    if approved is None:
        return {"status": "SKIPPED",
                "reason": f"{LAWS_FILE} has no valid '# approved:' line (missing, malformed, "
                          "or its content hash no longer matches the law body); unapproved "
                          "laws are never reported as PASS"}
    if not has_law_decl:
        return {"status": "SKIPPED", "reason": f"{LAWS_FILE} declares no laws"}
    if not has_proof:
        return {"status": "FAIL", "reason": f"{LAWS_FILE} is approved but {PROOF_FILE} is missing"}
    if not proof_imports_laws:
        return {"status": "FAIL", "reason": f"{PROOF_FILE} does not import {LAWS_FILE}"}
    if len(bad_imports) > 0:
        return {"status": "FAIL",
                "reason": "disallowed import (only 'import Base' and "
                          "'import ./<file>.bend as <Name>' of a .bend file inside the "
                          "laws directory are allowed): "
                          + "; ".join(bad_imports)}
    return None


def needs_plain_fallback(exit_code: Optional[int], stderr: str, verdict_requested: bool) -> bool:
    """Row #11: --verdict was asked for but the Lean re-check kernel is unavailable."""
    return verdict_requested and exit_code not in (0, None) and BENDTT_INFRA_MARKER in stderr


def judge_run(exit_code: Optional[int], stdout: str, timed_out: bool) -> Dict[str, str]:
    """Rows #9, #10, #12 for a finished bend run."""
    if timed_out:
        return {"status": "TIMEOUT", "reason": "bend exceeded the time limit"}
    if exit_code == 0 and ALL_PROOFS_CHECK in stdout:
        return {"status": "PASS", "reason": f"bend reported {ALL_PROOFS_CHECK}"}
    if exit_code == 0:
        return {"status": "FAIL", "reason": f"bend exited 0 but did not report {ALL_PROOFS_CHECK}"}
    return {"status": "FAIL",
            "reason": f"bend exited {exit_code} (SOME PROOFS FAIL or a syntax error)"}


def run_bend(laws_dir: Path, verdict: bool, timeout: int) -> Dict[str, object]:
    """Spawn ``bend [--verdict] PROOF.bend`` inside laws_dir with telemetry disabled."""
    args = ["bend"] + (["--verdict"] if verdict else []) + [PROOF_FILE]
    env = dict(os.environ, BEND_NO_TELEMETRY="1")
    try:
        r = subprocess.run(args, cwd=laws_dir, env=env, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return {"command": " ".join(args), "exit_code": r.returncode,
                "stdout": r.stdout[-8000:], "stderr": r.stderr[-4000:], "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"command": " ".join(args), "exit_code": None, "stdout": "", "stderr": "",
                "timed_out": True}
    except OSError as e:  # bend vanished between which() and run(), or is not executable
        return {"command": " ".join(args), "exit_code": None, "stdout": "", "stderr": str(e),
                "timed_out": False, "launch_error": True}


def _sdd_relative(laws_dir: Path, sdd_root: Path) -> str:
    try:
        return laws_dir.resolve().relative_to(sdd_root.resolve()).as_posix()
    except ValueError:  # outside ${SDD_ROOT}: can never match a spec's laws: entry
        return laws_dir.as_posix()


def run_proof_dir(laws_dir: Path, verdict: bool, timeout: int, sdd_root: Path,
                  registry: Dict[str, Dict[str, object]],
                  bend_found: Optional[bool] = None) -> Dict[str, object]:
    """Decision for one laws directory (rows #1-#12) plus the additive FR-013 warnings."""
    if bend_found is None:
        bend_found = shutil.which("bend") is not None
    result = _decide_proof_dir(laws_dir, verdict, timeout, sdd_root, registry, bend_found)
    warnings = drift_warnings(laws_dir, sdd_root, registry, bend_found)
    if warnings:
        result["warnings"] = warnings
    return result


def drift_warnings(laws_dir: Path, sdd_root: Path, registry: Dict[str, Dict[str, object]],
                   bend_found: bool) -> List[Dict[str, str]]:
    """FR-013: source_drift / source_invalid for an approved, bound laws directory.

    Never changes the status: only directories with a valid approval line that
    passed the orphan check (row #4) are evaluated, and nothing is reported
    when bend is absent (the static check and the hook cover that case).
    """
    laws = laws_dir / LAWS_FILE
    if not bend_found or not laws.is_file():
        return []
    if valid_approval(read_header(laws), law_body_hash(laws)) is None:
        return []
    spec_values = read_header(laws).get("spec", [])
    spec_id = spec_values[0] if spec_values else None
    if orphan_reason(spec_id, _sdd_relative(laws_dir, sdd_root), registry) is not None:
        return []
    try:
        return source_drift(laws, Path(str(registry[str(spec_id)]["path"])))
    except OSError:
        return []


def _decide_proof_dir(laws_dir: Path, verdict: bool, timeout: int, sdd_root: Path,
                      registry: Dict[str, Dict[str, object]],
                      bend_found: bool) -> Dict[str, object]:
    laws = laws_dir / LAWS_FILE
    proof = laws_dir / PROOF_FILE
    model = laws_dir / MODEL_FILE
    has_laws = laws.is_file()
    header = read_header(laws) if has_laws else {}
    model_header = read_header(model) if model.is_file() else {}
    current_hash = law_body_hash(laws) if has_laws else ""
    approved = valid_approval(header, current_hash) if has_laws else None
    spec_values = header.get("spec", [])
    base: Dict[str, object] = {
        "laws_dir": str(laws_dir),
        "spec": spec_values[0] if len(spec_values) > 0 else None,
        "approved": approved,
        "model_of": model_header.get("model-of", []),
        "verdict": "checked" if verdict else "not-requested",
    }
    early = precheck(
        bend_found=bend_found,
        dir_exists=laws_dir.is_dir(),
        has_laws=has_laws,
        orphan=(orphan_reason(base["spec"], _sdd_relative(laws_dir, sdd_root), registry)  # type: ignore[arg-type]
                if has_laws else None),
        approved=approved,
        has_law_decl=declares_laws(laws) if has_laws else False,
        has_proof=proof.is_file(),
        proof_imports_laws=imports_laws(proof) if proof.is_file() else False,
        bad_imports=disallowed_imports(laws_dir) if laws_dir.is_dir() else [],
    )
    if early is not None:
        if has_laws and approved is None and early["status"] == "SKIPPED":
            # spec §4.1: give the current hash so the approver can write the line directly.
            early = {**early,
                     "reason": early["reason"] + f" Current law-body hash: sha256:{current_hash}"}
        return {**base, **early}

    run = run_bend(laws_dir, verdict, timeout)
    if run.get("launch_error"):
        return {**base, "status": "TOOL_NOT_FOUND",
                "reason": f"bend could not be launched: {run['stderr']}"}
    exit_code = run["exit_code"] if isinstance(run["exit_code"], int) else None
    if needs_plain_fallback(exit_code, str(run["stderr"]), verdict):
        base["verdict"] = "unavailable"  # FR-006: keep the primary verdict, note the gap
        run = run_bend(laws_dir, False, timeout)
        if run.get("launch_error"):
            return {**base, "status": "TOOL_NOT_FOUND",
                    "reason": f"bend could not be launched: {run['stderr']}"}
        exit_code = run["exit_code"] if isinstance(run["exit_code"], int) else None
    outcome = judge_run(exit_code, str(run["stdout"]), bool(run["timed_out"]))
    return {**base, **outcome,
            **{k: run[k] for k in ("command", "exit_code", "stdout", "stderr")}}


def aggregate(results: List[Dict[str, object]], verdict_requested: bool) -> Dict[str, object]:
    """Worst status wins; its directory's reason becomes the top-level reason."""
    if len(results) == 0:
        return {"status": "SKIPPED", "reason": "no laws directories found",
                "verdict": "checked" if verdict_requested else "not-requested"}
    worst = max(results, key=lambda r: SEVERITY[str(r["status"])])
    verdicts = {str(r.get("verdict")) for r in results}
    if "unavailable" in verdicts:
        verdict = "unavailable"
    elif verdict_requested:
        verdict = "checked"
    else:
        verdict = "not-requested"
    n_worst = sum(1 for r in results if r["status"] == worst["status"])
    reason = (f"{n_worst} of {len(results)} laws directories {worst['status']}: "
              f"{worst['laws_dir']} - {worst['reason']}")
    return {"status": str(worst["status"]), "reason": reason, "verdict": verdict}


def main_proof(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(prog="run-verification.py proof")
    parser.add_argument("--laws-dir", action="append", default=[],
                        help="laws directory (project-relative); repeatable. "
                             "Default: discover under SDD_LAWS_PATH")
    parser.add_argument("--verdict", action="store_true", default=None,
                        help="also re-check with the Lean kernel (falls back to the plain "
                             "check if unavailable)")
    parser.add_argument("--timeout", type=int, default=None, help="seconds per laws directory")
    parser.add_argument("--print-laws-hash", action="store_true",
                        help="print the LAWS.bend law-body hash for each directory and exit")
    ns = parser.parse_args(argv)

    project_root = Path.cwd()
    config = load_proof_config(str(project_root))
    paths = load_sdd_paths(str(project_root))
    verdict = bool(config["verdict"]) if ns.verdict is None else True
    timeout = (ns.timeout if ns.timeout is not None and ns.timeout > 0
               else int(config["timeout_seconds"]))

    if len(ns.laws_dir) > 0:
        laws_dirs = [project_root / d for d in ns.laws_dir]
    else:
        laws_dirs = discover_laws_dirs(project_root / paths.laws_prefix)

    def rel(p: Path) -> str:
        return os.path.relpath(str(p), str(project_root))

    if ns.print_laws_hash:
        hashes = {rel(d): law_body_hash(d / LAWS_FILE)
                  for d in laws_dirs if (d / LAWS_FILE).is_file()}
        print(json.dumps({"category": "proof", "laws_hash": hashes},
                         ensure_ascii=False, indent=2))
        return

    sdd_root = project_root / paths.root
    registry = build_spec_registry(project_root / paths.specification_prefix)
    bend_found = shutil.which("bend") is not None
    results = [run_proof_dir(d, verdict, timeout, sdd_root, registry, bend_found)
               for d in laws_dirs]
    for r in results:
        r["laws_dir"] = rel(Path(str(r["laws_dir"])))
    summary = aggregate(results, verdict)
    print(json.dumps({"category": "proof", **summary, "timeout_seconds": timeout,
                      "results": results, "note": PASS_NOTE},
                     ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "proof":
        main_proof(sys.argv[2:])
        return
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_CATEGORIES:
        log(f"Usage: run-verification.py <{'|'.join(VALID_CATEGORIES)}>"
            " | proof [--laws-dir DIR ...] [--verdict] [--timeout SEC] [--print-laws-hash]")
        sys.exit(2)
    category = sys.argv[1]

    project_root = Path.cwd()
    project_type = detect_project_type(project_root)

    if project_type is None:
        result = {
            "category": category,
            "project_type": None,
            "status": "SKIPPED",
            "reason": "No recognized project manifest found "
                      "(package.json, pyproject.toml, Cargo.toml, go.mod, setup.py, "
                      "requirements.txt, Gemfile).",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    candidates = COMMANDS.get(project_type, {}).get(category, [])
    if not candidates:
        result = {
            "category": category,
            "project_type": project_type,
            "status": "SKIPPED",
            "reason": f"No {category} command is defined for project type '{project_type}' "
                      "(e.g. this category has no separate tool for this ecosystem).",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    attempts = []
    for command in candidates:
        outcome = run_command(command, project_root)
        attempts.append(outcome)
        if outcome["status"] not in ("TOOL_NOT_FOUND",):
            result = {"category": category, "project_type": project_type, **outcome}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

    # Every attempt above returned to the loop only on TOOL_NOT_FOUND (any other
    # status returns immediately), so reaching here means all candidates were
    # missing -- report TOOL_NOT_FOUND (see SKILL.md's status table) rather than
    # SKIPPED, which is reserved for "no candidate command is defined" and
    # "the tool ran but had nothing to verify".
    result = {
        "category": category,
        "project_type": project_type,
        "status": "TOOL_NOT_FOUND",
        "reason": f"None of the candidate tools were installed: {[c for c in candidates]}",
        "attempts": attempts,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
