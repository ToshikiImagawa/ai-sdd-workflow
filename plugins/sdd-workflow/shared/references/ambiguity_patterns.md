# Ambiguity Detection Patterns

## Expressions to Avoid

| Pattern                      | Issue                     | Improvement Example               |
|:-----------------------------|:--------------------------|:----------------------------------|
| "appropriately," "as needed" | Criteria unclear          | Describe specific conditions      |
| "if necessary"               | Decision criteria unclear | Specify when necessary            |
| "etc.," "and so on"          | Scope ambiguous           | List specifically                 |
| "fast," "efficient"          | No numeric criteria       | Describe specific numeric targets (e.g., "response within 2 seconds", "memory usage under 100MB") |
| "flexible," "scalable"       | Definition vague          | Specify concrete extension points (e.g., "supports 10,000 concurrent users", "handles 1M records") |

## Commonly Missing Information

- Error case handling
- Boundary conditions (maximum, minimum values)
- Non-functional requirement numeric targets
- External system integration specifications
- Data persistence and consistency
