---
name: task-cleanup
description: "Clean up task/ directory after implementation completion, integrating important design decisions into *_design.md before deletion"
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Task Cleanup - Task Log Cleanup

Organizes documents under `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/`, integrating important design decisions into `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/*_design.md`
before deletion.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Document Persistence Rules (Reference)

| Path                        | Persistence    | Management Rules                                                                                  |
|:----------------------------|:---------------|:--------------------------------------------------------------------------------------------------|
| `specification/*_design.md` | **Persistent** | Describe technical design, architecture, rationale for technology selection                       |
| `task/`                     | **Temporary**  | **Delete** after implementation complete. Integrate important design decisions into `*_design.md` |

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

| Argument | Required | Description |
|:--|:--|:--|
| `ticket-number` | - | Target ticket number or path. Targets entire task/ if omitted |

### Input Examples

```
/task-cleanup TICKET-123
/task-cleanup feature/task-management
/task-cleanup  # Without arguments, targets entire task/
```

### Scope Confirmation for No-Argument Execution

**When executed without arguments, display the contents of the target directory and ask for user confirmation before starting the process.**

**Reference**: `examples/scope_confirmation.md`

Replace placeholders with actual directory/file names, types, dates, and counts.

**Post-confirmation behavior**:
- User approves -> Execute cleanup on entire task/
- User cancels or specifies a particular directory -> Re-execute with the specified scope

## Processing Flow

### 1. Identify Target Directory

```
With argument -> Target ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{argument}/
Without argument -> Target entire ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/
```

### 2. Check Target Files

```bash
# Get file list in target directory
ls -la ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/

# Check last update date for each file
git log -1 --format="%ci" -- <file_path>
```

### 3. Analyze and Classify Content

Review content of each file and classify as follows:

**Content to Integrate (-> `*_design.md`)**:

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
   - If related *_spec.md exists -> Create new corresponding *_design.md
   - If no related *_spec.md -> Skip integration (delete information)
```

### 5. Integrate Information

When performing integration:

- Naturally integrate into existing sections or add new sections
- Do not document source file name (don't leave history)
- Format to match technical design document format

### 6. Delete Files/Directories

```bash
# Delete files
git rm ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/{file}

# Delete entire directory (after all files processed)
git rm -r ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/
```

## Output

Use the `templates/${SDD_LANG:-en}/cleanup_output.md` template for output formatting.

## Notes

### Cases Requiring Careful Judgment

- **Implementation not complete**: Keep task/
- **Integration target unclear**: Confirm with user
- **Information spanning multiple features**: Integrate into most related document

### Deletion Principles

- **Don't leave history**: Don't add notations like "migrated from ..." during migration
- **Minimal migration**: Migrate only truly valuable information
- **Avoid duplication**: Don't migrate content already documented in `*_design.md`
