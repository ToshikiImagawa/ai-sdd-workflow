# Target Specification Loading

## For Flat Structure

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md (PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md (if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md (if exists)
```

## For Hierarchical Structure (when argument contains `/`)

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md (parent feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md (child feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md (parent feature design, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md (child feature design, if exists)
```
