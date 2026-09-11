# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[日本語版 CHANGELOG](CHANGELOG.ja.md)

## [Unreleased]

## [5.0.0] - 2026-09-10

**Note**: This is a major release with breaking changes to the document model. Read
"Migration from v4.x" in README.md / README.ja.md before upgrading an existing project. Migrating is
**not urgent**: existing `specification/*_design.md` files remain valid, the naming hook accepts them,
and the skills that read a technical design read them as supplementary input — nothing breaks until you
move their decisions into `adr/`, at your own pace.

### Breaking Changes

#### Document Structure

- **`specification/{feature-name}_design.md` is no longer a persistent document** - Technical Design
  Documents are now a temporary draft at `task/{ticket-number}/design-draft.md`, deleted after
  implementation like the rest of `task/`. Only the decisions, their rationale, and rejected
  alternatives are persisted, in the new `adr/{feature-name}.md` (append-only). Existing
  `specification/*_design.md` files from v4.x **remain valid**: the skills that read a technical design
  read them as supplementary input, and none of them reports them as a naming violation or proposes
  deleting them (see "v4.x persistent design documents" under Fixed for the full list). Moving their decisions
  into `adr/{feature-name}.md` is a human-paced step you can take feature by feature — see "Migration
  from v4.x" in README.md / README.ja.md
- **`/generate-spec` now requires a ticket number** - The design draft path is ticket-scoped
  (`task/{ticket-number}/design-draft.md`), so `/generate-spec` takes `--ticket <number>` (required in
  `--ci` mode, resolved interactively otherwise)
- **`doc-consistency-checker` now checks PRD ↔ spec ↔ adr, not PRD ↔ spec ↔ design**
- **`/check-spec` now compares the implementation against the spec, not against a design document** -
  The design document is a temporary draft (`task/{ticket-number}/design-draft.md`) that is deleted after
  implementation, so it can no longer serve as a persistent comparison baseline. `/check-spec` now takes
  every spec under `specification/` (suffix optional) as the first-class baseline, and uses a design draft
  only as an optional auxiliary input when one exists — a missing draft is the normal state after
  implementation and is never reported as a discrepancy. Because a spec is an abstract specification, the
  comparison is limited to what it can express (public API, data model, behavior, literal values); module
  structure and technology stack are compared only while a draft exists. Projects that still keep v4.x
  `{feature}_design.md` files under `specification/` get the same auxiliary treatment for those files
- **`/plan-refactor` decides Case A / Case B from the spec, and writes the plan into the design draft** -
  The case used to be decided by the presence of `specification/{feature-name}_design.md`, which is no
  longer a persistent document, so every run fell through to Case B and reverse-engineered a persisted
  design doc that the new model had just retired. The case now comes from whether a **spec** exists
  (matched with *and* without the `_spec` suffix), the refactoring plan and the reverse-engineered design
  are written to `task/{ticket-number}/design-draft.md`, and the reverse-engineered spec continues to be
  persisted under `specification/`. A leftover `*_design.md` from v4.x is still detected, but only as
  reading context — it never decides the case and is never written to
- **`/plan-refactor` now takes a ticket number** - The design draft path is ticket-scoped, so
  `/plan-refactor` takes `--ticket=<number>` (required in `--ci` mode, resolved interactively otherwise).
  An existing `task/{ticket-number}/design-draft.md` is picked up as supplementary input in Case A
- **`/task-breakdown` now requires a ticket number** - Both the design draft it reads and the `tasks.md`
  it writes live under `task/{ticket-number}/`, so the ticket number can no longer be omitted.
  `tasks.md` is always written to `task/{ticket-number}/tasks.md`; the previous fallback to
  `task/{feature}/tasks.md` is gone

### Added

#### Skills

- **`/generate-prd --amend`** - New mode that appends newly-provided requirements to an existing PRD instead
  of regenerating it. Preserves existing requirement IDs, sections, and requirements-diagram nodes, and
  assigns new IDs continuing from the existing maximum per prefix. `finalize-prd` now accepts the existing
  PRD text and merges the new content when called with `--amend`
- **`/generate-spec --amend`** - New mode that appends new functional/non-functional requirements to an
  existing spec instead of regenerating it, preserving existing requirement IDs and sections
- **`render-adr-review`** - New skill that renders an `adr/{feature-name}.md` decision log (or
  the decision rationale section of a `*_spec.md`/`*_design.md`) into a temporary review HTML, structured
  by decision / rationale / rejected alternative rather than a plain Markdown-to-HTML conversion. Output
  is written under `.sdd/.cache/render-adr-review/` and is not meant to be committed.
  Because the log records a reversal one-way — on the newer entry, leaving the entry it reverses
  untouched — a superseded decision carries no marker of its own in the source and reads as current.
  The render resolves each entry's `Supersedes` reference and marks the entry it points at as
  superseded, so an obsolete decision is visibly distinct from the live one and links to the entry that
  replaced it. The marker carries the one-line "what changed" the `Supersedes` item records, and its link
  points at the superseding entry's card in the same page rather than reusing a Markdown anchor from the
  source. The file-level `supersedes` / `superseded-by` front matter fields are never consulted for this,
  because they mean a whole log file was retired, not that one entry was reversed. A decision that was
  later reversed still shows as adopted within its own comparison table: that is what was chosen at the
  time, and the reversal belongs to the entry's state, not to its history. `Rejected alternatives: None
  considered` is rendered as "no alternatives were weighed", not as a rejected option
- **`task-cleanup`** - Posts a summary comment to the ticket when implementation completes, and checks
  whether the decisions being integrated into `adr/` also trigger a `*_spec.md` update per the "When to
  Update `*_spec.md`" criteria; if so, proposes the spec update via `AskUserQuestion`
- **`/sdd-init` now generates `${SDD_ROOT}/ADR_TEMPLATE.md`** - The decision log template ships with the
  plugin in both languages and is copied like the PRD / spec / design templates (existing files are never
  overwritten). It carries the settled ADR entry format, a worked two-entry example including one entry
  superseding another, and a note to append below the last entry without touching the ones above. Note
  that `/sdd-init` still creates only the `${SDD_ROOT}/` root itself — `adr/`, like `requirement/`,
  `specification/` and `task/`, is created when its first file is written
- **`/sdd-init` now adds the cache directory to your project's `.gitignore`** - `.sdd/.cache/` (or
  `${SDD_ROOT}/.cache/` for a custom root) holds generated, disposable files — the document index, the
  per-skill working copies, the `render-adr-review` HTML — and used to be left for you to ignore by hand.
  This is a **new write into a file outside `${SDD_ROOT}/`**, so it is deliberately minimal: the entry is
  appended once under a comment naming what it is, an existing `.gitignore` keeps every line it already
  had (and gains a trailing newline only if it was missing one), a `.gitignore` that does not exist is
  created holding just that entry, and a project that already ignores the path — with or without a
  leading or trailing slash — is left untouched. Re-running `/sdd-init` never duplicates the line. Only
  `.cache/` is ignored: your PRDs, specs, design drafts and decision logs under `${SDD_ROOT}/` stay
  tracked
- **`/check-spec --ticket <number>`** - Scopes the auxiliary design draft to one ticket (see Fixed below)

#### Configuration

- **`SDD_ADR_DIR` / `SDD_ADR_PATH`** - New environment variables for the `adr/` directory, set at session
  start alongside the existing `SDD_*_DIR` / `SDD_*_PATH` variables

#### Hooks

- **`${SDD_ROOT}/MIGRATION_PENDING.md` lists the v4.x documents still waiting to be migrated** - When a
  project still holds `specification/**/*_design.md` files, the SessionStart hook writes them into this
  file (up to ten individually, then a count of the rest) and states that they remain valid and are read
  as supplementary input, where their decisions move (`adr/{feature-name}.md`), where new technical
  design goes (`task/{ticket-number}/design-draft.md`), and that the originals should be kept until the
  migration is done. The steps are named as a path you can actually open — `<plugin root>/README.md`,
  section "Extracting Existing `*_design.md` Files into `adr/`" under "Migration from v4.x", with
  `README.ja.md` alongside it — instead of "see the plugin README". The file is deliberately **separate
  from `UPDATE_REQUIRED.md`**, which reports only that `CLAUDE.md` is outdated and disappears once
  `/sdd-init` has run: an unfinished migration is a different concern with a different pace, so
  `MIGRATION_PENDING.md` survives `/sdd-init`, is rewritten at every session start for as long as any
  such file remains, and is removed automatically once none do. It is generated, so hand edits are
  replaced next session. A project with no such files never gets the file. Unlike `UPDATE_REQUIRED.md`,
  whose presence makes the skills warn you to run `/sdd-init` first, `MIGRATION_PENDING.md` is not a
  pre-execution check: a pending migration never holds up a skill

#### Front Matter

- **`sdd-version` common field** - Documents may record the sdd-workflow plugin version at generation time
  in the `sdd-version` front matter field, read from `plugin.json`. `generate-spec`, `generate-prd`,
  `finalize-prd`, and `task-cleanup` set it when creating new front matter. Absent in documents generated
  before this field was introduced, or when a document's front matter is added retroactively by
  `recommend-front-matter` (which intentionally omits it rather than fabricate a false generation-time value)
- **`sdd-version` is now read, not just written** - The document index (`.cache/index.md`) now includes
  `sdd-version` in its Metadata table. `front-matter-reviewer` validates its semver format and warns when a
  document's major version is older than the current plugin's major (a possible sign of a missed migration).
  `doc-consistency-checker` enumerates both documents with a stale generation and documents whose
  generation is unknown (no `sdd-version` at all — the normal state for anything written before v5), as
  two separate advisory lists for manual migration review
- **`type: "adr"` schema** - `shared/references/front_matter_reference.md` now defines the front matter
  fields for a decision log, including `status` (always `"approved"` at write time) and `supersedes` /
  `superseded-by`. Those two fields are **file-level only**: a log holds many entries but a single front
  matter block, so they record that a whole log file was retired and replaced (a feature renamed, split
  or merged). One entry reversing another is recorded in the body of the newer entry instead — see the
  ADR entry format below
- **`impl-status` is now a valid Spec field, not just Design** - A spec can now record whether its described
  behavior is reflected in the implementation, independent of `status` (the document's approval lifecycle).
  `generate-spec` sets it to `"not-implemented"` on new specs; `implement` advances it to `"in-progress"` /
  `"implemented"` as work proceeds; `task-cleanup` sets it as a safety net if `implement` didn't. `check-spec`
  now classifies a spec-documented function with no matching implementation by this field instead of always
  flagging it Critical: `implemented` is a regression (Critical), `not-implemented`/`in-progress` is expected
  (Info), and a missing field is undecidable (Warning, with a recommendation to add it). `front-matter-reviewer`
  validates the field's enum value on specs, and `recommend-front-matter` lists the specs that are missing it
  — it never writes the value, because it does not inspect the implementation (see Changed below)

#### Workflow Guidance

- **Task Type Determination now covers Breaking Changes** - The Task Type Determination table and Task
  Scale Criteria in `AI-SDD-PRINCIPLES.md` gained a "Breaking Change" row, plus a new "Breaking Change
  Handling" section defining impact analysis, the backward-compatibility decision, and where migration
  steps are recorded (`adr/`). The table is now also transcribed into `.claude/rules/ai-sdd-instructions.md`
  so every project gets the same guidance without opening the principles document
- **Drafting a new PRD when none exists is now explicitly allowed** - `AI-SDD-PRINCIPLES.md` clarifies that
  the "PRD is never automated" rule governs rewriting an existing PRD, not drafting a new one from scratch;
  a drafted PRD must use `status: "draft"` and the `"reverse-engineered"` tag until a human approves it.
  `/plan-refactor` now proposes this when its reverse-engineered spec has no PRD to depend on
- **`vibe-detector` now recommends a starting phase** - Its risk report classifies the request against the
  Task Type Determination table and reports the corresponding starting phase (Specify/Plan/Tasks/Implement),
  in addition to the existing ambiguity risk assessment
- **The ADR entry format is now specified instead of left to each skill** - `AI-SDD-PRINCIPLES.md` gained
  an "Entry Format" section under Architecture Decision Record: a file is one front matter block, one `#`
  title, and many `##` entries appended at the end. Each entry is headed `## YYYY-MM-DD {decision title}`
  and carries **Decision**, **Rationale** and **Rejected alternatives** (`None considered` when there were
  none — never invented), plus an optional **Supersedes** linking to the earlier entry in the same file
  that it reverses. Superseding is recorded one-way on the newer entry; the entry it reverses is never
  edited, not even to add a back-pointer, so the log stays append-only and the last entry is always the
  current decision. Those items match one-for-one what `render-adr-review` and `doc-consistency-checker`
  extract, so a log written this way is readable by the skills without further conventions

### Fixed

- **`adr/` is now scanned by the document index and by `/recommend-front-matter`** - Both previously
  scanned only `requirement/` and `specification/` (plus `task/` for the latter), so decision logs never
  appeared in the compressed index or in front matter recommendations
- **Editing a decision log now refreshes the document index** - The `PostToolUse` reminder fired, but the
  index update it triggers for other document types did not run for `adr/`
- **`AI-SDD-PRINCIPLES.md`'s Configuration Items table and `.sdd-config.json` example now document
  `directories.adr`** - `session-start` already resolved the setting into `SDD_ADR_DIR` / `SDD_ADR_PATH`,
  and `adr/` is created the first time a file is written into it (`/sdd-init` creates only the
  `${SDD_ROOT}/` root, never the subdirectories); only the documentation of the setting was missing
