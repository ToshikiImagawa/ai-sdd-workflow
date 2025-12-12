# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-12-12

### Added

#### Agents

- Added document link convention to all agents
    - `sdd-workflow` - Defined markdown link format for files/directories
    - `spec-reviewer` - Added link convention check points
    - `requirement-analyzer` - Added link convention for requirement diagrams
    - File links: `[filename.md](path)` format
    - Directory links: `[directory-name](path/index.md)` format

### Removed

#### Agents

- `sdd-workflow` - Removed commit message convention section
    - Changed policy to delegate to Claude Code's standard commit conventions

## [2.0.0] - 2025-12-09

### Breaking Changes

#### Directory Structure Changes

- **Root directory**: `.docs/` → `.sdd/`
- **Requirement directory**: `requirement-diagram/` → `requirement/`
- **Task log directory**: `review/` → `task/`

#### Command Rename

- `/review_cleanup` → `/task_cleanup`

#### Migration

Use the `/sdd_migrate` command to migrate from legacy versions (v1.x):

- **Option A**: Rename directories to migrate to new structure
- **Option B**: Generate `.sdd-config.json` to maintain legacy structure

### Added

#### Commands

- `/sdd_init` - AI-SDD workflow initialization command
    - Adds AI-SDD Instructions section to project's `CLAUDE.md`
    - Creates `.sdd/` directory structure (requirement/, specification/, task/)
    - Generates template files using `sdd-templates` skill
- `/sdd_migrate` - Migration command from legacy versions
    - Detects legacy structure (`.docs/`, `requirement-diagram/`, `review/`)
    - Choose between migrating to new structure or generating compatibility config

#### Agents

- `requirement-analyzer` - Requirement analysis agent
    - SysML requirements diagram-based analysis
    - Requirement tracking and verification

#### Skills

- `sdd-templates` - AI-SDD templates skill
    - Provides fallback templates for PRD, specification, and design documents
    - Clarifies project template priority rules

#### Hooks

- `session-start` - Session start initialization hook
    - Loads settings from `.sdd-config.json` and sets environment variables
    - Auto-detects legacy structure and shows migration guidance

#### Configuration File

- `.sdd-config.json` - Project configuration file support
    - `root`: Root directory (default: `.sdd`)
    - `directories.requirement`: Requirement directory (default: `requirement`)
    - `directories.specification`: Specification directory (default: `specification`)
    - `directories.task`: Task log directory (default: `task`)

### Changed

#### Plugin Configuration

- `plugin.json` - Enhanced author field
    - Added `author.url` field

#### Commands

- Added `allowed-tools` field to all commands
    - Explicitly specifies available tools for each command
    - Improved security and clarity
- All commands now support `.sdd-config.json` configuration file

#### Skills

- Improved skill directory structure
    - Migrated from `skill-name.md` to `skill-name/SKILL.md` + `templates/` structure
    - Applied Progressive Disclosure pattern
    - Externalized template files, simplifying SKILL.md

### Removed

#### Hooks

- `check-spec-exists` - Removed
    - Specification creation is optional, and non-existence is a common valid case
- `check-commit-prefix` - Removed
    - Removed because commit message conventions are not used by plugin functionality

## [1.1.0] - 2025-12-06

### Added

#### Commands

- `/sdd_init` - AI-SDD workflow initialization command
    - Adds AI-SDD Instructions section to project's `CLAUDE.md`
    - Creates `.docs/` directory structure (requirement-diagram/, specification/, review/)
    - Generates template files using `sdd-templates` skill

#### Skills

- `sdd-templates` - AI-SDD templates skill
    - Provides fallback templates for PRD, specification, and design documents
    - Clarifies project template priority rules

### Changed

#### Plugin Configuration

- `plugin.json` - Enhanced author field
    - Added `author.url` field

#### Commands

- Added `allowed-tools` field to all commands
    - Explicitly specifies available tools for each command
    - Improved security and clarity

#### Skills

- Improved skill directory structure
    - Migrated from `skill-name.md` to `skill-name/SKILL.md` + `templates/` structure
    - Applied Progressive Disclosure pattern
    - Externalized template files, simplifying SKILL.md

## [1.0.1] - 2025-12-04

### Changed

#### Agents

- `spec-reviewer` - Added prerequisites section
    - Added instruction to read `sdd-workflow:sdd-workflow` agent content before execution
    - Promotes understanding of AI-SDD principles, document structure, persistence rules, and Vibe Coding prevention

#### Commands

- Added prerequisites section to all commands
    - `generate_prd`, `generate_spec`, `check_spec`, `task_breakdown`, `review_cleanup`
    - Added instruction to read `sdd-workflow:sdd-workflow` agent content before execution
    - Ensures consistent behavior following sdd-workflow agent principles

#### Skills

- Added prerequisites section to all skills
    - `vibe-detector`, `doc-consistency-checker`
    - Added instruction to read `sdd-workflow:sdd-workflow` agent content before execution

#### Hooks

- `check-spec-exists.sh` - Improved path resolution
    - Dynamically retrieves repository root using `git rev-parse --show-toplevel`
    - Falls back to current directory if not a git repository
- `check-spec-exists.sh` - Extended test file exclusion patterns
    - Jest: `__tests__/`, `__mocks__/`
    - Storybook: `*.stories.*`
    - E2E: `/e2e/`, `/cypress/`
- `settings.example.json` - Added setup instructions as comments
    - Fixed path to `./hooks/` format

#### Skills

- `vibe-detector` - Added `AskUserQuestion` to `allowed-tools`
    - Supports user confirmation flow
- `doc-consistency-checker` - Added `Bash` to `allowed-tools`
    - Supports directory structure verification

## [1.0.0] - 2024-12-03

### Added

#### Agents

- `sdd-workflow` - AI-SDD development flow management agent
    - Phase determination (Specify → Plan → Tasks → Implement & Review)
    - Vibe Coding prevention (detection of vague instructions and promotion of clarification)
    - Document consistency checks
- `spec-reviewer` - Specification quality review agent
    - Ambiguous description detection
    - Missing section identification
    - SysML compliance checks

#### Commands

- `/generate_prd` - Generate PRD (Requirements Specification) in SysML requirements diagram format from business
  requirements
- `/generate_spec` - Generate abstract specification and technical design document from input
    - PRD consistency review feature
- `/check_spec` - Check consistency between implementation code and specifications
    - Multi-layer check: PRD ↔ spec ↔ design ↔ implementation
- `/task_breakdown` - Break down tasks from technical design document
    - Requirement coverage verification
- `/review_cleanup` - Clean up review/ directory after implementation

#### Skills

- `vibe-detector` - Automatic detection of Vibe Coding (vague instructions)
- `doc-consistency-checker` - Automatic consistency check between documents

#### Integration

- Serena MCP optional integration
    - Enhanced functionality through semantic code analysis
    - Support for 30+ programming languages
    - Text-based search fallback when not configured
