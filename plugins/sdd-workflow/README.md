# sdd-workflow

A Claude Code plugin supporting AI-driven Specification-Driven Development (AI-SDD) workflow.

## Overview

This plugin provides tools to prevent Vibe Coding problems and achieve high-quality implementations using specifications
as the source of truth.

### What is Vibe Coding?

Vibe Coding occurs when AI must guess thousands of undefined requirements due to vague instructions.
This plugin solves this problem by providing a specification-centered development flow.

## Installation

### Method 1: Install from Marketplace (Recommended)

Run the following in Claude Code:

```
/plugin marketplace add ToshikiImagawa/ai-sdd-workflow
```

Then install the plugin:

```
/plugin install sdd-workflow@ToshikiImagawa/ai-sdd-workflow
```

### Method 2: Clone from GitHub

```bash
git clone https://github.com/ToshikiImagawa/ai-sdd-workflow.git ~/.claude/plugins/sdd-workflow
```

After installation, restart Claude Code.

### Verification

Run the `/plugin` command in Claude Code and verify that `sdd-workflow` is displayed.

## Quick Start

### 1. Project Initialization

**For projects using this plugin for the first time, run `/sdd_init`.**

```
/sdd_init
```

This command automatically:

- Adds the AI-SDD Instructions section to your project's `CLAUDE.md`
- Creates the `.sdd/` directory structure (requirement/, specification/, task/)
- Generates PRD, specification, and design document template files

## Included Components

### Agents

| Agent                     | Description                                                                                                             |
|:--------------------------|:------------------------------------------------------------------------------------------------------------------------|
| `sdd-workflow`            | Manages AI-SDD development flow. Phase determination, Vibe Coding prevention, document consistency checks               |
| `prd-reviewer`            | Reviews PRD quality and CONSTITUTION.md compliance. Attempts auto-fix on violations                                     |
| `spec-reviewer`           | Reviews specification quality and CONSTITUTION.md compliance. Attempts auto-fix on violations                           |
| `requirement-analyzer`    | SysML requirements diagram-based analysis, requirement tracking and verification                                        |
| `clarification-assistant` | Specification clarification support. Analyzes requirements across 9 categories and integrates answers into specs        |

### Commands

| Command           | Description                                                                                                  |
|:------------------|:-------------------------------------------------------------------------------------------------------------|
| `/sdd_init`       | AI-SDD workflow initialization. CLAUDE.md setup and template generation                                      |
| `/sdd_migrate`    | Migration from legacy version (v1.x). Migrate to new structure or generate compatibility config              |
| `/generate_spec`  | Generates an abstract specification and technical design document from input                                 |
| `/generate_prd`   | Generates a PRD (Requirements Specification) in SysML requirements diagram format from business requirements |
| `/check_spec`     | Checks consistency between implementation code and specifications, detecting discrepancies                   |
| `/task_cleanup`   | Cleans up the task/ directory after implementation, integrating design decisions                             |
| `/task_breakdown` | Breaks down tasks from the technical design document into a list of small tasks                              |
| `/clarify`        | Scans specs across 9 categories, generates questions to clarify ambiguity                                    |
| `/implement`      | TDD-based 5-phase implementation execution with automatic progress marking in tasks.md                       |
| `/checklist`      | Auto-generates 9-category quality checklists from specs and design docs                                      |
| `/constitution`   | Defines and manages non-negotiable project principles (constitution)                                         |

### Skills

| Skill                     | Description                                                                                         |
|:--------------------------|:----------------------------------------------------------------------------------------------------|
| `vibe-detector`           | Analyzes user input to automatically detect Vibe Coding (vague instructions)                        |
| `doc-consistency-checker` | Automatically checks consistency between documents (PRD, spec, design)                              |
| `sdd-templates`           | Provides fallback templates for PRD, spec, design, checklist, constitution, and implementation logs |

### Hooks

| Hook            | Trigger      | Description                                                                         |
|:----------------|:-------------|:------------------------------------------------------------------------------------|
| `session-start` | SessionStart | Loads settings from `.sdd-config.json` and sets environment variables automatically |

**Note**: Hooks are automatically enabled when the plugin is installed. No additional configuration is required.

## Usage

### sdd-workflow Agent

The agent automatically performs the following when a task starts:

1. **Phase Determination**: Identifies required phases based on task nature
2. **Vibe Coding Prevention**: Detects vague instructions and promotes specification clarification
3. **Document Management**: Guides specification/design document creation and updates

### Command Usage Examples

#### PRD Generation

```
/generate_prd A feature for users to manage tasks.
Available only to logged-in users.
```

#### Specification/Design Document Generation

```
/generate_spec User authentication feature. Supports login and logout with email and password.
```

#### Consistency Check

```
/check_spec user-auth
```

#### Task Breakdown

```
/task_breakdown task-management TICKET-123
```

#### Task Cleanup

```
/task_cleanup TICKET-123
```

#### Specification Clarification

```
/clarify user-auth
```

