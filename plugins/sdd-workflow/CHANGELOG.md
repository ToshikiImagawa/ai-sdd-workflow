# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.4.1] - 2026-01-26

### Fixed

#### Commands

- **argument-hint corrections and argument descriptions** - Fixed argument specifications to match actual usage
    - Unified `argument-hint` expressions ("file-path" → "feature-name" corrections)
    - Added argument description tables to each command (argument name, required/optional, description)
    - Affected commands:
        - `task_breakdown`: `<design-doc-path>` → `<feature-name> [ticket-number]`
        - `check_spec`: `<design-doc-path>` → `[feature-name] [--full]`
        - `checklist`: `<file-path>` → `<feature-name> [ticket-number]`
        - `clarify`: `[spec-file-path]` → `<feature-name> [--interactive]`
        - `constitution`: `<init|update|check>` → `<subcommand> [arguments]` (added subcommand details table)
        - `generate_prd`: `<feature-name> [requirements-description]` → `<requirements-description>`
        - `generate_spec`: `<feature-name> [prd-file-path]` → `<requirements-description>`
        - `implement`: `<task-file-path>` → `<feature-name> [ticket-number]`
        - `task_cleanup`: `<ticket-number>` → `[ticket-number]` (made optional)
    - Users can now understand correct argument formats when executing commands

## [2.5.0] - 2026-01-25

### Changed

#### Architecture

- **Output Format Separation** - Separated command output formats into `skills/output-templates/`
    - Command md files now contain only Claude-facing instructions
    - Output formats are managed as independent template files
    - New skill: `output-templates` (includes 9 template files)
    - Existing `sdd-templates` skill is now dedicated to project document templates

### Added

#### Skills

- **output-templates** - New skill providing command output formats
    - `init_output.md` - Initialization complete message
    - `prd_output.md` - PRD generation complete message
    - `spec_output.md` - Specification & design generation complete message
    - `breakdown_output.md` - Task breakdown results
    - `cleanup_output.md` - Cleanup confirmation
    - `clarification_output.md` - Specification clarification report
    - `check_spec_output.md` - Consistency check results
    - `migrate_output.md` - Migration results
    - `constitution_output.md` - Constitution management results

### Fixed

#### Commands

- **Unified Prompt Expressions** - Removed user-facing explanations and unified to clear Claude-facing instructions
    - Removed "Next Steps" list items (from plain text within "Post-Generation Actions" section)
    - Removed "Recommended Manual Verification" sections (moved to output templates)
    - Changed "manually" expressions to Claude-directed instructions (e.g., "recommend manual verification to user")
    - Unified output format reference method (from file path to skill reference)
    - Affected commands: `sdd_init`, `generate_prd`, `generate_spec`, `task_breakdown`, `task_cleanup`, `clarify`, `check_spec`, `sdd_migrate`, `constitution`

#### Agents

- **Unified Prompt Expressions** - Changed "recommended" expressions to directive forms
    - spec-reviewer: "recommended to be added" → "need to be added"
    - clarification-assistant: "Supplementation recommended" → "Supplementation needed"
    - clarification-assistant: "Recommended Clarity Scores" → "Clarity Score Evaluation Criteria"

## [2.4.0] - 2026-01-25

### Added

#### Documentation

- **PLUGIN.md** - Comprehensive guide for Claude Code plugin and marketplace creation
    - Plugin basic structure (directory layout, marketplace structure)
    - Manifest files (plugin.json, marketplace.json details)
    - Commands, agents, skills implementation (frontmatter, best practices)
    - MCP server integration (external tool integration)
    - Hooks implementation (event-driven automation)
    - Marketplace publishing process (quality standards, distribution model)
- **CLAUDE.md** - Added reference to PLUGIN.md (similar to AGENTS.md structure)

#### Skills

- Added `version: 2.3.1` and `license: MIT` fields to all skills
    - vibe-detector
    - doc-consistency-checker
    - sdd-templates

#### Commands

- Added `argument-hint` field to all commands for improved usability
    - generate_spec: `<feature-name> [prd-file-path]`
    - generate_prd: `<feature-name> [requirements-description]`
    - check_spec: `<design-doc-path>`
    - task_breakdown: `<design-doc-path> [ticket-number]`
    - task_cleanup: `<ticket-number>`
    - constitution: `<init|update|check>`
    - implement: `<task-file-path>`
    - clarify: `[spec-file-path]`
    - checklist: `<file-path>`

