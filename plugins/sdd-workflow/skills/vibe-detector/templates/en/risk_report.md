# Vibe Coding Risk Detection Report Template

This template is the output format for Vibe Coding risk detection.

---

## Vibe Coding Risk Detected

### Risk Level: High / Medium / Low

### Detected Vague Instructions

| # | Location     | Pattern        | Issue            |
|:--|:-------------|:---------------|:-----------------|
| 1 | "{location}" | {Pattern name} | {Specific issue} |
| 2 | "{location}" | {Pattern name} | {Specific issue} |

### Items Requiring Clarification

- [ ] {Question 1}
- [ ] {Question 2}
- [ ] {Question 3}

### Specification Status

| Document    | Status           |
|:------------|:-----------------|
| PRD         | Exists / Missing |
| *_spec.md   | Exists / Missing |
| *_design.md | Exists / Missing |

### Recommended Actions

**For High Risk**:

1. Confirm clarification items above with user
2. Create specifications with `/generate_spec`
3. Start implementation after spec review

**For Medium Risk**:

1. Confirm ambiguous points with a user
2. Update specifications as needed
3. Start implementation

**For Low Risk**:

- Can start implementation
