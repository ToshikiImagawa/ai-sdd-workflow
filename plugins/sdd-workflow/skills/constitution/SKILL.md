---
name: constitution
description: "Define and manage non-negotiable project principles (Constitution) and verify synchronization with other documents"
argument-hint: "<subcommand> [arguments]"
version: 3.1.0
license: MIT
user-invocable: true
disable-model-invocation: true
allowed-tools: Skill
---

# Constitution - Router

## Routing Logic

1. Check `SDD_CLI_AVAILABLE` environment variable
2. If `SDD_CLI_AVAILABLE=true`: invoke skill `constitution-cli` with `$ARGUMENTS`
3. Otherwise: invoke skill `constitution-cli-fallback` with `$ARGUMENTS`
