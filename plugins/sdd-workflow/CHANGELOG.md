# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- `/generate_prd` - Generate PRD (Requirements Specification) in SysML requirements diagram format from business requirements
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

#### Hooks

- `check-spec-exists` - Verify specification existence before implementation
- `check-commit-prefix` - Check commit message convention ([docs], [spec], [design])

#### Integration

- Serena MCP optional integration
  - Enhanced functionality through semantic code analysis
  - Support for 30+ programming languages
  - Text-based search fallback when not configured
