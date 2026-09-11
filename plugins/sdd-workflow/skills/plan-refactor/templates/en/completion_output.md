# Completion Output Templates

## Phase 5: Next Steps Summary

```
✅ Refactoring plan completed

**Generated/Updated Files:**
- {spec_path} (Case B only — persistent, reverse-engineered spec)
- {design_draft_path} (temporary draft, deleted after implementation)

**Refactoring Plan Location:**
{design_draft_path} - "Refactoring Plan" section

**Reverse-Engineered Analysis (Case B only) — what persists:**
- Carried into {spec_path}: {Public API | Internal Interfaces | Data Model | Behavior and Data Flow |
  Architecture Pattern — list the sections actually written}
- Discarded with the draft, by design: component inventory, directory layout, per-component dependencies,
  internal call sequence, key algorithms, state management internals, test coverage figures. They are
  re-derivable from the code; re-run `/plan-refactor` when they are needed again

**Technical Debt Observations — persistent destinations:**
| Observation | Destination |
|:--|:--|
| {debt item} | {`adr/` entry at cleanup | tracker item {id / to be created} | proposed spec correction} |

Observations still without a destination: {none | list} — assign one before implementation starts, or they are
lost when the draft is deleted.

**Next Steps:**
1. Review the refactoring plan at: {design_draft_path}
2. Create the tracker items for the deferred debt observations listed above
3. Run `/task-breakdown {feature-name} {ticket-number}` to break down the refactoring into actionable tasks
4. Execute tasks with `/implement {feature-name} {ticket-number}` using TDD approach — pass the same
   ticket number, since `tasks.md` and the design draft both live under `task/{ticket-number}/`
5. When implementation completes, run `/task-cleanup {ticket-number}` to append the settled decisions to
   ${SDD_ADR_PATH}/{feature-name}.md — the draft (and this plan) is deleted at that point, so the decision
   log is the only lasting record
```

## Output Format

```
File: {file_path}
Persistence: {Persistent (specification/) | Temporary draft (task/{ticket-number}/)}
Status: {Created/Updated}
Sections Added: Refactoring Plan
```
