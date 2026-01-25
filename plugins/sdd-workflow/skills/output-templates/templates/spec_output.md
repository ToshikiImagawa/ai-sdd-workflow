## Specification & Design Doc Generation Complete

### Generated Files

- [x] `.sdd/specification/[{parent}/]{feature}_spec.md` (Abstract Specification)
- [x] `.sdd/specification/[{parent}/]{feature}_design.md` (Technical Design Doc)

※ For hierarchical structure, parent features use `index_spec.md`, `index_design.md`

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

**Auto-fixed**: {count} items
**Fixes needed**: {count} items (see details above)

### Next Steps

1. Review generated specification & design doc content
2. Break down into tasks with `/task_breakdown`
3. Verify clarity with `/clarify` before starting implementation

### Recommended Manual Verification

- [ ] Verify generated specification content matches user intent
- [ ] Verify technology stack selection fits project constraints
- [ ] Verify data model type definitions follow project conventions

### Verification Commands

```bash
# Consistency check (design ↔ implementation)
/check_spec {feature}

# Comprehensive review (inter-document consistency + quality)
/check_spec {feature} --full

# Specification clarity scan
/clarify {feature}
```
