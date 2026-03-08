---
name: check-spec-cli
description: "Check consistency between implementation code and design documents (design), detecting discrepancies - CLI-enhanced version"
argument-hint: "[feature-name] [--full]"
version: 3.1.0
license: MIT
user-invocable: false
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash
---

# Check Spec (CLI) - Design & Implementation Consistency Check

CLI-enhanced version: Uses `sdd-cli` for structural validation and document discovery,
focusing LLM effort on semantic analysis.

**Role**: This command specializes in **design <-> implementation consistency checking**.
**Document-level consistency** (PRD <-> spec, spec <-> design) is handled by the `spec-reviewer`
agent when called with the `--full` option.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables
- `references/cli_integration_guide.md` - CLI command reference and integration patterns
- `references/cli_error_handling.md` - Error handling and fallback strategies

### Document Dependencies

See `references/document_dependencies.md` for the document dependency chain and direction meaning.

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

| Argument       | Required | Description                                                                                                  |
|:---------------|:---------|:-------------------------------------------------------------------------------------------------------------|
| `feature-name` | -        | Target feature name or path (e.g., `user-auth`, `auth/user-login`). If omitted, all design docs are targeted |

### Options

- `--full`: In addition to consistency checking, also runs quality review by the `spec-reviewer` agent

### Input Examples

```
user-auth              # Consistency check only (default)
task-management --full # Consistency check + quality review
--full                 # Comprehensive check for all specifications
                       # Without arguments, targets all specifications (consistency check only)
```

### Scope Confirmation for No-Argument Execution

**When executed without arguments, display the list of target files and ask for user confirmation before starting the process.**

**Reference**: `examples/scope_confirmation.md`

## Processing Flow

### Phase 1: CLI - Document Discovery & Structural Validation

Use `sdd-cli` to discover design documents and validate structure:

```bash
# Get all design documents
sdd-cli search --dir specification --format json
```

If `feature-name` is specified:

```bash
# Get documents for specific feature
sdd-cli search --feature-id <feature-name> --format json
```

Then validate structure:

```bash
# Structural validation of discovered documents
sdd-cli lint --json
```

**From CLI output, extract:**

1. List of design documents (`*_design.md`) with paths
2. Corresponding spec files (`*_spec.md`) via `depends_on` chain
3. Front matter data (id, type, status, depends_on)
4. Structural validation errors/warnings

**Error Handling**: If CLI commands fail, fall back to the shell script approach:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/check-spec-cli/scripts/find-design-docs.sh" [feature-name]
```

### Phase 2: LLM - Semantic Consistency Analysis

With structural data from CLI, focus on semantic analysis:

#### 1. Load Design Documents

Read design documents identified by CLI. Extract:

| Item                        | Description                                                              |
|:----------------------------|:-------------------------------------------------------------------------|
| **Module Structure**        | Directory structure, file organization                                   |
| **Technology Stack**        | Libraries, frameworks used                                               |
| **Interface Definitions**   | API signatures (function names, arguments, return values), type definitions, data models |
| **Functional Requirements** | List of features to implement                                            |
| **Implementation Approach** | Architecture patterns, design decisions                                  |

#### 2. Verify Implementation Code

Search for code corresponding to specification contents:

- Search APIs/functions (using methods appropriate for project language)
- Search type definitions/data models
- Verify module/file existence

#### 3. Semantic Consistency Check

**Note**: Structural validation (front matter, file naming, dependency chain) is already done by CLI in Phase 1.
Focus LLM analysis on semantic aspects:

| Check Target                | Verification Content                               | Importance |
|:----------------------------|:---------------------------------------------------|:-----------|
| **API Signature**           | Do function names, arguments, return values match? | High       |
| **Type Definitions**        | Do interfaces and types match?                     | High       |
| **Module Structure**        | Does directory/file structure match?               | Medium     |
| **Functional Requirements** | Are functions specified in specs implemented?      | High       |
| **Technology Stack**        | Are documented libraries being used?               | Low        |

#### 4. Integrate CLI Structural Results

Merge CLI lint results (structural errors/warnings) with LLM semantic analysis results:

- CLI structural errors -> Report as structural issues
- LLM semantic findings -> Report as semantic issues
- Combined report provides comprehensive coverage

### 5. Discrepancy Classification

Classify detected discrepancies as follows:

**Critical (Immediate Action Required)**:

- API signature mismatch (arguments, return value types)
- Functions specified in specs not implemented
- Type definition mismatch

**Warning (Action Recommended)**:

- Module structure mismatch
- Classes/functions existing but not in documentation
- Naming convention mismatch
- CLI structural validation warnings

**Info (Reference)**:

- Minor technology stack differences
- Missing comments/documentation

### 6. Comprehensive Review (--full option only)

When the `--full` option is specified, the `spec-reviewer` agent is invoked to perform comprehensive review.

#### Review Content

| Check Item                      | Description                                                              |
|:--------------------------------|:-------------------------------------------------------------------------|
| **PRD <-> spec Traceability**   | Verify PRD requirements are covered in spec (80% coverage threshold)     |
| **spec <-> design Consistency** | Verify spec content is properly detailed in design                       |
| **CONSTITUTION.md Compliance**  | Verify compliance with project principles                                |
| **Completeness**                | Verify required sections (purpose, API, constraints, etc.) are present   |
| **Clarity**                     | Detect vague descriptions ("nice to have", "appropriately", etc.)        |
| **SysML Compliance**            | Verify requirement ID format (UR/FR/NFR-xxx) and traceability are proper |

## Output

Use the `templates/${SDD_LANG:-en}/check_spec_output.md` template for output formatting.

## Check Execution Timing

| Timing                           | Recommended Action                         |
|:---------------------------------|:-------------------------------------------|
| **Before Implementation Start**  | Verify specification existence and content |
| **At Implementation Completion** | Verify consistency with specifications     |
| **Before PR Creation**           | Run as final verification                  |
| **Periodic Check**               | Prevent documentation obsolescence         |

## Serena MCP Integration (Optional)

If Serena MCP is enabled, high-precision consistency checking through semantic code analysis is possible.

### Usage Conditions

- `serena` is configured in `.mcp.json`
- Target language's Language Server is supported (30+ languages supported)

### Additional Features When Serena is Enabled

#### Symbol-Based Consistency Check

| Feature                    | Description                                                             |
|:---------------------------|:------------------------------------------------------------------------|
| `find_symbol`              | Search implementation code for APIs/functions documented in spec        |
| `find_referencing_symbols` | Understand usage locations of specific symbols to identify impact scope |

**Reference**: `examples/serena_symbol_analysis.md`

### Behavior When Serena is Not Configured

Even without Serena, consistency checking is performed using traditional text-based search (Grep/Glob).

## Notes

- If specifications don't exist, recommend creating them with `/generate-spec` first
- If many discrepancies exist, major specification updates may be needed
- If implementation is correct and specs are outdated, update specifications
- If specifications are correct and implementation is wrong, fix implementation
