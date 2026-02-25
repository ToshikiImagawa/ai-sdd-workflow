# Front Matter 推奨レポート

## サマリー

- **スキャンした総ドキュメント数**: {total_count}
- **Front Matter あり**: {with_fm_count}
- **Front Matter なし**: {without_fm_count}

{recommendations_section}

## 次のステップ

### オプション A: 自動適用

以下のコマンドを実行して、すべてのドキュメントに Front Matter を自動追加します：

```
/recommend-front-matter --apply
```

**注意**: ファイルを直接変更します。適用前に Git コミットを推奨します。

### オプション B: 手動適用

1. 上記の推奨内容を確認
2. 推奨された YAML ブロックをドキュメントにコピー＆ペースト
3. 必要に応じてメタデータを調整（特に `depends-on`, `tags`, `category`）

## Front Matter のメリット

Front Matter を追加することで以下が可能になります：

- **構造化検索**: type, status, tags, category でドキュメントをフィルタリング
- **相互参照検証**: `/check-spec --full` で `depends-on` 参照を検証
- **依存関係追跡**: ドキュメント間の依存関係を可視化し、変更の影響を追跡
- **自動化ツール**: ドキュメント管理ツールのサポート向上

## 重要な注意事項

- Front Matter は**オプション**です（後方互換性あり）
- 推論されたメタデータは手動調整が必要な場合があります
- 適用前に推奨内容を確認してください
- `--apply` 使用前に必ず Git にコミットしてください
