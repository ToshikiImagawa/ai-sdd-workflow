#!/usr/bin/env bash
# Fixture: row 8: orphan laws directory under --cross-ref
set -euo pipefail
mkdir -p .sdd/laws/notes .sdd/requirement .sdd/specification
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
updated: "2026-01-10"
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
cat > .sdd/laws/notes/LAWS.bend <<'EOF'
# laws: notes
# spec: spec-notes
# approved: 2026-01-12 @owner sha256:000000000000
import Base

{inv : for n: Nat. n == n}
EOF
