---
name: doc-consistency-checker
description: "Automatically executed during document updates or before implementation to check consistency between PRD ↔ *_spec.md ↔ *_design.md. Detects missing requirement ID (UR/FR/NFR) references, data model mismatches, API definition discrepancies, terminology inconsistencies, and ensures traceability between documents."
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Skill
---

# Doc Consistency Checker - Router

## Routing Logic

1. Check `SDD_CLI_AVAILABLE` environment variable
2. If `SDD_CLI_AVAILABLE=true`: invoke skill `doc-consistency-checker-cli` with `$ARGUMENTS`
3. Otherwise: invoke skill `doc-consistency-checker-cli-fallback` with `$ARGUMENTS`
