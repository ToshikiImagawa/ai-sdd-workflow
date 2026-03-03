---
name: recommend-front-matter
description: "Scan existing AI-SDD documents and recommend YAML front matter additions"
argument-hint: "[--apply]"
version: 3.2.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Recommend Front Matter - Add YAML Metadata to Existing Documents

Scans existing AI-SDD documents (PRD, spec, design, task) and recommends adding YAML front matter for structured metadata.

**Purpose**: Help users add front matter to existing documents created before front matter support was added.

**Note**: Front matter is optional and backward compatible. This skill provides recommendations but does not require adoption.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/front_matter_prd.md` - PRD front matter schema
- `references/front_matter_spec_design.md` - Spec/Design front matter schema
- `references/front_matter_task.md` - Task front matter schema
- `references/front_matter_impl.md` - Implementation Log front matter schema

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

### Options

- `--apply`: Automatically apply recommended front matter to documents (after user confirmation)
    - Without this option: Generate recommendation report only
    - With this option: Apply front matter to files and generate result report

### Input Examples

```
/recommend-front-matter          # Generate recommendation report only
/recommend-front-matter --apply  # Apply front matter after confirmation
```

## Processing Flow

**Optimized Execution Flow**:

### Phase 1: Document Scan

#### Strategy A: CLI Available (`SDD_CLI_AVAILABLE=true`)

Read `shared/references/cli_integration_guide.md` for standard CLI search patterns and JSON output schema.

Use CLI search to scan all AI-SDD documents, **replacing shell script execution**:

```bash
${SDD_CLI_COMMAND} search --format json 2>&1
```

- CLI search returns all documents with `file_path`, `file_type`, `title`, and `feature_id`
- LLM determines front matter presence by reading each document's first few lines (check for `---`)
- **Do NOT execute `scan-documents.sh`** — CLI search replaces the shell script scan
- Build the equivalent scan result structure from CLI search output

#### Strategy B: CLI Not Available (Fallback)

Execute `scan-documents.sh` to scan AI-SDD documents:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/recommend-front-matter/scripts/scan-documents.sh"
```

This script:
1. Loads `.sdd-config.json` to resolve directory paths
2. Scans documents in `${SDD_REQUIREMENT_DIR}`, `${SDD_SPECIFICATION_DIR}`, and `${SDD_TASK_DIR}` directories
3. Detects Front Matter presence (checks for opening/closing `---`)
4. Determines document type from file path and naming convention
5. Extracts title from first `#` heading
6. Generates JSON report (`.sdd/.cache/recommend-front-matter/scan_result.json`)
7. Exports environment variables to `$CLAUDE_ENV_FILE`:
   - `RECOMMEND_FM_CACHE_DIR` - Cache directory
   - `RECOMMEND_FM_SCAN_RESULT` - JSON scan result file path
   - `SDD_LANG` - Language configuration

**Scan Result JSON Schema**:

```json
{
  "scan_timestamp": "2026-02-24T12:00:00Z",
  "total_documents": 15,
  "documents_with_front_matter": 5,
  "documents_without_front_matter": 10,
  "documents": [
    {
      "path": "/absolute/path/.sdd/requirement/user-login.md",
      "relative_path": "requirement/user-login.md",
      "basename": "user-login",
      "type": "prd",
      "has_front_matter": false,
      "title_line": "User Login Feature"
    },
    ...
  ]
}
```

### Phase 2: Claude - Generate Front Matter Recommendations

For each document **without front matter** in the scan result:

#### 1. Read Document Content

Use the Read tool to read the first 100 lines of each document. This provides context for:
- Extracting accurate title
- Inferring tags from headings and content keywords
- Determining category from content structure

#### 2. Infer Common Fields

| Field        | Inference Logic                                                                                                      |
|:-------------|:---------------------------------------------------------------------------------------------------------------------|
| `id`         | Generate from file path and type: `"{type}-{feature-name}"` (hierarchical: `"{type}-{parent}-{feature-name}"`)      |
| `title`      | Extract from first `#` heading (fallback: basename)                                                                  |
| `type`       | Use `type` field from scan result (`prd`, `spec`, `design`, `task`, `implementation-log`)                           |
| `status`     | Default to `"draft"` for new front matter                                                                            |
| `created`    | Use current date `YYYY-MM-DD`                                                                                        |
| `updated`    | Same as `created` for initial front matter                                                                           |
| `depends-on` | Infer from file naming patterns (spec → prd, design → spec, task → design). Empty list if no match found.           |
| `tags`       | Extract from headings and content keywords (max 5 tags). Use lowercase, hyphenated format (e.g., `"user-auth"`).    |
| `category`   | Infer from directory hierarchy or parent feature name. Empty if no clear category.                                   |

**Dependency Inference Logic**:

Follow the dependency direction rules from the type-specific front matter references:

- **PRD** → No dependencies (or parent PRD if hierarchical)
- **Spec** → Search for matching PRD in `${SDD_REQUIREMENT_PATH}` directory:
    - Try exact match: `{basename}.md`
    - Try hierarchical match: `{parent-name}.md`
    - If no match found: Empty list
- **Design** → Search for matching spec in `${SDD_SPECIFICATION_PATH}` directory:
    - Try exact match: `{basename}_spec.md`
    - Try hierarchical match: `{parent-name}_spec.md` or `{parent-name}/index_spec.md`
    - If no match found: Empty list
- **Task** → Search for matching design in `${SDD_SPECIFICATION_PATH}` directory:
    - Try exact match: `{basename}_design.md`
    - Try hierarchical match: `{parent-name}_design.md` or `{parent-name}/index_design.md`
    - If no match found: Empty list