- **`doc-consistency-checker`'s Obsolescence Detection now specifies how to record a reversal** - The
  follow-up action used to be undefined. It now proposes appending a new entry to the end of the same
  `adr/{feature-name}.md`, with the required items plus a `Supersedes` link to the entry it reverses. The
  obsolete entry is left exactly as it is — no back-pointer, no `status: "deprecated"`, and nothing
  written into the file-level `supersedes` / `superseded-by` front matter fields, which cannot express a
  relationship between two entries of the same file
- **`adr/{feature}.md` front matter now has a `ticket` field, and `task-cleanup` sets it** - Previously,
  when a ticket's tracker (GitHub Issue / JIRA) was unreachable, `task-cleanup` skipped step 9 (posting a
  completion summary) with no fallback, and deleting `task/{ticket-number}/` erased the only link between
  the ticket number and the feature. The `adr` entry created in step 7 now records `ticket`, so the
  association survives even when no tracker is reachable
- **`run-checklist` can now actually run tests/linters/security scanners** - `allowed-tools` had no shell
  access at all, so the skill's core function (executing verification commands) silently fell back to
  guessing from static analysis. Added a scoped `scripts/run-verification.py` (detects the project's
  toolchain and runs test/lint/typecheck/security commands, per `references/verification_commands.md`)
  and pre-approved only that single script, consistent with this repo's "no bare `Bash`" convention.
  A project with no tests configured is reported as `SKIPPED` rather than `FAIL`, so an unconfigured
  category never fails the quality gate. The categories the script does not cover (formatter checks,
  dependency analysis, doc coverage) are now stated explicitly in
  `references/verification_commands.md` as manual-review items instead of being implied to be automatic
- **README.md / README.ja.md's Tool Permissions section no longer understates what is pre-approved** -
  It still listed `/run-checklist` among the skills that pre-approve no shell access at all, which
  stopped being true the moment this release gave the skill `scripts/run-verification.py` (above) — a
  script that starts your project's own test, lint, typecheck and audit commands in a subprocess without
  asking. Because that is a judgement you make before installing, the section now names the script and
  its full path, the project markers it looks for (`package.json`, `pyproject.toml`, `Cargo.toml`,
  `go.mod`, `setup.py`, `requirements.txt`, `Gemfile`, and — with no manifest at all — a `tests/` or
  `test/` directory containing `test_*.py` / `*_test.py`), the commands it runs per
  toolchain, its 300-second per-command timeout, and the fact that commands written inside your
  `checklist.md` are **not** executed — only that one script is pre-approved, not bare `Bash`. It also
  lists the ten helper scripts a skill pre-approves and states that this is the only one of them that
  starts another process. Of the three skills that had `Bash` removed in v4.0.1, `/implement` and
  `/task-cleanup` are the two that still pre-approve no shell access
- **`checklist`'s bundled template no longer contradicts its own SKILL.md** - The template used a
  `P0`-`P3` priority scale and sequential `CHK001` IDs, while SKILL.md's Processing Flow and canonical
  example (`examples/checklist_full_example.md`) define `P1`-`P3` and `CHK-{category}{seq}` IDs (e.g.
  `CHK-501`). Rewrote both language templates to match, folded the template's extra "Project Principles
  Review" category into Requirements Review (`CHK-104`/`CHK-105`) so the category count stays at the 9
  categories `run-checklist`'s `CHK-1xx`-`CHK-9xx` mapping assumes, and fixed a leftover "P0 items"
  reference (there is no P0) in the Export Formats section
- **`vibe-detector`'s Escalation step no longer instructs an action it cannot perform** - Its
  `disallowed-tools` blocks `Write`/`Edit`/`Bash` (a deliberate constraint — the skill is
  `user-invocable: false` and runs automatically ahead of implementation, without the user asking for it,
  so it must stay read-only), but the Escalation section told it to save
  `assumed-spec.md` directly. It now drafts that document's content in its own output and instructs the
  calling session (which holds normal write access) to save it
- **`recommend-front-matter` now knows the ADR schema** - `scan-documents.py` already scans and classifies
  `adr/` documents, but the skill's Prerequisites and `type_specific_fields.md` templates never defined
  ADR's fields, so a front-matter-less decision log got an incomplete or invented recommendation. Added
  `references/front_matter_adr.md` and an ADR entry in both language `type_specific_fields.md` templates,
  and added `adr` to the skill's own `type` enumeration and `depends-on` inference table (which listed
  every other scanned type, so the new reference would otherwise never be reached)
- **`naming.py::determine_type()` no longer misclassifies `task/{ticket}/design-draft.md` as `type: "task"`**
  - It special-cased `implementation_log`/`impl_log` filenames but had no branch for `design-draft.md`,
    the canonical location for the new-era design draft, so callers like `recommend-front-matter` recommended
    the wrong type-specific fields for it
- **`constitution`'s two version-bump tables now agree row for row** - The "Update Constitution" table said
  adding a principle is a MAJOR bump, while the dedicated `add` flow and the "Semantic Versioning" table
  both said MINOR. It also mapped "Clarify principle" to MINOR while the Semantic Versioning table mapped
  "Fix expression of principle" (the same act) to PATCH, and omitted the priority change that the
  "Conditions for Major Version Bump" section lists as breaking. Both tables now enumerate the same change
  types, split by one stated rule — does the change alter what an existing principle demands?
- **`sdd-init`'s "Configuration File Management" section no longer contradicts its own script** - It said
  `init-structure.py` auto-creates `.sdd-config.json` with defaults when missing; the script actually
  exits with an error (by design — the SessionStart hook owns default creation, so `sdd-init` doesn't
  duplicate that responsibility). Corrected the prose to match the actual, intended behavior
- **`front_matter_reference.md`'s ADR schema no longer contradicts its own Status Transition Rules** - The
  field table listed a `draft`/`review`/`approved`/`deprecated` lifecycle for ADR's `status` field, while
  the Status Transition Rules section says ADR doesn't follow that lifecycle at all. Corrected the field
  table to reflect that ADR `status` is always `"approved"` at write time, and that a reversal is recorded
  one-way in the body of the newer entry (its `Supersedes` item) — never in the file-level `supersedes` /
  `superseded-by` fields, which record only that a whole log file was retired and replaced
- **`finalize-prd`'s Rule 7 (Amend Mode Integration) no longer contradicts its own PRD template** - It
  described new UR/FR/NFR row insertion as appending to "the end of the matching table in §4 (Detailed
  Requirements)", but §4 in `templates/{en,ja}/prd_template.md` is prose (`### FR_001: {name}` headings),
  not a table. Corrected the description to match the template (append a new subsection matching the style
  of existing entries). Also added a default policy for which existing use case a new
  `<<include>>`/`<<extend>>` relationship should attach to when the caller doesn't specify, and a rule to
  surface (rather than silently drop) input attributes that have no corresponding slot in the existing PRD
  structure (e.g. `Priority`)
- **The "Migration from v4.x" steps in README.md / README.ja.md now work** - Step 1 told you to re-run
  `/sdd-init` to create the `adr/` directory and its template, but the script creates only the
  `${SDD_ROOT}/` root and no ADR template existed at all. Step 6 told you to verify with `/check-spec` or
  `doc-consistency-checker` after deleting a `*_design.md`, and neither skill checks link health, so
  following it would have left broken `depends-on` values and body links behind silently. Step 1 now
  states what re-running actually gives you (`ADR_TEMPLATE.md`, with `adr/` created on the first write
  into it), and step 6 is now two runnable `grep` commands — one for path references (`_design\.md`) and
  one for id references (`design-{feature-name}`, or `design-{parent}-{feature}` for a hierarchical
  feature) — both excluding `.sdd/.cache/` and `.sdd/AI-SDD-PRINCIPLES.md`, which are regenerated from
  the installed plugin and whose hits are the plugin's own prose rather than references from your
  documents. Without those exclusions the search drowned in generated files. The step now says to update
  only the hits that point at a file you actually deleted, that prose mentioning the convention is not a
  reference, that no skill reports broken links, and that keeping the old file is a valid choice. The
  remaining steps now use the settled ADR entry format and the real front matter field list
- **README.md / README.ja.md now list every breaking change, and explain ticket numbers** - "Breaking
  Changes in v5.0.0" covered three of this release's breaking changes, so the `/check-spec` baseline
  inversion, `/plan-refactor`'s new case decision and ticket argument, `/task-breakdown`'s required
  ticket number and dropped fallback, and `doc-consistency-checker`'s new target were discoverable only
  from this changelog; the section now matches it one-for-one. A new "Ticket Numbers" section lists, per
  skill, how the number is passed and whether it is required, and explains that a project without an
  issue tracker can use any stable identifier (the feature name being the easy choice) — only
  `/task-cleanup`'s completion comment needs a tracker, and when none is reachable it is skipped while
  the association survives in the `ticket` front matter field of `adr/{feature-name}.md`. The `/sdd-init`
  description was corrected (it creates the root only, and `CONSTITUTION.md` comes from
  `/constitution init`), and `SDD_INDEX` was added to the environment variable table
- **README.md / README.ja.md's component table and `/check-spec` description now match the shipped
  skills** - The table still described `doc-consistency-checker` as checking `PRD ↔ spec ↔ design`, which
  this release's own breaking-changes list contradicts, and six other rows had drifted from their skill's
  description (`/plan-refactor` "creates/updates design documents", `/generate-prd` limited to SysML
  output, `/check-spec` against "specifications" rather than the abstract spec, `/task-breakdown` reading
  a "technical design document", and `/checklist` and `/task-cleanup` naming retired destinations); all
  of them were corrected against the descriptions the skills actually declare, and the `spec-reviewer` /
  `front-matter-reviewer` rows now mention their `adr/` responsibilities. The `/check-spec` section also
  claimed that with several tickets in flight and no `--ticket` no draft is read at all; it now lists the
  five outcomes the skill really has (no draft, `--ticket`, `depends-on` match, sole draft, or several
  candidates with no evidence) and notes that `--ticket` is only required in that last case and can be
  avoided by setting `depends-on` in the draft. What `--full` actually reviews is spelled out, including
  that a feature with no decision log is "not applicable" rather than consistent. The distribution
  repository's landing README, which had no mention of v5 at all, now covers updating an installed plugin
  and the two headline breaking changes, and links to the full migration section
- **v4.x persistent design documents are handled the same way everywhere a technical design is read** -
  `check-spec`, `plan-refactor` and `task-breakdown` already read a leftover `specification/*_design.md`
  as an auxiliary input, but the rest of the plugin disagreed with them and with each other: `/implement`
  did not accept one as satisfying its Technical Design prerequisite, so resuming a feature started on
  v4.x asked you to regenerate a design draft that had never existed; `/generate-spec`'s
  existing-document check never looked for one, so a new draft could contradict the recorded technology
  stack and module layout; `/checklist` and `/clarify` ignored it outright, narrowing their Design Review
  items and design-level questions to what the abstract spec supports — a regression against v4.1.0,
  which read that document (and, in `/checklist`'s case, required it); `spec-reviewer` could not review
  one; `task-cleanup` declared it a temporary file deleted by another flow; `plan-refactor` called it
  "needs manual migration"; and the naming quick reference listed it under "Incorrect Naming (never use
  these)" even though the naming hook has always allowed it. `/check-spec`, `/checklist`, `/clarify`,
  `/constitution`, `/generate-spec`, `/implement`, `/plan-refactor`, `/recommend-front-matter`,
  `/sdd-init`, `/task-breakdown`, `/task-cleanup`, `doc-consistency-checker`, `spec-reviewer` and
  `front-matter-reviewer` now all say the same thing: such files **remain valid**, are read as
  **supplementary input**, their **absence is normal**, new technical design always goes to
  `task/{ticket-number}/design-draft.md`, and none of them ever reports one as a naming violation or
  proposes deleting it. `/checklist` and `/clarify` resolve the document from the **feature name** rather
  than a ticket number — flat `{feature-name}_design.md`, or `{parent-feature}/index_design.md` /
  `{parent-feature}/{feature-name}_design.md` for a hierarchical feature — so it is consulted even when
  the ticket number is omitted, and both treat it as read-only: neither writes answers or checklist edits
  back into it. The checklist that `/checklist` generates records which design source it used, and
  `/checklist`'s warning about a ticket directory holding neither a design draft nor `tasks.md` still
  fires, because the legacy document lives under `specification/` and says nothing about the ticket
- **`/generate-spec`'s completion report no longer claims files it never wrote** - It reported
  `specification/{feature}_design.md` (or `index_design.md` for a hierarchical feature) as generated — the
  very document this release retired — and pointed at `/task_breakdown` and `/check_spec`, neither of
  which is a real command name. It now reports the persistent spec plus the temporary
  `task/{ticket-number}/design-draft.md`, with instructions to drop that line and say why when the draft
  was skipped, and the next steps are the real `/task-breakdown {feature} {ticket-number}`, `/check-spec`,
  and `/task-cleanup {ticket-number}` to move the decisions into `adr/` before the draft is deleted
- **`/generate-prd`'s completion report no longer recommends a command that cannot succeed yet** - It
  offered `/check-spec {feature} --full` as the verification step to run right after the PRD is written.
  At that point `specification/` does not exist — like the other subdirectories it is created with its
  first file — so `/check-spec` stopped with "Specification directory not found" every single time the
  advice was followed. The report now splits its commands by what can run when: `/clarify {feature}`
  works on a PRD alone (with the note that its answers cannot be written into `requirement/`, so they go
  into the `/generate-spec` input or into the PRD by hand), while `/check-spec {feature} --full` is
  listed under what needs a spec first, with the reason. The next step is a copy-pasteable
  `/generate-spec --ticket {ticket-number} {requirements-description}`, and the "generated files" section
  now says the PRD is the only document this skill writes — the use case diagram, the UR/FR/NFR tables
  and the SysML requirements diagram are sections inside it, not separate files