Scans specifications across 9 categories and generates up to 5 clarification questions.

#### TDD-based Implementation

```
/implement user-auth TICKET-123
```

Executes implementation in 5 phases (Setup→Tests→Core→Integration→Polish) and auto-marks progress in tasks.md.

#### Quality Checklist Generation

```
/checklist user-auth TICKET-123
```

Auto-generates 9-category quality checklists from specifications and design documents.

#### Project Constitution Management

```
/constitution show                    # Display current constitution
/constitution add "Library-First"     # Add a new principle
/constitution validate                # Verify specs/designs comply with constitution
```

Defines and manages non-negotiable project principles. Use `/constitution init` to create the constitution file
initially.

### Complete Workflow Example

Here's a complete workflow for implementing a new "User Authentication" feature.

#### Step 1: Project Initialization (First Time Only)

```
/sdd_init
```

Generates project constitution (CONSTITUTION.md) and templates.

#### Step 2: Create Requirements Document (PRD)

```
/generate_prd User authentication feature. Login and logout with email and password.
Includes session management and password reset functionality.
```

→ `.sdd/requirement/user-auth.md` is generated.

#### Step 3: Generate Specification and Design Documents

```
/generate_spec user-auth
```

→ `.sdd/specification/user-auth_spec.md` and `user-auth_design.md` are generated.

#### Step 4: Clarify Specifications

```
/clarify user-auth
```

Scans specifications across 9 categories and generates questions for unclear points. Answers are automatically integrated into specs.

#### Step 5: Task Breakdown

```
/task_breakdown user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/tasks.md` is generated with the task list.

#### Step 6: Generate Quality Checklist

```
/checklist user-auth TICKET-123
```

→ `.sdd/task/TICKET-123/checklist.md` is generated with 9-category quality checklist.

#### Step 7: TDD-based Implementation

```
/implement user-auth TICKET-123
```

Proceeds through 5 phases (Setup→Tests→Core→Integration→Polish) with automatic progress marking.

#### Step 8: Consistency Check

```
/check_spec user-auth
```

Verifies consistency between implementation and specifications, reporting any discrepancies.

#### Step 9: Task Cleanup

```
/task_cleanup TICKET-123
```

Cleans up temporary files and integrates important design decisions into `*_design.md`.

## About Hooks

This plugin automatically loads `.sdd-config.json` and sets environment variables at session start.
**Hooks are automatically enabled when the plugin is installed. No additional configuration is required.**

### Hook Behavior

| Hook            | Trigger      | Description                                                           |
|:----------------|:-------------|:----------------------------------------------------------------------|
| `session-start` | SessionStart | Loads settings from `.sdd-config.json` and sets environment variables |

### Environment Variables Set

The following environment variables are automatically set at session start:

| Environment Variable     | Default              | Description                             |
|:-------------------------|:---------------------|:----------------------------------------|
| `SDD_ROOT`               | `.sdd`               | Root directory                          |
| `SDD_REQUIREMENT_DIR`    | `requirement`        | Requirements specification directory    |
| `SDD_SPECIFICATION_DIR`  | `specification`      | Specification/design document directory |
| `SDD_TASK_DIR`           | `task`               | Task log directory                      |
| `SDD_REQUIREMENT_PATH`   | `.sdd/requirement`   | Requirements specification full path    |
| `SDD_SPECIFICATION_PATH` | `.sdd/specification` | Specification/design document full path |
| `SDD_TASK_PATH`          | `.sdd/task`          | Task log full path                      |

### Hook Debugging

To check hook registration status:

```bash
claude --debug
```

## Serena MCP Integration (Optional)

Configure [Serena](https://github.com/oraios/serena) MCP to enable enhanced functionality through semantic code
analysis.

### What is Serena?

Serena is a semantic code analysis tool based on LSP (Language Server Protocol) that supports 30+ programming languages.
It enables symbol-level code search and analysis.

### Configuration

Add the following to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        ".",
        "--enable-web-dashboard",
        "false"
      ]
    }
  }
}
```

### Enhanced Features

| Command           | Enhancement with Serena                                                                       |
|:------------------|:----------------------------------------------------------------------------------------------|
| `/generate_spec`  | References existing code API/type definitions for consistent specification generation         |
| `/check_spec`     | Provides high-precision API implementation and signature verification via symbol-based search |
| `/task_breakdown` | Analyzes change impact scope for accurate task dependency mapping                             |

### Without Serena

All features work without Serena. Text-based search (Grep/Glob) is used for analysis and works language-agnostically.

## AI-SDD Development Flow

```
Specify → Plan → Tasks → Implement & Review
```

### Recommended Directory Structure

Both flat and hierarchical structures are supported.

#### Flat Structure (for small to medium projects)

```
.sdd/
├── CONSTITUTION.md               # Project constitution (highest level)
├── PRD_TEMPLATE.md               # PRD template (optional)
├── SPECIFICATION_TEMPLATE.md     # Abstract specification template (optional)
├── DESIGN_DOC_TEMPLATE.md        # Technical design document template (optional)
├── requirement/                  # PRD (Requirements Specification)
│   └── {feature-name}.md
├── specification/                # Persistent knowledge assets
│   ├── {feature-name}_spec.md    # Abstract specification
│   └── {feature-name}_design.md  # Technical design document
└── task/                         # Temporary task logs (deleted after implementation)
    └── {ticket-number}/
