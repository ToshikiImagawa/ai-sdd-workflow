---
type: regex
target: last_message
pattern: "^[ \\t]*(?:#{2,4} |[-*] |\\*\\*)*(Risk Level|リスクレベル)\\**[:：]\\** *(🔴 |🟡 |🟢 )?(High|Medium|Low|高|中|低)\\b"
flags: m
match: "count:1"
---

Exactly one risk-level line (heading, bold or list item — the layout is the template's business), naming
exactly one level (source: vibe-detection_spec 3.1.1).
