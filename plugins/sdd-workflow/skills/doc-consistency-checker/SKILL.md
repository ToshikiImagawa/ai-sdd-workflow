---
name: doc-consistency-checker
description: "Automatically executed during document updates or before implementation to check consistency between PRD ↔ *_spec.md ↔ adr/*.md. Detects missing requirement ID (UR/FR/NFR) references, data model mismatches, API definition discrepancies, terminology inconsistencies, PRD-contradicting spec changes, documents with a stale or absent sdd-version generation, and ensures traceability between documents."
argument-hint: "[feature-name]"
license: MIT
user-invocable: false
allowed-tools: Read, Glob, Grep
disallowed-tools: Write, Edit, Bash
---

# Doc Consistency Checker - Document Consistency Check

Automatically checks consistency between AI-SDD documents (PRD, `*_spec.md`, `adr/*.md`) and detects inconsistencies.

## Language Configuration

!`echo "Current language: ${SDD_LANG:-en}"`

When reading templates, use the path: `templates/${SDD_LANG:-en}/`

## Prerequisites

**Before execution, read the AI-SDD principles document.**

AI-SDD principles document path: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles, document structure, persistence rules, and Vibe Coding prevention details.

See `references/prerequisites_directory_paths.md` for directory path resolution using `SDD_*` environment variables.

### Index Fast Path

When `SDD_INDEX` is `on`, a pre-built compressed index exists at `${SDD_ROOT}/.cache/index.md`.
Read it **once** and use all its tables (`Metadata`, `Requirement IDs`, `SysML Relationships`,
`Data Models`, `API Signatures`) for cross-document consistency checks. This replaces
the need for multiple Glob/Grep/Read calls across `.sdd/`. Fall back to raw Read of a specific file
only when cross-reference verification requires full section text. When `SDD_INDEX` is unset or `off`,
use the existing Glob/Grep/Read flow. The `Metadata` table's `sdd-version` column also drives Check
Item 3 (Generation Detection) below, where an **empty** cell in that column means the document's generation
is unknown rather than current.

## Input

This skill is triggered by an advisory hint from the `PostToolUse` hook (`scripts/post-tool-use.py`) when
files under `${SDD_REQUIREMENT_PATH}` or `${SDD_SPECIFICATION_PATH}` are edited. It scans documents based on
feature context.

| Input Source       | Description                                                    |
|:-------------------|:---------------------------------------------------------------|
| Feature context    | Current feature being worked on (from task or document update) |
| Document paths     | Automatically resolved from `${SDD_*}` environment variables   |

**Note**: This skill is `user-invocable: false` and cannot be called directly. Use `/check-spec` for manual consistency checks.

## Document Dependencies

See `references/document_dependencies.md` for the document dependency chain and direction meaning.

## Directory Structure Support

Both flat and hierarchical structures are supported. See `references/directory_structure.md` for the
flat and hierarchical directory layouts.

**⚠️ Note the difference in naming conventions**:

| Directory         | Naming Pattern                      | Examples                                        |
|:------------------|:-------------------------------------|:-------------------------------------------------|
| **requirement**   | No suffix (a `_spec`/`_design` suffix is forbidden here) | `index.md`, `user-login.md`        |
| **specification** | `_spec` optional, legacy-valid       | `index_spec.md`, `user-login.md`                |
| **adr**           | `-decisions` optional, legacy-valid (append-only)  | `index.md`, `user-login.md` |

Consistency checks also consider parent-child relationships for hierarchical structures.

**v4.x persistent design docs (`specification/*_design.md`)**: a project that started on AI-SDD v4.x may still
contain these. They **remain valid** — read them as **supplementary input, and treat their absence as normal**.
Do not create new ones (new technical design goes to `task/{ticket-number}/design-draft.md`), and never report
an existing one as a naming violation or propose deleting it; it may stay until its decisions have been migrated
to `adr/{feature}.md`. See "v4.x Legacy Fallback" under "spec ↔ adr Consistency" below for how such a file is
covered by the checks.

## Check Items

### 0. Front Matter Cross-Reference Consistency

