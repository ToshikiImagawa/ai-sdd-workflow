---
name: parallel-worktree
description: "複数の GitHub Issue を並列で実装するためのスキル。各 issue を独立した git worktree + iTerm2 タブ + Codex セッションとして起動し、ファイル衝突なしに同時実装→PR 作成まで自走させる。ユーザーが「並列で issue 実装したい」「worktree で複数まとめて」「parallel worktree」「複数 issue を一気に」「子セッション起動」「issue を分担」と言ったとき、または独立性の高い複数 issue を効率的に処理したい場面で必ず使用する。プラグイン改修とドキュメント改修など互いに非干渉なタスクの一括処理に特に有効。"
version: 0.1.0
license: MIT
user-invocable: true
argument-hint: "<ref>:<slug> [<ref>:<slug> ...]"
allowed-tools: Read, Bash, Write, Edit, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
---

# Parallel Worktree - 並列 worktree 起動スキル

GitHub Issue を **並列に** 実装するためのオーケストレーションスキル。引数で指定した複数 issue それぞれを独立した git worktree + iTerm2 タブ + Codex 子セッションとして同時起動し、各セッションが PR 作成まで自走する仕組みを提供する。

このセッション (親) はオーケストレーター役で、実際の実装は各 worktree 内の子セッションが担当する。親は spawn コマンドを実行し、競合確認・wave 設計・後片付けに専念する。

## Input

`$ARGUMENTS`

各引数は `<ref>:<slug>` 形式 (スペース区切り、可変長)。最大 3〜4 並列を推奨。

### Input Examples

```
/parallel-worktree 42:fix-typo 43:add-agent 44:update-docs
/parallel-worktree [bug]:fix-link [feat]:new-skill
/parallel-worktree --branch-prefix feat 45:session-start-fix
```

### 引数仕様

| 要素 | 形式 | 説明 |
|---|---|---|
| `<ref>` | 数値 OR 文字列 | 数値なら issue 番号として直接使用、文字列なら issue title の前方一致検索キー |
| `<slug>` | `[a-z0-9-]{2,40}` | worktree/branch 名の末尾識別子。日本語不可。 |

### オプション (引数より前に指定)

| オプション | デフォルト | 説明 |
|---|---|---|
| `--prompt-template <path>` | **必須 (デフォルトなし)** | Codex が起動直後に読み込む詳細指示テンプレ。未指定はエラー。例は `examples/prompt-template/` を参照 |
| `--branch-prefix <prefix>` | `parallel` | branch 命名 prefix。実 branch は `<prefix>/<issue_number>-<slug>` |
| `--base-branch <branch>` | `main` | worktree のベースブランチ |
| `--dry-run`, `-n` | — | 実行せず内容のみ表示 |
| `--help`, `-h` | — | ヘルプ表示 |

## 前提条件

- macOS + iTerm2 3.x
- `gh` (認証済み), `jq`, `envsubst` (`brew install gettext`) が PATH 上にあること
- リポジトリは git 管理されていること
- `.agents/worktrees/` ディレクトリへの書き込み権限があること

## ワークフロー

### Step 1: 並列対象の妥当性確認

親セッションは spawn 前に以下を必ず確認する。**ユーザーが指定した issue 一覧だけを鵜呑みにせず、競合解析を行う**。

1. **対象 issue を取得**: 各 `<ref>` を `gh issue view` で確認 (タイトル / 本文 / 対象ファイル)
2. **競合検出**: `gh issue view` で issue 本文を取得し、同一ファイル・同一プラグイン・同一スキルを複数 issue が触る組を検出
3. **wave 設計**:
   - 競合なし → 同 wave (並列起動 OK)
   - 競合あり → 異 wave (順番に。merge 後に次を起動)
4. **依存検出**: 一方が他方の変更を前提とする依存関係があれば直列化

競合 / 依存が見つかった場合は wave 構成をユーザーに提案 → 承認 → 実行。

### Step 2: 事前チェック

```bash
# 必要 CLI がそろっているか
command -v gh jq envsubst codex

# iTerm2 が起動しているか
osascript -e 'tell application "System Events" to (name of processes) contains "iTerm2"'

# ベースブランチが clean か
git status -sb
git fetch origin
```

非 macOS、iTerm2 未起動、`gh` 未認証は致命的なので即停止 + 原因報告。

### Step 3: spawn 実行

```bash
.agents/skills/parallel-worktree/scripts/spawn.sh [options] <ref>:<slug> [<ref>:<slug> ...]
```

スクリプトは内部で以下を順に実行する:

