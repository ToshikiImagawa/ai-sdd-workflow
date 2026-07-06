# 調査レポート: 最新 Claude Code 機能の SDD ワークフローへの活用可能性

- 対象 Issue: [#68](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/68)
- 調査日: 2026-07-06
- 前提バージョン: sdd-workflow plugin v3.3.0 / Claude Code v2.1.199+ の公式ドキュメントに基づく

## 調査方法

1. 公式ドキュメント（workflows.md / skills.md / hooks.md）から各機能の正確な仕様・プラグイン配布可否を確認
2. 現行プラグイン実装（skills frontmatter / hooks.json / scripts / agents / plugin.json）を棚卸しし、ギャップを特定

## 結論サマリー

| # | アイデア | 実現可能性 | 優先度 | 判定 |
|:-:|:--|:--|:--:|:--|
| 1 | Workflow による SDD 段階のオーケストレーション | △ プラグイン配布不可 | 低 | 保留（配布手段の制約） |
| 2 | `disallowed-tools` による Vibe Coding 防止の構造的強化 | ◎ 公式サポート・変更小 | 高 | [#79](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/79) |
| 3 | `context: fork` による検出/明確化スキルの分離実行 | ○ 公式サポート・要設計 | 中 | [#80](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/80) |
| 4 | `arguments` フィールドによるパラメータ明示化 | ○ 公式サポート（v2.1.199+） | 中 | [#81](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/81) |
| 5 | PreToolUse JSON 出力による CONSTITUTION.md 原則注入 | ○ 公式サポート・要設計 | 中 | [#82](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/82) |

## 各アイデアの詳細評価

### 1. Workflow 機能による SDD 段階の自動オーケストレーション — 保留

**仕様確認結果**: Workflow は `.claude/workflows/*.js` に配置する JavaScript スクリプトで、
`agent()` / `pipeline()` / `parallel()` による決定論的なマルチエージェント制御が可能
（Claude Code v2.1.154+）。

**制約**: Workflow は**プラグイン経由で配布できない**。プラグインで配布可能なコンポーネントは
agents / skills / hooks 等に限られ、配置先は `.claude/workflows/`（プロジェクト単位）または
`~/.claude/workflows/`（ユーザー単位）のみ。

**判定**: 本プロジェクトの成果物はプラグインであるため、`/generate-prd` → `/generate-spec` →
`/task-breakdown` の連鎖をプラグイン機能としてユーザーへ届ける手段が現状存在しない。
代替案（ドキュメントでのサンプル Workflow 提供、`/sdd-init` によるユーザープロジェクトへの
コピー配置）は考えられるが、プラグイン更新への追従性に課題があるため、プラグイン配布が
サポートされるまで保留とする。

### 2. `disallowed-tools` による Vibe Coding 防止の構造的強化 — 高優先

**仕様確認結果**: Skill frontmatter の `disallowed-tools` は公式サポート。スキル実行中に
指定ツールの使用を禁止する（次のユーザーメッセージで解除）。`allowed-tools`（許可プロンプト
省略のホワイトリスト）とは独立に機能し、プラグイン内スキルでも利用可能。

**現状ギャップ**: 全 19 スキルとも `allowed-tools` のみ定義。`allowed-tools` は使用ツールを
制限しない（許可プロンプトを省略するだけ）ため、`/clarify` や `/vibe-detector` の実行中に
実装着手（Bash / Write / Edit）を構造的にブロックできていない。

**適用対象例**: 分析・検出系スキル（clarify, vibe-detector, doc-consistency-checker,
check-spec, run-checklist 等）に `disallowed-tools: Write, Edit, Bash`（スキル特性に応じて
調整）を追加する。変更は frontmatter のみで小さく、既存動作への影響も限定的。

### 3. `context: fork` による分離実行環境化 — 中優先

**仕様確認結果**: Skill frontmatter に `context: fork` を指定すると、スキルは親セッションの
会話履歴にアクセスしない独立サブエージェントとして実行され、結果の要約のみが親へ返る。
`agent` フィールドで実行エージェント（Explore / Plan / general-purpose / カスタム）を指定可能。

**現状ギャップと設計上の論点**: 対象候補の vibe-detector は「ユーザー指示の曖昧さ分析」を行う
自動起動スキル（`user-invocable: false`）であり、fork すると分析対象であるユーザー指示や
会話文脈が見えなくなる。fork 化には分析対象を `$ARGUMENTS` として明示的に渡す設計変更が必須。
また `AskUserQuestion` によるユーザー対話がサブエージェント内でどう振る舞うかの検証も必要。
効果（メインコンテキストの汚染防止・Issue #25 のコンテキスト削減にも寄与）は大きいため、
設計検証付きで Issue 化する。

### 4. `arguments` フィールドとパラメータ置換 — 中優先

**仕様確認結果**: v2.1.199+ で `arguments: [name1, name2]` による名前付き引数と
`$name` / `$ARGUMENTS` / `$N` 置換が公式サポート。プラグイン内スキルで利用可能。

**現状ギャップ**: 各スキルは `argument-hint`（表示用ヒント）のみ定義し、本文では引数を
自然言語で受け取っている。`/generate-spec` / `/task-breakdown` / `/implement` 等で
feature-name や ticket-number を名前付き引数として構造的に受け取れば、引数解釈の曖昧さを
排除できる。ただし旧バージョンの Claude Code との互換性（v2.1.199 未満での挙動）確認が必要。

### 5. PreToolUse フックによる CONSTITUTION.md 原則の動的注入 — 中優先

**仕様確認結果**: PreToolUse フックは JSON 出力
（`hookSpecificOutput.permissionDecision` = allow/deny/ask/defer、`additionalContext`、
`updatedInput` 等）による Decision Control を公式サポート。`additionalContext` は
permissionDecision と独立に Claude へ文脈を注入できる。

**現状ギャップ**: `scripts/pre-tool-use.py` はファイル命名規則違反を stderr + `exit 2` で
ブロックする旧方式のみ。`hook_common.emit_additional_context()` は UserPromptSubmit /
PostToolUse で使用済みだが、PreToolUse では未使用。

**適用案**: Write/Edit 対象が実装コードの場合に CONSTITUTION.md の原則（存在する場合）を
`additionalContext` として注入する。ただし全ツール呼び出しへの注入はコンテキスト肥大化
（Issue #25 と同根の課題）を招くため、注入条件（対象パス・注入頻度・要約注入）の設計が必要。
併せて既存の exit 2 方式を `permissionDecision: "deny"` の JSON 方式へ移行する改善も含める。

## 関連 Issue

- [#25](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/25): コンテキスト増加の最適化（アイデア 3・5 と関連）
- [#57](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/57): allowed-tools の lint 検証（アイデア 2 導入時に disallowed-tools も検証対象へ拡張推奨）
- [#54](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/54): hooks 拡大（実装済み・アイデア 5 の基盤）

## 参照

- https://code.claude.com/docs/en/workflows.md
- https://code.claude.com/docs/en/skills.md
- https://code.claude.com/docs/en/hooks.md
