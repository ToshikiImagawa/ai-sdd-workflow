## Application Results

- **Success**: {success_count} files updated
- **Skipped**: {skip_count} files (already have front matter)
- **Failed**: {error_count} files
- **Specs still missing `impl-status`**: {specs_missing_impl_status_count} (not written by this skill — see below)

### Updated Files

{updated_files_list}

### Specs Needing `impl-status` (manual)

{specs_missing_impl_status_list}

This skill never writes `impl-status`: it does not inspect the implementation, and a wrong `"not-implemented"`
would hide a regression instead of reporting it. Check each spec against the implementation, then add
`impl-status: "implemented"`, `"in-progress"`, or `"not-implemented"` after its `sdd-phase` line.

### Next Steps

1. Review the updated files
2. Adjust metadata as needed (priority, risk, tags, category)
3. Add `impl-status` by hand to the specs listed above
4. Commit changes:
   ```bash
   git add .
   git commit -m "[docs] Add Front Matter to existing documents"
   ```
