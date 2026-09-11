---
name: plan-refactor
description: "Plan refactoring for existing features. Analyzes current implementation and records the refactoring plan in the ticket-scoped design draft."
argument-hint: "<feature-name> [context] [--scope=<dir>] [--ticket <number>] [--ci]"
arguments: [feature-name]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/**), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/scripts/scan-existing-docs.py" *), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/scripts/find-implementation-files.py" *)
---

# Plan Refactoring

Plans refactoring for existing features by analyzing current implementation and writing a comprehensive refactoring
plan into the ticket-scoped Design Doc draft (`task/{ticket-number}/design-draft.md`).

This skill supports two scenarios, decided by whether a **spec** exists:

- **Case A**: Spec exists → Analyze gaps against spec/implementation and add the refactoring plan to the design draft
- **Case B**: No spec → Reverse-engineer the spec from code (persisted under `specification/`) and the design into the
  design draft, then add the refactoring plan

**Never decide the case from a design document.** Technical Design Documents are not persistent: they live at
`task/{ticket-number}/design-draft.md` and are deleted after implementation, so their absence is the normal state.
A leftover `specification/{feature-name}_design.md` from v4.x is read-only context, never a case signal and never
a write target.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

**PRD is read-only context**: Although `allowed-tools` grants `Edit(.sdd/**)`, this skill only writes to
`${SDD_TASK_PATH}/{ticket-number}/design-draft.md` and — in Case B only — a reverse-engineered spec under
`specification/`. The PRD loaded in Step 3A.1 is reference context for the refactoring plan — never write to
`requirement/**`. If the analysis surfaces a PRD/implementation contradiction, record it in the plan for human
review; do not resolve it by editing the PRD. See AI-SDD-PRINCIPLES.md § Document Update Triggers
("Updating `requirement/` (PRD) — Never Automated").

**`adr/` is not written by this skill either**: the decisions the plan settles on are integrated into
`${SDD_ADR_PATH}/{feature-name}.md` by `task-cleanup` once implementation completes — see "Decision Log Hand-off"
below.

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

- `feature-name`: $feature-name

Full argument string: $ARGUMENTS

> **Fallback**: If the value above is empty, remains a literal `$` placeholder, or starts with `--`
> (a flag captured positionally), treat the argument as omitted and interpret the full argument
> string instead. Ask the user interactively when a required argument is missing.
> `context` is free-form text and flags — extract them from the full argument string
> (everything after `feature-name`).

| Argument            | Required | Description                                                                                                                                                                             |
|:--------------------|:---------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `feature-name`      | Yes      | Target feature name or path (supports flat/hierarchical structure)                                                                                                                      |
| `context`           | No       | Refactoring goal or improvement intent (e.g., "無限スクロール化", "依存性注入導入")                                                                                                                    |
| `--scope=<dir>`     | No       | Limit implementation file search scope (e.g., `src/`, `lib/`)                                                                                                                           |
| `--ticket <number>` | No       | Ticket number (GitHub issue number, JIRA key, etc.) that locates the Design Doc draft `task/{ticket-number}/design-draft.md`. **Both `--ticket <number>` and `--ticket=<number>` are accepted.** Resolved interactively when omitted; required in `--ci` mode |
| `--ci`              | No       | CI/non-interactive mode (auto-confirm, no user prompts)                                                                                                                                 |

**Ticket argument forms**: write it with a space or an equals sign — `--ticket 123` and `--ticket=123` are
equivalent; strip the `--ticket`/`--ticket=` prefix before using the value.

**When the ticket number is missing**:

- **Interactive**: Step 1.0 asks for it with `AskUserQuestion` before any script runs or any file is written
- **`--ci` mode**: abort immediately with an error naming the missing flag and the fix
  (`/plan-refactor {feature-name} --ticket=<number>`). Nothing is created under `task/`, no reverse-engineered
  spec is written, and no cache file is produced

## Input Examples

See `examples/cli_usage.md` for example invocations.

## Front Matter Generation Rules

When generating a reverse-engineered spec or a new design draft, include YAML front matter.
When updating an existing design draft, preserve existing front matter and update relevant fields.

See `references/front_matter_spec_design.md` for full schema definition, dependency direction rules, and validation checklist.

### Case B: Reverse-Engineered Spec Rules

| Field | Rule |
|:------|:-----|
| `id` | `"spec-{feature-name}"`. For hierarchical: `"spec-{parent}-{feature-name}"` |
| `status` | `"review"` (reverse-engineered documents require review) |
| `depends-on` | PRD ID if PRD exists (e.g., `["prd-auth"]`). Empty if no PRD |
| `tags` | Always include `"reverse-engineered"`, plus keywords from code analysis |

**No PRD found**: This skill never writes to `requirement/**` (see "PRD is read-only context" above). When
`depends-on` is left empty because no PRD exists for `feature-name`, do not stop at the empty field — include a
proposal in the refactoring plan output recommending a human-approved, reverse-engineered draft PRD
(`status: "draft"`, `tags` including `"reverse-engineered"`), per AI-SDD-PRINCIPLES.md § Workflow Management
Guidelines ("Never Automated" governs rewriting, not drafting a new PRD from scratch). The proposal is a
recommendation only — never draft or write the PRD file itself.

### Reverse-Engineered Design Draft Rules

| Field | Rule |
|:------|:-----|
| `id` | `"design-{ticket-number}"` (matches the ticket-scoped draft path, not the feature name) |
| `status` | `"review"` (reverse-engineered documents require review) |
| `impl-status` | `"implemented"` (already implemented since reverse-engineered) |
| `depends-on` | Spec ID (e.g., `["spec-auth"]`) |
| `tags` | Always include `"reverse-engineered"`, plus keywords from code analysis |

### Updating an Existing Design Draft

When adding a refactoring plan to a design draft that already exists:

1. Preserve all existing front matter fields
2. Update `updated` to current date
3. Add `"refactoring-planned"` to `tags` if not present

## Processing Flow

### Phase 1: Pre-flight Checks

**Step 1.0: Resolve the Ticket Number**

The Design Doc draft path is ticket-scoped, so a ticket number is required before anything can be written.

- Take it from the `--ticket` flag when given — accept **both** `--ticket <number>` and `--ticket=<number>`
- Otherwise ask the user with `AskUserQuestion` (offer the branch name / current issue as a hint)
- In `--ci` mode, `--ticket` is required: abort here with an error naming the flag and the fix
  (`--ticket=<number>`), before Step 1.1 runs — never fall back to a guessed ticket number

Set `TICKET_NUMBER` from the resolved value.

**Step 1.1: Scan for Existing Documents**

Run the document scanning script: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/scripts/scan-existing-docs.py" "${FEATURE_NAME}" "${TICKET_NUMBER}"`

This script:

1. Checks for the PRD and the spec in both flat and hierarchical structures. The spec is matched with **and** without
   the `_spec` suffix (`{feature-name}_spec.md`, then `{feature-name}.md`), because the suffix is optional under
   `specification/`
2. Checks for the ticket-scoped design draft `${SDD_TASK_PATH}/{ticket-number}/design-draft.md`
3. Also reports a legacy `specification/{feature-name}_design.md` (v4.x) as `legacy_design_*` — reading context only
4. Exports results to `${SDD_ROOT}/.cache/plan-refactor/existing-docs.json`, including a resolved `case` field

**Step 1.2: Read Scan Results**

Read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/existing-docs.json`.

See `examples/cache_json_outputs.md` for an example of this file's content.

**Step 1.3: Determine Processing Case**

- If `spec_exists` is `true` (`case` is `"A"`) → **Case A** (spec exists)
- If `spec_exists` is `false` (`case` is `"B"`) → **Case B** (no spec, reverse-engineering needed)

`design_draft_exists` and `legacy_design_exists` never affect this decision — they only add reading context in
Step 3A.1.

**If `legacy_design_exists` is `true`**, tell the user that the file is read as supplementary input but not
updated, and that it **remains valid** where it is. Its decisions may eventually move to `adr/{feature}.md`
— the steps are in `${CLAUDE_PLUGIN_ROOT}/README.md`, section "Extracting Existing `*_design.md` Files into
`adr/`" under "Migration from v4.x" (`README.ja.md` next to it holds the Japanese version) — but that is a
human judgment call: do not migrate it yourself, and never report it as a naming violation or a deletion
candidate.

---

### Phase 1.5: Parse User Intent (Optional)

**If `context` argument is provided:**

Parse the user's refactoring goal and extract:

1. **Primary Goal** - What to achieve (e.g., "無限スクロール化", "依存性注入導入")
2. **Motivation** - Why it's needed (e.g., "パフォーマンス改善", "テスト容易性向上")
3. **Approach** - Specific technique if mentioned (e.g., "react-window使用", "Strangler Figパターン")

**Example context parsing:**

| Context Input                       | Extracted Information                          |
|:------------------------------------|:-----------------------------------------------|
| `"無限スクロール化してパフォーマンス改善"`             | Goal: 無限スクロール化<br>Motivation: パフォーマンス改善        |
| `"依存性注入を導入してテスト容易性を向上"`             | Goal: 依存性注入導入<br>Motivation: テスト容易性向上          |
| `"Strangler Figパターンで段階的にマイクロサービス化"` | Goal: マイクロサービス化<br>Approach: Strangler Figパターン |
| `"テスト容易性を上げるため密結合を解消"`              | Goal: 密結合解消<br>Motivation: テスト容易性向上            |
| `"モジュール境界を明確化してメンテナンス性向上"`          | Goal: モジュール境界明確化<br>Motivation: メンテナンス性向上      |
| `"react-windowを使って仮想スクロール化"`        | Goal: 仮想スクロール化<br>Approach: react-window使用     |

**Use extracted information in Phase 3:**

- Prioritize the user's goal in "Purpose and Background"
- Align "Refactoring Strategy" with the specified approach
- Include the motivation in "Business/Technical Drivers"

**If `context` is NOT provided:**
→ Skip this phase, proceed with automatic analysis only (Phase 2)

---

### Phase 2: Implementation Discovery

**Step 2.1: Find Implementation Files**

Run the implementation file search script. Set `SCOPE_DIR` from the `--scope` argument (or leave empty), then run
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/scripts/find-implementation-files.py" "${FEATURE_NAME}" "${SCOPE_DIR}"`.

This script:

1. Searches for files matching feature name (by filename and content)
2. Limits search to specified scope if `--scope` is provided
3. Excludes `node_modules/`, `.git/`, `dist/`, etc.
4. Exports results to `${SDD_ROOT}/.cache/plan-refactor/implementation-files.json`

**Step 2.2: Read Implementation File List**

Read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/implementation-files.json`.

See `examples/cache_json_outputs.md` for an example of this file's content.

**Step 2.3: Validate File Count**

- If `file_count` > 20 and NOT in `--ci` mode:
    - Use `AskUserQuestion` to confirm: "Found {count} files. This may take time to analyze.
      Continue? [Yes/No/Adjust Scope]"
    - If "Adjust Scope": Ask user for new scope directory

**Step 2.4: Read Implementation Files**

Read `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/all-files.txt`.

Then read the actual implementation files (prioritize key files):

1. Read up to 10 most relevant files
2. Focus on main logic files, avoid test files initially

### Phase 3: Process Branching

#### Case A: Spec Exists

**Step 3A.1: Load Existing Documents**

Read the following files (paths from scan results):

- PRD: `{prd_path}` (if exists)
- Spec: `{spec_path}` (required for Case A)
- Design draft: `{design_draft_path}` (if exists — supplementary input: an in-progress plan for this ticket)
- Legacy design doc: `{legacy_design_path}` (if exists — supplementary input only, from v4.x; do not edit it)

**Step 3A.2: Analyze Implementation vs. Specification**

Compare implementation with the spec (and with the design draft's component descriptions, if present):

1. Identify the behavior and components the spec requires
2. Check if implementation matches them
3. Identify deviations, technical debt, or areas needing refactoring

**Step 3A.3: Identify Refactoring Opportunities**

Based on analysis, identify:

- **Problems**: Tight coupling, code duplication, poor testability, etc.
- **Gaps**: Missing functionality, incomplete implementation
- **Technical Debt**: Hard-coded values, lack of error handling, etc.

Assign each debt item a persistent destination as you record it — see "Technical Debt Observations — Where They
Persist" below. The design draft is deleted at cleanup, so an item with no destination does not survive.

**If `context` was provided (from Phase 1.5):**

- Prioritize issues related to the user's goal
- Align identified problems with the specified motivation
- Example: If context is "無限スクロール化してパフォーマンス改善", focus on:
    - Current loading performance issues
    - Memory usage problems
    - Scalability concerns

**Step 3A.4: Generate Refactoring Plan**

Use template: read `${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/templates/${SDD_LANG}/refactor_plan_section.md`.

Fill in the template with:

- **Purpose and background** (why refactoring is needed)
    - **If `context` provided**: Start with user's goal (e.g., "無限スクロール化してパフォーマンス改善")
    - Include motivation from context in "Business/Technical Drivers"
- **Current state analysis** (problems, metrics, root cause)
    - Focus on issues related to user's goal if context provided
- **Refactoring strategy** (goals, approach, trade-offs)
    - **If `context` provided**: Align goals with user's intent
    - **If approach specified in context**: Use it (e.g., "Strangler Figパターン", "react-window使用")
- Migration plan (phased tasks)
- Impact analysis (breaking changes, affected components, rollback plan)
    - **If this refactoring breaks backward compatibility**: compare at least 2 concrete alternative approaches
      (e.g., immediate breaking change / phased deprecation with a migration window / dual old-new shim). Do not
      implement any of them — present the comparison and leave the choice for human review.
- Testing strategy
- Success criteria
- Risks and mitigations
- Timeline and milestones

**Step 3A.5: Write the Plan into the Design Draft**

Target: `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/design-draft.md`.

- If the draft already exists (`design_draft_exists` is `true`), append the "## Refactoring Plan" section at the end
  (replace it if a section with that heading is already there)
- If it does not exist, create it from `templates/${SDD_LANG}/reverse_design_template.md` — filled in from the spec and
  the implementation analysis — and then append the "## Refactoring Plan" section
- Never write the plan into `specification/**`; a persisted design doc there is not a valid target

See `references/design_doc_integration.md` for guidelines on integration.

---

#### Case B: No Spec (Reverse Engineering)

**Step 3B.1: Reverse-Engineer Specification**

Analyze implementation files and extract:

- Functional requirements (what the feature does)
- Non-functional requirements (performance, security, etc.)
- Interface specifications (APIs, function signatures, and the internal module boundaries other code depends on)
- Dependencies
- Data model
- Externally observable data flow (entry points, external calls and side effects, results returned)

Use template: read `${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/templates/${SDD_LANG}/reverse_spec_template.md`.

This spec is the **only persistent** output of the reverse-engineering, so anything extracted in Step 3B.3
that belongs here must land here — see "Reverse-Engineered Analysis — What Persists and What Does Not".

**Step 3B.2: Write Specification Document**

The reverse-engineered spec is a **persistent** document. Determine path based on structure:

- Flat: `${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`
- Hierarchical: `${SDD_SPECIFICATION_PATH}/{parent-feature}/{child-feature}_spec.md`

The `_spec` suffix is optional under `specification/`; keep it for new files unless the project's existing files
consistently omit it.

`Write {spec_path}`.

Mark the document as reverse-engineered:
> **⚠️ Note**: This specification was reverse-engineered from existing implementation on {DATE}.
> It may not reflect the original design intent. Please review and update as needed.

**Step 3B.3: Reverse-Engineer the Design Draft**

Analyze implementation files and extract:

- Architecture overview
- Component structure
- Data flow
- Key algorithms
- API design
- Database schema
- Testing strategy
- Technical debt observations (each with a persistent destination — see "Technical Debt Observations — Where
  They Persist")

Use template: read `${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/templates/${SDD_LANG}/reverse_design_template.md`.

Most of this list does **not** survive the draft's deletion, and only part of it belongs in the spec written
in Step 3B.2. Before writing the draft, settle each item against the mapping in "Reverse-Engineered Analysis
— What Persists and What Does Not". The spec-bound parts must not be left here only: the spec was already
written in Step 3B.2, so go back and add them to it (its `updated` field moves to the current date).

**Step 3B.4: Write the Design Draft**

The path is ticket-scoped and fixed, independent of the spec's flat/hierarchical structure:

- `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/design-draft.md`

`Write {design_draft_path}`.

This file is a **temporary draft**: it is deleted after implementation, once its key decisions are integrated into
`${SDD_ADR_PATH}/{feature-name}.md` (see `task-cleanup` skill). Do not write a design document under
`specification/`.

**Step 3B.5: Generate Refactoring Plan**

Follow the same process as Case A Step 3A.4-3A.5:

1. Read refactoring plan template
2. Fill in the template
3. Append "## Refactoring Plan" section to the newly created design draft

---

### Phase 4: Validation

Verify the refactoring plan includes all required sections:

**Required Sections Checklist:**

- [ ] Purpose and Background
- [ ] Current State Analysis (with problems identified)
- [ ] Refactoring Strategy (with goals and approach)
- [ ] Migration Plan (with phased tasks and estimates)
- [ ] Impact Analysis (breaking changes, affected components, rollback plan)
- [ ] Testing Strategy (unit, integration, E2E tests)
- [ ] Success Criteria (metrics and acceptance criteria)
- [ ] Risks and Mitigations
- [ ] Timeline and Milestones (optional but recommended)
- [ ] References (to PRD, spec, patterns)
- [ ] Every Technical Debt Observation names a persistent destination (`adr/` entry at cleanup / tracker item /
      spec update proposal) — see "Technical Debt Observations — Where They Persist"
- [ ] Case B only: every spec-bound item extracted in Step 3B.3 is present in the reverse-engineered spec
      (Public API / Internal Interfaces / Data Model / Behavior and Data Flow / Architecture Pattern) — see
      "Reverse-Engineered Analysis — What Persists and What Does Not"

If any required section is missing, add it before proceeding.

### Phase 5: Next Steps

Output a summary and recommend next steps. See `templates/${SDD_LANG:-en}/completion_output.md` for the "Next Steps
Summary" format.

Always include the Decision Log Hand-off below in the recommended next steps, and — in Case B — the persistence
boundary from "Reverse-Engineered Analysis — What Persists and What Does Not".

### Decision Log Hand-off (`adr/`)

The design draft — and with it the refactoring plan — is deleted once implementation completes, so the decisions the
plan settles on must be persisted elsewhere:

1. The plan records the chosen strategy, the rejected alternatives, and the trade-offs (the "Refactoring Strategy" and
   "Impact Analysis" sections are written with that in mind)
2. After implementation, `/task-cleanup` integrates those decisions and their rationale into
   `${SDD_ADR_PATH}/{feature-name}.md` (append-only) and then deletes `task/{ticket-number}/`
3. This skill does **not** write to `adr/` itself: the plan is a proposal, and implementation may change it. Only
   settled decisions belong in the append-only log

Tell the user this explicitly in the completion output, so the plan is not left as the only record.

### Reverse-Engineered Analysis — What Persists and What Does Not

Step 3B.3 extracts more from the code than a spec is allowed to hold, and the design draft that receives it is
deleted at `/task-cleanup`. Each extracted item therefore has exactly one of two fates: it goes into the
persistent reverse-engineered spec (Step 3B.2), or it is knowingly discarded with the draft. The mapping is
fixed:

| Extracted item                                                                    | Persistent home                                                                                                                       |
|:----------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|
| API design (public functions, classes, endpoints, signatures)                     | Spec § "Interface Specifications" → "Public API"                                                                                       |
| Module boundaries other code depends on                                            | Spec § "Interface Specifications" → "Internal Interfaces" — the boundary and its contract, not the components behind it                |
| Database schema, data structures                                                   | Spec § "Data Model"                                                                                                                    |
| Data flow, **externally observable part only** (entry points, external calls and side effects, results returned) | Spec § "Behavior and Data Flow"                                                                        |
| Architecture overview, **pattern name only** (e.g. layered, MVC, event-driven)      | Spec § "Implementation Notes" → "Architecture Pattern"                                                                                 |
| Component structure (component inventory, per-component responsibilities and dependencies, directory layout) | **None — discarded with the draft, by design**                                                              |
| Data flow between private components (internal call sequence)                       | **None — discarded with the draft, by design**                                                                                         |
| Key algorithms, state management internals, error-handling patterns, current test coverage figures | **None — discarded with the draft, by design**                                                                        |

The "None" rows are a deliberate limit, not a gap to be fixed:

- They are **derived information**: re-running this skill re-derives them from the code, and a persisted copy
  starts drifting from the code the moment the code changes
- `adr/` is not the answer: it records **decisions**, not know-how or structure descriptions
  (`AI-SDD-PRINCIPLES.md` § Knowledge Asset Persistence Management). Only a *decision about* the structure
  ("split the fetch layer out of the view component, because ...") persists, and `/task-cleanup` appends that
  as an `adr/{feature-name}.md` entry
- The spec is not the answer either: `generate-spec`'s `spec_template.md` § "What NOT to Include" routes
  "Architecture and module structure", "Directory structure and file placement" and "Test strategy and
  coverage goals" **away** from the spec. Writing them there would contradict the spec template and create a
  second, stale description of the code's structure
- Do not invent a new document for them

In Case A the spec already exists and this skill never rewrites it. The same boundary applies to the draft's
analysis sections; when the implementation contradicts the behavior the spec describes, propose a spec
correction for human approval instead (see "Technical Debt Observations — Where They Persist").

State this in the Phase 5 output: name the spec sections the reverse-engineering wrote to, and say plainly
that the draft's component structure and internal flow go away with the draft.

### Technical Debt Observations — Where They Persist

The "Technical Debt Observations" list (Step 3B.3 / the "Problems Identified" and "Technical Debt" analysis in
Step 3A.3) lives in the design draft, which is deleted at `/task-cleanup`. **Every observation must therefore
name a persistent destination in the plan**, chosen from the three below. An observation whose only record is
the draft is lost at cleanup — that is a plan defect, not an acceptable outcome.

| Observation                                                                 | Persistent destination                                                                                                                                     | Who records it                                     |
|:----------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------|
| Debt this refactoring resolves                                              | The `adr/{feature-name}.md` entry for the refactoring decision — the debt is the constraint written under **Rationale**                                     | `/task-cleanup`, after implementation              |
| Debt consciously deferred or accepted (out of scope for this ticket)         | A tracker item (GitHub Issue / JIRA). Recommend creating it and record the resulting ticket id next to the observation. When the deferral was itself a decision ("accept this debt for now, because ..."), it also earns its own `adr/` entry at cleanup | Human creates the ticket; `/task-cleanup` the entry |
| Debt that means the implementation contradicts the behavior the spec describes | The spec (`*_spec.md`) — propose the correction for human approval, per "Post-Refactoring Cleanup" below                                                    | Human-approved spec update                          |

Rules:

- Do **not** invent a new document for debt: v5 has no standing debt list, and `adr/` records decisions, not
  know-how (`AI-SDD-PRINCIPLES.md` § Knowledge Asset Persistence Management). A debt observation reaches `adr/`
  only as the rationale of a decision that is being recorded anyway
- This skill never creates the tracker item or edits the spec itself — it names the destination in the plan and
  recommends the action in the completion output (Phase 5)
- Repeat the destination assignment in the Phase 5 summary, listing any observation still without one

## Output

- **Case A**: Design draft (`task/{ticket-number}/design-draft.md`) created or updated with a "Refactoring Plan" section
- **Case B**:
    - New specification document under `specification/` (reverse-engineered, persistent) — the only lasting
      record of the analysis; what it does and does not carry is fixed by "Reverse-Engineered Analysis — What
      Persists and What Does Not"
    - New design draft under `task/{ticket-number}/` (reverse-engineered, temporary, with the refactoring plan)

Output format: see the "Output Format" section in `templates/${SDD_LANG:-en}/completion_output.md`.

## Notes

### Using Context Parameter

The optional `context` parameter allows you to explicitly specify your refactoring goal:

**Without context (automatic analysis):** `/plan-refactor user-list`

→ Claude analyzes code and design, automatically identifies technical debt and proposes generic refactoring

**With context (goal-directed refactoring):** `/plan-refactor user-list "無限スクロール化してパフォーマンス改善"`

→ Claude focuses on infinite scroll implementation, prioritizes performance issues, proposes specific approach

**Context examples:**

| Use Case                 | Context Example                     |
|:-------------------------|:------------------------------------|
| Performance optimization | `"無限スクロール化してパフォーマンス改善"`             |
| Architecture improvement | `"依存性注入を導入してテスト容易性を向上"`             |
| Gradual migration        | `"Strangler Figパターンで段階的にマイクロサービス化"` |
| Technology upgrade       | `"react-windowを使って仮想スクロール化"`        |
| Code quality             | `"密結合を解消してモジュール境界を明確化"`             |

**Benefits of using context:**

- More focused refactoring plan
- Aligns with your specific intent
- Includes your preferred approach/pattern
- Reduces ambiguity in Purpose and Strategy sections

### Context Parameter Edge Cases

**Ambiguous Context:**

If context is unclear or too vague (e.g., "improve it", "make it better"), use `AskUserQuestion` to clarify. See
`examples/ask_user_question_patterns.md` for the question/options pattern.

**Unrealistic or Infeasible Context:**

If context contains technically unrealistic goals (e.g., "make it 100x faster", "zero latency"):

1. Acknowledge the goal in "Purpose and Background"
2. Propose realistic, achievable targets in "Refactoring Strategy"
3. Explain trade-offs and constraints in "Trade-offs" section

Example:

- User context: "make it 100x faster"
- Plan approach: "Target 5-10x performance improvement through caching and query optimization. 100x improvement would
  require architectural changes beyond refactoring scope."

**Conflicting Requirements:**

If context includes conflicting goals (e.g., "maximize performance and minimize code complexity"), use
`AskUserQuestion` to prioritize. See `examples/ask_user_question_patterns.md` for the question/options pattern.
Document the prioritization in "Purpose and Background".

### Document Integration

- Refactoring plans are integrated into the ticket's design draft, not separate files
- This keeps the plan next to the technical design it depends on, and lets both be discarded together once the
  decisions have been moved into `adr/`
- See `references/design_doc_integration.md` for detailed integration guidelines

### Refactoring Patterns

- See `references/refactor_patterns.md` for common refactoring patterns
- Includes: Extract Interface, Extract Class, Dependency Injection, Strategy Pattern, Strangler Fig Pattern, etc.

### File Naming Conventions

**IMPORTANT:** Follow the established naming conventions:

| Directory        | File Type    | Naming Pattern                                                |
|:-----------------|:-------------|:--------------------------------------------------------------|
| `requirement/`   | PRD          | `{feature-name}.md` (no suffix)                               |
| `specification/` | Spec         | `{feature-name}_spec.md` (`_spec` suffix optional)            |
| `task/`          | Design draft | `{ticket-number}/design-draft.md` (fixed filename, temporary) |
| `adr/`           | Decision log | `{feature-name}.md` (`-decisions` suffix optional)            |

New design documents are no longer written under `specification/`. A `{feature-name}_design.md` left there by
v4.x remains valid: read it as supplementary input (its absence is normal), never write to it, and never treat
it as a naming violation.

### Hierarchical Structure Support

Both flat and hierarchical structures are supported **for the spec**; the design draft path is always ticket-scoped.
See the "Hierarchical Structure Support" section in `references/design_doc_integration.md` for the flat /
hierarchical-parent / hierarchical-child directory layouts.

### Examples

- See `examples/case_a_existing_docs.md` for Case A example
- See `examples/case_b_no_docs.md` for Case B example

### Multi-Feature Refactoring

When refactoring affects multiple features:

1. Keep one refactoring plan per ticket in that ticket's design draft
2. Name every affected feature in the plan's "Affected Components" table
3. When the ticket's decisions are integrated into `adr/`, append them to each affected feature's decision log

See `references/design_doc_integration.md` for guidance.

### Post-Refactoring Cleanup

After refactoring is complete:

1. Update the Refactoring Plan section status to "Completed" in the design draft
2. Update the spec if the refactoring changed the feature's abstract behavior (see `task-cleanup`'s
   "When to Update `*_spec.md`" criteria)
3. Run `/task-cleanup` to integrate the settled decisions into `${SDD_ADR_PATH}/{feature-name}.md` and delete
   `task/{ticket-number}/`

---

**Last Updated:** 2026-02-15
**Maintained by:** AI-SDD Workflow Plugin
