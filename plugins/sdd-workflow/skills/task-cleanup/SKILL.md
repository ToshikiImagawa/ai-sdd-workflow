---
name: task-cleanup
description: "Clean up task/ directory after implementation completion, integrating design decisions and rejected alternatives into adr/{feature}.md before deletion"
argument-hint: "[ticket-number]"
arguments: [ticket-number]
license: MIT
user-invocable: true
model: haiku
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/**)
---

# Task Cleanup - Task Log Cleanup

Organizes documents under `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/`, integrating design decisions and rejected
alternatives into `${CLAUDE_PROJECT_DIR}/${SDD_ADR_PATH}/{feature}.md` (append-only) before deletion.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Tool Permissions

`allowed-tools` above deliberately **omits `Bash`**. This skill deletes files (step 9) and comments on a
ticket (step 10), and deleting files must never be pre-approved. Consequently **every shell command this
skill runs asks the user for confirmation at the moment it runs** — `ls` and `git log` (step 2),
`git ls-files` and then `git rm` / `git rm -r` or `rm` / `rm -r` (step 9), `gh issue comment`
(step 10). That is the intended configuration, not a
misconfiguration: do not propose widening `allowed-tools`, and do not route around the prompt. If a
confirmation cannot be answered (non-interactive session), the command fails — report the pending deletion
in the output and leave `task/` in place rather than retrying.

### Document Persistence Rules (Reference)

| Path                                   | Persistence           | Management Rules                                                                                  |
|:---------------------------------------|:----------------------|:----------------------------------------------------------------------------------------------------|
| `task/{ticket-number}/`                | **Temporary**         | **Delete** after implementation complete (this skill), `design-draft.md` included. Integrate decisions/rejected alternatives into `adr/{feature}.md` first |
| `specification/*_design.md`            | **Persistent (v4.x)** | v4.x persistent design doc. Read as **supplementary input, and treat its absence as normal**. This skill never deletes it and never reports it as a naming violation; it may stay until its decisions have been migrated to `adr/{feature}.md` by a human |
| `adr/{feature}.md`                     | **Persistent**        | **Append-only** decision log. Never rewrite past entries — append new decisions as they are made   |

**Role separation**: `task/` is temporary, AI-facing working notes, deleted once cleanup completes. The ticket
(GitHub Issue / JIRA) is the persistent, team-facing progress record — step 10 dumps a summary there so humans
keep visibility after `task/` is gone. When no ticket tracker is reachable (step 10 is skipped), step 7's
fallback is the only remaining link from the ticket number back to this feature — without it, deleting
`task/{ticket-number}/` erases the ticket-to-feature association entirely. The fallback target depends on
what step 5 produced:

- An `adr` entry was created or already existed for this feature -> set its `ticket` field.
- No `adr` entry exists (nothing to integrate, or this project's generation has no `adr/` concept) but the
  feature's design doc still exists (a v4.x persistent `specification/*_design.md`) -> set that design doc's
  `ticket` field instead.
- Neither exists -> note this gap explicitly in the output; there is no remaining persistent record of the
  ticket-to-feature association.

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

- `ticket-number`: $ticket-number

Full argument string: $ARGUMENTS

> **Fallback**: If the value above is empty or remains a literal `$` placeholder, treat the
> argument as omitted and follow the no-argument flow (scope confirmation below).

| Argument | Required | Description |
|:--|:--|:--|
| `ticket-number` | - | Target ticket number or path. Accepted positionally, or as a flag in either form: `--ticket <number>` and `--ticket=<number>`. Targets entire task/ if omitted |

`ticket-number` may be passed positionally or as a flag; both spellings — `--ticket {number}` and
`--ticket={number}` — are accepted and mean the same thing. Strip the `--ticket`/`--ticket=` prefix before
using the value.

### Input Examples

- `/task-cleanup TICKET-123`
- `/task-cleanup --ticket TICKET-123`
- `/task-cleanup --ticket=TICKET-123`
- `/task-cleanup feature/task-management`
- `/task-cleanup` (without arguments, targets entire task/)

### Scope Confirmation for No-Argument Execution

**When executed without arguments, display the contents of the target directory and ask for user confirmation before starting the process.**

**Reference**: `examples/scope_confirmation.md`

Replace placeholders with actual directory/file names, types, dates, and counts.

**Post-confirmation behavior**:
- User approves -> Execute cleanup on entire task/
- User cancels or specifies a particular directory -> Re-execute with the specified scope

## Processing Flow

### 1. Identify Target Directory

- With argument -> Target `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{argument}/`
- Without argument -> Target entire `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/` (one or more `{ticket}/` subdirectories)

Record each target subdirectory's ticket identifier now (directory name, or its `ticket` front matter field) — later steps reuse it rather than re-resolving it.

### 2. Check Target Files

Get the file list in the target directory with `ls -la ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/`, then check the last update date for each file with `git log -1 --format="%ci" -- <file_path>`.

### 3. Analyze and Classify Content

Review content of each file and classify as follows:

**Content to Integrate (-> `adr/{feature}.md`)**:

| Category                             | Examples                                                                  |
|:-------------------------------------|:--------------------------------------------------------------------------|
| **Design decisions and rationale**   | "Reason for choosing Redis: ...", "Reason for adopting this pattern: ..." |
| **Rejected alternatives**            | "Comparison of Option A vs Option B", "Rejected alternatives and reasons" |
| **Constraints a decision rests on**  | The measurement or limitation that forced a recorded choice ("the 200ms budget ruled out a second round trip") — integrated as part of that decision's **Rationale**, never as a standalone note |

**Content Safe to Delete (No Migration Needed)**:

| Category                          | Examples                                            |
|:-----------------------------------|:-----------------------------------------------------|
| **Work progress notes**           | "Implementing X", "Y completed"                     |
| **Temporary investigation logs**  | Diary-like content, trial and error records         |
| **Specific implementation steps** | Detailed procedures already reflected in code       |
| **Task lists**                    | Lists of completed tasks                            |
| **Date-dependent information**    | Information dependent on specific periods or dates  |
| **Technical tips / troubleshooting / reusable patterns** | Implementation know-how, performance findings, debugging notes |
| **Structure descriptions derived from code** | The design draft's architecture overview, component inventory, directory layout, internal data flow |

**Know-how is not a decision**: implementation tips, performance findings, debugging notes and reusable
patterns are **not** appended to `adr/` just because they are useful — `adr/` records decisions
(`AI-SDD-PRINCIPLES.md` § Knowledge Asset Persistence Management). Before deleting such content, check whether
it belongs somewhere it stays verifiable — a code comment, the test that pins the behavior, or `*_spec.md`
when it changes the specified behavior (step 6) — and name that destination in the output so the user can act
on it. Such knowledge enters an ADR entry only as the **Rationale** of a decision that is being recorded
anyway.

**Structure descriptions are not decisions either**: the draft's architecture overview, component inventory,
directory layout and internal data flow are derived from the code and stay re-derivable from it
(`/plan-refactor` regenerates them on demand). Delete them without naming a destination — a persisted copy
would only drift from the code. What does persist is a *decision about* the structure ("split the fetch layer
out of the view component, because ...") — that is appended as its own entry in step 5.

### 4. Determine Integration Target

When there is information to integrate, determine the appropriate `adr/{feature}.md`:

1. Find the existing decision log most related to content with a single Glob covering both the current
   suffix-free name and the legacy `-decisions` suffix (still valid on existing files):
   - Flat layout: `${CLAUDE_PROJECT_DIR}/${SDD_ADR_PATH}/{feature-name}*.md`
   - Hierarchical layout: `${CLAUDE_PROJECT_DIR}/${SDD_ADR_PATH}/{parent-feature}/{child-feature}*.md`
2. If no existing file for the feature -> create a new `adr/{feature}.md` (no suffix — the default for new files)
3. If no design decision or rejected alternative was found in the target -> skip integration (nothing to append)

### 5. Integrate Information

Append **one `##` entry per decision** at the end of `adr/{feature}.md`. Resolve the entry format in this
order:

1. Check if `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/ADR_TEMPLATE.md` exists
2. **If exists**: use that template — it is the project's own entry format (`/sdd-init` copies it there and
   never overwrites an edited copy)
3. **If not exists**: fall back to the entry format defined in `AI-SDD-PRINCIPLES.md` § Architecture Decision
   Record → Entry Format

One file holds many entries. Follow the field definitions in `AI-SDD-PRINCIPLES.md` § Architecture Decision
Record → Entry Format exactly (heading, `- **Decision**:`, `- **Rationale**:`, `- **Rejected
alternatives**:`, optional `- **Supersedes**:`) — that table is the canonical source, so it is not
restated here in full. The notes below only add cleanup-specific refinements the canonical definition
does not cover:

- **Heading date**: take it from the task file / its last commit date recorded in step 2 — not today's
  cleanup date when they differ. Omit any colon from the title so the anchor stays predictable
- **Rejected alternatives**: write `None considered` when the task files record none — never invent one

When the project's template adds sections of its own, follow the template and keep these items.

Rules:

- **Append-only**: entries go at the end of the file, below its `#` title. Never rewrite, reorder or remove
  past entries
- **Never edit the superseded entry** — the reversal is recorded one-way on the new entry; no back-pointer is
  added to the old one
- One ticket may yield several decisions -> append several entries to the same file, one per decision
- The file has exactly one front matter block, covering the whole file (step 7). Do not add per-entry front
  matter, and **never** record an entry-to-entry reversal in the front matter's `supersedes` /
  `superseded-by` — those fields retire an entire decision-log file
- Do not document source file name (don't leave history)
- When the file does not exist yet, create it as: the `adr` front matter block (step 7), then a
  `# {feature} Decision Log` title, then the entries

### 6. Determine Whether a Spec Update Is Needed

For each decision integrated in step 5, judge whether it matches the "When to Update `*_spec.md`" rule defined in
`AI-SDD-PRINCIPLES.md` (public API changes, new data models, fundamental behavior changes, new requirements).

If any decision matches, propose a `*_spec.md` update to the user via `AskUserQuestion` (present the matching
decision and the affected `*_spec.md`). **Do not edit `*_spec.md` automatically** — spec changes require explicit
user confirmation. Record the outcome (updated / deferred / not applicable) for the output.

### 7. Update Front Matter in Related Documents

Independent of step 6 — do not wait for the spec-update decision to perform these edits. Before deleting task
files, update front matter in related documents if they have YAML front matter. See `references/front_matter_task.md`
for task fields and `references/front_matter_spec_design.md` for design fields.

| Action | Description |
|:-------|:------------|
| **Update/create `adr` front matter** | Set the fields defined for `type: "adr"` in `${CLAUDE_PLUGIN_ROOT}/shared/references/front_matter_reference.md` (`id`, `title`, `status` — always `"approved"` at write time — `created`, `updated`, `sdd-version` — read `version` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` — plus `depends-on` and `ticket` set to the identifier recorded in step 1). **Leave `supersedes` / `superseded-by` alone**: they retire a whole decision-log **file** (feature renamed, split or merged), not one entry. A decision that reverses an earlier one is recorded by the new entry's `Supersedes` item in step 5, and never by rewriting `status` to `deprecated` |
| **Update design doc `updated`** | Only if this skill actually edited the related design doc (e.g. the `ticket` fallback below): set `updated` to the current date. Do not bump it on a document left untouched |
| **Set design doc `ticket` (fallback)** | Only if no `adr` entry was created/updated above (this project's generation has no `adr/` concept, or step 5 found nothing to integrate) and the related design doc still exists as a persistent document (a v4.x `specification/*_design.md`, not a temporary `task/{ticket-number}/design-draft.md` that will itself be deleted): set its `ticket` field to the identifier recorded in step 1, per `references/front_matter_spec_design.md`. This is the fallback link once `task/` is gone. Editing this field is the **only** change this skill makes to a v4.x design doc — it never deletes, rewrites or migrates it |
| **Update spec `status`** | Consider updating to `"approved"` if implementation validates the spec |
| **Update spec `impl-status`** | Before setting, verify against reality: read the relevant source under the feature's implementation path and run the test suite. Do not rely solely on `tasks.md`'s self-reported completion. Set to `"implemented"` only once this check confirms the spec's requirements are met (this is the safety net for cases where the `implement` skill's own update was skipped, e.g. work resumed from a different session) |

### 8. Verify the Integration Landed (Gate for Deletion)

The task files are the only remaining copy of anything step 5 failed to append, and step 9's deletion is not
recoverable for content that was never written. **Verify on disk before deleting.**

For each entry appended in step 5:

1. Re-read `adr/{feature}.md` from disk with `Read`. Do not rely on the edit's return value or on your memory
   of what was written
2. Confirm the entry's `## YYYY-MM-DD {title}` heading is present, and that its `Decision`, `Rationale` and
   `Rejected alternatives` items are all present and non-empty (plus `Supersedes`, if one was intended)
3. Confirm every entry that existed in the file before this run is still present and unchanged (append-only)
4. Confirm the `adr` front matter fields set in step 7 are on disk, including `ticket`

Then re-read the other documents step 7 edited (design doc `ticket` fallback, spec fields) and confirm those
edits are on disk too.

**If any check fails, delete nothing.** Report which entry or field is missing or malformed, leave
`task/{ticket-number}/` in place, and stop. Re-run the append and verify again, or hand the discrepancy to the
user — never proceed to step 9 on an unverified integration.

When step 5 found nothing to integrate, there is nothing to verify: record that in the output and continue.

### 9. Delete Files/Directories

Only after step 8 passed for this target.

**First determine whether git tracks the target**, because `git rm` only works on tracked paths:

`git ls-files -- ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/`

Judge by its **output**, not its exit status: `git ls-files` exits 0 whether or not anything matched.

Then delete according to the result:

| `git ls-files` result                           | Delete with                                                                                                                                           |
|:------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|
| Lists the target's files (tracked)              | `git rm ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/{file}` per file, or `git rm -r ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/` for the whole directory once all files are processed |
| Empty (nothing under the target is tracked)     | `rm ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/{file}` per file, or `rm -r ${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{target}/` for the whole directory |
| Lists some files but not others (mixed)         | `git rm` the listed paths, `rm` the unlisted ones. Never pass an untracked path to `git rm`                                                            |

The `rm` fallback is the **normal** route for a `task/` directory that was never committed, not a workaround:
`git rm` on an untracked path fails with `fatal: pathspec '...' did not match any files` and deletes nothing,
which would leave the cleanup unfinished with no way forward.

`Bash` is not pre-approved (see "Tool Permissions"), so `git ls-files` and each delete command ask for
confirmation. If the user declines the deletion itself, stop and report it — do not switch to the other
delete command to get around the prompt. Choosing `rm` over `git rm` is only valid when `git ls-files`
showed the path is untracked.

### 10. Dump Summary to Ticket

For each target ticket identified in step 1, once its integration and deletion are done, post a summary comment
on that ticket (don't wait for other targets when running without an argument — post per ticket as it completes).

The summary should include: which `adr/{feature}.md` entries were added, whether a spec update was
proposed (and its outcome), and which files were deleted.

- GitHub: `gh issue comment <ticket-number> --body "<summary>"`
- JIRA: use the `mcp-atlassian` MCP (`jira_add_comment`) with the ticket key

If the ticket tracker cannot be determined, skip this step and note it in the output instead of failing —
but verify step 7's fallback `ticket` field (on the `adr` entry, or on the design doc when no `adr` entry
exists) was still set, since it is now the only surviving record of which ticket this feature's decisions
came from.

## Output

Use the `templates/${SDD_LANG:-en}/cleanup_output.md` template for output formatting.

## Notes

### Cases Requiring Careful Judgment

- **Implementation not complete**: Keep task/
- **Integration target unclear**: Confirm with user
- **Information spanning multiple features**: Integrate into most related document
- **Spec update trigger matched but user declines**: Record as "deferred" in the output, do not re-prompt within the same run
- **Step 8 verification failed**: Keep `task/{ticket-number}/` and report the missing entry. An unverified
  integration is treated exactly like "nothing was integrated"

### Deletion Principles

- **Verify before deleting**: never run a delete command (`git rm` or `rm`) on a target whose step 8
  verification has not passed
- **Don't leave history**: Don't add notations like "migrated from ..." during migration
- **Minimal migration**: Migrate only truly valuable information (decisions and rejected alternatives only)
- **Avoid duplication**: Don't migrate content already documented in `adr/{feature}.md`
- **Deletion is scoped to `task/`**: nothing outside `${SDD_TASK_PATH}/` is ever deleted — a v4.x
  `specification/*_design.md` in particular stays where it is
