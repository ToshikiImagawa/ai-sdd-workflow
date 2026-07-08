---
id: "design-spec-design-generate-spec"
title: "仕様書・設計書生成"
type: "design"
status: "draft"
sdd-phase: "plan"
impl-status: "implemented"
created: "2026-07-08"
updated: "2026-07-08"
depends-on: ["spec-spec-design-generate-spec"]
tags: ["specification", "design-doc", "generation"]
category: "spec-design"
priority: "high"
risk: "high"
---

# 仕様書・設計書生成

**関連 Spec:** [generate-spec_spec.md](generate-spec_spec.md)
**関連 PRD:** [generate-spec.md](../../requirement/spec-design/generate-spec.md)（親: [spec-design](../../requirement/spec-design/index.md)）
**準拠する原則:** [CONSTITUTION.md](../../CONSTITUTION.md) A-001（Skills-First）, A-002（フックとスクリプトの責務分離）, B-002（多言語対応の一貫性）, D-002（ファイル命名規則の厳守）, T-003（日本語出力の文字化け防止）

---

# 1. 実装ステータス `<MUST>`

**ステータス:** 🟢 実装済み

本設計書は既存実装（`skills/generate-spec/`）の挙動を逆算して記述したものである。
トリガー方式（`/generate-spec` スキル呼び出し・`--ci` フラグ）・生成フロー・命名規則・
テンプレート適用ロジックは実装コードを真実の源とする。

## 1.1. 実装進捗

| モジュール/機能              | ステータス | 備考                                                                     |
|----------------------------|--------|------------------------------------------------------------------------|
| generate-spec スキル本体      | 🟢     | `skills/generate-spec/SKILL.md`（2 フェーズ実行・生成ルール・front matter 規則） |
| テンプレート前処理スクリプト     | 🟢     | `skills/generate-spec/scripts/prepare-spec.py`（テンプレート・参照のキャッシュ・環境変数エクスポート） |
| 日英テンプレート              | 🟢     | `skills/generate-spec/templates/{en,ja}/`（spec_template / design_template / spec_output） |
| 参照ドキュメント群            | 🟢     | `skills/generate-spec/references/`（生成フロー・front matter・既存文書チェック等） |
| レビュー連携                 | 🟢     | `agents/spec-reviewer.md`・`agents/front-matter-reviewer.md` を生成後に呼び出す |
| plugin.json 登録            | 🟢     | `.claude-plugin/plugin.json` の `skills` に登録済み（T-002）                   |

---

# 2. 設計目標 `<MUST>`

- 入力内容から抽象度を分離した 2 層のドキュメント（spec / design）を生成する（FR-001 / FR-002 / DC_001）
- 命名規則・テンプレート構造・front matter スキーマへの準拠を生成フローに組み込む（FR-003 / IR_001 / D-002）
- 対応 PRD の構造（フラット / 階層）に追従して出力先と `id` を決定する（FR-004）
- 決定的なファイル操作（テンプレート・参照のコピー、環境変数エクスポート）をスクリプトへ委譲し、
  Claude は判断・生成に専念する 2 フェーズ実行とする（A-002）
- 出力言語を `SDD_LANG` に従わせ、日本語出力の文字化けを防止する（NFR-001 / B-002 / T-003）
- 生成前のリスク評価（FR-007）・生成後のレビュー連携（FR-008）・CI モード分岐（FR-009）を
  スキルのオーケストレーション責務として組み込み、対話モードでは品質ゲートを維持する

---

# 3. 実装方式 `<MUST>`

| 領域     | 採用方式                                          | 選定理由                                                                                          |
|--------|-----------------------------------------------|-------------------------------------------------------------------------------------------------|
| skill  | Markdown プロンプトスキル（`user-invocable: true`）   | 入力解析・仕様/設計の生成・整合レビューは Claude の推論を要する。A-001（Skills-First）に従いスキルとして実装 |
| script | Python 3 スクリプト（2 フェーズ実行の前処理）            | テンプレート・参照のコピーと環境変数エクスポートは決定的操作。A-002 に従い機械的処理をスクリプトへ委譲しトークンを節約 |
| 多言語   | `SDD_LANG` + `templates/{en,ja}/` + プロジェクト優先 | B-002 の一貫性要件。プロジェクトの `SPECIFICATION_TEMPLATE.md` を優先し、無ければ言語別スキルテンプレートを使う |
| 出力先   | `SDD_*` 環境変数 + フラット/階層の分岐                | 出力先を環境変数で解決し、対応 PRD の構造に追従して保存パスと `id` を決定する（FR-004）                     |
| レビュー連携（FR-008） | サブエージェント呼び出し（Task 相当）              | 生成後の原則準拠・front matter 検証を spec-reviewer / front-matter-reviewer に委譲（責務分離）。各文書生成直後に逐次呼び出す |

