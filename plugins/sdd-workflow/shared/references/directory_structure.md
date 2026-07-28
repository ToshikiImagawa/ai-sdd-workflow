# Directory Structure

Requirement diagrams support both flat and hierarchical structures.

## Flat Structure

    {root}/{requirement}/
    └── {feature-name}.md

## Hierarchical Structure

    {root}/{requirement}/
    ├── {feature-name}.md           # Top-level feature
    └── {parent-feature}/           # Parent feature directory
        ├── index.md                # Parent feature overview & requirements list
        └── {child-feature}.md      # Child feature requirements

* `{root}` and `{requirement}` use `.sdd-config.json` configuration values, or default values (`.sdd` / `requirement`)
