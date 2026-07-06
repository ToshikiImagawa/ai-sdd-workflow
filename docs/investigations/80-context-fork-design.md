# 設計検証レポート: vibe-detector / clarify の `context: fork` による分離実行環境化

- 対象 Issue: [#80](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/80)
- 検証日: 2026-07-06
- 前提バージョン: sdd-workflow plugin v3.3.0 / Claude Code v2.1.193（PoC 実行環境）
- 調査元: [68-claude-code-feature-adoption.md](68-claude-code-feature-adoption.md)（アイデア 3）

## 結論サマリー

| 対象スキル | 判定 | 主な理由 |
|:--|:--:|:--|
| vibe-detector | **見送り** | fork 環境から会話文脈が不可視・AskUserQuestion が fork 内で利用不可（PoC で確認） |
| clarify | **見送り** | `--interactive` の対話ループと回答統合（Edit/Write）が fork の実行モデルと非互換 |

`context: fork` 自体は有効な機構であり、対話を伴わない生成系スキル 4 件
（analyze-requirements / finalize-prd / generate-requirements-diagram / generate-usecase-diagram、
いずれも `agent: sonnet` 併用）には導入済み。本 Issue の対象である検出・明確化系 2 スキルは
**ユーザー対話と会話文脈がスキルの本質的な入力**であるため、fork による分離は設計的に不適合と判断した。

## 検証方法

1. 公式ドキュメント（skills.md / agent-sdk/subagents.md）および anthropics/claude-code の
   関連 Issue から `context: fork` の仕様を確認
2. PoC プラグイン（`context: fork` を付与したプローブスキル）を作成し、headless モード
   （`claude -p --plugin-dir`）で実挙動を検証
3. 対照実験として fork なしのメインエージェントでも同条件を確認

## PoC 検証結果

プローブスキル（`context: fork`、`allowed-tools: Read, Glob, Grep, AskUserQuestion`）を
headless 実行し、以下を確認した。

| 検証項目 | 結果 |
|:--|:--|
| 親会話履歴の可視性 | **不可視**。呼び出し前にユーザーが伝えた情報（秘密の単語）は fork 内から参照できない |
| `$ARGUMENTS` の置換 | **正常動作**。スキル呼び出し時の引数がそのまま本文に展開される |
| fork 内の利用可能ツール | Agent / Bash / Edit / Read / Write / Skill 等。**AskUserQuestion は利用不可** |
| 結果の返却 | fork の最終メッセージのみが親に返る（中間ツール呼び出しは親コンテキストに蓄積されない） |

**PoC の限界**: headless（`-p`）モードでは対照実験の結果、メインエージェント側でも
AskUserQuestion が無効だった。したがって「fork 内で AskUserQuestion が使えない」ことが
fork 固有の制約か headless 固有の制約かは、headless PoC 単独では確定できない。
ただし公式ドキュメント上も fork（サブエージェント）内でのユーザー対話はサポートが
明記されておらず、サブエージェントの実行モデル（親へ最終メッセージのみを返す非対話実行）
とも整合しないため、**fork 内のユーザー対話は利用不可または未保証**として設計判断した。

## 仕様確認結果（設計上の論点への回答）

### 論点 1: fork 環境からの会話文脈の可視性

公式仕様・PoC とも「fork は親セッションの会話履歴にアクセスできず、スキル本文と
`$ARGUMENTS` のみを受け取る」ことを確認。vibe-detector を fork 化する場合、
分析対象のユーザー指示を `$ARGUMENTS` として明示的に渡す設計変更が必須となる。

技術的には可能（メインエージェントがユーザー指示テキストを引数として渡せばよい）だが、
vibe-detector の検出精度は「直近の会話の流れ」「参照している既存仕様とのギャップ」など
指示テキスト単体に閉じない文脈に依存する。`$ARGUMENTS` へ切り出した時点で
「あの機能」「さっきと同じ」等の照応表現が解決不能になり、検出対象そのものが
分析不能になるという自己矛盾を抱える。

### 論点 2: fork 環境内での AskUserQuestion の挙動

PoC では fork 内のツール一覧に AskUserQuestion が現れず利用不可（前述の限界付き）。
公式ドキュメントにもサブエージェント内ユーザー対話のサポートは記載されていない。

- vibe-detector は検出後の明確化フロー（リスク提示 → ユーザー判断）が本体であり、
  対話不能な環境では「検出して警告し、ユーザーに問い返す」という役割を果たせない
- clarify は `--interactive` モードで質問を 1 問ずつ AskUserQuestion で確認し、
  回答を仕様書へ Edit/Write で統合する。fork は最終メッセージのみを親へ返すため、
  「質問 → 回答 → 統合」の往復ループが成立しない

### 論点 3: `agent` フィールドの選定

導入済みの生成系 4 スキルは `agent: sonnet`（モデル指定）を採用しており、
仮に導入する場合もこの既存パターンに従うのが一貫する。なお anthropics/claude-code
Issue #40104 では fork + `allowed-tools` 指定時に親セッションの全 MCP ツール定義が
サブエージェントへ注入されコンテキストが肥大化する問題が報告されており（not planned で
クローズ）、小型モデル指定時はコンテキストオーバーフローのリスクがある点も留意が必要。

## スキル別の設計判断

### vibe-detector: 見送り

| 観点 | 評価 |
|:--|:--|
| 入力の自己完結性 | ✗ ユーザー指示＋会話文脈＋既存仕様のギャップが分析対象。`$ARGUMENTS` 化で照応表現が解決不能になる |
| ユーザー対話 | ✗ 検出 → リスク提示 → ユーザー判断（AskUserQuestion）がフローの本体 |
| 起動経路 | UserPromptSubmit フック（`user-prompt-submit.py`）が additionalContext でメインエージェントに分析を促す方式。メインの会話進行（実装着手の抑止）に直結するため、結果が非同期に要約で返る fork とは役割が噛み合わない |
| コンテキスト削減効果 | 小。スキル本文は 129 行で、分析自体が大量のファイル読み込みを伴わない |

### clarify: 見送り

| 観点 | 評価 |
|:--|:--|
| 入力の自己完結性 | ○ `feature-name` 引数から仕様書を読むため入力は自己完結 |
| ユーザー対話 | ✗ `--interactive` / `--integrate` の質問応答ループが中核機能 |
| 書き戻し | ✗ 回答の仕様書統合（Edit/Write）が必要。fork の「最終メッセージのみ返却」モデルと非互換 |
| 既存の分離設計 | 分析フェーズは既に `clarification-assistant` エージェントへ委譲済みで、コンテキスト分離の効果は現行設計で相当程度達成されている |

clarify の分析フェーズのみを fork 化する案も検討したが、分析は既に
`clarification-assistant` サブエージェントへの委譲で分離されており、
fork の重複導入は複雑さを増すだけで追加効果がない（YAGNI）。

## 今後 fork 導入を再検討する条件

- Claude Code が fork（サブエージェント）内での AskUserQuestion / ユーザー対話を公式サポートした場合
- 対話部分を親に残し分析部分のみを fork へ委譲する `context: fork` の部分適用構文が提供された場合

## 手動検証が必要な残項目

- 対話セッション（非 headless）における fork 内 AskUserQuestion の挙動
  （headless PoC では fork 固有か headless 固有かを切り分けられなかったため）

## 関連 Issue

- [#68](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/68): 調査元
- [#25](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/25): コンテキスト最適化（生成系 4 スキルへの fork 導入済みで部分的に対応）

## 参照

- https://code.claude.com/docs/en/skills.md
- https://code.claude.com/docs/en/agent-sdk/subagents.md
- https://github.com/anthropics/claude-code/issues/40104 （fork + allowed-tools の MCP ツール定義注入問題）
- https://github.com/anthropics/claude-code/issues/61461 （fork 実行時の動的コンテキスト注入の不具合報告）