1. issue 番号解決 (`gh issue view`)
2. branch / worktree 名生成
3. `git worktree add -b <branch> <path> origin/<base>` (既存 worktree は再利用)
4. `envsubst` でテンプレ展開 → `<worktree>/.session-prompt.md` 配置
5. `<worktree>/.start-codex.sh` 生成 (短文 kickoff prompt 付きの Codex 起動 wrapper)
6. iTerm2 で新タブを作成 → `cd && exec ./.start-codex.sh` を 1 回の write text で送信
7. 起動間に 3 秒スリープ ([.git/config.lock 競合回避](https://github.com/anthropics/claude-code/issues/34645))
8. spawn 履歴を `.agents/worktrees/.issues-index.json` に追記

### Step 4: 起動後のユーザーへの案内

spawn 完了したら、ユーザーに以下を伝える:

- 起動した issue 一覧 (#番号 + title)
- iTerm2 で各タブを巡れば各セッションが PR まで自走することの説明
- 競合グループがある場合の次 wave の予告
- クリーンアップコマンド (PR merge 後)

### Step 5: 進捗観察と次 wave 投入

各セッションが PR を作成したら、ユーザーから報告を受けて次 wave を組み立てる。引き続き並列対象がある場合は Step 1 から再帰。

## プロンプトテンプレートの書き方

**プロンプトの中身は skill 実行側 (＝各プロジェクト) で決まる。** 規約・lint・PR 手順・利用スキルはプロジェクトごとに異なるため、skill ディレクトリに特定プロジェクト向けの正式テンプレは置かない。`spawn.sh` はデフォルトのテンプレを持たず、`--prompt-template <path>` は**必須**である。

- **skill が提供するのは「例」だけ**: `examples/prompt-template/` にサンプルを置く (汎用の [generic.md](examples/prompt-template/generic.md) と、本リポジトリの AI-SDD spec 生成向け [generate-spec.md](examples/prompt-template/generate-spec.md))。
- **実際に使うテンプレはプロジェクト側に置く**: サンプルをコピーし自プロジェクトの規約に合わせて編集したものを、プロジェクト管理下の任意の場所に配置して `--prompt-template` で渡す。
- 詳しい書き方と使い方は [examples/prompt-template/README.md](examples/prompt-template/README.md) を参照。

テンプレ内では次の 5 変数が `envsubst` で実値置換される:

| 変数 | 内容 | 例 |
|---|---|---|
| `${ISSUE_NUMBER}` | issue 番号 | `42` |
| `${ISSUE_ID}` | spawn 引数の `<ref>` | `[bug]` or `42` |
| `${ISSUE_TITLE}` | issue title | `[bug] リンク切れ修正` |
| `${BRANCH}` | 命名 branch | `feat/42-fix-typo` |
| `${WORKTREE_PATH}` | worktree の絶対パス | `/path/.agents/worktrees/42-fix-typo` |

**注意**: `{{VAR}}` (Mustache 風) は `envsubst` の対象外。必ず `${VAR}` 形式で記述する。

## 既知の制限と注意

詳細は `references/reference.md` を参照。重要点だけ抜粋:

- **同時起動数**: 3〜4 が現実的。
- **`.git/config.lock` 競合**: 並列 `git worktree add` が config.lock を奪う事例 ([claude-code#34645](https://github.com/anthropics/claude-code/issues/34645))。spawn.sh は 3 秒スリープで回避済み。
- **iTerm2 必須**: AppleScript 経由で iTerm 3.x に依存。Terminal.app / Ghostty / WezTerm は未対応。
- **iTerm `write text` バッファ破壊**: 連続 2 回以上の write text は入力バッファ上で結合・破壊される既知の挙動あり。spawn.sh は起動コマンドを worktree 内 `.start-codex.sh` に固めて write text を 1 回に抑えている。

## ディレクトリ構成

```
.agents/skills/parallel-worktree/
├── SKILL.md                        ← 本ファイル (skill 定義)
├── scripts/
│   └── spawn.sh                    ← 起動本体
├── examples/
│   └── prompt-template/            ← プロンプトテンプレの例 (サンプル)
│       ├── README.md               ← 設計原則・変数・使い方
│       ├── generic.md              ← 汎用サンプル
│       └── generate-spec.md        ← AI-SDD spec 生成向けサンプル
└── references/
    └── reference.md                ← 詳細仕様・トラブルシュート
```

> プロジェクト固有の正式テンプレは skill 配下に置かず、プロジェクト管理下に配置して `--prompt-template` で渡す。

```
.agents/worktrees/                 ← gitignored (spawn 生成物)
├── .issues-index.json              ← spawn 履歴
└── <issue_number>-<slug>/
    ├── .session-prompt.md          ← envsubst 展開済み詳細指示
    ├── .start-codex.sh            ← iTerm 起動 wrapper
    └── <worktree 本体>
```

## クリーンアップ

PR が merge されたら:

```bash
git worktree remove .agents/worktrees/<name>
git branch -D <branch>
git worktree prune
```

複数同時削除はループで:

```bash
for wt in $(ls .agents/worktrees | grep -v '^\.'); do
  git worktree remove ".agents/worktrees/$wt" 2>/dev/null
done
git worktree prune
```

## トラブルシューティング

主要なものだけ。詳細は `references/reference.md`。

| 症状 | 原因 | 対処 |
|---|---|---|
| Codex が「何を進めますか？」と聞く | `.session-prompt.md` が届いていない or テンプレ変数未置換 | `cat .agents/worktrees/<name>/.session-prompt.md` で `${...}` のまま残っていないか確認。ダメなら手動で `./.session-prompt.md を読み込み、その手順に従って実装してください。` を Codex に送る |
| `current window を ... に設定できません (-10006)` | iTerm window 自体が消滅 | spawn.sh は window 不在時に `create window` で復旧する実装済み。再発時は `osascript -e 'tell application "iTerm" to count windows'` で状態確認 |
| `fatal: '<path>' already exists` | worktree が前回残置 | `git worktree remove --force .agents/worktrees/<name>` + `git branch -D <branch>` で完全削除 |
