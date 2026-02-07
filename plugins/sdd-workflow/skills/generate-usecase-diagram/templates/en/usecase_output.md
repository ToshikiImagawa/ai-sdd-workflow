# Use Case Diagram Output Format

**IMPORTANT: This skill returns TEXT only. It does NOT write files.**

Return the following sections:

## 1. Use Case Diagram (Mermaid)

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    User((User))

    subgraph System [System Name]
        UC1(["Use Case 1"])
        UC2(["Use Case 2"])
    end

    User --- UC1
    UC1 -.->|" <<include>> "| UC2
    classDef actor fill: #4a148c, stroke: #ba68c8, color: #fff
    classDef usecase fill: #bf360c, stroke: #ff8a65, color: #fff
    class User actor
    class UC1,UC2 usecase
```

## 2. Actors Table

| Actor | Description      |
|:------|:-----------------|
| User  | Role description |

## 3. Use Cases Table

| ID  | Use Case | Description | Related Actors |
|:----|:---------|:------------|:---------------|
| UC1 | Name     | Description | Actor          |

## 4. Relationships (if any include/extend exists)

| Relationship | From | To  | Description                    |
|:-------------|:-----|:----|:-------------------------------|
| include      | UC1  | UC2 | Always executed as part of UC1 |
| extend       | UC3  | UC1 | Optional behavior for UC1      |