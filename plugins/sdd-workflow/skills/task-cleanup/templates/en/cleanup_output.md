## Task Cleanup Confirmation

### Target

- Directory: `${SDD_TASK_PATH}/{target}/`

### Analysis Results

#### Integration Status

| File                         | Decisions / Rejected Alternatives | Status       |
|:-----------------------------|:-----------------------------------|:-------------|
| `implementation_log_{id}.md` | {decision count}                   | To Integrate |
| `implementation_log_{id}.md` | {decision count}                   | To Integrate |

**Total**: {count} entries to append to `adr/{feature}.md`

#### Integration Verification (gate for deletion)

Re-read from disk after appending — deletion proceeds only when every row is `Verified`.

| Appended Entry (`## YYYY-MM-DD {title}`) | Target file                     | Decision / Rationale / Rejected alternatives present | Past entries intact | Result                  |
|:-----------------------------------------|:--------------------------------|:-----------------------------------------------------|:--------------------|:------------------------|
| `## {date} {title}`                      | `${SDD_ADR_PATH}/{feature}.md`  | {Yes / missing: {item}}                              | {Yes / No}          | {Verified / **Failed**} |

- Front matter fields on disk: {Verified / missing: {field}}
- Other documents edited in step 7: {Verified / missing: {file}: {field}}
- **Deletion decision**: {Proceed / **Blocked** — task/ kept, missing content reported above}

#### Files to Delete

- [ ] `${SDD_TASK_PATH}/{target}/implementation_log_{id}.md`
- [ ] `${SDD_TASK_PATH}/{target}/implementation_log_{id}.md`
- [ ] `${SDD_TASK_PATH}/{target}/tasks.md`

#### Know-how Not Recorded in the ADR

`adr/` records decisions, not know-how. Name a destination for reusable knowledge before it is deleted.

| Knowledge                            | Suggested destination                                                        |
|:-------------------------------------|:-----------------------------------------------------------------------------|
| {implementation tip / debugging note} | {code comment / the test that pins the behavior / `*_spec.md` if it changes specified behavior} |

### Spec Update Judgement

| Decision | Trigger Matched | Recommendation |
|:---------|:-----------------|:----------------|
| {decision} | {Public API change / New data model / Behavior change / None} | {Propose update to `{name}_spec.md` / No spec update needed} |

### Ticket Dump

- Ticket: `{ticket-number}`
- Summary to post: {one-paragraph summary of appended decisions, spec update outcome, and deleted files}

### Next Actions

1. **Append decisions to ADR** (one `## YYYY-MM-DD {title}` entry per decision, append-only):
    - Append {decision} to `${SDD_ADR_PATH}/{feature}.md`
    - Append {decision} to `${SDD_ADR_PATH}/{feature}.md`

2. **Verify the appends on disk** — see "Integration Verification" above

3. **Delete processed files** (only if verification passed; `git rm` when git tracks them, `rm` when it does
   not — each asks for confirmation):
    - Delete `${SDD_TASK_PATH}/{target}/` directory

4. **Post summary to ticket `{ticket-number}`**

Would you like to proceed with cleanup?
