---
name: clarify
description: "Analyze specifications and generate clarification questions to eliminate ambiguity before implementation"
argument-hint: "<feature-name> [--interactive]"
version: 3.0.0
license: MIT
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Clarify - Specification Clarification

Scans specifications across 9 key categories and generates targeted clarification questions to eliminate ambiguity
before implementation.

## Prerequisites

**Read the following prerequisite references before execution:**

- `references/prerequisites_plugin_update.md` - Check for plugin updates
- `references/prerequisites_principles.md` - Read AI-SDD principles document
- `references/prerequisites_directory_paths.md` - Resolve directory paths using `SDD_*` environment variables

### Relationship to Vibe Detector Skill

This command is complementary to the `vibe-detector` skill:

| Tool              | Purpose                                     | When to Use                    |
|:------------------|:--------------------------------------------|:-------------------------------|
| **vibe-detector** | Detects vague instructions in user requests | During task initiation         |
| **clarify**       | Scans existing specs for ambiguity and gaps | Before implementation planning |

### Language Configuration

Output templates are located under `templates/${SDD_LANG:-en}/` within this skill directory.
The `SDD_LANG` environment variable determines the language (default: `en`).

## Input

$ARGUMENTS

| Argument        | Required | Description                                                        |
|:----------------|:---------|:-------------------------------------------------------------------|
| `feature-name`  | Yes      | Target feature name or path (e.g., `user-auth`, `auth/user-login`) |
| `--interactive` | -        | Interactive mode: Answer questions one at a time                   |

### Input Examples

```
/clarify user-auth
/clarify task-management
/clarify auth/user-login  # For hierarchical structure
```

## Processing Flow

### 1. Load Target Specifications

Both flat and hierarchical structures are supported.

**For flat structure**:

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{feature-name}.md (PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md (if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{feature-name}_design.md (if exists)
```

**For hierarchical structure** (when argument contains `/`):

```
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/index.md (parent feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_REQUIREMENT_PATH}/{parent-feature}/{feature-name}.md (child feature PRD, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_spec.md (parent feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_spec.md (child feature spec, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/index_design.md (parent feature design, if exists)
Load ${CLAUDE_PROJECT_DIR}/${SDD_SPECIFICATION_PATH}/{parent-feature}/{feature-name}_design.md (child feature design, if exists)
```

**Note the difference in naming conventions**:

- **Under requirement**: No suffix (`index.md`, `{feature-name}.md`)
- **Under specification**: `_spec` or `_design` suffix required (`index_spec.md`, `{feature-name}_spec.md`)

### 2. Nine Category Analysis

Analyze specifications across 9 key categories. See `references/nine_category_analysis.md` for:

- Full category definitions and analysis focus
- Clarity level classification (Clear / Partial / Missing)
- Question prioritization criteria
- Question format template

### 3. Generate Clarification Questions

Based on category analysis, generate up to 5 high-impact questions using the format in
`references/nine_category_analysis.md`.

### 4. Integrate Answers

After receiving user answers, the **main agent (this skill)** applies the integration:

1. **Review Integration Proposals**: Review proposals from `clarification-assistant` agent output
2. **Update Specifications**: Apply approved changes to appropriate `*_spec.md` or `*_design.md` using Edit/Write tools
3. **Mark Resolved**: Track which questions have been addressed
4. **Generate Diff**: Show what was added to specifications

**Note**: The `clarification-assistant` agent outputs integration proposals (target file, section, content). This skill
applies the actual edits.

## Output

Use the `templates/${SDD_LANG:-en}/clarification_output.md` template for output formatting.

## Integration Mode

When user provides answers, use `--integrate` flag:

```
/clarify user-auth --integrate
```

This will:

1. Prompt for answers to each question
2. Update specifications incrementally
3. Show diffs of changes

## Best Practices

### When to Use This Command

| Scenario                               | Recommended Action                                |
|:---------------------------------------|:--------------------------------------------------|
| **Before task breakdown**              | Run `/clarify` to catch ambiguities early         |
| **After receiving vague requirements** | Use with `/generate-spec` to build complete specs |
| **During spec review**                 | Verify all 9 categories are addressed             |
| **Before implementation**              | Final check to ensure no hidden assumptions       |

### Complementary Commands

```
/clarify {feature}           # Identify ambiguities
|
(Update specs with answers)
|
/check-spec {feature}        # Verify consistency
|
/task-breakdown {feature}    # Generate tasks
```

## Advanced Options

### Focus on Specific Categories

```
/clarify user-auth --categories flow,integrations,edge-cases
```

### Specify Output Detail Level

```
/clarify user-auth --detail minimal    # Top 3 questions only
/clarify user-auth --detail standard   # Top 5 questions (default)
/clarify user-auth --detail comprehensive  # All identified issues
```

## Post-Clarification Verification

### Automatic Verification (Performed)

The following verifications are automatically performed during clarification:

- [x] **Nine Category Scan**: Comprehensively detect ambiguities across functional scope, data model, flow, etc.
- [x] **Clarity Score Calculation**: Classify items as Clear/Partial/Missing and calculate overall score
- [x] **Question Prioritization**: Select questions based on impact, risk, and blocker status

### Verification Commands

```bash
# Re-scan to verify clarity improvements
/clarify {feature-name}

# Consistency check (verify updated specifications)
/check-spec {feature-name} --full
```

### Implementation Readiness Criteria

| Clarity Score | Recommended Action                                   |
|:--------------|:-----------------------------------------------------|
| 80% or above  | Ready for implementation                             |
| 60-79%        | Recommended to resolve Partial items                 |
| Below 60%     | Further clarification required before implementation |

## Notes

- Questions are generated based on specification analysis, not assumptions
- Prioritize questions that would cause most implementation uncertainty
- Some ambiguity is acceptable for low-risk, low-impact decisions
- Re-run after major specification updates to catch new ambiguities
- Works best when combined with vibe-detector skill during task initiation
