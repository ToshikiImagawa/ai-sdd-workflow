# Pre-Implementation Verification

## Load and Verify Documents

```
1. Load task breakdown: ${SDD_TASK_PATH}/{ticket}/tasks.md
2. Load design draft: ${SDD_TASK_PATH}/{ticket}/design-draft.md
3. Load v4.x persistent design doc (if the project has one):
   ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_design.md
4. Load abstract spec: ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}.md or {feature}_spec.md
5. Load PRD (if exists): ${SDD_REQUIREMENT_PATH}/[{path}/]{feature}.md
```

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may
still contain these. They **remain valid** — read them as **supplementary input, and treat their absence as
normal**. Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and
never report an existing one as a naming violation or propose deleting it; it may stay until its decisions
have been migrated to `adr/{feature}.md`. When step 2 finds no `design-draft.md` but step 3 finds such a
file, implement from it — do not prompt for a regenerated draft.

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` suffix optional (`index_spec.md`, `{feature-name}_spec.md`, or no suffix) —
  either form satisfies step 4
- **Under task**: Design draft uses the fixed filename `design-draft.md`, ticket-scoped and independent of
  the spec's flat/hierarchical structure
