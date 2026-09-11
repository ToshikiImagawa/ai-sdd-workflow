# Example: Case B (No Spec)

This example demonstrates `/plan-refactor` usage when no PRD or spec exists yet.

## Scenario

**Feature:** User profile management
**Problem:** Code has grown organically without documentation. Need to refactor before adding new features.
**Existing Docs:** None (legacy code)

## Command

```bash
/plan-refactor user-profile --ticket=72
```

## Expected Behavior

### Phase 1: Pre-flight Checks

```
[plan-refactor] Running document scan...
[scan-existing-docs] Scanning for: user-profile
[scan-existing-docs] Structure: none
[scan-existing-docs] PRD: false, Spec: false, DesignDraft: false, LegacyDesign: false
[scan-existing-docs] Case: B (No spec, reverse-engineering needed)

Detected: Case B (No spec)
```

Case B is reached because **no spec** was found — this is the one path that turns undocumented code into a spec.
A missing design document alone never triggers it.

### Phase 2: Implementation Discovery

```
[plan-refactor] Searching for implementation files...
[find-implementation-files] Found 12 files
- src/profile/edit.ts
- src/profile/view.ts
- src/profile/avatar.ts
- src/utils/profile-validator.ts
- ...

⚠️ Warning: 12 files found. This may take time to analyze.
Continue? [Yes/No]
```

User: Yes

### Phase 3: Reverse Engineering

Claude reads implementation files and reverse-engineers the spec and design.

#### Step 3.1: Generate Spec

Claude creates `.sdd/specification/user-profile_spec.md`:

```markdown
# user-profile - Specification (Reverse Engineered)

> **⚠️ Note**: This specification was reverse-engineered from existing implementation on 2026-02-15.

## Overview

**Current Implementation Summary:**

The user profile module manages user profile information, including personal data, avatar uploads, and privacy settings.

**Original Purpose (Inferred):**

Allow users to view and edit their profile information, upload profile pictures, and control visibility settings.

## Functional Requirements

### Existing Implementation

- **FR-001**: Users can view their profile
  - Implementation: `src/profile/view.ts:15-45`
  - Status: ✅ Implemented

- **FR-002**: Users can edit profile fields (name, bio, email)
  - Implementation: `src/profile/edit.ts:20-80`
  - Status: ✅ Implemented

- **FR-003**: Users can upload and update avatar images
  - Implementation: `src/profile/avatar.ts:10-60`
  - Status: ✅ Implemented

- **FR-004**: Profile validation (email format, bio length)
  - Implementation: `src/utils/profile-validator.ts:5-40`
  - Status: ✅ Implemented

### Known Gaps

- **Gap-001**: No privacy controls (all profiles are public)
- **Gap-002**: Avatar size validation is inconsistent

## Non-Functional Requirements

### Performance

- Avatar upload limit: 5MB (observed in code)
- No caching mechanism observed

### Security

- Email validation: Regex-based (may need improvement)
- No rate limiting on profile updates

## Interface Specifications

### Public API

**GET /api/profile/:userId** - Returns user profile data
**POST /api/profile/update** - Updates profile fields
**POST /api/profile/avatar** - Uploads new avatar

## Dependencies

- `express`, `multer`, `sharp`, `@prisma/client`

## Data Model

```sql
table User {
  id: string (PK)
  name: string
  email: string (unique)
  bio: string (nullable)
  avatarUrl: string (nullable)
  createdAt: datetime
  updatedAt: datetime
}
```
```

#### Step 3.2: Generate the Design Draft

Claude creates `.sdd/task/72/design-draft.md` — a **temporary draft**, not a document under `specification/`:

```markdown
---
id: "design-72"
title: "user-profile"
type: "design"
status: "review"
sdd-phase: "plan"
impl-status: "implemented"
depends-on: ["spec-user-profile"]
tags: ["reverse-engineered"]
---

# user-profile - Technical Design Draft (Reverse Engineered)

> **⚠️ Note**: This design draft was reverse-engineered from existing implementation on 2026-02-15.
> It is deleted after implementation, once its settled decisions have been appended to `.sdd/adr/user-profile.md`.

## Design Overview

**Current Architecture:**

Layered architecture:
- API Layer: Express routes
- Service Layer: Business logic
- Data Layer: Prisma ORM

**Technology Stack:**
- Language: TypeScript
- Framework: Express.js
- Database: PostgreSQL (via Prisma)
- Libraries: multer, sharp, validator

## Architecture

### Component Structure

```
src/profile/
├── view.ts          # Profile viewing
├── edit.ts          # Profile editing
├── avatar.ts        # Avatar upload
└── routes.ts        # API routes

