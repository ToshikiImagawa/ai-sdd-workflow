# Output Example

Example of the markdown structure returned by this skill:

````markdown
## Requirements Diagram (SysML)

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram
    requirement Task_Management {
        id: UR_001
        text: "Users can efficiently manage tasks"
        risk: high
        verifymethod: demonstration
    }

    functionalRequirement Create_Task {
        id: FR_001
        text: "User can create new tasks"
        risk: high
        verifymethod: test
    }

    functionalRequirement Edit_Task {
        id: FR_002
        text: "User can edit existing tasks"
        risk: medium
        verifymethod: test
    }

    functionalRequirement Delete_Task {
        id: FR_003
        text: "User can delete tasks"
        risk: medium
        verifymethod: test
    }

    performanceRequirement Response_Time {
        id: NFR_001
        text: "Response time under 1 second"
        risk: medium
        verifymethod: demonstration
    }

    Task_Management - contains -> Create_Task
    Task_Management - contains -> Edit_Task
    Task_Management - contains -> Delete_Task
    Response_Time - traces -> Create_Task
```

## Diagram Structure

- **UR_001**: Task_Management (User Requirement)
  - **FR_001**: Create_Task (contains)
  - **FR_002**: Edit_Task (contains)
  - **FR_003**: Delete_Task (contains)
- **NFR_001**: Response_Time → traces → FR_001

## Relationship Summary

| From    | Relationship | To      | Rationale                                 |
|:--------|:-------------|:--------|:------------------------------------------|
| UR_001  | contains     | FR_001  | Task creation is part of task management  |
| UR_001  | contains     | FR_002  | Task editing is part of task management   |
| UR_001  | contains     | FR_003  | Task deletion is part of task management  |
| NFR_001 | traces       | FR_001  | Response time affects task creation UX    |
````
