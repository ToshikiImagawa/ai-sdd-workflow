# HTML Structure Contract

This skill composes the output HTML from three template layers instead of converting Markdown
line-by-line. This is what keeps the result "structured by decision / rationale / rejected
alternatives" rather than a surface-level Markdown-to-HTML pass.

## Template Layers

| Layer | File | Repeats | Purpose |
|:--|:--|:--|:--|
| Shell | `templates/${SDD_LANG:-en}/review_shell.md` | Once | Page chrome: `<style>`, header banner, footer notice |
| Decision card | `templates/${SDD_LANG:-en}/decision_card.md` | Once per ADR/decision entry | One `<section>` per decision: title, context, rationale |
| Comparison row | `templates/${SDD_LANG:-en}/alternative_row.md` | Once per option considered (adopted + rejected) | One `<tr>` in the comparison table |

Render bottom-up: fill each `alternative_row.md` copy, join them into `{alternative_rows}`, fill
`decision_card.md` with that and the decision's own fields, join the cards into
`{decision_cards}`, then fill `review_shell.md`.

## Placeholder Reference

| Placeholder | Layer | Content |
|:--|:--|:--|
| `{header_title}` | shell | Feature/ticket name being reviewed |
| `{header_meta}` | shell | Source file path(s) and generation context |
| `{decision_cards}` | shell | Concatenated rendered `decision_card.md` blocks |
| `{decision_anchor}` | card | Slug for the `id` attribute (anchor links from the header) |
| `{decision_title}` | card | The decision statement itself |
| `{decision_date}` | card | Date/context recorded with the entry, if any |
| `{decision_status_class}` | card | `superseded` when a later entry supersedes this one, otherwise empty (drives the dimmed card styling) |
| `{decision_badge_label}` | card | Localized state label ("Decision"/"Superseded" or "決定"/"失効") |
| `{decision_supersession}` | card | The rendered `<p class="decision-supersession">` note(s) linking this entry to the entry it replaced and/or the entry that replaced it, including the reversing entry's "what changed" line. Links must target the other card's `{decision_anchor}` in this same file, not a Markdown anchor copied from the source. Empty string when neither applies |
| `{decision_rationale}` | card | Why this option was chosen |
| `{alternative_rows}` | card | Concatenated rendered `alternative_row.md` blocks (adopted row first, then rejected) |
| `{option_name}` | row | Name of the option (the adopted decision, or a rejected alternative) |
| `{option_summary}` | row | One-line description of the option |
| `{option_verdict_reason}` | row | Why it was adopted, or why it was rejected |
| `{verdict_class}` | row | `verdict-adopted` or `verdict-rejected` (drives the highlight styling) |
| `{verdict_label}` | row | Localized label ("Adopted"/"Rejected" or "採用"/"却下") |

## Highlighting Rule

The comparison table always lists the adopted decision as its first row (`verdict-adopted`,
highlighted) followed by every rejected alternative recorded in the source entry
(`verdict-rejected`, muted/struck-through). If the source entry recorded no rejected
alternatives — including when it says so explicitly with `None considered` — omit the table and
render only the rationale section. Do not invent alternatives that were not in the source, and do
not turn `None considered` into a `verdict-rejected` row.

**Rejected and superseded are different axes; never render one as the other.** A rejected
alternative was never adopted — it is a row inside one entry's comparison table. A superseded
decision *was* adopted and later reversed by another entry — it is the state of a whole card. An
entry whose decision was later superseded still shows its own adopted row as `verdict-adopted`
inside its table: at the time, that is what was chosen, and rewriting that history would misreport
the log. The reversal is carried by the card's state and its `{decision_supersession}` note.

## Non-Goals

- Do not pipe the source Markdown through a generic renderer and drop the result into a single
  `<div>` — every entry must land in its own card with rationale and alternatives in distinct
  regions, or this skill degenerates into the plain conversion it exists to avoid.
- Do not add navigation, search, or multi-page output — this is a single-file scratch artifact for
  one review session (see `SKILL.md` Output section for the non-persistence rule).
