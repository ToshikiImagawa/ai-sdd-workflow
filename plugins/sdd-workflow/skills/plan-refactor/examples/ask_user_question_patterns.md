# AskUserQuestion Patterns for Context Edge Cases

## Ambiguous Context

If context is unclear or too vague (e.g., "improve it", "make it better"), use `AskUserQuestion` to clarify:

```
Question: "What specific aspect do you want to improve?"
Options:
- Performance (e.g., speed, memory usage)
- Maintainability (e.g., code structure, readability)
- Testability (e.g., unit test coverage, mockability)
- Scalability (e.g., handle more users, larger datasets)
```

## Conflicting Requirements

If context includes conflicting goals (e.g., "maximize performance and minimize code complexity"), use
`AskUserQuestion` to prioritize:

```
Question: "These goals may conflict. Which is more important?"
Options:
- Prioritize performance (may increase complexity)
- Prioritize simplicity (may sacrifice some performance)
- Balance both (moderate improvements to each)
```

Document the prioritization in "Purpose and Background".
