# {Feature Name} Technical Design Document

## Document Information

| Item | Content |
|:---|:---|
| Feature Name | {Feature Name} |
| Created | YYYY-MM-DD |
| Implementation Status | Not Started / In Progress / Implemented / Testing / Complete |
| Related Documents | [PRD](.docs/requirement-diagram/{feature-name}.md), [Spec](.docs/specification/{feature-name}_spec.md) |

## Design Goals

### Primary Goals

1. {Technical goal to achieve 1}
2. {Technical goal to achieve 2}
3. {Technical goal to achieve 3}

### Quality Attributes

| Attribute | Target | Measurement Method |
|:---|:---|:---|
| Performance | {Specific target value} | {Measurement method} |
| Scalability | {Specific target value} | {Measurement method} |
| Maintainability | {Specific target value} | {Measurement method} |
| Testability | {Specific target value} | {Measurement method} |

## Technology Stack

### Adopted Technologies

| Category | Technology/Library | Version | Selection Rationale |
|:---|:---|:---|:---|
| Language | {Language name} | {Version} | {Rationale} |
| Framework | {Framework name} | {Version} | {Rationale} |
| Database | {DB name} | {Version} | {Rationale} |
| Testing | {Test framework} | {Version} | {Rationale} |
| Other | {Library name} | {Version} | {Rationale} |

### Dependencies

```mermaid
graph TD
    subgraph "This Feature"
        A[{Feature Name}]
    end

    subgraph "Internal Dependencies"
        B[{Dependency Module 1}]
        C[{Dependency Module 2}]
    end

    subgraph "External Dependencies"
        D[{External Service 1}]
        E[{External Library 1}]
    end

    A --> B
    A --> C
    A --> D
    A --> E
```

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[UI Component]
    end

    subgraph "Application Layer"
        SVC[{FeatureName}Service]
        UC[UseCase]
    end

    subgraph "Domain Layer"
        ENT[Entity]
        REPO_IF[Repository Interface]
    end

    subgraph "Infrastructure Layer"
        REPO[Repository Implementation]
        EXT[External Service Client]
    end

    UI --> SVC
    SVC --> UC
    UC --> ENT
    UC --> REPO_IF
    REPO_IF --> REPO
    UC --> EXT
```

### Module Structure

```
src/
├── {feature-name}/
│   ├── index.ts                 # Public API
│   ├── types.ts                 # Type definitions
│   ├── {feature-name}.service.ts      # Service layer
│   ├── {feature-name}.usecase.ts      # Use case layer
│   ├── domain/
│   │   ├── entities/            # Entities
│   │   └── repositories/        # Repository interfaces
│   ├── infrastructure/
│   │   ├── repositories/        # Repository implementations
│   │   └── external/            # External service clients
│   └── __tests__/               # Tests
│       ├── unit/
│       └── integration/
```

### Layer Responsibilities

| Layer | Responsibility | Allowed Dependencies |
|:---|:---|:---|
| Presentation | UI, I/O handling | Application |
| Application | Use case orchestration | Domain |
| Domain | Business logic, entities | None (pure) |
| Infrastructure | Technical implementation, external integration | Domain (interface implementation) |

## Design Decisions

### Decisions Made

#### DJ-001: {Design Decision Title 1}

**Context**: {Background that necessitated this decision}

**Decision**: {Adopted design approach}

**Rationale**:
- {Reason 1}
- {Reason 2}

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejection Reason |
|:---|:---|:---|:---|
| {Alternative 1} | {Pros} | {Cons} | {Rejection reason} |
| {Alternative 2} | {Pros} | {Cons} | {Rejection reason} |

**Impact**:
- {Impact of this decision 1}
- {Impact of this decision 2}

#### DJ-002: {Design Decision Title 2}

**Context**: {Background}

**Decision**: {Adopted design}

**Rationale**:
- {Reason}

### Pending Decisions

| ID | Item | Options | Deadline | Owner |
|:---|:---|:---|:---|:---|
| TBD-001 | {Pending item} | {Option 1}, {Option 2} | YYYY-MM-DD | {Owner} |

## Data Model (Detailed)

### Database Schema

```sql
-- {Table 1}
CREATE TABLE {table_name1} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {column1} VARCHAR(255) NOT NULL,
    {column2} INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_{table_name1}_{column1} ON {table_name1}({column1});

