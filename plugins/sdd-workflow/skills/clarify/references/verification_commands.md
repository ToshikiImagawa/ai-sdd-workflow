# Verification Commands

```bash
# Re-scan to verify clarity improvements
/clarify {feature-name}

# Consistency check (verify updated specifications)
# Only once a spec exists under ${SDD_SPECIFICATION_PATH}/ — /clarify also runs on a PRD alone,
# and /check-spec exits with an error when that directory is absent. Run /generate-spec first in
# that case.
/check-spec {feature-name} --full
```
