# {FEATURE_NAME} - Technical Design Document (Reverse Engineered)

> **⚠️ Note**: This design document was reverse-engineered from existing implementation on {DATE}.
> It documents the current state, not the original design. Review and update as needed.

## Design Overview

**Current Architecture:**

{HIGH_LEVEL_ARCHITECTURE_DESCRIPTION}

**Technology Stack:**
- Language: {Programming language used in the project}
- Framework: {Framework used}
- Database: {Database system used}
- Libraries: {key libraries}

## Architecture

### Component Structure

```
{CURRENT_DIRECTORY_STRUCTURE}
```

**Components:**

1. **{Component 1 Name}** (`{file_path}`)
   - Responsibility: {What it does}
   - Dependencies: {What it depends on}

2. **{Component 2 Name}** (`{file_path}`)
   - Responsibility: ...
   - Dependencies: ...

### Data Flow

```
{DATA_FLOW_DIAGRAM_OR_DESCRIPTION}
```

## Implementation Details

### Key Algorithms

**{Algorithm Name}** ({file_path}:{line_number})
```
{PSEUDOCODE_OR_DESCRIPTION}
```

### State Management

{How state is managed - Redux, Context, database, etc.}

### Error Handling

{Current error handling patterns}

## API Design

### Endpoints (if applicable)

| Method | Path | Description | Implementation |
|:--|:--|:--|:--|

## Testing Strategy

**Current Test Coverage:**
- Unit tests: {file paths}
- Integration tests: {file paths}
- Coverage: {percentage, if known}

**Gaps:**
{Areas lacking tests}

## Deployment

{Current deployment process, if observable}

## Technical Debt Observations

1. **{Debt Item 1}**: {Description}
   - Severity: {High/Medium/Low}
   - Location: `{file_path}`

2. **{Debt Item 2}**: ...

---

**Next Steps:**
1. Verify this design matches actual implementation
2. Address technical debt items
3. Plan refactoring (add Refactoring Plan section below)
