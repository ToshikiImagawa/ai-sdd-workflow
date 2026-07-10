#!/usr/bin/env bash
#
# .claude/skills/parallel-worktree/scripts/spawn.sh
#
# GitHub Issue を並列 git worktree で起動する汎用ヘルパー。
# 各 issue ごとに git worktree を作成し、iTerm2 タブで Claude Code セッションを起動する。
# プロンプトは envsubst でテンプレ変数 (${ISSUE_NUMBER} 等) を実値置換した本文を
# 各 worktree 内に配置し、Claude が起動直後に Read で読み込む設計。
#
# Usage:
#   .claude/skills/parallel-worktree/scripts/spawn.sh [options] <ref>:<slug> [<ref>:<slug> ...]
#
# <ref>:<slug> の <ref> は次のいずれか:
#   - 数値          → GitHub Issue 番号として直接使用 (例: 42:fix-typo)
#   - 文字列        → issue title の前方一致検索キー
#
# <slug> は識別用の英小文字+数字+ハイフンの短い名前 (2〜40 字、worktree 名と branch 名末尾に使われる)。
#
# Options:
#   --prompt-template <path>   起動時に Claude が読む詳細指示テンプレ (必須・デフォルトなし)
#                              未指定はエラー。プロンプトはプロジェクト側で決めるため skill は既定値を持たない。
#                              サンプルは .claude/skills/parallel-worktree/examples/prompt-template/ を参照。
#                              テンプレ内で ${ISSUE_NUMBER} / ${ISSUE_ID} / ${ISSUE_TITLE} / ${BRANCH} / ${WORKTREE_PATH}
#                              の 5 変数を envsubst で実値置換できる。
#                              (ISSUE_ID は <ref> をそのまま渡す)
#   --branch-prefix <prefix>   ブランチ命名の prefix (default: parallel)
#                              実際の branch 名は "<prefix>/<issue_number>-<slug>" になる。
#   --base-branch <branch>     worktree のベースブランチ (default: main, BASE_BRANCH 環境変数でも上書き可)
#   --dry-run, -n              実行はせず、何をするかを表示するだけ
#   --help, -h                 ヘルプ表示
#
# Examples:
#   .claude/skills/parallel-worktree/scripts/spawn.sh 42:fix-typo 43:add-agent
#
# Output:
#   .claude/worktrees/<issue_number>-<slug>/                  # 各 worktree
#     ├── .session-prompt.md   (envsubst で展開済みの詳細指示)
#     └── .start-claude.sh     (iTerm 経由で実行される起動 wrapper)
#   .claude/worktrees/.issues-index.json                      # spawn 履歴
#
# Requirements: iTerm2 (3.x), gh, jq, envsubst
# Known limits: SKILL.md と references/reference.md を参照
#
set -euo pipefail

# ---------- デフォルト設定 ----------
# このスクリプトは .claude/skills/parallel-worktree/scripts/spawn.sh に配置されている前提。
# REPO_ROOT はそこから 3 階層上 (= リポジトリルート)。
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${SKILL_DIR}/../../.." && pwd)"
WORKTREE_BASE="${REPO_ROOT}/.claude/worktrees"
ISSUES_INDEX="${WORKTREE_BASE}/.issues-index.json"
# --prompt-template は必須 (デフォルトなし)。プロンプトはプロジェクト側で決めるため既定値を持たない。
PROMPT_TEMPLATE=""
BRANCH_PREFIX="parallel"
BASE_BRANCH="${BASE_BRANCH:-main}"
DRY_RUN=false

# ---------- 引数パース ----------
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|-n)
      DRY_RUN=true
      shift
      ;;
    --prompt-template)
      PROMPT_TEMPLATE="$2"
      shift 2
      ;;
    --prompt-template=*)
      PROMPT_TEMPLATE="${1#*=}"
      shift
      ;;
    --branch-prefix)
      BRANCH_PREFIX="$2"
      shift 2
      ;;
    --branch-prefix=*)
      BRANCH_PREFIX="${1#*=}"
      shift
      ;;
    --base-branch)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --base-branch=*)
      BASE_BRANCH="${1#*=}"
      shift
      ;;
    --help|-h)
      sed -n '3,43p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "Usage: $0 [options] <ref>:<slug> [<ref>:<slug> ...]" >&2
  echo "Run '$0 --help' for full documentation" >&2
  exit 2
fi

