---
type: regex
target: last_message
pattern: "(High|高) */ *(Medium|中) */ *(Low|低)"
match: not_contains
---

The template placeholder listing all three levels must not be echoed verbatim (source: vibe-detection_spec 3.1.1).
