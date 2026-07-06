# Constitution as Code Example

Example machine-readable JSON export of a constitution (see `/constitution export --format json`):

```json
{
  "version": "1.0.0",
  "principles": [
    {
      "id": "P1",
      "name": "Specification-First",
      "enforceable": true,
      "checks": [
        {
          "type": "file_exists",
          "pattern": ".sdd/specification/*_spec.md"
        }
      ]
    }
  ]
}
```
