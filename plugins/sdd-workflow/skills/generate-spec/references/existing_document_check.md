# Existing Document Check

## For Flat Structure

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md exist? (PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md already exist?
```

## For Hierarchical Structure (when placing under parent feature)

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md exist? (parent feature PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md exist? (child feature PRD)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md already exist? (parent feature spec)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md already exist? (child feature spec)
```

## Design Doc Draft (ticket-scoped, independent of flat/hierarchical structure)

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket-number}/design-draft.md already exist?
```

## Legacy Persistent Design Doc (v4.x — auxiliary input)

```
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md exist? (flat, v4.x)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md exist? (hierarchical parent, v4.x)
Does ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md exist? (hierarchical child, v4.x)
```

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may still
contain these. They **remain valid** — read them as **supplementary input, and treat their absence as normal**.
When one exists, read it for the technology stack, module structure, and recorded design decisions already in
force, so the new draft does not contradict them. Do not create new ones (new technical design goes to
`${SDD_TASK_PATH}/{ticket-number}/design-draft.md`), and never report an existing one as a naming violation or
propose deleting it; it may stay until its decisions have been migrated to `adr/{feature}.md`.
