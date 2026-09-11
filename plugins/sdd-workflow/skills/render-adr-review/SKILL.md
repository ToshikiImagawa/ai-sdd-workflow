---
name: render-adr-review
description: "Render an ADR decision log (or a spec/design doc's decision-rationale section) into a temporary review HTML, restructured around decision / rationale / rejected alternatives instead of a plain Markdown-to-HTML conversion. Output is a scratch file under .sdd/.cache/, never committed."
argument-hint: "<source-path> [ticket-number]"
arguments: [source-path, ticket-number]
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Edit(.sdd/.cache/**)
---

# Render ADR Review - Decision-Axis Review HTML

Reorganizes an `adr/{feature}.md` decision log (or the decision-rationale content of a
`*_spec.md` / `*_design.md`) around **decision / rationale / rejected alternatives**, and renders it
as a temporary HTML file for human review. This is not a Markdown-to-HTML converter: content is
mapped into dedicated template regions (decision card, comparison table) so a reviewer can see what
was decided, why, and what was passed over, at a glance.

This skill does not modify any existing review agent or skill (`spec-reviewer`, `prd-reviewer`,
`doc-consistency-checker`, etc.) — it only adds a new rendering path for human-facing review
material.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/html_structure_reference.md` - Template layers, placeholders, and the highlighting contract this skill must follow

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

- `source-path`: $source-path
- `ticket-number`: $ticket-number

Full argument string: $ARGUMENTS

> **Fallback**: If a value above is empty, remains a literal `$` placeholder, or starts with `--`
> (a flag captured positionally), treat that argument as omitted and interpret the full argument
> string instead. When `source-path` ends up omitted, search
> `${CLAUDE_PROJECT_DIR}/${SDD_ADR_PATH}/**/*.md` with Glob (`adr/` is a single-type directory, so every
> file found is a decision log regardless of whether it carries the legacy `-decisions` suffix). If
> exactly one file is found, use it. If several are found, ask the user to pick one with
> `AskUserQuestion`. If none are found, tell the user no ADR decision log exists yet and stop (do not
> fall back to inventing content).

| Argument        | Required | Description                                                                          |
|:-----------------|:---------|:--------------------------------------------------------------------------------------|
| `source-path`    | -        | Path to an `adr/{feature}.md` decision log, or a `*_spec.md` / `*_design.md` that contains a decision-rationale section. Searched under `${SDD_ADR_PATH}` when omitted |
| `ticket-number`  | -        | Used for the output file name. Accepted positionally, or as a flag in either form: `--ticket <number>` and `--ticket=<number>`. Falls back to the source file's feature name if omitted |

`ticket-number` may be passed positionally (`/render-adr-review {source-path} {ticket-number}`) or as a
flag; both spellings — `--ticket {number}` and `--ticket={number}` — are accepted and mean the same
thing. Strip the `--ticket`/`--ticket=` prefix before using the value, so the flag spelling never reaches
the output file name.

### Input Examples

| Example                                              | Description                                  |
|:------------------------------------------------------|:----------------------------------------------|
| `/render-adr-review adr/auth/user-login.md` | Render a single feature's decision log        |
| `/render-adr-review adr/user-auth.md TICKET-123` | Name the output after the ticket instead of the feature |
| `/render-adr-review adr/user-auth.md --ticket TICKET-123` | Same, with the ticket passed as a flag |
| `/render-adr-review adr/user-auth.md --ticket=TICKET-123` | Same, equals-sign spelling |
| `/render-adr-review`                                  | No argument - pick from ADR logs found under `${SDD_ADR_PATH}` |

## Processing Flow

### 1. Resolve and Read the Source

Both flat (`{feature}.md`) and hierarchical (`{parent-feature}/{child-feature}.md`) ADR layouts are
supported, matching `${SDD_ADR_PATH}` (see the Fallback note above for the legacy `-decisions` suffix
form). Read the resolved file in full.

### 2. Extract Decision Entries

An ADR decision log is append-only: each heading-delimited entry is one decision, in the order it
was recorded. For each entry, extract:

| Field | Source | Notes |
|:--|:--|:--|
| Decision | The choice that was made | This is the entry's own subject, not an alternative |
| Rationale | Why it was chosen | Keep the source's own wording; do not paraphrase away specifics |
| Rejected alternatives | Options considered and not chosen, with the reason each was rejected | Omit the comparison table entirely if the entry recorded none - do not invent alternatives. `None considered` is the log's way of writing "there were none": treat it as no alternatives, never as an option named "None considered" |
| Date/context | Whatever date or situational note the entry carries | The entry heading is `## YYYY-MM-DD {decision title}`, so the date normally comes from the heading; leave blank if the entry has none |
| Supersedes | The earlier entry in the same file that this entry reverses, if the entry records one | The item holds a link to that entry's heading **plus one line on what changed** - carry both into the rendering. Present only on the reversing entry - `adr/` is append-only, so the entry it reverses is never edited |

If a `*_spec.md` / `*_design.md` is given instead of an ADR log, apply the same extraction to its
design-decision / rationale sections; skip sections that are plain behavior description with no
decision-vs-alternative content.

### 2b. Derive Which Entries Are Superseded

A decision log records a reversal in one direction only: the later entry names what it supersedes, and
the entry it reverses is left untouched. So a superseded decision carries **no marker of its own** in
the source. Reading the raw Markdown, an obsolete decision looks exactly like a live one.

Deriving that back-pointer is the main thing this rendered view adds over the source file. After
extracting every entry, resolve each `Supersedes` reference to the entry it points at, and mark that
target as superseded. Then render each entry in one of three states:

| State | Condition | Rendering |
|:--|:--|:--|
| Current | Nothing supersedes it | `{decision_status_class}` empty, `{decision_badge_label}` = `Decision` (ja: `決定`) |
| Superseded | A later entry supersedes it | `{decision_status_class}` = `superseded`, `{decision_badge_label}` = `Superseded` (ja: `失効`), and `{decision_supersession}` states which later entry replaced it, as an anchor link |
| Reversing | It supersedes an earlier entry | Current state, plus `{decision_supersession}` stating which earlier entry it replaced, as an anchor link |

An entry can be both superseded and reversing (a decision reversed twice); render both notes. Include
the reversing entry's own "what changed" line in the note, so a reviewer reads the reason for the
reversal and not only its direction. Fill `{decision_supersession}` with an empty string when the entry
is neither.

Resolve references by the target's heading text or its anchor. Anchor links in
`{decision_supersession}` must point at the other card's rendered `{decision_anchor}` in this same HTML
file - not at the Markdown anchor copied out of the source - so both directions of the reversal are
clickable within the rendered page.

Only the entry-level `Supersedes` item drives any of this. The front matter fields `supersedes` /
`superseded-by` mark the retirement of a **whole decision-log file** (renamed, split, or merged feature)
and say nothing about which entry inside it is obsolete: never use them to mark an entry as superseded.

If a `Supersedes` reference cannot be matched to an entry in the same file, render the entry as Current
and state the unresolved reference in `{decision_supersession}` verbatim - **never guess which entry was
meant**, and never treat an unresolved reference as "nothing was superseded".

### 3. Render Bottom-Up

Follow `references/html_structure_reference.md` exactly:

1. For each option in an entry (the adopted decision first, then each rejected alternative), fill a
   copy of `templates/${SDD_LANG:-en}/alternative_row.md`.
2. Join those rows and fill `templates/${SDD_LANG:-en}/decision_card.md` for the entry.
3. Join all cards and fill `templates/${SDD_LANG:-en}/review_shell.md` to produce the full HTML
   document.

### 4. Write the Output File

Write the rendered HTML with `Edit` to
`${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/render-adr-review/{ticket-number or feature-name}-review.html`.

Report the absolute path to the user so they can open it directly in a browser.

## Output

**This HTML file is a temporary scratch artifact, exactly like the other per-skill caches under
`${SDD_ROOT}/.cache/`. It is not part of the persisted AI-SDD documentation set
(PRD / spec / design / adr) and must never be `git add`-ed or committed.** Re-running this skill
overwrites the previous file for the same feature/ticket; nothing here needs to survive between
review sessions.

Do not assume the project already ignores that path in Git. Unless `${SDD_ROOT}/.cache/` is covered by
the project's `.gitignore`, the rendered HTML shows up as an untracked file. Recommend adding
`.sdd/.cache/` (or `${SDD_ROOT}/.cache/` for a custom root) to `.gitignore` when it is not there yet,
and never stage the file yourself. `/sdd-init` appends that rule (idempotently) since v5.0.0, so for a
project initialized before it, re-running `/sdd-init` is the shortest fix.

## Notes

- Read-only with respect to the source ADR/spec — this skill never edits `adr/` or `specification/`
  content, only writes the rendered HTML under `.sdd/.cache/`
- If the source has no rejected alternatives for a decision, render the rationale only and omit the
  comparison table for that card - an empty table implies a comparison that never happened
- Do not start a dev server or open a browser automatically; report the file path and let the user
  open it
