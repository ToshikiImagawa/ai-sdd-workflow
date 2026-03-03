# CLI Integration Guide

This document provides standard patterns for integrating with the `sdd-cli` tool across all AI-SDD workflow skills.

## CLI Availability Detection

The `session-start` hook sets the following environment variables:

| Environment Variable | Description                       | Example Value                                   |
|:---------------------|:----------------------------------|:------------------------------------------------|
| `SDD_CLI_AVAILABLE`  | CLI availability flag             | `"true"` or `"false"`                           |
| `SDD_CLI_COMMAND`    | Full CLI command (when available) | `uvx --from git+https://github.com/... sdd-cli` |

**Usage**:

```bash
if [ "$SDD_CLI_AVAILABLE" = "true" ]; then
    ${SDD_CLI_COMMAND} <subcommand> <options>
fi
```

## Standard CLI Command Patterns

### Document Discovery (sdd-cli search)

**All documents**:

```bash
${SDD_CLI_COMMAND} search --format json 2>&1
```

**Feature-specific search**:

```bash
${SDD_CLI_COMMAND} search --feature-id "${FEATURE_NAME}" --format json 2>&1
```

**Directory filter**:

```bash
${SDD_CLI_COMMAND} search --dir specification --format json 2>&1
${SDD_CLI_COMMAND} search --dir requirement --format json 2>&1
${SDD_CLI_COMMAND} search --dir task --format json 2>&1
```

**Combined filters**:

```bash
${SDD_CLI_COMMAND} search --feature-id "${FEATURE}" --dir specification --format json 2>&1
```

**Keyword search** (for constitution validation, etc.):

```bash
${SDD_CLI_COMMAND} search "CONSTITUTION" --format json 2>&1
${SDD_CLI_COMMAND} search "KEYWORD" --format json 2>&1
```

**Additional options**:

- `--tag TAG`: Filter by tag
- `--limit N`: Limit number of results
- `--quiet`: Suppress progress output

### Structural Validation (sdd-cli lint)

**Basic lint**:

```bash
${SDD_CLI_COMMAND} lint --json 2>&1
```

**With quiet mode**:

```bash
${SDD_CLI_COMMAND} lint --json --quiet 2>&1
```

**With custom root**:

```bash
${SDD_CLI_COMMAND} lint --root ${SDD_ROOT} --json 2>&1
```

### Index Building (sdd-cli index)

Required before first `search` operation:

```bash
${SDD_CLI_COMMAND} index 2>&1
```

**Note**: `search` automatically builds index if missing, but explicit `index` call provides better error reporting.

## JSON Output Schemas

### search Output Schema

```json
{
  "results": [
    {
      "file_path": "/absolute/path/.sdd/requirement/user-login.md",
      "file_type": "prd|spec|design|task|implementation-log",
      "title": "User Login Feature",
      "feature_id": "user-login",
      "id": "prd-user-login",
      "status": "draft",
      "tags": [
        "auth",
        "security"
      ],
      "category": "authentication"
    }
  ]
}
```

**Filtering results by `file_type`**:

- `"prd"`: PRD documents in `requirement/`
- `"spec"`: Abstract specs (`*_spec.md`)
- `"design"`: Technical design docs (`*_design.md`)
- `"task"`: Task breakdown docs
- `"implementation-log"`: Implementation logs

### lint Output Schema

```json
{
  "issues": [
    {
      "severity": "error|warning|info",
      "rule": "duplicate-id|unresolved-dependency|broken-link|...",
      "file_path": "/absolute/path/.sdd/specification/user-login_spec.md",
      "line": 5,
      "column": 10,
      "message": "Dependency target 'prd-user-auth' not found",
      "details": {
        "field": "depends-on",
        "target_id": "prd-user-auth"
      }
    }
  ]
}
```

## CLI Issue Type Mapping

| CLI Issue Type           | Semantic Meaning                    | Typical LLM Replacement    |
|:-------------------------|:------------------------------------|:---------------------------|
| `duplicate-id`           | Two documents have the same ID      | Glob + Grep id scanning    |
| `unresolved-dependency`  | `depends-on` target does not exist  | Dependency chain traversal |
| `broken-link`            | Cross-document reference is invalid | Link validation            |
| `circular-dependency`    | Circular dependency chain detected  | Recursive dependency check |
| `orphan-reference`       | Referenced ID is not used anywhere  | Reverse reference search   |
| `missing-required-field` | Required front matter field missing | Front matter parsing       |
| `invalid-field-value`    | Field value does not match schema   | Value validation           |

