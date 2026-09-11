## PRD Generation Complete

### Generated Files

- [x] `${SDD_REQUIREMENT_PATH}/[{parent}/]{feature}.md`

※ For hierarchical structure, parent features use `index.md`

※ This PRD file is the only document written. The use case diagram, the UR/FR/NFR tables, and the SysML
requirements diagram are sections **inside** it — do not report them as separate files, and do not list
`${SDD_SPECIFICATION_PATH}/` paths here (no spec is created by this skill)

### CONSTITUTION.md Compliance Check Results

| Principle Category      | Status       |
|:------------------------|:-------------|
| Business Principles     | 🟢 Compliant |
| Architecture Principles | 🟢 Compliant |
| Development Principles  | 🟢 Compliant |
| Technical Constraints   | 🟢 Compliant |

**Fix proposals applied**: {count} items
**Requires discussion**: {count} items (see details above)

### Next Steps

1. Review PRD content and adjust as needed
2. Create the abstract specification and the technical design draft with `/generate-spec` — the next phase
   after Specify's PRD. Pass the ticket number, because the design draft is written to
   `${SDD_TASK_PATH}/{ticket-number}/design-draft.md`:

   ```bash
   /generate-spec --ticket {ticket-number} {requirements-description}
   ```

   `--ticket={ticket-number}` is accepted as well. In interactive mode the ticket number is asked for when the
   flag is omitted; with `--ci` the flag is required and the run aborts without it
3. Reference PRD requirement IDs in specifications

### Recommended Manual Verification

- [ ] Verify generated PRD content matches business requirements
- [ ] Verify uniqueness of requirement IDs (format resolved from `id_conventions` in `.sdd-config.json`)
- [ ] Verify priority (MoSCoW) classification is appropriate
- [ ] Align with stakeholders

### Verification Commands

**Runnable now** — at this point only the PRD exists; `${SDD_SPECIFICATION_PATH}/` has not been created yet:

```bash
# Clarity scan. Runs on the PRD alone until a spec exists
/clarify {feature}
```

`/clarify` never writes to `requirement/**`, so its answers cannot be applied to the PRD — carry them into the
`/generate-spec` input above, or edit the PRD yourself.

**Available after `/generate-spec` has written the spec** — `/check-spec` reads
`${SDD_SPECIFICATION_PATH}/` and exits with an error while that directory is absent, so do not offer it as a
post-PRD step:

```bash
# Comprehensive review (inter-document consistency: PRD ↔ spec ↔ adr, plus quality)
/check-spec {feature} --full
```
