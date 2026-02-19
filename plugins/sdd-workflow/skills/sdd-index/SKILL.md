---
description: "Build or rebuild SDD document index"
allowed-tools: [Bash, Read]
---

# SDD Index Builder

## Overview

Scans all documents under `.sdd/` (requirement, specification, task) and builds a SQLite FTS5 full-text search index.

## Prerequisites

- CLI tool must be installed (`sdd-cli` command available)

## Processing Flow

**Phase 1: Shell Script** - Build index using CLI:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/sdd-index/scripts/rebuild-index.sh"
```

**Phase 2: Claude** - Verify and report results:

1. Check if the index build was successful
2. Read index metadata (`.sdd/.cache/index/metadata.json`)
3. Report results to the user:
   - Number of indexed documents
   - Index file path
   - Last update timestamp

## Output Example

```
✓ SDD document index built successfully

- Indexed documents: 15
- Index file: .sdd/.cache/index/index.db
- Last updated: 2026-02-19T12:34:56

You can now use /sdd-search to quickly search documents.
```

## Error Handling

- If CLI tool is unavailable, provide installation instructions
- If SDD directory does not exist, suggest running `/sdd-init`

## Related Skills

- `/sdd-search`: Search using the index
- `/sdd-visualize`: Visualize dependencies
- `/sdd-init`: Initialize SDD workflow