```

#### Hierarchical Structure (for medium to large projects)

```
.sdd/
├── CONSTITUTION.md               # Project constitution (highest level)
├── PRD_TEMPLATE.md               # PRD template (optional)
├── SPECIFICATION_TEMPLATE.md     # Abstract specification template (optional)
├── DESIGN_DOC_TEMPLATE.md        # Technical design document template (optional)
├── requirement/                  # PRD (Requirements Specification)
│   ├── {feature-name}.md         # Top-level feature (backward compatible with flat structure)
│   └── {parent-feature}/         # Parent feature directory
│       ├── index.md              # Parent feature overview and requirements list
│       └── {child-feature}.md    # Child feature requirements
├── specification/                # Persistent knowledge assets
│   ├── {feature-name}_spec.md    # Top-level feature (backward compatible with flat structure)
│   ├── {feature-name}_design.md
│   └── {parent-feature}/         # Parent feature directory
│       ├── index_spec.md         # Parent feature abstract specification
│       ├── index_design.md       # Parent feature technical design document
│       ├── {child-feature}_spec.md   # Child feature abstract specification
│       └── {child-feature}_design.md # Child feature technical design document
└── task/                         # Temporary task logs (deleted after implementation)
    └── {ticket-number}/
```

#### Document Dependencies

```
CONSTITUTION.md → requirement/ → *_spec.md → *_design.md → task/ → Implementation
```

All documents are created following `CONSTITUTION.md` project principles.

**Hierarchical structure usage examples**:

```
/generate_prd auth/user-login   # Generate user-login PRD under auth domain
/generate_spec auth/user-login  # Generate specification under auth domain
/check_spec auth                # Check consistency for entire auth domain
```

### Project Configuration File

Place a `.sdd-config.json` file in your project root to customize directory names.

```json
{
  "root": ".sdd",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
```

| Setting                     | Default         | Description                                |
|:----------------------------|:----------------|:-------------------------------------------|
| `root`                      | `.sdd`          | Root directory                             |
| `directories.requirement`   | `requirement`   | PRD (Requirements Specification) directory |
| `directories.specification` | `specification` | Specification/design document directory    |
| `directories.task`          | `task`          | Temporary task logs directory              |

**Notes**:

- If the configuration file doesn't exist, default values are used
- Partial configuration is supported (unspecified items use defaults)

**Custom configuration example**:

```json
{
  "root": "docs",
  "directories": {
    "requirement": "requirements",
    "specification": "specs"
  }
}
```

This configuration results in the following directory structure:

```
docs/
├── requirements/       # PRD (Requirements Specification)
├── specs/              # Specification/design documents
└── task/               # Temporary task logs (default value)
```

## Plugin Structure

```
sdd-workflow/
├── .claude-plugin/
│   └── plugin.json                # Plugin manifest
├── agents/
│   ├── sdd-workflow.md            # AI-SDD development flow agent
│   ├── prd-reviewer.md            # PRD review and CONSTITUTION compliance agent
│   ├── spec-reviewer.md           # Specification review agent
│   ├── requirement-analyzer.md    # Requirement analysis agent
│   └── clarification-assistant.md # Specification clarification assistant
├── commands/
│   ├── sdd_init.md                # AI-SDD workflow initialization
│   ├── sdd_migrate.md             # Migration from legacy version
│   ├── generate_spec.md           # Specification/design document generation
│   ├── generate_prd.md            # PRD generation
│   ├── check_spec.md              # Consistency check
│   ├── task_cleanup.md            # Task cleanup
│   ├── task_breakdown.md          # Task breakdown
│   ├── clarify.md                 # Specification clarification
│   ├── implement.md               # TDD-based implementation execution
│   ├── checklist.md               # Quality checklist generation
│   └── constitution.md            # Project constitution management
├── skills/
│   ├── vibe-detector/             # Vibe Coding detection skill
│   │   ├── SKILL.md
│   │   └── templates/
│   ├── doc-consistency-checker/   # Document consistency checker
│   │   ├── SKILL.md
│   │   └── templates/
│   └── sdd-templates/             # AI-SDD templates
│       ├── SKILL.md
│       └── templates/
│           ├── prd_template.md
│           ├── spec_template.md
│           ├── design_template.md
│           ├── checklist_template.md
│           ├── constitution_template.md
│           └── implementation_log_template.md
├── hooks/
│   └── hooks.json                 # Hooks configuration
├── scripts/
│   └── session-start.sh           # Session start initialization script
├── LICENSE
└── README.md
```

## License

MIT License
