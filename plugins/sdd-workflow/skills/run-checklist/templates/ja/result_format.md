# 結果フォーマットテンプレート

## チェックリスト項目の更新形式

検証が成功した場合：

```markdown
- [x] {元の項目テキスト} ✅ 検証済み: {YYYY-MM-DD}
```

検証が失敗した場合：

```markdown
- [ ] {元の項目テキスト} ❌ 失敗: {YYYY-MM-DD}
```

手動検証が必要な場合：

```markdown
- [ ] {元の項目テキスト} ⚠️ 手動検証が必要
```

検証がスキップされた場合：

```markdown
- [ ] {元の項目テキスト} ⏭️ スキップ: {理由}
```

## 自動検証結果ブロック

検証されたCHKセクションの後に追加：

```markdown
**自動検証結果**:
- コマンド: `{実行されたコマンド}`
- ステータス: {PASSED | FAILED | SKIPPED}
- {該当する場合は追加のメトリクス}
- 実行日時: {YYYY-MM-DD HH:mm:ss}
```

### カテゴリ別の例

#### テストレビュー (CHK-5xx)

```markdown
**自動検証結果**:
- コマンド: `npm test -- --coverage`
- ステータス: PASSED
- テスト: 45件成功、0件失敗
- カバレッジ: 行 85.2%、分岐 78.5%
- 実行日時: 2024-01-15 10:30:45
```

#### 実装レビュー (CHK-4xx)

```markdown
**自動検証結果**:
- コマンド: `eslint . && tsc --noEmit`
- ステータス: PASSED
- Lintエラー: 0
- 型エラー: 0
- 実行日時: 2024-01-15 10:31:20
```

#### セキュリティレビュー (CHK-7xx)

```markdown
**自動検証結果**:
- コマンド: `npm audit`
- ステータス: PASSED
- 脆弱性: critical 0、high 0、moderate 2
- 実行日時: 2024-01-15 10:32:00
```

## 失敗詳細フォーマット

検証が失敗した場合、詳細を含める：

```markdown
**自動検証結果**:
- コマンド: `npm test`
- ステータス: FAILED
- テスト: 42件成功、3件失敗
- 失敗したテスト:
  - `auth.test.ts`: "should validate token expiry"
  - `user.test.ts`: "should reject invalid email"
  - `api.test.ts`: "should return 401 for unauthenticated"
- 実行日時: 2024-01-15 10:30:45
```
