---
name: migrate-design-to-adr
description: "Migrate a v4.x persisted specification/*_design.md into adr/{feature-name}.md, carrying over decisions and rejected alternatives only, then report the references that need updating"
argument-hint: "<feature-name> | --all"
arguments: [feature-name]
license: MIT
user-invocable: true
model: sonnet
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/**), Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/migrate-design-to-adr/scripts/detect-references.py" *)
---

# Migrate Design to ADR - Extract v4.x Design Docs into `adr/`

Migrates a v4.x persisted technical design document
(`${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md`) into an append-only decision log
at `${CLAUDE_PROJECT_DIR}/${SDD_ADR_PATH}/{feature-name}.md`, carrying over **only** the decisions, their
rationale and the rejected alternatives.

**This migration is never urgent.** Existing `*_design.md` files remain valid and are read as supplementary
input by the skills that need a technical design. Keeping a file in place is a valid outcome; this skill only
makes the migration mechanical when the user chooses to do it.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/front_matter_reference.md` - Front matter schema (the `type: "adr"` table is the authority for the
  file-level fields written in step 4)
- `references/reference_detection_schema.md` - Schema of the reference-detection script's JSON output

### Tool Permissions

`allowed-tools` above deliberately **omits a bare `Bash`**: the only pre-approved command is this skill's own
reference-detection script. Deleting the migrated `*_design.md` (step 6) therefore always goes through a
permission prompt at the moment it runs — that is the intended configuration, not a misconfiguration. Do not
propose widening `allowed-tools`, and do not route around the prompt. If the confirmation cannot be answered
(non-interactive session), report the pending deletion in the output and leave the file in place.

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

### Options

- `<feature-name>`: migrate a single `{feature-name}_design.md`
- `--all`: migrate every v4.x design doc reported in `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/MIGRATION_PENDING.md`
- `--docs-only`: passed through to the detection script to skip the source-file scan, for a large repository
  where only the documents matter

### Input Examples

- `/migrate-design-to-adr user-auth` — migrate one feature
- `/migrate-design-to-adr --all` — work through every pending file

With `--all`, migrate **one pilot file first and get the user's approval on its resulting ADR entries**, then
process the rest in one pass. A format misreading caught on one file avoids redoing every file.

## Processing Flow

### 1. Resolve Targets

Run `python3 "${CLAUDE_PLUGIN_ROOT}/skills/migrate-design-to-adr/scripts/detect-references.py"` with the
feature name, or `--all`. The script resolves the directory layout from `.sdd-config.json`, lists the v4.x
design docs to migrate (each with its `adr/` counterpart path and id), scans the project for references to
them, classifies every reference, and writes the result JSON reported on its last log line. Read that file —
do not re-derive the list by hand.

The script never reports a reference to `task/{ticket-number}/design-draft.md` or to a `design-{ticket-number}`
id: those are correct v5 records, not migration targets.

If the target list is empty, report that there is nothing to migrate and stop.

### 2. Read the Design Doc and Extract Decisions

Read each target `*_design.md` in full and pull out the decision-bearing content only.

**Carry over (the *why*)**

1. Every row of a design-decision table (the options, what was decided, and the reason)
2. A technology-stack choice **whose rationale is written down**
3. A rejected alternative and the reason it lost
4. A constraint that forced the decision (the applicable CONSTITUTION principle id, a platform limit, a
   compatibility requirement)

**Do not carry over (the *how* / *what*)**

1. Implementation-status tables
2. Module-breakdown tables and system-architecture diagrams
3. Data models and interface definitions
4. Test strategies and test-case tables
5. Change history
6. Open questions (an undecided item is not a decision)

When the document has no design-decision table, apply the same criteria per `##` section.

**Never invent a decision.** If a section states a choice without a rationale, either carry it over with the
rationale left as the document's own words, or leave it out — do not supply a reason the document does not give.

### 3. Determine the Entry Format

Resolve the ADR entry format in this order — the same two-step fallback `task-cleanup` uses (see
`../task-cleanup/SKILL.md` step 5), so this skill defines **no** format of its own:

1. Check whether `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md` exists
2. **If it exists**: use that template — it is the project's own entry format (`/sdd-init` copies it there and
   never overwrites an edited copy)
3. **If it does not exist**: fall back to the entry format defined in `AI-SDD-PRINCIPLES.md` § Architecture
   Decision Record → Entry Format

That table is the canonical field definition (heading, `- **Decision**:`, `- **Rationale**:`,
`- **Rejected alternatives**:`, optional `- **Supersedes**:`) and is not restated here. Two refinements apply
to a migration specifically:

- **Heading date**: use the date the decision was made, taken from the design doc (its decision table, its
  change history, or its front matter `created` / `updated`) — not today's migration date. Fall back to the
  file's last commit date only when the document records nothing
- **Rejected alternatives**: write `None considered` when the design doc records none — never invent one

When the project's template adds sections of its own, follow the template and keep these items.

### 4. Append to `adr/{feature-name}.md`

Mirror the feature's path under `specification/` (a design doc at `{parent}/{feature}_design.md` becomes
`adr/{parent}/{feature}.md`; the script already reports the path and id to use).

- **Append-only**: one `##` entry per decision, at the end of the file, below its `#` title. Never rewrite,
  reorder or remove an existing entry
- When the file does not exist yet, create it as: the `adr` front matter block, then a
  `# {feature-name} Decision Log` title, then the entries. Set the fields defined for `type: "adr"` in
  `references/front_matter_reference.md` (`id`, `type`, `title`, `status` — always `"approved"`, since a
  decision is recorded after the fact — `created`, `updated`, `sdd-phase`, `sdd-version`, `depends-on`, and
  `ticket` when the design doc records one)
- Leave the front matter `supersedes` / `superseded-by` fields out: they retire a decision-log **file** as a
  whole (a renamed, split or merged feature), never one entry reversing another
- Order the entries oldest first, so the file reads chronologically like one written incrementally
- Do not record the source file name — the ADR is not a history of the migration

### 5. Verify the Entries Landed

Re-read `adr/{feature-name}.md` from disk with `Read` before proposing anything destructive. Do not rely on
the edit's return value. Confirm that every appended entry's heading and its `Decision` / `Rationale` /
`Rejected alternatives` items are present and non-empty, that every pre-existing entry is unchanged, and that
the front matter fields are on disk.

**If any check fails, propose no deletion.** Report what is missing and stop.

### 6. Confirm the Original File's Fate

Ask the user with `AskUserQuestion` whether to delete the migrated `*_design.md` or keep it. **Never delete it
without that confirmation** — it is a destructive operation, and the design doc is the only remaining copy of
anything step 2 left behind.

- **Deleting is the recommended default**: it completes the move to the v5 model, and once no `*_design.md`
  remains the `session-start` hook removes `MIGRATION_PENDING.md` on its own
- Present the file's remaining content that was deliberately not carried over (module tables, data models,
  test strategy) so the user can judge, and name the references from step 7 that would dangle
- **Keeping the file is a valid choice**: it stays valid as supplementary input, and nothing reports it as a
  violation. When the user keeps it, skip the rewrite proposals in step 7 — nothing is dangling — and report
  the detected references as informational only
- The deletion itself runs as a shell command and will ask for permission separately (see Tool Permissions)

### 7. Report the References

Read the detection result from step 1 and act per category.

**Core standard references** (`category: "core_standard"`) — propose a rewrite via `AskUserQuestion`, one
grouped proposal per document:

- A `*_spec.md` "Related Design Doc" link or in-body link → link to `adr/{feature-name}.md`
- A `depends-on` front matter entry naming `design-{feature-name}` → the ADR's id (`adr-{feature-name}`) or the
  current draft's id (`design-{ticket-number}`), depending on which the dependency actually meant
- A **link line** inside a PRD → link to `adr/{feature-name}.md`. Only the link line. Requirement text, ids and
  structure are never touched: the AI-SDD PRD Non-Automation principle forbids inferring requirement content
  from downstream documents, and repairing a broken link is not a requirement change

**Project-specific references** (`category: "project_specific"`) — **detection only**. List them under
"manual action required" with path, line and text, and change nothing. They cover a project's own front matter
fields (e.g. `source_design`), its own document types (e.g. `*_spec-test.md`), prose mentions, temporary
`task/` documents, and code comments. This skill cannot know what a project's own convention means.

**Never touched** (the script excludes these from its output, except where noted):

- `${SDD_ROOT}/AI-SDD-PRINCIPLES.md` and `${SDD_ROOT}/MIGRATION_PENDING.md` / `UPDATE_REQUIRED.md` — generated
  files, rewritten by the `session-start` hook
- `CHANGELOG.md` — rewriting a past entry rewrites history
- Existing ADR entries — reported as `adr_reference` so the mention is visible, but never rewritten: `adr/` is
  append-only
- Anything under `${SDD_ROOT}/.cache/` — regenerated every session
- Any reference to `design-draft.md` or a `design-{ticket-number}` id — correct v5 records

### 8. Output the Report

Render `templates/${SDD_LANG:-en}/migration_report.md`. With `--all`, report the remaining count after each
file so the user can stop at any point.

## Notes

- The completed decision log can be read back with `/render-adr-review adr/{feature-name}.md`
- Neither `/check-spec` nor `doc-consistency-checker` verifies Markdown link health, so the reference report in
  step 7 is the only place a dangling link surfaces
- This skill never creates or edits a `*_design.md`, and never touches `task/{ticket-number}/design-draft.md`
