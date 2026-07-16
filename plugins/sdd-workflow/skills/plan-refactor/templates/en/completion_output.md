# Completion Output Templates

## Phase 5: Next Steps Summary

```
✅ Refactoring plan completed

**Generated/Updated Files:**
- {spec_path} (if Case B)
- {design_path}

**Refactoring Plan Location:**
{design_path} - "Refactoring Plan" section

**Next Steps:**
1. Review the refactoring plan at: {design_path}
2. Run `/task-breakdown {feature-name}` to break down the refactoring into actionable tasks
3. Execute tasks with `/implement {feature-name}` using TDD approach
```

## Output Format

```
File: {file_path}
Status: {Created/Updated}
Sections Added: Refactoring Plan
```
