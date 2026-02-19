# SDD CLI

AI-SDD Workflow のドキュメント管理 CLI ツール

## 機能

- **インデックス構築**: `.sdd/` 配下のドキュメントを SQLite FTS5 でインデックス化
- **全文検索**: キーワード、feature ID、タグによる高速検索
- **依存関係可視化**: ドキュメント間の依存関係を Mermaid 図として生成

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

## 開発

### テスト実行

```bash
pytest
```

### パッケージビルド

```bash
uv build
```