src/utils/
└── profile-validator.ts  # Validation logic
```

## Implementation Details

### Key Algorithms

**Avatar Resizing** (`src/profile/avatar.ts:35-50`)
1. Receive uploaded file via multer
2. Validate file size (<5MB) and type (image/*)
3. Resize to 200x200 using sharp
4. Upload to S3
5. Save URL to database

## API Design

| Method | Path | Description | Implementation |
|:--|:--|:--|:--|
| GET | /api/profile/:userId | Get user profile | `view.ts:15` |
| POST | /api/profile/update | Update profile | `edit.ts:20` |
| POST | /api/profile/avatar | Upload avatar | `avatar.ts:10` |

## Testing Strategy

**Current Test Coverage:**
- Unit tests: ~40% (estimated)
- Integration tests: None found

**Gaps:**
- No integration tests for full user journey
- Avatar upload edge cases not covered

## Technical Debt Observations

1. **Inconsistent Validation**: Validation logic split between controller and utils
   - Severity: Medium
   - Location: `src/profile/edit.ts:25`, `src/utils/profile-validator.ts`

2. **No Privacy Controls**: All profiles are public
   - Severity: High

3. **Hard-coded S3 Configuration**: S3 bucket hard-coded
   - Severity: Low
   - Location: `src/profile/avatar.ts:40`
```

#### Step 3.3: Add Refactoring Plan

Claude appends the Refactoring Plan section to the design draft:

```markdown
## Refactoring Plan

### Purpose and Background

**Why Refactoring is Needed:**

The user profile module lacks proper documentation and has technical debt that must be addressed before adding privacy controls (requested feature).

### Current State Analysis

**Problems Identified:**

1. **Inconsistent Validation** (Severity: Medium)
   - Description: Validation logic is split between controllers and utils, leading to duplication
   - Impact: Bug-prone when adding new validation rules
   - Location: `src/profile/edit.ts:25-40`, `src/utils/profile-validator.ts:5-40`

2. **No Privacy Controls** (Severity: High)
   - Description: All profiles are publicly visible, no privacy settings
   - Impact: Cannot implement requested privacy feature without major changes

3. **Hard-coded Configuration** (Severity: Low)
   - Description: S3 bucket name is hard-coded
   - Impact: Difficult to use different buckets for dev/staging/prod
   - Location: `src/profile/avatar.ts:40`

**Code Quality Metrics:**
- Code duplication: 30% (validation logic repeated)
- Test coverage: 40% (target: 80%)

### Refactoring Strategy

**Goals:**

1. Centralize validation logic
2. Add privacy control layer
3. Externalize configuration

**Approach:**

- **Pattern:** Service Layer refactoring + Configuration Injection
- **Technique:** Extract validation to dedicated service, introduce privacy service

### Migration Plan

**Phase 1: Preparation** (Estimated: 2 days)

- **Task 1.1:** Add integration tests for current behavior
- **Task 1.2:** Document current API contracts

**Phase 2: Refactoring** (Estimated: 4 days)

- **Task 2.1:** Create `ValidationService` and consolidate validation logic
- **Task 2.2:** Add `PrivacyService` for privacy controls
- **Task 2.3:** Externalize S3 configuration to environment variables

**Phase 3: Validation** (Estimated: 1 day)

- **Task 3.1:** Verify all tests pass
- **Task 3.2:** Code review

**Phase 4: Deployment** (Estimated: 1 day)

- **Task 4.1:** Deploy to staging
- **Task 4.2:** Deploy to production

### Impact Analysis

**Breaking Changes:**

- [ ] None (backward compatible)

**Affected Components:**

| Component | Type | Impact | Mitigation |
|:--|:--|:--|:--|
| `ProfileEditService` | Internal | Validation moved to new service | Update imports |

### Testing Strategy

**Unit Tests:**
- Test `ValidationService` in isolation

**Integration Tests:**
- Test full profile update flow

### Success Criteria

- [ ] Validation logic centralized
- [ ] Privacy service implemented
- [ ] Configuration externalized
- [ ] Test coverage > 80%
```

### Phase 4: Validation

```
✅ Reverse-engineered spec generated (persistent): .sdd/specification/user-profile_spec.md
✅ Reverse-engineered design draft generated (temporary): .sdd/task/72/design-draft.md
✅ Refactoring plan added to the design draft
```

### Phase 5: Next Steps

```
Next steps:
1. Review generated documents:
   - .sdd/specification/user-profile_spec.md (persistent)
   - .sdd/task/72/design-draft.md (temporary draft)

2. Update documents to reflect true original intent (if known)

3. Run `/task-breakdown user-profile 72` to break down refactoring

4. Execute with `/implement user-profile`

5. After implementation, run `/task-cleanup user-profile` to append the settled decisions to
   .sdd/adr/user-profile.md and delete .sdd/task/72/
```

## Notes

- In Case B, Claude generates the spec and the design draft from scratch by analyzing code
- The two artifacts have different lifetimes: the spec is persistent, the design draft is deleted after
  implementation once its decisions have been appended to `adr/user-profile.md`
- Nothing is written to `specification/{feature}_design.md` — that path is no longer a persistent document
- Users should review and correct any misunderstandings before proceeding
