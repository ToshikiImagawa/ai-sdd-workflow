# Design Draft Integration Guide

This guide explains how to integrate refactoring plans into the ticket-scoped Design Doc draft for the
`/plan-refactor` skill.

## Overview

Refactoring plans are added to the **Design Doc draft** at `task/{ticket-number}/design-draft.md` rather than to a
separate file — and never to a document under `specification/`. The draft is where the technical "how" of a ticket
lives, and the refactoring plan is exactly that.

Both are **temporary**: they are deleted once implementation completes and the settled decisions have been appended
to `adr/{feature-name}.md`. That is why the plan must state its decisions explicitly enough to survive the move
(see "Decision Log Hand-off" below).

`specification/` holds only the abstract spec. A `{feature-name}_design.md` left there by v4.x is read-only reading
context — do not append the plan to it, and do not create a new one.

## Placement Rules

### When the Design Draft Exists

**Add as new section** at the end of the draft:

```markdown
# {Feature Name} - Technical Design Draft

## Design Overview
...

## Architecture
...

## Implementation Details
...

## Testing Strategy
...

## Refactoring Plan  ← Add here

### Purpose and Background
...

### Current State Analysis
...

### Refactoring Strategy
...
```

If a `## Refactoring Plan` section is already present, replace it rather than appending a second one.

### When the Design Draft Does Not Exist

1. **Create the draft** at `task/{ticket-number}/design-draft.md` from
   `templates/${SDD_LANG}/reverse_design_template.md`, filled in from the spec (Case A) or from the
   reverse-engineering analysis (Case B)
2. **Add the Refactoring Plan section** immediately after the standard sections

## Section Structure

The Refactoring Plan section should include:

1. **Purpose and Background** - Why refactoring is needed
2. **Current State Analysis** - Problems, metrics, root cause
3. **Refactoring Strategy** - Goals, approach, trade-offs
4. **Migration Plan** - Phased tasks with estimates
5. **Impact Analysis** - Breaking changes, affected components, rollback plan
6. **Testing Strategy** - Unit, integration, E2E tests
7. **Success Criteria** - Metrics, acceptance criteria
8. **Risks and Mitigations** - Potential issues and how to handle them
9. **Timeline and Milestones** - Target dates and owners
10. **References** - Links to PRD, spec, patterns, decision log

See `templates/${SDD_LANG}/refactor_plan_section.md` for the full template.

## Integration with Other Sections

### Linking to Existing Sections

When writing the Refactoring Plan, reference the draft's own sections and the spec:

```markdown
### Current State Analysis

**Problems Identified:**

1. **High Coupling** (See "Architecture" section above)
   - Description: Components X and Y are tightly coupled
   - Location: `src/x.ts:45`, referenced in the draft's Component Structure
```

### Updating Existing Sections

As the refactoring progresses, keep the draft's own sections current:

**Before Refactoring:**
```markdown
## Architecture

### Component Structure

- `LoginService`: Handles authentication and session management
```

**After Refactoring:**
```markdown
## Architecture

### Component Structure

- `LoginService`: Handles authentication only (session management extracted)
- `SessionManager`: Manages user sessions (extracted from LoginService)
```

Do not keep a "Refactoring History" list in the draft — the draft is discarded, so history belongs in
`adr/{feature-name}.md`.

## Decision Log Hand-off

The plan is a proposal; implementation may change it. Only **settled** decisions are persisted, and only after
implementation:

1. `/task-cleanup` reads `task/{ticket-number}/` (including `design-draft.md`)
2. It appends the decisions, their rationale, and the rejected alternatives to `adr/{feature-name}.md` (append-only)
3. It then deletes `task/{ticket-number}/`

So write the plan's "Refactoring Strategy" and "Impact Analysis" sections in a form that can be lifted into a
decision log: name the approach chosen, the alternatives rejected, and why.

## Version Control Best Practices

### Commit Strategy

When adding a refactoring plan:

```bash
git add .sdd/task/{ticket-number}/design-draft.md
git commit -m "[add] リファクタリング計画を design-draft.md に追加

- 現状分析: {brief summary}
- 戦略: {approach}
- フェーズ: {number of phases}
"
```

Whether `task/` is committed at all is a project decision: it is a temporary directory, and some projects keep it
out of version control. Follow the project's existing practice.

### Tracking Changes

Use a status header to track where the plan stands:

```markdown
## Refactoring Plan

> **Last Updated:** 2026-02-20
> **Status:** In Progress (Phase 2 of 4)
> **Owner:** @alice
```

## File Naming Conventions

**IMPORTANT:** Follow the established naming conventions:

