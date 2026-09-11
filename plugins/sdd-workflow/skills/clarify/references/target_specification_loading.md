# Target Specification Loading

## Design Draft (Same Path in Both Structures)

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/design-draft.md (if ticket-number given and file exists)
```

The design draft is ticket-scoped with a fixed filename, so its path does not vary with the spec's
flat/hierarchical structure. It is also a **temporary** document, deleted once implementation completes:
treat it as an optional input, and when it is absent (or `ticket-number` was not supplied) continue the
clarity analysis with the PRD, the abstract spec, and any v4.x persistent design doc listed below.

## Upstream Documents — Flat Structure

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md (PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md (if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md (v4.x persistent design doc, if exists)
```

## Upstream Documents — Hierarchical Structure (when `feature-name` contains `/`)

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md (parent feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md (parent feature v4.x persistent design doc, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md (child feature v4.x persistent design doc, if exists)
```

The `*_design.md` paths above are the **v4.x persistent design doc**. They are resolved from `feature-name`,
not from `ticket-number`, so they are consulted even when `ticket-number` was omitted. See the
"v4.x persistent design docs" paragraph in `SKILL.md` § 1 for how to treat them (supplementary input,
absence normal, never a write target).