### Changed

#### Commands

- **implement** - Added TaskList-based progress management
    - Creates tasks using TaskCreate at the start of each phase
    - Updates task status using TaskUpdate during phase execution (pending → in_progress → completed)
    - Sets dependencies to ensure next phase starts only after previous phase completes
    - Users can check implementation progress using `/tasks` command
    - Falls back to traditional markdown progress display when TaskList is unavailable

#### Marketplace

- **marketplace.json** improvements
    - Added `author.url` (creator attribution)
    - Added `category: "development"` (marketplace filtering)
    - Added `tags` array (search discoverability)
        - "specification-driven-development"
        - "japanese" / "english"
        - "workflow"
        - "sysml"
        - "requirements"
        - "documentation"

#### Agents

- Improved `description` for all agents with clearer usage scenarios
    - Changed from functional description style to "when to use" style
    - Added specific trigger phrases (e.g., "review spec", "check spec")
    - Made explicit relationships with commands (e.g., after /check_spec or /generate_spec execution)
    - Specified required input information (e.g., specification file path needed)
    - Removed self-referential "agent" terminology
    - Target agents: spec-reviewer, requirement-analyzer, prd-reviewer, clarification-assistant

#### Skills

- Improved `description` for all skills with clearer execution context
    - Specified execution timing (e.g., automatically executed before implementation, invoked by commands)
    - Specified detection details (e.g., ambiguous expressions like "make it nice", "somehow")
    - Made explicit traceability guarantees
    - Detailed fallback behavior explanation
    - Target skills: vibe-detector, doc-consistency-checker, sdd-templates

## [2.3.1] - 2026-01-14

### Fixed

#### Hooks

- `session-start.sh` - Improved error handling with temporary file existence check
    - Fixed `mv: No such file or directory` error when sed command fails
    - Added `&& [ -f "$TEMP_FILE" ]` to verify temporary file existence before executing mv
    - Improved fallback process to work properly
    - Added warning file deletion process (else clause) to English version for consistency with Japanese version

## [2.3.0] - 2026-01-09

### Changed

#### Agents

- **Role Separation**: Renamed `sdd-workflow` agent to `AI-SDD-PRINCIPLES.md`
    - Separated principle definitions into an independent document
    - Updated all commands, agents, and skills to reference `../AI-SDD-PRINCIPLES.md`
    - Centralized AI-SDD principles for better maintainability

- `spec-reviewer` - Added document traceability check functionality
    - **PRD ↔ spec traceability check**: Verify PRD requirements are properly covered in spec
        - Requirement ID (UR/FR/NFR) mapping verification
        - Coverage rate calculation (80% threshold check)
        - Classification of partial/missing coverage
    - **spec ↔ design consistency check**: Verify spec content is properly detailed in design
        - API definition elaboration check
        - Type definition consistency check
        - Constraint consideration check
    - Added `Edit` to `allowed-tools` (for auto-fix support)
    - Clarified input format and output format (`--summary` option support)

#### Commands

- `/check_spec` - **Specialized for design ↔ implementation consistency check**
    - **[BREAKING]** Delegated document-to-document consistency checks (PRD↔spec, spec↔design) to `spec-reviewer`
        - **Before (v2.2.0)**: Performed all consistency checks (CONSTITUTION↔docs, PRD↔spec, spec↔design, design↔implementation)
        - **After (v2.3.0)**: Performs only design↔implementation consistency check (improved performance)
        - **Migration**:
            - If document-to-document consistency checks are needed: Use `/check_spec --full`
            - If design↔implementation only is sufficient: Keep using `/check_spec` (same command as before)
        - **Impact**: If using `/check_spec` in CI/CD pipeline, consider adding `--full` option
    - Added `--full` option: Runs comprehensive review by `spec-reviewer` in addition to consistency check
    - Limited target documents to `*_design.md`
    - Simplified output format (focused on design↔implementation)

- `/sdd_init` - Updated reference path
    - Changed agent reference to `AI-SDD-PRINCIPLES.md`

### Added

#### Documentation

- `AI-SDD-PRINCIPLES.md` - Independent document defining AI-SDD principles
    - Separated principle definitions previously contained in `sdd-workflow` agent
    - Commonly referenced by commands, agents, and skills

#### README

