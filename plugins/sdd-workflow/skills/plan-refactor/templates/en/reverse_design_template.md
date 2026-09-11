---
id: "design-{ticket-number}"
title: "{FEATURE_NAME}"
type: "design"
status: "review"
sdd-phase: "plan"
impl-status: "implemented"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
depends-on: []
tags: ["reverse-engineered"]
category: ""
priority: "medium"
risk: "medium"
---

# {FEATURE_NAME} - Technical Design Draft (Reverse Engineered)

> **⚠️ Note**: This design draft was reverse-engineered from existing implementation on {DATE}.
> It documents the current state, not the original design. Review and update as needed.
>
> **This is a temporary draft** at `${SDD_TASK_PATH}/{ticket-number}/design-draft.md`. It is deleted
> after implementation completes, once its settled decisions have been appended to
> `${SDD_ADR_PATH}/{feature-name}.md` by `/task-cleanup`.

## Design Overview

**Current Architecture:**

{HIGH_LEVEL_ARCHITECTURE_DESCRIPTION}

**Technology Stack:**
- Language: {Programming language used in the project}
- Framework: {Framework used}
- Database: {Database system used}
- Libraries: {key libraries}

## Architecture

> **Working material for this ticket.** Of the content below, only the externally observable data flow and
> the module boundaries other code depends on are carried into the persistent spec
> (`{feature-name}_spec.md` § "Behavior and Data Flow" / § "Internal Interfaces"). The component inventory,
> the directory layout and the per-component dependencies are discarded together with this draft — by design,
> because they are re-derivable from the code. See "Reverse-Engineered Analysis — What Persists and What Does
> Not" in the `plan-refactor` skill.

### Component Structure

```
{CURRENT_DIRECTORY_STRUCTURE}
```

**Components:**

1. **{Component 1 Name}** (`{file_path}`)
   - Responsibility: {What it does}
   - Dependencies: {What it depends on}

2. **{Component 2 Name}** (`{file_path}`)
   - Responsibility: ...
   - Dependencies: ...

### Data Flow

```
{DATA_FLOW_DIAGRAM_OR_DESCRIPTION}
```

## Implementation Details

### Key Algorithms

**{Algorithm Name}** ({file_path}:{line_number})
```
{PSEUDOCODE_OR_DESCRIPTION}
```

### State Management

{How state is managed - Redux, Context, database, etc.}

### Error Handling

{Current error handling patterns}

## API Design

### Endpoints (if applicable)

| Method | Path | Description | Implementation |
|:--|:--|:--|:--|

## Testing Strategy

**Current Test Coverage:**
- Unit tests: {file paths}
- Integration tests: {file paths}
- Coverage: {percentage, if known}

**Gaps:**
{Areas lacking tests}

## Deployment

{Current deployment process, if observable}

## Technical Debt Observations

This draft is deleted at `/task-cleanup`, so every item below names where it survives.

1. **{Debt Item 1}**: {Description}
   - Severity: {High/Medium/Low}
   - Location: `{file_path}`
   - Persistent destination: {Resolved by this refactoring -> rationale of the `adr/{feature-name}.md` entry
     appended by `/task-cleanup` | Deferred -> tracker item `{issue/ticket id, or "to be created"}` |
     Contradicts the spec -> proposed `{feature-name}_spec.md` correction (human approval)}

2. **{Debt Item 2}**: ...

---

**Next Steps:**
1. Verify this design matches actual implementation
2. Address technical debt items, or create the tracker items for the deferred ones
3. Plan refactoring (add Refactoring Plan section below)
4. After implementation, run `/task-cleanup` to append the settled decisions to
   `${SDD_ADR_PATH}/{feature-name}.md` before this draft is deleted
