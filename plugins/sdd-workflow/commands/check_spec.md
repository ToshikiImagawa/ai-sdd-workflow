---
description: "Check consistency between implementation code and design documents (design), detecting discrepancies"
allowed-tools: Read, Glob, Grep, AskUserQuestion, Task
---

# Check Spec - Design & Implementation Consistency Check

Verifies consistency between implementation code and design documents (`*_design.md`), detecting discrepancies.

**Role**: This command specializes in **design ↔ implementation consistency checking**.
**Document-level consistency** (PRD ↔ spec, spec ↔ design) is handled by the `spec-reviewer`
agent when called with the `--full` option.

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This command follows the sdd-workflow agent principles for consistency checking.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value        | Description                    |
|:-------------------------|:---------------------|:-------------------------------|
| `SDD_ROOT`               | `.sdd`               | Root directory                 |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | PRD/Requirements directory     |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`          | Task log directory             |

**Path Resolution Priority:**

1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

The following documentation uses default values, but replace with custom values if environment variables or
configuration file exists.

### Document Dependencies (Reference)

```
Implementation → task/ → *_design.md → *_spec.md → requirement/ → CONSTITUTION.md
```

## Input

$ARGUMENTS

### Options

- `--full`: In addition to consistency checking, also runs quality review by the `spec-reviewer` agent
  - CONSTITUTION.md compliance check
  - Completeness, clarity, and SysML compliance check
  - Vague description detection

### Input Examples

```
/check_spec user-auth              # Consistency check only (default)
/check_spec task-management --full # Consistency check + quality review
/check_spec --full                 # Comprehensive check for all specifications
/check_spec                        # Without arguments, targets all specifications (consistency check only)
```

## Processing Flow

### 1. Identify Target Documents

Target design documents (`*_design.md`). Both flat and hierarchical structures are supported.

**For flat structure**:

```
With argument → Target the following file:
  - .sdd/specification/{argument}_design.md
Without argument → Target all *_design.md files under .sdd/specification/ (recursively)
```

**For hierarchical structure** (when argument contains `/`, or when specifying hierarchical path):

```
Argument in "{parent-feature}/{feature-name}" format → Target the following file:
  - .sdd/specification/{parent-feature}/{feature-name}_design.md

