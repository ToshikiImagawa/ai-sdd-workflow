# Continuous Verification

## Auto-Checks After Each Task

```
1. Run related tests -> Must pass
   |
2. Check spec consistency -> Must match
   |
3. Update tasks.md -> Mark [x]
```

## Spec Consistency Check (automatic)

````markdown
### Spec Consistency Check

| Verification Item               | Status | Notes                       |
|:--------------------------------|:-------|:----------------------------|
| API signatures match spec       | pass   | All public APIs implemented |
| Data models match spec          | pass   | Types align with spec       |
| Behavior matches sequence diagrams | pass | Flow verified               |
| Non-functional requirements met | warn   | Response time needs tuning  |
````

## Progress Update in tasks.md

```diff
### Phase 2: Core Implementation

| # | Task | Description | Completion Criteria | Status |
|:---|:---|:---|:---|:---|
- | 2.1 | User validation | Validate user input | [ ] |
+ | 2.1 | User validation | Validate user input | [x] |
```
