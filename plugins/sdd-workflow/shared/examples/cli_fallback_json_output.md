# CLI-Fallback JSON Output Format

This document defines the JSON output format for CLI-fallback skills (skills that emulate CLI behavior when `sdd-cli` is not available).

## Overview

CLI-fallback skills output JSON to stdout in the same format as the CLI, with additional fields for tracking execution status.

**Key principles**:

1. **CLI compatibility**: `search_results` and `lint_results` match CLI output schemas
2. **Status tracking**: Additional fields (`generated_file`, `status`) indicate execution state
3. **Non-interactive**: All output is machine-readable JSON (no user prompts)

---

## Common JSON Structure

All CLI-fallback skills output the following top-level structure:

```json
{
  "search_results": {
    "results": [...]
  },
  "lint_results": {
    "issues": [...]
  },
  "generated_file": "...",
  "generated_files": [...],
  "validated_files": [...],
  "status": "success|error"
}
```

**Field descriptions**:

| Field               | Type     | Required | Description                                                |
|:--------------------|:---------|:---------|:-----------------------------------------------------------|
| `search_results`    | Object   | Yes      | Document metadata (same as CLI `search` output)            |
| `lint_results`      | Object   | Yes      | Structural validation results (same as CLI `lint` output)  |
| `generated_file`    | String   | No       | Absolute path to single generated file (PRD)               |
| `generated_files`   | String[] | No       | Absolute paths to multiple generated files (Spec + Design) |
| `validated_files`   | String[] | No       | Absolute paths to validated files (Constitution)           |
| `status`            | String   | Yes      | Execution status: `"success"` or `"error"`                 |

**Reference**:

- `search_results` schema: See `cli_integration_guide.md` > "search Output Schema"
- `lint_results` schema: See `cli_integration_guide.md` > "lint Output Schema"

---

## PRD Generation Output (generate-prd-cli-fallback)

### JSON Schema

```json
{
  "search_results": {
    "results": [
      {
        "file_path": "{absolute-path-to-generated-prd}",
        "file_type": "prd",
        "title": "{Feature Title from YAML}",
        "feature_id": "{feature-name}",
        "id": "{id from YAML (prd-{feature-name})}",
        "status": "{status from YAML}",
        "tags": ["{tag1}", "{tag2}"],
        "category": "{category from YAML}"
      }
    ]
  },
  "lint_results": {
    "issues": []
  },
  "generated_file": "{absolute-path-to-generated-prd}",
  "status": "success"
}
```

### Field Mapping

| Placeholder                       | Source                                      | Example                                  |
|:----------------------------------|:--------------------------------------------|:-----------------------------------------|
| `{absolute-path-to-generated-prd}`| Full path to saved PRD file                 | `/path/.sdd/requirement/user-login.md`   |
| `{Feature Title from YAML}`       | `title` field from YAML front matter        | `"User Login Feature"`                   |
| `{feature-name}`                  | Extracted feature identifier                | `"user-login"`                           |
| `{id from YAML}`                  | `id` field from YAML front matter           | `"prd-user-login"`                       |
| `{status from YAML}`              | `status` field from YAML front matter       | `"draft"`                                |
| `{tag1}`, `{tag2}`                | `tags` array from YAML front matter         | `["auth", "security"]`                   |
| `{category from YAML}`            | `category` field from YAML front matter     | `"authentication"`                       |

### Example Output

```json
{
  "search_results": {
    "results": [
      {
        "file_path": "/Users/user/project/.sdd/requirement/user-login.md",
        "file_type": "prd",
        "title": "User Login Feature",
        "feature_id": "user-login",
        "id": "prd-user-login",
        "status": "draft",
        "tags": ["auth", "security"],
        "category": "authentication"
      }
    ]
  },
  "lint_results": {
    "issues": []
  },
  "generated_file": "/Users/user/project/.sdd/requirement/user-login.md",
  "status": "success"
}
```

**Note**: `lint_results.issues` is always empty for CLI-fallback (no automated linting).

---

## Spec/Design Generation Output (generate-spec-cli-fallback)

### JSON Schema

```json
{
  "search_results": {
    "results": [
      {
        "file_path": "{absolute-path-to-generated-spec}",
        "file_type": "spec",
        "title": "{Spec Title from YAML}",
        "feature_id": "{feature-name}",
        "id": "{id from YAML (spec-{feature-name})}",
        "status": "{status from YAML}",
        "tags": ["{tag1}", "{tag2}"],
        "category": "{category from YAML}"
      },
      {
        "file_path": "{absolute-path-to-generated-design}",
        "file_type": "design",
        "title": "{Design Title from YAML}",
        "feature_id": "{feature-name}",
        "id": "{id from YAML (design-{feature-name})}",
        "status": "{status from YAML}",
        "tags": ["{tag1}", "{tag2}"],
        "category": "{category from YAML}"
      }
    ]
  },
  "lint_results": {
    "issues": [
      {
        "severity": "error|warning|info",
        "rule": "duplicate-id|unresolved-dependency|broken-link|yaml-validation|cross-reference",
        "file_path": "{file-path-with-issue}",
        "line": 0,
        "column": 0,
        "message": "{issue-description}",
        "details": {
          "field": "{field-name}",
          "value": "{problematic-value}"
        }
      }
    ]
  },
  "generated_files": [
    "{absolute-path-to-generated-spec}",
    "{absolute-path-to-generated-design}"
  ],
  "status": "success"
}
```

### Field Mapping

Same as PRD generation, with additional:

