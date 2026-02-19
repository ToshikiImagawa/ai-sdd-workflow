# SDD CLI

AI-SDD Workflow のドキュメント管理 CLI ツール

## 機能

- **インデックス構築**: `.sdd/` 配下のドキュメントを SQLite FTS5 でインデックス化
- **全文検索**: キーワード、feature ID、タグによる高速検索
- **依存関係可視化**: ドキュメント間の依存関係を Mermaid 図として生成

## キャッシュディレクトリ

インデックスと可視化結果は **XDG Base Directory** 仕様に従い、以下のディレクトリに保存されます：

```
~/.cache/sdd-cli/
├── my-project.a1b2c3d4/          # プロジェクト別キャッシュ
│   ├── index.db                  # SQLite FTS5 インデックス
│   ├── metadata.json             # インデックスメタデータ
│   ├── dependency-graph.mmd      # Mermaid 依存関係図
│   └── search-results.json       # 検索結果（スキル実行時）
└── another-project.e5f6g7h8/
    └── ...
```

**命名規則** (GitHub Copilot式):
- フォーマット: `{project-name}.{8-char-hash}`
- `project-name`: プロジェクトディレクトリ名
- `8-char-hash`: パス衝突回避用のハッシュ値

**メリット**:
- プロジェクトが一目でわかる
- 不要なキャッシュの削除が容易
- Claude Code 非依存で、他のエディタやCI/CDでも利用可能

## インストール

```bash
uv pip install -e .
```

## 使用方法

### インデックス構築

```bash
sdd-cli index --root .sdd
```

### ドキュメント検索

```bash
# キーワード検索
sdd-cli search "ログイン機能"

# Feature ID で検索
sdd-cli search --feature-id user-login

# タグで検索
sdd-cli search --tag authentication

# ディレクトリで絞り込み
sdd-cli search "認証" --dir specification

# JSON 形式で出力
sdd-cli search "ログイン" --format json --output results.json
```

### 依存関係可視化

```bash
# 全体の依存関係図を生成
sdd-cli visualize

# 特定ディレクトリのみ
sdd-cli visualize --filter-dir specification

# 特定機能のみ
sdd-cli visualize --feature-id user-login
```

### キャッシュ管理

```bash
# キャッシュ一覧表示
sdd-cli cache list

# JSON形式で表示
sdd-cli cache list --format json

# 特定プロジェクトのキャッシュを削除（ドライラン）
sdd-cli cache clean --project 'old-project*' --dry-run

# 特定プロジェクトのキャッシュを削除
sdd-cli cache clean --project slide-presentation-app

# すべてのキャッシュを削除
sdd-cli cache clean --all
```

## 開発

### テスト実行

```bash
pytest
```

### パッケージビルド

```bash
uv build
```
