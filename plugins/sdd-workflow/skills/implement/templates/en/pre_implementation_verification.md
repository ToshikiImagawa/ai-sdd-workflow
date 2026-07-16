# Pre-Implementation Verification

## Load and Verify Documents

```
1. Load task breakdown: ${SDD_TASK_PATH}/{ticket}/tasks.md
2. Load design document: ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_design.md
3. Load abstract spec: ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_spec.md
4. Load PRD (if exists): ${SDD_REQUIREMENT_PATH}/[{path}/]{feature}.md
```

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)
