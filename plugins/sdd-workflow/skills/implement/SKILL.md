---
name: implement
description: "Execute TDD-based implementation and progressively complete checklist in tasks.md"
argument-hint: "<feature-name> [ticket-number]"
version: 3.1.0
license: MIT
user-invocable: true
allowed-tools: Skill
---

# Implement - Router

## Routing Logic

1. Check `SDD_CLI_AVAILABLE` environment variable
2. If `SDD_CLI_AVAILABLE=true`: invoke skill `implement-cli` with `$ARGUMENTS`
3. Otherwise: invoke skill `implement-cli-fallback` with `$ARGUMENTS`
