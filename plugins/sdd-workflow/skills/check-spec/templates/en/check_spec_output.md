## Design Doc & Implementation Consistency Check

### Target

- Design Doc: `${SDD_SPECIFICATION_PATH}/[{parent}/]{feature}_design.md`
- Implementation: `{implementation_files}`

### Consistency Check Results

#### Summary

| Category              | Status  | Details                  |
|:----------------------|:--------|:-------------------------|
| API Implementation    | 🟢 OK   | All APIs implemented     |
| Data Model            | 🔴 NG   | {count} mismatches found |
| Module Structure      | 🟢 OK   | Follows design           |
| Literal Values        | 🟡 Warn | {count} value drifts     |
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

#### 🟡 Value Drift

##### {value_name} (e.g., rag_confidence_threshold)

```
[WARN] Value drift detected: {value_name}
  spec: {spec_value} ({spec_section}, {requirement_id})
  design: {design_value} ({design_section})
  {implementation_file}: {impl_value} ← drift
```

**Impact**: {impact description, e.g., gate threshold looser than specified}

**Fix Suggestion**: Align {implementation_file} with the spec value, or update spec/design if the implementation is correct

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
