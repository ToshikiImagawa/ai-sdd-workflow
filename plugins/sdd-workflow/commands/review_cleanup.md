---
name: review_cleanup
description: "Clean up review/ directory after implementation completion, integrating important design decisions into *_design.md before deletion"
---

# Review Cleanup - Review Document Cleanup

Organizes documents under `.docs/review/`, integrating important design decisions into `.docs/specification/*_design.md`
before deletion.

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for cleanup.

### Document Persistence Rules (Reference)

| Path                        | Persistence    | Management Rules                                                                                  |
|:----------------------------|:---------------|:--------------------------------------------------------------------------------------------------|
| `specification/*_design.md` | **Persistent** | Describe technical design, architecture, rationale for technology selection                       |
| `review/`                   | **Temporary**  | **Delete** after implementation complete. Integrate important design decisions into `*_design.md` |

## Input

$ARGUMENTS

### Input Examples

```
/review_cleanup TICKET-123
/review_cleanup feature/task-management
/review_cleanup  # Without arguments, targets entire review/
```

## Processing Flow

### 1. Identify Target Directory

```
With argument → Target .docs/review/{argument}/
Without argument → Target entire .docs/review/
```

### 2. Check Target Files

```bash
# Get file list in target directory
ls -la .docs/review/{target}/

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
git rm .docs/review/{target}/{file}

# Delete entire directory (after all files processed)
git rm -r .docs/review/{target}/
```

### 7. Commit

```bash
# Commit integration and deletion together
git commit -m "[docs] Clean up review/{target}

- Integrate design decisions into {design.md}
- Delete temporary work logs"
```

## Output Format

```markdown
## review/ Cleanup Confirmation

### Target Directory

`.docs/review/{target}/`

### File List

| File | Last Updated | Status |
|:---|:---|:---|
| {filename} | YYYY-MM-DD | To Integrate / To Delete |

### Content to Integrate (→ `*_design.md`)

- [ ] **{Design Decision 1}**: {Summary}
    - Integration Target: `.docs/specification/{name}_design.md`
    - Target Section: Design Decisions / Technology Stack / Other
- [ ] **{Design Decision 2}**: {Summary}
    - Integration Target: ...

### Deletable Content

- `{file1}`: Temporary investigation log
- `{file2}`: Work progress notes
- `{file3}`: Completed task list

### Recommended Actions

1. Add {design decision} to {section} in `{design.md}`
2. Delete `review/{target}/`
3. Commit

### Confirmation Items

- [ ] Have all design decisions to integrate been identified?
- [ ] Does deletable content contain no important information?
- [ ] Is consistency with integration target document maintained?
```

## Notes

### Cases Requiring Careful Judgment

- **Implementation not complete**: Keep review/
- **Integration target unclear**: Confirm with user
- **Information spanning multiple features**: Integrate into most related document

### Deletion Principles

- **Don't leave history**: Don't add notations like "migrated from ..." during migration
- **Minimal migration**: Migrate only truly valuable information
- **Avoid duplication**: Don't migrate content already documented in `*_design.md`
