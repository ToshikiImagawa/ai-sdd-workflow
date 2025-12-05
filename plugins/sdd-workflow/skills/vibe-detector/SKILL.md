---
name: vibe-detector
description: "Analyzes user input to automatically detect Vibe Coding (vague instructions) and assess risk. Used when detecting ambiguous implementation instructions or specification gaps."
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Vibe Detector - Automatic Detection of Vague Instructions

Analyzes user input to detect Vibe Coding (the problem where AI must guess undefined requirements due to vague instructions).

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This skill follows the sdd-workflow agent principles for Vibe Coding detection.

## Detection Patterns

### Vague Instructions

| Pattern | Examples |
|:---|:---|
| **Subjective expressions** | "Make it nice," "somehow," "make it work," "make it look good" |
| **Unclear degree** | "Make it faster," "improve a bit," "roughly working is fine" |
| **Ambiguous scope** | "That feature," "the previous one," "the usual" |
| **Implicit assumptions** | "Same as before," "as usual," "obviously..." |
| **Ambiguous priority** | "If possible," "when you have time," "while you're at it" |

### Missing Specifications

| Pattern | Examples |
|:---|:---|
| **Missing requirements** | "Create X feature" (no details) |
| **Undefined I/O** | No arguments, return values, error cases documented |
| **Unknown boundary conditions** | Maximum/minimum values, edge cases undefined |
| **Undefined error handling** | Abnormal case behavior unclear |

### Unclear Scope

| Pattern | Examples |
|:---|:---|
| **Vague target** | "Improve performance" (which part? what criteria?) |
| **Unknown impact scope** | "Refactor" (which scope?) |
| **Missing completion criteria** | When is it considered complete? |

## Risk Assessment Criteria

| Level | Condition | Response |
|:---|:---|:---|
| **High** | No specs + vague instructions | **Require** specification creation before implementation |
| **Medium** | Specs exist + some ambiguity | Clarify ambiguous points before implementation |
| **Low** | Specs exist + clear requirements | Can start implementation |

## Detection Response Flow

```
1. Identify ambiguous points
   ↓
2. Determine risk level
   ↓
3. Request user confirmation/clarification
   ├─ Clarified → Proceed to implementation
   └─ Declined → Go to 4
   ↓
4. Propose specification creation/update
   ├─ Accepted → Implement after spec creation
   └─ Declined → Go to 5
   ↓
5. Explicitly warn of risks
   ↓
6. Record inferred specs in review/
   ↓
7. Implement with verification points set
```

## Output Format

Use [templates/risk_report.md](templates/risk_report.md) for risk detection output.

## Escalation When Specifications Are Insufficient

Even when user refuses specification creation, ensure minimum guardrails:

### 1. Document Inferred Specifications

Use [templates/assumed_spec.md](templates/assumed_spec.md) for creating inferred specification documents.

**Save Location**: `.docs/review/{ticket}/assumed-spec.md`

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
