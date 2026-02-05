# sdd-workflow-ja

`sdd-workflow` プラグインの日本語デフォルト版です。

## 概要

このプラグインは `sdd-workflow` と同一機能を提供しますが、`SDD_LANG` のデフォルト値が `ja`（日本語）に設定されています。

エージェント、スキル、テンプレートはすべて `sdd-workflow` のものをシンボリックリンクで参照しています。唯一の違いは `session-start.sh` で `SDD_LANG` のデフォルトが `ja` になっている点です。

## インストール

```
/plugin install sdd-workflow-ja@ToshikiImagawa/ai-sdd-workflow
```

## sdd-workflow との違い

| 項目 | sdd-workflow | sdd-workflow-ja |
|:---|:---|:---|
| `SDD_LANG` デフォルト | `en` | `ja` |
| `.sdd-config.json` 自動生成時の `lang` | `en` | `ja` |
| エージェント・スキル | 独自 | sdd-workflow を参照（symlink） |

## 注意

- `.sdd-config.json` に `"lang": "en"` が明示的に設定されている場合は、そちらが優先されます
- 機能の詳細は [sdd-workflow/README.md](../sdd-workflow/README.md) を参照してください

## ライセンス

MIT License
