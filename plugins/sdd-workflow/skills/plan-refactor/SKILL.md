---
name: plan-refactor
description: "Plan refactoring for existing features. Analyzes current implementation and creates/updates design documents with refactoring plan."
argument-hint: "<feature-name> [context] [--scope=<dir>] [--ci]"
version: 1.0.2
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
---

# Plan Refactoring

Plans refactoring for existing features by analyzing current implementation and creating/updating design documents with
a comprehensive refactoring plan.

This skill supports two scenarios:

- **Case A**: Existing documents (PRD/spec/design) → Analyze gaps and add refactoring plan
- **Case B**: No documents → Reverse-engineer spec/design from code, then add refactoring plan

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Language Configuration

Templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

| Argument        | Required | Description                                                          |
|:----------------|:---------|:---------------------------------------------------------------------|
| `feature-name`  | Yes      | Target feature name or path (supports flat/hierarchical structure)   |
| `context`       | No       | Refactoring goal or improvement intent (e.g., "無限スクロール化", "依存性注入導入") |
| `--scope=<dir>` | No       | Limit implementation file search scope (e.g., `src/`, `lib/`)        |
| `--ci`          | No       | CI/non-interactive mode (auto-confirm, no user prompts)              |

## Input Examples

```
/plan-refactor auth
/plan-refactor user-list "無限スクロール化してパフォーマンス改善"
/plan-refactor auth "依存性注入を導入してテスト容易性を向上"
/plan-refactor user-profile --scope=src/profile
/plan-refactor auth/login --ci
/plan-refactor payment-service "Strangler Figパターンで段階的にマイクロサービス化" --scope=src/services
```

## Processing Flow

### Phase 1: Pre-flight Checks

**Step 1.1: Scan for Existing Documents**

