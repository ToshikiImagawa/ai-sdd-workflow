# Type-Specific Front Matter Fields

Additional fields to include based on the document `type` field.

**PRD** (`type: "prd"`):

```yaml
priority: "medium"
risk: "medium"
```

**Spec** (`type: "spec"`):

```yaml
sdd-phase: "specify"
```

**Design** (`type: "design"`):

```yaml
sdd-phase: "plan"
```

`impl-status` is deliberately absent from the Spec and Design blocks. This skill reads document metadata only and
never inspects the implementation, so it cannot know whether the spec's behavior is implemented — and writing the
plausible-looking default `"not-implemented"` onto an already-implemented document would downgrade a real
regression from Critical to Info in `check-spec`. Report the document as needing the field and let a human add
`implemented` / `in-progress` / `not-implemented` after checking the implementation.

**Task** (`type: "task"`):

```yaml
sdd-phase: "tasks"
ticket: ""
```

**ADR** (`type: "adr"`):

```yaml
status: "approved"
sdd-phase: "implement"
```

An ADR decision log records decisions that were already made, so its `status` is `"approved"` rather than the
`"draft"` default used for other types.

Set `ticket` only if the source `task/{ticket-number}/` had no reachable issue tracker to record completion in.

Leave `supersedes`/`superseded-by` out. In the front matter they mean the **whole decision log file** was retired
in favor of another file (a renamed, split, or merged feature) — a rare, project-level fact this skill cannot
infer. One decision reversing an earlier decision in the same file is recorded in that entry's body
(`- **Supersedes**: ...`), not in the front matter, and this skill never edits document bodies.

**Implementation Log** (`type: "implementation-log"`):

```yaml
sdd-phase: "implement"
ticket: ""
completed: ""
implementer: ""
```