- Documented Windows platform incompatibility
    - Added platform support matrix (macOS/Linux: ✅, Windows: ❌)
    - Documented alternatives for Windows users (WSL, Git Bash)
    - Future support plans (PowerShell version, cross-platform implementation under consideration)

## [2.2.0] - 2026-01-06

### Added

#### Agents

- `prd-reviewer` - PRD (Requirements Specification) review agent
    - CONSTITUTION.md compliance check (most important feature)
    - Principle category checks (Business, Architecture, Development, Technical Constraints)
    - Auto-fix flow (attempts auto-fix on violation detection)
    - SysML requirements diagram format validation
    - Ambiguous expression detection and improvement suggestions

### Changed

#### Agents

- `spec-reviewer` - Added CONSTITUTION.md compliance check functionality
    - Added preparation instruction to read CONSTITUTION.md using Read tool
    - Spec-focused principle category checks (Architecture principles emphasized)
    - Design-focused principle category checks (Technical constraints emphasized)
    - Auto-fix flow (attempts auto-fix on violation detection)
    - Added CONSTITUTION.md compliance check results to review output format

#### Commands

- `/generate_prd` - Added CONSTITUTION.md compliant generation flow
    - Added CONSTITUTION.md reading step to generation flow (Step 2)
    - Made prd-reviewer principle compliance check mandatory (Step 6)
    - Added principle category impact table for PRD
    - Added check result output template

- `/generate_spec` - Added CONSTITUTION.md compliant generation flow
    - Added CONSTITUTION.md reading step to generation flow (Step 2)
    - Made spec-reviewer principle compliance check mandatory (Steps 6, 8)
    - Added check result output templates for both spec and design doc

## [2.1.1] - 2025-12-23

### Changed

- Removed automatic git commit instructions from all commands and agents
    - `task_cleanup` - Removed commit step from cleanup workflow
    - `implement` - Removed commit instruction from continuous verification flow
    - `generate_spec` - Removed commit step from generation flow
    - `sdd-workflow` agent - Removed commit steps from workflow phases
    - `clarify` - Removed commit instructions from integration mode
    - `task_breakdown` - Removed commit step from post-generation actions
    - `generate_prd` - Removed commit step from post-generation actions
    - `sdd_migrate` - Removed commit instructions and commit message examples
    - `sdd_init` - Removed commit step from initialization flow

## [2.1.0] - 2025-12-12

### Added

#### Commands

- `/clarify` - Specification clarification command
    - Scans specifications across 9 categories (functional scope, data model, flow, non-functional requirements,
      integrations, edge cases, constraints, terminology, completion signals)
    - Classifies unclear items as Clear/Partial/Missing
    - Generates up to 5 high-impact clarification questions
    - Incrementally integrates answers into `*_spec.md`
    - Complementary to `vibe-detector` skill
- `/implement` - TDD-based implementation execution command
    - Verifies checklist completion rate in tasks.md
    - Executes 5 phases in order (Setup→Tests→Core→Integration→Polish)
    - Test-first (TDD) approach
    - Auto-marks progress in tasks.md
    - Completion verification (all tasks done, tests pass, spec consistency)
- `/checklist` - Quality checklist generation command
    - Auto-generates checklists from specs and plans across 9 categories
    - Assigns IDs in CHK-{category-number}{sequence} format
    - Auto-sets priority levels (P1/P2/P3)
- `/constitution` - Project constitution management command
    - Defines non-negotiable project principles (business, architecture, development methodology, technical constraints)
    - Semantic versioning (MAJOR/MINOR/PATCH)
    - Sync validation with specifications and design documents

#### Agents

- `clarification-assistant` - Specification clarification assistant agent
    - Systematically analyzes user requirements across 9 categories
    - Generates high-impact clarification questions
    - Integrates answers into specifications
    - Backend role for `/clarify` command

#### Templates

- `checklist_template.md` - Quality checklist template
    - 9 categories of quality check items
    - Priority levels (P1/P2/P3)
    - Verification methods for each item
- `constitution_template.md` - Project constitution template
    - Principle hierarchy (business → architecture → development methodology → technical constraints)
    - Verification methods, violation examples, compliance examples for each principle
    - Version history and amendment process
- `implementation_log_template.md` - Implementation log template
    - Session-based implementation decision records
    - Challenges and solutions tracking
    - Technical discoveries and performance metrics

#### Skills

- `sdd-templates` - Added references to new templates

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
