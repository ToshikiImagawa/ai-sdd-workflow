# Verification Commands Reference

## Running Verifications

The skill's `allowed-tools` pre-approves exactly one scoped command — `scripts/run-verification.py` — instead of
bare `Bash`, so every verification goes through that script. Run it from the project root, once per category:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" test
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" lint
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" typecheck
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" security
```

The opt-in `proof` category takes options (see "Law Proof (CHK-205)" below).

The script owns detection and execution; it implements the "Detection Priority" order below and the
test / lint / type-check / security rows of the tables that follow. It prints a JSON result
(`PASS` / `FAIL` / `SKIPPED` / `TOOL_NOT_FOUND` / `TIMEOUT`) on stdout — see SKILL.md for how each status maps
to a checklist outcome.

**Categories the script does not cover**: the formatter row (CHK-4xx), Design Review (CHK-3xx), and
Documentation Review (CHK-6xx) commands listed below are *not* implemented by the script, and bare `Bash` is
deliberately not granted — so those items cannot be verified automatically by this skill. Record them as manual
review items rather than reporting them as failures.

## Project Type Detection

| Project Type | Detection File         | Package Manager |
|:-------------|:-----------------------|:----------------|
| Node.js      | `package.json`         | npm / yarn / pnpm |
| Python       | `pyproject.toml`, `setup.py`, `requirements.txt` | pip / poetry / uv |
| Rust         | `Cargo.toml`           | cargo           |
| Go           | `go.mod`               | go              |
| Ruby         | `Gemfile`              | bundler         |

## Verification Commands by Category

### Testing (CHK-5xx)

| Project Type | Test Command                      | Coverage Command                    |
|:-------------|:----------------------------------|:------------------------------------|
| Node.js      | `npm test` or `yarn test`         | `npm test -- --coverage`            |
| Python       | `pytest`                          | `pytest --cov`                      |
| Rust         | `cargo test`                      | `cargo tarpaulin`                   |
| Go           | `go test ./...`                   | `go test -cover ./...`              |

### Implementation Review (CHK-4xx)

| Tool Type    | Node.js                 | Python                  | Rust           | Go              |
|:-------------|:------------------------|:------------------------|:---------------|:----------------|
| Linter       | `eslint .`              | `ruff check .`          | `cargo clippy` | `golangci-lint` |
| Formatter    | `prettier --check .`    | `ruff format --check .` | `cargo fmt --check` | `gofmt -l .` |
| Type Check   | `tsc --noEmit`          | `mypy .`                | (built-in)     | (built-in)      |

### Security Review (CHK-7xx)

| Project Type | Audit Command           | Additional Scanners     |
|:-------------|:------------------------|:------------------------|
| Node.js      | `npm audit`             | `npx snyk test`         |
| Python       | `pip-audit`             | `safety check`          |
| Rust         | `cargo audit`           | -                       |
| Go           | `govulncheck ./...`     | -                       |

### Specification Review (CHK-2xx)

| Check Type           | Command / Method                    |
|:---------------------|:------------------------------------|
| Spec Consistency     | `/check-spec {feature}`             |
| Type Definition      | Run type checker (tsc, mypy, etc.)  |
| API Signature        | Compare exports with spec document  |

### Law Proof (CHK-205, opt-in)

Only for specs whose front matter has `laws:`. Pass every directory in one call (each element prefixed with `${SDD_ROOT}/`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" proof \
  --laws-dir .sdd/laws/auth/user-login --laws-dir .sdd/laws/auth/signup [--verdict] [--timeout 300]
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checklist/scripts/run-verification.py" proof \
  --print-laws-hash --laws-dir .sdd/laws/auth/user-login   # for a human writing the approval line
```

Without `--laws-dir` the script scans `${SDD_LAWS_PATH}`. Defaults come from `.sdd-config.json` (`proof.timeout_seconds`, `proof.verdict`); CLI options win.

| Decision (first match wins)                                           | Status           |
|:----------------------------------------------------------------------|:-----------------|
| `bend` not on PATH                                                    | `TOOL_NOT_FOUND` |
| Specified directory missing                                           | `FAIL`           |
| No `LAWS.bend`                                                        | `SKIPPED`        |
| Orphan laws (no `# spec:`, unresolved id, or not in the spec's `laws:`) | `FAIL`           |
| No valid `# approved:` line (missing, malformed, hash mismatch)       | `SKIPPED`        |
| No `law` declaration                                                  | `SKIPPED`        |
| No `PROOF.bend`; `PROOF.bend` does not import `LAWS`; disallowed import | `FAIL`         |
| Time limit exceeded                                                   | `TIMEOUT`        |
| Exit 0 and `ALL PROOFS CHECK`                                         | `PASS`           |
| `--verdict` and Lean kernel unavailable                               | re-run without it, `verdict: "unavailable"` |
| Anything else                                                         | `FAIL`           |

Approved directories may also carry a `warnings` array (`source_drift` / `source_invalid`, FR-013) when a `# source:` section hash no longer matches the spec. It is additive: status and aggregation are unchanged, and it is omitted when `bend` is absent.

Multiple directories aggregate as FAIL > TIMEOUT > TOOL_NOT_FOUND > SKIPPED > PASS. `BEND_NO_TELEMETRY=1` is always set.
**PASS means the reference model satisfies the approved laws; it does not prove the implementation.**

### Design Review (CHK-3xx)

| Check Type           | Node.js                | Python               |
|:---------------------|:-----------------------|:---------------------|
| Circular Deps        | `madge --circular`     | `pydeps --no-show`   |
| Unused Deps          | `depcheck`             | `pip-check`          |
| Architecture         | Manual review          | Manual review        |

### Documentation Review (CHK-6xx)

| Check Type           | Node.js                | Python               |
|:---------------------|:-----------------------|:---------------------|
| JSDoc Coverage       | `jsdoc-coverage`       | -                    |
| Docstring Coverage   | -                      | `interrogate`        |
| README Exists        | Check file exists      | Check file exists    |

## Detection Priority

When multiple detection files exist, use this priority:

1. `package.json` → Node.js project
2. `pyproject.toml` → Python project (modern)
3. `Cargo.toml` → Rust project
4. `go.mod` → Go project
5. `setup.py` or `requirements.txt` → Python project (legacy)
6. `Gemfile` → Ruby project

## Command Execution Guidelines

1. **Check tool availability** before running (e.g., `which eslint`)
2. **Use project-local tools** when available (e.g., `npx eslint` instead of global `eslint`)
3. **Capture both stdout and stderr** for result recording
4. **Set reasonable timeouts** (default: 5 minutes per command)
5. **Continue on failure** - record failure and proceed to next verification
