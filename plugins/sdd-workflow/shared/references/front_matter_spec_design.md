# Front Matter Reference — Spec / Design

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

### Spec (`type: "spec"`)

| Field        | Valid Values / Pattern                      | Notes                                  |
|:-------------|:--------------------------------------------|:---------------------------------------|
| `id`         | `"spec-{name}"`                             | Hierarchical: `"spec-{parent}-{name}"` |
| `type`       | `"spec"`                                    |                                        |
| `status`     | `draft`, `review`, `approved`, `deprecated` |                                        |
| `sdd-phase`  | `"specify"`                                 | Always `"specify"`                     |
| `priority`   | `critical`, `high`, `medium`, `low`         | Inherit from PRD if available          |
| `risk`       | `high`, `medium`, `low`                     | Inherit from PRD if available          |
| `depends-on` | `["prd-*"]`                                 | References PRD                         |

### Design (`type: "design"`)

| Field         | Valid Values / Pattern                          | Notes                                    |
|:--------------|:------------------------------------------------|:-----------------------------------------|
| `id`          | `"design-{name}"`                               | Hierarchical: `"design-{parent}-{name}"` |
| `type`        | `"design"`                                      |                                          |
| `status`      | `draft`, `review`, `approved`, `deprecated`     |                                          |
| `sdd-phase`   | `"plan"`                                        | Always `"plan"`                          |
| `impl-status` | `not-implemented`, `in-progress`, `implemented` | Design-specific field                    |
| `priority`    | `critical`, `high`, `medium`, `low`             | Inherit from spec                        |
| `risk`        | `high`, `medium`, `low`                         | Inherit from spec                        |
| `depends-on`  | `["spec-*"]`                                    | References spec                          |

## Dependency Direction Rules

Dependencies (`depends-on`) point **upstream only** — toward higher-level documents. A document never references its
downstream documents.

```
prd ← spec (depends-on: ["prd-*"]) ← design (depends-on: ["spec-*"])
```

- **Spec**: Depends on PRD (`"prd-*"`)
- **Design**: Depends on spec (`"spec-*"`)

## Validation Checklist

### Common Checks (All Documents)

| Check Item                  | Description                                                                                      | Importance |
|:----------------------------|:-------------------------------------------------------------------------------------------------|:-----------|
| **`id` format**             | Matches expected pattern for type (`spec-*`, `design-*`)                                         | Medium     |
| **`type` correctness**      | Matches document location (`"spec"`/`"design"` for `specification/`)                             | Medium     |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                     | High       |
| **`depends-on` direction**  | Dependencies point upstream only (spec→prd, design→spec)                                         | High       |
| **`status` validity**       | Value is one of the allowed values for the document type                                         | Low        |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                             | High       |

### Type-Specific Checks

| Document Type | Additional Check            | Description                         | Importance |
|:--------------|:----------------------------|:------------------------------------|:-----------|
| Spec          | **`sdd-phase` correctness** | Must be `"specify"`                 | Low        |
| Design        | **`sdd-phase` correctness** | Must be `"plan"`                    | Low        |
| Design        | **`impl-status` accuracy**  | Matches actual implementation state | Medium     |

### Cross-Reference Checks

| Check Item                 | Description                                                                | Importance |
|:---------------------------|:---------------------------------------------------------------------------|:-----------|
| **`status` consistency**   | Downstream documents should not be `approved` if upstream is still `draft` | Medium     |
| **`depends-on` integrity** | All referenced IDs exist in actual documents                               | High       |
| **Status propagation**     | Changes in upstream status may require downstream review                   | Medium     |

## Status Transition Rules

### Spec / Design

```
draft → review → approved → deprecated
```

### Design `impl-status` Transitions

```
not-implemented → in-progress → implemented
```

## Missing Front Matter Policy

- Documents without front matter remain valid (backward compatibility).
- If front matter is absent, note in reports: "Front matter not found. Consider adding YAML front matter for structured
  metadata."
- Do **not** treat missing front matter as a violation.
- When generating new documents, always include front matter.
- When updating existing documents that lack front matter, do not add it unless explicitly requested.
