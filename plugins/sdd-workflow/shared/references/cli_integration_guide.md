# CLI Integration Guide

## Overview

The `sdd-cli` command provides structural validation and document discovery for AI-SDD projects.
When `SDD_CLI_AVAILABLE=true`, skills should delegate structural/mechanical checks to the CLI
and focus LLM effort on semantic analysis.

## CLI Commands

### `sdd-cli search`

Search for SDD documents by various criteria.

```bash
# Search documents (optionally filter by --dir and/or --feature-id)
sdd-cli search [--dir specification|requirement] [--feature-id <name>] --format json
```

**Output fields**: `documents[]` array with `path`, `type` (spec|design|prd|task|implementation-log), `id`, `title`, `status`, `depends_on`, `front_matter`. Top-level `total` count.

### `sdd-cli lint`

Validate document structure, front matter, and cross-references.

```bash
# Lint all, specific file, or specific directory
sdd-cli lint [--file path/to/file.md] [--dir specification] --json
```

**Output fields**: `results[]` array with `file`, `valid`, `errors[]` (code/message/line), `warnings[]`, `front_matter` (id/type/status/depends_on), `dependencies` (upstream/downstream). `summary` with total/valid/errors/warnings counts.

## Integration for Skills

1. **CLI for structural validation**: Use `sdd-cli search` and `sdd-cli lint --json` to get document inventory, front matter, and dependency chains
2. **Parse JSON output**: Extract file paths, front matter, dependencies
3. **Focus LLM on semantic analysis**: With structural data from CLI, focus on API signature correctness, terminology consistency, design quality, requirement coverage

## Environment Variable

| Variable | Description |
|:---|:---|
| `SDD_CLI_AVAILABLE` | Set to `"true"` when sdd-cli is installed and configured |

Check availability:

```bash
if [ "$SDD_CLI_AVAILABLE" = "true" ]; then
  # Use CLI commands
else
  # Fallback to Glob/Grep
fi
```