- **Implementation Log** → Same logic as Task

**ID Generation for Hierarchical Structure**:

For hierarchical directory structures (e.g., `specification/auth/user-login_design.md`):
- Extract parent from path: `"auth"`
- Extract feature from basename: `"user-login"`
- Generate ID: `"design-auth-user-login"`

For flat structures (e.g., `specification/user-login_design.md`):
- Generate ID: `"design-user-login"`

#### 3. Infer Type-Specific Fields

Based on the `type` field:

**PRD** (`type: "prd"`):
```yaml
priority: "medium"
risk: "medium"
```

**Spec** (`type: "spec"`):
```yaml
sdd-phase: "specify"
```

**Design** (`type: "design"`):
```yaml
sdd-phase: "plan"
impl-status: "not-implemented"
```

**Task** (`type: "task"`):
```yaml
sdd-phase: "tasks"
ticket: ""
```

**Implementation Log** (`type: "implementation-log"`):
```yaml
sdd-phase: "implement"
ticket: ""
completed: ""
implementer: ""
```

### Phase 3: Generate Recommendation Report

Use the report template at `templates/${SDD_LANG}/recommendation_report.md`.

For each document without front matter:
1. Show current first heading
2. Show recommended YAML front matter block
3. Explain inference logic for each field
4. Provide copy-paste-ready YAML block

**Report Sections**:
1. **Summary**: Total count, with/without front matter count
2. **Recommendations**: One section per document with recommended YAML
3. **Next Steps**: Instructions for applying recommendations (manual or `--apply`)

### Phase 4: Apply Front Matter (if `--apply` option)

**Only execute if `--apply` argument is present.**

#### 1. User Confirmation

Use AskUserQuestion to confirm before modifying files:

**Question**: "以下の {count} 個のファイルに Front Matter を追加します。よろしいですか？" (en: "Add Front Matter to {count} files?")

**Display**:
- List of files to be modified (max 10 files shown, "+ X more" if >10)
- Warning: "この操作はファイルを直接変更します。変更前に Git コミットを推奨します。" (en: "This operation will modify files directly. Git commit recommended before applying.")

**Options**:
- "Yes, apply to all files" (recommended option)
- "No, cancel"

If user cancels → Output recommendation report only and exit.

#### 2. Apply Front Matter to Files

For each document without front matter (after user confirms):

1. **Read current file content** (Read tool)
2. **Generate YAML front matter block**:
   ```yaml
   ---
   id: "{inferred_id}"
   title: "{extracted_title}"
   type: "{type}"
   status: "draft"
   created: "{created_date}"
   updated: "{updated_date}"
   depends-on: [{dependency_ids}]
   tags: [{inferred_tags}]
   category: "{inferred_category}"
   {type_specific_fields}
   ---
   ```
3. **Insert at file beginning** using Edit tool:
   - Add YAML block at the very top
   - Remove leading blank lines from original content if present
   - Ensure one blank line between front matter closing `---` and first heading

**Error Handling**:
- If Edit fails for any file: Record error, continue to next file
- Track success/skip/error counts

#### 3. Post-Apply Verification with CLI Lint (when available)

After applying front matter to all files, verify the results using CLI lint if available:

```bash
if [ "$SDD_CLI_AVAILABLE" = "true" ]; then
    ${SDD_CLI_COMMAND} lint --json 2>&1
fi
```

Check the lint output for the following issue types:

| Issue Type               | Action                                                              |
|:-------------------------|:--------------------------------------------------------------------|
| `duplicate-id`           | Report as error — two documents received the same generated ID      |
| `missing-required-field` | Report as warning — generated front matter may be incomplete        |
| `invalid-field-value`    | Report as warning — inferred value does not match expected format   |
| `unresolved-dependency`  | Report as info — `depends-on` target was not found                  |

Include verification results in the Application Result Report. If any `duplicate-id` errors are found, list the
conflicting files and recommend manual ID adjustment.

**When CLI is not available**: Skip verification and proceed to the result report.

#### 4. Generate Application Result Report

Use the result template at `templates/${SDD_LANG}/application_result.md`.

## Output

### Without `--apply` Option

Generate recommendation report using `templates/${SDD_LANG}/recommendation_report.md`:

1. **Summary section**: Document counts
2. **Recommendations section**: Per-document YAML recommendations with inference explanations
3. **Next Steps**: Instructions for manual or automatic application

### With `--apply` Option

After user confirmation and file updates:

1. **Application result summary**: Success/skip/error counts
2. **Updated file list**: Paths of successfully updated files
3. **Next Steps**: Instructions for reviewing changes and committing

## Important Notes

### Backward Compatibility

- Front matter is **optional** in AI-SDD v3.x
- Documents without front matter remain fully functional
- This skill helps users adopt structured metadata for better tooling support

### Review Before Applying

**Strongly recommend users to**:
1. Review recommendations in the report
2. Commit current state to Git before applying
3. Manually adjust inferred metadata (especially `depends-on`, `tags`, `category`) after applying

### Inference Limitations

The following fields are inferred using pattern matching and may require manual adjustment:

- **`depends-on`**: May miss dependencies if naming conventions differ
- **`tags`**: Basic keyword extraction, may not capture domain-specific concepts
- **`category`**: Inferred from directory structure, may need refinement
- **`priority`/`risk`**: Always default to `"medium"`, should be reviewed

### What This Skill Does NOT Do

- Does **not** validate existing front matter (use `/check-spec --full` for validation)
- Does **not** update outdated front matter (only adds missing front matter)
- Does **not** modify documents that already have front matter
