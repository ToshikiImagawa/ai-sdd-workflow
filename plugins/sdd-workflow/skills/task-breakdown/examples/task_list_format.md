# {Feature Name} Task Breakdown

## Meta Information

| Item | Content |
|:---|:---|
| Feature Name | {Feature Name} |
| Ticket Number | {Ticket Number} (if specified) |
| Design Document | `.sdd/specification/{feature-name}_design.md` |
| Created Date | YYYY-MM-DD |

## Task List

### Phase 1: Foundation

| # | Task | Description | Completion Criteria | Dependencies |
|:---|:---|:---|:---|:---|
| 1.1 | {Task Name} | {Detailed Description} | {Completion Criteria} | - |
| 1.2 | {Task Name} | {Detailed Description} | {Completion Criteria} | 1.1 |

### Phase 2: Core Implementation

| # | Task | Description | Completion Criteria | Dependencies |
|:---|:---|:---|:---|:---|
| 2.1 | {Task Name} | {Detailed Description} | {Completion Criteria} | 1.x |
| 2.2 | {Task Name} | {Detailed Description} | {Completion Criteria} | 1.x |

### Phase 3: Integration

| # | Task | Description | Completion Criteria | Dependencies |
|:---|:---|:---|:---|:---|
| 3.1 | {Task Name} | {Detailed Description} | {Completion Criteria} | 2.x |

### Phase 4: Testing

| # | Task | Description | Completion Criteria | Dependencies |
|:---|:---|:---|:---|:---|
| 4.1 | {Task Name} | {Detailed Description} | {Completion Criteria} | 3.x |

### Phase 5: Finishing

| # | Task | Description | Completion Criteria | Dependencies |
|:---|:---|:---|:---|:---|
| 5.1 | {Task Name} | {Detailed Description} | {Completion Criteria} | 4.x |

## Dependency Diagram

```mermaid
graph TD
    subgraph "Phase 1: Foundation"
        T1_1[1.1 {Task Name}]
        T1_2[1.2 {Task Name}]
    end

    subgraph "Phase 2: Core"
        T2_1[2.1 {Task Name}]
        T2_2[2.2 {Task Name}]
    end

    T1_1 --> T1_2
    T1_2 --> T2_1
    T1_2 --> T2_2
```

## Implementation Notes

- {Note 1}
- {Note 2}

## Reference Documents

- Abstract Specification: `.sdd/specification/[{parent-feature}/]{feature-name}_spec.md`
- Technical Design Document: `.sdd/specification/[{parent-feature}/]{feature-name}_design.md`

For hierarchical structure, parent feature uses `index_spec.md`, `index_design.md`
