---
name: check-spec
description: "Check consistency between implementation code and abstract specifications (spec), detecting discrepancies"
argument-hint: "[feature-name] [--ticket <number>] [--full]"
arguments: [feature-name]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-spec-docs.py" *)
disallowed-tools: Write, Edit
---

# Check Spec - Specification & Implementation Consistency Check

Verifies consistency between implementation code and the abstract specifications under
`${SDD_SPECIFICATION_PATH}/`, detecting discrepancies.

**Role**: This command specializes in **spec <-> implementation consistency checking**.
The spec is the persistent source of truth, so it is the **first-class comparison baseline**.
**Document-level consistency** (PRD <-> spec, spec <-> adr) is handled by the `spec-reviewer`
agent when called with the `--full` option.

**Design drafts are optional**: the technical design document lives at
`${SDD_TASK_PATH}/{ticket-number}/design-draft.md` and is deleted once implementation completes.
When a draft exists it is used as an **auxiliary input** for details the spec cannot express
(module structure, technology stack). Its absence is the normal state and is never reported as a
problem.

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may
still contain these. They **remain valid** — read them as **supplementary input, and treat their absence as
normal**. Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and
never report an existing one as a naming violation or propose deleting it; it may stay until its decisions
have been migrated to `adr/{feature}.md`.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Document Dependencies

See `references/document_dependencies.md` for the document dependency chain and direction meaning.

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

- `feature-name`: $feature-name

Full argument string: $ARGUMENTS

> **Fallback**: If the value above is empty, remains a literal `$` placeholder, or starts with `--`
> (a flag captured positionally), treat the argument as omitted and interpret the full argument
> string instead (e.g., `/check-spec --full` means all specs with the `--full` option).

| Argument       | Required | Description                                                                                                |
|:---------------|:---------|:-----------------------------------------------------------------------------------------------------------|
| `feature-name` | -        | Target feature name or path (e.g., `user-auth`, `auth/user-login`). If omitted, all specs are targeted     |

### Options

- `--ticket <number>`: Ticket whose design draft (`${SDD_TASK_PATH}/{ticket-number}/design-draft.md`) is used as
  the auxiliary design input. Both `--ticket <number>` and `--ticket=<number>` are accepted. Omit it when no
  ticket is in flight — see "Auxiliary design input" below for how a draft is otherwise selected
- `--full`: In addition to consistency checking, also runs quality review by the `spec-reviewer` agent
    - CONSTITUTION.md compliance check
    - Completeness, clarity, and SysML compliance check
    - Vague description detection

### Input Examples

- `/check-spec user-auth` — Consistency check only (default)
- `/check-spec user-auth --ticket 123` — Consistency check with ticket 123's design draft as auxiliary input
- `/check-spec task-management --full` — Consistency check + quality review
- `/check-spec --full` — Comprehensive check for all specifications
- `/check-spec` — Without arguments, targets all specifications (consistency check only)

### Scope Confirmation for No-Argument Execution

**When executed without arguments, display the list of target files and ask for user confirmation before starting the process.**

**Reference**: `examples/scope_confirmation.md`

Replace placeholders with actual file names and counts.

**Post-confirmation behavior**:

- User approves -> Execute check on all files
- User cancels or specifies a particular file -> Re-execute with the specified scope

## Processing Flow

**Optimized Execution Flow**:

**Phase 1: Shell Script** - Execute `python3 "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-spec-docs.py" [feature-name] [--ticket <number>]` to scan specification documents.

This script:
1. Finds all spec documents under `${SDD_SPECIFICATION_PATH}/` in flat or hierarchical structure,
   with or without the `_spec` suffix (`{feature}.md` / `{feature}_spec.md`)
2. Selects the design drafts (`${SDD_TASK_PATH}/{ticket-number}/design-draft.md`) that belong to this run
   as an optional auxiliary input; an empty list is normal, not an error. Drafts of other tickets are
   **not** attached (see "Auxiliary design input" below)
3. Resolves each target spec's decision log under `${SDD_ADR_PATH}/` — the suffix-free `{feature}.md` and the
   legacy `{feature}-decisions.md`, at the same relative position as the spec (so
   `specification/auth/user-login.md` maps to `adr/auth/user-login.md`); when neither name exists, an adr whose
   front matter `depends-on` references the spec's ID. An empty result is normal, not an error
