---
name: plan-refactor-cli
description: "CLI-enhanced refactoring planner. Analyzes current implementation and creates/updates design documents with refactoring plan using sdd-cli for document discovery."
argument-hint: "<feature-name> [context] [--scope=<dir>] [--ci]"
version: 1.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
---

# Plan Refactoring (CLI)

CLI-enhanced version: Uses `sdd-cli search` for related document discovery,
reducing Glob/Grep overhead for document location.

This skill supports two scenarios:

- **Case A**: Existing documents (PRD/spec/design) -> Analyze gaps and add refactoring plan
- **Case B**: No documents -> Reverse-engineer spec/design from code, then add refactoring plan

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/cli_integration_guide.md` - CLI command reference
- `references/cli_error_handling.md` - Error handling and fallback strategies

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.

## Input

$ARGUMENTS

| Argument        | Required | Description                                                          |
|:----------------|:---------|:---------------------------------------------------------------------|
| `feature-name`  | Yes      | Target feature name or path (supports flat/hierarchical structure)   |
| `context`       | No       | Refactoring goal or improvement intent |
| `--scope=<dir>` | No       | Limit implementation file search scope                               |
| `--ci`          | No       | CI/non-interactive mode                                              |

## Input Examples

```
auth
user-list "Improve performance with infinite scroll"
auth "Introduce dependency injection for testability"
user-profile --scope=src/profile
auth/login --ci
```

## Front Matter Generation Rules

Same as non-CLI version. See `references/front_matter_spec_design.md` for full schema definition.

## Processing Flow

### Phase 1: CLI - Document Discovery

Use `sdd-cli` to find existing documents for the feature:

```bash
# Find all documents related to the feature
sdd-cli search --feature-id <feature-name> --format json
```

**From CLI output, extract:**

1. Whether PRD, spec, and design documents exist
2. Their file paths
3. Front matter data (status, depends_on, etc.)

**Determine Processing Case:**

- If design document found -> **Case A** (existing documents)
- If no design document -> **Case B** (reverse-engineering needed)

**Error Handling**: If CLI fails, fall back to the shell script approach:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor-cli/scripts/scan-existing-docs.sh" "${FEATURE_NAME}"
```

---

### Phase 1.5: Parse User Intent (Optional)

Same as non-CLI version. Parse context argument if provided.

---

### Phase 2: Implementation Discovery

**Step 2.1: Find Implementation Files**

```bash
SCOPE_DIR="${SCOPE_ARG}"
bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor-cli/scripts/find-implementation-files.sh" "${FEATURE_NAME}" "${SCOPE_DIR}"
```

**Step 2.2-2.4**: Same as non-CLI version (read file list, validate count, read files).

### Phase 3: Process Branching

#### Case A: Existing Documents

1. Load existing documents (paths from CLI Phase 1)
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
- [ ] Current State Analysis
- [ ] Refactoring Strategy
- [ ] Migration Plan
- [ ] Impact Analysis
- [ ] Testing Strategy
- [ ] Success Criteria
- [ ] Risks and Mitigations

### Phase 5: Next Steps

Output summary and recommend next steps.

## Output

- **Case A**: Updated design document with new "Refactoring Plan" section
- **Case B**: New specification + design document (reverse-engineered with refactoring plan)

## Notes

See `examples/case_a_existing_docs.md` for Case A example.
See `examples/case_b_no_docs.md` for Case B example.
See `references/refactor_patterns.md` for common refactoring patterns.
