## User Requirements (UR)

| ID     | Requirement                               | Priority | Risk   |
|:-------|:------------------------------------------|:---------|:-------|
| UR-001 | Users can efficiently manage tasks        | Must     | High   |
| UR-002 | System provides intuitive task operations | Should   | Medium |

## Functional Requirements (FR)

| ID     | Requirement                     | Derived From | Priority | Risk   | Verification |
|:-------|:--------------------------------|:-------------|:---------|:-------|:-------------|
| FR-001 | User can create new tasks       | UR-001       | Must     | High   | Test         |
| FR-002 | User can edit existing tasks    | UR-001       | Must     | Medium | Test         |
| FR-003 | User can delete tasks           | UR-001       | Must     | Medium | Test         |
| FR-004 | User can mark tasks as complete | UR-001       | Must     | Low    | Test         |

## Non-Functional Requirements (NFR)

| ID      | Requirement                   | Category    | Priority | Risk   | Verification  |
|:--------|:------------------------------|:------------|:---------|:-------|:--------------|
| NFR-001 | Response time under 1 second  | Performance | Should   | Medium | Demonstration |
| NFR-002 | System available 99.9% uptime | Reliability | Should   | High   | Analysis      |
| NFR-003 | User actions logged for audit | Security    | Could    | Low    | Inspection    |

## Requirements Summary

| Category  | Count |  Must | Should | Could |
|:----------|------:|------:|-------:|------:|
| UR        |     2 |     1 |      1 |     0 |
| FR        |     4 |     4 |      0 |     0 |
| NFR       |     3 |     0 |      2 |     1 |
| **Total** | **9** | **5** |  **3** | **1** |
