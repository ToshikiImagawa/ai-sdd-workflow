# Laws Migration Report: {{FEATURE}}

- Spec: {{SPEC_PATH}} (`{{SPEC_ID}}`)
- Law file: {{LAWS_FILE}} (approval: `{{APPROVAL_STATE}}`)
- Generated: {{DATE}} by `/draft-laws migrate` (read-only: nothing under the laws directory or the spec was changed)
- Differential test target: `{{TESTS_TARGET}}`

## Implementation location (spec 3.1.5)

| Source | Paths | Lawifiable | Reason |
|:--|:--|:--|:--|
| `{{IMPL_SOURCE}}` | {{IMPL_PATHS}} | {{LAWIFIABLE}} | {{IMPL_REASON}} |

{{IMPL_OF_PROPOSAL}}

## Classification

| Law | Source | Class | `for` | Kind guess | Suggested test | Note |
|:--|:--|:--|:--|:--|:--|:--|
| {{LAW_NAME}} | §{{SECTION}} | {{CLASSIFICATION}} | {{HAS_FOR}} | {{KIND_GUESS}} | {{SUGGESTED_TEST}} | {{NOTE}} |

Totals: keep {{KEEP}} / to_tests {{TO_TESTS}} / prose_delete {{PROSE_DELETE}}

{{HUMAN_REVIEW_NOTE}}

## Human steps

| Class | What to do |
|:--|:--|
| `keep` | Nothing. The law stays in `LAWS.bend` and is proved by the proof gate. |
| `to_tests` | Write the differential test (`/draft-laws draft` routes the same proposition there; or copy the row into `{{TESTS_TARGET}}` with its `# source:` line), run `pytest`, then delete the law from `LAWS.bend`. The body changes, so the approval expires: rewrite the `# approved:` line with the new hash (`run-verification.py proof --print-laws-hash --laws-dir {{LAWS_DIR}}`) and update `PROOF.bend`. An empty-input / single-element / identity law listed here stays in Bend instead (FR-014 exemption). |
| `prose_delete` | The implementation is prose, so the laws cannot be tied to code: remove the laws directory, drop `laws:` / `laws-status` from the spec front matter, and record the reason (`prose_implementation`) in the ADR. The property itself belongs in skill evaluation, not in Bend. |
