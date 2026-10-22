#!/usr/bin/env bash
# Fixture: row 15: sdd-version not semver or older major
set -euo pipefail
mkdir -p .sdd/specification
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
sdd-version: "v5"
---

# Notes spec

## 3.1. Functional Requirements

| ID | Requirement |
|:--|:--|
| FR-001 | `add_note(text)` stores a note (UR_001) |
EOF
