# Document Consistency Check Results Template

This template is the output format for document consistency check results.

---

## Document Consistency Check Results

### Target Documents

| Document | Path                                          | Last Updated |
|:---------|:----------------------------------------------|:-------------|
| PRD      | `.sdd/requirement/{feature-name}.md`          | YYYY-MM-DD   |
| spec     | `.sdd/specification/{feature-name}_spec.md`   | YYYY-MM-DD   |
| design   | `.sdd/specification/{feature-name}_design.md` | YYYY-MM-DD   |

### Check Results Summary

| Check Target            | Result                    | Count     |
|:------------------------|:--------------------------|:----------|
| PRD ↔ spec              | Consistent / Inconsistent | {n} items |
| spec ↔ design           | Consistent / Inconsistent | {n} items |
| design ↔ Implementation | Consistent / Inconsistent | {n} items |

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

#### design ↔ Implementation

##### 1. {Inconsistency Title}

**Type**: Missing / Contradiction / Obsolescence

**design States**:

```
{design content}
```

**Implementation**:

```
{Actual file structure/code}
```

**Recommended Action**:

- [ ] Update design to match implementation
- [ ] Fix implementation to match design

---

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
