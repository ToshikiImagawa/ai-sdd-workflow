---
paths:
  - ".sdd/**"
---

# YAML Front Matter

`.sdd/` 配下の各ドキュメントにはオプションでYAML front matterを追加できる。機械的な検索・フィルタリングに活用される。

| ドキュメント種別 | `type`                 | `id` パターン         | 固有フィールド                                                        |
|:---------|:-----------------------|:------------------|:---------------------------------------------------------------|
| PRD      | `"prd"`                | `"prd-{name}"`    | `priority`, `risk`                                             |
| Spec     | `"spec"`               | `"spec-{name}"`   | `sdd-phase: "specify"`                                         |
| Design   | `"design"`             | `"design-{name}"` | `sdd-phase: "plan"`, `impl-status`                             |
| Task     | `"task"`               | `"task-{name}"`   | `sdd-phase: "tasks"`, `ticket`                                 |
| Impl Log | `"implementation-log"` | `"impl-{name}"`   | `sdd-phase: "implement"`, `ticket`, `completed`, `implementer` |

共通フィールド: `id`, `title`, `type`, `status`, `created`, `updated`, `depends-on`, `tags`, `category`

**依存方向**: `depends-on` は上流方向のみ。下位ドキュメントへの参照は持たない。

```
prd ← spec (depends-on: prd) ← design (depends-on: spec) ← task (depends-on: design)
```

- 階層構造の場合: `id` にパスを含める（例: `"spec-auth-user-login"`）
- feature 名自体が type プレフィックスで始まる場合（例: feature 名 `prd-generation`）は、二重接頭辞
  （`"prd-prd-generation"`）とせず feature 名をそのまま `id` とする（例: `"prd-generation"`）
- front matterなしの既存ドキュメントも引き続き有効（後方互換）