- **The spec template copied into your project now describes the v5 document model** -
  `.sdd/SPECIFICATION_TEMPLATE.md` still sent technology-choice rationale, architecture and the record of
  design decisions to a persistent `xxx_design.md` and never mentioned `adr/`, so specs written from it
  kept pointing at the retired document. Its comparison table now covers all three documents (spec:
  persistent / design draft: temporary / decision log: persistent and append-only), the header links to a
  Related Design Draft and a Related Decision Log, the excluded content is split by destination
  (decisions, their rationale and rejected alternatives to `adr/{feature-name}.md`; everything else
  technical to the draft), and it warns that a decision left only in the draft is lost when the draft is
  deleted
- **`task-cleanup` verifies the `adr/` append before deleting `task/{ticket-number}/`** - The deletion
  step ran `git rm` without checking that the integration had landed, so an incomplete extraction or a
  failed edit destroyed the design decisions permanently. A verification gate now runs first: the decision
  log is re-read from disk, the appended entry's `## YYYY-MM-DD {title}` heading and its Decision /
  Rationale / Rejected alternatives are confirmed present and non-empty, the entries that existed
  beforehand are confirmed unchanged, and the front matter and other document edits from the preceding
  step are confirmed on disk. If any check fails nothing is deleted: `task/{ticket-number}/` is left in
  place and the gap is reported
- **`task-cleanup` can now delete a `task/` directory that was never committed** - The deletion step was
  fixed to `git rm`, which fails on an untracked path (`fatal: pathspec '...' did not match any files`)
  and deletes nothing, while the skill was simultaneously told not to try another delete route — so a
  project that keeps `task/` out of Git could reach a completed, verified cleanup and still never finish
  it. The step now establishes tracking first with `git ls-files` on the target, judged by its **output**
  (it exits 0 whether or not anything matched), and then deletes with `git rm` for tracked paths, plain
  `rm` for untracked ones, and both — each on its own paths — for a directory holding a mix. `rm` is
  documented as the normal route for an uncommitted `task/`, not a workaround. `Bash` is still not
  pre-approved for this skill, so `git ls-files` and every delete command ask for confirmation;
  declining the deletion stops the skill and is reported, and switching delete commands to dodge a
  confirmation prompt is prohibited. If you allowlist these to cut down on prompts, the commands to
  allow are `git ls-files`, `git rm` and `rm` — the README's example `settings.json` now lists all three,
  with a warning that allowing `rm` allows every `rm`
- **`doc-consistency-checker` no longer reports "0 stale" for a project it never assessed** - Documents
  with no `sdd-version` were explicitly excluded from the stale list, and that field does not exist in
  anything written before v5, so a project made entirely of pre-v5 documents always got "stale: 0" —
  indistinguishable from a completed migration. Stale (`sdd-version` present, older major) and
  generation-unknown (`sdd-version` absent) are now counted and reported as two separate lists, both
  always shown even when one is zero (e.g. `stale: 0 / generation unknown: 85 of 85 checked`), and both
  are computed with Grep + Glob, so the check is no longer skipped when the document index is disabled
- **`doc-consistency-checker` no longer reports an area it never checked as consistent** - With `adr/`
  empty and only v4.x `specification/*_design.md` files present, the spec ↔ decision-record checks simply
  did not run and the report came back clean. It now branches: entries in `adr/` are checked as before;
  with no entries but a v4.x design document present, the same four checks run against that document and
  are reported as `spec ↔ design (v4.x legacy)`; with neither, the area is reported as `not checked`,
  never as consistent. Every report now opens with which decision record it used, and which checks it
  could not run and why
- **`front-matter-reviewer` can now validate `adr/` documents** - `adr/` was missing from its type
  determination, its id patterns and its cross-reference Glob, so every `adr-*` reference looked
  unresolved, duplicate ids inside `adr/` went undetected, and ADR's own fields were never checked. It now
  determines `type: "adr"` for `adr/*.md` (and `type: "design"` for
  `task/{ticket-number}/design-draft.md`), accepts `adr-*` ids, checks the ADR-specific fields, verifies
  the file-level `supersedes` / `superseded-by` pointers on both sides, and raises an error when an entry
  heading or anchor has been written into those file-level fields instead of the entry body. A missing
  `sdd-version` is reported as info ("generation unknown") rather than silently dropped
- **`spec-reviewer` reviews the design draft** - Its input format and its technical-design section still
  required `specification/{feature}_design.md`, so it could not review what `/generate-spec` now produces.
  It takes `task/{ticket-number}/design-draft.md` — whose absence is normal, in which case the spec ↔
  design traceability check is reported as not applicable — checks ticket scope in place of the retired
  hierarchical structure, asks for the rejected alternatives a later `adr/` entry will need, and reviews a
  v4.x design document as supplementary input
- **`/check-spec` no longer mixes another ticket's design draft into the comparison** - Its helper script
  collected every `design-draft.md` under `task/`, so with several tickets in flight another ticket's
  design was fed in as auxiliary input and produced module-structure warnings against the wrong feature.
  A draft is now selected by `--ticket <number>` when given, otherwise by its `depends-on` matching the
  target spec's id, otherwise by being the only draft in the project; when several candidates remain and
  there is no evidence, none is used, the candidates are listed, and re-running with `--ticket` is
  recommended. The same script also no longer mistakes a leading flag for a feature name, which made
  `/check-spec --full` search for a spec named `--full`
- **`/check-spec` now reports the discrepancies it downgraded** - The `impl-status`-based downgrade of
  Critical findings happens silently, and since v4.x documents have no `impl-status` at all, an entire
  report could be downgraded and then read as "0 Critical". The report now always states how many
  findings were downgraded to Warning (field absent) and to Info (`not-implemented` / `in-progress`),
  even when that is zero, and that downgraded findings are unresolved rather than fixed. The undecidable
  case no longer points at an automatic `impl-status` fix that does not exist — it explains listing the
  specs, checking the implementation, and filling in the value yourself. And because neither the default
  run nor `--full` detects drift between `adr/` and the implementation (`--full` compares spec ↔ adr as
  documents), the report now shows `adr ↔ Implementation: Not checked` with the manual step, and the
  limitation is stated in the skill
- **`/check-spec --full` now actually performs the spec ↔ adr review it advertises** - The mode was
  documented as comparing each spec against its decision log, but nothing resolved which log belonged to
  which spec, the reviewer had no checks defined for that pair, and the English output template had no
  field for the result (only the Japanese one did). `/check-spec` now resolves a decision log per spec —
  by name, mirroring the spec's position under `specification/` (`adr/{feature}.md`, and the legacy
  `adr/{feature}-decisions.md`), and otherwise by an `adr` document whose `depends-on` names that spec —
  honoring a custom `directories.adr`, and hands the resolved paths to `spec-reviewer`. The review asks
  whether the decisions behind the spec's described behavior are recorded at all, whether the current
  decision (the latest entry not reversed by a later one) agrees with the spec, whether the spec still
  relies on a decision a later entry reversed, whether the spec elements an entry cites still exist,
  whether entries carry their required items, and whether the terminology matches. A disagreement is
  fixed either by correcting the spec or by appending a new entry with a `Supersedes` link — never by
  editing an entry already recorded, and never through the file-level front matter fields. A feature
  whose decision log could not be resolved is reported as **not applicable**, never as consistent, and a
  project with no `adr/` directory at all is not an error and produces no warning. This remains a
  document-level review: drift between `adr/` and the implementation stays out of scope, as stated above
- **`recommend-front-matter` recommends the right id for a design draft** - Id generation had no design
  exception, so `task/{ticket-number}/design-draft.md` was given a feature-scoped id that no
  cross-reference could resolve; it is now `design-{ticket-number}` (no feature name, and the ticket
  directory is not treated as a hierarchy parent), while a v4.x `specification/*_design.md` keeps its
  feature-scoped form. `depends-on` inference for a task or implementation log now looks for the draft in
  the same `task/{ticket-number}/` first and falls back to a v4.x design document, with neither being
  present a normal result, and the missing `adr` -> `spec` inference step was added
- **`sdd-init`'s Migration Support no longer describes work it does not do** - It claimed that re-running
  the command generates `${SDD_ROOT}/AI-SDD-PRINCIPLES.md` when missing; that file (and
  `.claude/rules/ai-sdd-instructions.md`) is owned by the SessionStart hook, which re-syncs it every
  session, and the script never touches it. It also detected "this project needs migration" from that
  file's absence — a state the hook makes impossible. Detection is now the absence of `ADR_TEMPLATE.md`
  (an initialization from before the `adr/` document model), the template list covers all four templates,
  and a new subsection walks through migrating a v4.x project to the v5 document model
- **`/constitution sync` now has a step for the ADR template it claims to sync** - `ADR_TEMPLATE.md` was
  listed among the files the command keeps in step with `CONSTITUTION.md`, but the procedure below the
  list jumped straight from the spec/design templates to the task templates, so the file was named and
  then never touched. The procedure now has that step: it adds the principle reference to the entry
  format and aligns the terminology, keeps the required entry items (Decision / Rationale / Rejected
  alternatives) because the skills read them, and touches only the template — the entries already
  recorded in `${SDD_ADR_PATH}/{feature-name}.md` are append-only and are never rewritten by a sync
- **The generated `.claude/rules/ai-sdd-instructions.md` now shows `ADR_TEMPLATE.md` in its directory
  layout** - Both the flat and the hierarchical diagram listed the PRD, spec and design templates but not
  the decision-log template that `/sdd-init` puts next to them, so the file the SessionStart hook re-syncs
  into every project — and that is loaded for any work under `.sdd/` — described a `${SDD_ROOT}/` that did
  not match what initialization actually produces
- **`checklist`'s spec table no longer contradicts its own naming note** - The table marked
  `{feature-name}_spec.md` (and `index_spec.md` for a hierarchical parent) as required, while the note
  below it said the suffix is optional under `specification/`. Either form now satisfies those rows
- **`/constitution validate` no longer skips suffix-free specs** - Its pre-scan globbed
  `specification/**/*_spec.md`, but this release makes the `_spec` suffix optional there, so a spec named
  `{feature-name}.md` was never scanned and its principle compliance silently went unchecked. The scan now
  takes every `.md` under `specification/` except a v4.x `*_design.md`, which keeps its own separate list
- **The constitution template no longer requires a persistent design document** - The shipped
  `CONSTITUTION.md` template (and the `/constitution` examples and report template) told a project to
  require `specification/*_design.md` for every implementation - the document this release retired. Those
  rows now name the v5 documents: the abstract spec (suffix optional), the ticket's temporary
  `task/{ticket-number}/design-draft.md`, and `adr/{feature-name}.md` for the settled decisions
- **v4-era document tables in the PRD template, the implementation log and the vibe-detector report** - The
  PRD template's document comparison, the implementation log's "content to integrate" section and
  `vibe-detector`'s specification-status table all still described `xxx_design.md` as the persistent
  technical document, so a project reading them would keep writing decisions into a file the workflow no
  longer keeps. They now show the spec / design-draft / decision-log split, and the implementation log's
  integration checklist points each item at the matching `adr/` entry item (Decision / Rationale /
  Rejected alternatives)
- **Output templates no longer print command names that do not exist** - Templates and examples across
  `task-breakdown`, `clarify`, `check-spec`, `implement`, `constitution` and `vibe-detector` still told the
  reader to run `/check_spec`, `/generate_spec` or `/task_cleanup` - the pre-v4 underscore spellings, which
  have not been valid command names since the rename to hyphens. They now name the real commands
  (`/check-spec`, `/generate-spec`, `/task-cleanup`)
- **`sdd-init`'s "What This Command Does" list no longer claims it creates `CONSTITUTION.md`** - Item 2 said
  the command generates `${SDD_ROOT}/CONSTITUTION.md` when missing, contradicting three later sections of the
  same file and `init-structure.py`, which deliberately excludes it. It now says the command reports the
  missing file and points at `/constitution init`
- **`run-checklist` reports a missing checklist instead of verifying nothing** - Its error handling covered
  test failures and unavailable tools, but not the checklist itself being absent. It now reports the path
  it resolved, how the ticket was resolved (argument or feature name), and the two ways forward (re-run
  with the ticket number, or generate the checklist with `/checklist`), and it never reports verification
  results for a checklist it could not read
- **PRD-level requirement ID format is resolved from `id_conventions` instead of being hardcoded** -
  `analyze-requirements`, `prd-reviewer`, and `generate-requirements-diagram` hardcoded hyphen notation
  (`UR-xxx` / `FR-xxx` / `NFR-xxx`) while the bundled PRD template and the rest of the pipeline already
  produced `UR_001` / `FR_001`. A project that configured `id_conventions` in `.sdd-config.json` had it
  ignored by those three, and even a default project got requirement-analysis IDs that did not match the
  IDs its own PRD template wrote. All three now resolve the format per
  `shared/references/id_conventions_config.md` § PRD-Level ID Format Resolution, falling back to
  `UR_xxx` / `FR_xxx` / `NFR_xxx`, so a configured convention is honored end to end
- **`check-spec` no longer attaches another ticket's design draft when exactly one draft exists** -
  `find-spec-docs.py`'s sole-draft fallback used to accept the only draft on disk even when its
  `depends-on` front matter named a different spec entirely — positive evidence it belongs to another
  feature, not merely an untagged draft that happens to be alone. That draft is now excluded from the
  sole-draft exception and the run falls back to `unscoped` (or to a remaining untagged draft, if one
  exists)
