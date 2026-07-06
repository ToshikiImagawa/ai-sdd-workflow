# Vibe Coding Risk Report (Fallback Format)

Use this structure only when `templates/${SDD_LANG:-en}/risk_report.md` does not exist:

```markdown
# Vibe Coding Risk Report

**Detection Date**: {YYYY-MM-DD}
**Risk Level**: 🔴 High / 🟡 Medium / 🟢 Low

## Detected Issues

- {Issue description with specific examples from user input}
- {Issue description...}

## Missing Information

- {What information is unclear or missing}
- {What assumptions would need to be made}

## Recommended Actions

1. {Specific action to clarify requirements}
2. {Specific action...}

## Risks if Proceeding Without Clarification

- Risk of re-implementation due to misunderstood requirements
- Risk of bug introduction from unhandled edge cases
- Risk of technical debt accumulation
```
