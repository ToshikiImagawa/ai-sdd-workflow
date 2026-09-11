# Directory Structure

**Persistence** (see `SKILL.md` for the checks that apply): `requirement/` and `specification/` are persistent;
`adr/` is persistent and append-only; `task/` (including `design-draft.md`) is temporary, deleted after
implementation. Inside `specification/` the `_spec` suffix is **optional**: `{feature-name}.md` and
`{feature-name}_spec.md` are both valid names for the same document.

## Flat Structure

```
${SDD_ROOT}/
├── CONSTITUTION.md                        # Project constitution (top-level)
├── requirement/{feature-name}.md
├── specification/
│   └── {feature-name}_spec.md             # Abstract specification (`{feature-name}.md` without the suffix is equally valid)
├── adr/
│   └── {feature-name}.md                  # Decision log
└── task/
    └── {ticket-number}/
        └── design-draft.md                # Technical design draft
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
├── specification/
│   ├── {feature-name}_spec.md             # Top-level feature abstract specification (`{feature-name}.md` is equally valid)
│   └── {parent-feature}/
│       ├── index_spec.md                  # Parent feature abstract specification (`index.md` is equally valid)
│       └── {child-feature}_spec.md        # Child feature abstract specification (`{child-feature}.md` is equally valid)
├── adr/
│   ├── {feature-name}.md                  # Top-level feature decision log
│   └── {parent-feature}/
│       ├── index.md                       # Parent feature decision log
│       └── {child-feature}.md             # Child feature decision log
└── task/
    └── {ticket-number}/
        └── design-draft.md                # Technical design draft
```
