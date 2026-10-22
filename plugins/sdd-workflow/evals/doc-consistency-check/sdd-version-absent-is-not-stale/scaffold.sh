#!/usr/bin/env bash
# Fixture: three PRDs: sdd-version absent / 4.1.0 / 5.2.0 (installed plugin major is 5)
set -euo pipefail
mkdir -p .sdd/requirement
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/requirement/legacy.md <<'EOF'
---
id: "prd-legacy"
title: "Legacy"
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
cat > .sdd/requirement/old-gen.md <<'EOF'
---
id: "prd-old-gen"
title: "Old generation"
type: "prd"
status: "approved"
created: "2026-01-10"
updated: "2026-01-10"
category: "notes"
sdd-version: "4.1.0"
---

# Notes PRD

## 2. Requirements

| ID | Requirement |
|:--|:--|
| UR_001 | Users can write a note |
EOF
cat > .sdd/requirement/current.md <<'EOF'
---
id: "prd-current"
title: "Current"
type: "prd"
status: "approved"
created: "2026-01-10"
updated: "2026-01-10"
category: "notes"
sdd-version: "5.2.0"
---

# Notes PRD

## 2. Requirements

| ID | Requirement |
|:--|:--|
| UR_001 | Users can write a note |
EOF
