---
name: vibe-detector
description: "Automatically executed before implementation to analyze user instructions and detect Vibe Coding (problems where AI must infer undefined requirements due to vague instructions). Warns when detecting ambiguous expressions like 'make it nice', 'somehow', 'same as before', specification gaps, or unclear requirements, prompting for clarification."
argument-hint: "[user-instruction]"
license: MIT
user-invocable: false
allowed-tools: Read, Glob, Grep, AskUserQuestion
disallowed-tools: Write, Edit, Bash
---

# Vibe Detector - Automatic Detection of Vague Instructions

Analyzes user input to detect Vibe Coding (the problem where AI must guess undefined requirements due to vague
instructions).

## Language Configuration

!`echo "Current language: ${SDD_LANG:-en}"`

When reading templates, use the path: `templates/${SDD_LANG:-en}/`

## Prerequisites

**Before execution, you must read the AI-SDD principles document.**

AI-SDD principles document path: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/AI-SDD-PRINCIPLES.md`

**Note**: This file is automatically updated at the start of each session.

Understand AI-SDD principles.

This skill follows AI-SDD principles for Vibe Coding detection.

See `references/prerequisites_directory_paths.md` for directory path resolution using `SDD_*` environment variables.

## Input

This skill is triggered automatically via hooks when the user submits a message.
It receives user input context for analysis.

| Input Source   | Description                                           |
|:---------------|:------------------------------------------------------|
| User message   | The user's instruction or request text                |
| Existing specs | Loaded from `${SDD_SPECIFICATION_PATH}/` if available |

**Note**: This skill is `user-invocable: false` and cannot be called directly with `/vibe-detector`.

## Detection Patterns

### Vague Instructions

| Pattern                    | Examples                                                       |
|:---------------------------|:---------------------------------------------------------------|
| **Subjective expressions** | "Make it nice," "somehow," "make it work," "make it look good" |
| **Unclear degree**         | "Make it faster," "improve a bit," "roughly working is fine"   |
| **Ambiguous scope**        | "That feature," "the previous one," "the usual"                |
| **Implicit assumptions**   | "Same as before," "as usual," "obviously..."                   |
| **Ambiguous priority**     | "If possible," "when you have time," "while you're at it"      |

### Missing Specifications

| Pattern                         | Examples                                            |
|:--------------------------------|:----------------------------------------------------|
| **Missing requirements**        | "Create X feature" (no details)                     |
| **Undefined I/O**               | No arguments, return values, error cases documented |
| **Unknown boundary conditions** | Maximum/minimum values, edge cases undefined        |
| **Undefined error handling**    | Abnormal case behavior unclear                      |

### Unclear Scope

| Pattern                         | Examples                                           |
|:--------------------------------|:---------------------------------------------------|
| **Vague target**                | "Improve performance" (which part? what criteria?) |
| **Unknown impact scope**        | "Refactor" (which scope?)                          |
| **Missing completion criteria** | When is it considered complete?                    |

## Risk Assessment Criteria

| Level      | Condition                        | Response                                                 |
|:-----------|:---------------------------------|:---------------------------------------------------------|
| **High**   | No specs + vague instructions    | **Require** specification creation before implementation |
| **Medium** | Specs exist + some ambiguity     | Clarify ambiguous points before implementation           |
| **Low**    | Specs exist + clear requirements | Can start implementation                                 |

## Detection Response Flow

See `references/detection_response_flow.md` for the step-by-step response flow.

## Output Format

Read `templates/${SDD_LANG:-en}/risk_report.md` and use it for risk detection output.

**If template does not exist**: Use `templates/${SDD_LANG:-en}/risk_report_fallback.md` as the output structure.

## Escalation When Specifications Are Insufficient

Even when user refuses specification creation, ensure minimum guardrails:

### 1. Document Inferred Specifications

Read `templates/${SDD_LANG:-en}/assumed_spec.md` and use it for creating inferred specification documents.

**If template does not exist**: Use `templates/${SDD_LANG:-en}/assumed_spec_fallback.md` as the document
structure.

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/assumed-spec.md`

### 2. Set Verification Points

List items to confirm with user upon implementation completion:

- Whether inferred specifications match intent
- Whether edge case behavior is as expected
- Whether non-functional requirements (performance, etc.) are met

### 3. Visualize Risks

Explicitly state potential issues due to specification gaps:

- Risk of re-implementation
- Risk of bug introduction
- Risk of technical debt accumulation

## Notes

- This skill **detects and warns** but does not block implementation
- Final judgment is left to the user
- If proceeding despite warnings, always record inferred specifications
- Reference existing project specifications to improve detection accuracy
