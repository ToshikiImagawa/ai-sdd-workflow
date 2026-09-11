# Document Consistency Check Results Template

This template is the output format for document consistency check results.

---

## Document Consistency Check Results

### Target Documents

| Document | Path                                          | Last Updated |
|:---------|:----------------------------------------------|:-------------|
| PRD      | `${SDD_REQUIREMENT_PATH}/{feature-name}.md`          | YYYY-MM-DD   |
| spec     | `${SDD_SPECIFICATION_PATH}/{feature-name}_spec.md`   | YYYY-MM-DD   |
| adr      | `${SDD_ADR_PATH}/{feature-name}.md`                  | YYYY-MM-DD   |

### Coverage / Not Checked

| Item                       | Value                                                                       |
|:---------------------------|:----------------------------------------------------------------------------|
| Decision-record source     | `adr/` / legacy `*_design.md` (v4.x) / none                                 |
| Check areas not run        | {area} - {reason}, or "none"                                                |

> A check area that could not be run is listed here as `not checked`. Never omit it and never report it as
> `Consistent`.

### Check Results Summary

| Check Target            | Result                    | Count     |
|:------------------------|:--------------------------|:----------|
| PRD ↔ spec              | Consistent / Inconsistent | {n} items |
| spec ↔ adr              | Consistent / Inconsistent | {n} items |
| Generation (`sdd-version`) | stale: {n} / generation unknown: {n} | {n} of {n} checked |

---

### Inconsistency Details

#### PRD ↔ spec

##### 1. {Inconsistency Title}

**Type**: Missing / Contradiction / Obsolescence

**PRD States**:

```markdown
{PRD content}
```

**spec States**:

```markdown
{spec content (or "Not documented")}
```

**Recommended Action**:

- [ ] Update spec to reflect requirement
- [ ] If PRD requirement is unnecessary, remove it

> **Note**: If the type is `Contradiction`, or `Missing` in the PRD → spec direction (a new behavior no PRD
> requirement covers), always report this item as `[must]` and do **not** edit the PRD automatically. Present
> the conflicting spec change and the affected PRD requirement, and let a human decide whether to update the
> PRD, revert the spec change, or accept it as an intentional scope change.

---

#### spec ↔ adr

##### 1. {Inconsistency Title}

**Type**: Missing / Contradiction / Obsolescence

**spec States**:

```
{spec content}
```

**adr States**:

```
{adr content (or "Not documented")}
```

**Recommended Action**:

- [ ] Append a new entry to adr to capture the decision behind the spec change
- [ ] If the adr entry is now stale (the spec element it describes was changed/removed), flag it for a
      follow-up append — never rewrite the existing entry

---

> **Note**: When the feature has no adr entries and its decisions still live in a v4.x persistent
> `specification/*_design.md`, keep the same four check items but title this section
> **`spec ↔ design (v4.x legacy)`** and name the design doc under "Target Documents". The design doc is
> supplementary input: its absence is normal and is never itself a finding.

> **Note**: `spec ↔ Implementation` checks — including a legacy `*_design.md`'s module structure, interface
> definitions and technology stack against the code — are out of scope for this skill. Use `/check-spec` (the
> `impl-spec-check` feature) for those checks.

#### Generation Detection (`sdd-version`)

**Stale generation** — `sdd-version` is present but its major is lower than the current plugin major:

| Document | `sdd-version` | Current Major |
|:---------|:--------------|:--------------|
| {doc_id or path} | {sdd-version value} | {current major} |

**Generation unknown** — `sdd-version` is absent (the document predates the field, the most common migration
signal):

| Document | Note |
|:---------|:-----|
| {path} | generation unknown |

Summary line (always print both, even when one is zero): `stale: {n} / generation unknown: {n} of {n} checked`

> **Note**: Both listings are advisory — they flag candidates for manual migration review. An absent
> `sdd-version` is **not** a front matter violation, and it is never folded into the stale count. The stale
> listing can be read straight from the index (`SDD_INDEX=on`); the generation-unknown count is computed with
> one Grep for `^sdd-version:` plus one Glob even when `SDD_INDEX` is unset or `off`, so neither listing is
> ever skipped.

### Verified Consistent Items

- {Verified item 1}
- {Verified item 2}

---

### Recommended Actions (Prioritized)

1. **High Priority**: {Action}
2. **Medium Priority**: {Action}
3. **Low Priority**: {Action}

---

### Notes

- {Supplementary notes}