- **`check-spec` / `constitution validate` no longer misclassify a spec named e.g. `api_design.md` as a
  legacy v4.x design doc** - The `_spec` suffix is optional under `specification/`, so a legitimately
  named new spec can itself end in `_design`; the filename-only heuristic could not tell the two apart
  and silently dropped such a spec from both commands' output. A file's own front matter `type` now
  overrides the heuristic when declared
- **`post-tool-use.py`'s spec-sync reminder now matches a source file name literally, even when it
  contains glob metacharacters** - `find_spec_doc` / `find_legacy_design_doc` interpolated the file's
  stem unescaped into an `rglob` pattern, so a file like `parse[v2].py` had `[v2]` treated as a wildcard
  character class instead of literal text, silencing the reminder for a spec that actually existed. The
  same fix applies to `check-spec`'s CLI target argument in its partial-match fallback
- **`run-checklist`'s verification script no longer reports `SKIPPED` when every candidate tool for a
  category is genuinely missing** - It now reports `TOOL_NOT_FOUND`, matching the status SKILL.md
  already documents for that case (`SKIPPED` remains reserved for "no command is defined for this
  category" and "the tool ran but had nothing to verify")
- **`run-checklist`'s verification script no longer risks an uncaught crash decoding non-UTF-8 tool
  output** - `subprocess.run` now decodes with `errors="replace"` instead of the locale's default, which
  could raise `UnicodeDecodeError` in a non-UTF-8 locale (e.g. a `LANG=C` CI container) and abort the
  script without producing the JSON result the skill expects
- **`evaluate-skills`' safety-guard audit no longer stops checking a keyword after its first, negated
  occurrence** - `audit_run_artifacts.py` located only the first occurrence of each keyword in a
  transcript; if that occurrence sat in a negated context ("...must not skip the check..."), a genuine
  later violation of the same keyword was never examined
- **`evaluate-skills`' skill-creator path resolver no longer aborts silently when no version has ever
  been cached** - Under `set -euo pipefail`, `find` failing on a nonexistent cache directory short-circuited
  the script before it could print its own "not installed" error message. It also no longer picks the
  wrong "latest" version when multiple are cached: the cache directories are named by an installation
  hash, not a sortable version number, so a lexical `sort` had no real ordering signal; it now picks by
  modification time instead

### Changed

#### Naming

- **`_spec`/`_design`/`-decisions` suffix is now optional under `specification/` and `adr/`** - Both are
  single-type directories (every file is an abstract spec / a decision log respectively), so the
  naming-enforcement hook no longer requires a suffix there. Existing suffixed files remain valid.
  `requirement/` is unaffected — a `_spec`/`_design` suffix is still forbidden there
- **Generation skills now default to `adr/{feature}.md` (no `-decisions` suffix) for new ADR files** -
  `task-cleanup`, `generate-spec`, `render-adr-review`, `doc-consistency-checker`, `sdd-init`,
  `implement`, and the shared `document_dependencies.md` reference now show the suffix-free filename as
  the default when creating a new decision log. Existing `-decisions.md` files remain valid and are
  still discovered/edited in place; `naming.py` validation is unchanged

#### Hooks

- **The post-edit reminder now points at the spec, not a design document** - After a source file edit,
  the `PostToolUse` hook looks for a matching spec (`{stem}_spec.md`, then `{stem}.md`) under
  `specification/` and asks for the spec to be kept in sync. Previously it looked for
  `{stem}_design.md`, which no longer exists as a persistent document, so the reminder never fired.
  The `.sdd/` document reminders now refer to PRD ↔ spec ↔ adr
- **A feature that has only a v4.x design document still gets a reminder** - With the lookup moved to the
  spec, editing source for a feature whose only document is `specification/{stem}_design.md` produced no
  output at all, silently dropping the reminder such projects used to get. That case now has its own
  message: the design document is valid supplementary reading, its decisions belong in
  `adr/{feature-name}.md`, and it should not be deleted before that is done. The steps are named as a
  path you can open — `<plugin root>/README.md`, section "Extracting Existing `*_design.md` Files into
  `adr/`" under "Migration from v4.x" — rather than "see the plugin README". When a spec exists the
  unchanged spec-sync reminder is used instead, and only ever one message is emitted
- **`adr/` edits now get a reminder** - Editing a decision log used to produce no output at all. It now
  reminds that decision logs are append-only and that a decision changing the specification must be
  reflected in the spec

#### Skills

- **Downstream skills now read the Design Doc from `task/{ticket-number}/design-draft.md`** -
  `task-breakdown`, `implement`, `checklist`, and `clarify` still pointed at the retired
  `specification/{feature}_design.md`, which `/generate-spec` no longer produces. Following
  `/generate-spec` → `/task-breakdown` → `/implement` therefore dead-locked: the design document the
  downstream skills required could never be created. All four now resolve the draft at the ticket-scoped
  fixed path, which is independent of the spec's flat/hierarchical structure
- **`checklist` and `clarify` treat the design draft as an optional input** - The draft is deleted at
  implementation completion, so its absence no longer blocks these skills; they continue with the
  abstract spec (and PRD/`tasks.md` when present). `clarify` takes an optional `ticket-number` argument
  to locate the draft. When the draft is gone but the project still has a v4.x
  `specification/{feature-name}_design.md` (or `index_design.md` for a hierarchical parent), the
  design-level questions and Design Review items come from that document instead of being dropped
- **`task-breakdown` and `implement` set `depends-on` to the ticket-scoped design ID** - The instructions
  said `design-{feature-name}` while the draft's own `id` is `design-{ticket-number}`, so the
  cross-reference check in `front-matter-reviewer` always failed. Both now instruct
  `["design-{ticket-number}"]`, and the `type: "design"` schema in `shared/references/front_matter_reference.md`
  was corrected to match
- **`implement` accepts an abstract spec with or without the `_spec` suffix** - The suffix became optional
  under `specification/`, but the prerequisite check still demanded `{feature}_spec.md`; either
  `{feature}.md` or `{feature}_spec.md` now satisfies it
- **`/plan-refactor` hands its decisions off to `adr/`** - The completion output now points at
  `/task-cleanup`, which appends the settled decisions to `adr/{feature-name}.md` before the design draft
  (and with it the refactoring plan) is deleted. The skill deliberately does not write to `adr/` itself:
  a plan is a proposal, and only settled decisions belong in an append-only log
- **`doc-consistency-checker` points PRD-update recommendations at `/generate-prd --amend`** - When a spec
  change contradicts a PRD requirement and a human chooses to update the PRD, the recommended path is now
  `/generate-prd --amend` instead of an unspecified manual edit
- **A ticket number can be passed as `--ticket <number>` or `--ticket=<number>` to every skill that takes
  one** - The skills each documented one form or the other, so a habit learned from one did not carry
  over. All ten skills that accept a ticket number — `/generate-spec`, `/plan-refactor`,
  `/task-breakdown`, `/implement`, `/checklist`, `/run-checklist`, `/clarify`, `/task-cleanup`,
  `/check-spec` and `/render-adr-review` — now state that both forms are accepted and equivalent, and
  that where the number is a positional argument
  the flag form does not consume the positional slot. `/render-adr-review` in particular also stopped
  taking a flag that landed in a positional slot as a value, so
  `/render-adr-review adr/x.md --ticket=123` no longer names its output file
  `--ticket=123-review.html`. `/generate-spec`'s `argument-hint` also lists
  `--ticket`, `--ci` and `--amend`, which never appeared in completion before. In `--ci` mode a missing
  ticket number stops the skill before anything is read or written, naming the missing argument and
  showing a corrected invocation, instead of inventing a placeholder number or a `task/unknown/` directory
- **The skills that allow omitting the ticket number now state what they resolved** - `/implement`,
  `/checklist`, `/run-checklist`, `/clarify` and `/task-cleanup` fall back to the feature name (or to the
  whole `task/` directory), which quietly changes which paths are read and written. Each now states the
  resolved path in its output, and when nothing is found there it reports that path, that the omitted
  ticket number is the likely cause, and the two ways forward — instead of searching other task
  directories or starting work without the document it needed. `/clarify` also states when it analyzed the
  PRD, the spec and any v4.x design document alone, so the reduced coverage of design-related questions
  is visible
- **`recommend-front-matter` reports specs missing `impl-status`, and never writes the field** - `--apply`
  used to add `impl-status: "not-implemented"` to specs that already had front matter, and include it in
  the block it wrote for documents that had none. That value is a claim about the implementation, which
  this skill does not inspect, and writing `not-implemented` onto an already-implemented spec turns
  `/check-spec`'s regression detection (Critical) into an expected-gap note (Info) — the exact failure the
  field exists to catch. It now leaves every document that already has front matter untouched, omits
  `impl-status` from the blocks it writes, and simply lists the specs missing the field so you can check
  the implementation and fill in `implemented` / `in-progress` / `not-implemented` yourself. The approval
  prompt's count is now just the documents that have no front matter
- **`task-cleanup`'s decision-log append follows the settled entry format** - The instruction was to
  "append to the end" and "match the structure of existing entries", which left the heading shape and the
  item names to chance. One decision is now one `## YYYY-MM-DD {decision title}` entry carrying Decision /
  Rationale / Rejected alternatives (`None considered` when there were none, never invented) and an
  optional `Supersedes` link to an earlier entry in the same file. Rewriting, reordering or deleting
  existing entries is prohibited, a superseded entry is not edited at all, and a reversal must not be
  written into the file-level `supersedes` / `superseded-by` front matter fields
- **`task-cleanup` names a destination for the know-how it deletes** - Implementation tips,
  troubleshooting notes and performance findings were classified as safe to delete with nowhere to put
  them, so they were simply lost. Know-how is not a decision and does not become an `adr/` entry (it can
  appear as part of a decision's rationale); the skill now requires a destination for each item it drops —
  a code comment, a test that pins the behavior, or the `*_spec.md` — and reports where each one went
- **`/plan-refactor`'s technical debt observations now get a persistent destination** - They were written
  into the design draft and vanished with it. Each observation is now assigned one of three destinations:
  debt this refactoring resolves goes into the rationale of the `adr/` entry `/task-cleanup` appends; debt
  deliberately deferred becomes a tracker item whose id is recorded in the plan (and, when deferring is
  itself a decision, its own entry at cleanup); debt where the implementation contradicts the spec becomes
  a proposed `*_spec.md` correction for a human to approve. No new debt document is created — v5 has no
  standing debt ledger and `adr/` records decisions — and the completion output lists any observation left
  without a destination
- **`/plan-refactor` states which parts of its reverse-engineered analysis survive the ticket** - In Case
  B it inventories the existing implementation into the design draft — which is deleted at cleanup — and
  nothing said which of those findings were meant to reach a persistent document, so the whole inventory
  was silently thrown away every ticket. The boundary is now explicit, and the reverse-engineering
  templates have a place for each part that persists: externally observable data flow goes into a new
  "Behavior and Data Flow" section of the reverse-engineered spec, the module boundaries other code
  depends on go into its "Internal Interfaces" section (contracts only, not the files behind them), and
  the architecture pattern name goes into its implementation notes. Component breakdowns, directory
  layout, inter-component dependencies, internal call order, algorithm walkthroughs, state-management
  internals and coverage numbers are deliberately **not** persisted: they are re-derivable from the code,
  a copy in a document drifts from it, and the spec template excludes them by design. The Case B
  completion output now tells you which findings were carried into the spec and which were dropped on
  purpose. `/task-cleanup` classifies the same structure descriptions as safe to delete for the same
  reason, and does not ask you to find them a home — while a *decision* about structure still becomes an
  `adr/` entry

#### Documentation

- **`AI-SDD-PRINCIPLES.md`** - Adds a `spec ↔ Implementation` row to the Consistency Checking table as
  the persistent implementation check, and reframes `design ↔ Implementation` as valid only while a
  design draft exists. Documents the `adr/` directory and the `design-draft.md` lifecycle, and
  makes explicit that `requirement/` (PRD) is never auto-updated from downstream spec/design/
  implementation changes — contradictions are reported for a human to resolve, not silently written back
- **`shared/references/document_dependencies.md`** - Updated to the `adr/` model (previously still
  described `specification/*_design.md` as persistent, out of sync with the rest of the redesign)
- **`check-spec`'s front-matter-reviewer delegation now states explicitly when it could not run** -
  Previously, an environment where agent delegation is unavailable silently skipped front matter
  validation while still reporting the check as done. It now says so and lists it as a manual review item
- **`generate-prd`'s prd-reviewer / front-matter-reviewer delegation has the same explicit fallback** -
  Same fix as above, applied to both call sites (initial generation and `--amend`)
- **`checklist` items now disclose their basis** - Each item states which document and statement it was
  derived from, or `synthesized from: {component}` when inferred from an implementation component's
  existence rather than quoted from a document, so a reviewer can tell "extracted" from "invented"
- **`clarify` now records a Clear/Partial/Missing classification for all 9 categories**, not only the
  ones that became a question, so the analysis's actual coverage is visible in the output
- **`generate-requirements-diagram` states a priority when completeness and the 10-15-requirement
  readability guideline conflict** - Completeness wins; split into a per-subsystem diagram first, and
  only compress sub-requirements into a single annotated node when splitting does not apply, stating
  explicitly which sub-requirements were compressed and why
- **`clarify` now checks the implementation before flagging an NFR/constraint as ambiguous** - When the
  target feature's `impl-status` is `implemented`, an apparently undefined threshold or timeout may
  already be a concrete decision recorded only in code (a `TIMEOUT_SECONDS` constant, for example)
  rather than in the spec's prose; the analysis now searches the implementation for that value before
  raising a question the codebase has already settled
- **`generate-requirements-diagram` no longer edits the target document to fill a missing diagram
  section** - The "returns text only" contract now says explicitly that a missing section must not be
  "helpfully" filled in with `Write`/`Edit`; the diagram is still returned as text, leaving the write
  decision to the caller
- **`checklist` requires a priority on every item, in every category** - Including any category added
  beyond the standard nine (e.g. a principle-compliance category), and the priority-scheme origin note
  now requires an actual comparison between the SKILL.md body and the template rather than a copy of the
  reminder text
- **`check-spec` matches NFRs individually against the implementation, the same way FRs are** - A closing
  summary sentence for NFRs no longer satisfies the per-requirement matching check; severity
  classification also now states explicitly that severity tracks impact (public interface / observable
  behavior / data model vs. internal-only), not detection confidence
- **`task-cleanup`'s ADR entry-format guidance no longer duplicates the full field table already defined
  in `AI-SDD-PRINCIPLES.md`** - It now references that table as the canonical source and keeps only the
  cleanup-specific refinements (heading date sourcing, the "None considered" wording) locally, so the
  two copies cannot silently drift apart
- **The `PreToolUse` hook reads `.sdd-config.json` once per tool call instead of twice** - Path resolution
  and the naming-ignore-pattern lookup each used to open and parse the file independently on every
  single Write/Edit
- **The `PostToolUse` hook's spec-sync reminder walks `specification/` once per source-file edit instead
  of up to three times** - `find_spec_doc`'s two suffix candidates and the separate `find_legacy_design_doc`
  fallback are now resolved from a single directory listing

## [4.1.0] - 2026-08-19

### Added

#### Configuration

- **`naming.ignore_patterns` in `.sdd-config.json`** - Glob patterns (e.g. `"*_test.md"`) matched
  against a file's basename to exempt it from the `requirement`/`specification` naming convention
  check, so intentionally non-conforming files (test fixtures, etc.) no longer get blocked

## [4.0.1] - 2026-07-28

### Changed

#### Permissions

- **Write access is no longer pre-approved wholesale** - A skill's `allowed-tools` grants tools *without
  asking*; it is a pre-approval, not a restriction. Eleven skills listed a bare `Write` / `Edit`, which
  pre-approved writing to any path. Writes are now scoped with the `Edit(<path>)` rule form -
  `Edit(.sdd/**)` plus `Edit(CLAUDE.md)`, `Edit(.sdd-config.json)` and `Edit(.claude/rules/**)` where a
  skill legitimately needs them. Writing outside those paths now asks for confirmation.
  Note that `Write(<path>)` is not a valid rule form; `Edit(<path>)` covers every file-editing tool
- **Shell access is limited to the plugin's own scripts** - Ten skills listed a bare `Bash`, which
  pre-approved any command. The seven skills that only run a bundled helper now name it explicitly, e.g.
  `Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-design-docs.py" *)`
- **`Bash` removed from three skills** - `implement` and `run-checklist` run arbitrary project test,
  lint and scanner commands, and `task-cleanup` runs `git rm` / `git rm -r`. None of those should be
  pre-approved, so they now ask before running a command
- Projects that set a custom `root` in `.sdd-config.json` will be asked to confirm writes, because
  `${SDD_ROOT}` is not expanded in `allowed-tools`. See the README for a settings snippet that
  pre-approves a custom root

#### Plugin Layout

- **Agent support files moved out of `agents/`** - `agents/references/`, `agents/examples/` and
  `agents/templates/{en,ja}/` now live under `shared/` (`shared/references/`, `shared/examples/`,
  `shared/templates/{en,ja}/`), leaving `agents/` with nothing but the six agent definitions.
  `claude plugin validate --strict` scans `agents/**` recursively and ignores the manifest's `agents`
  array, so every support file parked there was reported as an agent without front matter
- **Agent reference paths are now absolute** - The 33 reference, example and template paths in the agent
  prompts use `${CLAUDE_PLUGIN_ROOT}/shared/...` instead of a bare relative path. The previous form
  depended on the reader resolving the path relative to the agent file; the placeholder resolves
  anywhere in agent content, so the target is now unambiguous
- Five symlinks under `agents/references/` that pointed into `shared/references/` are gone; the agents
  reference those files directly

### Fixed

#### Agents

- **Tool restrictions were not applied** - All six agents declared their tool allowlist with
  `allowed-tools:`, which is a skill-only front matter key. Subagents recognize `tools:` /
  `disallowedTools:`, so the declaration was silently ignored and every agent inherited **all** tools,
  including `Write` / `Edit` / `Bash`. Renamed the key to `tools:`, restoring the intended read-only
  scope (`Read`, `Glob`, `Grep`, `AskUserQuestion`)

#### Skills

- **Model selection was not applied** - Eight skills selected a model with `agent: sonnet` / `agent:
  haiku`. The `agent` field names a *subagent type* and only applies when `context: fork` is set, so a
  model alias there was silently ignored and fell back to `general-purpose`. Switched to the `model:`
  field, which applies whether or not the skill forks

#### Hooks

- **Hooks failed when the install path contained a space** - `${CLAUDE_PLUGIN_ROOT}` was unquoted in all
  four hook commands, so the path was word-split and every hook failed to start under such paths (for
  example a `$HOME` containing a space). The variable is now quoted
- **Stale tool name in matchers** - `PreToolUse` / `PostToolUse` matched `Write|Edit|MultiEdit`, but
  `MultiEdit` is no longer a Claude Code tool. Narrowed the matchers to `Write|Edit`

#### Plugin Manifest

- **Duplicate hooks load** - Removed the `"hooks": "./hooks/hooks.json"` declaration from `plugin.json`.
  Claude Code auto-detects `hooks/hooks.json` at the plugin root, and a manifest path supplements the
  default path rather than replacing it, so declaring the standard path loaded the same file twice and
  surfaced a `Duplicate hooks file detected` error on plugin load. Hook behavior itself is unchanged
- **Redundant skills declaration** - Removed `"skills": "./skills"`. The default `skills/` directory is
  always scanned and the `skills` field only *adds* to that scan, so declaring the standard path had no
  effect. All 19 skills continue to load

#### Documentation

- **Japanese README was out of sync with the English one** - `README.ja.md` listed 5 agents (6 exist) and
  1 hook (4 exist), documented `ja` as the default for `SDD_LANG` and `.sdd-config.json` `lang` (the
  default is `en`), and listed 1 of the 10 files under `scripts/`. Both READMEs are now aligned

## [4.0.0] - 2026-07-16

### Added

#### Agents

- **`cross-prd-reviewer`** - New agent that reviews consistency across multiple PRDs
    - Checks category boundary consistency (scope-out cross-references), terminology alignment across
      glossaries, structure and notation style uniformity, CONSTITUTION.md principle reference coverage,
      and front matter labeling consistency
    - Findings are classified as [must]/[recommend]/[nits]; single-PRD quality remains prd-reviewer's role
    - Adds `templates/{en,ja}/cross_prd_review_output.md` output templates

#### Configuration

- **`.sdd-config.json` `index`** - New boolean setting that controls the compressed `.sdd` document index
  built at session start to reduce token consumption
    - **Enabled by default** (`true`). Set `"index": false` to opt out
    - Auto-generated `.sdd-config.json` now includes `"index": true` explicitly for discoverability
    - **Index extraction expansion** - The index now also covers SysML requirement diagrams and data model
      fields, so the SysML trace axis that previously required raw reads is included in the token-reduction index

### Changed

#### Configuration

- **`.sdd-config.json` `index`** - Value format is now **boolean-only** (`true`/`false`); the previous
  string form (`"on"`/`"off"`) is no longer supported. A non-boolean value is rejected with a warning and
  falls back to the default (on)
    - The default changed from **off to on**, so the token-reduction index is built out of the box

#### Hooks

- **`PreToolUse`** - Injects `.sdd/CONSTITUTION.md` principles as `additionalContext` when Write/Edit
  targets implementation source code
    - Injection is limited to source-file edits inside the project, happens at most once per session,
      and is truncated to 3000 characters to avoid context bloat
    - Nothing is injected when CONSTITUTION.md does not exist

#### Agents

- **`front-matter-reviewer`** - Changed `model` from `sonnet` to `haiku`
    - Rule-based format validation does not require complex reasoning; a lightweight model reduces cost and latency
    - Other agents (prd-reviewer, spec-reviewer, requirement-analyzer, clarification-assistant) keep `sonnet`

#### Skills

- **Model tiers** - Reduced the model for mechanical / rule-based skills to cut cost and latency
    - `generate-requirements-diagram` / `generate-usecase-diagram` - `agent` changed from `sonnet` to `haiku`
    - `recommend-front-matter` / `run-checklist` / `sdd-init` / `task-cleanup` - now declare `agent: haiku`
- **`sdd-init`** / **SessionStart hook** - Moved the detailed AI-SDD guide out of the always-loaded
  `CLAUDE.md` into a path-scoped rule `.claude/rules/ai-sdd-instructions.md` (loads only under `.sdd/**`)
  to cut context usage during work that does not touch `.sdd/`
    - `CLAUDE.md` now keeps only the declaration, trigger conditions, and a pointer to the rule;
      the ~90-line directory-structure / naming / link-convention block moved to the rule file
    - The rule file is created and version-synced automatically by the SessionStart hook
      (`session-start.py`); `/sdd-init` (`update-claude-md.sh`) only maintains the minimal `CLAUDE.md` section
    - The rule is a single English file (agent-facing guidance, not human-facing) regardless of `SDD_LANG`,
      so no per-language rule files ever load together
      because they require cross-document consistency reasoning

#### Skills

- Introduced named skill arguments via the `arguments` frontmatter field (Claude Code v2.1.199+)
    - 8 skills (`task-breakdown`, `implement`, `clarify`, `check-spec`, `checklist`, `run-checklist`,
      `task-cleanup`, `plan-refactor`) now declare `feature-name` / `ticket-number` as named positional
      arguments and reference them via `$name` substitution in the skill body
    - Free-text-input skills (`generate-spec`, `generate-prd`, etc.) keep interpreting the whole
      `$ARGUMENTS` string
    - Each skill body documents a fallback: when a value is empty, unsubstituted, or a positionally
      captured flag (`--...`), the skill falls back to interpreting the full argument string or asking
      the user interactively, preserving pre-v2.1.199 behavior

### Added

#### Hooks

- Expanded `hooks.json` beyond `SessionStart`
    - **`UserPromptSubmit`** (`scripts/user-prompt-submit.py`) - Detects Vibe Coding signals (vague instructions such
      as "make it nice" / "いい感じに") in the user prompt and injects additional context prompting a vibe-detector
      style clarification flow (detection only, never blocks)
    - **`PreToolUse`** (`scripts/pre-tool-use.py`, matcher `Write|Edit|MultiEdit`) - Validates AI-SDD file naming
      conventions before writing under `.sdd/` (requirement: no suffix, specification: `_spec.md` / `_design.md`
      required) and blocks violating writes
    - **`PostToolUse`** (`scripts/post-tool-use.py`, matcher `Write|Edit|MultiEdit`) - Detects potential document
      update omissions: reminds to run consistency checks after `.sdd/` document edits, and reminds to sync the
      design doc after editing a source file with a matching `*_design.md`

#### Agents

- **`requirement-analyzer`** - Added ID numbering validation (`--validate-ids`, also runs as part of `--analyze`)
    - Naming convention validation via configurable regex patterns (`id_conventions` section in `.sdd-config.json`)
    - Ascending order validation with move suggestions for out-of-order ID sequences
    - Numbering gap detection and stale-ID detection after renames
    - Added "ID Numbering Validation" section to `requirement_analysis_output` templates (en/ja)

#### Documentation

- **`AI-SDD-PRINCIPLES`** - Documented the optional `id_conventions` section of `.sdd-config.json`

#### Skills

- **`check-spec`** (v3.1.0) - Extended consistency check to literal values
    - Parses the spec's "Value Range / Threshold Registry" (Schema Registry) section when present, with fallback to
      extracting literal values from spec/design body text
    - Extracts implementation-side literals from config files, ORM CHECK constraints, validation constraints
      (e.g., Pydantic), and language-specific enums/constants
    - Detects value drift across spec / design / implementation and reports it as a Warning
      (e.g., spec `0.7` vs `config.py` `0.6`)
    - Verifies enum / CHECK constraint member-set completeness and requirement ID trace completeness
      (PRD <-> spec <-> design)
    - Added value drift sections to output templates (en/ja)
- **`generate-spec`** - Added "Pseudocode Completeness Rules" section to design doc templates (`templates/{en,ja}/design_template.md`)
    - Language-specific guidance (Python general / Pydantic v2 / SQLAlchemy & alembic) to keep design pseudocode copyable verbatim
    - Extensible sub-section structure for additional languages (TypeScript / Go / Rust, etc.)

### Fixed

- **Custom `.sdd-config.json` `root` (and directory names) are now honored across the plugin.** Previously
  many paths were hardcoded to the default `.sdd/`, so projects using a custom root silently broke.
    - `session-start.py` substitutes the configured root into the generated path-scoped rule's `paths:` glob,
      so `.claude/rules/ai-sdd-instructions.md` auto-loads under a customized root (e.g. `.ai-docs/`) — this
      also fixes the regression where the glob was baked to `.sdd/**`
    - `update-claude-md.sh` substitutes the configured root into the generated `CLAUDE.md` section
    - Skill/agent prompts and output templates now resolve SDD paths via `${SDD_ROOT}` / `${SDD_*_PATH}`
      instead of literal `.sdd/...`
    - `find-design-docs.sh` and `validate-files.sh` write their cache under the configured root; `pre-tool-use.py`
      naming-violation messages report the configured directory paths
- **`post-tool-use.py`** - The advisory hint shown after editing `.sdd/requirement/` or `.sdd/specification/`
  files now also suggests `/constitution validate`, not just the `doc-consistency-checker` skill, so
  CONSTITUTION.md principle violations are more likely to be caught after generation/edits
- **`doc-consistency-checker`** - Removed the `design ↔ Implementation` check (former spec FR-004), which
  duplicated `impl-spec-check` (`/check-spec`) and contradicted the parent PRD's explicit scope-out for that
  check. `design ↔ Implementation` consistency is now handled exclusively by `/check-spec`
- **Section requirement markers in generated output** - Prevented author-facing section requirement
  markers (`<MUST>` / `<RECOMMENDED>` / `<OPTIONAL>`) from leaking into generated documents. `generate-spec`
  now strips them from headings in the final output, and `prd-reviewer` / `spec-reviewer` gained a
  "No Marker Residue" check that flags any residual markers

## [3.3.0] - 2026-03-02

### Changed

#### Hooks

- **`session-start`** - Migrated `session-start.sh` (Bash) to `session-start.py` (Python 3.7+)
    - Eliminated `jq` dependency by using Python's built-in `json` module
    - Unified script across `sdd-workflow` and `sdd-workflow-ja` via `--default-lang` argument
    - `sdd-workflow-ja/scripts/` is now a symlink to `sdd-workflow/scripts/` (deduplication)
    - Added error handling for invalid `.sdd-config.json` (graceful fallback to defaults)
    - Requires Python 3.7+ (for `dataclasses` and `subprocess.run(capture_output=True)`)

#### Documentation

- Added `README.ja.md` as the Japanese README for `sdd-workflow` plugin
- Removed standalone `sdd-workflow-ja/README.md` (now symlinked to `sdd-workflow/README.ja.md`)
- Added CI badge and license badge to root `README.md`

## [3.2.1] - 2026-02-26

### Fixed

#### Hooks

- **`hooks.json`** - Workaround for Claude Code Issue [#24529](https://github.com/anthropics/claude-code/issues/24529)
    - `CLAUDE_PLUGIN_ROOT` is not set as an environment variable during hook execution
    - Explicitly set `CLAUDE_PLUGIN_ROOT` in the hook command to ensure availability in `session-start.sh`
    - Before: `source ${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh`
    - After: `CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT} source ${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh`

## [3.2.0] - 2026-02-25

### Added

#### Skills

- **`recommend-front-matter`** - New skill to recommend adding YAML front matter to existing documents
    - Scans all AI-SDD documents (PRD, spec, design, task) for front matter presence
    - Generates recommendations with inferred metadata (id, title, type, status, depends-on, tags, category)
    - Supports automatic application with `--apply` option after user confirmation
    - Provides bilingual report templates (en/ja)
    - Includes document scanning script (`scan-documents.sh`)

#### Agents

- **`front-matter-reviewer`** - New agent for validating YAML front matter in AI-SDD documents
    - Checks field formats, dependency direction, status values, and type-specific fields
    - Validates cross-reference integrity and id uniqueness
    - Use after document generation or during consistency checks

#### Shared References

- **`shared/references/`** - Added YAML front matter reference documents
    - `front_matter_reference.md` - Comprehensive front matter field reference
    - `front_matter_prd.md` - PRD-specific front matter guide
    - `front_matter_spec_design.md` - Spec/design-specific front matter guide
    - `front_matter_task.md` - Task-specific front matter guide
    - `front_matter_impl.md` - Implementation log-specific front matter guide

### Removed

#### Skills

- **`sdd-migrate`** - Legacy migration skill removed (v1.x → v2.0.0 directory structure migration)
    - Migration functionality is no longer needed for current users
    - Reduces maintenance overhead and code complexity

#### Hooks

- **`session-start.sh`** - Removed legacy directory structure detection and auto-migration logic
    - Simplified `.sdd-config.json` generation to default values only
    - Removes lines 29-82 (legacy detection and migration warning)

#### Documentation

- **`sdd-init/SKILL.md`** - Removed reference to v3.0.0 migration (`lang` field addition)

## [3.1.1] - 2026-02-23

### Changed

#### Hooks

- **`session-start.sh`** - Improved POSIX compatibility and robustness
    - Added `CLAUDE_PLUGIN_ROOT` guard check at script entry
    - Replaced `&> /dev/null` with POSIX-compatible `>/dev/null 2>&1`
    - Removed unnecessary `>&2` redirections from echo statements
    - Simplified `CLAUDE_PLUGIN_ROOT` existence check for principles copy

#### Skills

- **`plan-refactor`** - Fixed template/reference file path references to use snake_case
    - `refactor-plan-section.md` → `refactor_plan_section.md`
    - `reverse-design-template.md` → `reverse_design_template.md`
    - `reverse-spec-template.md` → `reverse_spec_template.md`
    - `design-doc-integration.md` → `design_doc_integration.md`
    - Renamed actual files in `templates/` and `references/` to match

## [3.1.0] - 2026-02-15

### Added

- **plan-refactor skill** - New skill to support refactoring planning for existing features
    - Analyzes current implementation and creates/updates design documents with refactoring plan
    - Supports two scenarios: Case A (existing documents) and Case B (no documents)
    - Provides templates, samples, and reference documents in both Japanese and English
    - Includes refactoring pattern references (Extract Interface, Dependency Injection, etc.)
    - Implementation file search script (`find-implementation-files.sh`)
    - Existing document scan script (`scan-existing-docs.sh`)
- **Agent samples and reference documents** - Improved usability
    - `clarification-assistant`: Added usage examples and clarification workflow references
    - `prd-reviewer`: Added usage examples
    - `requirement-analyzer`: Added usage examples
    - `spec-reviewer`: Added usage examples
    - Added stop report format templates (en/ja) for all agents
    - Added directory structure references and fix proposal flow references
- **SKILL.md argument-hint** - Added `argument-hint` field to all skills to clarify argument specifications

### Changed

- **/constitution init** - Added context argument for non-interactive mode initialization
    - Specify `[context]` argument to generate principles based on project context without interaction
    - Without argument, runs in interactive mode as before
- **Agent configuration files** - Improved Markdown format to enhance code block extraction accuracy
    - clarification-assistant: Reduced verbose descriptions for more concise structure (103 lines reduced)
    - prd-reviewer: Organized workflow descriptions
    - requirement-analyzer: Improved analysis flow descriptions
    - spec-reviewer: Organized review process descriptions

### Fixed

- **plan-refactor template language neutralization** - Removed dependency on specific technologies
    - `reverse-design-template.md`: Removed specific examples like TypeScript, React, PostgreSQL
    - `reverse-design-template.md`: Removed language-specific code blocks (typescript, sql)
    - API endpoints section: Simplified by removing sample rows, keeping only table headers
    - Database schema section: Completely removed as it cannot be reverse-engineered from implementation
    - Function signatures section: Completely removed due to TypeScript-specific nature
    - Changed placeholders to descriptive guidance format (e.g., `{e.g., TypeScript}` →
      `{Programming language used in the project}`)

## [3.0.2] - 2026-02-09

### Fixed

- **`sdd-init`** - Fixed language setting inheritance from `.sdd-config.json`
    - `update-claude-md.sh` now reads `SDD_LANG` directly from `.sdd-config.json` instead of relying on environment
      variable
    - Previously, when `lang: "ja"` was set in `.sdd-config.json`, the `## AI-SDD Instructions` section in `CLAUDE.md`
      was incorrectly generated in English
    - Root cause: `CLAUDE_ENV_FILE` writes from `init-structure.sh` were not reflected in the same shell session when
      `update-claude-md.sh` ran

## [3.0.1] - 2026-02-09

### Added

#### New Skills (PRD Generation Workflow)

- **`/generate-usecase-diagram`** - Use case diagram generation skill
    - Generates Mermaid flowchart-based use case diagrams from business requirements
    - `context: fork` for context isolation
    - Supports Interactive and CI (`--ci`) modes
    - Returns text only (no file write)

- **`/analyze-requirements`** - Requirements analysis skill
    - Extracts UR (User Requirements), FR (Functional Requirements), NFR (Non-Functional Requirements)
    - `context: fork` for context isolation
    - Supports MoSCoW prioritization and risk assessment
    - Returns text only (no file write)

- **`/generate-requirements-diagram`** - SysML requirements diagram generation skill
    - Generates Mermaid requirementDiagram from requirements analysis
    - `context: fork` for context isolation
    - Supports requirement relationships (contains, derives, traces)
    - Returns text only (no file write)

- **`/finalize-prd`** - PRD integration skill
    - Integrates use case diagram, requirements analysis, and requirements diagram into complete PRD
    - `context: fork` for context isolation
    - Follows PRD template structure
    - Returns text only (no file write)

#### Skills Enhancements

- **`sdd-init`** - Added automatic `.sdd-config.json` `lang` field management
    - If config file doesn't exist: Create with default settings (including `lang: "en"`)
    - If config file exists but missing `lang` field (v3.0.0 migration): Add `lang: "en"`
    - Added step 1.5 "Manage Configuration File" to execution flow
    - Added shell scripts: `init-structure.sh`, `update-claude-md.sh`

- **`check-spec`** - Added shell script for file scanning
    - `scripts/find-design-docs.sh` - Pre-scans design documents to reduce Claude's Glob/Grep overhead

- **`constitution`** - Added shell script for validation
    - `scripts/validate-files.sh` - Pre-scans requirement/spec/design files for validation

- **`generate-spec`** - Added shell script for preparation
    - `scripts/prepare-spec.sh` - Pre-processes files for spec generation

#### Documentation

- **Added notes to Mermaid notation guides**
    - Labels containing `<` and `>` (like `<<include>>`) must be escaped using HTML entities
    - Example: Write `&lt;&lt;include&gt;&gt;` to display `<<include>>`

- **Added reference files for Progressive Disclosure**
    - `clarify/references/nine_category_analysis.md` - 9-category analysis definitions
    - `constitution/references/best_practices.md` - Constitution best practices
    - `constitution/examples/validation_report.md` - Validation report example

### Changed

#### Skills Architecture

- **`generate-prd`** - Refactored to orchestrator pattern
    - Now orchestrates 4 sub-skills: `/generate-usecase-diagram`, `/analyze-requirements`,
      `/generate-requirements-diagram`, `/finalize-prd`
    - Sub-skills run with `context: fork` for context isolation
    - Sub-skills return text only; `generate-prd` handles file writes
    - Reduced SKILL.md from 374 lines to 140 lines
    - Added Progress Checklist for workflow tracking

- **All skills** - Claude Code Skills Best Practices compliance
    - Added `$ARGUMENTS` placeholder and `## Input` section to all skills
    - Added `allowed-tools` to frontmatter where missing
    - Added `Quality Checks` section before output
    - SKILL.md files kept under 500 lines (Progressive Disclosure pattern)
    - Detailed content moved to `references/` and `examples/` directories

- **`constitution`** - Reduced from 558 to 392 lines
    - Moved validation report example to `examples/validation_report.md`
    - Moved best practices to `references/best_practices.md`

- **`clarify`** - Reduced line count
    - Moved 9-category analysis to `references/nine_category_analysis.md`

#### Shared References

- **`usecase_diagram_guide.md`** - Fixed use case diagram relationship notation to UML standard
    - Association: `-->` → `---` (solid line, bidirectional)
    - Include: `-. include .->` → `-.->|"<<include>>"|` (dotted arrow with stereotype label)
    - Extend: `-. extend .->` → `-.->|"<<extend>>"|` (dotted arrow with stereotype label)
    - Updated Common Mistakes table
    - Updated all Mermaid code examples to new notation

- **`mermaid_notation_rules.md`** - Updated use case diagram notation
    - Fixed association notation to `---`
    - Updated Include/Extend label format
    - Updated Common Mistakes section

#### Templates

- **`generate-prd`** - Fixed use case diagram notation in PRD templates
    - `templates/en/prd_template.md`: Updated association, Include, Extend notation
    - `templates/ja/prd_template.md`: Same fixes (keeping Japanese labels `<<包含>>`, `<<拡張>>`)

## [3.0.0] - 2026-02-06

### Added

#### New Skills

- **`/run-checklist`** - Automated quality verification skill
    - Automatically executes verification commands for checklist items generated by `/checklist`
    - Runs tests, linters, security scanners, and spec consistency checks
    - Supports filtering by category (`--category`) and priority (`--priority`)
    - Integrates with TaskList for progress tracking
    - Records results directly in checklist file with timestamps
    - Generates verification report in `.sdd/task/{ticket}/verification_report.md`

#### Shared References

- **`shared/references/`** - Centralized reference documentation
    - `mermaid_notation_rules.md` - Comprehensive Mermaid syntax guide (1100+ lines)
        - Flowchart, sequence, class, state, ER, requirement, and Gantt diagram syntax
        - Escape rules, styling, and common pitfalls
    - `usecase_diagram_guide.md` - Use case diagram guide for Mermaid (750+ lines)
        - Actor, use case, system boundary definitions
        - Relationship types (association, include, extend, generalization)
        - Styling and layout best practices
    - `requirements_diagram_components.md` - SysML requirements diagram components (800+ lines)
        - Requirement element definitions with attributes (id, text, risk, verifyMethod)
        - Relationship types (containment, derivation, refinement, satisfaction, verification)
        - Mermaid syntax examples and templates
    - `document_dependencies.md` - Document dependency chain reference
    - `prerequisites_directory_paths.md` - SDD environment variable reference
    - `prerequisites_plugin_update.md` - Plugin update check instructions
    - `prerequisites_principles.md` - AI-SDD principles reference

#### Agent Structure Improvements

- **Agent output templates** - Language-specific templates for all agents
    - `agents/templates/en/` - English output templates
    - `agents/templates/ja/` - Japanese output templates
    - Templates: `clarification_analysis_output.md`, `clarification_question_template.md`, `prd_review_output.md`,
      `requirement_analysis_output.md`, `spec_review_output.md`
- **Agent references** - Reusable reference documentation
    - `agents/references/ambiguity_patterns.md` - Ambiguous expression patterns
    - `agents/references/document_link_convention.md` - Markdown link conventions
    - `agents/references/sysml_requirements_theory.md` - SysML requirements theory
    - Symlinks to shared references: `mermaid_notation_rules.md`, `requirements_diagram_components.md`,
      `usecase_diagram_guide.md`
- **Agent examples** - Usage examples
    - `agents/examples/clarification_questions.md` - Example clarification questions

#### Skill Structure Improvements

- **Added `references/` directories** to all skills with symlinks to shared references
    - Enables consistent prerequisite handling across skills
    - Reduces duplication of prerequisite documentation
- **Added `examples/` directories** to skills with usage examples
    - `check-spec/examples/` - scope_confirmation.md, serena_symbol_analysis.md
    - `checklist/examples/` - checklist_full_example.md
    - `constitution/examples/` - constitution_as_code.json, constitution_file_structure.md, principle_template.md
    - `generate-spec/examples/` - compliance_check_design.md, compliance_check_spec.md, prd_reference_section.md
    - `implement/examples/` - implementation_progress_log.md, input_format.md, option_* files, output_* files
    - `task-breakdown/examples/` - requirement_coverage.md, serena_analysis.md, task_list_format.md
    - `task-cleanup/examples/` - scope_confirmation.md

### Changed

#### Skills

- **All skills refactored** to use shared references via symlinks
    - Prerequisites now reference `references/prerequisites_*.md` symlinks
    - Reduces maintenance overhead and ensures consistency
- **`implement` skill** - Added extensive reference and template files
    - `references/commit_strategy.md`, `five_phases_overview.md`, `tdd_principles.md`, etc.
    - `templates/{en,ja}/phase_*.md` - Phase execution templates
    - `templates/{en,ja}/tasklist_patterns.md` - TaskList integration patterns
- **`generate-prd` skill** - Added Mermaid diagram references
    - Links to `mermaid_notation_rules.md`, `usecase_diagram_guide.md`, `requirements_diagram_components.md`
- **`doc-consistency-checker` skill** - Added document dependencies reference

#### Agents

- **All agents refactored** with Progressive Disclosure pattern
    - Agent markdown files now use `@reference` imports for large content
    - Output templates externalized to `templates/{en,ja}/`
- **`spec-reviewer`** - Streamlined from 566 to ~200 lines using references
- **`prd-reviewer`** - Streamlined from 328 to ~150 lines using references
- **`requirement-analyzer`** - Streamlined from 420 to ~150 lines using references
- **`clarification-assistant`** - Streamlined from 626 to ~200 lines using references

### Removed

#### Skills

- **`sdd-templates`** - Merged into shared references and individual skill templates
- **`output-templates`** - Templates moved to respective skill directories

#### Legacy Commands

- **`commands/` directory fully removed**
    - `commands/checklist.md` - Migrated to `skills/checklist/SKILL.md`
    - `commands/implement.md` - Migrated to `skills/implement/SKILL.md`
    - `commands/sdd_init.md` - Migrated to `skills/sdd-init/SKILL.md`

---

## [3.0.0-alpha] - 2026-02-03

### Breaking Changes

#### Plugin Consolidation

- **Merged `sdd-workflow-ja` and `sdd-workflow` into a single unified plugin** (`sdd-workflow`)
    - Language selection via `SDD_LANG` environment variable (from `.sdd-config.json` `lang` field, default: `en`)
    - Templates split by language: `templates/ja/` and `templates/en/`
    - SKILL.md and agent files are in English only
    - Removed `sdd-workflow-ja` plugin entirely

#### Commands Converted to Skills

- **All 11 commands migrated to skills** with `user-invocable: true`
    - `commands/` directory removed entirely
    - All commands now live under `skills/{name}/SKILL.md`

#### Command Name Changes (Underscore → Hyphen)

| Old (v2.x)        | New (v3.0.0)      |
|:------------------|:------------------|
| `/sdd_init`       | `/sdd-init`       |
| `/generate_spec`  | `/generate-spec`  |
| `/generate_prd`   | `/generate-prd`   |
| `/check_spec`     | `/check-spec`     |
| `/task_breakdown` | `/task-breakdown` |
| `/task_cleanup`   | `/task-cleanup`   |
| `/sdd_migrate`    | `/sdd-migrate`    |

### Added

#### Multi-Language Support

- **`SDD_LANG` environment variable** - Controls template language selection
    - Set via `.sdd-config.json` `lang` field
    - Supported values: `en` (default), `ja`
    - `session-start.sh` reads `lang` from config and exports `SDD_LANG`

#### Language-Specific Templates

- All 4 existing skills now have language-separated templates:
    - `sdd-templates/templates/{en,ja}/`
    - `vibe-detector/templates/{en,ja}/`
    - `doc-consistency-checker/templates/{en,ja}/`
    - `output-templates/templates/{en,ja}/`
- Japanese templates copied from former `sdd-workflow-ja` plugin

### Changed

#### Skills

- **11 new skills created** from former commands:
    - `sdd-init`, `constitution`, `generate-spec`, `generate-prd`, `check-spec`
    - `task-breakdown`, `implement`, `clarify`, `task-cleanup`, `sdd-migrate`, `checklist`
    - Each skill has appropriate `allowed-tools`, `user-invocable: true`, and optional `disable-model-invocation`
- **4 existing skills updated** to v3.0.0 with language configuration support
    - Added `## Language Configuration` section with dynamic `SDD_LANG` context injection
    - Template path references updated to `templates/en/` format

#### Agents

- **spec-reviewer** - Added `skills` field: `["sdd-workflow:sdd-templates", "sdd-workflow:doc-consistency-checker"]`
- **prd-reviewer** - Added `skills` field: `["sdd-workflow:sdd-templates"]`
- All 4 agents updated with hyphenated command name references
- All agent descriptions updated to reference new command names

#### Configuration

- **`.sdd-config.json`** - Added `lang` field for language configuration
- **`session-start.sh`** - Added `SDD_LANG` reading and export
- **`plugin.json`** - Updated to v3.0.0 with unified plugin description
- **`marketplace.json`** - Removed `sdd-workflow-ja` entry, updated `sdd-workflow` to v3.0.0

#### Documentation

- **`CLAUDE.md`** - Updated repository structure to reflect single plugin with skills
- **`README.md`** - Added migration guide from v2.x, updated all command references

### Removed

- **`plugins/sdd-workflow-ja/`** - Entire Japanese plugin directory (merged into `sdd-workflow`)
- **`plugins/sdd-workflow/commands/`** - Entire commands directory (migrated to skills)

## [2.4.2] - 2026-01-26

### Fixed

#### Plugin Manifest

- **Removed skills field from plugin.json** - Fixed plugin installation error
    - Removed `skills` field as it is not supported in Claude Code's plugin.json schema
    - Skills are automatically discovered from `skills/` directory
    - Resolved "Invalid input" error during installation

## [2.4.1] - 2026-01-26

### Fixed

#### Commands

- **argument-hint corrections and argument descriptions** - Fixed argument specifications to match actual usage
    - Unified `argument-hint` expressions ("file-path" → "feature-name" corrections)
    - Added argument description tables to each command (argument name, required/optional, description)
    - Affected commands:
        - `task_breakdown`: `<design-doc-path>` → `<feature-name> [ticket-number]`
        - `check_spec`: `<design-doc-path>` → `[feature-name] [--full]`
        - `checklist`: `<file-path>` → `<feature-name> [ticket-number]`
        - `clarify`: `[spec-file-path]` → `<feature-name> [--interactive]`
        - `constitution`: `<init|update|check>` → `<subcommand> [arguments]` (added subcommand details table)
        - `generate_prd`: `<feature-name> [requirements-description]` → `<requirements-description>`
        - `generate_spec`: `<feature-name> [prd-file-path]` → `<requirements-description>`
        - `implement`: `<task-file-path>` → `<feature-name> [ticket-number]`
        - `task_cleanup`: `<ticket-number>` → `[ticket-number]` (made optional)
    - Users can now understand correct argument formats when executing commands

## [2.4.0] - 2026-01-25

### Added

#### Documentation

- **PLUGIN.md** - Comprehensive guide for Claude Code plugin and marketplace creation
    - Plugin basic structure (directory layout, marketplace structure)
    - Manifest files (plugin.json, marketplace.json details)
    - Commands, agents, skills implementation (frontmatter, best practices)
    - MCP server integration (external tool integration)
    - Hooks implementation (event-driven automation)
    - Marketplace publishing process (quality standards, distribution model)
- **CLAUDE.md** - Added reference to PLUGIN.md (similar to PLUGIN_AGENTS.md structure)

#### Skills

- Added `version: 2.3.1` and `license: MIT` fields to all skills
    - vibe-detector
    - doc-consistency-checker
    - sdd-templates
- **output-templates** - New skill providing command output formats
    - `init_output.md` - Initialization complete message
    - `prd_output.md` - PRD generation complete message
    - `spec_output.md` - Specification & design generation complete message
    - `breakdown_output.md` - Task breakdown results
    - `cleanup_output.md` - Cleanup confirmation
    - `clarification_output.md` - Specification clarification report
    - `check_spec_output.md` - Consistency check results
    - `migrate_output.md` - Migration results
    - `constitution_output.md` - Constitution management results

#### Commands

- Added `argument-hint` field to all commands for improved usability
    - generate_spec: `<feature-name> [prd-file-path]`
    - generate_prd: `<feature-name> [requirements-description]`
    - check_spec: `<design-doc-path>`
    - task_breakdown: `<design-doc-path> [ticket-number]`
    - task_cleanup: `<ticket-number>`
    - constitution: `<init|update|check>`
    - implement: `<task-file-path>`
    - clarify: `[spec-file-path]`
    - checklist: `<file-path>`

### Changed

#### Architecture

- **Output Format Separation** - Separated command output formats into `skills/output-templates/`
    - Command md files now contain only Claude-facing instructions
    - Output formats are managed as independent template files
    - New skill: `output-templates` (includes 9 template files)
    - Existing `sdd-templates` skill is now dedicated to project document templates

#### Commands

- **implement** - Added TaskList-based progress management
    - Creates tasks using TaskCreate at the start of each phase
    - Updates task status using TaskUpdate during phase execution (pending → in_progress → completed)
    - Sets dependencies to ensure next phase starts only after previous phase completes
    - Users can check implementation progress using `/tasks` command
    - Falls back to traditional markdown progress display when TaskList is unavailable

#### Marketplace

- **marketplace.json** improvements
    - Added `author.url` (creator attribution)
    - Added `category: "development"` (marketplace filtering)
    - Added `tags` array (search discoverability)
        - "specification-driven-development"
        - "japanese" / "english"
        - "workflow"
        - "sysml"
        - "requirements"
        - "documentation"

#### Agents

- Improved `description` for all agents with clearer usage scenarios
    - Changed from functional description style to "when to use" style
    - Added specific trigger phrases (e.g., "review spec", "check spec")
    - Made explicit relationships with commands (e.g., after /check_spec or /generate_spec execution)
    - Specified required input information (e.g., specification file path needed)
    - Removed self-referential "agent" terminology
    - Target agents: spec-reviewer, requirement-analyzer, prd-reviewer, clarification-assistant

#### Skills

- Improved `description` for all skills with clearer execution context
    - Specified execution timing (e.g., automatically executed before implementation, invoked by commands)
    - Specified detection details (e.g., ambiguous expressions like "make it nice", "somehow")
    - Made explicit traceability guarantees
    - Detailed fallback behavior explanation
    - Target skills: vibe-detector, doc-consistency-checker, sdd-templates

### Fixed

#### Commands

- **Unified Prompt Expressions** - Removed user-facing explanations and unified to clear Claude-facing instructions
    - Removed "Next Steps" list items (from plain text within "Post-Generation Actions" section)
    - Removed "Recommended Manual Verification" sections (moved to output templates)
    - Changed "manually" expressions to Claude-directed instructions (e.g., "recommend manual verification to user")
    - Unified output format reference method (from file path to skill reference)
    - Affected commands: `sdd_init`, `generate_prd`, `generate_spec`, `task_breakdown`, `task_cleanup`, `clarify`,
      `check_spec`, `sdd_migrate`, `constitution`

#### Agents

- **Unified Prompt Expressions** - Changed "recommended" expressions to directive forms
    - spec-reviewer: "recommended to be added" → "need to be added"
    - clarification-assistant: "Supplementation recommended" → "Supplementation needed"
    - clarification-assistant: "Recommended Clarity Scores" → "Clarity Score Evaluation Criteria"

## [2.3.1] - 2026-01-14

### Fixed

#### Hooks

- `session-start.sh` - Improved error handling with temporary file existence check
    - Fixed `mv: No such file or directory` error when sed command fails
    - Added `&& [ -f "$TEMP_FILE" ]` to verify temporary file existence before executing mv
    - Improved fallback process to work properly
    - Added warning file deletion process (else clause) to English version for consistency with Japanese version

## [2.3.0] - 2026-01-09

### Changed

#### Agents

- **Role Separation**: Renamed `sdd-workflow` agent to `AI-SDD-PRINCIPLES.md`
    - Separated principle definitions into an independent document
    - Updated all commands, agents, and skills to reference `../AI-SDD-PRINCIPLES.md`
    - Centralized AI-SDD principles for better maintainability

- `spec-reviewer` - Added document traceability check functionality
    - **PRD ↔ spec traceability check**: Verify PRD requirements are properly covered in spec
        - Requirement ID (UR/FR/NFR) mapping verification
        - Coverage rate calculation (80% threshold check)
        - Classification of partial/missing coverage
    - **spec ↔ design consistency check**: Verify spec content is properly detailed in design
        - API definition elaboration check
        - Type definition consistency check
        - Constraint consideration check
    - Added `Edit` to `allowed-tools` (for auto-fix support)
    - Clarified input format and output format (`--summary` option support)

#### Commands

- `/check_spec` - **Specialized for design ↔ implementation consistency check**
    - **[BREAKING]** Delegated document-to-document consistency checks (PRD↔spec, spec↔design) to `spec-reviewer`
        - **Before (v2.2.0)**: Performed all consistency checks (CONSTITUTION↔docs, PRD↔spec, spec↔design,
          design↔implementation)
        - **After (v2.3.0)**: Performs only design↔implementation consistency check (improved performance)
        - **Migration**:
            - If document-to-document consistency checks are needed: Use `/check_spec --full`
            - If design↔implementation only is sufficient: Keep using `/check_spec` (same command as before)
        - **Impact**: If using `/check_spec` in CI/CD pipeline, consider adding `--full` option
    - Added `--full` option: Runs comprehensive review by `spec-reviewer` in addition to consistency check
    - Limited target documents to `*_design.md`
    - Simplified output format (focused on design↔implementation)

- `/sdd_init` - Updated reference path
    - Changed agent reference to `AI-SDD-PRINCIPLES.md`

### Added

#### Documentation

- `AI-SDD-PRINCIPLES.md` - Independent document defining AI-SDD principles
    - Separated principle definitions previously contained in `sdd-workflow` agent
    - Commonly referenced by commands, agents, and skills

#### README

- Documented Windows platform incompatibility
    - Added platform support matrix (macOS/Linux: ✅, Windows: ❌)
    - Documented alternatives for Windows users (WSL, Git Bash)
    - Future support plans (PowerShell version, cross-platform implementation under consideration)

## [2.2.0] - 2026-01-06

### Added

#### Agents

- `prd-reviewer` - PRD (Requirements Specification) review agent
    - CONSTITUTION.md compliance check (most important feature)
    - Principle category checks (Business, Architecture, Development, Technical Constraints)
    - Auto-fix flow (attempts auto-fix on violation detection)
    - SysML requirements diagram format validation
    - Ambiguous expression detection and improvement suggestions

### Changed

#### Agents

- `spec-reviewer` - Added CONSTITUTION.md compliance check functionality
    - Added preparation instruction to read CONSTITUTION.md using Read tool
    - Spec-focused principle category checks (Architecture principles emphasized)
    - Design-focused principle category checks (Technical constraints emphasized)
    - Auto-fix flow (attempts auto-fix on violation detection)
    - Added CONSTITUTION.md compliance check results to review output format

#### Commands

- `/generate_prd` - Added CONSTITUTION.md compliant generation flow
    - Added CONSTITUTION.md reading step to generation flow (Step 2)
    - Made prd-reviewer principle compliance check mandatory (Step 6)
    - Added principle category impact table for PRD
    - Added check result output template

- `/generate_spec` - Added CONSTITUTION.md compliant generation flow
    - Added CONSTITUTION.md reading step to generation flow (Step 2)
    - Made spec-reviewer principle compliance check mandatory (Steps 6, 8)
    - Added check result output templates for both spec and design doc

## [2.1.1] - 2025-12-23

### Changed

- Removed automatic git commit instructions from all commands and agents
    - `task_cleanup` - Removed commit step from cleanup workflow
    - `implement` - Removed commit instruction from continuous verification flow
    - `generate_spec` - Removed commit step from generation flow
    - `sdd-workflow` agent - Removed commit steps from workflow phases
    - `clarify` - Removed commit instructions from integration mode
    - `task_breakdown` - Removed commit step from post-generation actions
    - `generate_prd` - Removed commit step from post-generation actions
    - `sdd_migrate` - Removed commit instructions and commit message examples
    - `sdd_init` - Removed commit step from initialization flow

## [2.1.0] - 2025-12-12

### Added

#### Commands

- `/clarify` - Specification clarification command
    - Scans specifications across 9 categories (functional scope, data model, flow, non-functional requirements,
      integrations, edge cases, constraints, terminology, completion signals)
    - Classifies unclear items as Clear/Partial/Missing
    - Generates up to 5 high-impact clarification questions
    - Incrementally integrates answers into `*_spec.md`
    - Complementary to `vibe-detector` skill
- `/implement` - TDD-based implementation execution command
    - Verifies checklist completion rate in tasks.md
    - Executes 5 phases in order (Setup→Tests→Core→Integration→Polish)
    - Test-first (TDD) approach
    - Auto-marks progress in tasks.md
    - Completion verification (all tasks done, tests pass, spec consistency)
- `/checklist` - Quality checklist generation command
    - Auto-generates checklists from specs and plans across 9 categories
    - Assigns IDs in CHK-{category-number}{sequence} format
    - Auto-sets priority levels (P1/P2/P3)
- `/constitution` - Project constitution management command
    - Defines non-negotiable project principles (business, architecture, development methodology, technical constraints)
    - Semantic versioning (MAJOR/MINOR/PATCH)
    - Sync validation with specifications and design documents

#### Agents

- `clarification-assistant` - Specification clarification assistant agent
    - Systematically analyzes user requirements across 9 categories
    - Generates high-impact clarification questions
    - Integrates answers into specifications
    - Backend role for `/clarify` command

#### Templates

- `checklist_template.md` - Quality checklist template
    - 9 categories of quality check items
    - Priority levels (P1/P2/P3)
    - Verification methods for each item
- `constitution_template.md` - Project constitution template
    - Principle hierarchy (business → architecture → development methodology → technical constraints)
    - Verification methods, violation examples, compliance examples for each principle
    - Version history and amendment process
- `implementation_log_template.md` - Implementation log template
    - Session-based implementation decision records
    - Challenges and solutions tracking
    - Technical discoveries and performance metrics

#### Skills

- `sdd-templates` - Added references to new templates

## [2.0.1] - 2025-12-12

### Added

#### Agents

- Added document link convention to all agents
    - `sdd-workflow` - Defined markdown link format for files/directories
    - `spec-reviewer` - Added link convention check points
    - `requirement-analyzer` - Added link convention for requirement diagrams
    - File links: `[filename.md](path)` format
    - Directory links: `[directory-name](path/index.md)` format

### Removed

#### Agents

- `sdd-workflow` - Removed commit message convention section
    - Changed policy to delegate to Claude Code's standard commit conventions

## [2.0.0] - 2025-12-09

### Breaking Changes

#### Directory Structure Changes

- **Root directory**: `.docs/` → `.sdd/`
- **Requirement directory**: `requirement-diagram/` → `requirement/`
- **Task log directory**: `review/` → `task/`

#### Command Rename

- `/review_cleanup` → `/task_cleanup`

#### Migration

Use the `/sdd_migrate` command to migrate from legacy versions (v1.x):

- **Option A**: Rename directories to migrate to new structure
- **Option B**: Generate `.sdd-config.json` to maintain legacy structure

### Added

#### Commands

- `/sdd_init` - AI-SDD workflow initialization command
    - Adds AI-SDD Instructions section to project's `CLAUDE.md`
    - Creates `.sdd/` directory structure (requirement/, specification/, task/)
    - Generates template files using `sdd-templates` skill
- `/sdd_migrate` - Migration command from legacy versions
    - Detects legacy structure (`.docs/`, `requirement-diagram/`, `review/`)
    - Choose between migrating to new structure or generating compatibility config

#### Agents

- `requirement-analyzer` - Requirement analysis agent
    - SysML requirements diagram-based analysis
    - Requirement tracking and verification

#### Skills

- `sdd-templates` - AI-SDD templates skill
    - Provides fallback templates for PRD, specification, and design documents
    - Clarifies project template priority rules

#### Hooks

- `session-start` - Session start initialization hook
    - Loads settings from `.sdd-config.json` and sets environment variables
    - Auto-detects legacy structure and shows migration guidance

#### Configuration File

- `.sdd-config.json` - Project configuration file support
    - `root`: Root directory (default: `.sdd`)
    - `directories.requirement`: Requirement directory (default: `requirement`)
    - `directories.specification`: Specification directory (default: `specification`)
    - `directories.task`: Task log directory (default: `task`)

### Changed

#### Plugin Configuration

- `plugin.json` - Enhanced author field
    - Added `author.url` field

#### Commands

- Added `allowed-tools` field to all commands
    - Explicitly specifies available tools for each command
    - Improved security and clarity
- All commands now support `.sdd-config.json` configuration file

#### Skills

- Improved skill directory structure
    - Migrated from `skill-name.md` to `skill-name/SKILL.md` + `templates/` structure
    - Applied Progressive Disclosure pattern
    - Externalized template files, simplifying SKILL.md

### Removed

#### Hooks

- `check-spec-exists` - Removed
    - Specification creation is optional, and non-existence is a common valid case
- `check-commit-prefix` - Removed
    - Removed because commit message conventions are not used by plugin functionality

## [1.1.0] - 2025-12-06

### Added

#### Commands

- `/sdd_init` - AI-SDD workflow initialization command
    - Adds AI-SDD Instructions section to project's `CLAUDE.md`
    - Creates `.docs/` directory structure (requirement-diagram/, specification/, review/)
    - Generates template files using `sdd-templates` skill

#### Skills

- `sdd-templates` - AI-SDD templates skill
    - Provides fallback templates for PRD, specification, and design documents
    - Clarifies project template priority rules

### Changed

#### Plugin Configuration

- `plugin.json` - Enhanced author field
    - Added `author.url` field

#### Commands

- Added `allowed-tools` field to all commands
    - Explicitly specifies available tools for each command
    - Improved security and clarity

#### Skills

- Improved skill directory structure
    - Migrated from `skill-name.md` to `skill-name/SKILL.md` + `templates/` structure
    - Applied Progressive Disclosure pattern
    - Externalized template files, simplifying SKILL.md

## [1.0.1] - 2025-12-04

### Changed

#### Agents

- `spec-reviewer` - Added prerequisites section
    - Added instruction to read `sdd-workflow:sdd-workflow` agent content before execution
    - Promotes understanding of AI-SDD principles, document structure, persistence rules, and Vibe Coding prevention

#### Commands

- Added prerequisites section to all commands
    - `generate_prd`, `generate_spec`, `check_spec`, `task_breakdown`, `review_cleanup`
    - Added instruction to read `sdd-workflow:sdd-workflow` agent content before execution
    - Ensures consistent behavior following sdd-workflow agent principles

#### Skills

- Added prerequisites section to all skills
    - `vibe-detector`, `doc-consistency-checker`
    - Added instruction to read `sdd-workflow:sdd-workflow` agent content before execution

#### Hooks

- `check-spec-exists.sh` - Improved path resolution
    - Dynamically retrieves repository root using `git rev-parse --show-toplevel`
    - Falls back to current directory if not a git repository
- `check-spec-exists.sh` - Extended test file exclusion patterns
    - Jest: `__tests__/`, `__mocks__/`
    - Storybook: `*.stories.*`
    - E2E: `/e2e/`, `/cypress/`
- `settings.example.json` - Added setup instructions as comments
    - Fixed path to `./hooks/` format

#### Skills

- `vibe-detector` - Added `AskUserQuestion` to `allowed-tools`
    - Supports user confirmation flow
- `doc-consistency-checker` - Added `Bash` to `allowed-tools`
    - Supports directory structure verification

## [1.0.0] - 2024-12-03

### Added

#### Agents

- `sdd-workflow` - AI-SDD development flow management agent
    - Phase determination (Specify → Plan → Tasks → Implement & Review)
    - Vibe Coding prevention (detection of vague instructions and promotion of clarification)
    - Document consistency checks
- `spec-reviewer` - Specification quality review agent
    - Ambiguous description detection
    - Missing section identification
    - SysML compliance checks

#### Commands

- `/generate_prd` - Generate PRD (Requirements Specification) in SysML requirements diagram format from business
  requirements
- `/generate_spec` - Generate abstract specification and technical design document from input
    - PRD consistency review feature
- `/check_spec` - Check consistency between implementation code and specifications
    - Multi-layer check: PRD ↔ spec ↔ design ↔ implementation
- `/task_breakdown` - Break down tasks from technical design document
    - Requirement coverage verification
- `/review_cleanup` - Clean up review/ directory after implementation

#### Skills

- `vibe-detector` - Automatic detection of Vibe Coding (vague instructions)
- `doc-consistency-checker` - Automatic consistency check between documents

#### Integration

- Serena MCP optional integration
    - Enhanced functionality through semantic code analysis
    - Support for 30+ programming languages
    - Text-based search fallback when not configured
