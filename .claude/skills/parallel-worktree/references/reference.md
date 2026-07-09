# parallel-worktree

複数の GitHub Issue を**並列**で実装するためのヘルパー。`git worktree` + `iTerm2 タブ` + `Claude Code セッション` を 1 コマンドで束ねる。

各セッションは独立した worktree で動くため、ファイル衝突なしに完全並列で実装→PR 作成まで自走できる。

## 仕組み

1 issue ごとに以下を作成し、iTerm2 のタブで Claude Code セッションを起動する。

```
.claude/worktrees/<issue_number>-<slug>/
├── .session-prompt.md   ← Claude が起動直後に Read する詳細指示
└── .start-claude.sh     ← iTerm から呼ばれる起動 wrapper
```

`--prompt-template` で指定したテンプレ（必須）の本文に対し `envsubst` でテンプレ変数を実値置換し、`.session-prompt.md` として配置する。Claude セッション起動時は短文 kickoff prompt のみが引数として渡され、起動後すぐに `.session-prompt.md` を Read で読み込むことで詳細指示を受け取る。テンプレのサンプルは `examples/prompt-template/` を参照。

## 必要環境

| ツール | バージョン | 用途 |
|---|---|---|
| macOS | — | AppleScript / iTerm2 連携 |
| iTerm2 | 3.x | タブ起動 |
| Claude Code CLI | `claude` がパス上にあること | セッション本体 |
| gh CLI | 認証済み | issue 解決・PR 作成 |
| jq | — | JSON 整形 |
| envsubst | `brew install gettext` | テンプレ変数展開 |

## 使い方

### 基本

```bash
# issue 番号で並列起動
.claude/skills/parallel-worktree/scripts/spawn.sh 42:fix-typo 43:add-agent

# issue title 前方一致で起動
.claude/skills/parallel-worktree/scripts/spawn.sh '[bug]:fix-link' '[feat]:new-skill'
```

`<ref>:<slug>` の `<ref>` は数字なら issue 番号として直接使われ、文字列なら issue title の前方一致検索キーとして使われる。

`<slug>` は worktree/branch 名末尾に使う識別子で、`[a-z0-9-]{2,40}` の制約あり。

### オプション

```bash
.claude/skills/parallel-worktree/scripts/spawn.sh \
  --prompt-template .claude/skills/parallel-worktree/examples/prompt-template/generic.md \
  --branch-prefix feat \
  --base-branch main \
  42:fix-typo
```

| オプション | デフォルト | 説明 |
|---|---|---|
| `--prompt-template <path>` | **必須 (デフォルトなし)** | Claude が読む詳細指示テンプレ。未指定はエラー。サンプルは `examples/prompt-template/` |
| `--branch-prefix <prefix>` | `parallel` | branch 名 prefix。実 branch 名は `<prefix>/<issue_number>-<slug>` |
| `--base-branch <branch>` | `main` (`BASE_BRANCH` 環境変数でも可) | worktree のベースブランチ |
| `--dry-run` / `-n` | — | 実行せず内容のみ表示 |
| `--help` / `-h` | — | ヘルプ表示 |

### プロンプトテンプレ

テンプレ内で以下 5 つの変数が `envsubst` で実値置換される:

| 変数 | 内容 | 例 |
|---|---|---|
| `${ISSUE_NUMBER}` | issue 番号 (数値) | `42` |
| `${ISSUE_ID}` | spawn 引数の `<ref>` をそのまま | `[bug]` または `42` |
| `${ISSUE_TITLE}` | issue title (gh から取得) | `[bug] リンク切れ修正` |
| `${BRANCH}` | 命名された branch | `feat/42-fix-typo` |
| `${WORKTREE_PATH}` | worktree の絶対パス | `/path/to/repo/.claude/worktrees/42-fix-typo` |

**プロンプトの中身はプロジェクト側で決める。** skill ディレクトリには特定プロジェクト向けの正式テンプレを置かず、`examples/prompt-template/` のサンプルをコピーして自プロジェクトの規約に合わせて編集し、プロジェクト管理下の任意の場所に配置して `--prompt-template` で渡す。設計原則の詳細は [examples/prompt-template/README.md](../examples/prompt-template/README.md) を参照。

```bash
# サンプルをプロジェクトの作業ディレクトリにコピーして編集
cp .claude/skills/parallel-worktree/examples/prompt-template/generic.md /path/to/your/my-flow.md
# my-flow.md を編集後、spawn 時に指定
.claude/skills/parallel-worktree/scripts/spawn.sh --prompt-template /path/to/your/my-flow.md 42:slug
```

### 進捗観察

iTerm2 で開いた各タブを巡って状態確認。Claude が `set name` で自身のタブ名を書き換える場合、どのタブが何の issue かが分かる。

### クリーンアップ

PR が merge されたら:

```bash
git worktree remove .claude/worktrees/42-fix-typo
git branch -D feat/42-fix-typo
git worktree prune
```

## 既知の制限と注意

- **同時起動数**: 3〜4 が現実的。worktree ごとに依存関係を別途持つ場合、5+ ではディスク圧迫が顕著。
- **`.git/config.lock` 競合**: 並列 `git worktree add` は config.lock を奪い合うため、spawn.sh では各起動の間に 3 秒スリープを入れている (cf. [anthropics/claude-code#34645](https://github.com/anthropics/claude-code/issues/34645))。
- **iTerm2 必須**: AppleScript 経由で iTerm2 3.x に依存。Terminal.app / Ghostty / WezTerm はサポート外。
- **single quote escape 未対応**: worktree path / branch prefix に single quote (`'`) を含めると AppleScript の引数が壊れる。通常パスでは問題なし。
- **iTerm の `write text` 多重実行**: `write text` を連続 2 回以上実行すると iTerm の入力バッファ上でコマンドが結合・破壊される既知の挙動がある。本スクリプトは起動コマンドを worktree 内 `.start-claude.sh` に固めて `write text` を 1 回に抑えている。

## トラブルシューティング

### Claude が「何を進めますか？」と聞いてくる

`.session-prompt.md` が正しく置かれていない、または kickoff prompt が届いていない可能性がある。

1. `cat .claude/worktrees/<name>/.session-prompt.md` で内容確認 (`${VAR}` のまま残っていないか)
2. `cat .claude/worktrees/<name>/.start-claude.sh` で kickoff 内容確認
3. ダメなら手動で Claude に: `./.session-prompt.md を Read で読み込み、その手順に従って実装してください。` を送る

### `current window を ... に設定できません (-10006)`

iTerm2 のウィンドウ自体が存在しない or AppleScript syntax が古い iTerm 用。spawn.sh は対応済みだが、再発したら window 数を `osascript -e 'tell application "iTerm" to count windows'` で確認。

### worktree 作成失敗

```
fatal: '<path>' already exists
```

→ 既存 worktree を再利用する場合は spawn.sh が自動で検知する。完全に消したい場合:

```bash
git worktree remove --force .claude/worktrees/<name>
git branch -D <branch>
```
