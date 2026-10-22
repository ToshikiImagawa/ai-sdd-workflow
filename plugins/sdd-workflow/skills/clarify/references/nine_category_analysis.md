# Nine Category Analysis

Analyze specifications across these categories to identify ambiguity and gaps.

## Categories

| Category                           | Analysis Focus                       | Examples of Ambiguity                   |
|:-----------------------------------|:-------------------------------------|:----------------------------------------|
| **1. Functional Scope**            | What the feature does vs doesn't do  | Edge cases, boundary conditions         |
| **2. Data Model**                  | Data structures, types, constraints  | Field nullability, validation rules     |
| **3. Flow & Behavior**             | State transitions, error handling    | Rollback behavior, retry logic          |
| **4. Non-Functional Requirements** | The seven categories in `nfr_checklist.md` | Response time requirements, rate limits |
| **5. Integrations**                | External system dependencies         | Authentication methods, API versions    |
| **6. Edge Cases**                  | Boundary conditions, error scenarios | Empty states, network failures          |
| **7. Constraints**                 | Technical limitations, trade-offs    | Browser support, data size limits       |
| **8. Terminology**                 | Domain-specific terms                | Consistent naming, acronym definitions  |
| **9. Completion Signals**          | "Done" criteria, success metrics     | Acceptance criteria, test coverage      |

For category 4, use the seven categories of `${CLAUDE_PLUGIN_ROOT}/shared/references/nfr_checklist.md` (Performance, Security,
Reliability, Scalability, Usability, Maintainability, Compatibility) and its Level 0–3 vocabulary: Level 0 is Missing,
Level 1 is Partial, Level 2 or higher is Clear (same mapping as `ambiguity_criteria.md` Section 3). Only categories the
feature affects are judged.

## Clarity Level Classification

For each category, classify clarity as:

| Level       | Criteria                               | Example                             |
|:------------|:---------------------------------------|:------------------------------------|
| **Clear**   | Fully specified with explicit examples | "Return 404 when user ID not found" |
| **Partial** | Concept exists but details missing     | "Handle errors appropriately"       |
| **Missing** | Not mentioned in specifications        | No mention of authentication flow   |

**Check the implementation before classifying Non-Functional Requirements / Constraints as Partial or
Missing**: when the target feature's `impl-status` is `implemented` (or it otherwise has real code
behind it), an apparently undefined threshold, limit, or timeout may already be a concrete decision
recorded only in the implementation (e.g. a `TIMEOUT_SECONDS` constant, a hard-coded retry count) rather
than in the spec's prose. Search the relevant implementation (scripts, config defaults, constants) for
the value before raising a clarification question about it. If the implementation already answers the
question, classify the category as **Clear** and cite the implementation as the basis instead of
re-asking something the codebase has already settled. Only when neither the spec nor the implementation
fixes the value does it remain genuinely ambiguous.

## Clarity Score Formula

**Clarity score** = Clear items ÷ (all items − N/A items). Counting is per item (the unit used in `clarify_spec.md`), not per category. Partial and Missing stay in the denominator but never enter the numerator. An item that does not apply to the feature is classified **N/A** and removed from the denominator; the 9-category summary below still records every category (a category whose items are all N/A is recorded as N/A with its basis).

Example: 20 items, 2 N/A, 9 Clear, 6 Partial, 3 Missing → 9 ÷ (20 − 2) = 50%.

This is the canonical definition; other files summarize in one line and link here.

## Category Analysis Summary (Required Output)

Record the Clear / Partial / Missing / N/A classification for **all 9 categories**, not only the ones that
become questions. A category that turns into no question still needs its classification and a one-line
basis (the specific statement, or its absence, that the classification rests on) recorded in the output.
Without this, the analysis's actual coverage — which categories were checked and how thoroughly — is
invisible to the reader, and detection granularity becomes unverifiable run to run.

```markdown
### Category Analysis Summary

| # | Category               | Classification | Basis                                    |
|:--|:------------------------|:----------------|:------------------------------------------|
| 1 | Functional Scope        | Clear/Partial/Missing/N/A | {statement, or "not mentioned"}     |
| ... (all 9 rows) |
```

## Question Prioritization

Generate up to 5 high-impact questions prioritizing:

**Selection Criteria**:

1. **Impact**: Would ambiguity cause major implementation divergence?
2. **Frequency**: Will this decision affect multiple modules?
3. **Risk**: Could wrong assumptions require significant rework?

## Question Format

```markdown
### Q{n}: {Category} - {Question Title}

**Context**: {Brief explanation of why this matters}

**Question**: {Specific question requiring user decision}

**Examples to Consider**:
- Option A: {Example}
- Option B: {Example}

**Current Specification State**: Clear / Partial / Missing
```
