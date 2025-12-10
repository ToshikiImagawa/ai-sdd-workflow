---
name: sdd-templates
description: "Provides fallback templates for AI-SDD documents. Use only when project templates do not exist in .sdd/ directory."
allowed-tools: Read, Glob
---

# SDD Templates - AI-SDD Document Templates (Fallback)

Provides templates for various documents used in the AI-SDD workflow.

## Important: Template Selection Procedure

**These templates are fallbacks. You MUST follow the procedure below.**

### Required Verification Steps

When generating documents, **always search for templates in this order**:

```
1. Check for project templates (HIGHEST PRIORITY)
   ├─ Does .sdd/PRD_TEMPLATE.md exist?
   ├─ Does .sdd/SPECIFICATION_TEMPLATE.md exist?
   └─ Does .sdd/DESIGN_DOC_TEMPLATE.md exist?
   ↓
2. If project template EXISTS
   → Use that template (DO NOT use this skill's templates)
   ↓
3. ONLY if project template does NOT exist
   → Use this skill's templates to generate project-specific templates
```

### Template Priority (STRICTLY ENFORCED)

| Priority         | Template          | Path                      | Usage Condition                         |
|:-----------------|:------------------|:--------------------------|:----------------------------------------|
| **1 (Highest)**  | Project templates | `.sdd/*.md`               | Use if exists                           |
| **2 (Fallback)** | Plugin templates  | This skill's `templates/` | ONLY when project templates don't exist |

## Prerequisites

**Before execution, you must read `sdd-workflow:sdd-workflow` agent content to understand AI-SDD principles.**

This skill provides templates that follow the sdd-workflow agent principles.

### Directory Path Resolution

**Use `SDD_*` environment variables to resolve directory paths.**

| Environment Variable     | Default Value         | Description                  |
|:-------------------------|:----------------------|:-----------------------------|
| `SDD_ROOT`          | `.sdd`                | Root directory               |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`    | PRD/Requirements directory   |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification`  | Specification/Design directory |
| `SDD_TASK_PATH`          | `.sdd/task`           | Task log directory           |

**Path Resolution Priority:**
1. Use `SDD_*` environment variables if set
2. Check `.sdd-config.json` if environment variables are not set
3. Use default values if neither exists

When generating templates, adjust paths within templates based on the environment variables or configuration file's directory names.

## Fallback Templates

Used only when project templates do not exist:

| Template                             | File                                                         | Corresponding Project Template   |
|:-------------------------------------|:-------------------------------------------------------------|:---------------------------------|
| **PRD (Requirements Specification)** | [templates/prd_template.md](templates/prd_template.md)       | `.sdd/PRD_TEMPLATE.md`           |
| **Abstract Specification**           | [templates/spec_template.md](templates/spec_template.md)     | `.sdd/SPECIFICATION_TEMPLATE.md` |
| **Technical Design Doc**             | [templates/design_template.md](templates/design_template.md) | `.sdd/DESIGN_DOC_TEMPLATE.md`    |

## Usage

### Case 1: Project Template EXISTS

```
/generate_spec {specifications}

1. Check .sdd/SPECIFICATION_TEMPLATE.md
2. EXISTS → Use that template
3. DO NOT reference this skill's templates
```

### Case 2: Project Template Does NOT Exist

```
/generate_spec {specifications}

1. Check .sdd/SPECIFICATION_TEMPLATE.md
2. Does NOT exist → Use this skill's templates
3. Customize according to project's language and structure
4. Recommend saving to .sdd/ as project template after generation
```

### Initializing Project Templates

If your project has no templates, initialize with these steps:

1. Copy this skill's templates to `.sdd/`
2. Modify type definition syntax to match project's programming language
3. Adjust paths to match project's directory structure
4. Project templates will take priority thereafter

## Template Overview

### PRD (Requirements Specification) Template

Defines the following in SysML Requirements Diagram format:

- Background and Purpose
- User Requirements (UR-xxx)
- Functional Requirements (FR-xxx)
- Non-Functional Requirements (NFR-xxx)
- Requirements Diagram (Mermaid)
- Constraints and Assumptions

### Abstract Specification Template

Defines the logical structure of the system:

- Background and Overview
- Functional Requirements (with PRD requirement ID mapping)
- Public API (SysML bdd format)
- Data Model
- Behavior (Sequence Diagrams)

### Technical Design Doc Template

Defines concrete implementation plans:

- Implementation Status
- Design Goals
- Technology Stack
- Architecture
- Design Decisions and Rationale

## Document Dependencies

```mermaid
graph RL
    IMPL[Implementation] --> DESIGN["*_design.md<br/>(Technical Design)"]
    DESIGN --> SPEC["*_spec.md<br/>(Abstract Spec)"]
    SPEC --> PRD["requirement/<br/>(PRD/Requirements)"]
```

Each template is designed to ensure traceability based on this dependency relationship.

## Notes

- Templates are **structural guidelines**; not all sections are mandatory
- Select necessary sections according to project scale and nature
- Manage requirement IDs (UR-xxx, FR-xxx, NFR-xxx) uniquely and enable cross-document references
