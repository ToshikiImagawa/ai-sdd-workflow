# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
