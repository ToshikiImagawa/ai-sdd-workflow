# sdd-workflow

A unified Claude Code plugin supporting AI-driven Specification-Driven Development (AI-SDD) workflow with multi-language support.

## Overview

This plugin provides tools to prevent Vibe Coding problems and achieve high-quality implementations using specifications
as the source of truth. Supports multiple languages via `SDD_LANG` configuration.

## Supported Environments

| OS      | Support | Notes                                  |
|:--------|:-------:|:---------------------------------------|
| macOS   |    ✅    | Fully supported                        |
| Linux   |    ✅    | Fully supported                        |
| Windows |    ❌    | Not supported (see alternatives below) |

### Windows Limitations

The `session-start.sh` hook in this plugin is implemented as a bash script and does not work on Windows.

### Alternatives for Windows Users

1. **Use WSL (Windows Subsystem for Linux)** (Recommended)
    - Install WSL2 and run Claude Code within the Linux environment
    - [WSL Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install)

2. **Use Git Bash**
    - Git Bash included with Git for Windows may allow bash scripts to run
    - [Git for Windows](https://gitforwindows.org/)

### Future Support Plans

- Considering adding PowerShell version of the script
- Considering migration to cross-platform implementation (e.g., Node.js)

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

## Language Configuration

Set the language via `.sdd-config.json`:

```json
{
  "lang": "ja"
}
```

Supported languages: `en` (default), `ja`

The `SDD_LANG` environment variable is automatically set at session start from this configuration.

## Quick Start

### 1. Project Initialization

**For projects using this plugin for the first time, run `/sdd-init`.**

```
/sdd-init
```

This command automatically:

- Adds the AI-SDD Instructions section to your project's `CLAUDE.md`
- Creates the `.sdd/` directory structure (requirement/, specification/, task/)
- Generates PRD, specification, and design document template files

## Included Components

### Agents

| Agent                     | Description                                                                                                      |
|:--------------------------|:-----------------------------------------------------------------------------------------------------------------|
| `prd-reviewer`            | Reviews PRD quality and CONSTITUTION.md compliance. Generates fix proposals for violations                        |
| `spec-reviewer`           | Reviews specification quality and CONSTITUTION.md compliance. Generates fix proposals for violations              |
| `requirement-analyzer`    | SysML requirements diagram-based analysis, requirement tracking and verification                                 |
| `clarification-assistant` | Specification clarification support. Analyzes requirements across 9 categories and outputs integration proposals |

### Skills (User-Invocable)

| Skill              | Description                                                                                                  |
|:-------------------|:-------------------------------------------------------------------------------------------------------------|
| `/sdd-init`        | AI-SDD workflow initialization. CLAUDE.md setup and template generation                                      |
| `/sdd-migrate`     | Migration from legacy version (v1.x/v2.x). Migrate to new structure or generate compatibility config        |
| `/generate-spec`   | Generates an abstract specification and technical design document from input                                 |
| `/generate-prd`    | Generates a PRD (Requirements Specification) in SysML requirements diagram format from business requirements |
| `/check-spec`      | Checks consistency between implementation code and specifications, detecting discrepancies                   |
| `/task-cleanup`    | Cleans up the task/ directory after implementation, integrating design decisions                             |
| `/task-breakdown`  | Breaks down tasks from the technical design document into a list of small tasks                              |
| `/clarify`         | Scans specs across 9 categories, generates questions to clarify ambiguity                                    |
| `/implement`       | TDD-based 5-phase implementation. Tracks progress with TaskList and auto-marks in tasks.md                   |
| `/checklist`       | Auto-generates 9-category quality checklists from specs and design docs                                      |
| `/constitution`    | Defines and manages non-negotiable project principles (constitution)                                         |

### Skills (Automatic)

| Skill                     | Description                                                                                         |
|:--------------------------|:----------------------------------------------------------------------------------------------------|
| `vibe-detector`           | Analyzes user input to automatically detect Vibe Coding (vague instructions)                        |
| `doc-consistency-checker` | Automatically checks consistency between documents (PRD, spec, design)                              |

### Hooks

| Hook            | Trigger      | Description                                                                         |
|:----------------|:-------------|:------------------------------------------------------------------------------------|
| `session-start` | SessionStart | Loads settings from `.sdd-config.json` and sets environment variables automatically |

**Note**: Hooks are automatically enabled when the plugin is installed. No additional configuration is required.

## Usage

### Command Usage Examples

#### PRD Generation

```
/generate-prd A feature for users to manage tasks.
Available only to logged-in users.
```

#### Specification/Design Document Generation

```
/generate-spec User authentication feature. Supports login and logout with email and password.
```

#### Consistency Check

```
/check-spec user-auth
```

#### Task Breakdown

```
/task-breakdown task-management TICKET-123
```

#### Task Cleanup

```
/task-cleanup TICKET-123
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
/sdd-init
```

Generates project constitution (CONSTITUTION.md) and templates.

#### Step 2: Create Requirements Document (PRD)

```
/generate-prd User authentication feature. Login and logout with email and password.
Includes session management and password reset functionality.
```

→ `.sdd/requirement/user-auth.md` is generated.

#### Step 3: Generate Specification and Design Documents

```
/generate-spec user-auth
```

→ `.sdd/specification/user-auth_spec.md` and `user-auth_design.md` are generated.

#### Step 4: Clarify Specifications

```
/clarify user-auth
```

Scans specifications across 9 categories and generates questions for unclear points. Answers are automatically
integrated into specs.

#### Step 5: Task Breakdown

```
/task-breakdown user-auth TICKET-123
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
/check-spec user-auth
```

Verifies consistency between implementation and specifications, reporting any discrepancies.

#### Step 9: Task Cleanup

```
/task-cleanup TICKET-123
```

Cleans up temporary files and integrates important design decisions into `*_design.md`.

## Migration from v2.x

### Breaking Changes in v3.0.0

1. **Two plugins merged into one**: `sdd-workflow-ja` and `sdd-workflow` are now a single `sdd-workflow` plugin with multi-language support via `SDD_LANG`
2. **Commands converted to skills**: All 11 commands are now skills with hyphenated names
3. **Command name changes**: Underscores replaced with hyphens (e.g., `/sdd_init` → `/sdd-init`)

### Command Name Migration

| Old (v2.x)         | New (v3.0.0)       |
|:--------------------|:-------------------|
| `/sdd_init`         | `/sdd-init`        |
| `/generate_spec`    | `/generate-spec`   |
| `/generate_prd`     | `/generate-prd`    |
| `/check_spec`       | `/check-spec`      |
| `/task_breakdown`   | `/task-breakdown`  |
| `/task_cleanup`     | `/task-cleanup`    |
| `/sdd_migrate`      | `/sdd-migrate`     |
| `/implement`        | `/implement`       |
| `/clarify`          | `/clarify`         |
| `/constitution`     | `/constitution`    |
| `/checklist`        | `/checklist`       |

### Migration Steps

1. If using `sdd-workflow-ja`, uninstall it and install `sdd-workflow`
2. Set `"lang": "ja"` in `.sdd-config.json` for Japanese language support
3. Update any automation scripts to use new command names (hyphens instead of underscores)

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
| `SDD_LANG`               | `en`                 | Language setting                        |
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

| Skill              | Enhancement with Serena                                                                       |
|:-------------------|:----------------------------------------------------------------------------------------------|
| `/generate-spec`   | References existing code API/type definitions for consistent specification generation         |
| `/check-spec`      | Provides high-precision API implementation and signature verification via symbol-based search |
| `/task-breakdown`  | Analyzes change impact scope for accurate task dependency mapping                             |

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
/generate-prd auth/user-login   # Generate user-login PRD under auth domain
/generate-spec auth/user-login  # Generate specification under auth domain
/check-spec auth                # Check consistency for entire auth domain
```

### Project Configuration File

Place a `.sdd-config.json` file in your project root to customize directory names and language.

```json
{
  "root": ".sdd",
  "lang": "en",
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
| `lang`                      | `en`            | Language (`en` or `ja`)                    |
| `directories.requirement`   | `requirement`   | PRD (Requirements Specification) directory |
| `directories.specification` | `specification` | Specification/design document directory    |
| `directories.task`          | `task`          | Temporary task logs directory              |

**Notes**:

- If the configuration file doesn't exist, default values are used
- Partial configuration is supported (unspecified items use defaults)

## Plugin Structure

```
sdd-workflow/
├── .claude-plugin/
│   └── plugin.json                # Plugin manifest
├── agents/
│   ├── prd-reviewer.md            # PRD review and CONSTITUTION compliance agent
│   ├── spec-reviewer.md           # Specification review agent
│   ├── requirement-analyzer.md    # Requirement analysis agent
│   └── clarification-assistant.md # Specification clarification assistant
├── skills/
│   ├── sdd-init/SKILL.md          # AI-SDD workflow initialization
│   ├── constitution/SKILL.md      # Project constitution management
│   ├── generate-spec/SKILL.md     # Specification/design document generation
│   ├── generate-prd/SKILL.md      # PRD generation
│   ├── check-spec/SKILL.md        # Consistency check
│   ├── task-breakdown/SKILL.md    # Task breakdown
│   ├── implement/SKILL.md         # TDD-based implementation execution
│   ├── clarify/SKILL.md           # Specification clarification
│   ├── task-cleanup/SKILL.md      # Task cleanup
│   ├── sdd-migrate/SKILL.md       # Migration from legacy version
│   ├── checklist/SKILL.md         # Quality checklist generation
│   ├── vibe-detector/             # Vibe Coding detection skill
│   │   ├── SKILL.md
│   │   └── templates/{en,ja}/
│   ├── doc-consistency-checker/   # Document consistency checker
│   │   ├── SKILL.md
│   │   └── templates/{en,ja}/
├── hooks/
│   └── hooks.json                 # Hooks configuration
├── scripts/
│   └── session-start.sh           # Session start initialization script
├── AI-SDD-PRINCIPLES.source.md
├── LICENSE
├── README.md
└── CHANGELOG.md
```

## License

MIT License
