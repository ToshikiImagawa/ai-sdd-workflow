# Output Format Example

This shows the markdown structure to return when generating a use case diagram.

```markdown
## Use Case Diagram

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    User((User))
    Admin((Admin))

    subgraph SystemName [System Name]
        UC1(["Use Case 1"])
        UC2(["Use Case 2"])
        UC3(["Use Case 3"])
        UC4(["Common Function"])
    end

    User --- UC1
    User --- UC2
    Admin --- UC3
    UC1 -.->|"&lt;&lt;include&gt;&gt;"| UC4

    classDef actor fill:#4a148c,stroke:#ba68c8,color:#fff
    classDef usecase fill:#bf360c,stroke:#ff8a65,color:#fff

    class User,Admin actor
    class UC1,UC2,UC3,UC4 usecase
```

## Actors

| Actor | Description |
|:------|:------------|
| User  | Logged-in user who performs main operations |
| Admin | Administrator with elevated privileges |

## Use Cases

| ID  | Use Case       | Description                        | Actor(s) |
|:----|:---------------|:-----------------------------------|:---------|
| UC1 | Use Case 1     | Brief description of use case 1    | User     |
| UC2 | Use Case 2     | Brief description of use case 2    | User     |
| UC3 | Use Case 3     | Brief description of use case 3    | Admin    |
| UC4 | Common Function| Shared function included by others | -        |
```
