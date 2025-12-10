---
description: "Clean up task/ directory after implementation completion, integrating important design decisions into *_design.md before deletion"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Task Cleanup - Task Log Cleanup

Organizes documents under `.sdd/task/`, integrating important design decisions into `.sdd/specification/*_design.md`
before deletion.

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for cleanup.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value         | Description                  |
|:-------------------------|:----------------------|:-----------------------------|
| `SDD_ROOT`          | `.sdd`                | Root directory               |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`    | PRD/Requirements directory   |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification`  | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`           | Task log directory           |

**Path Resolution Priority:**
1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or configuration file exists.

### Document Persistence Rules (Reference)

| Path                        | Persistence    | Management Rules                                                                                  |
|:----------------------------|:---------------|:--------------------------------------------------------------------------------------------------|
| `specification/*_design.md` | **Persistent** | Describe technical design, architecture, rationale for technology selection                       |
| `task/`                     | **Temporary**  | **Delete** after implementation complete. Integrate important design decisions into `*_design.md` |

## Input

$ARGUMENTS

### Input Examples

```
/task_cleanup TICKET-123
/task_cleanup feature/task-management
/task_cleanup  # Without arguments, targets entire task/
```

## Processing Flow

### 1. Identify Target Directory

```
With argument → Target .sdd/task/{argument}/
Without argument → Target entire .sdd/task/
```

### 2. Check Target Files

```bash
# Get file list in target directory
ls -la .sdd/task/{target}/

# Check last update date for each file
git log -1 --format="%ci" -- <file_path>
```

### 3. Analyze and Classify Content

Review content of each file and classify as follows:

**Content to Integrate (→ `*_design.md`)**:

| Category                           | Examples                                                                  |
|:-----------------------------------|:--------------------------------------------------------------------------|
| **Design decisions and rationale** | "Reason for choosing Redis: ...", "Reason for adopting this pattern: ..." |
| **Alternative evaluation results** | "Comparison of Option A vs Option B", "Rejected alternatives and reasons" |
| **Technical tips and know-how**    | Discoveries during implementation, performance improvement points         |
| **Troubleshooting information**    | Problems encountered and solutions                                        |
| **Reusable patterns**              | Code patterns or design patterns usable in other features                 |

**Content Safe to Delete (No Migration Needed)**:

| Category                          | Examples                                           |
|:----------------------------------|:---------------------------------------------------|
| **Work progress notes**           | "Implementing X", "Y completed"                    |
| **Temporary investigation logs**  | Diary-like content, trial and error records        |
| **Specific implementation steps** | Detailed procedures already reflected in code      |
| **Task lists**                    | Lists of completed tasks                           |
| **Date-dependent information**    | Information dependent on specific periods or dates |

### 4. Determine Integration Target

When there is information to integrate, determine appropriate integration target:

```
1. Find existing *_design.md most related to content
2. If no appropriate existing file:
   - If related *_spec.md exists → Create new corresponding *_design.md
   - If no related *_spec.md → Skip integration (delete information)
```

### 5. Integrate Information

When performing integration:

- Naturally integrate into existing sections or add new sections
- Do not document source file name (don't leave history)
- Format to match technical design document format

### 6. Delete Files/Directories

```bash
# Delete files
git rm .sdd/task/{target}/{file}

# Delete entire directory (after all files processed)
git rm -r .sdd/task/{target}/
```

### 7. Commit

```bash
# Commit integration and deletion together
git commit -m "[docs] Clean up task/{target}

- Integrate design decisions into {design.md}
- Delete temporary task logs"
```

## Output Format

```markdown
## task/ Cleanup Confirmation

### Target Directory

`.sdd/task/{target}/`

### File List

| File | Last Updated | Status |
|:---|:---|:---|
| {filename} | YYYY-MM-DD | To Integrate / To Delete |

### Content to Integrate (→ `*_design.md`)

- [ ] **{Design Decision 1}**: {Summary}
    - Integration Target: `.sdd/specification/{name}_design.md`
    - Target Section: Design Decisions / Technology Stack / Other
- [ ] **{Design Decision 2}**: {Summary}
    - Integration Target: ...

### Deletable Content

- `{file1}`: Temporary investigation log
- `{file2}`: Work progress notes
- `{file3}`: Completed task list

### Recommended Actions

1. Add {design decision} to {section} in `{design.md}`
2. Delete `task/{target}/`
3. Commit

### Confirmation Items

- [ ] Have all design decisions to integrate been identified?
- [ ] Does deletable content contain no important information?
- [ ] Is consistency with integration target document maintained?
```

## Notes

### Cases Requiring Careful Judgment

- **Implementation not complete**: Keep task/
- **Integration target unclear**: Confirm with user
- **Information spanning multiple features**: Integrate into most related document

### Deletion Principles

- **Don't leave history**: Don't add notations like "migrated from ..." during migration
- **Minimal migration**: Migrate only truly valuable information
- **Avoid duplication**: Don't migrate content already documented in `*_design.md`
