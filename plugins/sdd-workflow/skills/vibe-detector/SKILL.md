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

## Task Type Determination

Independently of the ambiguity/risk assessment above, classify the request against the **Task Type
Determination** table in `AI-SDD-PRINCIPLES.md` § Workflow Management Guidelines and report the starting
phase that type requires — the first phase listed in that table's "Required Phases" column for the matched
row (e.g. Breaking Change and New Feature both start at Specify; Bug Fix and Technical Investigation start
at Tasks; Refactoring starts at Plan). Match by signal in the request:

| Signal in the request                                                              | Task Type               |
|:-------------------------------------------------------------------------------------|:-------------------------|
| Removes/changes existing public API or behavior; existing consumers must adapt       | Breaking Change          |
| No existing spec covers the request; new business domain or cross-feature scope      | New Feature (Large)      |
| No existing spec covers the request; contained to an existing feature/module         | New Feature (Small)      |
| Corrects a deviation from an existing spec; no spec change needed                    | Bug Fix                  |
| Restructures existing code with no behavior change                                   | Refactoring               |
| Pure investigation/analysis, no code change implied                                  | Technical Investigation  |

When signals are mixed or unclear, report the closest match and note the ambiguity rather than guessing
silently — this determination feeds the risk report's "Recommended Starting Phase" field below.

## Detection Response Flow

See `references/detection_response_flow.md` for the step-by-step response flow.

## Output Format

Read `templates/${SDD_LANG:-en}/risk_report.md` and use it for risk detection output.

**If template does not exist**: Use `templates/${SDD_LANG:-en}/risk_report_fallback.md` as the output structure.

## Escalation When Specifications Are Insufficient

Even when user refuses specification creation, ensure minimum guardrails:

### 1. Document Inferred Specifications

Read `templates/${SDD_LANG:-en}/assumed_spec.md` and use it to draft the inferred specification content.

**If template does not exist**: Use `templates/${SDD_LANG:-en}/assumed_spec_fallback.md` as the document
structure.

This skill's `allowed-tools` deliberately excludes `Write`/`Edit`/`Bash` — it fires automatically before every
implementation, so it must stay a read-only detector and never persist files on its own. Include the fully
drafted document content in this skill's own output (under the risk report) and instruct the calling session
to save it to `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/assumed-spec.md`. The calling session (which
invoked this skill and holds normal write access) performs the actual save.

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
- If proceeding despite warnings, always include the inferred specification in the output so the calling
  session can record it (this skill cannot write files itself)
- Reference existing project specifications to improve detection accuracy
