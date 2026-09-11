# Front Matter Reference — Spec / Design

YAML front matter is optional metadata added at the top of AI-SDD documents. It enables structured search, filtering,
and cross-reference validation.

## Schema Definition

### Common Fields (All Document Types)

| Field        | Type   | Required | Description                                           |
|:-------------|:-------|:---------|:------------------------------------------------------|
| `id`         | string | Yes      | Unique identifier. Pattern: `"{type}-{feature-name}"` (design: `"design-{ticket-number}"` — see Design section) |
| `title`      | string | Yes      | Human-readable title                                  |
| `type`       | string | Yes      | Document type (see per-type tables below)             |
| `status`     | string | Yes      | Current status                                        |
| `created`    | string | Yes      | Creation date (YYYY-MM-DD)                            |
| `updated`    | string | Yes      | Last update date (YYYY-MM-DD)                         |
| `sdd-version` | string | No      | sdd-workflow plugin version at generation time (e.g., `"5.0.0"`), read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Absent in documents generated before this field was introduced |
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
| `impl-status` | `not-implemented`, `in-progress`, `implemented` | Whether this spec's described behavior is reflected in the implementation. Independent of `status` — see "`status` vs `impl-status`" below |
| `priority`   | `critical`, `high`, `medium`, `low`         | Inherit from PRD if available          |
| `risk`       | `high`, `medium`, `low`                     | Inherit from PRD if available          |
| `depends-on` | `["prd-*"]`                                 | References PRD                         |

##### `status` vs `impl-status`

`status` tracks the document's **approval lifecycle** (`draft` → `review` → `approved` → `deprecated`): has this
spec been reviewed and agreed on as the source of truth? `impl-status` tracks a completely independent axis —
**whether the implementation currently matches what the spec describes**. A spec can be `approved` and still
`not-implemented` (an agreed-upon plan not yet built), or `draft` and `implemented` (a quick implementation whose
spec hasn't been formally reviewed yet). Neither field can be derived from the other.

### Design (`type: "design"`) — temporary draft under `task/{ticket-number}/design-draft.md`

**Note**: Unlike spec, the Design Doc is a temporary draft, not a persistent knowledge asset — see
`AI-SDD-PRINCIPLES.md`'s Document Persistence Rules. Front matter is still included while the draft exists, so
that `spec-reviewer` / `front-matter-reviewer` can validate it before deletion.

| Field         | Valid Values / Pattern                          | Notes                                    |
|:--------------|:------------------------------------------------|:-----------------------------------------|
| `id`          | `"design-{ticket-number}"`                      | Ticket-scoped, not feature-scoped        |
| `type`        | `"design"`                                      |                                          |
| `status`      | `draft`, `review`, `approved`, `deprecated`     |                                          |
| `sdd-phase`   | `"plan"`                                        | Always `"plan"`                          |
| `impl-status` | `not-implemented`, `in-progress`, `implemented` | Same meaning as the spec's `impl-status` field (see Spec section above), scoped to this ticket's draft |
| `priority`    | `critical`, `high`, `medium`, `low`             | Inherit from spec                        |
| `risk`        | `high`, `medium`, `low`                         | Inherit from spec                        |
| `depends-on`  | `["spec-*"]`                                    | References spec                          |
| `ticket`      | string                                          | External ticket reference (e.g., `"TICKET-123"`). Optional -- relevant for a persistent design doc (e.g. a project layout without an `adr/` concept, or one where `task-cleanup` found nothing to integrate into `adr/`). Set it when no `adr` entry exists to carry the link and no ticket tracker was reachable to record completion -- it becomes the only durable link from a ticket back to this feature once `task/{ticket-number}/` is deleted |

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
| **`type` correctness**      | Matches document location (`"spec"` for `specification/`, `"design"` for `task/{ticket-number}/design-draft.md`) | Medium     |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                     | High       |
| **`depends-on` direction**  | Dependencies point upstream only (spec→prd, design→spec)                                         | High       |
| **`status` validity**       | Value is one of the allowed values for the document type                                         | Low        |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                             | High       |

### Type-Specific Checks

| Document Type | Additional Check            | Description                         | Importance |
|:--------------|:----------------------------|:------------------------------------|:-----------|
| Spec          | **`sdd-phase` correctness** | Must be `"specify"`                 | Low        |
| Spec          | **`impl-status` accuracy**  | Matches actual implementation state (see `check-spec`'s Critical/Info/Warning branching) | Medium |
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

### Spec `impl-status` Transitions

```
not-implemented → in-progress → implemented
```

Unlike `status`, which a human reviews and advances, `impl-status` is updated mechanically by the skill that
observes the implementation state:

| Transition                        | Updated By                          | When                                                              |
|:-----------------------------------|:-------------------------------------|:--------------------------------------------------------------------|
| (new spec) → `not-implemented`     | `generate-spec`                      | On spec creation                                                     |
| `not-implemented` → `in-progress`  | `implement`                          | When implementation for the spec starts                             |
| `in-progress` → `implemented`      | `implement`                          | When implementation completes (all tasks done, verification passes) |
| → `implemented` (safety net)       | `task-cleanup`                       | If `implement` did not set it (e.g. work resumed from a different session) |

## Missing Front Matter Policy

- Documents without front matter remain valid (backward compatibility).
- If front matter is absent, note in reports: "Front matter not found. Consider adding YAML front matter for structured
  metadata."
- Do **not** treat missing front matter as a violation.
- When generating new documents, always include front matter.
- When updating existing documents that lack front matter, do not add it unless explicitly requested.
