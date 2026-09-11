# Front Matter Recommendation Report

## Summary

- **Total documents scanned**: {total_count}
- **Documents with Front Matter**: {with_fm_count}
- **Documents without Front Matter**: {without_fm_count}
- **Specs missing `impl-status`**: {specs_missing_impl_status_count} (manual completion — never auto-applied)

{recommendations_section}

## Next Steps

### Option A: Automatic Application

Run the following command to automatically add Front Matter to all documents that have none:

```
/recommend-front-matter --apply
```

**Note**: This will modify files directly. Git commit recommended before applying.

`--apply` only adds a front matter block to documents that have none. Documents that already have front matter
are left untouched, so the specs listed under "Specs Missing `impl-status`" always need the manual step in
Option B — this skill does not inspect the implementation and will not guess that value.

### Option B: Manual Application

1. Review the recommendations above
2. Copy-paste the recommended YAML blocks into your documents
3. Adjust metadata as needed (especially `depends-on`, `tags`, `category`)
4. For each spec listed as missing `impl-status`: check whether the implementation matches the spec, then add
   `impl-status: "implemented"`, `"in-progress"`, or `"not-implemented"` after its `sdd-phase` line

## Benefits of Front Matter

Adding front matter enables:

- **Structured search**: Filter documents by type, status, tags, or category
- **Cross-reference validation**: Verify `depends-on` references with `/check-spec --full`
- **Dependency tracking**: Visualize document dependencies and trace impact of changes
- **Automated tooling**: Enable better support for documentation management tools

## Important Notes

- Front Matter is **optional** (backward compatible)
- Inferred metadata may need manual adjustment
- Review recommendations before applying
- Always commit changes to Git before using `--apply`
