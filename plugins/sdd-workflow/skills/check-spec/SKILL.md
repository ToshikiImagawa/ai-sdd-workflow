---
name: check-spec
description: "Check consistency between implementation code and design documents (design), detecting discrepancies"
argument-hint: "[feature-name] [--full]"
version: 3.1.0
license: MIT
user-invocable: true
allowed-tools: Skill
---

# Check Spec - Router

## Routing Logic

1. Check `SDD_CLI_AVAILABLE` environment variable
2. If `SDD_CLI_AVAILABLE=true`: invoke skill `check-spec-cli` with `$ARGUMENTS`
3. Otherwise: invoke skill `check-spec-cli-fallback` with `$ARGUMENTS`
