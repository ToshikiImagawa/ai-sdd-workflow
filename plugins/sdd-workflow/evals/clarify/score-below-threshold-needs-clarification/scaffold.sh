#!/usr/bin/env bash
# Fixture: a spec; the analysis counts are supplied in the prompt
set -euo pipefail
mkdir -p .sdd/specification
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/specification/reminder_spec.md <<'EOF'
---
id: "spec-reminder"
title: "Reminder"
type: "spec"
status: "approved"
sdd-phase: "specify"
created: "2026-01-10"
updated: "2026-01-10"
depends-on: ["prd-notes"]
category: "notes"
---

# Notes spec

## 3.1. Functional Requirements

| ID | Requirement |
|:--|:--|
| FR-001 | `add_note(text)` stores a note (UR_001) |
EOF
