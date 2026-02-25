## 適用結果

- **成功**: {success_count} ファイル更新
- **スキップ**: {skip_count} ファイル（Front Matter 既存）
- **失敗**: {error_count} ファイル

### 更新されたファイル

{updated_files_list}

### 次のステップ

1. 更新されたファイルを確認
2. 必要に応じてメタデータを調整（priority, risk, tags, category）
3. 変更をコミット：
   ```bash
   git add .
   git commit -m "[docs] Front Matter を既存ドキュメントに追加"
   ```
