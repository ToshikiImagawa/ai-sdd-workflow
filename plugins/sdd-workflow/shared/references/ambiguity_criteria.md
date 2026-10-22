# Ambiguity Assessment Criteria

Single place for the criteria used to judge ambiguity. Consumers (`vibe-detector`, and the skills that follow its risk wording) reference this file instead of restating the criteria. The risk table in `vibe-detector/SKILL.md` is a summary; this file is the canonical, detailed definition.

All ratios here are **guidance**, not fixed cut-offs. Marks are judged per requirement; the overall High/Medium/Low is fixed by Section 2.

## 1. Per-Requirement Marks (○ / △ / ×)

Judge each requirement (FR, NFR, or a stated request item) on its own. The marks correspond in meaning to the clarity scale of `/clarify` (○ = Clear, △ = Partial, × = Missing); the granularity differs, since `/clarify` scores per category item. The test is the same one `spec-reviewer` uses for 🟡 Partially Covered, but `spec-reviewer` applies it to PRD→spec traceability and aggregates the result as the Coverage Rate (which includes Partially); that rate is separate from the `/clarify` clarity score.

| Mark | Meaning | Test |
|:-----|:--------|:-----|
| ○ | Clear | A third party can decide pass/fail from the text alone: target, inputs/outputs, error behavior, boundary conditions, and completion criteria that apply to the requirement are all stated |
| △ | Partial | The requirement is stated but at least one applicable item is missing or vague (e.g., a target without a value, a success path without error cases) |
| × | Missing | The requirement is absent, or only names a topic with nothing to judge against ("Create X feature", "improve performance") |

Rules:

- Judge only items that apply to the requirement; mark an item N/A explicitly rather than counting it as missing
- When unsure between two marks, choose the lower one and list the missing item as a clarification question
- For an NFR, take the mark from Section 3
- When a spec weakens the verification method or strength its PRD states (e.g., PRD: test; spec: manual check), mark △
- When a requirement is delegated by link to a canonical document, mark ○ if the link target exists and satisfies the requirement; otherwise judge as usual

### Reading the Distribution (when a PRD or spec exists)

A **core requirement** is one the PRD or spec itself positions as central (e.g., its main functional requirements); everything else is supporting. Read the marks as a distribution, not a score to compute. This reading is a lead-in: the level that is reported is fixed by Section 2 (Section 2 wins on any disagreement).

| Reading | Guidance |
|:--------|:---------|
| Mostly clear | Almost all ○; a × should rarely be tolerated, and a × normally rules out reporting Low |
| Mixed | ○ is the majority with some △; each × is already listed as a question |
| Mostly unclear | △ and × are the majority, or × appears on a core requirement |

A single × on a core requirement outweighs a high ○ ratio. Report the counts (○ / △ / ×) with the judgment so the reader can disagree.

## 2. Risk Level (for `vibe-detector`)

`vibe-detector` also receives input with no PRD or spec (a one-line request), so a ratio cannot always be computed. The level is fixed by **viewpoint checks**.

### Viewpoints

For the request (and the specs, if any), mark each as ○ / △ / ×:

| # | Viewpoint | ○ when |
|:--|:----------|:-------|
| V1 | Target and purpose | What is built or changed, and why, is identifiable |
| V2 | Inputs/outputs | Arguments, return values, data shapes are stated |
| V3 | Error handling | Abnormal-case behavior is stated |
| V4 | Boundary conditions | Limits and edge cases are stated |
| V5 | Completion criteria | "Done" can be verified |
| V6 | Non-functional targets | The NFR mark from Section 3. N/A when no NFR category is affected (requirement wording that fits none of the seven categories is outside V6; see "Mapping Requirements to the Seven Categories" in `nfr_checklist.md`) |

### Decision

V1–V5 are also N/A when the spec explicitly states that the viewpoint does not apply (e.g., "no inputs: takes no arguments"). V3 and V4 marks: △ = some abnormal cases or boundaries are stated; × = none is stated at all.

Every input falls in exactly one row. Only applicable viewpoints count (N/A is ignored).

| Specs | Viewpoints | Level |
|:------|:-----------|:------|
| None | Any of V1–V5 is × | **High** |
| None | No × in V1–V5 (△ allowed, or all ○) | **Medium** |
| Exist | Any applicable viewpoint (V1–V6) is △ or × | **Medium** |
| Exist | All applicable viewpoints are ○ | **Low** |

This extends the 3-row risk table in `vibe-detector` (High / Medium / Low) so that "vague" and "some ambiguity" are checkable and so that "no specs but a clear request" has a defined level (Medium: a spec is still needed). Task type is determined separately.

## 3. NFR: Using `nfr_checklist.md`

Do not invent a second scale for NFRs. Take the level (0–3) from `nfr_checklist.md` (which also maps requirement wording to the seven categories) and map it to a mark:

| NFR level | Mark |
|:----------|:-----|
| 0 Not stated | × |
| 1 Mention only | △ |
| 2 Target value, 3 Target + condition + verification | ○ |

The "Mapping to Risk Tiers" in `nfr_checklist.md` is a guideline for a single category. After aggregation below, the tier is fixed through V6 in Section 2.

### Aggregating the Seven Categories

The seven categories are Performance, Security, Reliability, Scalability, Usability, Maintainability, Compatibility.

1. Select the **affected categories**: those the request or the spec affects. An affected category that is not mentioned is Level 0 (×)
2. Mark each affected category
3. The **NFR mark** (the V6 value) is the lowest mark among affected categories (any × → ×; else any △ → △; else ○)
4. If no category is affected, V6 is N/A
5. Categories that are not affected are only noted in the report; they do not enter any mark

If the PRD has no NFR of its own and refers to a parent PRD, judge the categories from the parent PRD's NFRs.

Report the per-category marks with the NFR mark, so one weak category stays visible. The NFR mark also counts as one requirement-level mark in Section 1.

Level 3 vs Level 2 does not change the mark. "Measurement method missing" is a quality note, written as a suggestion in the report's clarification items.
