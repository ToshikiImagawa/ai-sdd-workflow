# id_conventions Configuration Example

Example `.sdd-config.json` `id_conventions` section used by requirement-analyzer's naming convention validation:

```json
{
  "id_conventions": {
    "prd_functional": "^FR_[A-Z]+_\\d{3}$",
    "spec_functional": "^FR-[A-Z]+-\\d{3}'?$",
    "spec_refined_relation": "^FR-{domain}-{prd_num}'$"
  }
}
```

## PRD-Level ID Format Resolution

Determine the ID format for UR/FR/NFR/IR/DC before generating or validating any PRD-level requirement ID:

1. From `id_conventions` in `.sdd-config.json` (PRD-level keys below), derive each type's ID format from its regex
   (e.g. `^UR_\d{3}$` → `UR_xxx`).
2. **Fallback**: if `.sdd-config.json` or a specific key is missing, default to the format below. Use the
   resolved format consistently for every ID produced or checked.

| Type                       | `id_conventions` Key | Default Format |
|:---------------------------|:----------------------|:----------------|
| User Requirement           | `prd_user`            | `UR_xxx`        |
| Functional Requirement     | `prd_functional`      | `FR_xxx`        |
| Non-Functional Requirement | `prd_nonfunctional`   | `NFR_xxx`       |
| Interface Requirement      | `prd_interface`       | `IR_xxx`        |
| Design Constraint          | `prd_constraint`      | `DC_xxx`        |

PRD-level IDs use underscores. Spec-level IDs (`spec_functional`/`spec_nonfunctional`) are hyphenated (default
`FR-xxx`/`NFR-xxx`) and must not be conflated with the PRD-level formats above.