## Strategy A/B Pattern Template

### Strategy A: CLI Available

When `SDD_CLI_AVAILABLE=true`, use CLI commands to **replace** LLM operations:

```markdown
#### Strategy A: CLI Available (`SDD_CLI_AVAILABLE=true`)

Use CLI search + lint to discover documents and validate structure, **replacing shell script execution**:

```bash
# Discover documents
${SDD_CLI_COMMAND} search <options> --format json 2>&1

# Structural validation
${SDD_CLI_COMMAND} lint --json 2>&1
```

- **CLI search** replaces: [LLM file scanning operation]
- **CLI lint** covers: [structural checks] — **LLM skips** these

**LLM focuses exclusively on semantic checks** that CLI cannot perform:

- [Semantic check 1]
- [Semantic check 2]
- [Semantic check 3]

**Do NOT execute [shell-script-name]** — CLI search replaces the shell script scan.

```

### Strategy B: Fallback

When `SDD_CLI_AVAILABLE` is not `"true"`, fall back to LLM operations:

```markdown
#### Strategy B: CLI Not Available (Fallback)

Execute [shell-script-name] to scan documents:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/[skill-name]/scripts/[script-name].sh" [args]
```

LLM performs both structural and semantic checks manually using Read, Glob, and Grep tools.

```

## LLM vs CLI Responsibility Division

### CLI Responsibilities (Strategy A)

- **Document discovery**: File path enumeration, flat/hierarchical structure detection
- **Structural validation**: ID uniqueness, dependency chain integrity, link validity
- **Metadata extraction**: File type, feature ID, title, tags (from front matter)

### LLM Responsibilities (Both Strategies)

- **Semantic validation**: API signature match, terminology consistency, principle compliance
- **Content analysis**: Requirement coverage, design decision reasoning, contradiction detection
- **User interaction**: Clarification questions, confirmation prompts, error reporting

### LLM Responsibilities (Strategy A Only)

- **JSON parsing**: Interpret CLI search/lint results
- **Filtering**: Apply business logic to CLI results (e.g., filter by specific criteria)
- **Integration**: Merge CLI structural findings with semantic analysis results

## Error Handling

See `cli_error_handling.md` for detailed error handling patterns.

## Common Integration Patterns

### Pattern 1: Document Discovery + Structural Validation

```bash
# Step 1: Discover documents
SEARCH_RESULT=$(${SDD_CLI_COMMAND} search --feature-id "${FEATURE}" --format json 2>&1)

# Step 2: Validate structure
LINT_RESULT=$(${SDD_CLI_COMMAND} lint --json 2>&1)

# Step 3: LLM parses JSON and focuses on semantic checks
```

### Pattern 2: Targeted Search + Conditional Lint

```bash
# Search for specific document types
DESIGN_DOCS=$(${SDD_CLI_COMMAND} search --feature-id "${FEATURE}" --dir specification --format json 2>&1 | jq '.results[] | select(.file_type == "design")')

# Lint only if documents found
if [ ! -z "$DESIGN_DOCS" ]; then
    ${SDD_CLI_COMMAND} lint --json 2>&1
fi
```

### Pattern 3: Keyword Search for Compliance

```bash
# Find documents mentioning specific keywords
${SDD_CLI_COMMAND} search "CONSTITUTION" --format json 2>&1
${SDD_CLI_COMMAND} search "API" --format json 2>&1
```

## Performance Considerations

- **search with `--limit`**: Limit results when full scan is not needed
- **search with `--dir`**: Filter by directory to reduce search scope
- **lint with `--quiet`**: Suppress progress output for faster execution
- **Caching**: CLI results can be cached within a single skill execution (store in variable, not file)

## Example: Replacing Shell Script with CLI

**Before (Strategy B only)**:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-design-docs.sh" "${FEATURE_NAME}"
```

**After (Strategy A/B)**:

```markdown
#### Strategy A: CLI Available

${SDD_CLI_COMMAND} search --feature-id "${FEATURE_NAME}" --dir specification --format json 2>&1

#### Strategy B: CLI Not Available (Fallback)

bash "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-design-docs.sh" "${FEATURE_NAME}"
```

---

**Last Updated**: 2026-03-03
**Maintained by**: AI-SDD Workflow Plugin