#!/usr/bin/env bash
# Fixture: PRD with UR_001 and NFR_001 but an empty FR table
set -euo pipefail
mkdir -p .sdd/requirement
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/requirement/task-management.md <<'EOF'
---
id: "prd-task-management"
title: "Task management"
type: "prd"
status: "approved"
created: "2026-01-10"
updated: "2026-01-10"
category: "task-management"
---

# Task management PRD

## 1. Overview

Users manage personal tasks.

## 2. User Requirements

| ID | Requirement | Priority |
|:--|:--|:--|
| UR_001 | Users can keep a list of tasks | Must |

## 3. Functional Requirements

| ID | Requirement | Priority | Traces to |
|:--|:--|:--|:--|

## 4. Non-Functional Requirements

| ID | Requirement | Priority |
|:--|:--|:--|
| NFR_001 | The list renders within 200 ms | Should |
EOF
