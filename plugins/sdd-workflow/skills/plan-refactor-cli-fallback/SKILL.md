---
name: plan-refactor-cli-fallback
description: "Plan refactoring for existing features. Analyzes current implementation and creates/updates design documents with refactoring plan."
argument-hint: "<feature-name> [context] [--scope=<dir>] [--ci]"
version: 1.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
---

# Plan Refactoring

Plans refactoring for existing features by analyzing current implementation and creating/updating design documents with
a comprehensive refactoring plan.

This skill supports two scenarios:

- **Case A**: Existing documents (PRD/spec/design) -> Analyze gaps and add refactoring plan
- **Case B**: No documents -> Reverse-engineer spec/design from code, then add refactoring plan

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

| Argument        | Required | Description                                                          |
|:----------------|:---------|:---------------------------------------------------------------------|
| `feature-name`  | Yes      | Target feature name or path (supports flat/hierarchical structure)   |
| `context`       | No       | Refactoring goal or improvement intent |
| `--scope=<dir>` | No       | Limit implementation file search scope (e.g., `src/`, `lib/`)        |
| `--ci`          | No       | CI/non-interactive mode (auto-confirm, no user prompts)              |

## Input Examples

```
auth
user-list "Improve performance with infinite scroll"
auth "Introduce dependency injection for testability"
user-profile --scope=src/profile
auth/login --ci
```

## Front Matter Generation Rules

When generating reverse-engineered spec/design documents (Case B), include YAML front matter.
When updating existing design documents (Case A), preserve existing front matter and update relevant fields.

See `references/front_matter_spec_design.md` for full schema definition.

### Case B: Reverse-Engineered Spec Rules

| Field | Rule |
|:------|:-----|
| `status` | `"review"` (reverse-engineered documents require review) |
| `depends-on` | PRD ID if PRD exists. Empty if no PRD |
| `tags` | Always include `"reverse-engineered"`, plus keywords from code analysis |

### Case B: Reverse-Engineered Design Doc Rules

| Field | Rule |
|:------|:-----|
| `status` | `"review"` (reverse-engineered documents require review) |
| `impl-status` | `"implemented"` (already implemented since reverse-engineered) |
| `depends-on` | Spec ID |
| `tags` | Always include `"reverse-engineered"`, plus keywords from code analysis |

### Case A: Updating Existing Front Matter

1. Preserve all existing front matter fields
2. Update `updated` to current date
3. Add `"refactoring-planned"` to `tags` if not present

## Processing Flow

### Phase 1: Pre-flight Checks

**Step 1.1: Scan for Existing Documents**

Run the document scanning script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor-cli-fallback/scripts/scan-existing-docs.sh" "${FEATURE_NAME}"
```

This script:

1. Checks for PRD, spec, and design documents in both flat and hierarchical structures
2. Exports results to `.sdd/.cache/plan-refactor/existing-docs.json`
3. Determines Case A (documents exist) or Case B (no documents)

**Step 1.2: Read Scan Results**

```bash
Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/existing-docs.json
```

**Step 1.3: Determine Processing Case**

- If `design_exists` is `true` -> **Case A** (existing documents)
- If `design_exists` is `false` -> **Case B** (no documents, reverse-engineering needed)

---

### Phase 1.5: Parse User Intent (Optional)

**If `context` argument is provided:**

Parse the user's refactoring goal and extract:

1. **Primary Goal** - What to achieve
2. **Motivation** - Why it's needed
3. **Approach** - Specific technique if mentioned

**If `context` is NOT provided:**
-> Skip this phase, proceed with automatic analysis only

---

### Phase 2: Implementation Discovery

**Step 2.1: Find Implementation Files**

```bash
SCOPE_DIR="${SCOPE_ARG}"
bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor-cli-fallback/scripts/find-implementation-files.sh" "${FEATURE_NAME}" "${SCOPE_DIR}"
```

**Step 2.2: Read Implementation File List**

```bash
Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/implementation-files.json
```

**Step 2.3: Validate File Count**

- If `file_count` > 20 and NOT in `--ci` mode: Confirm with user

**Step 2.4: Read Implementation Files**

Read up to 10 most relevant files, focusing on main logic.

### Phase 3: Process Branching

#### Case A: Existing Documents

1. Load existing documents (PRD, spec, design)
2. Analyze implementation vs. specification
3. Identify refactoring opportunities
4. Generate refactoring plan using `templates/${SDD_LANG}/refactor_plan_section.md`
5. Update design document (append "## Refactoring Plan" section)

See `references/design_doc_integration.md` for integration guidelines.

#### Case B: No Documents (Reverse Engineering)

1. Reverse-engineer specification using `templates/${SDD_LANG}/reverse_spec_template.md`
2. Write specification document
3. Reverse-engineer design using `templates/${SDD_LANG}/reverse_design_template.md`
4. Write design document
5. Generate and append refactoring plan

---

### Phase 4: Validation

Verify the refactoring plan includes all required sections:

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

### Phase 5: Next Steps

Output summary and recommend next steps.

## Output

- **Case A**: Updated design document with new "Refactoring Plan" section
- **Case B**: New specification + design document (reverse-engineered with refactoring plan)

## Notes

### Using Context Parameter

See `examples/case_a_existing_docs.md` for Case A example.
See `examples/case_b_no_docs.md` for Case B example.
See `references/refactor_patterns.md` for common refactoring patterns.
See `references/design_doc_integration.md` for integration guidelines.

### File Naming Conventions

| Directory        | File Type | Naming Pattern                                         |
|:-----------------|:----------|:-------------------------------------------------------|
| `requirement/`   | PRD       | `{feature-name}.md` (no suffix)                        |
| `specification/` | Spec      | `{feature-name}_spec.md` (`_spec` suffix required)     |
| `specification/` | Design    | `{feature-name}_design.md` (`_design` suffix required) |
