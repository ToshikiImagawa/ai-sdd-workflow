# Pre-Implementation Verification

## Load and Verify Documents

```
1. Load task breakdown: .sdd/task/{ticket}/tasks.md
2. Load design document: .sdd/specification/[{path}/]{feature}_design.md
3. Load abstract spec: .sdd/specification/[{path}/]{feature}_spec.md
4. Load PRD (if exists): .sdd/requirement/[{path}/]{feature}.md
```

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)
