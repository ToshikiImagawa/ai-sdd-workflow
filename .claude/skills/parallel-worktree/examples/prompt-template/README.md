# prompt-template の例

`parallel-worktree` skill の `spawn.sh` に `--prompt-template` で渡す**プロンプトテンプレートのサンプル集**です。
各 worktree で起動する子セッションが、起動直後に読み込む詳細指示の雛形になります。

## 設計原則: テンプレはプロジェクト側で決める

**プロンプトの中身は skill 実行側（＝各プロジェクト）で決まります。** 規約・lint・PR 手順・利用スキルは
プロジェクトごとに異なるため、skill ディレクトリに特定プロジェクト向けの正式テンプレを置くのは不適切です。

- **skill が提供するのは「例」だけ** — この `examples/` 配下のファイルはあくまでサンプル／出発点です。
- **実際に使うテンプレはプロジェクト側に置く** — サンプルをコピーし、自プロジェクトの規約に合わせて
  編集したものを、プロジェクト管理下の任意の場所（多くは gitignore 対象の作業ディレクトリ）に配置します。
- **`--prompt-template` は必須** — この設計を徹底するため、`spawn.sh` はデフォルトのテンプレを持ちません。
  `--prompt-template <path>` の指定が無い場合はエラーで停止します。

## envsubst で置換される 5 変数

テンプレ内では次の 5 変数が `spawn.sh` により `envsubst` で実値置換されます。必ず `${VAR}` 形式で記述してください
（`{{VAR}}` など Mustache 風は置換対象外）。

| 変数 | 内容 | 例 |
|---|---|---|
| `${ISSUE_NUMBER}` | issue 番号 | `42` |
| `${ISSUE_ID}` | spawn 引数の `<ref>` をそのまま | `[bug]` or `42` |
| `${ISSUE_TITLE}` | issue title | `[bug] リンク切れ修正` |
| `${BRANCH}` | 命名された branch | `feat/42-fix-typo` |
| `${WORKTREE_PATH}` | worktree の絶対パス | `/path/.claude/worktrees/42-fix-typo` |

## サンプル一覧

| ファイル | 用途 |
|---|---|
| [generic.md](generic.md) | どのプロジェクトでも使える汎用雛形。規約・lint・PR 手順を「リポジトリの記述を確認して従う」形にしてあり、ハードコードを避けている。 |
| [generate-spec.md](generate-spec.md) | AI-SDD ワークフロー（本リポジトリ）向けの spec/design 生成テンプレの例。プロジェクト固有テンプレの書き方の参考。 |

## 使い方

1. 目的に近いサンプルをコピーする。
2. 自プロジェクトの規約（コミット prefix、lint/test コマンド、PR 作成手順、利用スキル等）に合わせて編集する。
3. `spawn.sh` に `--prompt-template` で渡す。

```bash
# サンプルをプロジェクトの作業ディレクトリにコピーして編集
cp .claude/skills/parallel-worktree/examples/prompt-template/generic.md /path/to/your/my-template.md
# 編集後、spawn 時に指定
.claude/skills/parallel-worktree/scripts/spawn.sh \
  --prompt-template /path/to/your/my-template.md \
  42:fix-typo 43:add-agent
```

本リポジトリで spec/design を生成する場合は、[generate-spec.md](generate-spec.md) をそのまま
`--prompt-template` に指定できます。
