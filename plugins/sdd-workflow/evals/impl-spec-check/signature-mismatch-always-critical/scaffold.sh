#!/usr/bin/env bash
# Fixture: spec impl-status=not-implemented; implementation has a different signature for archive_task
set -euo pipefail
mkdir -p .sdd/specification src
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/specification/task-archive_spec.md <<'EOF'
---
id: "spec-task-archive"
title: "Task archive"
type: "spec"
status: "approved"
sdd-phase: "specify"
impl-status: "not-implemented"
created: "2026-01-10"
updated: "2026-01-10"
---

# Task archive

## 3.1. Functional Requirements

| ID | Requirement | Priority |
|:--|:--|:--|
| FR-001 | `create_task(title: str) -> Task` creates a task | Must |
| FR-002 | `archive_task(task_id: str) -> None` marks a task archived | Must |

## 4. Public API

- `src/tasks.py`: `create_task`, `archive_task`
EOF
cat > src/tasks.py <<'EOF'
from dataclasses import dataclass


@dataclass
class Task:
    id: str
    title: str
    archived: bool = False


def create_task(title: str) -> Task:
    return Task(id=title.lower().replace(" ", "-"), title=title)


def archive_task(task: Task, reason: str = "") -> bool:
    task.archived = True
    return True
EOF
