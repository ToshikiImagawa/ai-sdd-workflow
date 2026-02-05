# Mermaid Notation Rules

Mermaid is a JavaScript-based tool that creates diagrams from markdown-like text syntax. This guide covers the essential syntax rules for creating diagrams in AI-SDD workflow documentation.

## Dark Theme Configuration

All diagrams should use dark theme for consistency. Add this directive at the beginning of each diagram:

```
%%{init: {'theme': 'dark'}}%%
```

---

## 1. Flowchart Syntax

Flowcharts are the most versatile diagram type, used for process flows, use case diagrams, and general visualizations.

### Diagram Direction

| Direction | Description       | Example                    |
|:----------|:------------------|:---------------------------|
| `TB`      | Top to Bottom     | Vertical flow (default)    |
| `TD`      | Top Down          | Same as TB                 |
| `BT`      | Bottom to Top     | Reverse vertical flow      |
| `LR`      | Left to Right     | Horizontal flow            |
| `RL`      | Right to Left     | Reverse horizontal flow    |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A[Start] --> B[Process] --> C[End]
```

### Node Shapes

| Shape                | Syntax              | Use Case                       |
|:---------------------|:--------------------|:-------------------------------|
| Rectangle            | `[text]`            | Process, action                |
| Round edges          | `(text)`            | Start/End, general             |
| Stadium (pill)       | `([text])`          | Use cases (oval-like)          |
| Subroutine           | `[[text]]`          | Predefined process             |
| Cylinder             | `[(text)]`          | Database                       |
| Circle               | `((text))`          | Actors, connectors             |
| Asymmetric           | `>text]`            | Input/Output                   |
| Rhombus (diamond)    | `{text}`            | Decision                       |
| Hexagon              | `{{text}}`          | Preparation                    |
| Parallelogram        | `[/text/]`          | Input                          |
| Parallelogram alt    | `[\text\]`          | Output                         |
| Trapezoid            | `[/text\]`          | Manual operation               |
| Trapezoid alt        | `[\text/]`          | Manual operation               |
| Double circle        | `(((text)))`        | Double circle                  |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A[Rectangle] --> B(Round)
    B --> C([Stadium])
    C --> D[(Database)]
    D --> E((Circle))
    E --> F{Decision}
```

### Link Types

| Type              | Syntax            | Description                    |
|:------------------|:------------------|:-------------------------------|
| Arrow             | `-->`             | Standard directed link         |
| Open link         | `---`             | Undirected connection          |
| Dotted arrow      | `-.->`            | Dependency, optional           |
| Dotted line       | `-.-`             | Weak connection                |
| Thick arrow       | `==>`             | Strong/main flow               |
| Thick line        | `===`             | Strong undirected              |
| Invisible         | `~~~`             | Layout control (no line)       |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A --> B
    B -.-> C
    C ==> D
    D --- E
```

### Link Labels

Add text to links using `|text|` syntax:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A -->|Yes| B
    A -->|No| C
    B -.include.-> D
    C -.extend.-> E
```

### Link Length

Control link length with additional dashes or equals:

| Length  | Syntax      | Description        |
|:--------|:------------|:-------------------|
| Normal  | `-->`       | Default length     |
| Long    | `--->`      | Longer link        |
| Longer  | `---->`     | Even longer        |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A --> B
    A ---> C
    A ----> D
```

### Subgraphs (System Boundary)

Group nodes using subgraphs:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    subgraph SystemBoundary [System Name]
        direction TB
        A[Process 1]
        B[Process 2]
    end

    Actor((Actor)) --> A
    Actor --> B
```

Nested subgraphs are supported:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph Main [Main System]
        subgraph Sub1 [Subsystem A]
            A1[Component 1]
        end
        subgraph Sub2 [Subsystem B]
            B1[Component 2]
        end
    end

    A1 --> B1
```

### Special Characters in Text

Use quotes for text with special characters:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A["Text with (parentheses)"]
    B["Text with [brackets]"]
    C["Line 1<br/>Line 2"]
```

### Node IDs and Display Text

Separate ID from display text:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    nodeId[Display Text]
    anotherNode([Different Shape])

    nodeId --> anotherNode
```

---

## 2. Requirement Diagram Syntax

For formal requirement diagrams, use the `requirementDiagram` type.

### Basic Structure

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram

    requirement Example_Requirement {
        id: REQ_001
        text: "Requirement description"
        risk: medium
        verifymethod: test
    }
```

### Requirement Types

| Type                     | Description             | Example                          |
|:-------------------------|:------------------------|:---------------------------------|
| `requirement`            | General requirement     | Overall system requirements      |
| `functionalRequirement`  | Functional requirement  | Display function, operation      |
| `performanceRequirement` | Performance requirement | Response time, throughput        |
| `interfaceRequirement`   | Interface requirement   | API design, UI components        |
| `physicalRequirement`    | Physical requirement    | Size, weight constraints         |
| `designConstraint`       | Design constraint       | Technology stack, architecture   |

### Attribute Values

**Important: Write all attribute values in lowercase**

#### Risk Level (risk)

| Value    | Meaning                                               |
|:---------|:------------------------------------------------------|
| `high`   | High risk (business-critical, difficult to implement) |
| `medium` | Medium risk (important but alternatives exist)        |
| `low`    | Low risk (nice to have)                               |

