---
name: doc-consistency-checker
description: "Automatically executed during document updates or before implementation to check consistency between PRD ↔ *_spec.md ↔ *_design.md. Detects missing requirement ID (UR/FR/NFR) references, data model mismatches, API definition discrepancies, terminology inconsistencies, and ensures traceability between documents."
version: 3.0.0
license: MIT
user-invocable: false
allowed-tools: Read, Glob, Grep, Bash
---

# Doc Consistency Checker - Document Consistency Check

Automatically checks consistency between AI-SDD documents (PRD, `*_spec.md`, `*_design.md`) and detects inconsistencies.

## Language Configuration

!`echo "Current language: ${SDD_LANG:-en}"`

When reading templates, use the path: `templates/${SDD_LANG:-en}/`

## Prerequisites

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles, document structure, persistence rules, and Vibe Coding prevention details.

See `references/prerequisites_directory_paths.md` for directory path resolution using `SDD_*` environment variables.

## Input

This skill is triggered automatically via hooks during document updates or before implementation. It scans documents based on feature context.

| Input Source       | Description                                                    |
|:-------------------|:---------------------------------------------------------------|
| Feature context    | Current feature being worked on (from task or document update) |
| Document paths     | Automatically resolved from `${SDD_*}` environment variables   |

**Note**: This skill is `user-invocable: false` and cannot be called directly. Use `/check-spec` for manual consistency checks.

## Document Dependencies

See `references/document_dependencies.md` for the document dependency chain and direction meaning.

## Directory Structure Support

Both flat and hierarchical structures are supported.

**Flat Structure**:

```
${SDD_ROOT}/
├── CONSTITUTION.md                        # Project constitution (top-level)
├── requirement/{feature-name}.md
└── specification/
    ├── {feature-name}_spec.md
    └── {feature-name}_design.md
```

**Hierarchical Structure**:

```
${SDD_ROOT}/
├── CONSTITUTION.md                        # Project constitution (top-level)
├── requirement/
│   ├── {feature-name}.md                  # Top-level feature
│   └── {parent-feature}/
│       ├── index.md                       # Parent feature overview and requirements list
│       └── {child-feature}.md             # Child feature requirements
└── specification/
    ├── {feature-name}_spec.md             # Top-level feature
    ├── {feature-name}_design.md
    └── {parent-feature}/
        ├── index_spec.md                  # Parent feature abstract specification
        ├── index_design.md                # Parent feature technical design document
        ├── {child-feature}_spec.md        # Child feature abstract specification
        └── {child-feature}_design.md      # Child feature technical design document
```

**⚠️ Note the difference in naming conventions**:

| Directory         | Naming Pattern               | Examples                                |
|:------------------|:-----------------------------|:----------------------------------------|
| **requirement**   | No suffix                    | `index.md`, `user-login.md`             |
| **specification** | `_spec` / `_design` required | `index_spec.md`, `user-login_design.md` |

Consistency checks also consider parent-child relationships for hierarchical structures.

## Check Items

### 0. Structural Consistency Check (Strategy A/B)

#### Strategy A: CLI Available (`SDD_CLI_AVAILABLE=true`)

Read `shared/references/cli_integration_guide.md` for standard CLI patterns and issue type mapping.

When `SDD_CLI_AVAILABLE` is `"true"`, use CLI lint to **replace** LLM structural checks in Checks 1-3:

```bash
${SDD_CLI_COMMAND} lint --json 2>&1
```

The CLI covers the following structural checks — **LLM skips these when CLI results are available**:

| CLI Issue Type          | Replaces in Check | LLM Check Skipped                           |
|:------------------------|:-------------------|:--------------------------------------------|
| `orphan-reference`      | Check 1            | Requirement ID mapping (structural part)    |
| `unresolved-dependency` | Check 2            | Dependency chain integrity                  |
| `broken-link`           | Check 2            | Cross-document reference validation         |
| `circular-dependency`   | Check 2            | Circular dependency detection               |

**Integration with Checks 1-3**:

- CLI-detected issues feed directly into the consistency report — no separate "Pre-Check" section
- For documents with CLI-detected structural issues: LLM reads and performs **semantic checks only**
- For documents with **no CLI issues**: LLM **skips dependency chain traversal** and only checks semantic consistency if the document is in scope
- LLM focuses on checks that CLI **cannot** perform (see each Check section below)

#### Strategy B: CLI Not Available (Fallback)