**Note**: Detailed front matter validation (common checks, type-specific checks, cross-reference checks) is handled by the `front-matter-reviewer` agent. The caller should invoke `front-matter-reviewer --cross-ref` separately when full front matter validation is needed.

This skill focuses on document content consistency only.

### 1. PRD ↔ spec Consistency

| Check Item                                 | Description                                                                                                                   |
|:--------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------|
| **Requirement ID Mapping**                  | Are PRD requirement IDs referenced in spec?                                                                                    |
| **Functional Requirement Coverage**         | Are PRD functional requirements covered in spec?                                                                               |
| **Non-Functional Requirement Reflection**   | Are PRD non-functional requirements reflected in spec?                                                                         |
| **Terminology Consistency**                 | Is same terminology used in PRD and spec?                                                                                      |
| **PRD Contradiction / Uncovered Behavior**  | Does a spec change contradict a PRD requirement (FR-xxx, NFR-xxx, etc.), or introduce new behavior no PRD requirement covers?  |

**⚠️ Judge Requirement ID Mapping by the cited requirement's own text only.** When a spec item cites a specific
upstream FR/NFR/UR ID as its source, check that ID's own description — nothing else. An unrelated PRD section
(e.g., an "Out of Scope" note describing a different feature area) does not retroactively justify a citation
whose cited ID says nothing about the downstream behavior — a scope boundary and a traceability claim answer
different questions. If the cited ID's text does not support the spec item, report it as a `[must]`/`[recommend]`
gap even if some other part of the PRD looks superficially compatible. Do not talk yourself out of a textual
mismatch you noticed during analysis by finding a plausible but unrelated justification elsewhere in the document.

**⚠️ The PRD is a record of human business decisions and must never be auto-updated by this check.** When the
"PRD Contradiction / Uncovered Behavior" item finds a contradiction or an uncovered new behavior, always report
it as `[must]` and stop short of editing the PRD. Present the conflicting spec change and the affected PRD
requirement, and let a human decide whether to update the PRD, revert the spec change, or accept it as an
intentional scope change. This mirrors the `task-cleanup` skill's rule for `*_spec.md` updates — see
`task-cleanup/SKILL.md` ("Do not edit `*_spec.md` automatically"); the trigger conditions themselves are listed
in `AI-SDD-PRINCIPLES.md` § Document Update Triggers. The same non-automation principle applies one level up,
from spec to PRD.

**PRD update handoff**: If the human decides to update the PRD, the update itself must go through
`/generate-prd --amend` — never a direct/ad-hoc edit — so existing requirement IDs and sections are preserved and
the change is captured as a normal, human-directed PRD addition (see `generate-prd/SKILL.md` for the `--amend`
flow). This skill still only detects and reports (its `allowed-tools` is read-only); it never invokes
`/generate-prd --amend` itself, since only a human can supply the requirement text `--amend` requires.

**`prd-reviewer` handoff timing**: This skill only detects and reports (its `allowed-tools` is read-only). Once
a human approves a PRD edit for a `[must]` PRD-contradiction finding and runs `/generate-prd --amend`, the
calling agent should invoke `prd-reviewer` against the updated PRD — the same way `generate-prd` does after PRD
generation. Do not call it before the human approves the edit.

### 2. spec ↔ adr Consistency

| Check Item                    | Description                                                                                                             |
|:---------------------------------|:----------------------------------------------------------------------------------------------------------------------------|
| **Decision Traceability**        | Are spec-driving decisions (API shape, data model choices) captured in `adr/*.md`?                              |
| **Referenced Spec Still Valid**  | Do adr entries reference spec elements (API, data model, requirement IDs) that still exist in the current spec?          |
| **Terminology Consistency**      | Is the same terminology used in spec and adr?                                                                             |
| **Obsolescence Detection**       | Does an adr entry describe a decision about spec elements that were since changed or removed, with no follow-up entry?   |

**Obsolescence Detection follow-up**: `adr/` is append-only, so an obsolete entry is never rewritten or deleted.
When this check finds one, propose **appending a new entry at the end of the same `adr/{feature}.md`** in the
entry format defined in `AI-SDD-PRINCIPLES.md` § Architecture Decision Record → Entry Format: a
`## YYYY-MM-DD {decision title}` heading followed by `- **Decision**:`, `- **Rationale**:` and
`- **Rejected alternatives**:`, plus a `- **Supersedes**:` item linking to the obsolete entry's heading anchor
and stating in one line what changed.

