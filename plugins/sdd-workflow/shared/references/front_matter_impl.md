# Front Matter Reference — Implementation Log

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

### Implementation Log (`type: "implementation-log"`)

| Field         | Valid Values / Pattern     | Notes                                               |
|:--------------|:---------------------------|:----------------------------------------------------|
| `id`          | `"impl-{name}"`            | Hierarchical: `"impl-{parent}-{name}"`              |
| `type`        | `"implementation-log"`     |                                                     |
| `status`      | `in-progress`, `completed` |                                                     |
| `sdd-phase`   | `"implement"`              | Always `"implement"`                                |
| `ticket`      | string                     | External ticket reference                           |
| `completed`   | string                     | Completion date (YYYY-MM-DD). Empty until completed |
| `implementer` | string                     | Name of the implementer                             |
| `depends-on`  | `["design-*"]`             | References design doc                               |

## Dependency Direction Rules

Dependencies (`depends-on`) point **upstream only** — toward higher-level documents. A document never references its
downstream documents.

```
prd ← spec (depends-on: ["prd-*"]) ← design (depends-on: ["spec-*"]) ← impl-log (depends-on: ["design-*"])
```

- **Implementation Log**: Depends on design (`"design-*"`)

## Validation Checklist

### Common Checks (All Documents)

| Check Item                  | Description                                                                                      | Importance |
|:----------------------------|:-------------------------------------------------------------------------------------------------|:-----------|
| **`id` format**             | Matches expected pattern for type (`impl-*`)                                                     | Medium     |
| **`type` correctness**      | Matches document location                                                                        | Medium     |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                     | High       |
| **`depends-on` direction**  | Dependencies point upstream only (impl-log→design)                                               | High       |
| **`status` validity**       | Value is one of the allowed values for the document type                                         | Low        |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                             | High       |

### Implementation Log-Specific Checks

| Check Item                  | Description            | Importance |
|:----------------------------|:-----------------------|:-----------|
| **`sdd-phase` correctness** | Must be `"implement"`  | Low        |

## Status Transition Rules

### Implementation Log

```
in-progress → completed
```

## Missing Front Matter Policy

- Documents without front matter remain valid (backward compatibility).
- If front matter is absent, note in reports: "Front matter not found. Consider adding YAML front matter for structured
  metadata."
- Do **not** treat missing front matter as a violation.
- When generating new documents, always include front matter.
- When updating existing documents that lack front matter, do not add it unless explicitly requested.
