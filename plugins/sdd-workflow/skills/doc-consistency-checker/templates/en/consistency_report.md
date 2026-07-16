# Document Consistency Check Results Template

This template is the output format for document consistency check results.

---

## Document Consistency Check Results

### Target Documents

| Document | Path                                          | Last Updated |
|:---------|:----------------------------------------------|:-------------|
| PRD      | `${SDD_REQUIREMENT_PATH}/{feature-name}.md`          | YYYY-MM-DD   |
| spec     | `${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`   | YYYY-MM-DD   |
| design   | `${SDD_SPECIFICATION_PATH}/{feature-name}_design.md` | YYYY-MM-DD   |

### Check Results Summary

| Check Target            | Result                    | Count     |
|:------------------------|:--------------------------|:----------|
| PRD ↔ spec              | Consistent / Inconsistent | {n} items |
| spec ↔ design           | Consistent / Inconsistent | {n} items |

---

### Inconsistency Details

#### PRD ↔ spec

##### 1. {Inconsistency Title}

**Type**: Missing / Contradiction / Obsolescence

**PRD States**:

```markdown
{PRD content}
```

**spec States**:

```markdown
{spec content (or "Not documented")}
```

**Recommended Action**:

- [ ] Update spec to reflect requirement
- [ ] If PRD requirement is unnecessary, remove it

---

#### spec ↔ design

##### 1. {Inconsistency Title}

**Type**: Missing / Contradiction / Obsolescence

**spec States**:

```
{spec content}
```

**design States**:

```
{design content (or "Not documented")}
```

**Recommended Action**:

- [ ] Update design to reflect specification
- [ ] If spec is outdated, update it

---

> **Note**: `design ↔ Implementation` consistency is out of scope for this skill. Use `/check-spec`
> (the `impl-spec-check` feature) for design ↔ implementation checks.

### Verified Consistent Items

- {Verified item 1}
- {Verified item 2}

---

### Recommended Actions (Prioritized)

1. **High Priority**: {Action}
2. **Medium Priority**: {Action}
3. **Low Priority**: {Action}

---

### Notes

- {Supplementary notes}
