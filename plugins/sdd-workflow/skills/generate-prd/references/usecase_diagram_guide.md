# Use Case Diagram Guide for Mermaid

## Mermaid Constraints

Mermaid does **NOT** have native support for use case diagrams. Use `flowchart` (graph) as an alternative representation.

## Basic Notation

### Diagram Direction

| Direction | Description          | Use Case                          |
|:----------|:---------------------|:----------------------------------|
| `TB`      | Top to Bottom        | Standard vertical layout          |
| `LR`      | Left to Right        | Horizontal layout (recommended)   |

### Actor Representation

Use double parentheses `(( ))` for circular nodes representing actors:

```mermaid
flowchart LR
    User((User))
    Admin((Admin))
```

### Use Case Representation

Use brackets `[ ]` for rectangular nodes representing use cases:

```mermaid
flowchart LR
    UC1[Login]
    UC2[View Dashboard]
```

### System Boundary

Use `subgraph` to represent the system boundary:

```mermaid
flowchart LR
    User((User))

    subgraph System [Task Management System]
        UC1[Create Task]
        UC2[Edit Task]
        UC3[Delete Task]
    end

    User --> UC1
    User --> UC2
    User --> UC3
```

## Relationships

### Association (Actor to Use Case)

Use solid arrows `-->` for associations:

```mermaid
flowchart LR
    User((User)) --> UC1[Login]
```

### Include Relationship

Use dotted arrows with label for include relationships. The base use case **always** includes the included use case:

```mermaid
flowchart LR
    UC1[Create Order] -. include .-> UC2[Validate User]
```

**Direction**: Arrow points from base use case **to** included use case.

### Extend Relationship

Use dotted arrows with label for extend relationships. The extending use case **optionally** extends the base use case:

```mermaid
flowchart LR
    UC1[Checkout] -. extend .-> UC2[Apply Coupon]
```

**Direction**: Arrow points from extending use case **to** base use case.

## Complete Example

```mermaid
flowchart LR
    User((User))
    Admin((Admin))

    subgraph TaskManagement [Task Management System]
        UC1[Create Task]
        UC2[Edit Task]
        UC3[Delete Task]
        UC4[View Tasks]
        UC5[Validate Authentication]
        UC6[Send Notification]
        UC7[Bulk Delete]
    end

    User --> UC1
    User --> UC2
    User --> UC4
    Admin --> UC3
    Admin --> UC4

    UC1 -. include .-> UC5
    UC2 -. include .-> UC5
    UC3 -. include .-> UC5

    UC1 -. extend .-> UC6
    UC3 -. extend .-> UC7
```

## Common Mistakes

| Incorrect                           | Correct                              | Explanation                                              |
|:------------------------------------|:-------------------------------------|:---------------------------------------------------------|
| `User((User))` without `flowchart`  | `flowchart LR` then `User((User))`   | Must declare diagram type first                          |
| `--include-->`                      | `-. include .->`                     | Use dotted line syntax for stereotypes                   |
| `<<include>>`                       | `include`                            | Mermaid doesn't support UML stereotype syntax            |
| `Actor[User]`                       | `User((User))`                       | Use `(( ))` for actors, `[ ]` for use cases              |
| `UC1 -. include .-> UC2` (extend)   | `UC2 -. extend .-> UC1`              | Extend arrow goes FROM extending TO base                 |
| `system { ... }`                    | `subgraph System [ ... ] ... end`    | Use subgraph for system boundary                         |
| Spaces in node names                | Use underscores or camelCase         | `Create Task` → `CreateTask` or `Create_Task`            |
| Missing `end` for subgraph          | Always close with `end`              | Each `subgraph` must have matching `end`                 |

## Include vs Extend

| Aspect      | Include                                  | Extend                                           |
|:------------|:-----------------------------------------|:-------------------------------------------------|
| **Meaning** | Base use case ALWAYS includes the target | Extending use case OPTIONALLY extends the base   |
| **Arrow**   | Base → Included                          | Extending → Base                                 |
| **Example** | Login **includes** Validate Credentials  | Checkout **extended by** Apply Coupon            |

## Style Tips

### Adding Descriptions

Use node text for brief descriptions:

```mermaid
flowchart LR
    UC1[Create Task<br/>Add new task with details]
```

### Grouping Related Use Cases

Use nested subgraphs for categorization:

```mermaid
flowchart LR
    subgraph System [Application]
        subgraph Auth [Authentication]
            UC1[Login]
            UC2[Logout]
        end
        subgraph Tasks [Task Management]
            UC3[Create Task]
            UC4[Delete Task]
        end
    end
```

## Limitations

1. **No native use case shape**: Mermaid uses rectangles `[ ]` instead of ovals
2. **No generalization arrows**: Actor/use case inheritance not directly supported
3. **Limited styling**: Use CSS classes for custom styling if needed
4. **Label positioning**: Stereotype labels (`include`, `extend`) appear on the line, not above it
