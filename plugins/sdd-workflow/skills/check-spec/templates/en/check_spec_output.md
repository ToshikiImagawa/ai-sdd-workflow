## Design Doc & Implementation Consistency Check

### Target

- Design Doc: `.sdd/specification/[{parent}/]{feature}_design.md`
- Implementation: `{implementation_files}`

### Consistency Check Results

#### Summary

| Category              | Status  | Details                  |
|:----------------------|:--------|:-------------------------|
| API Implementation    | 🟢 OK   | All APIs implemented     |
| Data Model            | 🔴 NG   | {count} mismatches found |
| Module Structure      | 🟢 OK   | Follows design           |
| Implementation Status | 🟡 Warn | {count} items incomplete |

#### 🔴 Mismatches

##### Data Model: User Type Definition

**Design Doc**:

```typescript
interface User {
    id: string;
    name: string;
    email: string;
}
```

**Implementation**: `src/models/user.ts:10`

```typescript
interface User {
    id: number;  // ← Different type
    name: string;
    email: string;
}
```

**Impact**: Type mismatch causes runtime errors

**Fix Suggestion**: Change `id` to `string` type

---

#### 🟡 Incomplete Items

##### API: Password Reset Function

**Designed**: Yes (Design Doc line 45)

**Implemented**: Not found

**Recommendation**: Implement or remove from design doc

---

### Implementation Status Update

Updated design doc implementation status:

- [x] User Login API → 🟢 Implemented
- [x] Logout API → 🟢 Implemented
- [ ] Password Reset API → 🔴 Not Implemented

### Next Actions

1. Fix mismatches:
    - Update `src/models/user.ts:10` type definition
2. Implement incomplete items:
    - Implement Password Reset API or remove from design

### Verification Commands

```bash
# Re-check after fixes
/check_spec {feature}

# Full review (document consistency + quality)
/check_spec {feature} --full
```
