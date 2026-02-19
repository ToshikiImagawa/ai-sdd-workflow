---
description: "Search SDD documents using index"
argument-hint: "<keyword> [--feature-id <id>] [--tag <tag>] [--dir <requirement|specification|task>]"
allowed-tools: [Bash, Read]
---

# SDD Index Search

## Overview

Performs fast search across indexed SDD documents. Supports keyword search, feature ID, tag, and directory filtering.

## Prerequisites

- `@shared/references/cli_tool_usage.md` - CLI tool usage guide
- Index must be built (run `/sdd-index` to build)

## Arguments

- `<keyword>`: Full-text search keyword (optional, 3+ characters recommended)
- `--feature-id <id>`: Filter by specific feature ID
- `--tag <tag>`: Filter by specific tag
- `--dir <type>`: Filter by directory type (requirement/specification/task)

## Processing Flow

**Phase 1: Shell Script** - Execute search using CLI:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/sdd-search/scripts/search.sh" "$ARGUMENTS"
```

**Phase 2: Claude** - Parse and present results:

1. Read search results JSON from `$SDD_SEARCH_RESULTS`
2. Format results by relevance
3. Present results to user:
   - File path (clickable link format)
   - Title
   - Feature ID
   - Tags
   - Snippet

## Output Example

```
Search results: 2 items

1. User Login Feature
   Path: .sdd/requirement/user-login.md
   Feature ID: user-login
   Tags: authentication, security, UX
   Snippet: Provides secure user login functionality...

2. User Login Specification
   Path: .sdd/specification/user-login_spec.md
   Feature ID: user-login
   Tags: authentication, spec
   Snippet: Defines authentication flow with email and password...
```

## Usage Examples

```bash
# Keyword search
/sdd-search "login feature"

# Search by feature ID
/sdd-search --feature-id user-login

# Search by tag
/sdd-search --tag authentication

# Filter by directory
/sdd-search "authentication" --dir specification

# Combined search
/sdd-search "security" --tag security --dir requirement
```

## Error Handling

- If index does not exist, suggest running `/sdd-index`
- If CLI tool is unavailable, provide installation instructions
- If no results found, suggest relaxing search criteria

## Notes

- **Full-text search limitation**: Current trigram tokenizer works optimally with 3+ character keywords
- For 2-character keywords or less, use Feature ID or tag exact match search

## Related Skills

- `/sdd-index`: Build the index
- `/sdd-visualize`: Visualize dependencies
- `/generate-spec`: Generate specification from search results
