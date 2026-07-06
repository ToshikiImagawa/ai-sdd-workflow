# Cache JSON Output Examples

Example contents of the intermediate JSON files written to `.sdd/.cache/plan-refactor/` by the
`plan-refactor` scripts.

## existing-docs.json

Written by `scripts/scan-existing-docs.sh`:

```json
{
  "prd_exists": true,
  "spec_exists": true,
  "design_exists": true,
  "prd_path": ".sdd/requirement/auth.md",
  "spec_path": ".sdd/specification/auth_spec.md",
  "design_path": ".sdd/specification/auth_design.md",
  "structure": "flat",
  "feature_name": "auth"
}
```

## implementation-files.json

Written by `scripts/find-implementation-files.sh`:

```json
{
  "feature_name": "auth",
  "file_count": 8,
  "scope_dir": "src/",
  "files_list_path": ".sdd/.cache/plan-refactor/all-files.txt"
}
```