# ---------- 事前チェック ----------
command -v gh >/dev/null || { echo "ERROR: gh CLI not found" >&2; exit 1; }
command -v claude >/dev/null || { echo "ERROR: claude CLI not found" >&2; exit 1; }
command -v jq >/dev/null || { echo "ERROR: jq not found" >&2; exit 1; }
command -v envsubst >/dev/null || { echo "ERROR: envsubst not found (install gettext: brew install gettext)" >&2; exit 1; }
if [[ -z "$PROMPT_TEMPLATE" ]]; then
  echo "ERROR: --prompt-template is required (no default)." >&2
  echo "       Copy and customize a sample from examples/prompt-template/ and pass it with --prompt-template <path>." >&2
  echo "       See .claude/skills/parallel-worktree/examples/prompt-template/README.md" >&2
  exit 2
fi
[[ -f "$PROMPT_TEMPLATE" ]] || { echo "ERROR: prompt template not found: $PROMPT_TEMPLATE" >&2; exit 1; }
[[ "$OSTYPE" == "darwin"* ]] || { echo "ERROR: macOS + iTerm2 only" >&2; exit 1; }

cd "$REPO_ROOT"

# base ブランチ最新化 (worktree のベースを揃える)
if ! $DRY_RUN; then
  echo "[setup] git fetch origin $BASE_BRANCH" >&2
  git fetch origin "$BASE_BRANCH" >/dev/null 2>&1 || true
fi

mkdir -p "$WORKTREE_BASE"
[[ -f "$ISSUES_INDEX" ]] || echo '[]' > "$ISSUES_INDEX"

# ---------- issue ref を issue 番号に解決 ----------
resolve_issue_number() {
  local ref="$1"
  if [[ "$ref" =~ ^[0-9]+$ ]]; then
    # 数値 ref: そのまま issue 番号として返す
    echo "$ref"
    return 0
  fi
  # 文字列 ref: title の前方一致で検索
  gh issue list --search "$ref" --state all --json number,title --limit 10 \
    | jq -r --arg ref "$ref" '
        map(select(.title | startswith($ref))) | .[0].number // empty
      '
}

# ---------- 1 issue を起動 ----------
spawn_one() {
  local pair="$1"
  local idx="$2"
  local total="$3"

  if [[ "$pair" != *:* ]]; then
    echo "[$idx/$total] ERROR: '$pair' is not in <ref>:<slug> form" >&2
    return 1
  fi
  local ref="${pair%%:*}"
  local slug="${pair##*:}"

  if ! [[ "$slug" =~ ^[a-z0-9-]{2,40}$ ]]; then
    echo "[$idx/$total] ERROR: invalid slug '$slug' (lowercase, digits, hyphen, 2-40 chars)" >&2
    return 1
  fi

  # issue 番号解決
  echo "[$idx/$total] Resolving issue for ref='$ref' ..." >&2
  local issue_number
  issue_number="$(resolve_issue_number "$ref")"
  if [[ -z "$issue_number" ]]; then
    echo "[$idx/$total] ERROR: cannot resolve issue from ref '$ref'" >&2
    return 1
  fi
  local issue_title
  issue_title="$(gh issue view "$issue_number" --json title -q .title 2>/dev/null)" || {
    echo "[$idx/$total] ERROR: gh issue view #$issue_number failed" >&2
    return 1
  }
  echo "[$idx/$total] Issue #$issue_number — $issue_title" >&2

  # branch / worktree 命名
  local branch="${BRANCH_PREFIX}/${issue_number}-${slug}"
  local wt_name="${issue_number}-${slug}"
  local wt_path="${WORKTREE_BASE}/${wt_name}"

  # worktree 既存チェック
  if [[ -d "$wt_path" ]]; then
    echo "[$idx/$total] NOTE: worktree already exists, reusing: $wt_path" >&2
  else
    local branch_exists=false
    if git show-ref --verify --quiet "refs/heads/$branch" || \
       git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
      branch_exists=true
    fi

    if $DRY_RUN; then
      if $branch_exists; then
        echo "[$idx/$total] [dry-run] git worktree add '$wt_path' '$branch'" >&2
      else
        echo "[$idx/$total] [dry-run] git worktree add -b '$branch' '$wt_path' 'origin/$BASE_BRANCH'" >&2
      fi
    else
      if $branch_exists; then
        git worktree add "$wt_path" "$branch"
      else
        git worktree add -b "$branch" "$wt_path" "origin/$BASE_BRANCH"
      fi
    fi
  fi

  # プロンプト生成 (envsubst でテンプレ変数を実値置換)
  local prompt_path="${wt_path}/.session-prompt.md"
  local prompt_content
  prompt_content="$(
    ISSUE_NUMBER="$issue_number" \
    ISSUE_ID="$ref" \
    ISSUE_TITLE="$issue_title" \
    BRANCH="$branch" \
    WORKTREE_PATH="$wt_path" \
    envsubst '${ISSUE_NUMBER} ${ISSUE_ID} ${ISSUE_TITLE} ${BRANCH} ${WORKTREE_PATH}' \
    < "$PROMPT_TEMPLATE"
  )"

  # 起動スクリプト (claude に短文 kickoff prompt を引数で渡す)
  local kickoff_script="${wt_path}/.start-claude.sh"
  local kickoff_msg="このセッションは GitHub Issue #${issue_number} (${issue_title}) を実装するために起動された並列 worktree です。まず ./.session-prompt.md を Read で読み込み、そこに書かれた手順に厳密に従って実装してください。"

  if $DRY_RUN; then
    echo "[$idx/$total] [dry-run] would write prompt to: $prompt_path" >&2
    echo "[$idx/$total] [dry-run] would write kickoff script to: $kickoff_script" >&2
    echo "[$idx/$total] [dry-run] would open iTerm2 tab and run: cd '$wt_path' && exec ./.start-claude.sh" >&2
  else
    [[ -d "$wt_path" ]] && printf '%s' "$prompt_content" >| "$prompt_path"

    cat >| "$kickoff_script" <<KICKOFF_EOF
