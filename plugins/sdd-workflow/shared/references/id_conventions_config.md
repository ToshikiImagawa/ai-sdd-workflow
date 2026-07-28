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
