# タイプ別 Front Matter フィールド

ドキュメントの `type` フィールドに応じて追加するフィールド。

**PRD** (`type: "prd"`):

```yaml
priority: "medium"
risk: "medium"
```

**Spec** (`type: "spec"`):

```yaml
sdd-phase: "specify"
```

**Design** (`type: "design"`):

```yaml
sdd-phase: "plan"
```

Spec / Design のブロックに `impl-status` を**意図的に含めていない**。このスキルはドキュメントのメタデータしか
読まず実装を確認しないため、spec の記述が実装済みかどうかを知り得ない。一見安全に見える既定値
`"not-implemented"` を実装済みのドキュメントに書き込むと、`check-spec` での退行検知が Critical から Info に
格下げされてしまう。フィールドが不足しているドキュメントとして報告し、実装の実態を確認した人間が
`implemented` / `in-progress` / `not-implemented` のいずれかを入れる。

**Task** (`type: "task"`):

```yaml
sdd-phase: "tasks"
ticket: ""
```

**ADR** (`type: "adr"`):

```yaml
status: "approved"
sdd-phase: "implement"
```

ADR の決定ログは既に確定した決定を記録するものなので、`status` は他のタイプの既定値 `"draft"` ではなく
`"approved"` とする。

`ticket` は元の `task/{ticket-number}/` に到達可能な課題管理ツールが無かった場合のみ設定する。

`supersedes`/`superseded-by` は設定しない。front matter におけるこれらは「**決定ログファイル全体**が別ファイルに
置き換えられて廃止された」ことを意味し（機能のリネーム・分割・統合）、このスキルが推論できないプロジェクト
規模の事実である。同一ファイル内で新しい決定が過去の決定を覆す場合は、そのエントリの本文
（`- **Supersedes**: ...`）に記録するものであり front matter には書かない。このスキルは本文を編集しない。

**Implementation Log** (`type: "implementation-log"`):

```yaml
sdd-phase: "implement"
ticket: ""
completed: ""
implementer: ""
```
