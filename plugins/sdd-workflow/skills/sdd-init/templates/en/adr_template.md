---
id: "adr-{feature-name}"
title: "{Feature Name} Decision Log"
type: "adr"
status: "approved"
sdd-phase: "implement"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
depends-on: []
tags: []
category: ""
---

# Architecture Decision Record Template (Decision Log)

This document is a template for the **persistent decision log** stored at
`${SDD_ADR_PATH}/{feature-name}.md`. One file per feature, **append-only**: it preserves the rationale
behind key decisions after the temporary `${SDD_TASK_PATH}/{ticket-number}/design-draft.md` is deleted.

> **Note**: `/sdd-init` copies this file to `${SDD_ROOT}/ADR_TEMPLATE.md`, and **that copy is the project's
> template** — customize it there to match your conventions (re-running `/sdd-init` never overwrites it).
> `/task-cleanup` reads `${SDD_ROOT}/ADR_TEMPLATE.md` when it exists, and falls back to the entry format in
> `AI-SDD-PRINCIPLES.md` § Architecture Decision Record when it does not. A customized copy must therefore
> keep the required entry items below, so the appended entries stay machine-readable.

## File Shape

One file holds **many entries** but only **one** front matter block:

| Part                                | Count | Notes                                                                                                                                  |
|:------------------------------------|:------|:---------------------------------------------------------------------------------------------------------------------------------------|
| Front matter                        | 1     | Metadata for the **whole file** (see `front_matter_reference.md`). `status` is always `"approved"` — entries are recorded only after a decision is made |
| `#` title                           | 1     | `# {Feature Name} Decision Log`                                                                                                        |
| `##` entry                          | Many  | One block per decision, **appended at the end of the file**                                                                            |

Past entries are **never rewritten or removed**. Whenever a decision is finalized, append a new `##` block
below the last one. The **latest** entry is the current decision; earlier entries are read as history.

## Entry Format

| Item                                      | Required | Content                                                                                                                  |
|:------------------------------------------|:---------|:-------------------------------------------------------------------------------------------------------------------------|
| Heading: `## YYYY-MM-DD {decision title}` | Yes      | Date the decision was finalized, then a short title naming what was decided (no colon, so the anchor stays predictable)   |
| `- **Decision**:`                         | Yes      | What was decided, in one or two sentences                                                                                |
| `- **Rationale**:`                        | Yes      | Why it was chosen, including the constraint that forced it                                                               |
| `- **Rejected alternatives**:`            | Yes      | Each alternative considered and the reason it lost. Write `None considered` when there were none — never invent one       |
| `- **Supersedes**:`                       | No       | Only when this decision reverses an earlier entry **in the same file**: a link to that entry's heading, plus one line on what changed. Omit the item entirely otherwise |

Superseding is recorded **on the new entry only, in one direction**. The superseded entry is not edited —
not even to add a back-pointer. The front matter fields `supersedes` / `superseded-by` are **not** used for
entry-to-entry reversals; they retire a whole decision-log file (renamed, split, or merged feature).

## Filled Example

Two entries in one file, where the second reverses the first:

```markdown
# user-login Decision Log

## 2025-11-02 Keep sessions in process memory

- **Decision**: Store session state in the application process's memory.
- **Rationale**: Single-instance deployment; an external store was not justified at launch scope.
- **Rejected alternatives**: Redis — an extra operational component with no benefit at one instance.

## 2026-02-14 Move the session store to Redis

- **Decision**: Store session state in Redis, keyed by session id.
- **Rationale**: The service now runs three instances behind a load balancer, so in-process sessions cannot survive request routing.
- **Rejected alternatives**: Sticky sessions at the load balancer — keeps the store simple but loses sessions on instance restart. Database-backed sessions — adds write load to the primary for no durability requirement.
- **Supersedes**: [2025-11-02 Keep sessions in process memory](#2025-11-02-keep-sessions-in-process-memory) — the instance count invalidated the constraint that decision rested on.
```

## What Does Not Belong Here

| Excluded                                | Where it goes instead                                           |
|:----------------------------------------|:----------------------------------------------------------------|
| Full technical design plans             | `${SDD_TASK_PATH}/{ticket-number}/design-draft.md` (temporary)  |
| What the system does, abstractly        | `${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`              |
| Work progress notes, investigation logs | Nowhere — deleted with `${SDD_TASK_PATH}/{ticket-number}/`      |

---

# {Feature Name} Decision Log `<MUST>`

## YYYY-MM-DD {decision title} `<MUST>`

- **Decision**: [What was decided, in one or two sentences]
- **Rationale**: [Why this option was chosen, including the constraint that forced it]
- **Rejected alternatives**: [Alternative — reason it lost], or `None considered`

## YYYY-MM-DD {next decision title} `<OPTIONAL: one block per additional decision>`

- **Decision**: [What was decided, in one or two sentences]
- **Rationale**: [Why this option was chosen, including the constraint that forced it]
- **Rejected alternatives**: [Alternative — reason it lost], or `None considered`
- **Supersedes**: [{earlier entry heading}](#yyyy-mm-dd-decision-title) — [what changed since that decision] `<OPTIONAL: only when reversing an earlier entry>`

Append the next decision below this line as a new `## YYYY-MM-DD {decision title}` block, and leave the
entries above untouched.
