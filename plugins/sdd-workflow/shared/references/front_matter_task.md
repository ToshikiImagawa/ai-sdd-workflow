# Front Matter Reference — Task

YAML front matter is optional metadata added at the top of AI-SDD documents. It enables structured search, filtering,
and cross-reference validation.

## Schema Definition

### Common Fields (All Document Types)

| Field        | Type   | Required | Description                                           |
|:-------------|:-------|:---------|:------------------------------------------------------|
| `id`         | string | Yes      | Unique identifier. Pattern: `"{type}-{feature-name}"` |
| `title`      | string | Yes      | Human-readable title                                  |
| `type`       | string | Yes      | Document type (see per-type tables below)             |
| `status`     | string | Yes      | Current status                                        |
| `created`    | string | Yes      | Creation date (YYYY-MM-DD)                            |
| `updated`    | string | Yes      | Last update date (YYYY-MM-DD)                         |
| `depends-on` | list   | No       | IDs of upstream documents                             |
| `tags`       | list   | No       | Keywords for search/filtering                         |
| `category`   | string | No       | Feature category                                      |

### Task (`type: "task"`)

| Field        | Valid Values / Pattern                             | Notes                                            |
|:-------------|:---------------------------------------------------|:-------------------------------------------------|
| `id`         | `"task-{name}"`                                    | Hierarchical: `"task-{parent}-{name}"`           |
| `type`       | `"task"`                                           |                                                  |
| `status`     | `pending`, `in-progress`, `completed`, `cancelled` |                                                  |
| `sdd-phase`  | `"tasks"`                                          | Always `"tasks"`                                 |
| `ticket`     | string                                             | External ticket reference (e.g., `"TICKET-123"`) |
| `depends-on` | `["design-*"]`                                     | References design doc                            |

## Dependency Direction Rules

Dependencies (`depends-on`) point **upstream only** — toward higher-level documents. A document never references its
downstream documents.

```
prd ← spec (depends-on: ["prd-*"]) ← design (depends-on: ["spec-*"]) ← task (depends-on: ["design-*"])
```

- **Task**: Depends on design (`"design-*"`)

## Validation Checklist

### Common Checks (All Documents)

| Check Item                  | Description                                                                                      | Importance |
|:----------------------------|:-------------------------------------------------------------------------------------------------|:-----------|
| **`id` format**             | Matches expected pattern for type (`task-*`)                                                     | Medium     |
| **`type` correctness**      | Matches document location                                                                        | Medium     |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                     | High       |
| **`depends-on` direction**  | Dependencies point upstream only (task→design)                                                   | High       |
| **`status` validity**       | Value is one of the allowed values for the document type                                         | Low        |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                             | High       |

### Task-Specific Checks

| Check Item                  | Description         | Importance |
|:----------------------------|:--------------------|:-----------|
| **`sdd-phase` correctness** | Must be `"tasks"`   | Low        |

## Status Transition Rules

### Task

```
pending → in-progress → completed
pending → cancelled
```

## Missing Front Matter Policy

- Documents without front matter remain valid (backward compatibility).
- If front matter is absent, note in reports: "Front matter not found. Consider adding YAML front matter for structured
  metadata."
- Do **not** treat missing front matter as a violation.
- When generating new documents, always include front matter.
- When updating existing documents that lack front matter, do not add it unless explicitly requested.
