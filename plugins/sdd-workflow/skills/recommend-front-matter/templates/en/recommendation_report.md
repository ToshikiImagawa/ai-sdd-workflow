# Front Matter Recommendation Report

## Summary

- **Total documents scanned**: {total_count}
- **Documents with Front Matter**: {with_fm_count}
- **Documents without Front Matter**: {without_fm_count}

{recommendations_section}

## Next Steps

### Option A: Automatic Application

Run the following command to automatically add Front Matter to all documents:

```
/recommend-front-matter --apply
```

**Note**: This will modify files directly. Git commit recommended before applying.

### Option B: Manual Application

1. Review the recommendations above
2. Copy-paste the recommended YAML blocks into your documents
3. Adjust metadata as needed (especially `depends-on`, `tags`, `category`)

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
