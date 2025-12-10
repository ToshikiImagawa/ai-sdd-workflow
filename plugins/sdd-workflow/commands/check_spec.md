---
description: "Check consistency between implementation code and specifications, detecting discrepancies"
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Check Spec - Specification Consistency Check

Verifies consistency between implementation code and specifications (`*_spec.md`, `*_design.md`), detecting
discrepancies.

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for consistency checking.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value         | Description                  |
|:-------------------------|:----------------------|:-----------------------------|
| `SDD_ROOT`          | `.sdd`                | Root directory               |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`    | PRD/Requirements directory   |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification`  | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`           | Task log directory           |

**Path Resolution Priority:**
1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or configuration file exists.

### Document Dependencies (Reference)

```
Implementation → *_design.md → *_spec.md → requirement/
```

## Input

$ARGUMENTS

### Input Examples

```
/check_spec user-auth
/check_spec task-management
/check_spec  # Without arguments, targets all specifications
```

## Processing Flow

### 1. Identify Target Documents

Both flat and hierarchical structures are supported.

**For flat structure**:

```
With argument → Target the following files:
  - .sdd/requirement/{argument}.md (PRD, if exists)
  - .sdd/specification/{argument}_spec.md
  - .sdd/specification/{argument}_design.md
Without argument → Target all files under .sdd/specification/ (recursively)
```

**For hierarchical structure** (when argument contains `/`, or when specifying hierarchical path):

```
Argument in "{parent-feature}/{feature-name}" format → Target the following files:
  - .sdd/requirement/{parent-feature}/{feature-name}.md (PRD)
  - .sdd/specification/{parent-feature}/{feature-name}_spec.md
  - .sdd/specification/{parent-feature}/{feature-name}_design.md

Argument is "{parent-feature}" only → Target the following files:
  - .sdd/requirement/{parent-feature}/index.md (parent feature PRD)
  - .sdd/requirement/{parent-feature}/*.md (child feature PRDs)
  - .sdd/specification/{parent-feature}/index_spec.md (parent feature spec)
  - .sdd/specification/{parent-feature}/*_spec.md (child feature specs)
  - .sdd/specification/{parent-feature}/index_design.md (parent feature design)
  - .sdd/specification/{parent-feature}/*_design.md (child feature designs)
```

**⚠️ Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

**Hierarchical structure input examples**:

```
/check_spec auth/user-login     # Check user-login feature under auth domain
/check_spec auth                # Check entire auth domain
```

### 2. Load Documents

Extract the following information from target documents:

**From PRD (`requirement/*.md`)** (if exists):

| Item                            | Description                         |
|:--------------------------------|:------------------------------------|
| **Requirement IDs**             | UR-xxx, FR-xxx, NFR-xxx             |
| **Functional Requirements**     | Functions the system should provide |
| **Non-Functional Requirements** | Performance, security, etc.         |

**From `*_spec.md`**:

| Item                        | Description                             |
|:----------------------------|:----------------------------------------|
| **Public API**              | Function names, arguments, return types |
| **Data Model**              | Type definitions, interfaces            |
| **Functional Requirements** | List of functions to implement          |
| **PRD Reference**           | Referenced requirement IDs              |

**From `*_design.md`**:

| Item                      | Description                            |
|:--------------------------|:---------------------------------------|
| **Module Structure**      | Directory structure, file organization |
| **Technology Stack**      | Libraries, frameworks used             |
| **Interface Definitions** | Interface definitions for each layer   |

### 3. Verify Implementation Code

Search for code corresponding to specification contents:

- Search APIs/functions (using methods appropriate for project language)
- Search type definitions/data models
- Verify module/file existence

### 4. Consistency Check Items

#### PRD ↔ spec Consistency (if PRD exists)

| Check Target                              | Verification Content                                   | Importance |
|:------------------------------------------|:-------------------------------------------------------|:-----------|
| **Requirement ID Mapping**                | Are PRD requirement IDs referenced in spec?            | High       |
| **Functional Requirement Coverage**       | Are PRD functional requirements covered in spec?       | High       |
| **Non-Functional Requirement Reflection** | Are PRD non-functional requirements reflected in spec? | Medium     |
| **Terminology Consistency**               | Is same terminology used in PRD and spec?              | Low        |

#### spec ↔ design Consistency

| Check Target                 | Verification Content                       | Importance |
|:-----------------------------|:-------------------------------------------|:-----------|
| **API Definition Match**     | Is spec API detailed in design?            | High       |
| **Type Definition Match**    | Do spec type definitions match design?     | High       |
| **Constraint Consideration** | Are spec constraints considered in design? | Medium     |

#### design ↔ Implementation Consistency

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

## Output Format

```markdown
## Specification Consistency Check Results

### Target Documents

- `.sdd/requirement/[{parent-feature}/]{feature-name}.md` (PRD, if exists)
- `.sdd/specification/[{parent-feature}/]{feature-name}_spec.md`
- `.sdd/specification/[{parent-feature}/]{feature-name}_design.md`

※ For hierarchical structure, parent feature uses `index.md`, `index_spec.md`, `index_design.md`

### Check Results Summary

| Check Target | Result | Count |
|:---|:---|:---|
| PRD ↔ spec | Consistent / Inconsistent | {n} items |
| spec ↔ design | Consistent / Inconsistent | {n} items |
| design ↔ Implementation | Consistent / Inconsistent | {n} items |

### PRD ↔ spec Consistency (if PRD exists)

| Requirement ID | PRD Requirement Content | Spec Mapping | Status |
|:---|:---|:---|:---|
| FR-001 | {Requirement content} | {Corresponding functional requirement} | Consistent / Not Mapped |
| FR-002 | {Requirement content} | Not documented | Not Mapped |

### Critical (Immediate Action Required)

#### 1. {Discrepancy Title}

**Specification States**:

```

// From *_spec.md
doSomething(arg: string): Result

```

**Implementation Code**:

```

// From implementation file
doSomething(arg: number): Result // Argument type differs

```

**Recommended Actions**:

- [ ] Update specification (if implementation is correct)
- [ ] Fix implementation (if specification is correct)

---

### Warning (Action Recommended)

#### 1. {Discrepancy Title}

**Content**: {Discrepancy details}

**Recommended Action**: {How to address}

---

### Info (Reference)

- {Info 1}
- {Info 2}

---

### Unimplemented Features

Features documented in specifications but implementation not confirmed:

| Feature | Specification Location | Status |
|:---|:---|:---|
| {Feature name} | {Section} in `*_spec.md` | Not Implemented |

### Undocumented Implementations

Features implemented but not documented in specifications:

| Implementation | File | Recommended Action |
|:---|:---|:---|
| {Function/class name} | `{file path}` | Add to spec / Remove if unnecessary |

### Recommended Actions

1. Resolve **Critical** discrepancies first
2. Decide whether to modify specification or implementation
3. After modifications, run `/check_spec` again to verify

```

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

```markdown
### Serena Symbol Analysis Results

| Symbol | In Spec | Implementation Status | Reference Count |
|:---|:---|:---|:---|
| `createUser` | Yes | Implemented | 5 |
| `deleteUser` | Yes | Not Implemented | 0 |
| `internalHelper` | No | Implemented | 3 |
```

### Behavior When Serena is Not Configured

Even without Serena, consistency checking is performed using traditional text-based search (Grep/Glob).
Features are limited but work language-agnostically.

## Notes

- If specifications don't exist, recommend creating them with `/generate_spec` first
- If many discrepancies exist, major specification updates may be needed
- If implementation is correct and specs are outdated, update specifications
- If specifications are correct and implementation is wrong, fix implementation