4. Generates file mapping JSON: per spec, its feature name, auxiliary design doc, `adr` documents and the
   attribution basis `adr_basis` (`name` / `depends-on` / `none`); plus the selected draft list, the
   selection basis `design_draft_scope`, any `unscoped_design_drafts`, and the flat `adr_documents` list
5. Exports environment variables to `$CLAUDE_ENV_FILE`:
   - `CHECK_SPEC_SPEC_FILES` - List of spec files (the comparison baseline)
   - `CHECK_SPEC_DESIGN_DRAFT_FILES` - List of selected design drafts (empty when none apply)
   - `CHECK_SPEC_DESIGN_DRAFT_SCOPE` - How the drafts were selected: `none` / `ticket` / `depends-on` /
     `sole-draft` / `unscoped`
   - `CHECK_SPEC_ADR_FILES` - List of the decision logs attributed to the target specs (empty when the
     features' decisions are not recorded yet). Input for the `--full` spec ↔ adr review
   - `CHECK_SPEC_MAPPING` - JSON mapping file

**Phase 2: Claude** - Read specs from pre-scanned lists and perform consistency check

### 1. Identify Target Documents

Target the spec documents under `${SDD_SPECIFICATION_PATH}/`. Both flat and hierarchical
structures are supported, and the `_spec` suffix is optional in every case.

**For flat structure**:

- With argument -> Target `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{argument}_spec.md` and
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{argument}.md` (whichever exist)
- Without argument -> Target all spec `.md` files under
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/` (recursively)

**For hierarchical structure** (when argument contains `/`, or when specifying hierarchical path):

- Argument in `"{parent-feature}/{feature-name}"` format -> Target
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md` or
  the suffix-free `.../{feature-name}.md`
- Argument is `"{parent-feature}"` only -> Target every spec `.md` file under
  `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/` (the parent's
  `index[_spec].md` and its child features)

**Naming convention**:

- **Under specification**: `_spec` suffix optional (`index.md`, `index_spec.md`,
  `{feature-name}.md`, or `{feature-name}_spec.md`)
- **Not a spec**: `{feature-name}_design.md` under specification is a v4.x persistent design doc.
  It is excluded from the spec list and read as supplementary input (see the mapping JSON). It is
  never a naming violation and is never proposed for deletion

**Auxiliary design input** (use only if present):

- `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/design-draft.md` — the in-progress
  technical design draft. The filename is fixed and ticket-scoped, so it cannot be matched to a
  spec by name. Use **only the drafts listed in `CHECK_SPEC_DESIGN_DRAFT_FILES`**; never glob
  `${SDD_TASK_PATH}/` yourself, because another ticket's design would be mixed into the check
- The `design` field of each mapping entry — a v4.x persistent `{feature}_design.md`, when present

**Decision logs (`--full` only)**:

The `adr` field of each mapping entry, and the flat list in `CHECK_SPEC_ADR_FILES`, hold the decision logs
resolved for the target specs. They are **not** used by the spec ↔ implementation check; they are passed to the
`spec-reviewer` agent for the spec ↔ adr document review under `--full` (see step 6). An empty list is the
normal state for a feature whose decisions are not recorded yet, and is never reported as a discrepancy.

**How a draft is selected** (`design_draft_scope` in the mapping JSON):

| Scope         | Meaning                                                                                   | Action |
|:--------------|:------------------------------------------------------------------------------------------|:-------|
| `none`        | No draft exists — the normal state after implementation completes                          | Skip every design ↔ implementation check; report nothing |
| `ticket`      | `--ticket <number>` was given; only that ticket's draft is used                             | Use it as auxiliary input |
| `depends-on`  | The draft's front matter `depends-on` references a target spec's ID (`spec-*`)              | Use it as auxiliary input |
| `sole-draft`  | Exactly one draft exists project-wide, and its `depends-on` (if declared) does not exclude the target spec(s) | Use it as auxiliary input |
| `unscoped`    | Several drafts exist and none could be tied to this run; **none** were selected             | Treat the run as having no draft, and report the notice below |

For the `unscoped` case, report an Info-level notice listing `unscoped_design_drafts` and stating that the
design ↔ implementation checks were skipped; recommend re-running with `--ticket <number>` (or
`--ticket=<number>`) for the ticket under work. Do not read those drafts.

**Hierarchical structure input examples**:

- `/check-spec auth/user-login` — Check user-login feature under auth domain
- `/check-spec auth` — Check entire auth domain

### 2. Load Specifications

The spec is an **abstract specification**: it states "what to build", not the technical detail of
"how". Only extract what the spec can actually express, and do not expect design-level detail
from it.

**Extract the following information from the spec**:

| Item                        | Typical spec section          | Description                                                                    |
|:----------------------------|:------------------------------|:-------------------------------------------------------------------------------|
| **Public API**              | Provided components, I/O definitions | Public interface names, arguments, return values, CLI arguments/options, environment variables |
| **Data Model**              | I/O definitions, glossary      | Entities, fields and their types, output file/JSON structures                  |
| **Behavior**                | Functional requirements, behavior diagrams | Observable behavior per requirement ID (FR-xxx / NFR-xxx), branch conditions   |
| **Functional Requirements** | Functional requirements table  | List of features to implement, with requirement IDs                            |
| **Constraints**             | Constraints                    | Explicitly excluded behavior, prerequisites                                    |
| **Literal Values**          | Schema Registry, body text     | Thresholds, enum values, CHECK constraint values, durations, and other constants |

**Additional items — only when a design draft (or a v4.x persisted design doc) exists**:

| Item                        | Description                                                        |
|:----------------------------|:-------------------------------------------------------------------|
| **Module Structure**        | Directory structure, file organization                             |
| **Technology Stack**        | Libraries, frameworks used                                         |
| **Implementation Approach** | Architecture patterns, design decisions                            |

If no draft exists, **omit these items from the comparison entirely** — do not report them as
missing or as a discrepancy.

**Literal value extraction sources** (in priority order):

1. **Schema Registry section** in the spec (a "Value Range / Threshold Registry" table), if present.
   Parse each entry as `{value-id, value, unit, source-requirement-id, section}`.
2. If no registry section exists, extract literal values mentioned in the body text of the spec
   (e.g., "confidence threshold 70%", `default 0.7`, `CHECK (risk_level IN ('low', 'high'))`, "p95 <= 15s").
3. A design draft, when present, may refine a value; the spec still holds the authoritative value.

### 3. Verify Implementation Code

Search for code corresponding to specification contents:

- Search APIs/functions (using methods appropriate for project language)
- Search type definitions/data models
- Verify module/file existence
- Extract literal values from implementation:
    - Configuration files (`config.py`, `settings.py`, `*.toml`, `*.yaml`, `*.json`, `.env.example`)
    - ORM CHECK constraints and DB migration files (e.g., `CheckConstraint`, `CHECK (... IN (...))`)
    - Validation constraints (e.g., Pydantic `Field(ge=..., le=...)`, zod, Bean Validation)
    - Language-specific enums and constants (`Enum`, `const`, `Literal[...]`, union types)

### 4. Consistency Check Items

**Note**: This command specializes in **spec <-> implementation consistency checking**. **Document-level consistency**
(PRD <-> spec, spec <-> adr) and **quality review** (CONSTITUTION.md compliance, completeness, clarity) are handled by
the `spec-reviewer` agent when using the `--full` option.

#### Front Matter Consistency

If documents contain YAML front matter, call the `front-matter-reviewer` agent to validate.
Pass all target document paths (the specs, plus any auxiliary design doc).

**If agent delegation is unavailable in the current execution environment**, do not silently skip this
check or report it as completed. State explicitly in the output that front matter validation was not
performed and why, and list it as a manual review item for a human to run separately.

After results are returned, integrate `impl-status` findings into the spec ↔ implementation consistency results.
Record the spec's `impl-status` value (or its absence) for use in the branching below.

#### Unimplemented-Function Classification by `impl-status`

A spec-documented function with no corresponding implementation is not automatically a defect: whether it is
expected or a regression depends on the spec's `impl-status` front matter field.

| Spec `impl-status`                | Meaning                                     | Classification |
|:------------------------------------|:----------------------------------------------|:-----------------|
| `implemented`                      | Spec declares the implementation is done      | **Critical** — regression: the implementation was removed, or never matched the declared status |
| `not-implemented` / `in-progress`  | Spec intentionally precedes the implementation | **Info** — expected: implementation has not caught up with the spec yet |
| Missing / absent                   | No implementation-state signal available       | **Warning** — undecidable; downgraded from Critical, so it must be counted in the downgrade summary below |

**Filling in a missing `impl-status`**: `/recommend-front-matter` only **lists** the specs that lack the field —
it never writes a value, because it cannot know the real implementation state. So recommend this sequence
instead of an automatic fix: run `/recommend-front-matter` to get the list of specs missing `impl-status`, check
for each listed spec whether its behavior is actually implemented (the findings of this run already tell you for
the specs checked here), then set `impl-status` yourself to the value that matches reality
(`implemented` / `in-progress` / `not-implemented`). Never describe the field as something a command fills in
automatically.

#### Downgrade Summary (required)

Every "specified in the spec but missing from the implementation" finding that landed in Warning or Info because
of `impl-status` was a Critical in AI-SDD v4.x, where the classification was unconditional. A v4-era document set
carries **no** `impl-status` at all, so **every** such finding is downgraded and a silent downgrade reads as
"Critical count dropped to 0 — things improved."

Always emit the counts, even when they are zero:

- `Downgraded to Warning (impl-status absent): N` — and list the specs whose front matter lacks the field
- `Downgraded to Info (impl-status not-implemented / in-progress): N`

State explicitly that these N findings are **not** resolved defects: they are undecidable or deferred, and the
Critical count in the summary excludes them.

This branching applies **only** to "function specified in the spec but missing from the implementation."
Public API mismatches, data model mismatches, and behavior contradicting the spec remain unconditionally
Critical regardless of `impl-status` — `impl-status` never excuses an implementation that diverges from what
it claims to implement, only one that simply hasn't started yet.

#### spec <-> Implementation Consistency

| Check Target                | Verification Content                                            | Importance |
|:----------------------------|:----------------------------------------------------------------|:-----------|
| **Public API**              | Do public names, arguments, return values, CLI options, and environment variables match? | High |
| **Data Model**              | Do entities, fields, types, and output structures match?        | High       |
| **Behavior**                | Does observable behavior match the spec per requirement ID?     | High       |
| **Functional Requirements** | Is each FR-xxx individually matched against the implementation? A closing sentence like "all FRs are implemented" does not satisfy this — show the matching implementation (or its absence) per FR-xxx | High       |
| **Non-Functional Requirements** | Is each NFR-xxx individually matched against the implementation, the same way each FR-xxx is? A closing sentence like "all NFRs are correctly reflected" does not satisfy this — show the matching implementation (or its absence) per NFR-xxx | High       |
| **Literal Values**          | Do thresholds, enum values, and constraint values match between spec and implementation? | High |
| **Constraints**             | Does the implementation stay within the spec's stated constraints? | Medium  |

#### design <-> Implementation Consistency (only when a design draft exists)

Skip this table entirely when no design draft (or v4.x persisted design doc) is available.

| Check Target                | Verification Content                               | Importance |
|:----------------------------|:---------------------------------------------------|:-----------|
| **Module Structure**        | Does directory/file structure match?               | Medium     |
| **Technology Stack**        | Are documented libraries being used?               | Low        |

#### Literal Value Consistency Check

Compare literal values between spec and implementation (adding the design draft as a third layer when one
exists) and detect drift:

1. **Build a value table**: For each value extracted in step 2 (spec registry or body text), find the corresponding
   value in the implementation (step 3 extraction sources), and in the design draft when present. Match by value
   identifier, requirement ID (UR/FR/NFR-xxx), or surrounding context (setting name, column name, enum name).
2. **Normalize before comparison**: Treat equivalent representations as equal (e.g., `70%` and `0.7`, `15s` and
   `15000ms`). Report the comparison in the original notation of each layer.
3. **Detect drift**: Report any layer whose value differs from the spec as a **Warning**, marking the drifting layer:

   ```
   [WARN] Value drift detected: rag_confidence_threshold
     spec: 0.7 (§4.1, NFR-AI-005)
     config.py: 0.6 ← drift
   ```

   Include a `design draft:` line only when a draft was actually loaded.

4. **Enum / CHECK constraint completeness**: For enumerated values, compare the full member sets. A member present in
   the implementation but missing from the spec's enumeration (or vice versa) is a drift, even if all other
   members match.
5. **Trace completeness**: If the spec registry entry references a requirement ID, verify the same ID appears in the
   PRD <-> spec traceability table. Report missing IDs as a Warning.

If a value exists in only one layer (e.g., a threshold hard-coded in the implementation with no spec mention),
report it under "Implementation not documented in specs" instead of as drift.

### 5. Discrepancy Classification

**Severity is about impact, not detection confidence.** How certain you are that a finding is real (e.g.
confirmed directly by reading the code vs. inferred from indirect evidence) is a different axis from how
much it matters (whether it touches a public interface, externally observable behavior, or the data
model, versus staying inside internal implementation detail). Do not substitute a confidence label for
the classification below, and do not let findings default to the same severity just because your
confidence in them happens to be equal — grade each by its own impact. A finding you are highly
confident about can still be low severity (an internal-only detail), and a finding you are less certain
about can still be Critical if, once confirmed, it would touch a public interface or the data model.

Classify detected discrepancies as follows:

**Critical (Immediate Action Required)**:

- Public API mismatch (arguments, return value types, CLI options, environment variables)
- Functions specified in the spec not implemented (see Unimplemented-Function Classification above — this is
  Critical only for the `impl-status: "implemented"` case; the other two cases land in Warning/Info below)
- Data model mismatch (entities, fields, types)
- Behavior contradicting the spec

**Warning (Action Recommended)**:

- Functions specified in the spec not implemented, `impl-status` case: undecidable (see classification above —
  count these in the Downgrade Summary)
- Literal value drift (thresholds, enum values, CHECK constraint values differing between spec and implementation)
- Requirement ID referenced by a spec registry entry missing from the traceability table
- Implementation exceeding a constraint stated in the spec
- Module structure mismatch (only when a design draft was loaded)
- Classes/functions existing but not in documentation
- Naming convention mismatch

**Info (Reference)**:

- Functions specified in the spec not implemented, `impl-status` case: expected (see classification above —
  count these in the Downgrade Summary)
- Design drafts left out of the check because they could not be scoped to this run
  (scope `unscoped`), together with the `--ticket` recommendation
- adr ↔ implementation drift is outside this check's scope (see Known Limitations)
- Minor technology stack differences
- Missing comments/documentation

### 6. Comprehensive Review (--full option only)

When the `--full` option is specified, the `spec-reviewer` agent is invoked to perform comprehensive review.

#### Agent Invocation (what to pass)

Invoke `spec-reviewer` per target spec with:

1. The **spec path** from `CHECK_SPEC_SPEC_FILES` (the review target)
2. The spec's **decision logs** — the entry's `adr` field in `CHECK_SPEC_MAPPING`, or the flat
   `CHECK_SPEC_ADR_FILES` list. Pass them explicitly so the agent reviews the same files this run resolved
   instead of re-globbing `${SDD_ADR_PATH}/`. When the list is empty, say so: the agent then records spec ↔ adr
   as **not applicable**, which is the correct result for a feature whose decisions are not recorded yet — not
   a finding, and not "consistent" either
3. `--summary` when the review is embedded in this skill's report

#### Review Content

| Check Item                      | Description                                                              |
|:--------------------------------|:-------------------------------------------------------------------------|
| **PRD <-> spec Traceability**   | Verify PRD requirements are covered in spec (80% coverage threshold)     |
| **spec <-> adr Consistency**    | Verify the decision log's current (latest, non-superseded) decisions agree with the spec, that the spec does not rely on a superseded decision, and that spec-driving decisions are recorded at all. Document level only — adr <-> implementation drift stays out of scope, see Known Limitations |
| **CONSTITUTION.md Compliance**  | Verify compliance with project principles                                |
| **Completeness**                | Verify required sections (purpose, API, constraints, etc.) are present   |
| **Clarity**                     | Detect vague descriptions ("nice to have", "appropriately", etc.)        |
| **SysML Compliance**            | Verify requirement ID format (UR/FR/NFR-xxx) and traceability are proper |

#### Execution Timing

- Executes after spec <-> implementation consistency check is complete
- Performs comprehensive review for target documents (PRD, spec, adr)
- Generates traceability matrix (PRD -> spec -> implementation correspondence)

#### Reporting the spec <-> adr Result

Report the agent's spec ↔ adr outcome in one of three states, never collapsing them:

| Outcome              | When                                                                     |
|:---------------------|:-------------------------------------------------------------------------|
| Consistent           | A decision log was reviewed and no disagreement was found                 |
| Inconsistent ({n})   | A decision log was reviewed and disagreements were found                  |
| Not applicable       | No decision log resolved for the feature — normal, and **not** consistent |

A fix for an inconsistency lands either in the spec, or in a **new appended** adr entry carrying a
`Supersedes` item that links the entry it replaces; `adr/` is append-only, so never edit or delete an existing
entry.

"Not applicable" here is scoped to the **decision log**: no `adr/{feature}.md` was resolved for this feature.
It does not claim the feature's decisions are unrecorded — in a project carried over from v4.x they may still
live in a persistent `specification/{feature}_design.md`. The `doc-consistency-checker` skill covers that case
as **spec ↔ design (v4.x legacy)** and calls the no-source-at-all case `not checked`; both vocabularies mean
"this area was not verified", so neither report may render it as `Consistent`.

**Note**: Comprehensive review requires additional execution time. For quick checks during development, run without
`--full`, and use `--full` before PR creation or for periodic checks.

## Output

Use the `templates/${SDD_LANG:-en}/check_spec_output.md` template for output formatting.

## Check Execution Timing

| Timing                           | Recommended Action                         |
|:---------------------------------|:-------------------------------------------|
| **Before Implementation Start**  | Verify specification existence and content |
| **At Implementation Completion** | Verify consistency with specifications     |
| **Before PR Creation**           | Run as final verification                  |
| **Periodic Check**               | Prevent documentation obsolescence         |

## Serena MCP Integration (Optional)

If Serena MCP is enabled, high-precision consistency checking through semantic code analysis is possible.

### Usage Conditions

- `serena` is configured in `.mcp.json`
- Target language's Language Server is supported (30+ languages supported)

### Additional Features When Serena is Enabled

#### Symbol-Based Consistency Check

| Feature                    | Description                                                             |
|:---------------------------|:------------------------------------------------------------------------|
| `find_symbol`              | Search implementation code for APIs/functions documented in spec        |
| `find_referencing_symbols` | Understand usage locations of specific symbols to identify impact scope |

#### Enhanced Check Items

1. **API Implementation Verification**: Verify functions/classes documented in spec are implemented via symbol search
2. **Signature Match**: Verify function argument/return types match spec
3. **Unused Code Detection**: Detect symbols implemented but not documented in spec
4. **Dependency Understanding**: Analyze reference relationships between modules

#### Additional Output When Using Serena

**Reference**: `examples/serena_symbol_analysis.md`

### Behavior When Serena is Not Configured

Even without Serena, consistency checking is performed using traditional text-based search (Grep/Glob).
Features are limited but work language-agnostically.

## Known Limitations

- **adr ↔ implementation drift is not detected automatically**. From v5.0.0 design decisions persist in
  `${SDD_ADR_PATH}/{feature}.md`, but this skill compares the **spec** with the implementation. An adr entry
  the implementation no longer follows (a library replaced, a rejected alternative later adopted, a decision
  quietly reverted) is not reported — neither by default nor with `--full`, which reviews spec ↔ adr
  **document** consistency only, not adr ↔ code. The one partial exception is a literal value that an adr
  entry states **and** the spec repeats: that value is covered by the literal value consistency check.
- Always state this gap in the report (the output template carries a row for it) so the check's scope is
  never mistaken for "adr verified".
- To cover it manually, read the latest entries of `adr/{feature}.md` for the feature under change and
  confirm the implementation still follows them. When a decision no longer holds, **append** a new entry
  whose body carries a `Supersedes` item pointing at the old entry — `adr/` is append-only, so never edit
  or delete the superseded entry.

## Notes

- If specifications don't exist, recommend creating them with `/generate-spec` first
- A missing design draft is **not** a problem: it is the normal state after implementation completes.
  Never ask the user to create one, and never report its absence as a discrepancy
- Never widen the design input beyond `CHECK_SPEC_DESIGN_DRAFT_FILES`. When several tickets are in flight,
  reading every draft under `${SDD_TASK_PATH}/` makes another ticket's module structure look like a
  discrepancy in this one; ask for `--ticket <number>` instead
- If many discrepancies exist, major specification updates may be needed
- If implementation is correct and specs are outdated, update specifications
- If specifications are correct and implementation is wrong, fix implementation
- Detail that the spec deliberately omits (internal structure, private helpers) is out of scope:
  record it under "Implementation not documented in specs" only when it changes observable behavior
