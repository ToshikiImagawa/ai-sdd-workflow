# Detection Method

1. Load target documents
2. Extract the following elements:
   - Requirement IDs and requirement/behavior statements (PRD)
   - API definitions and behavior statements (spec)
   - Type definitions (spec)
   - Decision entries and rationale (adr)
3. Compare across documents:
   - Match by requirement ID where present
   - Compare requirement/behavior statements between PRD and spec for logical contradiction or PRD-uncovered
     new behavior
   - Compare adr decision entries against current spec elements for staleness
4. Detect and classify inconsistencies. A PRD contradiction or PRD-uncovered behavior is always reported as
   `[must]` and never auto-fixed — see `SKILL.md` § PRD ↔ spec Consistency
