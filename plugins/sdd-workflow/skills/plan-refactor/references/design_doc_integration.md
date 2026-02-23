# Design Document Integration Guide

This guide explains how to integrate refactoring plans into existing design documents for the `/plan-refactor` skill.

## Overview

Refactoring plans should be added to the **existing design document** (`*_design.md`) rather than creating separate files. This maintains traceability and keeps all design information in one place.

## Placement Rules

### When Design Doc Exists

**Add as new section** at the end of the document:

```markdown
# {Feature Name} - Technical Design Document

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

### When Design Doc Does Not Exist

1. **Generate design doc** using reverse-engineering
2. **Add Refactoring Plan section** immediately after standard sections

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
10. **References** - Links to PRD, spec, patterns

See `templates/${SDD_LANG}/refactor-plan-section.md` for full template.

## Integration with Other Sections

### Linking to Existing Sections

When writing the Refactoring Plan, reference existing sections in the design doc:

```markdown
### Current State Analysis

**Problems Identified:**

1. **High Coupling** (See "Architecture" section above)
   - Description: Components X and Y are tightly coupled
   - Location: `src/x.ts:45`, referenced in design doc's Component Structure
```

### Updating Existing Sections

After refactoring is complete, update relevant sections:

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

**Refactoring History:**
- 2026-02-20: Extracted SessionManager from LoginService (See Refactoring Plan below)
```

## Version Control Best Practices

### Commit Strategy

When adding a refactoring plan:

```bash
git add .sdd/specification/{feature-name}_design.md
git commit -m "[add] リファクタリング計画を {feature-name}_design.md に追加

- 現状分析: {brief summary}
- 戦略: {approach}
- フェーズ: {number of phases}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Tracking Changes

Use comments to track when refactoring plans are updated:

```markdown
## Refactoring Plan

> **Last Updated:** 2026-02-20
> **Status:** In Progress (Phase 2 of 4)
> **Owner:** @alice

### Changelog

- **2026-02-20**: Phase 1 completed, updated metrics
- **2026-02-15**: Initial plan created
```

## File Naming Conventions

**IMPORTANT:** Follow the established naming conventions:

| Directory | File Type | Naming Pattern |
|:--|:--|:--|
| `requirement/` | PRD | `{feature-name}.md` (no suffix) |
| `specification/` | Spec | `{feature-name}_spec.md` (`_spec` suffix required) |
| `specification/` | Design | `{feature-name}_design.md` (`_design` suffix required) |

**Examples:**

- ✅ `.sdd/specification/auth_design.md`
- ❌ `.sdd/specification/auth-design.md` (wrong separator)
- ❌ `.sdd/specification/auth_refactor.md` (separate file not recommended)

## Hierarchical Structure Support

### Flat Structure

```
.sdd/
├── requirement/
│   └── auth.md
└── specification/
    ├── auth_spec.md
    └── auth_design.md ← Add Refactoring Plan here
```

### Hierarchical Structure (Parent Feature)

```
.sdd/
├── requirement/
│   └── auth/
│       └── index.md
└── specification/
    └── auth/
        ├── index_spec.md
        └── index_design.md ← Add Refactoring Plan here
```

### Hierarchical Structure (Child Feature)

```
.sdd/
├── requirement/
│   └── auth/
│       ├── index.md (parent PRD)
│       └── login.md (child PRD)
└── specification/
    └── auth/
        ├── index_design.md (parent design)
        └── login_design.md ← Add Refactoring Plan here (child design)
```

## Multi-Feature Refactoring

When refactoring affects multiple features:

### Option 1: Add to Each Feature's Design Doc

If refactoring affects features A and B:

1. Add Refactoring Plan to `feature-a_design.md`
2. Add cross-reference in `feature-b_design.md`:

```markdown
## Related Refactoring

This feature is affected by refactoring work documented in:
- `feature-a_design.md` - Refactoring Plan section
```

### Option 2: Create Parent Feature

If refactoring is large enough:

1. Create parent feature (e.g., `auth/`)
2. Add Refactoring Plan to `auth/index_design.md`
3. Reference from child features

## Post-Refactoring Cleanup

After refactoring is complete:

1. **Update Refactoring Plan section** with "Completed" status
2. **Archive old implementation notes** (move to end or remove)
3. **Update main sections** to reflect new architecture
4. **Clean up task logs** (`task/` directory) after implementation

**Example:**

```markdown
## Refactoring Plan

> **Status:** ✅ Completed on 2026-03-01
> **Original Issue:** High coupling between auth and session modules
> **Result:** Successfully decoupled, test coverage increased from 45% to 85%

<details>
<summary>View Original Plan (Archived)</summary>

### Purpose and Background
...

</details>
```

## References

- See `templates/${SDD_LANG}/refactor-plan-section.md` for full template
- See `references/refactor-patterns.md` for refactoring techniques
- See AI-SDD-PRINCIPLES.md for document structure guidelines

---

**Last Updated:** 2026-02-15
**Maintained by:** AI-SDD plan-refactor skill
