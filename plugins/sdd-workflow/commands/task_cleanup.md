---
description: "Clean up task/ directory after implementation completion, integrating important design decisions into *_design.md before deletion"
argument-hint: "<ticket-number>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Task Cleanup - Task Log Cleanup

Organizes documents under `.sdd/task/`, integrating important design decisions into `.sdd/specification/*_design.md`
before deletion.

## Prerequisites

### Plugin Update Check

**Before execution, check if `.sdd/UPDATE_REQUIRED.md` exists.**

If this file exists, the AI-SDD plugin needs to be updated. Display a warning to the user and prompt them to run the following command:

```
/sdd_init
```

### AI-SDD Principles Document

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `.sdd/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles.

This command follows AI-SDD principles for cleanup.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value        | Description                    |
|:-------------------------|:---------------------|:-------------------------------|
| `SDD_ROOT`               | `.sdd`               | Root directory                 |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | PRD/Requirements directory     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`          | Task log directory             |

**Path Resolution Priority:**

1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or
configuration file exists.

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

### Scope Confirmation for No-Argument Execution

**When executed without arguments, display the contents of the target directory and ask for user confirmation before starting the process.**

```markdown
## Scope Confirmation

No argument was specified, so the following directories/files will be targeted for cleanup:

| Type | Path | Last Modified |
|:--|:--|:--|
| Directory | .sdd/task/{ticket1}/ | YYYY-MM-DD |
| Directory | .sdd/task/{ticket2}/ | YYYY-MM-DD |
| File | .sdd/task/{file1}.md | YYYY-MM-DD |
| ... | ... | ... |

**Total: {n} items**

⚠️ **Warning**: Cleanup involves deletion. Important design decisions will be integrated into `*_design.md`, but content deemed unnecessary for integration will be deleted.

Do you want to proceed with this scope?
- To target a specific directory only, re-run with a ticket number specified
- Example: `/task_cleanup TICKET-123`
```

**Post-confirmation behavior**:
- User approves → Execute cleanup on entire task/
- User cancels or specifies a particular directory → Re-execute with the specified scope

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

## Output

Use the output-templates skill to display cleanup confirmation message.

## Notes

### Cases Requiring Careful Judgment

- **Implementation not complete**: Keep task/
- **Integration target unclear**: Confirm with user
- **Information spanning multiple features**: Integrate into most related document

### Deletion Principles

- **Don't leave history**: Don't add notations like "migrated from ..." during migration
- **Minimal migration**: Migrate only truly valuable information
- **Avoid duplication**: Don't migrate content already documented in `*_design.md`