---

# 4. アーキテクチャ `<MUST>`

## 4.1. システム構成図

```mermaid
graph TD
    U[開発者: /generate-spec 要件記述] --> SK[generate-spec SKILL.md]
    SK -->|Phase 1: 前処理| PS[prepare-spec.py]
    PS -->|.sdd-config.json 読取| CFG[lang / root]
    PS -->|テンプレート/参照コピー| CACHE[.sdd/.cache/generate-spec]
    PS -->|環境変数 export| ENV[CLAUDE_ENV_FILE]
    SK -->|Phase 2: 生成| GEN[Claude: 入力解析・生成]
    GEN -->|CONSTITUTION.md 読取| CONST[原則準拠]
    GEN -->|対応 PRD 確認| PRD[要求 ID / 構造]
    GEN -->|spec 生成| SPEC[{feature}_spec.md]
    GEN -->|design 生成| DESIGN[{feature}_design.md]
    SPEC --> RVS[spec / front-matter reviewer（spec）]
    DESIGN --> RVD[spec / front-matter reviewer（design）]
    RVS -->|指摘| GEN
    RVD -->|指摘| GEN
```

レビューは文書ごとに逐次実行する（spec 生成 → spec のレビュー → design 生成 → design のレビュー）。
`--ci` モードではリスク評価とレビューを省略する（FR-009）。

## 4.2. モジュール分割

| モジュール名                | 責務                                                                       | 依存関係                         | 配置場所                                                    |
|--------------------------|--------------------------------------------------------------------------|--------------------------------|-----------------------------------------------------------|
| generate-spec SKILL.md   | 入力解析・リスク評価（FR-007）・spec/design 生成（FR-001/002）・整合レビュー連携（FR-008）・CI モード分岐（FR-009）のオーケストレーション | prepare-spec.py, spec-reviewer, front-matter-reviewer | `plugins/sdd-workflow/skills/generate-spec/SKILL.md`      |
| prepare-spec.py          | テンプレート/参照のキャッシュコピーと `GENERATE_SPEC_*` 環境変数のエクスポート（前処理） | os, sys, json, shutil, pathlib | `plugins/sdd-workflow/skills/generate-spec/scripts/prepare-spec.py` |
| templates/{en,ja}/       | spec / design / 出力レポートの言語別テンプレート                                 | SDD_LANG                       | `plugins/sdd-workflow/skills/generate-spec/templates/{en,ja}/` |
| references/              | 生成フロー・front matter 規則・既存文書チェック・前提条件の参照ドキュメント             | -                              | `plugins/sdd-workflow/skills/generate-spec/references/`   |
| spec-reviewer（外部）      | 生成物の CONSTITUTION 準拠・トレーサビリティ・SysML 妥当性のレビュー                  | Read/Glob/Grep/AskUserQuestion | `plugins/sdd-workflow/agents/spec-reviewer.md`            |
| front-matter-reviewer（外部） | front matter の形式・依存方向・id 一意性の検証                                  | Read/Glob/Grep                 | `plugins/sdd-workflow/agents/front-matter-reviewer.md`    |

---

# 5. データ構造 `<OPTIONAL>`

## 5.1. 前処理スクリプトの環境変数エクスポート

`prepare-spec.py` は `.sdd-config.json` から `lang` / `root` を読み取り、テンプレートと参照を
`{root}/.cache/generate-spec/` にコピーしたうえで、`CLAUDE_ENV_FILE` に以下を追記する。
既存の `GENERATE_SPEC_*` 行は事前に除去してから書き込む（再実行時の重複防止）。

```sh
export GENERATE_SPEC_CACHE_DIR="{root}/.cache/generate-spec"
export GENERATE_SPEC_SPEC_TEMPLATE="{root}/.cache/generate-spec/spec_template.md"
export GENERATE_SPEC_DESIGN_TEMPLATE="{root}/.cache/generate-spec/design_template.md"
export GENERATE_SPEC_REFERENCES="{root}/.cache/generate-spec/references"
```