Argument is "{parent-feature}" only → Target the following files:
  - .sdd/specification/{parent-feature}/index_design.md (parent feature design)
  - .sdd/specification/{parent-feature}/*_design.md (child feature designs)
```

**⚠️ Naming convention**:

- **Under specification**: `_design` suffix required (`index_design.md`, `{feature-name}_design.md`)

**Hierarchical structure input examples**:

```
/check_spec auth/user-login     # Check user-login feature under auth domain
/check_spec auth                # Check entire auth domain
```

### 2. Load Design Documents

**Extract the following information from `*_design.md`**:

| Item                      | Description                                                                |
|:--------------------------|:---------------------------------------------------------------------------|
| **Module Structure**      | Directory structure, file organization                                     |
| **Technology Stack**      | Libraries, frameworks used                                                 |
| **Interface Definitions** | API signatures (function names, arguments, return values), type definitions, data models |
| **Functional Requirements** | List of features to implement                                            |
| **Implementation Approach** | Architecture patterns, design decisions                                  |

### 3. Verify Implementation Code

Search for code corresponding to specification contents:

- Search APIs/functions (using methods appropriate for project language)
- Search type definitions/data models
- Verify module/file existence

### 4. Consistency Check Items

**Note**: This command specializes in **design ↔ implementation consistency checking**. **Document-level consistency**
(PRD ↔ spec, spec ↔ design) and **quality review** (CONSTITUTION.md compliance, completeness, clarity) are handled by
the `spec-reviewer` agent when using the `--full` option.

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

### 6. Comprehensive Review (--full option only)

When the `--full` option is specified, the `spec-reviewer` agent is invoked to perform comprehensive review.

#### Review Content

| Check Item                         | Description                                                                    |
|:-----------------------------------|:-------------------------------------------------------------------------------|
| **PRD ↔ spec Traceability**        | Verify PRD requirements are covered in spec (80% coverage threshold)           |
| **spec ↔ design Consistency**      | Verify spec content is properly detailed in design                             |
| **CONSTITUTION.md Compliance**     | Verify compliance with project principles                                      |
| **Completeness**                   | Verify required sections (purpose, API, constraints, etc.) are present         |
| **Clarity**                        | Detect vague descriptions ("nice to have", "appropriately", etc.)              |
| **SysML Compliance**               | Verify requirement ID format (UR/FR/NFR-xxx) and traceability are proper       |

#### Execution Timing

- Executes after design ↔ implementation consistency check is complete
- Performs comprehensive review for target documents (PRD, spec, design)
- Generates traceability matrix (PRD → spec → design correspondence)

**Note**: Comprehensive review requires additional execution time. For quick checks during development, run without `--full`, and use `--full` before PR creation or for periodic checks.

## Output Format

````markdown
## Design & Implementation Consistency Check Results

### Target Documents

- `.sdd/specification/[{parent-feature}/]{feature-name}_design.md`

※ For hierarchical structure, parent feature uses `index_design.md`

### Check Results Summary

**design ↔ Implementation Consistency Check**:

| Check Target                | Result                          | Count     |
|:----------------------------|:--------------------------------|:----------|
| design ↔ Implementation     | 🟢 Consistent / 🔴 Inconsistent | {n} items |

**Document-level Consistency & Quality Review** (`--full` option only):

Comprehensive review results from `spec-reviewer` agent displayed below.

| Aspect                      | Result                          | Count     |
|:----------------------------|:--------------------------------|:----------|
| PRD ↔ spec Traceability     | 🟢 Consistent / 🔴 Inconsistent | {n} items |
| spec ↔ design Consistency   | 🟢 Consistent / 🔴 Inconsistent | {n} items |
| CONSTITUTION.md Compliance  | 🟢 Compliant / 🔴 Violation     | {n} items |
| Completeness                | ✅ Good / ⚠️ Needs Improvement  | {n} items |
| Clarity                     | ✅ Good / ⚠️ Needs Improvement  | {n} items |

### 🔴 Critical (Immediate Action Required)

| Requirement ID | PRD Requirement Content | Spec Mapping | Status |
|:---|:---|:---|:---|
| UR-001 | {User requirement content} | {Corresponding user story} | 🟢 Covered / 🟡 Partially Covered |
| FR-001 | {Functional requirement content} | {Corresponding functional requirement/API} | 🟢 Covered |
| FR-002 | {Functional requirement content} | Not documented | 🔴 Not Covered |
| NFR-001 | {Non-functional requirement content} | {Corresponding constraint/quality requirement} | 🟢 Covered |
| NFR-002 | {Non-functional requirement content} | Partially documented | 🟡 Partially Covered |

**Coverage: {X}% ({Covered+Partially Covered}/{Total Requirements})**

⚠️ Warning: Coverage is below 80% (displayed only when coverage is below 80%)

**Criteria**:
- 🟢 **Covered**: PRD requirement is clearly documented in spec with defined implementation approach
- 🟡 **Partially Covered**: Related description exists in spec but doesn't fully cover the requirement
- 🔴 **Not Covered**: No corresponding description found in spec

#### PRD ↔ spec Inconsistency Details

##### 🔴 Not Covered Requirements ({n} items)

###### FR-002: {Functional Requirement Title}

**PRD States**:
```
{Detailed requirement content from PRD}
```

**Spec Status**:
- No corresponding functional requirement documented
- No related API definition found

**Recommended Actions**:
1. [ ] Add functional requirement to spec and clarify implementation approach
2. [ ] Add API design if necessary
3. [ ] Verify if PRD requirement is still valid (remove if obsolete)

---

##### 🟡 Partially Covered Requirements ({n} items)

###### NFR-002: {Non-Functional Requirement Title}

**PRD States**:
```
{Detailed requirement content from PRD}
Example: Response time must be within 2 seconds at 95th percentile
```

**Spec States**:
```
{Related content in spec}
Example: Design considering performance
```

**Missing Points**:
- Specific numerical targets (95th percentile, 2 seconds) not documented
- Performance measurement method not defined

**Recommended Actions**:
1. [ ] Add specific numerical targets to spec's constraints section
2. [ ] Add performance measurement/verification method to design document
3. [ ] Add monitoring requirements if necessary

---

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

---

### Quality Review Results (--full option only)

#### Specification Quality Score

| Document                              | CONSTITUTION Compliance | Completeness | Clarity | SysML Compliance | Overall Rating    |
|:--------------------------------------|:------------------------|:-------------|:--------|:-----------------|:------------------|
| `.sdd/specification/{feature}_spec.md` | 🟢 Compliant / 🔴 Violation | ✅ / ⚠️       | ✅ / ⚠️  | ✅ / ⚠️           | 🟢 Good / 🟡 Needs Improvement |
| `.sdd/specification/{feature}_design.md` | 🟢 Compliant / 🔴 Violation | ✅ / ⚠️       | ✅ / ⚠️  | -                | 🟢 Good / 🟡 Needs Improvement |

#### Detected Issues

##### 🔴 CONSTITUTION.md Violations ({n} items)

- **Violation**: {Content violating project principles}
- **Location**: `{filename}` section {section}
- **Recommended Fix**: {How to fix}

##### 🟡 Completeness Issues ({n} items)

- **Missing Section**: {Required section name}
- **Target File**: `{filename}`
- **Recommended Action**: Add section and document {content}

##### 🟡 Vague Descriptions ({n} items)

- **Vague Expression**: "{Detected vague expression}"
- **Location**: `{filename}` section {section}
- **Recommended Fix**: Specify concrete criteria and implementation approach

**Note**: The above is a brief summary. Detailed review results (principle violation details, auto-fix summary, etc.) will be output separately by the spec-reviewer agent.

---

### Recommended Actions

#### Priority Order

1. **PRD ↔ spec Coverage Improvement** (if coverage is below 80%)
   - Resolve 🔴 Not Covered requirements first
   - Update 🟡 Partially Covered requirements to full coverage
   - Target to raise coverage above 80%

2. **Resolve Critical Discrepancies**
   - API signature mismatches
   - Implementation or removal of unimplemented features from spec
   - Type definition mismatches

3. **Address Warnings and Info**
   - Ensure module structure consistency
   - Document undocumented implementations in spec

#### Resolution Flow

1. Review PRD ↔ spec inconsistencies and assess each requirement's coverage status
2. For Not Covered or Partially Covered requirements, determine:
   - Is the requirement still valid? → If valid, add to spec
   - Has the requirement become obsolete? → If obsolete, remove or deprecate from PRD
3. Resolve spec ↔ design ↔ implementation discrepancies
4. Decide whether to modify specification or implementation
5. After modifications, run `/check_spec` again to verify

````

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

````markdown
### Serena Symbol Analysis Results

| Symbol | In Spec | Implementation Status | Reference Count |
|:---|:---|:---|:---|
| `createUser` | Yes | Implemented | 5 |
| `deleteUser` | Yes | Not Implemented | 0 |
| `internalHelper` | No | Implemented | 3 |
````

### Behavior When Serena is Not Configured

Even without Serena, consistency checking is performed using traditional text-based search (Grep/Glob).
Features are limited but work language-agnostically.

## Notes

- If specifications don't exist, recommend creating them with `/generate_spec` first
- If many discrepancies exist, major specification updates may be needed
- If implementation is correct and specs are outdated, update specifications
- If specifications are correct and implementation is wrong, fix implementation
