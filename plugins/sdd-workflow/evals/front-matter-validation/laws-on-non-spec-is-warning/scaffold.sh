#!/usr/bin/env bash
# Fixture: row 12: laws: on a non-spec document
set -euo pipefail
mkdir -p .sdd/requirement
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
laws: ["laws/notes"]
---

# Notes PRD

## 2. Requirements

| ID | Requirement |
|:--|:--|
| UR_001 | Users can write a note |
EOF
