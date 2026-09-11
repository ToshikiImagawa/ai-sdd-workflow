# Front Matter Reference

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
| `sdd-version` | string | No      | sdd-workflow plugin version at generation time (e.g., `"5.0.0"`), read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Absent in documents generated before this field was introduced |
| `depends-on` | list   | No       | IDs of upstream documents                             |
| `tags`       | list   | No       | Keywords for search/filtering                         |
| `category`   | string | No       | Feature category                                      |

### Per-Type Fields

#### PRD (`type: "prd"`)

| Field        | Valid Values / Pattern                      | Notes                                 |
|:-------------|:--------------------------------------------|:--------------------------------------|
| `id`         | `"prd-{name}"`                              | Hierarchical: `"prd-{parent}-{name}"` |
| `type`       | `"prd"`                                     |                                       |
| `status`     | `draft`, `review`, `approved`, `deprecated` |                                       |
| `priority`   | `critical`, `high`, `medium`, `low`         | PRD-specific field                    |
| `risk`       | `high`, `medium`, `low`                     | PRD-specific field                    |
| `depends-on` | `["prd-*"]` (parent PRDs only)              |                                       |

#### Spec (`type: "spec"`)

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

#### Design (`type: "design"`) — temporary draft under `task/{ticket-number}/design-draft.md`

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
| `ticket`      | string                                          | External ticket reference (e.g., `"TICKET-123"`). Optional — relevant for a persistent design doc (e.g. a project layout without an `adr/` concept, or one where `task-cleanup` found nothing to integrate into `adr/`). Set it when no `adr` entry exists to carry the link and no ticket tracker was reachable to record completion — it becomes the only durable link from a ticket back to this feature once `task/{ticket-number}/` is deleted |

#### ADR (`type: "adr"`) — persistent decision log under `adr/{feature-name}.md`

| Field            | Valid Values / Pattern              | Notes                                                                  |
|:-----------------|:-------------------------------------|:------------------------------------------------------------------------|
| `id`             | `"adr-{name}"`                       | Hierarchical: `"adr-{parent}-{name}"`                                   |
| `type`           | `"adr"`                              |                                                                          |
| `status`         | `"approved"`                          | ADR entries are recorded only after a decision is made, so this is always `"approved"` at write time — it never transitions through `draft`/`review`. A reversed decision is marked on the **new entry** in the file body (see "Entry-Level vs File-Level Superseding" below), not by rewriting `status` to `deprecated` |
| `sdd-phase`      | `"implement"`                        | Always `"implement"`                                                    |
| `depends-on`     | `["spec-*"]`                         | References the spec whose decisions this entry records                  |
| `ticket`         | string                               | External ticket reference (e.g., `"TICKET-123"`) of the implementation that produced this entry. Optional, but set it when the source `task/{ticket-number}/` had no reachable issue tracker to record completion in — it is the only durable link from a ticket back to this feature once `task/` is deleted |
| `supersedes`     | list of `"adr-*"`                    | IDs of prior decision-log **files** this file replaces as a whole (e.g. a renamed or merged feature). Omit unless a whole file was retired |
| `superseded-by`  | `"adr-*"`                            | ID of the decision-log **file** that replaced this whole file. Absent while the file is still the live log for its feature |

##### Entry-Level vs File-Level Superseding

One `adr/{feature}.md` file holds **many entries** but only **one** front matter block, so the front matter
cannot express "entry X reverses entry Y". The two levels are therefore separate:

| Level          | Where it is recorded                                                    | Use it for                                                              |
|:---------------|:------------------------------------------------------------------------|:------------------------------------------------------------------------|
| **Entry**      | A `Supersedes` item inside the new entry's body (see `AI-SDD-PRINCIPLES.md` § Architecture Decision Record → Entry Format) | One decision reversing an earlier decision in the same file — the normal case |
| **File**       | The `supersedes` / `superseded-by` front matter fields                  | Retiring an entire decision log: the feature was renamed, split, or merged and its whole log now lives in another file |

`adr/` is append-only at both levels: past entries are never rewritten, and a superseded entry gets **no**
back-pointer added to it. The current decision is the **latest** entry; earlier entries are read as history.
A retired file likewise keeps its content and only gains `superseded-by` in its front matter.

#### Task (`type: "task"`)

