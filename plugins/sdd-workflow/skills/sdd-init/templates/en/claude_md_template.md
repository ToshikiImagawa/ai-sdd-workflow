## AI-SDD Instructions (v{PLUGIN_VERSION})

<!-- sdd-workflow version: "{PLUGIN_VERSION}" -->

This project follows AI-SDD (AI-driven Specification-Driven Development) workflow.

### Document Operations

When operating files under `.sdd/` directory, refer to `.sdd/AI-SDD-PRINCIPLES.md` to ensure proper AI-SDD workflow compliance.

**Trigger Conditions**:

- Reading or modifying files under `.sdd/`
- Creating new specifications, design docs, or requirement docs
- Implementing features that reference `.sdd/` documents

### Directory Structure

Supports both flat and hierarchical structures.

**Flat Structure (for small to medium projects)**:

    .sdd/
    |- CONSTITUTION.md               # Project principles (top-level)
    |- PRD_TEMPLATE.md               # PRD template for this project
    |- SPECIFICATION_TEMPLATE.md     # Abstract specification template
    |- DESIGN_DOC_TEMPLATE.md        # Technical design template
    |- requirement/                  # PRD (Product Requirements Documents)
    |   |- {feature-name}.md
    |- specification/                # Specifications and designs
    |   |- {feature-name}_spec.md    # Abstract specification
    |   |- {feature-name}_design.md  # Technical design
    |- task/                         # Temporary task logs
        |- {ticket-number}/

**Hierarchical Structure (for medium to large projects)**:

    .sdd/
    |- CONSTITUTION.md               # Project principles (top-level)
    |- PRD_TEMPLATE.md               # PRD template for this project
    |- SPECIFICATION_TEMPLATE.md     # Abstract specification template
    |- DESIGN_DOC_TEMPLATE.md        # Technical design template
    |- requirement/                  # PRD (Product Requirements Documents)
    |   |- {feature-name}.md         # Top-level feature
    |   |- {parent-feature}/         # Parent feature directory
    |       |- index.md              # Parent feature overview & requirements list
    |       |- {child-feature}.md    # Child feature requirements
    |- specification/                # Specifications and designs
    |   |- {feature-name}_spec.md    # Top-level feature
    |   |- {feature-name}_design.md
    |   |- {parent-feature}/         # Parent feature directory
    |       |- index_spec.md         # Parent feature abstract spec
    |       |- index_design.md       # Parent feature technical design
    |       |- {child-feature}_spec.md   # Child feature abstract spec
    |       |- {child-feature}_design.md # Child feature technical design
    |- task/                         # Temporary task logs
        |- {ticket-number}/

### File Naming Convention (Important)

**Warning: The presence of suffixes differs between requirement and specification. Do not confuse them.**

| Directory         | File Type        | Naming Pattern                                 | Example                                   |
|:------------------|:-----------------|:-----------------------------------------------|:------------------------------------------|
| **requirement**   | All files        | `{name}.md` (no suffix)                        | `user-login.md`, `index.md`               |
| **specification** | Abstract spec    | `{name}_spec.md` (`_spec` suffix required)     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | Technical design | `{name}_design.md` (`_design` suffix required) | `user-login_design.md`, `index_design.md` |

#### Naming Pattern Quick Reference

```
# Correct Naming
requirement/auth/index.md              # Parent feature overview (no suffix)
requirement/auth/user-login.md         # Child feature requirements (no suffix)
specification/auth/index_spec.md       # Parent feature abstract spec (_spec required)
specification/auth/index_design.md     # Parent feature technical design (_design required)
specification/auth/user-login_spec.md  # Child feature abstract spec (_spec required)
specification/auth/user-login_design.md # Child feature technical design (_design required)

# Incorrect Naming (never use these)
requirement/auth/index_spec.md         # requirement doesn't need _spec
specification/auth/user-login.md       # specification requires _spec/_design
specification/auth/index.md            # specification requires _spec/_design
```

### Document Link Convention

Follow these formats for markdown links within documents:

| Link Target    | Format                                     | Link Text             | Example                                              |
|:---------------|:-------------------------------------------|:----------------------|:-----------------------------------------------------|
| **File**       | `[filename.md](path or URL)`               | Include filename      | `[user-login.md](../requirement/auth/user-login.md)` |
| **Directory**  | `[directory-name](path or URL/index.md)`   | Directory name only   | `[auth](../requirement/auth/index.md)`               |

This convention makes it visually clear whether the link target is a file or directory.
