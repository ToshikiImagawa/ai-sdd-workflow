#!/usr/bin/env bash
# Fixture: row 13: laws-status proven but LAWS.bend has no approval line
set -euo pipefail
mkdir -p .sdd/laws/notes .sdd/specification
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/specification/notes_spec.md <<'EOF'
---
id: "spec-notes"
title: "Notes spec"
type: "spec"
status: "approved"
sdd-phase: "specify"
created: "2026-01-10"
updated: "2026-01-10"
depends-on: ["prd-notes"]
category: "notes"
laws: ["laws/notes"]
laws-status: "proven"
---

# Notes spec

## 3.1. Functional Requirements

| ID | Requirement |
|:--|:--|
| FR-001 | `add_note(text)` stores a note (UR_001) |
EOF
cat > .sdd/laws/notes/LAWS.bend <<'EOF'
# laws: notes
# spec: spec-notes
import Base

{inv : for n: Nat. n == n}
EOF
