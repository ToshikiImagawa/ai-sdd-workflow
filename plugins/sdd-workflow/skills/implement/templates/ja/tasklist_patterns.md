# TaskList パターン

## Phase 1 タスクの作成

```
TaskCreate({
  subject: "セットアップフェーズを実行",
  description: "ディレクトリ構造の作成、型定義ファイルの作成、基本インターフェースの定義、テスト環境のセットアップ",
  activeForm: "セットアップフェーズを実行中"
})
```

## Phase 2 タスクの作成（Phase 1 に依存）

Phase 1 のタスクIDを取得した後、Phase 2 タスクを作成:

```
TaskCreate({
  subject: "テストケースを作成",
  description: "各機能の失敗するテストを作成（TDD Red）",
  activeForm: "テストケースを作成中"
})
```

作成後、TaskUpdate で依存関係を設定:

```
TaskUpdate({
  taskId: "<Phase 2 タスクID>",
  addBlockedBy: ["<Phase 1 タスクID>"]
})
```

## フェーズステータスの更新

**フェーズ開始時**:

```
TaskUpdate({
  taskId: "<対象フェーズのタスクID>",
  status: "in_progress"
})
```

**フェーズ完了時**:

```
TaskUpdate({
  taskId: "<対象フェーズのタスクID>",
  status: "completed"
})
```

## 注意事項

- `subject` は命令形で短く簡潔に（例: "セットアップを実行", "テストを作成"）
- `activeForm` は進行形で（例: "セットアップを実行中", "テストを作成中"）
- すべてのタスクは `pending` ステータスで作成される
- 依存関係は TaskCreate 後に TaskUpdate で設定する
