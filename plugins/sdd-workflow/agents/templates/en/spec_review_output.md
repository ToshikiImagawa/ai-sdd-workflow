## Specification Review Results

### Target Document

- `{document path}`

### CONSTITUTION.md Compliance Check

**Principle Version**: v{X.Y.Z}
**Principle File**: `.sdd/CONSTITUTION.md`

| Principle Category        | Principle ID | Principle Name   | Compliance Status                      |
|:--------------------------|:-------------|:-----------------|:---------------------------------------|
| Architecture Principles   | A-001        | {Principle Name} | Compliant / Violation / Needs Review   |
| Architecture Principles   | A-002        | {Principle Name} | Compliant / Violation / Needs Review   |
| Development Principles    | D-001        | {Principle Name} | Compliant / Violation / Needs Review   |
| Technical Constraints     | T-001        | {Principle Name} | Compliant / Violation / Needs Review   |
| ...                       | ...          | ...              | ...                                    |

### Principle Violations (Fix Proposals)

#### Violation 1: {Principle ID} - {Principle Name}

**Violation Location**: {Section name} / {Relevant text}

**Violation Content**:
{Specific violation description}

**Fix Proposal**:
```markdown
{Corrected description}
```

**Fix Priority**: High / Medium / Low

---

### Evaluation Summary

| Perspective              | Rating                                           | Comment   |
|:-------------------------|:-------------------------------------------------|:----------|
| CONSTITUTION Compliance  | Compliant / Partial Violation / Major Violation  | {Comment} |
| Completeness             | Good / Needs Improvement / Needs Fix             | {Comment} |
| Clarity                  | Good / Needs Improvement / Needs Fix             | {Comment} |
| Consistency              | Good / Needs Improvement / Needs Fix             | {Comment} |
| SysML Compliance         | Good / Needs Improvement / Needs Fix             | {Comment} |

### Needs Fix (Critical)

#### 1. {Issue Title}

**Location**: {Section name} / {Line number}

**Issue**:
{Specific problem description}

**Improvement Suggestion**:

```md
{Example of corrected description}
```

---

### Needs Improvement (Recommended)

#### 1. {Issue Title}

**Location**: {Section name}

**Issue**: {Problem description}

**Improvement Suggestion**: {Direction for improvement}

---

### Good Practices

- {Good point 1}
- {Good point 2}

---

### Missing Sections

The following sections need to be added:

| Section        | Reason          | Priority            |
|:---------------|:----------------|:--------------------|
| {Section name} | {Reason to add} | High / Medium / Low |

### Traceability Check Results

#### PRD - spec Traceability Matrix (spec files only)

| Requirement ID | Requirement Type | PRD Requirement Content | Spec Mapping | Status |
|:---|:---|:---|:---|:---|
| UR-001 | User Requirement | {User requirement content} | {Corresponding user story} | 🟢 Covered / 🟡 Partially Covered |
| FR-001 | Functional Requirement | {Functional requirement content} | {Corresponding functional requirement/API} | 🟢 Covered |
| FR-002 | Functional Requirement | {Functional requirement content} | Not documented | 🔴 Not Covered |
| NFR-001 | Non-Functional Requirement | {Non-functional requirement content} | {Corresponding constraints/quality requirements} | 🟢 Covered |
| NFR-002 | Non-Functional Requirement | {Non-functional requirement content} | Partially documented | 🟡 Partially Covered |

**Coverage: {X}% ({Covered+Partially Covered}/{Total Requirements})**

Warning: Coverage is below 80% (displayed only when coverage is below 80%)

**Criteria**:
- 🟢 **Covered**: PRD requirement is clearly documented in spec with implementation approach defined
- 🟡 **Partially Covered**: Related description exists in spec but doesn't fully cover the requirement
- 🔴 **Not Covered**: No corresponding description found in spec

##### 🔴 Not Covered Requirements ({n} items)

###### FR-002: {Functional Requirement Title}

**PRD Description**:
```
{Requirement details documented in PRD}
```

**spec Status**: No corresponding functional requirement documented

**Recommended Actions**:
1. [ ] Add functional requirement to spec and clarify implementation approach
2. [ ] Add API design if necessary

#### spec - design Consistency (design files only)