#### Verification Method (verifymethod)

| Value           | Meaning                       | Description                             |
|:----------------|:------------------------------|:----------------------------------------|
| `analysis`      | Verification by analysis      | Design review, static analysis          |
| `test`          | Verification by testing       | Unit test, integration test, E2E test   |
| `demonstration` | Verification by demonstration | Operation verification on actual device |
| `inspection`    | Verification by inspection    | Code review, document review            |

### Relationship Types

| Relationship | Notation                            | Meaning                              |
|:-------------|:------------------------------------|:-------------------------------------|
| `contains`   | `A - contains -> B`                 | A contains B (parent-child)          |
| `derives`    | `A - derives -> B`                  | A derives from B                     |
| `satisfies`  | `A - satisfies -> B`                | A satisfies requirement B            |
| `verifies`   | `A - verifies -> B`                 | A verifies requirement B             |
| `refines`    | `A - refines -> B`                  | A refines requirement B              |
| `traces`     | `A - traces -> B`                   | A traces to B                        |
| `copies`     | `A - copies -> B`                   | A copies from B                      |

### Elements (Non-requirement nodes)

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram

    requirement Login_Feature {
        id: REQ_001
        text: "User can login"
        risk: high
        verifymethod: test
    }

    element AuthService {
        type: "Block"
    }

    element LoginTest {
        type: "TestCase"
    }

    AuthService - satisfies -> Login_Feature
    LoginTest - verifies -> Login_Feature
```

---

## 3. Styling

### Inline Node Styling

Apply styles directly to nodes:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A[Requirement]
    B[Use Case]
    C[Block]

    style A fill:#1a237e,stroke:#7986cb,color:#fff
    style B fill:#bf360c,stroke:#ff8a65,color:#fff
    style C fill:#1b5e20,stroke:#81c784,color:#fff

    A --> B --> C
```

### Style Classes

Define reusable classes:

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A[Requirement 1]:::req
    B[Requirement 2]:::req
    C[Component]:::block

    A --> C
    B --> C

    classDef req fill:#1a237e,stroke:#7986cb,color:#fff
    classDef block fill:#1b5e20,stroke:#81c784,color:#fff
```

### Recommended Dark Theme Color Palette

| Element Type    | Fill Color | Stroke Color | Text Color |
|:----------------|:-----------|:-------------|:-----------|
| Requirement     | `#1a237e`  | `#7986cb`    | `#fff`     |
| Use Case        | `#bf360c`  | `#ff8a65`    | `#fff`     |
| Block/Component | `#1b5e20`  | `#81c784`    | `#fff`     |
| Actor           | `#4a148c`  | `#ba68c8`    | `#fff`     |
| Test Case       | `#006064`  | `#4dd0e1`    | `#fff`     |
| Rationale       | `#f57f17`  | `#ffee58`    | `#000`     |

---

## 4. Common Mistakes

| Incorrect                       | Correct                            | Explanation                           |
|:--------------------------------|:-----------------------------------|:--------------------------------------|
| `risk: High`                    | `risk: high`                       | Attribute values in lowercase         |
| `verifymethod: Test`            | `verifymethod: test`               | Attribute values in lowercase         |
| `text: description`             | `text: "description"`              | Enclose text in quotes                |
| `requirement name with space`   | `requirement_name_with_underscore` | No spaces in names (use underscores)  |
| `User((User))` without flowchart| `flowchart LR` then `User((User))` | Must declare diagram type first       |
| `--include-->`                  | `-. include .->`                   | Use dotted syntax for stereotypes     |
| `<<include>>`                   | `include` (as label)               | Mermaid doesn't support UML syntax    |
| Missing `end` for subgraph      | Always close with `end`            | Each subgraph needs matching end      |
| Spaces in node IDs              | `Create_Task` or `CreateTask`      | Use underscores or camelCase          |

---

## 5. Complete Example

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    User((User))
    Admin((Admin))

    subgraph System [Task Management System]
        UC1(["Create Task"])
        UC2(["Edit Task"])
        UC3(["Delete Task"])
        UC4(["Authenticate"])
    end

    User --> UC1
    User --> UC2
    Admin --> UC3

    UC1 -. include .-> UC4
    UC2 -. include .-> UC4
    UC3 -. include .-> UC4

    classDef actor fill:#4a148c,stroke:#ba68c8,color:#fff
    classDef usecase fill:#bf360c,stroke:#ff8a65,color:#fff

    class User,Admin actor
    class UC1,UC2,UC3,UC4 usecase
```

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram

    requirement Task_Management {
        id: REQ_001
        text: "System shall manage tasks"
        risk: high
        verifymethod: test
    }

    functionalRequirement Create_Task {
        id: FR_001
        text: "User can create tasks"
        risk: medium
        verifymethod: test
    }

    functionalRequirement Edit_Task {
        id: FR_002
        text: "User can edit tasks"
        risk: low
        verifymethod: test
    }

    element TaskService {
        type: "Block"
    }

    Task_Management - contains -> Create_Task
    Task_Management - contains -> Edit_Task
    TaskService - satisfies -> Create_Task
    TaskService - satisfies -> Edit_Task
```

---

## References

- [Mermaid Official Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [GitHub Mermaid Support](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
