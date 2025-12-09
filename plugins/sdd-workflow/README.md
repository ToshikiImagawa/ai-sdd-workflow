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

**For projects using this plugin for the first time, we recommend running `/sdd_init` first.**

```
/sdd_init
```

This command automatically:

- Adds the AI-SDD Instructions section to your project's `CLAUDE.md`
- Creates the `.sdd/` directory structure (requirement/, specification/, task/)
- Generates PRD, specification, and design document template files

## Included Components

### Agents

| Agent                  | Description                                                                                                             |
|:-----------------------|:------------------------------------------------------------------------------------------------------------------------|
| `sdd-workflow`         | Manages AI-SDD development flow. Phase determination, Vibe Coding prevention, document consistency checks               |
| `spec-reviewer`        | Reviews specification quality and provides improvement suggestions. Detects ambiguous descriptions and missing sections |
| `requirement-analyzer` | SysML requirements diagram-based analysis, requirement tracking and verification                                        |

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

### Skills

| Skill                     | Description                                                                  |
|:--------------------------|:-----------------------------------------------------------------------------|
| `vibe-detector`           | Analyzes user input to automatically detect Vibe Coding (vague instructions) |
| `doc-consistency-checker` | Automatically checks consistency between documents (PRD, spec, design)       |
| `sdd-templates`           | Provides fallback templates for PRD, specification, and design documents     |

### Hooks

| Hook                  | Trigger                 | Description                                                               |
|:----------------------|:------------------------|:--------------------------------------------------------------------------|
| `session-start`       | SessionStart            | Loads settings from `.sdd-config.json` and sets environment variables    |
| `check-spec-exists`   | PreToolUse (Edit/Write) | Verifies specification existence before implementation, shows warning    |
| `check-commit-prefix` | PostToolUse (Bash)      | Checks commit message conventions                                         |

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

## Hook Configuration

To enable hooks, add the following to your project's `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "hooks/session-start.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "hooks/check-spec-exists.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "hooks/check-commit-prefix.sh"
          }
        ]
      }
    ]
  }
}
```

**Note**: Hook scripts require execute permission:

```bash
chmod +x hooks/*.sh
```

See `hooks/settings.example.json` for a configuration example.

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
├── SPECIFICATION_TEMPLATE.md     # Abstract specification template (optional)
├── DESIGN_DOC_TEMPLATE.md        # Technical design document template (optional)
├── requirement/          # PRD (Requirements Specification)
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
├── SPECIFICATION_TEMPLATE.md     # Abstract specification template (optional)
├── DESIGN_DOC_TEMPLATE.md        # Technical design document template (optional)
├── requirement/          # PRD (Requirements Specification)
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
  "docsRoot": ".sdd",
  "directories": {
    "requirement": "requirement",
    "specification": "specification",
    "task": "task"
  }
}
```

| Setting                     | Default              | Description                              |
|:----------------------------|:---------------------|:-----------------------------------------|
| `docsRoot`                  | `.sdd`              | Documentation root directory             |
| `directories.requirement`   | `requirement`| PRD (Requirements Specification) directory |
| `directories.specification` | `specification`      | Specification/design document directory  |
| `directories.task`          | `task`               | Temporary task logs directory            |

**Notes**:
- If the configuration file doesn't exist, default values are used
- Partial configuration is supported (unspecified items use defaults)
- Hook scripts (`check-spec-exists.sh`, `check-commit-prefix.sh`) also reference this configuration file (requires jq)

**Custom configuration example**:
```json
{
  "docsRoot": "docs",
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
│   └── plugin.json              # Plugin manifest
├── agents/
│   ├── sdd-workflow.md          # AI-SDD development flow agent
│   ├── spec-reviewer.md         # Specification review agent
│   └── requirement-analyzer.md  # Requirement analysis agent
├── commands/
│   ├── sdd_init.md              # AI-SDD workflow initialization
│   ├── sdd_migrate.md           # Migration from legacy version
│   ├── generate_spec.md         # Specification/design document generation
│   ├── generate_prd.md          # PRD generation
│   ├── check_spec.md            # Consistency check
│   ├── task_cleanup.md          # Task cleanup
│   └── task_breakdown.md        # Task breakdown
├── skills/
│   ├── vibe-detector/           # Vibe Coding detection skill
│   │   ├── SKILL.md
│   │   └── templates/
│   ├── doc-consistency-checker/ # Document consistency checker
│   │   ├── SKILL.md
│   │   └── templates/
│   └── sdd-templates/           # AI-SDD templates
│       ├── SKILL.md
│       └── templates/
├── hooks/
│   ├── session-start.sh         # Session start initialization
│   ├── check-spec-exists.sh     # Specification existence check
│   ├── check-commit-prefix.sh   # Commit prefix check
│   └── settings.example.json    # Hooks configuration example
├── LICENSE
└── README.md
```

## Commit Message Convention

| Prefix     | Usage                                       |
|:-----------|:--------------------------------------------|
| `[docs]`   | Add/update documentation                    |
| `[spec]`   | Add/update specifications (`*_spec.md`)     |
| `[design]` | Add/update design documents (`*_design.md`) |

## License

MIT License
