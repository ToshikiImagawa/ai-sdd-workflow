# 法則 移行表: {{FEATURE}}

- spec: {{SPEC_PATH}}（`{{SPEC_ID}}`）
- 法則ファイル: {{LAWS_FILE}}（承認: `{{APPROVAL_STATE}}`）
- 生成日: {{DATE}}（`/draft-laws migrate`。読み取り専用: 法則ディレクトリと spec は変更していない）
- 差分テストの出力先: `{{TESTS_TARGET}}`

## 実装の所在（spec 3.1.5）

| 固定元 | パス | 法則化可 | 理由 |
|:--|:--|:--|:--|
| `{{IMPL_SOURCE}}` | {{IMPL_PATHS}} | {{LAWIFIABLE}} | {{IMPL_REASON}} |

{{IMPL_OF_PROPOSAL}}

## 分類

| 法則 | 出典 | 分類 | `for` | kind 推定 | 対応テスト案 | 備考 |
|:--|:--|:--|:--|:--|:--|:--|
| {{LAW_NAME}} | §{{SECTION}} | {{CLASSIFICATION}} | {{HAS_FOR}} | {{KIND_GUESS}} | {{SUGGESTED_TEST}} | {{NOTE}} |

合計: keep {{KEEP}} / to_tests {{TO_TESTS}} / prose_delete {{PROSE_DELETE}}

{{HUMAN_REVIEW_NOTE}}

## 人の作業

| 分類 | 作業 |
|:--|:--|
| `keep` | なし。法則は `LAWS.bend` に残り、proof ゲートで証明する。 |
| `to_tests` | 差分テストを書く（`/draft-laws draft` が同じ命題をそこへ振り分ける。または `# source:` 行付きで `{{TESTS_TARGET}}` に写す）→ `pytest` を通す → `LAWS.bend` から法則を削除する。本文が変わるため承認は失効する: 新しいハッシュ（`run-verification.py proof --print-laws-hash --laws-dir {{LAWS_DIR}}`）で `# approved:` 行を書き直し、`PROOF.bend` を更新する。ここに挙がった空入力・単一要素・単位元の法則は例外（FR-014）として Bend に残す。 |
| `prose_delete` | 実装が散文のため法則を実装に結べない: 法則ディレクトリを削除し、spec の front matter から `laws:` / `laws-status` を外し、理由（`prose_implementation`）を ADR に記録する。その性質の検証先はスキル評価であり Bend ではない。 |