Superseding is recorded **only on the new entry, in one direction**:

- Do **not** propose editing the obsolete entry — not even to add a back-pointer. The current decision is the
  latest entry; earlier entries are read as history.
- Do **not** propose writing the reversal into the file's front matter. The front matter `supersedes` /
  `superseded-by` fields are **file-level only** (an entire decision log retired because its feature was
  renamed, split, or merged) and cannot express "entry X reverses entry Y" — one file has many entries but a
  single front matter block. See
  `${CLAUDE_PLUGIN_ROOT}/shared/references/front_matter_reference.md` § ADR → "Entry-Level vs File-Level
  Superseding".
- Do **not** propose flipping the file's `status` to `deprecated`; an ADR's `status` stays `"approved"`.

The file's front matter `depends-on` already points at the spec, so appending an entry does not change it.

#### v4.x Legacy Fallback (`specification/*_design.md` with no adr coverage)

A project migrated from v4.x may still hold its design rationale in a persistent
`${SDD_SPECIFICATION_PATH}/{feature}_design.md` instead of `adr/{feature}.md`. Before reporting spec ↔ adr
results, determine the feature's coverage:

| Situation                                                                 | Action                                                                                                        |
|:--------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------|
| `adr/{feature}*.md` exists with entries                                   | Run the spec ↔ adr checks above as normal                                                                     |
| No adr file (or it holds no entries) **and** a `{feature}_design.md` exists | Run the same four check items against the legacy design doc, reporting them as **spec ↔ design (v4.x legacy)** |
| Neither exists                                                            | Report the area as **not checked** (see below) — never as consistent                                          |

`/check-spec --full` reports the same no-decision-log situation as **not applicable** (its check has no
legacy-design-doc branch, so "no `adr/` resolved" is all it can say). Both labels mean the area was not
verified; neither may be rendered as consistent.

Use Glob against `${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}` (flat: `{feature}_design.md`; hierarchical:
`{parent-feature}/{child-feature}_design.md`) to find the legacy design doc. For the legacy branch, read
`Decision Traceability` as "are the spec-driving decisions captured anywhere — an adr entry or this design
doc's decision-rationale section?", and treat the design doc as **supplementary input**: its absence is normal
and is never itself a finding.

**Never report an unchecked area as consistent.** State the coverage explicitly at the top of the report:

- Which decision-record source was used for this feature (`adr/`, legacy `*_design.md`, or none)
- Every check area that could not be run, and why (no adr entries and no legacy design doc; index disabled;
  PRD missing). A check that did not run must appear as `not checked`, not as `Consistent`.

**Note — out of scope for this skill**:

- `task/{ticket-number}/design-draft.md` consistency with `*_spec.md`, and its integration into
  `adr/*.md` before deletion, are checked by the `task-cleanup` skill at cleanup time (see
  `AI-SDD-PRINCIPLES.md`)
- `spec <-> Implementation` checks — including a legacy `*_design.md`'s module structure, interface definitions
  and technology stack against the code — are checked by `/check-spec` (the `impl-spec-check` feature). The
  v4.x legacy fallback above stays at the document level (decisions, terminology, referenced spec elements)

This skill checks the **persisted** artifacts only: `*_spec.md`, `adr/*.md`, and — in the v4.x legacy fallback
above — an existing `specification/*_design.md`.

### 3. Generation Detection (`sdd-version`)

`sdd-version` was introduced in v5, so documents written by earlier generations **do not have the field at
all**. Absence is therefore the *normal* state of an unmigrated v4.x document, and it is the single most common
migration signal. Report the two populations **separately** — never merge them, and never let an all-absent
project read as "nothing stale":

| Check Item                        | Description                                                                                                                                             |
|:-----------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Stale generation listing**      | Documents whose `sdd-version` is **present** but whose major is lower than the current plugin's major (`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`'s `version`) |
| **Generation-unknown listing**    | Documents where `sdd-version` is **absent**. Report the count, plus the paths (or, above ~20, the count and the directories they fall under)              |

