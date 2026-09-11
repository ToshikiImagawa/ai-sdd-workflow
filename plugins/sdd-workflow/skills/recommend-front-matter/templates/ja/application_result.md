## 適用結果

- **成功**: {success_count} ファイル更新
- **スキップ**: {skip_count} ファイル（Front Matter 既存）
- **失敗**: {error_count} ファイル
- **`impl-status` が未設定の spec**: {specs_missing_impl_status_count} 件（このスキルは書き込まない。下記参照）

### 更新されたファイル

{updated_files_list}

### `impl-status` の手動追加が必要な spec

{specs_missing_impl_status_list}

このスキルは `impl-status` を書き込まない。実装を確認しないため値を知り得ず、誤った `"not-implemented"` は
退行を報告するどころか隠してしまう。各 spec と実装を照合し、`sdd-phase` の行の後に
`impl-status: "implemented"` / `"in-progress"` / `"not-implemented"` のいずれかを追加すること。

### 次のステップ

1. 更新されたファイルを確認
2. 必要に応じてメタデータを調整（priority, risk, tags, category）
3. 上記の spec に `impl-status` を手動で追加
4. 変更をコミット：
   ```bash
   git add .
   git commit -m "[docs] Front Matter を既存ドキュメントに追加"
   ```
