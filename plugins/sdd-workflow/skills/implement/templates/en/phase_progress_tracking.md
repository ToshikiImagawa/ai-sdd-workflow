# Phase Progress Tracking Templates

## Phase 1: Foundation

````markdown
### Phase 1: Foundation

| #   | Task            | Description              | Completion Criteria | Status |
|:----|:----------------|:-------------------------|:--------------------|:-------|
| 1.1 | Directory setup | Create module structure  | Directories exist   | [x]    |
| 1.2 | Type definitions | Define core types       | Types compile       | [x]    |
| 1.3 | Test setup      | Configure test framework | Tests can run       | [x]    |
````

## Phase 2: Core Implementation

````markdown
### Phase 2: Core Implementation

| #   | Task            | Description          | Completion Criteria | Status |
|:----|:----------------|:---------------------|:--------------------|:-------|
| 2.1 | User validation | Validate user input  | Tests pass          | [x]    |
| 2.2 | Data persistence | Save to database    | Tests pass          | [ ]    |
| 2.3 | Business logic  | Core feature logic   | Tests pass          | [ ]    |
````

## Phase 3: Integration

**Purpose**: Connect components

**Tasks**:

- Service layer integration
- API endpoint wiring
- Event handling
- Middleware integration

**Verification**:

- Integration tests pass
- End-to-end flows work
- Verify spec compliance

## Phase 4: Testing

**Purpose**: Comprehensive test coverage

Read: `references/test_types.md` for test type details.

**Auto-Verification**:

- Run test suite
- Check coverage metrics
- Verify all acceptance criteria met

## Phase 5: Finishing (Polish)

**Purpose**: Final improvements

**Tasks**:

- Code cleanup
- Documentation update
- Performance optimization
- Design document update
