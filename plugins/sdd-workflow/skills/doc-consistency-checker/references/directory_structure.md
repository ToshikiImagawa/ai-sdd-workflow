# Directory Structure

## Flat Structure

```
${SDD_ROOT}/
├── CONSTITUTION.md                        # Project constitution (top-level)
├── requirement/{feature-name}.md
└── specification/
    ├── {feature-name}_spec.md
    └── {feature-name}_design.md
```

## Hierarchical Structure

```
${SDD_ROOT}/
├── CONSTITUTION.md                        # Project constitution (top-level)
├── requirement/
│   ├── {feature-name}.md                  # Top-level feature
│   └── {parent-feature}/
│       ├── index.md                       # Parent feature overview and requirements list
│       └── {child-feature}.md             # Child feature requirements
└── specification/
    ├── {feature-name}_spec.md             # Top-level feature
    ├── {feature-name}_design.md
    └── {parent-feature}/
        ├── index_spec.md                  # Parent feature abstract specification
        ├── index_design.md                # Parent feature technical design document
        ├── {child-feature}_spec.md        # Child feature abstract specification
        └── {child-feature}_design.md      # Child feature technical design document
```
