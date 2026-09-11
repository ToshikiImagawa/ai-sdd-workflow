## Specification & Design Doc Generation Complete

### Generated Files

- [x] `${SDD_SPECIFICATION_PATH}/[{parent}/]{feature}_spec.md` (Abstract Specification, persistent)
- [x] `${SDD_TASK_PATH}/{ticket-number}/design-draft.md` (Technical Design Doc draft, temporary — deleted after
  implementation, once its key decisions are appended to `${SDD_ADR_PATH}/{feature}.md`)

※ For hierarchical structure, parent features use `index_spec.md`. The design draft is ticket-scoped, so its
path is the same in both structures

※ List only the files actually written. If Design Doc generation was skipped (see "Skip Design Doc Generation"),
remove that line and state why it was skipped

### CONSTITUTION.md Compliance Check Results

#### spec Check Results

| Principle Category      | Status       |
|:------------------------|:-------------|
| Business Principles     | 🟢 Compliant |
| Architecture Principles | 🟢 Compliant |
| Development Principles  | 🟢 Compliant |
| Technical Constraints   | 🟢 Compliant |

#### design Check Results

| Principle Category      | Status       |
|:------------------------|:-------------|
| Business Principles     | 🟢 Compliant |
| Architecture Principles | 🟢 Compliant |
| Development Principles  | 🟢 Compliant |
| Technical Constraints   | 🟢 Compliant |

**Fix proposals applied**: {count} items
**Requires discussion**: {count} items (see details above)

### Next Steps

1. Review generated specification & design draft content
2. Break down into tasks with `/task-breakdown {feature} {ticket-number}`
3. Verify clarity with `/clarify` before starting implementation
4. After implementation, `/task-cleanup {ticket-number}` appends the key decisions to
   `${SDD_ADR_PATH}/{feature}.md` and deletes the draft

### Recommended Manual Verification

- [ ] Verify generated specification content matches user intent
- [ ] Verify technology stack selection fits project constraints
- [ ] Verify data model type definitions follow project conventions

### Verification Commands

```bash
# Consistency check (spec ↔ implementation) — run once implementation exists
/check-spec {feature}

# Comprehensive review (inter-document consistency: PRD ↔ spec ↔ adr, plus quality)
/check-spec {feature} --full

# Specification clarity scan
/clarify {feature}
```