テンプレート解決の優先順位は「プロジェクトの `{root}/SPECIFICATION_TEMPLATE.md`・
`{root}/DESIGN_DOC_TEMPLATE.md` → 無ければスキルの `templates/{lang}/`」である。
なお `prepare-spec.py` はテンプレートのコピーのみを担い、プロジェクトテンプレートが不在の場合に
スキルテンプレートを基にプロジェクトの `*_TEMPLATE.md` を生成する処理は Phase 2（Claude）が担う。

## 5.2. 生成物の front matter スキーマ

| フィールド      | spec                                    | design                                     |
|--------------|-----------------------------------------|--------------------------------------------|
| `id`          | `spec-{feature}` / 階層: `spec-{parent}-{feature}` | `design-{feature}` / 階層: `design-{parent}-{feature}` |
| `type`        | `"spec"`                                | `"design"`                                 |
| `sdd-phase`   | `"specify"`                             | `"plan"`                                   |
| `status`      | `"draft"`（新規）                         | `"draft"`（新規）                            |
| `impl-status` | —                                       | `"not-implemented"`（新規）                  |
| `depends-on`  | PRD ID（例: `["prd-{feature}"]`）         | spec ID（例: `["spec-{feature}"]`）          |
| `priority` / `risk` | PRD から継承（無ければ `"medium"`）        | spec から継承                                |

**依存方向は上流のみ**（`prd ← spec ← design`）。下位ドキュメントへの参照は持たない。

## 5.3. 出力先パスの決定

| 構造            | spec                                                | design                                                |
|---------------|-----------------------------------------------------|-------------------------------------------------------|
| フラット         | `{SDD_SPECIFICATION_PATH}/{feature}_spec.md`         | `{SDD_SPECIFICATION_PATH}/{feature}_design.md`         |
| 階層（親機能）     | `{SDD_SPECIFICATION_PATH}/{parent}/index_spec.md`    | `{SDD_SPECIFICATION_PATH}/{parent}/index_design.md`    |
| 階層（子機能）     | `{SDD_SPECIFICATION_PATH}/{parent}/{feature}_spec.md` | `{SDD_SPECIFICATION_PATH}/{parent}/{feature}_design.md` |

対応 PRD が階層構造で存在する場合、または入力で親機能（カテゴリ）が指定された場合に階層構造を用いる。

---

# 6. ファイル構成 `<OPTIONAL>`

```
plugins/sdd-workflow/
├── skills/generate-spec/
│   ├── SKILL.md                  # スキル本体（2 フェーズ実行・生成ルール・front matter 規則）
│   ├── scripts/
│   │   └── prepare-spec.py       # Phase 1: テンプレート/参照のキャッシュ・環境変数 export
│   ├── templates/{en,ja}/        # spec_template / design_template / spec_output
│   ├── references/               # generation_flow / front_matter_spec_design / existing_document_check 等
│   └── examples/                 # 入力例・整合性チェック出力例・検証コマンド例
├── agents/
│   ├── spec-reviewer.md          # 生成後の原則準拠・トレーサビリティレビュー（外部連携）
│   └── front-matter-reviewer.md  # 生成後の front matter 検証（外部連携）
└── .claude-plugin/plugin.json    # skills に generate-spec を登録（T-002）
```

生成先は本プラグイン外の対象プロジェクトの `${SDD_SPECIFICATION_PATH}`（既定 `.sdd/specification/`）である。

---

# 7. 非機能要件実現方針 `<OPTIONAL>`

| 要件                                    | 実現方針                                                                                     |
|---------------------------------------|--------------------------------------------------------------------------------------------|
| NFR-001（言語の一貫性）                    | `SDD_LANG` に従い `templates/{en,ja}/` を選択。プロジェクト優先テンプレートも同一言語で運用             |
| NFR-002（命名規則・テンプレート・front matter 準拠） | 生成フロー内でサフィックス・テンプレート必須セクション・front matter スキーマを検証し、front-matter-reviewer で再確認 |
| NFR-003（移植性）                         | 前処理は標準ライブラリのみの Python 3。`CLAUDE_PROJECT_DIR` 未設定時は git root / cwd にフォールバック |
| T-003（文字化け防止）                       | 日本語テンプレート・生成物で UTF-8 を維持し、mojibake / U+FFFD の混入を出力前に確認                    |

---

# 8. テスト戦略 `<OPTIONAL>`

