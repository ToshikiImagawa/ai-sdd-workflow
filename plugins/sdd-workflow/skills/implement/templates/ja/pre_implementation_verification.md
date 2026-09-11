# 実装前検証

## ドキュメントの読み込みと検証

```
1. タスク分解を読み込み: ${SDD_TASK_PATH}/{ticket}/tasks.md
2. 技術設計ドラフトを読み込み: ${SDD_TASK_PATH}/{ticket}/design-draft.md
3. v4.x の永続設計書を読み込み（プロジェクトに存在する場合）:
   ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_design.md
4. 抽象仕様書を読み込み: ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}.md または {feature}_spec.md
5. PRDを読み込み（存在する場合）: ${SDD_REQUIREMENT_PATH}/[{path}/]{feature}.md
```

**v4.x の永続設計書（`specification/*_design.md`）について**: AI-SDD v4.x から始まったプロジェクトには
これが残っている場合がある。これらは**依然として有効**であり、**補助入力として読み、不在は正常な状態として
扱う**。新規作成はしない（新しい技術設計は `task/{ticket-number}/design-draft.md` に書く）。既存ファイルを
命名規則違反として報告したり削除を提案してはならない。その決定内容が `adr/{feature}.md` に移行されるまで
残しておいてよい。手順 2 で `design-draft.md` が見つからず手順 3 でこのファイルが見つかった場合は、
それを設計入力として実装を進める（ドラフトの再生成を促さない）。

**命名規則の違いに注意**:

- **requirement 配下**: サフィックスなし（`index.md`, `{feature-name}.md`）
- **specification 配下**: `_spec` サフィックスは任意（`index_spec.md`, `{feature-name}_spec.md`、または
  サフィックスなし）。どちらの形式でも手順 4 を満たす
- **task 配下**: 技術設計ドラフトは `design-draft.md` の固定ファイル名。チケット単位のパスであり、
  抽象仕様書のフラット／階層構造とは独立している