| Field        | Valid Values / Pattern                             | Notes                                            |
|:-------------|:---------------------------------------------------|:-------------------------------------------------|
| `id`         | `"task-{name}"`                                    | Hierarchical: `"task-{parent}-{name}"`           |
| `type`       | `"task"`                                           |                                                  |
| `status`     | `pending`, `in-progress`, `completed`, `cancelled` |                                                  |
| `sdd-phase`  | `"tasks"`                                          | Always `"tasks"`                                 |
| `ticket`     | string                                             | External ticket reference (e.g., `"TICKET-123"`) |
| `depends-on` | `["design-*"]`                                     | References design doc                            |

#### Implementation Log (`type: "implementation-log"`)

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
prd ← spec (depends-on: ["prd-*"]) ← design (depends-on: ["spec-*"]) ← task (depends-on: ["design-*"])
                                   ← adr (depends-on: ["spec-*"])
                                                                       ← impl-log (depends-on: ["design-*"])
```

- **PRD**: May depend on parent PRDs only (`"prd-*"`)
- **Spec**: Depends on PRD (`"prd-*"`)
- **Design**: Depends on spec (`"spec-*"`)
- **ADR**: Depends on spec (`"spec-*"`). `supersedes` / `superseded-by` are lateral references between ADR
  **files**, not upstream dependencies
- **Task**: Depends on design (`"design-*"`)
- **Implementation Log**: Depends on design (`"design-*"`)

## Validation Checklist

### Common Checks (All Documents)

| Check Item                  | Description                                                                                      | Importance |
|:----------------------------|:-------------------------------------------------------------------------------------------------|:-----------|
| **`id` format**             | Matches expected pattern for type (`prd-*`, `spec-*`, `design-*`, `task-*`, `impl-*`, `adr-*`)   | Medium     |
| **`type` correctness**      | Matches document location (`"prd"` for `requirement/`, `"spec"`/`"design"` for `specification/`, `"adr"` for `adr/`) | Medium |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                     | High       |
| **`depends-on` direction**  | Dependencies point upstream only (spec→prd, design→spec, task→design)                            | High       |
| **`status` validity**       | Value is one of the allowed values for the document type                                         | Low        |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                             | High       |
| **`sdd-version` format**    | If present, must be a semver string (`"{major}.{minor}.{patch}"`). Absent is not a violation (info) | Low        |
| **`sdd-version` generation** | If present, its major must not be lower than the current plugin's major (from `plugin.json`)     | Low        |

### Type-Specific Checks

| Document Type | Additional Check            | Description                                 | Importance |
|:--------------|:----------------------------|:--------------------------------------------|:-----------|
| PRD           | **`priority` validity**     | One of: `critical`, `high`, `medium`, `low` | Low        |
| PRD           | **`risk` validity**         | One of: `high`, `medium`, `low`             | Low        |
| Spec          | **`sdd-phase` correctness** | Must be `"specify"`                         | Low        |
| Spec          | **`impl-status` accuracy**  | Matches actual implementation state (see `check-spec`'s Critical/Info/Warning branching) | Medium |
| Design        | **`sdd-phase` correctness** | Must be `"plan"`                            | Low        |
| Design        | **`impl-status` accuracy**  | Matches actual implementation state         | Medium     |
| Task          | **`sdd-phase` correctness** | Must be `"tasks"`                           | Low        |
| Impl Log      | **`sdd-phase` correctness** | Must be `"implement"`                       | Low        |
| ADR           | **`sdd-phase` correctness** | Must be `"implement"`                       | Low        |
| ADR           | **`supersedes`/`superseded-by` consistency** | File-level only: referenced `adr-*` file ids exist and the reverse pointer is set on the other file. An entry-level reversal must **not** be recorded here — it belongs in the new entry's `Supersedes` item | High |

### Cross-Reference Checks

| Check Item                 | Description                                                                | Importance |
|:---------------------------|:---------------------------------------------------------------------------|:-----------|
| **`status` consistency**   | Downstream documents should not be `approved` if upstream is still `draft` | Medium     |
| **`depends-on` integrity** | All referenced IDs exist in actual documents                               | High       |
| **Status propagation**     | Changes in upstream status may require downstream review                   | Medium     |

## Status Transition Rules

### PRD / Spec / Design

```
draft → review → approved → deprecated
```

### Task

```
pending → in-progress → completed
pending → cancelled
```

### Implementation Log

```
in-progress → completed
```

### ADR

ADR entries are append-only and do not follow the draft/review/approved lifecycle: an entry is written once a
decision is made. Validity is tracked in the file body rather than by rewriting `status`: a later entry carrying
a `Supersedes` item replaces an earlier decision, and the replaced entry's text is never edited. `superseded-by`
in the front matter says something different — that the whole file has been retired in favor of another
decision log.

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
