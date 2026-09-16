# Reference Detection Result Schema

`scripts/detect-references.py` writes its result to
`${SDD_ROOT}/.cache/migrate-design-to-adr/reference_detection.json` and exports
`MIGRATE_ADR_CACHE_DIR` / `MIGRATE_ADR_DETECTION_RESULT` / `SDD_LANG` to `CLAUDE_ENV_FILE`.

## Top Level

| Field              | Type   | Description                                                     |
|:-------------------|:-------|:----------------------------------------------------------------|
| `scan_timestamp`   | string | UTC timestamp of the scan (`YYYY-MM-DDTHH:MM:SSZ`)              |
| `mode`             | string | `"single"` (a feature name was given) or `"all"`                |
| `total_targets`    | number | Number of v4.x design docs matched                              |
| `total_references` | number | Number of references across all targets (deduplicated per line) |
| `targets`          | list   | One object per design doc (see below)                           |

## Target

| Field                     | Type   | Description                                                        |
|:--------------------------|:-------|:-------------------------------------------------------------------|
| `feature`                 | string | Feature name (the `_design` suffix stripped)                        |
| `design_path`             | string | Absolute path of the `*_design.md`                                  |
| `design_relative_path`    | string | Path relative to the SDD root                                       |
| `design_file_name`        | string | File name only                                                      |
| `design_id`               | string | `design-{feature}` (hierarchical: `design-{parent}-{feature}`)       |
| `adr_relative_path`       | string | Decision log to append to, relative to the SDD root                 |
| `adr_id`                  | string | `adr-{feature}` (hierarchical: `adr-{parent}-{feature}`)             |
| `references`              | list   | One object per referencing line (see below)                         |
| `core_standard_count`     | number | References whose `category` is `core_standard`                      |
| `project_specific_count`  | number | References whose `category` is `project_specific`                   |

## Reference

| Field      | Type   | Description                                                                  |
|:-----------|:-------|:-----------------------------------------------------------------------------|
| `path`     | string | Path relative to the SDD root, or to the project root for a file outside it   |
| `line`     | number | 1-based line number                                                          |
| `text`     | string | The line, stripped                                                            |
| `category` | string | `core_standard` (rewrite may be proposed) or `project_specific` (report only) |
| `kind`     | string | See the table below                                                           |
| `matched`  | string | The file name or id token that matched                                        |

## Kinds

| Kind                        | Category           | Meaning                                              |
|:----------------------------|:-------------------|:-----------------------------------------------------|
| `spec_related_design_link`  | `core_standard`    | A spec's link to, or "Related Design Doc" label for, the design doc |
| `front_matter_depends_on`   | `core_standard`    | A `depends-on` entry naming `design-{feature}`        |
| `prd_design_link`           | `core_standard`    | A **link line** in a PRD                              |
| `prd_prose_mention`         | `project_specific` | A PRD mention that is not a link line (PRD Non-Automation) |
| `spec_prose_mention`        | `project_specific` | Prose in a spec, not a link                           |
| `custom_front_matter_field` | `project_specific` | A front matter key outside the core schema (e.g. `source_design`) |
| `front_matter_field`        | `project_specific` | A core front matter key other than `depends-on`       |
| `custom_document_type`      | `project_specific` | A project's own document type - one declared in `.sdd-config.json` `naming.ignore_patterns`, or a stem carrying an undeclared suffix (e.g. `*_spec-test.md`) |
| `design_doc_cross_reference`| `project_specific` | One `*_design.md` referencing another                 |
| `adr_reference`             | `project_specific` | A mention inside an existing decision log (reported, never rewritten: `adr/` is append-only) |
| `task_reference`            | `project_specific` | A reference inside the temporary `task/` tree          |
| `other_document_reference`  | `project_specific` | Another Markdown document under the SDD root           |
| `code_comment`              | `project_specific` | A reference in a source file                           |

## Exclusions

Never reported:

- `AI-SDD-PRINCIPLES.md`, `MIGRATION_PENDING.md`, `UPDATE_REQUIRED.md` - generated files
- `CHANGELOG.md` - historical record
- Anything under `.cache/` - regenerated every session
- The target `*_design.md` itself (its own `id` and name are not references to it)
- A token containing `design-draft`, or a ticket-scoped id (`design-123`, `design-TICKET-123`) - correct v5
  draft records

Existing `adr/` entries are surfaced as `adr_reference` when they mention the file, so they appear in the
manual list; they are never rewritten, because `adr/` is append-only.

Two needles are searched per line: the design doc's file name, and its `design-{feature}` id (matched with a
word boundary, so `design-user-auth-extra` does not count). Its relative path is not a needle, since every
line containing it also contains the file name.

`--docs-only` skips the source-file scan (Markdown under the SDD root only). Source files are those with a
`hook_common.SOURCE_EXTENSIONS` extension; build and dependency directories are pruned from the walk.
