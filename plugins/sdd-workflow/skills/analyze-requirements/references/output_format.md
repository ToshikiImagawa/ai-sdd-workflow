# Output Format Reference

This document defines the markdown structure that `analyze-requirements` must return.

```markdown
## User Requirements (UR)

| ID     | Requirement                                | Priority | Risk   |
|:-------|:--------------------------------------------|:---------|:-------|
| UR_001 | Users can efficiently manage tasks         | Must     | High   |
| UR_002 | System provides intuitive task operations  | Should   | Medium |

## Functional Requirements (FR)

| ID     | Requirement                           | Derived From | Priority | Risk   | Verification |
|:-------|:--------------------------------------|:-------------|:---------|:-------|:-------------|
| FR_001 | User can create new tasks             | UR_001       | Must     | High   | Test         |
| FR_002 | User can edit existing tasks          | UR_001       | Must     | Medium | Test         |
| FR_003 | User can delete tasks                 | UR_001       | Must     | Medium | Test         |
| FR_004 | User can mark tasks as complete       | UR_001       | Must     | Low    | Test         |

## Non-Functional Requirements (NFR)

| ID      | Requirement                          | Category    | Priority | Risk   | Verification   |
|:--------|:--------------------------------------|:------------|:---------|:-------|:---------------|
| NFR_001 | Response time under 1 second         | Performance | Should   | Medium | Demonstration  |
| NFR_002 | System available 99.9% uptime        | Reliability | Should   | High   | Analysis       |
| NFR_003 | User actions logged for audit        | Security    | Could    | Low    | Inspection     |

## Requirements Summary

| Category | Count | Must | Should | Could |
|:---------|------:|-----:|-------:|------:|
| UR       |     2 |    1 |      1 |     0 |
| FR       |     4 |    4 |      0 |     0 |
| NFR      |     3 |    0 |      2 |     1 |
| **Total**|   **9**| **5**|  **3** | **1** |
```