| Directory        | File Type    | Naming Pattern                                                |
|:-----------------|:-------------|:--------------------------------------------------------------|
| `requirement/`   | PRD          | `{feature-name}.md` (no suffix)                               |
| `specification/` | Spec         | `{feature-name}_spec.md` (`_spec` suffix optional)            |
| `task/`          | Design draft | `{ticket-number}/design-draft.md` (fixed filename, temporary) |
| `adr/`           | Decision log | `{feature-name}.md` (`-decisions` suffix optional)            |

**Examples:**

- ✅ `.sdd/task/68/design-draft.md`
- ✅ `.sdd/specification/auth_spec.md`
- 🕘 `.sdd/specification/auth_design.md` — legacy naming (v4.x): still valid for an existing file, do not
  create a new one
- ❌ `.sdd/task/68/auth_design.md` (the draft filename is fixed)
- ❌ `.sdd/specification/auth_refactor.md` (separate plan file not supported)

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may
still contain these. They **remain valid** — read them as **supplementary input, and treat their absence as
normal**. Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and
never report an existing one as a naming violation or propose deleting it; it may stay until its decisions
have been migrated to `adr/{feature}.md`.

## Hierarchical Structure Support

The **spec** supports flat and hierarchical layouts; the design draft path is always ticket-scoped and flat.

### Flat Structure

```
.sdd/
├── requirement/
│   └── auth.md
├── specification/
│   └── auth_spec.md
├── task/
│   └── 68/
│       └── design-draft.md ← Add Refactoring Plan here
└── adr/
    └── auth.md             ← Settled decisions land here after cleanup
```

### Hierarchical Structure (Parent Feature)

```
.sdd/
├── requirement/
│   └── auth/
│       └── index.md
├── specification/
│   └── auth/
│       └── index_spec.md
├── task/
│   └── 68/
│       └── design-draft.md ← Add Refactoring Plan here
└── adr/
    └── auth/
        └── index.md
```

### Hierarchical Structure (Child Feature)

```
.sdd/
├── requirement/
│   └── auth/
│       ├── index.md (parent PRD)
│       └── login.md (child PRD)
├── specification/
│   └── auth/
│       ├── index_spec.md (parent spec)
│       └── login_spec.md (child spec)
├── task/
│   └── 68/
│       └── design-draft.md ← Add Refactoring Plan here
└── adr/
    └── auth/
        └── login.md
```

## Multi-Feature Refactoring

When refactoring affects multiple features, the plan still lives in a single place — the ticket's draft:

1. Keep one Refactoring Plan per ticket in `task/{ticket-number}/design-draft.md`
2. Name every affected feature in the plan's "Affected Components" table, with its spec path:

```markdown
### Impact Analysis

**Affected Components:**

| Component | Spec | Impact | Mitigation |
|:--|:--|:--|:--|
| `LoginService` | `specification/auth_spec.md` | Constructor signature changes | Update all instantiation sites |
| `ProfileService` | `specification/profile_spec.md` | Reads sessions via the new interface | Update imports |
```

3. At cleanup time, append the decisions to each affected feature's decision log (`adr/auth.md`,
   `adr/profile.md`), so each feature's history is complete on its own

If the work is large enough to need its own requirement, that is a PRD-level split — not a second plan file.

## Post-Refactoring Cleanup

After refactoring is complete:

1. **Update the Refactoring Plan section** with "Completed" status
2. **Update the draft's main sections** to reflect the new architecture
3. **Update the spec** if the refactoring changed the feature's abstract behavior (see `task-cleanup`'s
   "When to Update `*_spec.md`" criteria)
4. **Run `/task-cleanup`** to append the settled decisions to `adr/{feature-name}.md` and delete
   `task/{ticket-number}/`

**Example of what lands in the decision log:**

```markdown
## 2026-03-01: Decoupled session management from authentication

**Decision**: Extract `ISessionManager` and inject it into `LoginService`.

**Rationale**: `LoginService` instantiated `SessionManager` directly, so auth logic could not be unit tested
without a database. Test coverage went from 45% to 85% after the change.

**Rejected alternatives**:
- Service locator — hides the dependency and keeps tests coupled to global state
- Keep the coupling, add integration tests only — leaves a 5s-per-test suite
```

## References

- See `templates/${SDD_LANG}/refactor_plan_section.md` for the full plan template
- See `references/refactor_patterns.md` for refactoring techniques
- See AI-SDD-PRINCIPLES.md for the document structure and persistence rules
- See the `task-cleanup` skill for the `adr/` integration it performs

---

**Last Updated:** 2026-09-02
**Maintained by:** AI-SDD plan-refactor skill