| Placeholder                         | Source                             | Example                                         |
|:------------------------------------|:-----------------------------------|:------------------------------------------------|
| `{absolute-path-to-generated-spec}` | Full path to saved spec file       | `/path/.sdd/specification/user-login_spec.md`   |
| `{absolute-path-to-generated-design}`| Full path to saved design file    | `/path/.sdd/specification/user-login_design.md` |

### Example Output

```json
{
  "search_results": {
    "results": [
      {
        "file_path": "/Users/user/project/.sdd/specification/user-login_spec.md",
        "file_type": "spec",
        "title": "User Login Specification",
        "feature_id": "user-login",
        "id": "spec-user-login",
        "status": "draft",
        "tags": ["auth"],
        "category": "authentication"
      },
      {
        "file_path": "/Users/user/project/.sdd/specification/user-login_design.md",
        "file_type": "design",
        "title": "User Login Design",
        "feature_id": "user-login",
        "id": "design-user-login",
        "status": "draft",
        "tags": ["auth"],
        "category": "authentication"
      }
    ]
  },
  "lint_results": {
    "issues": [
      {
        "severity": "error",
        "rule": "duplicate-id",
        "file_path": "/Users/user/project/.sdd/specification/legacy/user_spec.md",
        "line": 5,
        "column": 0,
        "message": "Duplicate ID 'spec-user-auth' found",
        "details": {
          "field": "id",
          "duplicate_id": "spec-user-auth",
          "other_files": ["/Users/user/project/.sdd/specification/auth/user_spec.md"]
        }
      }
    ]
  },
  "generated_files": [
    "/Users/user/project/.sdd/specification/user-login_spec.md",
    "/Users/user/project/.sdd/specification/user-login_design.md"
  ],
  "status": "success"
}
```

**Note**: `lint_results.issues` contains results from Manual Structural Verification.

---

## Constitution Validation Output (constitution-cli-fallback)

### JSON Schema

```json
{
  "search_results": {
    "results": [
      {
        "file_path": "{absolute-path-to-validated-file}",
        "file_type": "prd|spec|design|task|implementation-log",
        "title": "{Title from YAML}",
        "feature_id": "{feature-name}",
        "id": "{id from YAML}",
        "status": "{status from YAML}",
        "tags": ["{tag1}", "{tag2}"],
        "category": "{category from YAML}"
      }
    ]
  },
  "lint_results": {
    "issues": [
      {
        "severity": "error|warning|info",
        "rule": "circular-dependency|broken-link|duplicate-id|orphan-reference|principle-compliance",
        "file_path": "{file-path-with-issue}",
        "line": 0,
        "column": 0,
        "message": "{issue-description}",
        "details": {
          "field": "{field-name}",
          "value": "{problematic-value}"
        }
      }
    ]
  },
  "validated_files": [
    "{absolute-path-to-validated-file-1}",
    "{absolute-path-to-validated-file-2}"
  ],
  "status": "success"
}
```

### Example Output

```json
{
  "search_results": {
    "results": [
      {
        "file_path": "/Users/user/project/.sdd/CONSTITUTION.md",
        "file_type": "constitution",
        "title": "Project Constitution",
        "id": "constitution-v1",
        "status": "active"
      }
    ]
  },
  "lint_results": {
    "issues": [
      {
        "severity": "error",
        "rule": "circular-dependency",
        "file_path": "/Users/user/project/.sdd/specification/auth/login_design.md",
        "line": 0,
        "column": 0,
        "message": "Circular dependency detected: design-auth → design-database → design-auth",
        "details": {
          "field": "depends-on",
          "cycle": ["design-auth", "design-database", "design-auth"]
        }
      },
      {
        "severity": "warning",
        "rule": "broken-link",
        "file_path": "/Users/user/project/.sdd/requirement/auth.md",
        "line": 15,
        "column": 0,
        "message": "Broken internal link: ../old-api.md does not exist",
        "details": {
          "field": "link",
          "target": "../old-api.md"
        }
      }
    ]
  },
  "validated_files": [
    "/Users/user/project/.sdd/CONSTITUTION.md",
    "/Users/user/project/.sdd/requirement/auth.md",
    "/Users/user/project/.sdd/specification/auth/login_spec.md",
    "/Users/user/project/.sdd/specification/auth/login_design.md"
  ],
  "status": "success"
}
```

---

## Output Method (Bash)

Use Bash tool to output JSON to stdout:

```bash
cat << 'EOF'
{
  "search_results": { ... },
  "lint_results": { ... },
  "generated_file": "...",
  "status": "success"
}
EOF
```

**Important**:

- Use heredoc with single quotes (`'EOF'`) to prevent variable expansion
- Replace all placeholders with actual values from generated/validated files
- Use absolute paths (e.g., `${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/...`)
- Extract values from YAML front matter of generated/validated files
- Include all structural validation issues in `lint_results.issues`
- If no issues found, use empty array `"issues": []`

---

## Error Handling

If an error occurs during execution, output:

```json
{
  "search_results": {
    "results": []
  },
  "lint_results": {
    "issues": []
  },
  "status": "error",
  "error": {
    "message": "{error-description}",
    "details": "{additional-context}"
  }
}
```

**Example**:

```json
{
  "search_results": {
    "results": []
  },
  "lint_results": {
    "issues": []
  },
  "status": "error",
  "error": {
    "message": "Failed to create PRD file",
    "details": "Permission denied: /path/.sdd/requirement/feature.md"
  }
}
```
