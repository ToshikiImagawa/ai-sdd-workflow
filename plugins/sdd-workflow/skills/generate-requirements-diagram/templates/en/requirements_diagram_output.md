# Requirements Diagram Output Format

**IMPORTANT: This skill returns TEXT only. It does NOT write files.**

Return the following sections:

## Requirements Diagram (SysML)

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram
    requirement System_Requirement {
        id: REQ_001
        text: "Overall system requirement"
        risk: high
        verifymethod: demonstration
    }

    functionalRequirement Create_Task {
        id: FR_001
        text: "User can create tasks"
        risk: high
        verifymethod: test
    }

    functionalRequirement Edit_Task {
        id: FR_002
        text: "User can edit tasks"
        risk: medium
        verifymethod: test
    }

    performanceRequirement Response_Time {
        id: NFR_001
        text: "Response time under 1 second"
        risk: medium
        verifymethod: test
    }

    System_Requirement - contains -> Create_Task
    System_Requirement - contains -> Edit_Task
    System_Requirement - contains -> Response_Time
    Response_Time - traces -> Create_Task
```

## Diagram Structure

### Requirement Hierarchy

```
REQ_001 (System Requirement)
├── FR_001 (Create Task)
├── FR_002 (Edit Task)
└── NFR_001 (Response Time)
    └── traces -> FR_001
```

### Relationship Summary

| Source  | Relationship | Target | Rationale                        |
|:--------|:-------------|:-------|:---------------------------------|
| REQ_001 | contains     | FR_001 | Core functionality               |
| REQ_001 | contains     | FR_002 | Core functionality               |
| NFR_001 | traces       | FR_001 | Performance applies to creation  |
