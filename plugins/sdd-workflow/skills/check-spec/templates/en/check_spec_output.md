## Spec & Implementation Consistency Check

### Target

- Spec: `${SDD_SPECIFICATION_PATH}/[{parent}/]{feature}[_spec].md`
- Design draft (auxiliary, only if present): `${SDD_TASK_PATH}/{ticket-number}/design-draft.md`
  (selection basis: `{design_draft_scope}`)
- Implementation: `{implementation_files}`

> Omit the design draft line when no draft exists — that is the normal state after implementation
> completes, not a finding.
> When `design_draft_scope` is `unscoped`, state instead that {n} design drafts were found but none could be
> tied to this run, list them, and recommend re-running with `--ticket <number>` (or `--ticket=<number>`).

### Consistency Check Results

#### Summary

| Category              | Status  | Details                  |
|:----------------------|:--------|:-------------------------|
| Public API            | 🟢 OK   | All APIs implemented     |
| Data Model            | 🔴 NG   | {count} mismatches found |
| Behavior              | 🟢 OK   | Matches the spec         |
| Literal Values        | 🟡 Warn | {count} value drifts     |
| Implementation Status | 🔴/🟡/🔵 | {critical_count} regression / {warning_count} undecidable / {info_count} expected-not-yet-implemented |
| adr ↔ Implementation  | ⚪ Not checked | Out of this check's scope — adr drift is not detected automatically |

> Add a **Module Structure** row only when a design draft was loaded.
> The adr row is always present: it keeps the unchecked scope visible instead of implying adr was verified.

#### Downgrade Summary (always shown)

`impl-status` moves "specified but not implemented" findings out of Critical. In v4.x these were unconditional
Criticals, and v4-era specs carry no `impl-status`, so report the counts explicitly:

| Downgrade                                          | Count | Specs                       |
|:---------------------------------------------------|:------|:----------------------------|
| Critical → 🟡 Warning (`impl-status` absent)        | {n}   | `{spec_paths}`              |
| Critical → 🔵 Info (`not-implemented`/`in-progress`) | {n}   | `{spec_paths}`              |

> These {total} findings are **not** resolved defects — they are undecidable or deferred, and the Critical
> count above excludes them. Print the table with zeros when nothing was downgraded.

#### Document Consistency & Quality Review (only with `--full`)

The `spec-reviewer` agent's comprehensive review is reported here.

| Perspective                | Result                                            | Count |
|:---------------------------|:--------------------------------------------------|:------|
| PRD ↔ spec traceability    | 🟢 Consistent / 🔴 Inconsistent                    | {n}   |
| spec ↔ adr consistency     | 🟢 Consistent / 🔴 Inconsistent / ⚪ Not applicable | {n}   |
| CONSTITUTION.md compliance | 🟢 Compliant / 🔴 Violation                        | {n}   |
| Completeness               | ✅ Good / ⚠️ Needs improvement                     | {n}   |
| Clarity                    | ✅ Good / ⚠️ Needs improvement                     | {n}   |

> Print ⚪ Not applicable for spec ↔ adr when the resolved decision-log list (`CHECK_SPEC_ADR_FILES`) is
> empty — the feature's decisions are not recorded yet. Never print 🟢 Consistent for an area that was not
> checked. A fix for an inconsistency goes into the spec, or into a **new appended** adr entry carrying a
> `Supersedes` item; never edit or delete an existing entry.

#### 🔴 Mismatches

##### Data Model: User Type Definition

**Spec**:

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
  {implementation_file}: {impl_value} ← drift
```

**Impact**: {impact description, e.g., gate threshold looser than specified}

**Fix Suggestion**: Align {implementation_file} with the spec value, or update the spec if the implementation is correct

---

#### Unimplemented Functions

A spec-documented function with no matching implementation is classified by the spec's `impl-status`:

| Function            | Spec Location                        | Spec `impl-status` | Classification            |
|:---------------------|:---------------------------------------|:----------------------|:----------------------------|
| Password Reset API  | spec §{section} ({requirement_id})   | `implemented`          | 🔴 Regression              |
| {feature_name}      | spec §{section} ({requirement_id})   | `not-implemented`      | 🔵 Expected (not due yet)  |
| {feature_name}      | spec §{section} ({requirement_id})   | Not set               | 🟡 Undecidable             |

**🔴 Regression example — API: Password Reset Function**

**Impact**: The spec declares this as implemented, but no matching code was found — likely a regression
(removed, or the field was set before the implementation actually landed).

**Recommendation**: Restore the implementation, or correct the spec's `impl-status` if it was never actually
implemented (and document why in the spec/adr). For a 🟡 Undecidable row, recommend this sequence instead:
run `/recommend-front-matter` to list the specs missing `impl-status` (it reports them but never writes a
value), confirm from the code whether each spec's behavior is implemented, then set `impl-status` by hand to
the value that matches reality. A 🔵 Expected row needs no action.

---

### Next Actions

1. Fix mismatches:
    - Update `src/models/user.ts:10` type definition
2. Address regressions (🔴 Unimplemented):
    - Restore Password Reset API, or correct its spec `impl-status`
3. Set `impl-status` by hand on the specs flagged as undecidable (🟡), after checking each one's real
   implementation state — `/recommend-front-matter` lists them but does not fill in the value
4. Review `${SDD_ADR_PATH}/{feature}.md` manually for decisions the implementation no longer follows
   (not covered by this check) — record any reversal as a **new** adr entry with a `Supersedes` item

### Verification Commands

```bash
# Re-check after fixes
/check-spec {feature}

# Re-check with a specific ticket's design draft as auxiliary input
/check-spec {feature} --ticket {ticket-number}

# Full review (document consistency + quality)
/check-spec {feature} --full
```