-- {Table 2}
CREATE TABLE {table_name2} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {table_name1}_id UUID REFERENCES {table_name1}(id),
    {column1} TEXT NOT NULL
);
```

### Migration Plan

| Version | Changes | Impact | Rollback Possible |
|:---|:---|:---|:---|
| v1.0 | Initial schema creation | None | Yes |
| v1.1 | {Changes} | {Impact} | Yes/No |

## Interface Definition (Detailed)

### Internal Interfaces

```typescript
// Service Interface
interface I{FeatureName}Service {
  operation1(param: Param1Type): Promise<Result1Type>;
  operation2(param: Param2Type): Promise<Result2Type>;
}

// Repository Interface
interface I{Entity}Repository {
  findById(id: string): Promise<{Entity} | null>;
  save(entity: {Entity}): Promise<void>;
  delete(id: string): Promise<void>;
}
```

### External API (If Applicable)

#### Endpoint List

| Method | Path | Description | Auth Required |
|:---|:---|:---|:---|
| GET | /api/{resource} | {Description} | Yes/No |
| POST | /api/{resource} | {Description} | Yes/No |
| PUT | /api/{resource}/:id | {Description} | Yes/No |
| DELETE | /api/{resource}/:id | {Description} | Yes/No |

#### Request/Response Examples

```json
// POST /api/{resource}
// Request
{
  "field1": "value1",
  "field2": 123
}

// Response (201 Created)
{
  "id": "uuid",
  "field1": "value1",
  "field2": 123,
  "createdAt": "2024-01-01T00:00:00Z"
}

// Error Response (400 Bad Request)
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "field1 is required"
  }
}
```

## Error Handling

### Error Classification

| Error Code | HTTP Status | Description | Response |
|:---|:---|:---|:---|
| VALIDATION_ERROR | 400 | Input validation error | Client fix |
| UNAUTHORIZED | 401 | Authentication error | Re-authenticate |
| FORBIDDEN | 403 | Authorization error | Check permissions |
| NOT_FOUND | 404 | Resource not found | Verify |
| INTERNAL_ERROR | 500 | Internal error | Retry/Report |

### Retry Strategy

| Error Type | Retry | Max Attempts | Backoff |
|:---|:---|:---|:---|
| Network error | Yes | 3 | Exponential |
| Timeout | Yes | 2 | Fixed interval |
| Auth error | No | - | - |
| Validation error | No | - | - |

## Testing Strategy

### Test Levels

| Level | Target | Coverage Goal | Tool |
|:---|:---|:---|:---|
| Unit Test | Functions, classes | 80%+ | {Test framework} |
| Integration Test | Module interactions | Key paths | {Test framework} |
| E2E Test | User scenarios | Critical paths | {E2E tool} |

### Test Case Overview

| Test ID | Target | Scenario | Expected Result |
|:---|:---|:---|:---|
| UT-001 | {Target} | {Happy path scenario} | {Expected result} |
| UT-002 | {Target} | {Error scenario} | {Expected result} |
| IT-001 | {Target} | {Integration scenario} | {Expected result} |

## Security Considerations

### Threats and Countermeasures

| Threat | Risk | Countermeasure |
|:---|:---|:---|
| {Threat 1} | High/Medium/Low | {Countermeasure} |
| SQL Injection | High | Parameterized queries |
| XSS | Medium | Output escaping |

### Authentication & Authorization

- Authentication Method: {JWT / Session / OAuth, etc.}
- Authorization Model: {RBAC / ABAC, etc.}
- Session Management: {Session timeout, refresh strategy}

## Performance Considerations

### Predicted Bottlenecks

| Location | Predicted Issue | Countermeasure |
|:---|:---|:---|
| {Location 1} | {Issue} | {Countermeasure} |
| Database queries | N+1 problem | Eager Loading |

### Optimization Strategy

- Cache Strategy: {Cache targets, TTL, invalidation strategy}
- Index Strategy: {Index target columns}
- Async Processing: {Processes to make asynchronous}

## Implementation Plan

### Milestones

| Phase | Content | Duration | Deliverables |
|:---|:---|:---|:---|
| 1 | Foundation implementation | {Duration} | {Deliverables} |
| 2 | Core feature implementation | {Duration} | {Deliverables} |
| 3 | Testing & fixes | {Duration} | {Deliverables} |

### Task Breakdown (Overview)

Detailed task breakdown is generated with `/task_breakdown` command and placed in `.docs/review/{ticket-number}/`.

## Specification Reference

- Related Spec: `.docs/specification/{feature-name}_spec.md`
- Related PRD: `.docs/requirement-diagram/{feature-name}.md`

### Specification Mapping

| Spec Requirement | Implementation in This Design |
|:---|:---|
| SPEC-001 | {Implementation approach} |
| SPEC-002 | {Implementation approach} |

---

## Change History

| Date | Version | Changes | Author |
|:---|:---|:---|:---|
| YYYY-MM-DD | 1.0 | Initial creation | {Name} |
