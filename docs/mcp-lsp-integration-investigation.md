# MCP / LSP サーバー連携の導入検討レポート

- **関連 Issue**: [#56 MCP/LSPサーバー連携の導入検討](https://github.com/ToshikiImagawa/ai-sdd-workflow/issues/56)
- **作成日**: 2026-07-06
- **ステータス**: 検討（意思決定前の調査資料）

## 1. 背景と目的

本プロジェクト（sdd-workflow プラグイン）は現状、プラグイン同梱の MCP サーバー設定（`.mcp.json`）・LSP サーバー設定（`.lsp.json`）を実装していない。一方で [PLUGIN.md](../PLUGIN.md) はこれらの統合方法（設定形式、配置場所、ベストプラクティス）を案内している。

本レポートは、MCP / LSP 連携を sdd-workflow プラグインに導入すべきか、導入するならどの形かを判断するための材料を整理する。

## 2. 現状分析

### 2.1 プラグインの MCP / LSP 関連の実態

| 項目 | 実態 |
|:-----|:-----|
| `plugins/sdd-workflow/.mcp.json` | **存在しない** |
| `plugins/sdd-workflow/.lsp.json` | **存在しない** |
| plugin.json の `mcpServers` / `lspServers` | **未定義** |
| Serena MCP のオプショナル連携文書 | **3スキルに記載済み**（後述） |

### 2.2 既に文書化されている Serena MCP 連携（オプショナル）

以下のスキルは、**ユーザーのプロジェクト側の `.mcp.json` に `serena` が設定されている場合**の追加機能を SKILL.md に文書化済みである。プラグイン自体は MCP サーバーを同梱せず、「存在すれば活用する」ソフト依存の設計になっている。

| スキル | Serena 有効時の追加機能 | 参照 |
|:-------|:------------------------|:-----|
| `check-spec` | `find_symbol` / `find_referencing_symbols` によるシンボルベースの設計↔実装整合性チェック（API実装確認、シグネチャ一致、未文書コード検出、依存関係把握） | `skills/check-spec/SKILL.md` §Serena MCP Integration |
| `generate-spec` | 既存コードベースのセマンティック解析による仕様書生成の精度向上 | `skills/generate-spec/SKILL.md` §Serena MCP Integration |
| `task-breakdown` | 影響範囲分析によるタスク分解の精度向上 | `skills/task-breakdown/SKILL.md` §Serena MCP Integration |

いずれも「Serena 未設定時は Grep/Glob ベースのテキスト検索にフォールバックし、言語非依存で動作する」というグレースフルデグラデーションを明記している。

**Issue #56 が提案する「LSP でcheck-spec を高精度化」というユースケースは、Serena MCP 連携として既に設計・文書化されている**点が本調査の重要な発見である。Serena は内部で各言語の Language Server を利用するため、LSP の型情報・シンボル参照を MCP 経由で利用する構成が既に選択されている。

## 3. 提案ユースケースの評価

### 3.1 MCP: 外部要求管理ツール（Jira / Notion 等）との PRD 同期

**構想**: `/generate-prd` 実行時に外部チケットへ自動反映、または外部チケットから PRD を生成する。

| 観点 | 評価 |
|:-----|:-----|
| 技術的実現性 | 高い。Jira（Atlassian Rovo）・Notion は公式 MCP サーバーを提供しており、プラグインの `.mcp.json` に HTTP 型サーバーとして定義するだけで接続自体は可能 |
| プラグイン同梱の適否 | **低い**。認証（OAuth / トークン）、ワークスペース選択、プロジェクトキーのマッピング等がユーザー環境ごとに異なり、プラグインに固定同梱すると強い前提を持ち込む |
| 需要 | **未検証**。外部ツールとの双方向同期は運用ルール（どちらが真実の源か）の設計が必要で、AI-SDD の「仕様書を真実の源とする」原則との整合を先に定義する必要がある |
| 保守コスト | 高い。外部 API 仕様・MCP サーバー仕様の変更に追従が必要 |

**評価結論**: プラグインへの `.mcp.json` 同梱は推奨しない。導入するなら Serena と同じ**ソフト依存パターン**（ユーザー側で Jira/Notion MCP が設定済みなら generate-prd / finalize-prd が同期手順を案内・実行する SKILL.md 追記）が設計的に正しい。ただし着手は需要ヒアリング後とすべき。

### 3.2 LSP: check-spec の整合性チェック高精度化

**構想**: LSP の型情報・シンボル参照を用いて設計書↔実装の整合性チェックを高精度化する。

| 観点 | 評価 |
|:-----|:-----|
| 技術的実現性 | 高い。ただし実現経路が2つある（下記） |
| 経路A: Serena MCP 経由（現行設計） | **文書化済み・追加実装不要**。30+ 言語対応、ユーザー側セットアップに委譲 |
| 経路B: プラグイン同梱 `.lsp.json` | 言語ごとに Language Server のコマンド定義が必要。sdd-workflow は言語非依存プラグインのため、特定言語の LSP を同梱するのは責務違反。ユーザーのプロジェクト言語を事前に知り得ない |
| 需要 | 経路Aの利用実績・フィードバックが未収集 |

**評価結論**: 経路Aが既に採用済みであり、経路B（`.lsp.json` 同梱）は言語非依存という本プラグインの性質と矛盾するため推奨しない。まず経路Aの利用実績を収集し、不足があれば拡張を検討する。

## 4. 選択肢と優先度評価

| # | 選択肢 | 難易度 | 有効度 | 判定 |
|:--|:-------|:-------|:-------|:-----|
| 1 | 現状維持（Serena ソフト依存の周知強化のみ。README にセットアップガイド追記） | ★☆☆☆☆ | ★★★☆☆ | **短期推奨** |
| 2 | Jira/Notion MCP のソフト依存連携を generate-prd 系スキルに追記 | ★★★☆☆ | ★★★☆☆（需要次第） | 需要ヒアリング後 |
| 3 | プラグインに `.mcp.json` を同梱（特定 MCP サーバーへのハード依存） | ★★☆☆☆ | ★☆☆☆☆ | 非推奨 |
| 4 | プラグインに `.lsp.json` を同梱 | ★★★★☆ | ★☆☆☆☆ | 非推奨（言語非依存性と矛盾） |

## 5. 推奨アクション

1. **需要ヒアリング（先行）**: 既存ユーザーに対し「外部要求管理ツール同期」「Serena 連携の利用有無」をヒアリングする。Issue #56 注記の推奨どおり、実装より先に需要を検証する。
2. **短期（低コスト）**: README（en/ja）に Serena MCP 連携のセットアップガイドと対象3スキルの機能差を明記し、既存のソフト依存機能の発見性を上げる。
3. **中期（需要確認後）**: Jira/Notion 同期に需要があれば、Serena と同じソフト依存パターンで `generate-prd` / `finalize-prd` に SKILL.md レベルの連携手順を追加する PoC を実施する。その際「仕様書を真実の源とする」原則との整合（同期方向・コンフリクト解決）を先に CONSTITUTION レベルで定義する。
4. **非採用**: プラグインへの `.mcp.json` / `.lsp.json` 同梱は、環境依存の強制・言語非依存性の毀損というデメリットが上回るため行わない。

## 6. 参考資料

- [PLUGIN.md](../PLUGIN.md) — MCP サーバー連携 / LSP サーバー連携セクション（設定形式・ベストプラクティス）
- `plugins/sdd-workflow/skills/check-spec/SKILL.md` — Serena MCP Integration セクション
- `plugins/sdd-workflow/skills/generate-spec/SKILL.md` — 同上
- `plugins/sdd-workflow/skills/task-breakdown/SKILL.md` — 同上
- `plugins/sdd-workflow/skills/check-spec/examples/serena_symbol_analysis.md` — シンボル解析出力例
