# CLI Integration Guide

## Overview

The `sdd-cli` command provides structural validation and document discovery for AI-SDD projects.
When `SDD_CLI_AVAILABLE=true`, skills should delegate structural/mechanical checks to the CLI
and focus LLM effort on semantic analysis.

## Responsibility Split

| Responsibility | Without CLI (LLM) | With CLI |
|:---|:---|:---|
| File discovery | Glob/Grep patterns | `sdd-cli search` |
| Structure validation | Manual pattern matching | `sdd-cli lint --json` |
| Front matter parsing | Read + manual extraction | `sdd-cli lint --json` |
| Dependency chain | Manual traversal | `sdd-cli lint --json` |
| Semantic analysis | LLM (full) | LLM (focused) |
| Quality review | LLM (full) | LLM (full) |

## CLI Commands

### `sdd-cli search`

Search for SDD documents by various criteria.

```bash
# Search all documents
sdd-cli search --format json

# Search by directory
sdd-cli search --dir specification --format json
sdd-cli search --dir requirement --format json

# Search by feature ID
sdd-cli search --feature-id <name> --format json
sdd-cli search --feature-id <name> --dir specification --format json
```

**JSON Output Schema**:

```json
{
  "documents": [
    {
      "path": "relative/path/to/file.md",
      "type": "spec|design|prd|task|implementation-log",
      "id": "spec-feature-name",
      "title": "Document Title",
      "status": "draft|review|approved|implemented",
      "depends_on": ["prd-feature-name"],
      "front_matter": { ... }
    }
  ],
  "total": 5
}
```

### `sdd-cli lint`

Validate document structure, front matter, and cross-references.

```bash
# Lint all documents
sdd-cli lint --json

# Lint specific file
sdd-cli lint --file path/to/file.md --json

# Lint specific directory
sdd-cli lint --dir specification --json
```

**JSON Output Schema**:

```json
{
  "results": [
    {
      "file": "relative/path/to/file.md",
      "valid": true,
      "errors": [],
      "warnings": [
        {
          "code": "W001",
          "message": "Missing optional field: tags",
          "line": 3
        }
      ],
      "front_matter": {
        "id": "design-user-auth",
        "type": "design",
        "status": "approved",
        "depends_on": ["spec-user-auth"]
      },
      "dependencies": {
        "upstream": ["spec-user-auth"],
        "downstream": ["task-user-auth"]
      }
    }
  ],
  "summary": {
    "total": 10,
    "valid": 8,
    "errors": 2,
    "warnings": 5
  }
}
```

## Integration Pattern for Skills

### Step 1: Use CLI for structural validation

```bash
# Get document inventory
sdd-cli search --dir specification --format json

# Validate structure
sdd-cli lint --json
```

### Step 2: Parse CLI JSON output

Extract file paths, front matter, dependency chains from JSON.

### Step 3: Focus LLM on semantic analysis

With structural data from CLI, the LLM can focus on:
- API signature semantic correctness
- Terminology consistency
- Design decision quality
- Requirement coverage completeness

## Environment Variable

| Variable | Description |
|:---|:---|
| `SDD_CLI_AVAILABLE` | Set to `"true"` when sdd-cli is installed and configured |

Check availability:

```bash
if [ "$SDD_CLI_AVAILABLE" = "true" ]; then
  # Use CLI commands
else
  # Fallback to Glob/Grep
fi
```
