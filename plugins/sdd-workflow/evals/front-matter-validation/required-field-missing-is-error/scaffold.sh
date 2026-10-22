#!/usr/bin/env bash
# Fixture: row 1: missing required field
set -euo pipefail
mkdir -p .sdd/requirement
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/requirement/notes.md <<'EOF'
---
id: "prd-notes"
title: "Notes"
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
