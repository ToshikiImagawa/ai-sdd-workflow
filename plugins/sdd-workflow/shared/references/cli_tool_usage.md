# CLI Tool Usage

## Overview

`sdd-cli` is a Python CLI tool for advanced document management in the AI-SDD workflow. It provides the following features:

1. **Indexing**: Build SQLite FTS5 full-text search index for documents under `.sdd/`
2. **Full-text Search**: Fast keyword, feature ID, and tag-based search
3. **Dependency Visualization**: Generate Mermaid diagrams showing document dependencies

## Installation

The CLI tool is automatically installed when a session starts. To install manually:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/cli
uv pip install -e .
```

## Command Reference

### sdd-cli index

Build document index.

**Syntax**:
```bash
sdd-cli index [--root <path>] [--quiet]
```

**Options**:
- `--root <path>`: SDD root directory (default: `$SDD_ROOT` or `.sdd`)
- `--quiet`: Suppress output messages

**Examples**:
```bash
sdd-cli index --root .sdd
sdd-cli index --quiet
```

### sdd-cli search

Search documents.

**Syntax**:
```bash
sdd-cli search [<query>] [options]
```

**Arguments**:
- `<query>`: Full-text search query (optional, 3+ characters recommended)

**Options**:
- `--root <path>`: SDD root directory
- `--feature-id <id>`: Filter by feature ID
- `--tag <tag>`: Filter by tag
- `--dir <type>`: Filter by directory type (requirement/specification/task)
- `--format <format>`: Output format (text/json, default: text)
- `--output <file>`: Output file path (default: stdout)
- `--limit <n>`: Maximum number of results (default: 10)

**Examples**:
```bash
# Keyword search
sdd-cli search "login feature"

# Search by feature ID
sdd-cli search --feature-id user-login

# Search by tag
sdd-cli search --tag authentication

# Combined search
sdd-cli search "security" --tag security --dir specification

# JSON output
sdd-cli search "login" --format json --output results.json
```

### sdd-cli visualize

Generate dependency graph visualization.

**Syntax**:
```bash
sdd-cli visualize [options]
```

**Options**:
- `--root <path>`: SDD root directory
- `--output <file>`: Output file path (default: `~/.cache/sdd-cli/{project-name}.{hash}/dependency-graph.mmd`)
- `--filter-dir <type>`: Filter by directory type (requirement/specification/task)
- `--feature-id <id>`: Filter by feature ID

**Examples**:
```bash
# Visualize all dependencies
sdd-cli visualize

# Visualize requirement only
sdd-cli visualize --filter-dir requirement

# Visualize specific feature
sdd-cli visualize --feature-id user-login --output user-login-deps.mmd
```

## Search Limitations

### Trigram Tokenizer Constraints

The current implementation uses SQLite FTS5 with a trigram tokenizer. This has the following limitations:

- **3+ character keywords**: Full-text search works optimally with keywords of 3 or more characters
- **2 or fewer character keywords**: For short keywords, use exact match search with Feature ID or tags

**Examples**:
```bash
# ❌ 2-character keyword (incomplete search results)
sdd-cli search "auth"

# ✅ Search by feature ID (exact match)
sdd-cli search --feature-id user-auth

# ✅ Search by tag (exact match)
sdd-cli search --tag auth

# ✅ 3+ character keyword (works well)
sdd-cli search "authentication"
```

## Cache Directory Structure

Index and visualization files are stored in **XDG Base Directory** compliant cache:

```
~/.cache/sdd-cli/
├── my-project.a1b2c3d4/
│   ├── index.db                  # SQLite FTS5 index
│   ├── metadata.json             # Index metadata
│   ├── dependency-graph.mmd      # Mermaid dependency graph
│   └── search-results.json       # Search results (from skills)
└── another-project.e5f6g7h8/
    └── ...
```

**Naming Convention** (GitHub Copilot-style):
- Format: `{project-name}.{8-char-hash}`
- `project-name`: Project directory name (human-readable)
- `8-char-hash`: Short hash to avoid path collisions

**Benefits**:
- Easy to identify projects at a glance
- Simple cleanup: `rm -rf ~/.cache/sdd-cli/old-project.*`
- Claude Code independent - works with any editor or CI/CD
- Persistent across sessions (survives system restart)

## Cache Management

### List Cached Projects

```bash
# List all cached projects
sdd-cli cache list

# Output:
# Found 2 cached project(s)
# Total cache size: 2.5 MB
#
# 1. my-project.a1b2c3d4
#    Size: 1.5 MB
#    Documents: 50
#    Last modified: 2026-02-19T14:30:00
#    Project root: /path/to/my-project

# JSON format
sdd-cli cache list --format json
```

### Clean Up Cache

```bash
# Dry-run: show what would be deleted
sdd-cli cache clean --project 'old-*' --dry-run

# Delete specific project
sdd-cli cache clean --project slide-presentation-app

# Delete projects matching pattern (supports wildcards)
sdd-cli cache clean --project 'test-*'

# Delete all cached projects
sdd-cli cache clean --all

# Dry-run for all projects
sdd-cli cache clean --all --dry-run
```

**When to Clean Cache**:
- Project deleted from disk → remove corresponding cache
- Running low on disk space → clean old/unused project caches
- Index corrupted → delete cache and rebuild with `sdd-cli index`

## Troubleshooting

### CLI not found

**Symptom**:
```
Error: sdd-cli not found.
```

**Solution**:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/cli
uv pip install -e .
```

### Index not found

**Symptom**:
```
Error: Index not found.
```

**Solution**:
```bash
sdd-cli index --root .sdd
```

Or in Claude Code:
```
/sdd-index
```

### No search results

**Causes and solutions**:
1. **Stale index**: Rebuild index with `/sdd-index`
2. **Short keyword**: Use 3+ character keywords
3. **Too strict filters**: Relax filter conditions

## Related Documentation

- `@shared/references/mermaid_notation_rules.md` - Mermaid notation rules
- `@shared/references/document_dependencies.md` - Document dependencies
- `@shared/references/prerequisites_directory_paths.md` - Directory paths
