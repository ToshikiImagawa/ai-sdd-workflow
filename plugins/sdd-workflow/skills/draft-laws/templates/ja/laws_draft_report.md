# 法則案 抽出レポート: {{FEATURE}}

- spec: {{SPEC_PATH}}（`{{SPEC_ID}}`）
- 出力: {{OUTPUT_FILE}}
- 生成日: {{DATE}}
- `laws.max_laws`: {{MAX_LAWS}}

## 採用した法則

| 法則 | 出典 | 命題 |
|:--|:--|:--|
| {{LAW_NAME}} | §{{SECTION}} | {{DESCRIPTION}} |

## モデル API

参照モデルが実装すべき関数（法則ファイルの `# model-api:` 行の写し。`model` 段階はこれに従う）。型は Bend の記法で書く（リストは `List<&2, T>`）。`for` の変数は 1 行に 1 つ宣言する。

固定元: `{{MODEL_API_SOURCE}}`（`spec` / `main.bend` / `unfixed`。`unfixed` は「未固定・要確認」: 承認時に人が API を確認する）。

| 関数 | 引数 | 戻り値 | 符号化の注記 |
|:--|:--|:--|:--|
| Model.{{FN}} | {{ARGS}} | {{RETURNS}} | {{ENCODING}} |

## 差分テストへ回した候補

点命題（`for` 量化を持たない。判定表 1 行ずつ）。`{{TESTS_TARGET}}` に書き、参照モデルではなく実装（`impl-of:` {{IMPL_PATHS}}）に対して assert する。プロジェクトの `pytest` で実行する。既存のテストファイルは上書きせず、下に差分を示す。

| 候補 | 出典 | テスト関数 | 命題 |
|:--|:--|:--|:--|
| {{CANDIDATE}} | §{{SECTION}} | {{SUGGESTED_TEST}} | {{DESCRIPTION}} |

## 未採用の候補

| 候補 | 出典 | 理由（上限超過 / 自明法則 / 重複 / unbounded_nat） |
|:--|:--|:--|
| {{CANDIDATE}} | §{{SECTION}} | {{REASON}} |

## 法則化しない理由

| 節 | 理由（IO 依存 / 性能 / 散文のみ / 節番号なし / prose_implementation） |
|:--|:--|
| §{{SECTION}} | {{REASON}} |

## 静的チェック

`draft_laws.py check` の結果（法則ファイルと `--tests`）: error {{ERRORS}} 件、warning {{WARNINGS}} 件。

| コード | 重大度 | 法則 | メッセージ |
|:--|:--|:--|:--|
| {{CODE}} | {{SEVERITY}} | {{LAW}} | {{MESSAGE}} |

## 次の手順（人が行う）

1. 法則をレビューし、法則ファイルの先頭コメント部の末尾（最初の `import` より上）に承認行を追記する:
   `# approved: YYYY-MM-DD <承認者> sha256:{{CURRENT_HASH}}`
   （現在の内容ハッシュ: `{{CURRENT_HASH}}`。再取得は `run-verification.py proof --print-laws-hash --laws-dir {{LAWS_DIR}}`）
2. spec の front matter への追加案（未適用。人が追加する）。`laws:` を追加するまでは、proof ゲートは未承認判定（SKIPPED・判定表 #5）より先に孤児 laws（FAIL・判定表 #4）を報告する:
   ```yaml
   laws: ["{{LAWS_DIR_SDD_RELATIVE}}"]
   laws-status: drafted
   ```
3. 承認後に `laws-status: approved` へ更新し、`/draft-laws model {{FEATURE}}` を実行する。
4. `/run-checklist {{FEATURE}} <ticket> --category proof` で検査する。PASS 後に人が `laws-status: proven` へ更新する。
5. 差分テストを実行する（`pytest {{TESTS_TARGET}}`）。proof ゲートとは独立で、実装を検証する。
6. 実装の所在: `{{IMPL_SOURCE}}`。{{IMPL_OF_PROPOSAL}}
