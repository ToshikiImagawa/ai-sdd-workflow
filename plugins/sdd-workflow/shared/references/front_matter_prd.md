# Front Matter Reference — PRD

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

### PRD (`type: "prd"`)

| Field        | Valid Values / Pattern                      | Notes                                 |
|:-------------|:--------------------------------------------|:--------------------------------------|
| `id`         | `"prd-{name}"`                              | Hierarchical: `"prd-{parent}-{name}"` |
| `type`       | `"prd"`                                     |                                       |
| `status`     | `draft`, `review`, `approved`, `deprecated` |                                       |
| `priority`   | `critical`, `high`, `medium`, `low`         | PRD-specific field                    |
| `risk`       | `high`, `medium`, `low`                     | PRD-specific field                    |
| `depends-on` | `["prd-*"]` (parent PRDs only)              |                                       |

## Dependency Direction Rules

Dependencies (`depends-on`) point **upstream only** — toward higher-level documents. A document never references its
downstream documents.

- **PRD**: May depend on parent PRDs only (`"prd-*"`)

## Validation Checklist

### Common Checks (All Documents)

| Check Item                  | Description                                                                                      | Importance |
|:----------------------------|:-------------------------------------------------------------------------------------------------|:-----------|
| **`id` format**             | Matches expected pattern for type (`prd-*`)                                                      | Medium     |
| **`type` correctness**      | Matches document location (`"prd"` for `requirement/`)                                           | Medium     |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                     | High       |
| **`depends-on` direction**  | Dependencies point upstream only                                                                 | High       |
| **`status` validity**       | Value is one of the allowed values for the document type                                         | Low        |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                             | High       |

### PRD-Specific Checks

| Check Item                | Description                                 | Importance |
|:--------------------------|:--------------------------------------------|:-----------|
| **`priority` validity**   | One of: `critical`, `high`, `medium`, `low` | Low        |
| **`risk` validity**       | One of: `high`, `medium`, `low`             | Low        |

## Status Transition Rules

### PRD

```
draft → review → approved → deprecated
```

## Missing Front Matter Policy

- Documents without front matter remain valid (backward compatibility).
- If front matter is absent, note in reports: "Front matter not found. Consider adding YAML front matter for structured
  metadata."
- Do **not** treat missing front matter as a violation.
- When generating new documents, always include front matter.
- When updating existing documents that lack front matter, do not add it unless explicitly requested.
