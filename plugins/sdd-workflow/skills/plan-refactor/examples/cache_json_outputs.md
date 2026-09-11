# Cache JSON Output Examples

Example contents of the intermediate JSON files written to `${SDD_ROOT}/.cache/plan-refactor/` by the
`plan-refactor` scripts.

## existing-docs.json

Written by `scripts/scan-existing-docs.py`:

```json
{
  "prd_exists": true,
  "spec_exists": true,
  "design_draft_exists": false,
  "legacy_design_exists": false,
  "prd_path": ".sdd/requirement/auth.md",
  "spec_path": ".sdd/specification/auth_spec.md",
  "design_draft_path": "",
  "legacy_design_path": "",
  "structure": "flat",
  "feature_name": "auth",
  "ticket_number": "68",
  "case": "A"
}
```

Field notes:

| Field                  | Meaning                                                                                                                    |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------|
| `spec_exists`          | Decides the case. Matched with **and** without the `_spec` suffix (`auth_spec.md`, then `auth.md`)                          |
| `case`                 | `"A"` when `spec_exists` is true, `"B"` otherwise. Never derived from a design document                                     |
| `design_draft_exists`  | `task/{ticket-number}/design-draft.md`. Supplementary input for Case A; only checked when a ticket number was passed        |
| `legacy_design_exists` | A `specification/{feature}_design.md` left over from v4.x. Reading context only — never a case signal, never a write target |

With no spec and no design draft (a legacy, undocumented feature), the same scan yields Case B:

```json
{
  "prd_exists": false,
  "spec_exists": false,
  "design_draft_exists": false,
  "legacy_design_exists": false,
  "prd_path": "",
  "spec_path": "",
  "design_draft_path": "",
  "legacy_design_path": "",
  "structure": "none",
  "feature_name": "user-profile",
  "ticket_number": "68",
  "case": "B"
}
```

## implementation-files.json

Written by `scripts/find-implementation-files.py`:

```json
{
  "feature_name": "auth",
  "file_count": 8,
  "scope_dir": "src/",
  "files_list_path": ".sdd/.cache/plan-refactor/all-files.txt"
}
```
