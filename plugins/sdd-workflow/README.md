# sdd-workflow

A Claude Code plugin supporting AI-driven Specification-Driven Development (AI-SDD) workflow.

## Overview

This plugin provides tools to prevent Vibe Coding problems and achieve high-quality implementations using specifications as the source of truth.

### What is Vibe Coding?

The problem where AI must guess thousands of undefined requirements due to vague instructions.
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

Run `/plugin` command in Claude Code and verify that `sdd-workflow` is displayed.

## Included Components

### Agents

| Agent | Description |
|:---|:---|
| `sdd-workflow` | AI-SDD development flow management. Phase determination, Vibe Coding prevention, document consistency checks |
| `spec-reviewer` | Specification quality review and improvement suggestions. Ambiguous description detection, missing section identification |

### Commands

| Command | Description |
|:---|:---|
| `/generate_spec` | Generate abstract specification and technical design document from input |
| `/generate_prd` | Generate PRD (Requirements Specification) in SysML requirements diagram format from business requirements |
| `/check_spec` | Check consistency between implementation code and specifications, detecting discrepancies |
| `/review_cleanup` | Clean up review/ directory after implementation, integrating design decisions |
| `/task_breakdown` | Break down tasks from technical design document into small task list |

### Skills

| Skill | Description |
|:---|:---|
| `vibe-detector` | Analyzes user input to automatically detect Vibe Coding (vague instructions) |
| `doc-consistency-checker` | Automatically checks consistency between documents (PRD, spec, design) |

### Hooks

| Hook | Trigger | Description |
|:---|:---|:---|
| `check-spec-exists` | PreToolUse (Edit/Write) | Verifies specification existence before implementation, shows warning |
| `check-commit-prefix` | PostToolUse (Bash) | Checks commit message convention |

## Usage

### sdd-workflow Agent

Automatically performs the following at task start:

1. **Phase Determination**: Identify required phases based on task nature
2. **Vibe Coding Prevention**: Detect vague instructions and promote specification clarification
3. **Document Management**: Guide specification/design document creation and updates

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

#### Review Cleanup

```
/review_cleanup TICKET-123
```

## Hook Configuration

To enable hooks, add the following to your project's `.claude/settings.json`:

```json
{
  "hooks": {
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

See `hooks/settings.example.json` for configuration example.

## Serena MCP Integration (Optional)

Configure [Serena](https://github.com/oraios/serena) MCP to enable enhanced functionality through semantic code analysis.

### What is Serena

Serena is a semantic code analysis tool based on LSP (Language Server Protocol), supporting 30+ programming languages. It enables symbol-level code search and analysis.

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

| Command | Enhancement with Serena |
|:---|:---|
| `/generate_spec` | Reference existing code API/type definitions for consistent specification generation |
| `/check_spec` | High-precision API implementation and signature verification via symbol-based search |
| `/task_breakdown` | Analyze change impact scope for accurate task dependency mapping |

### Without Serena

All features work without Serena. Text-based search (Grep/Glob) is used for analysis, working language-agnostically.

## AI-SDD Development Flow

```
Specify → Plan → Tasks → Implement & Review
```

### Recommended Directory Structure

```
.docs/
├── SPECIFICATION_TEMPLATE.md     # Abstract specification template (optional)
├── DESIGN_DOC_TEMPLATE.md        # Technical design document template (optional)
├── requirement-diagram/          # PRD (Requirements Specification)
│   └── {feature-name}.md
├── specification/                # Persistent knowledge assets
│   ├── {feature-name}_spec.md    # Abstract specification
│   └── {feature-name}_design.md  # Technical design document
└── review/                       # Temporary work logs (deleted after implementation)
    └── {ticket-number}/
```

## Plugin Structure

```
sdd-workflow/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── agents/
│   ├── sdd-workflow.md          # AI-SDD development flow agent
│   └── spec-reviewer.md         # Specification review agent
├── commands/
│   ├── generate_spec.md         # Specification/design document generation
│   ├── generate_prd.md          # PRD generation
│   ├── check_spec.md            # Consistency check
│   ├── review_cleanup.md        # Review cleanup
│   └── task_breakdown.md        # Task breakdown
├── skills/
│   ├── vibe-detector.md         # Vibe Coding detection skill
│   └── doc-consistency-checker.md
├── hooks/
│   ├── check-spec-exists.sh
│   ├── check-commit-prefix.sh
│   └── settings.example.json
├── LICENSE
└── README.md
```

## Commit Message Convention

| Prefix | Usage |
|:---|:---|
| `[docs]` | Add/update documentation |
| `[spec]` | Add/update specifications (`*_spec.md`) |
| `[design]` | Add/update design documents (`*_design.md`) |

## License

MIT License
