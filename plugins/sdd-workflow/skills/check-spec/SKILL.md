---
name: check-spec
description: "Check consistency between implementation code and design documents (design), detecting discrepancies"
argument-hint: "[feature-name] [--full]"
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash
---

# Check Spec - Design & Implementation Consistency Check

Verifies consistency between implementation code and design documents (`*_design.md`), detecting discrepancies.

**Role**: This command specializes in **design <-> implementation consistency checking**.
**Document-level consistency** (PRD <-> spec, spec <-> design) is handled by the `spec-reviewer`
agent when called with the `--full` option.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

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
    - CONSTITUTION.md compliance check
    - Completeness, clarity, and SysML compliance check
    - Vague description detection

### Input Examples

```
/check-spec user-auth              # Consistency check only (default)
/check-spec task-management --full # Consistency check + quality review
/check-spec --full                 # Comprehensive check for all specifications
/check-spec                        # Without arguments, targets all specifications (consistency check only)
```

### Scope Confirmation for No-Argument Execution

**When executed without arguments, display the list of target files and ask for user confirmation before starting the process.**

**Reference**: `examples/scope_confirmation.md`

Replace placeholders with actual file names and counts.

**Post-confirmation behavior**:

- User approves -> Execute check on all files
- User cancels or specifies a particular file -> Re-execute with the specified scope

## Processing Flow

**Optimized Execution Flow**:

**Phase 1: Shell Script** - Execute `find-design-docs.sh` to scan design documents:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-design-docs.sh" [feature-name]
```

This script:
1. Finds all design documents (`*_design.md`) in flat or hierarchical structure
2. Finds corresponding spec files (`*_spec.md`)
3. Generates file mapping JSON (design → spec → implementation)
4. Exports environment variables to `$CLAUDE_ENV_FILE`:
   - `CHECK_SPEC_DESIGN_FILES` - List of design files
   - `CHECK_SPEC_SPEC_FILES` - List of spec files
   - `CHECK_SPEC_MAPPING` - JSON mapping file

**Phase 2: Claude** - Read design docs from pre-scanned lists and perform consistency check

### 1. Identify Target Documents

Target design documents (`*_design.md`). Both flat and hierarchical structures are supported.

**For flat structure**:

```
With argument -> Target the following file:
  - ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{argument}_design.md
Without argument -> Target all *_design.md files under ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/ (recursively)
```

**For hierarchical structure** (when argument contains `/`, or when specifying hierarchical path):

```
Argument in "{parent-feature}/{feature-name}" format -> Target the following file:
  - ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md

Argument is "{parent-feature}" only -> Target the following files:
  - ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md (parent feature design)
  - ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/*_design.md (child feature designs)
```

**Naming convention**:

- **Under specification**: `_design` suffix required (`index_design.md`, `{feature-name}_design.md`)

**Hierarchical structure input examples**:

```
/check-spec auth/user-login     # Check user-login feature under auth domain
/check-spec auth                # Check entire auth domain
```

### 2. Load Design Documents

**Extract the following information from `*_design.md`**:

| Item                        | Description                                                                              |
|:----------------------------|:-----------------------------------------------------------------------------------------|
| **Module Structure**        | Directory structure, file organization                                                   |
| **Technology Stack**        | Libraries, frameworks used                                                               |
| **Interface Definitions**   | API signatures (function names, arguments, return values), type definitions, data models |
| **Functional Requirements** | List of features to implement                                                            |
| **Implementation Approach** | Architecture patterns, design decisions                                                  |

### 3. Verify Implementation Code

Search for code corresponding to specification contents:

- Search APIs/functions (using methods appropriate for project language)
- Search type definitions/data models
- Verify module/file existence

### 4. Consistency Check Items

**Note**: This command specializes in **design <-> implementation consistency checking**. **Document-level consistency**
(PRD <-> spec, spec <-> design) and **quality review** (CONSTITUTION.md compliance, completeness, clarity) are handled by
the `spec-reviewer` agent when using the `--full` option.

#### design <-> Implementation Consistency

| Check Target                | Verification Content                               | Importance |
|:----------------------------|:---------------------------------------------------|:-----------|
| **API Signature**           | Do function names, arguments, return values match? | High       |
| **Type Definitions**        | Do interfaces and types match?                     | High       |
| **Module Structure**        | Does directory/file structure match?               | Medium     |
| **Functional Requirements** | Are functions specified in specs implemented?      | High       |
| **Technology Stack**        | Are documented libraries being used?               | Low        |

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

#### Execution Timing

- Executes after design <-> implementation consistency check is complete
- Performs comprehensive review for target documents (PRD, spec, design)
- Generates traceability matrix (PRD -> spec -> design correspondence)

**Note**: Comprehensive review requires additional execution time. For quick checks during development, run without
`--full`, and use `--full` before PR creation or for periodic checks.

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

#### Enhanced Check Items

1. **API Implementation Verification**: Verify functions/classes documented in spec are implemented via symbol search
2. **Signature Match**: Verify function argument/return types match spec
3. **Unused Code Detection**: Detect symbols implemented but not documented in spec
4. **Dependency Understanding**: Analyze reference relationships between modules

#### Additional Output When Using Serena

**Reference**: `examples/serena_symbol_analysis.md`

### Behavior When Serena is Not Configured

Even without Serena, consistency checking is performed using traditional text-based search (Grep/Glob).
Features are limited but work language-agnostically.

## Notes

- If specifications don't exist, recommend creating them with `/generate-spec` first
- If many discrepancies exist, major specification updates may be needed
- If implementation is correct and specs are outdated, update specifications
- If specifications are correct and implementation is wrong, fix implementation
