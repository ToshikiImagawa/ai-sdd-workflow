# Laws Draft Report: {{FEATURE}}

- Spec: {{SPEC_PATH}} (`{{SPEC_ID}}`)
- Output: {{OUTPUT_FILE}}
- Generated: {{DATE}}
- `laws.max_laws`: {{MAX_LAWS}}

## Adopted laws

| Law | Source | Proposition |
|:--|:--|:--|
| {{LAW_NAME}} | §{{SECTION}} | {{DESCRIPTION}} |

## Model API

Functions the reference model must implement (copied from the `# model-api:` lines of the law file; the `model` stage follows these). Write types in Bend's notation (a list is `List<&2, T>`); declare `for` variables one per line.

Fixed by: `{{MODEL_API_SOURCE}}` (`spec` / `main.bend` / `unfixed`; `unfixed` means "unfixed - needs confirmation": a human confirms the API at approval).

| Function | Arguments | Returns | Encoding notes |
|:--|:--|:--|:--|
| Model.{{FN}} | {{ARGS}} | {{RETURNS}} | {{ENCODING}} |

## Candidates routed to differential tests

Point assertions (no `for` quantifier; one decision-table row each). Written to `{{TESTS_TARGET}}` and asserted against the implementation (`impl-of:` {{IMPL_PATHS}}), not against the reference model. Run them with the project's `pytest`. An existing test file is not overwritten: the diff is shown below instead.

| Candidate | Source | Test function | Proposition |
|:--|:--|:--|:--|
| {{CANDIDATE}} | §{{SECTION}} | {{SUGGESTED_TEST}} | {{DESCRIPTION}} |

## Rejected candidates

| Candidate | Source | Reason (limit / trivial / duplicate / unbounded_nat) |
|:--|:--|:--|
| {{CANDIDATE}} | §{{SECTION}} | {{REASON}} |

## Sections not turned into laws

| Section | Reason (IO-dependent / performance / prose only / no section number / prose_implementation) |
|:--|:--|
| §{{SECTION}} | {{REASON}} |

## Static check

`draft_laws.py check` result (law file and `--tests`): {{ERRORS}} error(s), {{WARNINGS}} warning(s).

| Code | Severity | Law | Message |
|:--|:--|:--|:--|
| {{CODE}} | {{SEVERITY}} | {{LAW}} | {{MESSAGE}} |

## Next steps (done by a human)

1. Review the laws, then add the approval line at the end of the leading comment block of the law file (above the first `import`):
   `# approved: YYYY-MM-DD <approver> sha256:{{CURRENT_HASH}}`
   (current content hash: `{{CURRENT_HASH}}`; get it again with `run-verification.py proof --print-laws-hash --laws-dir {{LAWS_DIR}}`)
2. Proposed front matter for the spec (not applied; add it yourself). Until `laws:` is added, the proof gate reports orphan laws (FAIL, table row #4) before it reaches the unapproved check (SKIPPED, row #5):
   ```yaml
   laws: ["{{LAWS_DIR_SDD_RELATIVE}}"]
   laws-status: drafted
   ```
3. After approval set `laws-status: approved`; then run `/draft-laws model {{FEATURE}}`.
4. Verify with `/run-checklist {{FEATURE}} <ticket> --category proof`; after PASS a human sets `laws-status: proven`.
5. Run the differential tests (`pytest {{TESTS_TARGET}}`); they are independent of the proof gate and check the implementation.
6. Implementation location: `{{IMPL_SOURCE}}`. {{IMPL_OF_PROPOSAL}}
