# Commit Strategy

## Commit Pattern by Phase

| Phase          | Commit Prefix | Example                              |
|:---------------|:--------------|:-------------------------------------|
| Setup          | `chore`       | `chore: setup test infrastructure`   |
| Tests          | `test`        | `test: add user validation tests`    |
| Implementation | `feat`        | `feat: implement user validation`    |
| Refactoring    | `refactor`    | `refactor: extract validation logic` |
| Fix            | `fix`         | `fix: handle null user status`       |
| Documentation  | `docs`        | `docs: update design decisions`      |

## Integration with Other Commands

```
Before: /clarify -> /task-breakdown -> /implement
During: /implement (continuous /check-spec)
After: /implement -> /check-spec -> /task-cleanup -> PR
```

## Implementation Log Items

| Item                           | Content Recorded                           |
|:-------------------------------|:-------------------------------------------|
| **Implementation Decisions**   | Implementation decisions not in design doc |
| **Issues & Solutions**         | Problems encountered and their solutions   |
| **Alternative Considerations** | Alternatives not chosen and reasons        |
| **Technical Discoveries**      | Insights gained during implementation      |
| **Test Results**               | Test execution result records              |

### Log Usage

After implementation complete, integrate important content into `*_design.md` (executed by `/task-cleanup`).
