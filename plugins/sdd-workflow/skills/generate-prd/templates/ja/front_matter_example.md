# PRD フロントマター例

`references/front_matter_prd.md`（`shared/references/front_matter_prd.md`）のスキーマに従う:

```yaml
---
id: "prd-{feature-name}"
title: "{Feature Title}"
type: "prd"
status: "draft"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
sdd-version: "{plugin-version}"  # ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json から取得
depends-on: []  # Parent PRD if hierarchical
priority: "medium"  # or extract from requirements
risk: "medium"  # or extract from requirements
tags: ["{tag1}", "{tag2}"]
category: "{category}"
---
```
