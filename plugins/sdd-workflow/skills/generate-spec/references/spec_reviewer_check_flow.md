# Spec-Reviewer Check Flow

```
1. Call spec-reviewer agent
   |
2. Execute CONSTITUTION.md compliance check
   |
3. If violations detected:
   |- Review fix proposals from spec-reviewer
   |- Apply approved fixes using Edit tool (main agent)
   |- Report non-applicable fixes to user
   |
4. Call front-matter-reviewer agent (pass spec/design file path)
   |- On issue detection: Apply fixes (main agent)
   |
5. After fix, re-check to verify
   |
6. Include check results in output
```