LLM performs all structural and semantic checks using Read, Glob, and Grep tools. Proceed directly to Checks 1-3 without CLI input.

### 0.1. Front Matter Cross-Reference Consistency

**Note**: Detailed front matter validation (common checks, type-specific checks, cross-reference checks) is handled by the `front-matter-reviewer` agent. The caller should invoke `front-matter-reviewer --cross-ref` separately when full front matter validation is needed.

This skill focuses on document content consistency only.

### 1. PRD ↔ spec Consistency

| Check Item                                | Description                                            | Strategy A (CLI) | Strategy B (LLM) |
|:------------------------------------------|:-------------------------------------------------------|:------------------|:--------------------|
| **Requirement ID Mapping**                | Are PRD requirement IDs referenced in spec?            | `orphan-reference` detects unreferenced IDs — LLM verifies **terminology consistency** only | LLM checks all |
| **Functional Requirement Coverage**       | Are PRD functional requirements covered in spec?       | LLM checks (semantic) | LLM checks |
| **Non-Functional Requirement Reflection** | Are PRD non-functional requirements reflected in spec? | LLM checks (semantic) | LLM checks |
| **Terminology Consistency**               | Is same terminology used in PRD and spec?              | LLM checks (semantic) | LLM checks |

### 2. spec ↔ design Consistency

| Check Item                                     | Description                                          | Strategy A (CLI) | Strategy B (LLM) |
|:-----------------------------------------------|:-----------------------------------------------------|:------------------|:--------------------|
| **API Definition Match**                       | Is spec API detailed in design?                      | LLM checks (semantic) | LLM checks |
| **Data Model Match**                           | Do spec type definitions match design?               | LLM checks (semantic) | LLM checks |
| **Requirement Reflection in Design Decisions** | Are spec requirements reflected in design decisions? | LLM checks (semantic) | LLM checks |
| **Constraint Consideration**                   | Are spec constraints considered in design?           | LLM checks (semantic) | LLM checks |
| **Dependency Chain Integrity**                 | Are `depends-on` references valid?                   | `unresolved-dependency`, `broken-link` — **LLM skips** | LLM checks |

### 3. design ↔ Implementation Consistency

| Check Item                     | Description                                                    |
|:-------------------------------|:---------------------------------------------------------------|
| **Module Structure Match**     | Does design module structure match actual directory structure? |
| **Interface Definition Match** | Do design definitions match implementation code?               |
| **Technology Stack Match**     | Are libraries documented in design actually being used?        |

## Automatic Detection Patterns

### Inconsistency Detection

1. **Missing**: Exists in upstream document but not reflected in downstream
2. **Contradiction**: Different content described in upstream and downstream
3. **Obsolescence**: Downstream changes not reflected in upstream

### Detection Method

```
1. Load target documents
   ↓
2. Extract the following elements:
   - Requirement IDs (PRD)
   - API definitions (spec)
   - Type definitions (spec, design)
   - Module structure (design)
   ↓
3. Compare across documents
   ↓
4. Detect and classify inconsistencies
```

## Output Format

Read `templates/${SDD_LANG:-en}/consistency_report.md` and use it for consistency check output.

## Check Execution Timing

| Timing                        | Recommended Check                                  |
|:------------------------------|:---------------------------------------------------|
| **Task Start**                | Verify existing document existence and consistency |
| **Plan Completion**           | spec ↔ design consistency                          |
| **Implementation Completion** | design ↔ implementation consistency                |
| **Review**                    | All inter-document consistency                     |
| **Periodic Check**            | Prevent documentation obsolescence                 |

## Document Update Triggers

Based on consistency check results, recommend document updates in the following cases:

### When to Update `*_spec.md`

- Public API signature changes (arguments, return values, types)
- New data model additions
- Fundamental changes to existing behavior
- When new requirements added in requirements diagram

### When to Update `*_design.md`

- Technology stack changes (library additions/changes)
- Important architectural decisions
- Module structure changes
- New design pattern introductions

### When Updates Are NOT Needed

- Internal implementation optimization (no interface changes)
- Bug fixes (correcting deviations from specifications)
- Refactoring (no behavior changes)

## Notes

- This skill **detects and reports** but does not auto-fix
- Inconsistency resolution is left to developer judgment
- Prioritize upstream documents (PRD > spec > design)
- Do not uniformly treat specs as correct, as implementation may be correct and specs outdated