| spec Element | spec Description | design Mapping | Status |
|:---|:---|:---|:---|
| API Definition | `{API name}({args})` | {Detailed implementation approach/signature} | 🟢 Consistent / 🔴 Inconsistent |
| Data Model | `{Type name}` | {Detailed type definition/field specification} | 🟢 Consistent / 🔴 Inconsistent |
| Constraints | {Constraint content} | {How constraint is considered/implementation response} | 🟢 Considered / 🔴 Not Considered |
| Functional Requirement | {Functional requirement content} | {Implementation approach/architecture choice} | 🟢 Consistent / 🔴 Inconsistent |

##### 🔴 Inconsistent Items ({n} items)

###### API Definition Inconsistency: {API Name}

**spec Description**:
```
{API name}({args}): {return value}
```

**design Description**:
```
{Different implementation definition}
```

**Inconsistency**: {Specific difference description}

**Recommended Actions**:
1. [ ] Unify definition between spec and design
2. [ ] Verify validity of change

#### Consistency Check Summary

| Check Target        | Result                      | Details                                      |
|:--------------------|:----------------------------|:---------------------------------------------|
| PRD - spec          | 🟢 Consistent / 🔴 Inconsistent | Coverage: {X}%, Not Covered: {n} items       |
| spec - design       | 🟢 Consistent / 🔴 Inconsistent | Inconsistencies: {n} items                   |
| CONSTITUTION - docs | 🟢 Compliant / 🔴 Violation / No Principles | Violations: {n} items, Partial Violations: {n} items |

### Fix Proposal Summary

| Fix Target | Fix Content | Status                    |
|:-----------|:------------|:--------------------------|
| {Target 1} | {Content 1} | Proposed                  |
| {Target 2} | {Content 2} | Requires Discussion       |

### Recommended Actions

1. {Action 1}
2. {Action 2}
3. {Action 3}

---

### Simplified Output (--summary option / called from check-spec)

### Quality Review Results

#### Specification Quality Score

| Document | CONSTITUTION Compliance | Completeness | Clarity | SysML Compliance | Overall Rating |
|:---|:---|:---|:---|:---|:---|
| `{file path}` | 🟢 Compliant / 🟡 Partial Violation / 🔴 Violation | Good / Needs Improvement | Good / Needs Improvement | Good / Needs Improvement / - | 🟢 Good / 🟡 Needs Improvement / 🔴 Requires Fix |

**Note**: Design files are not subject to SysML compliance check (`-` displayed)

#### Traceability Check Results

##### PRD - spec Traceability (spec files only)

| Requirement ID | PRD Requirement Content | Spec Mapping | Status |
|:---|:---|:---|:---|
| UR-001 | {User requirement content} | {Corresponding user story} | 🟢 Covered / 🟡 Partially Covered |
| FR-001 | {Functional requirement content} | {Corresponding functional requirement/API} | 🟢 Covered |
| FR-002 | {Functional requirement content} | Not documented | 🔴 Not Covered |
| NFR-001 | {Non-functional requirement content} | {Corresponding constraints/quality requirements} | 🟢 Covered |

**Coverage: {X}% ({Covered+Partially Covered}/{Total Requirements})**

Warning: Coverage is below 80% (displayed only when coverage is below 80%)

##### spec - design Consistency (design files only)

| spec Element | spec Description | design Mapping | Status |
|:---|:---|:---|:---|
| API Definition | `{API name}({args})` | {Detailed implementation approach} | 🟢 Consistent / 🔴 Inconsistent |
| Data Model | `{Type name}` | {Detailed type definition} | 🟢 Consistent / 🔴 Inconsistent |
| Constraints | {Constraint content} | {How constraint is considered} | 🟢 Considered / 🔴 Not Considered |

#### Detected Issues

##### 🔴 CONSTITUTION.md Violations ({n} items)

- **Violation**: {Content violating project principles}
- **Location**: `{filename}` section {section}
- **Recommended Fix**: {How to fix}

##### 🟡 Completeness Issues ({n} items)

- **Missing Section**: {Required section name}
- **Target File**: `{filename}`
- **Recommended Action**: Add section and document {content}

##### 🟡 Vague Descriptions ({n} items)

- **Vague Expression**: "{Detected vague expression}"
- **Location**: `{filename}` section {section}
- **Recommended Fix**: {Specify concrete criteria and implementation approach}
