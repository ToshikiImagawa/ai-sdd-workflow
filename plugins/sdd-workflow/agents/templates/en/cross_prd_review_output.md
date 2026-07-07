## Cross-PRD Review Results

### Target Documents

| # | PRD | id | category |
|:--|:----|:---|:---------|
| 1 | `{document path}` | `{front matter id}` | `{category}` |
| 2 | `{document path}` | `{front matter id}` | `{category}` |

### Perspective Summary

| Perspective                       | Rating                               | Comment   |
|:----------------------------------|:--------------------------------------|:----------|
| Category Boundary Consistency     | Good / Needs Improvement / Needs Fix | {Comment} |
| Terminology Alignment             | Good / Needs Improvement / Needs Fix | {Comment} |
| Structure & Notation Uniformity   | Good / Needs Improvement / Needs Fix | {Comment} |
| Principle Reference Coverage      | Good / Needs Improvement / Skipped   | {Comment} |
| Front Matter Labeling Consistency | Good / Needs Improvement / Needs Fix | {Comment} |

### Findings

#### [must] 1. {Finding Title}

**Files**: `{file A}` ({section}), `{file B}` ({section})

**Issue**:
{Contradiction or broken cross-reference description}

**Fix Proposal**:
```markdown
{Corrected description or delegation}
```

---

#### [recommend] 1. {Finding Title}

**Files**: `{file(s)}` ({section})

**Issue**: {Inconsistency description}

**Fix Proposal**: {Unified convention or wording}

---

#### [nits] 1. {Finding Title}

**Files**: `{file(s)}`

**Issue**: {Cosmetic divergence}

---

### Principle Reference Coverage Matrix

| Principle | {PRD 1} | {PRD 2} | {PRD n} | Gap Assessment |
|:----------|:-------:|:-------:|:-------:|:----------------|
| B-001     | ○       | ○       | ✗       | {Relevant? Why} |
| D-002     | ○       | ✗       | ✗       | {Relevant? Why} |

### Boundary Delegation Matrix

| Responsibility | Declared Out of Scope by | Claimed by | Status                     |
|:----------------|:--------------------------|:-----------|:----------------------------|
| {Responsibility} | {PRD A}                  | {PRD B}    | Covered / Orphaned / Duplicated |

### Good Practices

- {Consistent practice worth keeping 1}
- {Consistent practice worth keeping 2}

### Fix Proposal Summary

| # | Severity | Files | Fix Content | Status              |
|:--|:---------|:------|:------------|:---------------------|
| 1 | must     | {files} | {content} | Proposed            |
| 2 | recommend | {files} | {content} | Requires Discussion |

### Recommended Actions

1. {Action 1}
2. {Action 2}
3. {Action 3}