Run the document scanning script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/scripts/scan-existing-docs.sh" "${FEATURE_NAME}"
```

This script:

1. Checks for PRD, spec, and design documents in both flat and hierarchical structures
2. Exports results to `.sdd/.cache/plan-refactor/existing-docs.json`
3. Determines Case A (documents exist) or Case B (no documents)

**Step 1.2: Read Scan Results**

```bash
Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/existing-docs.json
```

Example output:

```json
{
  "prd_exists": true,
  "spec_exists": true,
  "design_exists": true,
  "prd_path": ".sdd/requirement/auth.md",
  "spec_path": ".sdd/specification/auth_spec.md",
  "design_path": ".sdd/specification/auth_design.md",
  "structure": "flat",
  "feature_name": "auth"
}
```

**Step 1.3: Determine Processing Case**

- If `design_exists` is `true` → **Case A** (existing documents)
- If `design_exists` is `false` → **Case B** (no documents, reverse-engineering needed)

---

### Phase 1.5: Parse User Intent (Optional)

**If `context` argument is provided:**

Parse the user's refactoring goal and extract:

1. **Primary Goal** - What to achieve (e.g., "無限スクロール化", "依存性注入導入")
2. **Motivation** - Why it's needed (e.g., "パフォーマンス改善", "テスト容易性向上")
3. **Approach** - Specific technique if mentioned (e.g., "react-window使用", "Strangler Figパターン")

**Example context parsing:**

| Context Input                       | Extracted Information                          |
|:------------------------------------|:-----------------------------------------------|
| `"無限スクロール化してパフォーマンス改善"`             | Goal: 無限スクロール化<br>Motivation: パフォーマンス改善        |
| `"依存性注入を導入してテスト容易性を向上"`             | Goal: 依存性注入導入<br>Motivation: テスト容易性向上          |
| `"Strangler Figパターンで段階的にマイクロサービス化"` | Goal: マイクロサービス化<br>Approach: Strangler Figパターン |
| `"テスト容易性を上げるため密結合を解消"`              | Goal: 密結合解消<br>Motivation: テスト容易性向上            |
| `"モジュール境界を明確化してメンテナンス性向上"`          | Goal: モジュール境界明確化<br>Motivation: メンテナンス性向上      |
| `"react-windowを使って仮想スクロール化"`        | Goal: 仮想スクロール化<br>Approach: react-window使用     |

**Use extracted information in Phase 3:**

- Prioritize the user's goal in "Purpose and Background"
- Align "Refactoring Strategy" with the specified approach
- Include the motivation in "Business/Technical Drivers"

**If `context` is NOT provided:**
→ Skip this phase, proceed with automatic analysis only (Phase 2)

---

### Phase 2: Implementation Discovery

**Step 2.1: Find Implementation Files**

Run the implementation file search script:

```bash
SCOPE_DIR="${SCOPE_ARG}"  # From --scope argument, or empty
bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/scripts/find-implementation-files.sh" "${FEATURE_NAME}" "${SCOPE_DIR}"
```

This script:

1. Searches for files matching feature name (by filename and content)
2. Limits search to specified scope if `--scope` is provided
3. Excludes `node_modules/`, `.git/`, `dist/`, etc.
4. Exports results to `.sdd/.cache/plan-refactor/implementation-files.json`

**Step 2.2: Read Implementation File List**

```bash
Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/implementation-files.json
```

Example output:

```json
{
  "feature_name": "auth",
  "file_count": 8,
  "scope_dir": "src/",
  "files_list_path": ".sdd/.cache/plan-refactor/all-files.txt"
}
```

**Step 2.3: Validate File Count**

- If `file_count` > 20 and NOT in `--ci` mode:
    - Use `AskUserQuestion` to confirm: "Found {count} files. This may take time to analyze.
      Continue? [Yes/No/Adjust Scope]"
    - If "Adjust Scope": Ask user for new scope directory

**Step 2.4: Read Implementation Files**

```bash
Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/.cache/plan-refactor/all-files.txt
```

Then read the actual implementation files (prioritize key files):

1. Read up to 10 most relevant files
2. Focus on main logic files, avoid test files initially

### Phase 3: Process Branching

#### Case A: Existing Documents

**Step 3A.1: Load Existing Documents**

Read the following files (paths from scan results):

- PRD: `{prd_path}` (if exists)
- Spec: `{spec_path}` (if exists)
- Design: `{design_path}` (required for Case A)

**Step 3A.2: Analyze Implementation vs. Specification**

Compare implementation with design document:

1. Identify components described in design doc
2. Check if implementation matches design
3. Identify deviations, technical debt, or areas needing refactoring

**Step 3A.3: Identify Refactoring Opportunities**

Based on analysis, identify:

- **Problems**: Tight coupling, code duplication, poor testability, etc.
- **Gaps**: Missing functionality, incomplete implementation
- **Technical Debt**: Hard-coded values, lack of error handling, etc.

**If `context` was provided (from Phase 1.5):**

- Prioritize issues related to the user's goal
- Align identified problems with the specified motivation
- Example: If context is "無限スクロール化してパフォーマンス改善", focus on:
    - Current loading performance issues
    - Memory usage problems
    - Scalability concerns

**Step 3A.4: Generate Refactoring Plan**

Use template:

```bash
Read ${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/templates/${SDD_LANG}/refactor-plan-section.md
```

Fill in the template with:

- **Purpose and background** (why refactoring is needed)
    - **If `context` provided**: Start with user's goal (e.g., "無限スクロール化してパフォーマンス改善")
    - Include motivation from context in "Business/Technical Drivers"
- **Current state analysis** (problems, metrics, root cause)
    - Focus on issues related to user's goal if context provided
- **Refactoring strategy** (goals, approach, trade-offs)
    - **If `context` provided**: Align goals with user's intent
    - **If approach specified in context**: Use it (e.g., "Strangler Figパターン", "react-window使用")
- Migration plan (phased tasks)
- Impact analysis (breaking changes, affected components, rollback plan)
- Testing strategy
- Success criteria
- Risks and mitigations
- Timeline and milestones

**Step 3A.5: Update Design Document**

Edit the existing design document:

```bash
Edit {design_path}
```

Append the "## Refactoring Plan" section at the end of the document.

See `references/design-doc-integration.md` for guidelines on integration.

---

#### Case B: No Documents (Reverse Engineering)

**Step 3B.1: Reverse-Engineer Specification**

Analyze implementation files and extract:

- Functional requirements (what the feature does)
- Non-functional requirements (performance, security, etc.)
- Interface specifications (APIs, function signatures)
- Dependencies
- Data model

Use template:

```bash
Read ${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/templates/${SDD_LANG}/reverse-spec-template.md
```

**Step 3B.2: Write Specification Document**

Determine path based on structure:

- Flat: `${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`
- Hierarchical: `${SDD_SPECIFICATION_PATH}/{parent-feature}/{child-feature}_spec.md`

```bash
Write {spec_path}
```

Mark the document as reverse-engineered:
> **⚠️ Note**: This specification was reverse-engineered from existing implementation on {DATE}.
> It may not reflect the original design intent. Please review and update as needed.

**Step 3B.3: Reverse-Engineer Design Document**

Analyze implementation files and extract:

- Architecture overview
- Component structure
- Data flow
- Key algorithms
- API design
- Database schema
- Testing strategy
- Technical debt observations

Use template:

```bash
Read ${CLAUDE_PLUGIN_ROOT}/skills/plan-refactor/templates/${SDD_LANG}/reverse-design-template.md
```

**Step 3B.4: Write Design Document**

Determine path based on structure:

- Flat: `${SDD_SPECIFICATION_PATH}/{feature-name}_design.md`
- Hierarchical: `${SDD_SPECIFICATION_PATH}/{parent-feature}/{child-feature}_design.md`

```bash
Write {design_path}
```

**Step 3B.5: Generate Refactoring Plan**

Follow the same process as Case A Step 3A.4-3A.5:

1. Read refactoring plan template
2. Fill in the template
3. Append "## Refactoring Plan" section to the newly created design document

---

### Phase 4: Validation

Verify the refactoring plan includes all required sections:

**Required Sections Checklist:**

- [ ] Purpose and Background
- [ ] Current State Analysis (with problems identified)
- [ ] Refactoring Strategy (with goals and approach)
- [ ] Migration Plan (with phased tasks and estimates)
- [ ] Impact Analysis (breaking changes, affected components, rollback plan)
- [ ] Testing Strategy (unit, integration, E2E tests)
- [ ] Success Criteria (metrics and acceptance criteria)
- [ ] Risks and Mitigations
- [ ] Timeline and Milestones (optional but recommended)
- [ ] References (to PRD, spec, patterns)

If any required section is missing, add it before proceeding.

### Phase 5: Next Steps

Output a summary and recommend next steps:

```
✅ Refactoring plan completed

**Generated/Updated Files:**
- {spec_path} (if Case B)
- {design_path}

**Refactoring Plan Location:**
{design_path} - "Refactoring Plan" section

**Next Steps:**
1. Review the refactoring plan at: {design_path}
2. Run `/task-breakdown {feature-name}` to break down the refactoring into actionable tasks
3. Execute tasks with `/implement {feature-name}` using TDD approach
```

## Output

- **Case A**: Updated design document with new "Refactoring Plan" section
- **Case B**:
    - New specification document (reverse-engineered)
    - New design document (reverse-engineered with refactoring plan)

Output format:

```
File: {file_path}
Status: {Created/Updated}
Sections Added: Refactoring Plan
```

## Notes

### Using Context Parameter

The optional `context` parameter allows you to explicitly specify your refactoring goal:

**Without context (automatic analysis):**

```bash
/plan-refactor user-list
```

→ Claude analyzes code and design, automatically identifies technical debt and proposes generic refactoring

**With context (goal-directed refactoring):**

```bash
/plan-refactor user-list "無限スクロール化してパフォーマンス改善"
```

→ Claude focuses on infinite scroll implementation, prioritizes performance issues, proposes specific approach

**Context examples:**

| Use Case                 | Context Example                     |
|:-------------------------|:------------------------------------|
| Performance optimization | `"無限スクロール化してパフォーマンス改善"`             |
| Architecture improvement | `"依存性注入を導入してテスト容易性を向上"`             |
| Gradual migration        | `"Strangler Figパターンで段階的にマイクロサービス化"` |
| Technology upgrade       | `"react-windowを使って仮想スクロール化"`        |
| Code quality             | `"密結合を解消してモジュール境界を明確化"`             |

**Benefits of using context:**

- More focused refactoring plan
- Aligns with your specific intent
- Includes your preferred approach/pattern
- Reduces ambiguity in Purpose and Strategy sections

### Context Parameter Edge Cases

**Ambiguous Context:**

If context is unclear or too vague (e.g., "improve it", "make it better"), use `AskUserQuestion` to clarify:

```
Question: "What specific aspect do you want to improve?"
Options:
- Performance (e.g., speed, memory usage)
- Maintainability (e.g., code structure, readability)
- Testability (e.g., unit test coverage, mockability)
- Scalability (e.g., handle more users, larger datasets)
```

**Unrealistic or Infeasible Context:**

If context contains technically unrealistic goals (e.g., "make it 100x faster", "zero latency"):

1. Acknowledge the goal in "Purpose and Background"
2. Propose realistic, achievable targets in "Refactoring Strategy"
3. Explain trade-offs and constraints in "Trade-offs" section

Example:

- User context: "make it 100x faster"
- Plan approach: "Target 5-10x performance improvement through caching and query optimization. 100x improvement would
  require architectural changes beyond refactoring scope."

**Conflicting Requirements:**

If context includes conflicting goals (e.g., "maximize performance and minimize code complexity"):

1. Use `AskUserQuestion` to prioritize:
   ```
   Question: "These goals may conflict. Which is more important?"
   Options:
   - Prioritize performance (may increase complexity)
   - Prioritize simplicity (may sacrifice some performance)
   - Balance both (moderate improvements to each)
   ```

2. Document the prioritization in "Purpose and Background"

### Document Integration

- Refactoring plans are integrated into existing design documents, not separate files
- This maintains traceability and keeps all design information in one place
- See `references/design-doc-integration.md` for detailed integration guidelines

### Refactoring Patterns

- See `references/refactor-patterns.md` for common refactoring patterns
- Includes: Extract Interface, Extract Class, Dependency Injection, Strategy Pattern, Strangler Fig Pattern, etc.

### File Naming Conventions

**IMPORTANT:** Follow the established naming conventions:

| Directory        | File Type | Naming Pattern                                         |
|:-----------------|:----------|:-------------------------------------------------------|
| `requirement/`   | PRD       | `{feature-name}.md` (no suffix)                        |
| `specification/` | Spec      | `{feature-name}_spec.md` (`_spec` suffix required)     |
| `specification/` | Design    | `{feature-name}_design.md` (`_design` suffix required) |

### Hierarchical Structure Support

Both flat and hierarchical structures are supported:

**Flat Structure:**

```
.sdd/
├── requirement/
│   └── auth.md
└── specification/
    ├── auth_spec.md
    └── auth_design.md
```

**Hierarchical Structure (Parent):**

```
.sdd/
├── requirement/
│   └── auth/
│       └── index.md
└── specification/
    └── auth/
        ├── index_spec.md
        └── index_design.md
```

**Hierarchical Structure (Child):**

```
.sdd/
├── requirement/
│   └── auth/
│       ├── index.md
│       └── login.md
└── specification/
    └── auth/
        ├── index_design.md
        └── login_design.md
```

### Examples

- See `examples/case-a-existing-docs.md` for Case A example
- See `examples/case-b-no-docs.md` for Case B example

### Multi-Feature Refactoring

When refactoring affects multiple features:

1. Add refactoring plan to each feature's design doc
2. Add cross-references between affected features
3. Or create a parent feature to centralize the plan

See `references/design-doc-integration.md` for guidance.

### Post-Refactoring Cleanup

After refactoring is complete:

1. Update the Refactoring Plan section status to "Completed"
2. Update main sections of design doc to reflect new architecture
3. Clean up task logs (`task/` directory) after implementation
4. Archive the refactoring plan (collapse into `<details>` tag) if desired

---

**Last Updated:** 2026-02-15
**Maintained by:** AI-SDD Workflow Plugin
