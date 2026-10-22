#!/usr/bin/env bash
# Fixture: row 18: upstream status changed after downstream was approved
set -euo pipefail
mkdir -p .sdd/requirement .sdd/specification
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/requirement/notes.md <<'EOF'
---
id: "prd-notes"
title: "Notes"
type: "prd"
status: "approved"
created: "2026-01-10"
updated: "2026-03-01"
category: "notes"
---

# Notes PRD

## 2. Requirements

| ID | Requirement |
|:--|:--|
| UR_001 | Users can write a note |
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
---

# Notes spec

## 3.1. Functional Requirements

| ID | Requirement |
|:--|:--|
| FR-001 | `add_note(text)` stores a note (UR_001) |
EOF
