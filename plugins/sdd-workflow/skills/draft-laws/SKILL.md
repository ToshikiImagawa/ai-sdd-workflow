---
name: draft-laws
description: "Draft Bend laws (LAWS.bend) and differential pytest cases from a spec for human approval, then write the reference model and proofs once approved; classify existing laws for migration. Never writes approval lines."
argument-hint: "<draft|model|migrate> <feature-name> [--ticket <number>] [--overwrite]"
arguments: [subcommand, feature-name]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit(.sdd/laws/**), Edit(.sdd/task/*/laws-draft-report.md), Edit(.sdd/task/*/laws-migration-report.md), Edit(tests/laws/**), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/draft-laws/scripts/draft_laws.py" *)
---

# Draft Laws - Spec to Bend Law Drafts

Turns the machine-checkable properties of a spec into Bend laws (universal properties, `for x: T`) and differential pytest cases (point assertions: one decision-table row each, asserted against the implementation), and after a human approves the laws writes the reference model and proofs. Detailed contract: `laws-drafting_spec.md`. This skill never calls `bend`; checking is `/run-checklist --category proof` for the laws and the project's `pytest` for the tests.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read only these sections of the AI-SDD principles document (not the whole file): § Role of Each Document and Abstraction Level, § Document Persistence Rules
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

Templates are under `templates/${SDD_LANG:-en}/`. Write the whole output (report, comments) in that one language.

## Input

- `subcommand`: $subcommand (`draft`, `model` or `migrate`)
- `feature-name`: $feature-name (`parent/child` for hierarchical specs)

Full argument string: $ARGUMENTS

## Hard rules

- **Never write** a `# approved:` line, `laws-status: approved|proven`, or any change to the spec (`laws:` / `laws-status: drafted` are only *proposed* in the report).
- Never modify a `LAWS.bend` that has an approval line (even with `--overwrite`). Never modify `LAWS.bend` in the `model` stage.
- Write only under `${SDD_LAWS_PATH}/{feature}/`, the differential test file `status.tests_target` (default `tests/laws/`; a project may change it with `.sdd-config.json` `laws.tests_dir`, which then needs approval) and the reports. Do not edit the PRD or spec. `migrate` writes only its report.
- Only the script decides hashes, ordering, cut-off, the point-assertion split, the implementation location and checks. Do not compute them yourself. Never pick a `# model-of:` path yourself: copy `status.impl.paths`.
- A spec whose implementation is prose (`status.impl.lawifiable` false, `reason: prose_implementation`: every `impl-of:` path is a `.md`) gets no laws and no tests: report the reason and stop.

## Script

All deterministic work goes through one script (JSON on stdout):

| Subcommand | Command (prefix: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/draft-laws/scripts/draft_laws.py"`) |
|:--|:--|
| state (incl. `impl`, `tests_target`) | `status <feature> [--overwrite]` |
| fixed model API | `model-api <feature>` |
| section hash | `hash <spec-path> <section>` |
| order, cut off, point-assertion split | `rank --max <n> <candidates.json>` |
| static check | `check <laws-file> --spec <spec-path> [--feature <feature> [--project-root <dir>]] [--require-model]` |
| test-source check | `check --tests <pytest-file> --spec <spec-path>` (combine with a laws file to check both) |
| migration table (read-only) | `migrate <feature>` |
| acceptance (maintainers) | `compare <generated> <reference> [--model <main.bend>] [--judgement <json>] [--check-result <check-output.json>]` |

## `draft <feature>`

1. `status <feature>`. If `ok` is false (spec missing, or no front matter `id`), stop with that error. Show `warnings` (including an invalid `laws.max_laws`, which falls back to 10). The script decides the target: write only `write_target` (`LAWS.bend` or `LAWS.draft.bend`). Pass `--overwrite` to `status` only when the user gave it; with an approval line the script refuses it (`overwrite_refused`: report it) and the proposal goes to `LAWS.draft.bend`. Without `--overwrite`, an unapproved existing `LAWS.bend` is kept and the new proposal goes to `LAWS.draft.bend`. Show a diff against the kept file.
   Then read `impl`: if `lawifiable` is false, write nothing (no laws, no tests), report the reason (`prose_implementation`) and the declared `impl-of:` paths under "Sections not turned into laws", and finish successfully. If `warnings` contains `impl_undeclared`, continue, but put an `impl-of: <path>` proposal for the spec in the report's next steps (a human adds it).
2. `model-api <feature>` and use the returned API as is: `source` is `spec` (a `model-api:` line in the spec; `main.bend` is then ignored, not merged), `main.bend` (existing model), `main.bend-unreadable` (main.bend exists but no `def` could be read: report the `warning`, treat the API as unfixed) or `unfixed`. Laws may reference only the returned `Model.*` functions; never add a function of your own (no extra helper or empty-input function) when `fixed` is true. When `unfixed`, propose the API yourself and write "unfixed - needs confirmation" in the report's model-API section.
3. Read the spec and extract candidates by priority (1 = decision tables / state transitions, 2 = aggregation rules, 3 = constraints and invariants, 4 = numeric targets of NFRs/constraints). Rules:
   - Only from structured sections. Never derive a law from FR-table prose alone.
   - Never from IO, network, filesystem, clock, performance measurements, output formatting.
   - A section without a leading number cannot be a source: list it under "Sections not turned into laws".
   - Write each law as an equation over the model API (`{lhs == rhs : T}`); copy the fixed signatures into `# model-api:` lines (when `unfixed`: decide the functions, argument types and numeric encodings and document them; a human approves them).
   - Write `for` with one variable per line, as in the first-round laws (`for a: Nat` on one line, `for b: Nat` on the next, then the `{...}` line). Never `for a b: T` or `for a, b: T`: Bend rejects them and `check` reports `multi_var_for` (error).
   - When `unfixed`, write the types in `# model-api:` in Bend's notation (a list is `List<&2, T>`, not `List(T)`), so the later `model` stage matches (`model_api_signature_mismatch`).
   - When the fixed API has constant rank functions (`Model.rank_*()`), write ranks with them, not with number literals; use literals only when the API has none. Never mix both in one law.
   - When the fixed API has an aggregate function (e.g. `Model.aggregate`) over a binary operation (e.g. `Model.worse`), write commutativity, identity, empty-input and single-element laws on the aggregate first (`aggregate([a, b]) == aggregate([b, a])`, not `worse(a, b) == worse(b, a)`). Add the binary-operation versions only when the cap has room, and flag them `level: "binary"` in step 4.
   - Do not write an equation that holds only for some values of a `for x: Nat` variable (absorption or fixed-value laws such as `worse(4n, a) == 4n`, false for `a > 4`). Do not adopt it: flag the candidate `unbounded: true` in step 4 so `rank` lists it under "Rejected candidates" with reason `unbounded_nat`; `check` warns with `unbounded_nat_literal` on the rest and a human reviews that before approving.
   - Still extract fixed-input propositions (one decision-table row, e.g. `{Model.severity(3n) == 0n : Nat}`): they are not dropped, `rank` routes them to the differential tests (step 6b). Do not try to turn them into `for` laws artificially.
4. For each candidate get the section hash with `hash`. Put candidates in a JSON array `{name, section, priority, kind, level, body, trivial, unbounded}` and run `rank --max <max_laws>`. Adopt exactly `adopted`; everything in `not_adopted` goes to "Rejected candidates" with its `reason`; everything in `to_tests` (reason `point_assertion`: no `for` in the body and `kind` not `empty` / `singleton` / `identity`) becomes a pytest case in step 6b and is listed under "Candidates routed to differential tests". Fields:
   - `kind`: `commutative` / `associative` / `identity` / `empty` / `singleton` for the basic properties of an aggregation or merge rule, else omit; `rank` takes those first inside one priority before the cut-off, and keeps `empty` / `singleton` / `identity` in Bend even without a `for`. Forgetting `kind: empty` sends an empty-input law to the tests, so set it.
   - `level`: `binary` for a property written on a binary operation when the fixed API has an aggregate function, else omit; `rank` puts those last inside one priority (it does not read the API, so setting `level` is your job).
   - `body`: the law text.
   - `trivial`: true for tautologies, restatements of a model definition, or type-only properties.
   - `unbounded`: true for equations that hold only for part of a `for x: Nat` range.
5. If nothing is adopted and nothing can be a law: write no `LAWS.bend` / `LAWS.draft.bend`, report "Sections not turned into laws" per section and finish successfully (not a failure; existing files untouched). Step 6b still runs when `to_tests` is non-empty.
6. Write the law file from `templates/${SDD_LANG}/laws_draft.md` with `adopted` only. Every `law` is preceded by `# source: <spec id> §<section> sha256:<hash>` placed **after** the imports (inside the hashed body). No approval line.
6b. Write the differential tests from `templates/${SDD_LANG}/laws_tests.md` to `status.tests_target` when `to_tests` is non-empty. One `def test_<candidate name>` per candidate, preceded by its `# source:` line (same format as the laws; decorators may sit between). The module header carries `# spec:` and `# impl-of:` (copy `status.impl.paths`). Each test calls the implementation in `impl.paths` directly (import it the way the project's existing tests do; in this repository `importlib.util.spec_from_file_location`) and asserts the implementation's real return value: no Bend numeric encoding. If `status.tests_target` already exists, do not overwrite it: show the diff in the report and let a human merge.
7. `check <file> --spec <spec> --feature <feature> [--tests <tests_target>]`. If the result has `notes` (model API not fixed, so check 6 did not run), put them in the report. Put the findings in the report. If `propose_drafted` is false, do not propose `drafted`; fix generation errors first when possible (a `test_source_missing` means a test lacks its `# source:` line).
8. Report from `templates/${SDD_LANG}/laws_draft_report.md`: with `--ticket <n>` write `${SDD_TASK_PATH}/<n>/laws-draft-report.md`, else print it. Include the current content hash and the approval-line format for the human. Mention that until the spec lists `laws:`, the gate reports orphan laws (FAIL, row #4) before the unapproved SKIPPED (row #5). Tell the human to run the project's `pytest` on the new test file.

## `model <feature>`

1. `status <feature>`. If `model_allowed` is false, **refuse** with `model_refusal` together with `approval_format` (the approval-line format with the `current_hash`; a human writes the line). Create nothing. (The spec's `laws-status` and `laws:` only produce warnings.)
2. Read `LAWS.bend`'s `# model-api:` lines and `Model.*` references only. Write `main.bend` (with `# spec:` and one `# model-of:` line per path in `status.impl.paths`; never choose the path yourself. When `impl.source` is `none`, leave `# model-of:` out and tell the human to add `impl-of:` to the spec) and `PROOF.bend` from `templates/${SDD_LANG}/main_model.md` and `proof_model.md` (the file bodies are the Bend text; the `.md` extension only satisfies the support-file rule). `PROOF.bend` may only use `import Base`, `import ./main.bend as Model` and `import ./LAWS.bend as Laws`.
3. Existing `main.bend` / `PROOF.bend` are not overwritten: show the diff instead.
4. If a law looks wrong, report it; do not edit `LAWS.bend` (a human revises it and re-approves).
5. `check LAWS.bend --spec <spec> --require-model`, then point to `/run-checklist <feature> <ticket> --category proof`. A missing `bend` is reported there as TOOL_NOT_FOUND.

## `migrate <feature>`

Read-only classification of an existing `LAWS.bend` for the human-run migration to the current rules (point assertions to pytest, prose implementations out). It never edits `LAWS.bend`, the spec or any approval line.

1. `migrate <feature>`. If `ok` is false, stop with the error.
2. Write the table from `templates/${SDD_LANG}/laws_migration_report.md`: with `--ticket <n>` to `${SDD_TASK_PATH}/<n>/laws-migration-report.md`, else print it. Copy `impl`, every row of `laws` (`classification`, `section`, `kind_guess`, `suggested_test`) and `human_review_note`. Describe the human steps per class: `keep` (nothing), `to_tests` (write the differential test with `draft`, run pytest, then a human deletes the law and re-approves: the body changes, so the approval line is rewritten), `prose_delete` (a human removes the laws directory and the spec's `laws:` / `laws-status`).
3. When `impl.source` is `main.bend` or `none`, add an `impl-of:` proposal for the spec to the report (copy the `# model-of:` paths, or say it is undeclared). Flag a `# model-of:` that points at something other than the real implementation if you notice one; do not fix it yourself.
