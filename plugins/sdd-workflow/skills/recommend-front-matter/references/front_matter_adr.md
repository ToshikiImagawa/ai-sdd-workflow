# Front Matter Reference — ADR

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

### ADR (`type: "adr"`) — persistent decision log under `adr/{feature-name}.md`

| Field            | Valid Values / Pattern              | Notes                                                                  |
|:-----------------|:-------------------------------------|:------------------------------------------------------------------------|
| `id`             | `"adr-{name}"`                       | Hierarchical: `"adr-{parent}-{name}"`                                   |
| `type`           | `"adr"`                              |                                                                          |
| `status`         | `"approved"`                         | A decision log records decisions already made, so this is always `"approved"` at write time — it never passes through `draft`/`review`, and a reversed decision is not marked by rewriting it to `deprecated` |
| `sdd-phase`      | `"implement"`                        | Always `"implement"`                                                    |
| `depends-on`     | `["spec-*"]`                         | References the spec whose decisions this log records                    |
| `ticket`         | string                               | External ticket reference (e.g., `"TICKET-123"`) of the implementation that produced the log's latest entry. Optional, but set it when the source `task/{ticket-number}/` had no reachable issue tracker to record completion in |
| `supersedes`     | list of `"adr-*"`                    | IDs of prior decision-log **files** this file replaces as a whole (e.g. a renamed, split, or merged feature). Omit unless a whole file was retired |
| `superseded-by`  | `"adr-*"`                            | ID of the decision-log **file** that replaced this whole file. Absent while this file is still the live log for its feature |

### Entry-Level vs File-Level Superseding

One `adr/{feature}.md` file holds **many entries** (append-only, appended at the end of the file) but only **one**
front matter block, so the front matter cannot express "entry X reverses entry Y". The two levels are separate:

| Level      | Where it is recorded                                                  | Use it for                                                                       |
|:-----------|:----------------------------------------------------------------------|:---------------------------------------------------------------------------------|
| **Entry**  | A `- **Supersedes**:` item in the new entry's body                    | One decision reversing an earlier decision in the same file — the normal case    |
| **File**   | The `supersedes` / `superseded-by` front matter fields                | Retiring an entire log: the feature was renamed, split, or merged and its whole log now lives in another file |

`adr/` is append-only at both levels: past entries are never rewritten, and a superseded entry gets **no**
back-pointer added to it. The current decision is the **latest** entry; earlier entries are read as history.
A retired file likewise keeps its content and only gains `superseded-by` in its front matter.

An entry-level reversal must never be written into the front matter's `supersedes` / `superseded-by`.

## Dependency Direction Rules

Dependencies (`depends-on`) point **upstream only** — toward higher-level documents. A document never references its
downstream documents.

```
prd ← spec (depends-on: ["prd-*"]) ← adr (depends-on: ["spec-*"])
```

- **ADR**: Depends on spec (`"spec-*"`). `supersedes` / `superseded-by` are lateral references between ADR
  **files**, not upstream dependencies.

## Validation Checklist

### Common Checks (All Documents)

| Check Item                  | Description                                                                                      | Importance |
|:----------------------------|:----------------------------------------------------------------------------------------------------|:-----------|
| **`id` format**             | Matches expected pattern for type (`adr-*`)                                                      | Medium     |
| **`type` correctness**      | Matches document location (`"adr"` for `adr/`)                                                    | Medium     |
| **`depends-on` references** | All referenced IDs exist in actual documents                                                      | High       |
| **`depends-on` direction**  | Dependencies point upstream only (adr→spec)                                                       | High       |
| **`id` uniqueness**         | No duplicate IDs across all documents in the project                                              | High       |

### ADR-Specific Checks

| Check Item                                    | Description                                                          | Importance |
|:-----------------------------------------------|:-----------------------------------------------------------------------|:-----------|
| **`sdd-phase` correctness**                    | Must be `"implement"`                                                  | Low        |
| **`status` value**                             | Must be `"approved"`                                                    | Low        |
| **`supersedes`/`superseded-by` consistency**   | File-level only: the referenced `adr-*` file ids exist and the reverse pointer is set on the other file. An entry-level reversal recorded here is a defect — it belongs in the new entry's body | High |

## Status Transition Rules

### ADR

ADR entries are append-only and do not follow the draft/review/approved/deprecated lifecycle: an entry is written
once a decision is made, so `status` is `"approved"` from the start and is never advanced or rewritten. Which
decision is current is read from the file body — the latest entry wins, and an entry replaced by a later one
carrying a `Supersedes` item is never edited. `superseded-by` in the front matter says something different: the
whole file has been retired in favor of another decision log.

## Missing Front Matter Policy

- Documents without front matter remain valid (backward compatibility).
- If front matter is absent, note in reports: "Front matter not found. Consider adding YAML front matter for structured
  metadata."
- Do **not** treat missing front matter as a violation.
- When generating new documents, always include front matter.
- When updating existing documents that lack front matter, do not add it unless explicitly requested.