#!/usr/bin/env bash
# Auto-generated by .claude/skills/parallel-worktree/scripts/spawn.sh for issue #${issue_number} (ref: ${ref})
set -e
exec claude "${kickoff_msg}"
KICKOFF_EOF
    chmod +x "$kickoff_script"

    open_iterm_tab "$wt_path"

    # 起動ずらし (.git/config.lock 競合回避: anthropics/claude-code#34645)
    if [[ "$idx" -lt "$total" ]]; then
      echo "[$idx/$total] Waiting 3s before next spawn (avoid worktree lock contention)..." >&2
      sleep 3
    fi
  fi

  # インデックス更新
  if ! $DRY_RUN; then
    local now
    now="$(date '+%Y-%m-%dT%H:%M:%S%z')"
    local entry
    entry="$(jq -n \
      --arg ref "$ref" \
      --arg number "$issue_number" \
      --arg title "$issue_title" \
      --arg branch "$branch" \
      --arg worktree "$wt_path" \
      --arg slug "$slug" \
      --arg spawned_at "$now" \
      '{ref: $ref, issue_number: ($number | tonumber), issue_title: $title, branch: $branch, worktree: $worktree, slug: $slug, spawned_at: $spawned_at}'
    )"
    local tmp
    tmp="$(mktemp)"
    jq --argjson e "$entry" '. + [$e]' "$ISSUES_INDEX" > "$tmp" && mv "$tmp" "$ISSUES_INDEX"
  fi

  echo "[$idx/$total] ✓ Spawned #$issue_number -> $wt_path  (branch: $branch)" >&2
}

# ---------- iTerm2 タブ起動 ----------
# iTerm 3.x: create window/tab 単独 → write text 1 回 で起動。
# write text を 2 回以上連続実行すると iTerm の入力バッファ上でコマンドが結合・破壊される
# 既知の挙動があるため、起動コマンドは worktree 内の .start-claude.sh に固めて 1 行で呼ぶ。
open_iterm_tab() {
  local wt_path="$1"
  local cmd="cd '${wt_path}' && exec ./.start-claude.sh"

  osascript <<APPLESCRIPT
tell application "iTerm"
  activate
  if (count of windows) is 0 then
    set newSession to (create window with default profile)
    tell current session of newSession
      write text "${cmd}"
    end tell
  else
    tell current window
      set newTab to (create tab with default profile)
      tell current session of newTab
        write text "${cmd}"
      end tell
    end tell
  end if
end tell
APPLESCRIPT
}

# ---------- メインループ ----------
total=${#ARGS[@]}
echo "==> Spawning $total parallel worktree session(s)..." >&2
echo "    base-branch    = $BASE_BRANCH" >&2
echo "    branch-prefix  = $BRANCH_PREFIX" >&2
echo "    prompt-template= ${PROMPT_TEMPLATE#$REPO_ROOT/}" >&2
echo "" >&2

i=0
for pair in "${ARGS[@]}"; do
  i=$((i + 1))
  spawn_one "$pair" "$i" "$total" || {
    echo "==> Spawn failed for '$pair', continuing..." >&2
  }
done

echo "" >&2
echo "==> Done. Active worktrees:" >&2
git worktree list | sed -n '2,$p' | sed 's/^/    /' >&2

if ! $DRY_RUN; then
  cat >&2 <<HINT

==> Watch progress in iTerm2 tabs. Each session will:
    1. Read .session-prompt.md (envsubst で展開済みの詳細指示)
    2. Implement according to the prompt
    3. Run lint/plugin-lint check
    4. Commit + push + create PR (prompt 次第)

==> Cleanup completed worktrees:
    git worktree remove <path>
    git branch -D <branch>
    (PR merge 後にローカルブランチ削除)
HINT
fi
