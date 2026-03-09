---
name: task-breakdown
description: "Break down tasks from technical design document, generating a list of independently testable small tasks"
argument-hint: "<feature-name> [ticket-number]"
version: 3.1.0
license: MIT
user-invocable: true
allowed-tools: Skill
---

# Task Breakdown - Router

## Routing Logic

1. Check `SDD_CLI_AVAILABLE` environment variable
2. If `SDD_CLI_AVAILABLE=true`: invoke skill `task-breakdown-cli` with `$ARGUMENTS`
3. Otherwise: invoke skill `task-breakdown-cli-fallback` with `$ARGUMENTS`
