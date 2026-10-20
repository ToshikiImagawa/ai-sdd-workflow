---
name: draft-laws
description: "Draft Bend laws (LAWS.bend) from a spec for human approval, then write the reference model and proofs once approved. Never writes approval lines."
argument-hint: "<draft|model> <feature-name> [--ticket <number>] [--overwrite]"
arguments: [subcommand, feature-name]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit(.sdd/laws/**), Edit(.sdd/task/*/laws-draft-report.md), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/draft-laws/scripts/draft_laws.py" *)
---

# Draft Laws - Spec to Bend Law Drafts

Turns the machine-checkable properties of a spec into Bend laws, and after a human approves them writes the reference model and proofs. Detailed contract: `laws-drafting_spec.md`. This skill never calls `bend`; checking is `/run-checklist --category proof`.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

Templates are under `templates/${SDD_LANG:-en}/`. Write the whole output (report, comments) in that one language.

## Input

- `subcommand`: $subcommand (`draft` or `model`)
- `feature-name`: $feature-name (`parent/child` for hierarchical specs)

Full argument string: $ARGUMENTS

## Hard rules

- **Never write** a `# approved:` line, `laws-status: approved|proven`, or any change to the spec (`laws:` / `laws-status: drafted` are only *proposed* in the report).
- Never modify a `LAWS.bend` that has an approval line (even with `--overwrite`). Never modify `LAWS.bend` in the `model` stage.
- Write only under `${SDD_LAWS_PATH}/{feature}/` and the report. Do not edit the PRD or spec.
- Only the script decides hashes, ordering, cut-off and checks. Do not compute them yourself.

## Script

All deterministic work goes through one script (JSON on stdout):

| Subcommand | Command (prefix: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/draft-laws/scripts/draft_laws.py"`) |
|:--|:--|
| state | `status <feature> [--overwrite]` |
| fixed model API | `model-api <feature>` |
| section hash | `hash <spec-path> <section>` |
| order and cut off | `rank --max <n> <candidates.json>` |
| static check | `check <laws-file> --spec <spec-path> [--feature <feature> [--project-root <dir>]] [--require-model]` |
| acceptance (maintainers) | `compare <generated> <reference> [--model <main.bend>] [--judgement <json>] [--check-result <check-output.json>]` |

## `draft <feature>`

1. `status <feature>`. If `ok` is false (spec missing, or no front matter `id`), stop with that error. Show `warnings` (including an invalid `laws.max_laws`, which falls back to 10). The script decides the target: write only `write_target` (`LAWS.bend` or `LAWS.draft.bend`). Pass `--overwrite` to `status` only when the user gave it; with an approval line the script refuses it (`overwrite_refused`: report it) and the proposal goes to `LAWS.draft.bend`. Without `--overwrite`, an unapproved existing `LAWS.bend` is kept and the new proposal goes to `LAWS.draft.bend`. Show a diff against the kept file.
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
4. For each candidate get the section hash with `hash`. Put candidates in a JSON array `{name, section, priority, kind, level, body, trivial, unbounded}` and run `rank --max <max_laws>`. Adopt exactly `adopted`; everything in `not_adopted` goes to "Rejected candidates" with its `reason`. Fields:
   - `kind`: `commutative` / `associative` / `identity` / `empty` / `singleton` for the basic properties of an aggregation or merge rule, else omit; `rank` takes those first inside one priority before the cut-off.
   - `level`: `binary` for a property written on a binary operation when the fixed API has an aggregate function, else omit; `rank` puts those last inside one priority (it does not read the API, so setting `level` is your job).
   - `body`: the law text.
   - `trivial`: true for tautologies, restatements of a model definition, or type-only properties.
   - `unbounded`: true for equations that hold only for part of a `for x: Nat` range.
5. If nothing is adopted and nothing can be a law: write no `LAWS.bend` / `LAWS.draft.bend`, report "Sections not turned into laws" per section and finish successfully (not a failure; existing files untouched).
6. Write the law file from `templates/${SDD_LANG}/laws_draft.md`. Every `law` is preceded by `# source: <spec id> §<section> sha256:<hash>` placed **after** the imports (inside the hashed body). No approval line.
7. `check <file> --spec <spec> --feature <feature>`. If the result has `notes` (model API not fixed, so check 6 did not run), put them in the report. Put the findings in the report. If `propose_drafted` is false, do not propose `drafted`; fix generation errors first when possible.
8. Report from `templates/${SDD_LANG}/laws_draft_report.md`: with `--ticket <n>` write `${SDD_TASK_PATH}/<n>/laws-draft-report.md`, else print it. Include the current content hash and the approval-line format for the human. Mention that until the spec lists `laws:`, the gate reports orphan laws (FAIL, row #4) before the unapproved SKIPPED (row #5).

## `model <feature>`

1. `status <feature>`. If `model_allowed` is false, **refuse** with `model_refusal` together with `approval_format` (the approval-line format with the `current_hash`; a human writes the line). Create nothing. (The spec's `laws-status` and `laws:` only produce warnings.)
2. Read `LAWS.bend`'s `# model-api:` lines and `Model.*` references only. Write `main.bend` (with `# spec:` and `# model-of: <implementation file>`) and `PROOF.bend` from `templates/${SDD_LANG}/main_model.md` and `proof_model.md` (the file bodies are the Bend text; the `.md` extension only satisfies the support-file rule). `PROOF.bend` may only use `import Base`, `import ./main.bend as Model` and `import ./LAWS.bend as Laws`.
3. Existing `main.bend` / `PROOF.bend` are not overwritten: show the diff instead.
4. If a law looks wrong, report it; do not edit `LAWS.bend` (a human revises it and re-approves).
5. `check LAWS.bend --spec <spec> --require-model`, then point to `/run-checklist <feature> <ticket> --category proof`. A missing `bend` is reported there as TOOL_NOT_FOUND.
