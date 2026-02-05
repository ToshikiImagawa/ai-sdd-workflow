# Phase Execution Order

```
Phase 1: Foundation (Setup)
   |
Phase 2: Core (TDD Loop)
   |
Phase 3: Integration
   |
Phase 4: Testing
   |
Phase 5: Finishing (Polish)
```

## Determine Starting Phase

```
- All Phase 1 tasks complete -> Start from Phase 2
- All Phase 2 tasks complete -> Start from Phase 3
- And so on...
```

**When --phase option specified**: Force start from specified phase

## Execute Per Phase

````
For each phase:

1. Display task list for the phase
2. Execute each task in order
   a. Check task details
   b. Refer to design/spec docs for implementation
   c. Follow TDD approach
   d. Mark [x] in tasks.md after completion
3. Run tests after phase completion
4. Move to next phase if all tests pass
````