| テストレベル       | 対象                                          | カバレッジ目標                                          |
|----------------|---------------------------------------------|------------------------------------------------------|
| 手動検証（デモ）    | `/generate-spec` の spec / design 生成           | 命名規則準拠・テンプレート必須セクション網羅・front matter 妥当性 |
| 静的検査          | 生成物のマークダウンリンク・front matter               | spec-reviewer / front-matter-reviewer による検証        |
| Lint            | プロンプトファイルの構文・命名規則                       | リポジトリの `plugin-lint`（CI の `plugin-lint` ジョブ）      |

本機能は入力依存の生成であり自動ユニットテストは持たない。品質は生成後のレビューエージェント連携（FR-008）で担保する。

---

# 9. 設計判断 `<MUST>`

## 9.1. 決定事項

| 決定事項              | 選択肢                                  | 決定内容                          | 理由                                                                       |
|--------------------|-----------------------------------------|-----------------------------------|--------------------------------------------------------------------------|
| 実行方式             | 単一プロンプト / 2 フェーズ（スクリプト+Claude） | 2 フェーズ実行                      | A-002。テンプレート/参照のコピーは決定的操作でありスクリプト化しトークンを節約する         |
| テンプレート解決順     | スキル固定 / プロジェクト優先              | プロジェクト `{root}/*_TEMPLATE.md` を優先 | プロジェクト固有のテンプレート差異を尊重し、無い場合のみ言語別スキルテンプレートにフォールバック |
| 抽象度の分離          | 単一ドキュメント / spec と design の 2 層    | 2 層に分離                         | DC_001。spec は「何を」、design は「どのように」に責務を分け、ガードレールとして機能させる |
| レビューの内製 / 外部委譲 | スキル内で完結 / 外部エージェントへ委譲       | spec-reviewer / front-matter-reviewer へ委譲 | 品質レビュー・front matter 検証は独立責務であり、専用エージェントへ委譲して重複を避ける（責務分離） |
| CI モードの挙動        | 常に対話 / `--ci` で省略                   | `--ci` でリスク評価・レビューを省略し上書き自動承認・Design Doc を常時生成 | 非対話パイプラインでの自動生成を可能にする。生成省略の確認を挟まず design まで必ず生成し、対話モードでは品質ゲートを維持する（FR-009） |
| 出力エンコーディング    | ASCII エスケープ / UTF-8                   | UTF-8 を維持                       | T-003。日本語生成物の文字化けを防止する                                            |

## 9.2. 未解決の課題 `<OPTIONAL>`

| 課題                                       | 影響度 | 対応方針                                                          |
|------------------------------------------|-----|-----------------------------------------------------------------|
| 生成品質が基盤モデルの能力に依存する               | 中   | 生成後のレビューエージェント連携（FR-008）で担保。将来のモデル更新で改善            |
| spec-reviewer 連携が spec-review 機能と責務境界を跨ぐ | 低   | 本機能は呼び出し（オーケストレーション）のみを担い、レビュー本体は spec-review 機能を正典とする |

---

# 10. 原則準拠チェックリスト `<RECOMMENDED>`

| 原則ID  | 原則名                       | 準拠状況 | 備考                                                            |
|-------|-----------------------------|--------|---------------------------------------------------------------|
| A-001 | Skills-First                 | ✅     | `skills/generate-spec/` として実装（legacy commands 不使用）           |
| A-002 | フックとスクリプトの責務分離       | ✅     | テンプレート/参照コピーは `prepare-spec.py`、判断・生成は Claude に分離        |
| B-002 | 多言語対応（EN/JA）の一貫性       | ✅     | `SDD_LANG` + `templates/{en,ja}/`。プロジェクト優先テンプレートも言語一貫      |
| D-001 | Specification-Driven          | ✅     | spec / design を生成し Specify → Plan フローを支える中核機能               |
| D-002 | ファイル命名規則の厳守            | ✅     | `_spec` / `_design` サフィックスと構造別パスを生成フローで強制                 |
| T-002 | plugin.json 登録の徹底          | ✅     | `skills` に generate-spec を登録済み                                |
| T-003 | 日本語出力の文字化け防止           | ✅     | 生成物の UTF-8 維持・mojibake / U+FFFD の混入を出力前に確認                 |

**原則から逸脱する場合**: 理由を「9.1. 決定事項」に明記し、CONSTITUTION.md の例外プロセスに従うこと。
