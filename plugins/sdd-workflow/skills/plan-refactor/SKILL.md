---
name: plan-refactor
description: "Plan refactoring for existing features. Analyzes current implementation and creates/updates design documents with refactoring plan."
argument-hint: "<feature-name> [context] [--scope=<dir>] [--ci]"
version: 1.1.0
license: MIT
user-invocable: true
allowed-tools: Skill
---

# Plan Refactoring - Router

## Routing Logic

1. Check `SDD_CLI_AVAILABLE` environment variable
2. If `SDD_CLI_AVAILABLE=true`: invoke skill `plan-refactor-cli` with `$ARGUMENTS`
3. Otherwise: invoke skill `plan-refactor-cli-fallback` with `$ARGUMENTS`