Both listings are advisory: report them so a human can decide whether each document needs a manual migration
review; do not edit the listed documents. Absence is **not** a front matter violation (see
`front_matter_reference.md`'s Missing Front Matter Policy) — it means the generation cannot be determined from
metadata, which is exactly what the reader needs to know.

**Report both counts even when one is zero**, and phrase the summary so the distinction is unmissable, e.g.
`stale: 0 / generation unknown: 85 of 85 checked`. Reporting only "0 stale" for a project whose documents all
predate the field would tell the reader their migration is complete when none of it has happened.

**Source of the two listings**:

- `SDD_INDEX=on`: read the `Metadata` table's `sdd-version` column from `${SDD_ROOT}/.cache/index.md` (see
  Index Fast Path above). An **empty cell** in that column is a generation-unknown document; no additional
  Glob/Grep is needed.
- `SDD_INDEX` unset or `off`: the generation-unknown count is still cheap, so do **not** skip it. One Grep for
  `^sdd-version:` across `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}` (counting only matches inside a document's leading
  front matter block) plus one Glob of the documents in scope gives both listings — the Grep output also
  carries the values needed for the stale listing. Two calls total; there is no need to Read every document.

## Automatic Detection Patterns

### Inconsistency Detection

1. **Missing**: Exists in upstream document but not reflected in downstream
2. **Contradiction**: Different content described in upstream and downstream
3. **Obsolescence**: Downstream changes not reflected in upstream

### Detection Method

See `references/detection_method.md` for the step-by-step detection procedure.

## Output Format

Read `templates/${SDD_LANG:-en}/consistency_report.md` and use it for consistency check output.

The template shows the common sections; the report must additionally carry the two items above even where the
template has no pre-printed row for them:

- **Coverage notice at the top**: the decision-record source used (`adr/`, legacy `*_design.md`, or none) and
  every check area reported as `not checked`, with the reason (see "v4.x Legacy Fallback")
- **Generation-unknown listing** alongside the stale listing, as `stale: {n} / generation unknown: {n} of {n}
  checked` (see "Generation Detection")

## Check Execution Timing

| Timing                        | Recommended Check                                                                             |
|:-------------------------------|:-----------------------------------------------------------------------------------------------|
| **Task Start**                | Verify existing document (PRD, spec, adr) existence and consistency                           |
| **Spec Update**               | PRD ↔ spec consistency (including PRD-contradiction / uncovered-behavior detection) and spec ↔ adr consistency |
| **Implementation Completion** | design-draft ↔ adr integration and spec-update-trigger judgment — handled by `task-cleanup`, not this skill |
| **Review**                    | All inter-document consistency (PRD ↔ spec ↔ adr)                                             |
| **Periodic Check**            | Prevent documentation obsolescence                                                             |

## Document Update Triggers

Based on consistency check results, recommend document updates in the following cases:

### When to Update `*_spec.md`

- Public API signature changes (arguments, return values, types)
- New data model additions
- Fundamental changes to existing behavior
- When new requirements added in requirements diagram

### When a PRD Update Should Be Proposed (never applied automatically)

- A spec change contradicts an existing PRD requirement (FR-xxx, NFR-xxx, etc.)
- A spec change introduces new behavior that no PRD requirement covers

See "PRD ↔ spec Consistency" above for how to report and handle this. This skill never edits `requirement/`
files itself.

### When to Append to `adr/{feature}.md`

Owned by the `task-cleanup` skill at implementation-completion time, not by this skill — see
`AI-SDD-PRINCIPLES.md` § Document Update Triggers for the trigger conditions.

### When Updates Are NOT Needed

- Internal implementation optimization (no interface changes)
- Bug fixes (correcting deviations from specifications)
- Refactoring (no behavior changes)

## Notes

- This skill **detects and reports** but does not auto-fix
- Inconsistency resolution is left to developer judgment. **PRD updates are never automated** — see
  "PRD ↔ spec Consistency" above
- Prioritize upstream documents (PRD > spec > adr)
- Do not uniformly treat specs as correct, as implementation may be correct and specs outdated
