# Design Doc Migration Report

**Target**: `${SDD_SPECIFICATION_PATH}/{feature-name}_design.md`
**Decision log**: `${SDD_ADR_PATH}/{feature-name}.md`
**Entry format**: {ADR_TEMPLATE.md | AI-SDD-PRINCIPLES.md § Architecture Decision Record}
**Mode**: {single feature | --all ({done}/{total}, {remaining} remaining)}

## Appended Entries

| # | Heading | Rejected alternatives |
|:--|:--------|:----------------------|
| 1 | `## YYYY-MM-DD {decision title}` | {count | None considered} |

Verified on disk: {yes | no}

## Not Carried Over

Content left out of the decision log, per the how/what criteria:

- {section name} - {reason (implementation status / module breakdown / data model / test strategy / change history / open question)}

## Original File

**Decision**: {deleted | kept}

{When kept: the file remains valid as supplementary input; nothing reports it as a violation.}
{When deleted: `MIGRATION_PENDING.md` disappears on its own once no `*_design.md` is left.}

## References

### Core standard - rewrite proposed

| Path | Line | Current | Proposed |
|:-----|:-----|:--------|:---------|
| `{path}` | {line} | {text} | {rewrite} |

Applied: {count} / Deferred: {count}

### Manual action required (project-specific)

| Path | Line | Kind | Text |
|:-----|:-----|:-----|:-----|
| `{path}` | {line} | {custom front matter field / custom document type / prose mention / task reference / code comment} | {text} |

These are reported only. A project's own convention is not rewritten automatically.

## Next Steps

- Read the result back with `/render-adr-review ${SDD_ADR_PATH}/{feature-name}.md`
- {With --all: {remaining} file(s) left - approve this pilot's format, then process the rest in one pass}
