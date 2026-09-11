# 変更履歴

このプラグインの重要な変更はすべてこのファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
このプロジェクトは [Semantic Versioning](https://semver.org/lang/ja/spec/v2.0.0.html) に準拠しています。

[English CHANGELOG](CHANGELOG.md)

## [Unreleased]

## [5.0.0] - 2026-09-10

**注記**: ドキュメントモデルに破壊的変更を含むメジャーリリースである。既存プロジェクトを
アップグレードする前に README.md / README.ja.md の「Migration from v4.x」を読むこと。ただし移行は
**急ぐ必要がない**。既存の `specification/*_design.md` は引き続き有効であり、命名フックも受理し、
技術設計を読むスキルは補助入力として読む。決定を `adr/` へ移すまで何も壊れないので、自分のペースで
進めればよい。

### Breaking Changes

#### ドキュメント構造

- **`specification/{feature-name}_design.md` は永続ドキュメントではなくなった** - 技術設計書は
  `task/{ticket-number}/design-draft.md` の一時ドラフトとなり、`task/` の他のファイルと同様、実装完了後に
  削除される。決定・その理由・却下した代替案のみが、新設の `adr/{feature-name}.md`
  （追記専用）に永続化される。v4.x 由来の既存 `specification/*_design.md` は**引き続き有効**であり、
  技術設計を読むスキルは補助入力として読み、いずれも命名違反として報告することも削除を提案することも
  ない（対象スキルの一覧は Fixed の「v4.x の永続設計書」項を参照）。それらの決定を
  `adr/{feature-name}.md` へ移すのは人間のペースで機能単位に進められる作業 —
  README.md / README.ja.md の「v4.x からの移行」を参照
- **`/generate-spec` にチケット番号が必須になった** - 設計ドラフトのパスがチケット単位
  （`task/{ticket-number}/design-draft.md`）になったため、`/generate-spec` は `--ticket <番号>`
  を受け取る（`--ci` モードでは必須、それ以外は対話的に解決）
- **`doc-consistency-checker` のチェック対象が PRD ↔ spec ↔ design から PRD ↔ spec ↔ adr へ変更**
- **`/check-spec` の比較基準が技術設計書から抽象仕様書（spec）へ変更** - 技術設計書は
  `task/{ticket-number}/design-draft.md` の一時ドラフトとなり実装完了後に削除されるため、恒久的な比較基準に
  できなくなった。`/check-spec` は `specification/` 配下の spec（サフィックス任意）を第一級の比較基準とし、
  設計ドラフトは存在する場合のみ補助入力として参照する。実装完了後にドラフトが存在しないことは正常な状態
  であり、乖離としては報告しない。spec は抽象仕様であるため、比較は spec から読み取れる項目（公開 API・
  データモデル・振る舞い・リテラル値）に限定し、モジュール構成・技術スタックはドラフトが存在する場合のみ
  比較する。`specification/` 配下に v4.x の `{feature}_design.md` を残しているプロジェクトでは、
  それらのファイルも同じ補助入力として扱う
- **`/plan-refactor` の Case A / Case B 判定が spec の有無ベースになり、計画の書き込み先が設計ドラフトに変更** -
  従来は `specification/{feature-name}_design.md` の有無で判定していたが、これは永続ドキュメントではなくなった
  ため、常に Case B に落ち、新方針が廃止したはずの永続設計書を逆生成して作ってしまっていた。判定は
  **spec の有無**（`_spec` サフィックスの有無どちらも検出）に変更し、リファクタリング計画と逆生成設計は
  `task/{ticket-number}/design-draft.md` に書き込む。逆生成 spec は従来どおり `specification/` 配下に
  永続化する。v4.x 由来の `*_design.md` が残っている場合も検出はするが、参照用のコンテキストとしてのみ扱い、
  Case 判定にも書き込み先にも使わない
- **`/plan-refactor` にチケット番号が必要になった** - 設計ドラフトのパスがチケット単位のため、
  `/plan-refactor` は `--ticket=<番号>` を受け取る（`--ci` モードでは必須、それ以外は対話的に解決）。
  既存の `task/{ticket-number}/design-draft.md` は Case A の補助入力として読み込まれる
- **`/task-breakdown` にチケット番号が必須になった** - 読み込む設計ドラフトと出力する `tasks.md` の
  いずれも `task/{ticket-number}/` 配下にあるため、チケット番号を省略できなくなった。`tasks.md` は
  常に `task/{ticket-number}/tasks.md` へ出力され、従来の `task/{feature}/tasks.md` へのフォール
  バックは廃止された

### Added

#### Skills

- **`/generate-prd --amend`** - 新規モード。既存 PRD を全上書きせず、新たに与えられた要求だけを追記する。
  既存の要求 ID・セクション・要求図ノードを保持し、新規 ID は既存の最大値（プレフィックス別）の続きから
  採番する。`finalize-prd` も `--amend` 呼び出し時は既存 PRD 本文を受け取り新規内容を統合するようになった
- **`/generate-spec --amend`** - 新規モード。既存の抽象仕様書を全上書きせず、新たな機能要求・非機能要求
  のみを追記する。既存の要求 ID・セクションは保持される
- **`render-adr-review`** - `adr/{feature-name}.md` の決定ログ（または `*_spec.md`/
  `*_design.md` の決定根拠セクション）を、単純な Markdown→HTML 変換ではなく決定・理由・却下した代替案の
  軸で構造化した一時レビューHTMLとしてレンダリングする新規スキル。生成物は
  `.sdd/.cache/render-adr-review/` 配下に出力され、コミットを想定しない。
  決定ログは覆しを一方向（新しいエントリ側）にのみ記録し、覆された側のエントリは編集しないため、
  失効した決定は原文中に何の目印も持たず現行の決定と同じに読めてしまう。本スキルは各エントリの
  `Supersedes` 参照を解決して指し先のエントリを失効として標示するので、陳腐化した決定が現行のものと
  視覚的に区別され、置き換えたエントリへのリンクを持つ。この標示には `Supersedes` 項目が記録している
  「何が変わったか」の1行も含み、リンク先は原文の Markdown アンカーを流用せず同一 HTML 内の覆した側の
  カードを指す。ファイルレベルの `supersedes` / `superseded-by` front matter フィールドはこの判定に
  一切使わない（決定ログファイルが丸ごと引退したことを表すフィールドであり、エントリ1件の失効を
  表さないため）。後から覆された決定も、自身の比較表の中では引き続き「採用」として表示される —
  その時点ではそれが選択されたものであり、覆しはエントリの状態に属する情報であって履歴を書き換える
  理由にはならない。`Rejected alternatives: None considered` は「代替案を検討していない」として扱い、
  却下された選択肢としては描画しない
- **`task-cleanup`** - 実装完了時にチケットへ要約コメントを投稿するようになった。また、`adr/` に統合する
  決定が「When to Update `*_spec.md`」の基準に該当するかを判定し、該当する場合は `AskUserQuestion` で
  Spec 更新を提案する
- **`/sdd-init` が `${SDD_ROOT}/ADR_TEMPLATE.md` を生成するようになった** - 決定ログのテンプレートを
  両言語でプラグインに同梱し、PRD / spec / design テンプレートと同様にコピーする（既存ファイルは
  上書きしない）。内容は確定した ADR エントリ形式、覆しを含む2エントリの記入例、そして「最後の
  エントリの下に追記し、上のエントリには触らない」という注記。なお `/sdd-init` が作成するのは
  `${SDD_ROOT}/` ルートのみで、`adr/` は `requirement/`・`specification/`・`task/` と同じく
  最初のファイル書き込み時に自動作成される
- **`/sdd-init` がキャッシュディレクトリをプロジェクトの `.gitignore` に追記するようになった** -
  `.sdd/.cache/`（カスタムルートなら `${SDD_ROOT}/.cache/`）には生成物で使い捨ての内容
  （ドキュメントインデックス、スキルごとの作業用コピー、`render-adr-review` の HTML）が入るが、
  無視するかどうかは利用者に任されていた。`${SDD_ROOT}/` の外にあるファイルへの**新規の書き込み**である
  ため、挙動は意図的に最小限にしている: 内容を説明するコメント付きで1度だけ追記し、既存の `.gitignore`
  の行はすべて保持し（末尾改行が無い場合のみ補う）、`.gitignore` が無ければ当該エントリのみで新規作成し、
  既に同じパスを無視しているプロジェクト（先頭・末尾のスラッシュの差は同一視）には何もしない。
  `/sdd-init` を再実行しても行は重複しない。無視されるのは `.cache/` のみで、`${SDD_ROOT}/` 配下の
  PRD・仕様書・設計ドラフト・決定ログは追跡対象のまま
- **`/check-spec --ticket <番号>`** - 補助入力の設計ドラフトを対象チケットに絞り込む（後述の Fixed 参照）

#### Configuration

- **`SDD_ADR_DIR` / `SDD_ADR_PATH`** - `adr/` ディレクトリ用の環境変数を新設。既存の `SDD_*_DIR` /
  `SDD_*_PATH` と同じパターンでセッション開始時に設定される

#### Hooks

- **`${SDD_ROOT}/MIGRATION_PENDING.md` が、移行待ちの v4.x ドキュメントを一覧するようになった** -
  プロジェクトに `specification/**/*_design.md` が残っている場合、SessionStart フックがこのファイルに
  それらを列挙（最大10件、超過分は件数で要約）し、(a) それらは引き続き有効で補助入力として読むこと、
  (b) 決定の移行先は `adr/{feature-name}.md`、(c) 新規の技術設計は
  `task/{ticket-number}/design-draft.md`、(d) 移行が済むまで元ファイルを削除しないこと、を記載する。
  手順の在り処は「プラグインの README を参照」ではなく、実際に開けるパスとして示す —
  `<plugin root>/README.md` の「Migration from v4.x」配下の
  「Extracting Existing `*_design.md` Files into `adr/`」節（日本語は同ディレクトリの `README.ja.md`）。
  このファイルは **`UPDATE_REQUIRED.md` とは意図的に別建て**である。`UPDATE_REQUIRED.md` は
  `CLAUDE.md` が古いことだけを報告し `/sdd-init` を実行すれば消えるが、未完了の移行は別軸・別ペースの
  関心事であるため、`MIGRATION_PENDING.md` は `/sdd-init` を跨いで残り、該当ファイルが1件でもある限り
  セッション開始ごとに書き直され、0件になると自動的に削除される。生成ファイルなので手編集は次の
  セッションで置き換わる。該当ファイルが無いプロジェクトには生成されない。なお `UPDATE_REQUIRED.md` は
  存在するとスキルが実行前に `/sdd-init` を促す一方、`MIGRATION_PENDING.md` は実行前チェックではない —
  移行が未完了でもスキルの実行が止まることはない

#### Front Matter

- **`sdd-version` 共通フィールド** - ドキュメントは front matter の `sdd-version` フィールドに、
  生成時点の sdd-workflow プラグインバージョン（`plugin.json` から取得）を記録できるようになった。
  `generate-spec`・`generate-prd`・`finalize-prd`・`task-cleanup` が front matter 生成時にこの値を
  設定する。このフィールド導入前に生成されたドキュメント、または `recommend-front-matter` が既存
  ドキュメントへ後付けで front matter を付与した場合は存在しない（後付け時に現行バージョンを設定すると
  偽の生成世代情報になるため、意図的に付与しない）
- **`sdd-version` を読み取り側でも活用** - ドキュメントインデックス（`.cache/index.md`）の Metadata
  テーブルに `sdd-version` を含めるようになった。`front-matter-reviewer` はその semver 形式を検証し、
  現行プラグインの major より古い場合は警告する（移行漏れの可能性を示す advisory）。
  `doc-consistency-checker` は「世代が古いドキュメント」と「世代不明のドキュメント」（`sdd-version` が
  そもそも無い＝v5 以前に書かれたものの通常状態）を、人間による移行レビュー用の2つの独立した候補リスト
  として一覧化する
- **`type: "adr"` スキーマ** - `shared/references/front_matter_reference.md` に決定ログの
  front matter フィールドを定義した。`status`（記録時点で常に `"approved"`）と `supersedes` /
  `superseded-by` を含む。後者2つは**ファイルレベル専用**である: 1つの決定ログは多数のエントリを
  持つが front matter は1つしかないため、これらは「決定ログファイルが丸ごと引退して置き換えられた」
  （機能のリネーム・分割・統合）ことを記録する。エントリ間の覆しは新しいエントリの本文に記録する —
  後述の ADR エントリ形式を参照
- **`impl-status` が Design 専用ではなく Spec でも有効なフィールドになった** - spec は、承認ライフサイクル
  （`status`）とは独立した軸として、自身が記述する振る舞いが実装に反映されているかを記録できるようになった。
  `generate-spec` が新規 spec に `"not-implemented"` を設定し、`implement` が実装の進行に応じて
  `"in-progress"` / `"implemented"` へ進め、`implement` が更新し忘れた場合の安全網として `task-cleanup` も
  更新する。`check-spec` は、仕様書に記載され実装が見つからない機能を常に Critical とするのではなく、この
  フィールドで分岐するようになった：`implemented` なら退行として Critical、`not-implemented`/`in-progress`
  なら意図した先行として Info、フィールド未設定なら判定不能として Warning（追加を推奨）。
  `front-matter-reviewer` は spec の `impl-status` の許容値も検証し、`recommend-front-matter` は本
  フィールドが欠落している spec を列挙する — 実装の実態を確認しないスキルであるため、値の書き込みは
  行わない（後述の Changed 参照）

#### ワークフローガイダンス

- **タスク種別判定に破壊的変更が追加された** - `AI-SDD-PRINCIPLES.md` の Task Type Determination 表と
  Task Scale Criteria に "Breaking Change" 行が追加され、影響範囲の洗い出し・後方互換性の方針決定・
  移行手順の記録先（`adr/`）を定義する新設の "Breaking Change Handling" 節が追加された。この表は
  `.claude/rules/ai-sdd-instructions.md` にも転記され、原則ドキュメントを開かなくても全プロジェクトに
  同じガイダンスが届くようになった
- **PRD が存在しない場合の新規起草が明示的に許可された** - `AI-SDD-PRINCIPLES.md` は「PRD は自動更新しない」
  というルールが既存 PRD の書き換えを禁じるものであり、存在しない PRD をゼロから起草する行為には適用され
  ないことを明記した。起草した PRD は人間が承認するまで `status: "draft"` と `"reverse-engineered"` タグを
  付ける。`/plan-refactor` は逆生成した spec に依存先の PRD が無い場合、この起草を提案するようになった
- **`vibe-detector` が推奨開始フェーズを出力するようになった** - リスクレポートは、従来の曖昧さリスク評価に
  加えて、依頼内容をタスク種別判定表に照らして分類し、対応する開始フェーズ（Specify/Plan/Tasks/Implement）
  を報告する
- **ADR エントリの本文形式が各スキル任せではなく仕様として確定した** - `AI-SDD-PRINCIPLES.md` の
  Architecture Decision Record に "Entry Format" 節を追加した。1ファイルは front matter 1個 + `#`
  タイトル1個 + 末尾に追記される `##` エントリ多数で構成される。各エントリの見出しは
  `## YYYY-MM-DD {decision title}` で、**Decision**・**Rationale**・**Rejected alternatives**
  （該当が無ければ `None considered`。捏造は禁止）を必ず持ち、同一ファイル内の過去エントリを覆す場合
  のみ任意の **Supersedes** でそのエントリへリンクする。覆しは新しいエントリ側に一方向で記録し、
  覆された側のエントリは逆参照の追加すら行わない（追記専用を保つため）。したがって最後のエントリが
  常に現行の決定である。これらの項目は `render-adr-review` と `doc-consistency-checker` が抽出する
  フィールドと1対1で対応するため、この形式で書けば追加の取り決めなしにスキルから読める

### Fixed

- **`adr/` がドキュメントインデックスと `/recommend-front-matter` の走査対象になった** - いずれも
  従来は `requirement/` と `specification/`（後者は加えて `task/`）のみを走査しており、決定ログが
  圧縮インデックスや front matter 推奨結果に一度も現れなかった
- **決定ログの編集でドキュメントインデックスが更新されるようになった** - `PostToolUse` のリマインダー
  自体は発火していたが、他のドキュメント種別では発火するインデックス更新が `adr/` では実行されて
  いなかった
- **`AI-SDD-PRINCIPLES.md` の Configuration Items 表と `.sdd-config.json` の例に `directories.adr`
  を記載** - `session-start` はこの設定を既に `SDD_ADR_DIR` / `SDD_ADR_PATH` に解決しており、`adr/`
  自体は最初のファイル書き込み時に作成される（`/sdd-init` が作成するのは `${SDD_ROOT}/` ルートのみで、
  サブディレクトリは作らない）。欠落していたのは設定項目のドキュメント記載のみだった
- **`doc-consistency-checker` の Obsolescence Detection に、決定の覆しを記録する方法を明記** -
  従来は追跡対応が未定義だった。同じ `adr/{feature-name}.md` の末尾に、必須項目と、覆す対象エントリへの
  `Supersedes` リンクを備えた新しいエントリを追記する提案に置き換えた。陳腐化したエントリは一切変更
  しない — 逆参照も追加せず、`status: "deprecated"` にも書き換えず、ファイルレベルの `supersedes` /
  `superseded-by` front matter フィールドにも書かない（同一ファイル内のエントリ間の関係は、そもそも
  front matter では表現できない）
- **`adr/{feature}.md` の front matter に `ticket` フィールドを追加し、`task-cleanup` がこれを設定
  するようにした** - チケットのトラッカー（GitHub Issue / JIRA）に到達できない場合、`task-cleanup`
  はステップ9（完了サマリの投稿）を代替手段なしにスキップしており、`task/{ticket-number}/` を削除する
  とチケット番号と機能の唯一の対応関係が失われていた。ステップ7で作成する `adr` エントリが `ticket`
  を記録するようになったため、トラッカーに到達できない場合でも対応関係が保持される
- **`run-checklist` が実際にテスト・リンタ・セキュリティスキャナを実行できるようになった** -
  `allowed-tools` にシェル実行権限が一切無く、スキルの核心機能（検証コマンドの実行）が静的解析による
  推測に黙って後退していた。プロジェクトのツールチェーンを検出しテスト/リンタ/型検査/セキュリティ
  コマンドを実行する `scripts/run-verification.py`（`references/verification_commands.md` のマッピングを
  実装）を新設し、このリポジトリの「ベアな`Bash`は使わない」規約に沿ってこのスクリプトのみを事前承認した。
  テストが未設定のプロジェクトは `FAIL` ではなく `SKIPPED` として報告するため、未設定のカテゴリが
  品質ゲートを落とすことはない。スクリプトが扱わないカテゴリ（フォーマッタ検査・依存関係解析・
  ドキュメントカバレッジ）は、自動検証されるかのような記述を避け、手動レビュー項目として
  `references/verification_commands.md` に明示した
- **README.md / README.ja.md の権限節が、事前承認の実態より安全側に書かれていたのを修正** -
  「シェル実行を一切事前承認していないスキル」の列挙に `/run-checklist` が残っていたが、本リリースで
  同スキルに `scripts/run-verification.py`（上記）を与えた時点でこれは事実でなくなっていた — この
  スクリプトはプロジェクト自身のテスト・リンタ・型検査・監査コマンドを確認なしにサブプロセスで起動する。
  インストール前に判断すべき情報であるため、権限節にはスクリプトのフルパス、検出に使うプロジェクト
  マーカー（`package.json`・`pyproject.toml`・`Cargo.toml`・`go.mod`・`setup.py`・`requirements.txt`・
  `Gemfile`、およびマニフェストが1つも無い場合は `test_*.py` / `*_test.py` を含む `tests/`・`test/`
  ディレクトリ）、ツールチェーンごとに実行するコマンド、1コマンドあたり300秒の
  タイムアウト、そして `checklist.md` 内に書かれたコマンドは**実行されない**こと（事前承認されているのは
  ベアな `Bash` ではなくこのスクリプト1本だけであるため）を記載した。スキルが事前承認しているヘルパー
  スクリプト10本を列挙し、そのうち別プロセスを起動するのはこの1本だけであることも明記した。
  v4.0.1 で `Bash` を外した3スキルのうち、シェル実行を一切事前承認しないまま残るのは
  `/implement` と `/task-cleanup` の2件である
- **`checklist` のテンプレートが自身のSKILL.mdと矛盾しなくなった** - テンプレートは `P0`〜`P3` の優先度と
  `CHK001` 通し番号を使っていたが、SKILL.md本文のProcessing Flowと正準例
  （`examples/checklist_full_example.md`）は `P1`〜`P3` と `CHK-{カテゴリ}{連番}`（例: `CHK-501`）を
  定義していた。両言語のテンプレートを正準の形式に書き換え、テンプレートにのみ存在した「10.
  プロジェクト原則レビュー」カテゴリを要求レビュー内（`CHK-104`/`CHK-105`）に統合して
  `run-checklist` の `CHK-1xx`〜`CHK-9xx` マッピングが前提とする9カテゴリ構成を維持し、Export
  Formats節に残っていた（存在しない）「P0 items」という記述も修正した
- **`vibe-detector` のEscalation手順が、実行できない操作を指示しなくなった** - `disallowed-tools` は
  `Write`/`Edit`/`Bash` を意図的に禁止している（`user-invocable: false` であり、ユーザーの明示的な
  呼び出しなしに実装前へ自動介入するため、読み取り専用を維持する設計）が、Escalation節は
  `assumed-spec.md` への直接保存を指示していた。今後は推定仕様の内容を自身の
  出力に含め、呼び出し元セッション（通常の書き込み権限を持つ）に保存を委ねる
- **`recommend-front-matter` がADRのスキーマを認識するようになった** - `scan-documents.py` は既に
  `adr/` を走査・分類していたが、スキルのPrerequisitesと `type_specific_fields.md` テンプレートには
  ADRのフィールド定義が一切無く、front matterが無い決定ログへの推奨が不完全または創作的になっていた。
  `references/front_matter_adr.md` を新設し、両言語の `type_specific_fields.md` にADRの項目を追加した。
  あわせて、スキル自身の `type` 列挙と `depends-on` 推論表にも `adr` を追加した（走査対象の他の型は
  すべて列挙されていたため、これが無いと新設したリファレンスに到達しない）
- **`naming.py::determine_type()` が `task/{ticket}/design-draft.md` を `type: "task"` に誤分類
  しなくなった** - `implementation_log`/`impl_log` というファイル名は特別扱いしていたが、新世代の
  設計ドラフトの正規配置場所である `design-draft.md` の分岐が無く、`recommend-front-matter` 等の
  呼び出し元が誤ったtype別フィールドを推奨していた
- **`constitution` の2つのバージョンバンプ表が行単位で一致するようになった** - 「Update Constitution」
  の表は原則追加をMAJORバンプとしていたが、専用の`add`手順と「Semantic Versioning」表はいずれもMINOR
  としていた。さらに同じ表は「Clarify principle」をMINORとする一方、「Semantic Versioning」表は同じ行為で
  ある「Fix expression of principle」をPATCHとしており、「Conditions for Major Version Bump」節が破壊的変更
  として挙げる優先度変更の行も欠けていた。両表が同じ変更種別を列挙し、「既存の原則が要求する内容を変えるか」
  という単一の基準で分類する形に統一した
- **`sdd-init` の「Configuration File Management」節が、自身のスクリプトと矛盾しなくなった** -
  `init-structure.py` が `.sdd-config.json` 不在時にデフォルト値で自動生成すると記述していたが、
  実際のスクリプトはエラー終了する（意図的な設計 — デフォルト生成の責務はSessionStartフックが持ち、
  `sdd-init`側では重複させない）。記述を実際の意図された挙動に修正した
- **`front_matter_reference.md` のADRスキーマが、自身のStatus Transition Rulesと矛盾しなくなった** -
  フィールド表はADRの`status`に `draft`/`review`/`approved`/`deprecated` のライフサイクルを列挙して
  いたが、Status Transition Rules節は「ADRはそのライフサイクルに従わない」と明記していた。ADRの
  `status` は記録時点で常に `"approved"` であり、決定の覆しは新しいエントリ本文の `Supersedes` 項目に
  一方向で記録する（ファイルレベルの `supersedes` / `superseded-by` は決定ログファイルが丸ごと引退して
  置き換えられたことのみを表す）、という記述に修正した
- **`finalize-prd` の Rule 7（Amend Mode Integration）が、自身のPRDテンプレートと矛盾しなくなった** -
  新規UR/FR/NFR行の挿入先を「§4（Detailed Requirements）内の表の末尾」と記述していたが、
  `templates/{en,ja}/prd_template.md` の §4 は `### FR_001: {name}` というプローズ見出し形式であり
  テーブルは存在しない。記述をテンプレート実態（新規サブセクションを既存エントリと同じ体裁で追加する）
  に修正した。あわせて、新規ユースケースの関係線（`<<include>>`/`<<extend>>`）の接続先が呼び出し元から
  明示されない場合のデフォルト方針と、入力側にはあるが既存PRD構造に対応する欄が無い属性（例:
  Priority）を黙って落とさずプローズ内に明記する方針を追加した
- **README.md / README.ja.md の「v4.x からの移行」手順が実際に機能するようになった** - 手順1は
  「`/sdd-init` を再実行して `adr/` ディレクトリとテンプレートを作成する」と案内していたが、スクリプトが
  作成するのは `${SDD_ROOT}/` ルートのみであり、そもそも ADR テンプレート自体が存在しなかった。手順6は
  「`*_design.md` を削除したら `/check-spec`（または `doc-consistency-checker`）で確認する」と案内して
  いたが、どちらのスキルもリンク健全性を検査しないため、そのまま従うと壊れた `depends-on` と本文リンクが
  黙って残る。手順1は再実行で実際に得られるもの（`ADR_TEMPLATE.md`。`adr/` は最初の書き込み時に作成
  される）に修正した。手順6は実行可能な `grep` 2本に差し替えた — パス参照用（`_design\.md`）と ID 参照用
  （`design-{feature-name}`、階層構造では `design-{parent}-{feature}`）で、いずれも `.sdd/.cache/` と
  `.sdd/AI-SDD-PRINCIPLES.md` を除外する（どちらもインストール済みプラグインから再生成される生成物で、
  ヒットするのは利用者のドキュメントからの参照ではなくプラグイン自身の説明文である）。除外が無いと
  検索結果が生成物で埋まって実用にならなかった。手順の指示も、実際に削除したファイルを指すヒットのみを
  更新すること・散文での規約言及は参照ではないこと・リンク切れはどのスキルも報告しないこと・旧ファイルを
  残す選択も妥当であることに書き換えた。残りの手順も確定した ADR エントリ形式と実際の front matter
  フィールド一覧に合わせた
- **README.md / README.ja.md が破壊的変更を網羅し、チケット番号の扱いを説明するようになった** -
  「v5.0.0 の破壊的変更」節は今回の破壊的変更のうち3件しか挙げておらず、`/check-spec` の比較基準の反転、
  `/plan-refactor` の Case 判定変更とチケット引数追加、`/task-breakdown` のチケット番号必須化と
  フォールバック廃止、`doc-consistency-checker` の対象変更は、この変更履歴を読まないと分からなかった。
  節の内容を本節と1対1で対応させた。さらに新設の「チケット番号について」節で、スキルごとの渡し方
  （オプション／位置引数）と必須性を一覧化し、チケットトラッカーを使っていないプロジェクトは任意の
  安定した識別子（機能名が最も簡単）を使えることを説明した — トラッカーを必要とするのは
  `/task-cleanup` の完了コメントだけで、到達できない場合はスキップされ、対応関係は
  `adr/{feature-name}.md` の `ticket` front matter フィールドに残る。あわせて `/sdd-init` の説明を実態に
  修正し（作成するのはルートのみ。`CONSTITUTION.md` は `/constitution init` で作る）、環境変数表に
  `SDD_INDEX` を追加した
- **README.md / README.ja.md のコンポーネント表と `/check-spec` の説明が、同梱スキルの実態に一致した** -
  表は `doc-consistency-checker` を「PRD ↔ spec ↔ design を検査」と説明し続けており、本リリース自身の
  破壊的変更一覧と矛盾していた。他にも6行がスキル側の description からずれていた（`/plan-refactor` の
  「設計書を作成／更新」、`/generate-prd` を SysML 出力に限定した記述、`/check-spec` の対象を抽象仕様書
  ではなく「仕様書」とした記述、`/task-breakdown` が「技術設計書」を読むという記述、`/checklist` と
  `/task-cleanup` が廃止済みの退避先を挙げていた記述）。全行をスキルが実際に宣言している description と
  突き合わせて修正し、`spec-reviewer` / `front-matter-reviewer` の行には `adr/` 関連の責務を追記した。
  `/check-spec` の節も、「複数チケットが並行していて `--ticket` を省略するとどのドラフトも読まない」という
  誤った説明を、スキルが実際に持つ5つの結果（ドラフト無し／`--ticket` 指定／`depends-on` 一致／
  ドラフトが1件だけ／候補複数で根拠なし）の一覧に置き換え、`--ticket` が必須なのは最後のケースのみで、
  ドラフトに `depends-on` を書けば回避できることを明記した。`--full` が実際に何をレビューするか
  （決定ログが解決できない機能は「整合」ではなく「該当なし」であることを含む）も明示した。v5 への言及が
  一切無かった配布リポジトリのランディング README も、インストール済みプラグインの更新手順と看板の
  破壊的変更2点を扱い、移行節へリンクするようになった
- **v4.x の永続設計書の扱いが、技術設計を読むすべての箇所で揃った** -
  `check-spec`・`plan-refactor`・`task-breakdown` は
  以前から残存する `specification/*_design.md` を補助入力として読んでいたが、プラグインの他の部分は
  それらとも互いとも食い違っていた: `/implement` はこれを Technical Design 前提条件の充足として
  認めないため、v4.x で着手した機能を再開すると存在したことのない設計ドラフトの再生成を促された。
  `/generate-spec` の既存ドキュメントチェックは一切探索しないため、記録済みの技術スタックやモジュール
  構成と矛盾するドラフトを生成しうる。`/checklist` と `/clarify` は完全に無視しており、設計レビュー項目と
  設計レベルの質問が抽象仕様書から読み取れる範囲に狭まっていた — v4.1.0 はこの設計書を読んでいた
  （`/checklist` は必須入力としていた）ので、リリース版に対する退行だった。`spec-reviewer` はレビューできず、
  `task-cleanup` は「別フローで
  削除される一時ファイル」と宣言し、`plan-refactor` は「手動移行が必要」と述べ、命名クイックリファレンスは
  命名フックが従来から許容しているにもかかわらず「Incorrect Naming (never use these)」に列挙していた。
  `/check-spec`・`/checklist`・`/clarify`・`/constitution`・`/generate-spec`・`/implement`・
  `/plan-refactor`・`/recommend-front-matter`・`/sdd-init`・`/task-breakdown`・`/task-cleanup`・
  `doc-consistency-checker`・`spec-reviewer`・`front-matter-reviewer` のすべてが同じ扱いに揃った:
  これらのファイルは**引き続き有効**であり、**補助入力として読み**、
  **不在は正常**、新規の技術設計は常に `task/{ticket-number}/design-draft.md` へ書き、いずれも
  命名違反として報告したり削除を提案したりしない。`/checklist` と `/clarify` はこの設計書をチケット番号
  ではなく**機能名**から解決する（フラットなら `{feature-name}_design.md`、階層構造なら
  `{parent-feature}/index_design.md` / `{parent-feature}/{feature-name}_design.md`）ため、チケット番号を
  省略しても参照される。また両スキルはこれを読み取り専用として扱い、回答やチェックリストの編集を
  書き戻さない。`/checklist` が生成するチェックリストはどの設計ソースを使ったかを記録する。なお
  「チケットディレクトリに設計ドラフトも `tasks.md` も無い」という `/checklist` の警告は従来どおり出る —
  この設計書は `specification/` 配下にあり、チケットについて何も語らないため
- **`/generate-spec` の完了レポートが、生成していないファイルを生成したと報告しなくなった** -
  今回のリリースで廃止したはずの `specification/{feature}_design.md`（階層構造では `index_design.md`）
  を生成物として報告し、次ステップと検証コマンドに実在しないコマンド名 `/task_breakdown` `/check_spec`
  を提示していた。永続 spec と一時ファイル `task/{ticket-number}/design-draft.md` を実際の書き込み先と
  して報告し（ドラフトをスキップした場合は行を削除して理由を書く指示付き）、次ステップは実在する
  `/task-breakdown {feature} {ticket-number}`・`/check-spec`・およびドラフト削除前に決定を `adr/` へ
  移す `/task-cleanup {ticket-number}` を提示するようになった
- **`/generate-prd` の完了レポートが、その時点では必ず失敗するコマンドを案内しなくなった** -
  PRD を書いた直後に実行する検証コマンドとして `/check-spec {feature} --full` を提示していた。しかし
  その時点では `specification/` が存在しない（他のサブディレクトリと同様、最初のファイル書き込み時に
  作成される）ため、案内に従うと `/check-spec` は毎回「Specification directory not found」で停止した。
  レポートは実行可能性でコマンドを2分割するようになった: PRD 単体で動作する `/clarify {feature}`
  （回答は `requirement/` へ書き込めないため、`/generate-spec` の入力に載せるか手で PRD に反映する旨を
  付記）と、仕様書が必要な `/check-spec {feature} --full`（理由付き）。次のステップはコピー＆ペーストで
  動く `/generate-spec --ticket {ticket-number} {requirements-description}` になり、「生成されたファイル」
  節には、このスキルが書き込むドキュメントは PRD 1ファイルだけである旨（ユースケース図・UR/FR/NFR 表・
  SysML 要求図は PRD 内部のセクションであり別ファイルではない）を明記した
- **プロジェクトへコピーされる spec テンプレートが v5 のドキュメントモデルを説明するようになった** -
  `.sdd/SPECIFICATION_TEMPLATE.md` は技術スタックの選定理由・アーキテクチャ・設計判断の記録を永続
  `xxx_design.md` へ退避させ続け、`adr/` に一切言及していなかったため、これを元に書いた spec は
  廃止済みドキュメントを指し続けていた。比較表を3ドキュメント（spec: 永続 / 設計ドラフト: 一時 /
  決定ログ: 永続・追記専用）に更新し、ヘッダーに Related Design Draft と Related Decision Log を持たせ、
  除外内容を退避先別に分割し（決定・その理由・却下した代替案は `adr/{feature-name}.md` へ、それ以外の
  技術内容はドラフトへ）、ドラフトにしか書かれていない決定はドラフト削除時に失われることを警告する
- **`task-cleanup` が `task/{ticket-number}/` を削除する前に `adr/` への追記結果を検証するようになった** -
  削除ステップは統合が実際に反映されたかを確認せずに `git rm` を実行していたため、抽出漏れや編集失敗が
  あると設計判断が永久に失われた。削除の前に検証ゲートを通すようになった: 決定ログをディスクから再読込し、
  追記したエントリの `## YYYY-MM-DD {title}` 見出しと Decision / Rationale / Rejected alternatives が
  存在し空でないこと、実行前から存在したエントリが無改変であること、直前ステップの front matter および
  他ドキュメントの編集がディスク上にあることを確認する。いずれかが失敗した場合は何も削除せず、
  `task/{ticket-number}/` を残して欠落を報告する
- **`task-cleanup` がコミットされていない `task/` ディレクトリも削除できるようになった** - 削除手段が
  `git rm` 固定だったため、未追跡のパスに対しては
  `fatal: pathspec '...' did not match any files` で失敗して何も削除せず、かつスキル側は「別の削除経路を
  試みるな」と定めていた。そのため `task/` を Git にコミットしない運用のプロジェクトでは、検証まで
  通ったクリーンアップを最後まで完了できなかった。まず対象に対して `git ls-files` を実行して追跡状態を
  確定し（一致有無に関わらず exit 0 なので**出力**で判断する）、追跡されていれば `git rm`、未追跡なら
  素の `rm`、混在しているディレクトリでは追跡分と未追跡分をそれぞれのコマンドで削除するようになった。
  未コミットの `task/` に対する `rm` は回避策ではなく正規の経路として明文化されている。このスキルは
  依然として `Bash` を事前承認していないため、`git ls-files` と各削除コマンドは都度確認を求める。
  ユーザーが削除自体を断った場合は停止して報告し、確認プロンプトを回避するために削除コマンドを
  切り替えることは禁止されている。確認回数を減らすために許可リストへ登録する場合の対象は
  `git ls-files`・`git rm`・`rm` の3つで、README の `settings.json` の例も3件を列挙し、`rm` を許可すると
  あらゆる `rm` を許可することになる旨を注記した
- **`doc-consistency-checker` が、実際には評価していないプロジェクトに「stale 0件」と報告しなくなった** -
  `sdd-version` を持たないドキュメントは stale リストから明示的に除外されており、このフィールドは v5 以前に
  書かれたものには存在しないため、v5 以前のドキュメントだけで構成されたプロジェクトは常に「stale: 0」と
  報告され、移行完了と区別できなかった。stale（`sdd-version` あり・major が古い）と世代不明
  （`sdd-version` 不在）を別々に数えて2つのリストとして報告し、片方が0でも必ず両方を出す
  （例: `stale: 0 / generation unknown: 85 of 85 checked`）。いずれも Grep + Glob で算出するため、
  ドキュメントインデックスが無効でもこの検査はスキップされない
- **`doc-consistency-checker` が、検査していない領域を「問題なし」と報告しなくなった** - `adr/` が空で
  v4.x の `specification/*_design.md` しか無い場合、spec ↔ 決定記録の検査はそもそも実行されないまま
  レポートが「問題なし」で返っていた。分岐するようになった: `adr/` にエントリがあれば従来どおり検査し、
  エントリが無く v4.x の設計書がある場合は同じ4項目をその設計書に対して実行して
  `spec ↔ design (v4.x legacy)` として報告し、どちらも無い場合は `not checked` と報告する（決して
  consistent とは報告しない）。すべてのレポート冒頭に、使用した決定記録のソースと、実行できなかった
  検査領域とその理由を明示する
- **`front-matter-reviewer` が `adr/` のドキュメントを検証できるようになった** - 型判定・id パターン・
  相互参照の Glob 対象のいずれからも `adr/` が欠けていたため、`adr-*` 参照はすべて未解決に見え、`adr/`
  内の id 重複は検出されず、ADR 固有のフィールドは一度も検査されなかった。`adr/*.md` を
  `type: "adr"`（`task/{ticket-number}/design-draft.md` を `type: "design"`）と判定し、`adr-*` の id を
  受理し、ADR 固有フィールドを検査し、ファイルレベルの `supersedes` / `superseded-by` の相互ポインタを
  双方向で確認し、エントリ見出しやアンカーがそれらのファイルレベルフィールドに書かれている場合は
  error として本文への移動を勧告するようになった。`sdd-version` の不在は info（世代不明）として報告し、
  黙って落とさない
- **`spec-reviewer` が設計ドラフトをレビューするようになった** - Input Format と技術設計レビュー節が
  `specification/{feature}_design.md` を要求し続けていたため、`/generate-spec` が実際に生成するものを
  レビューできなかった。`task/{ticket-number}/design-draft.md` を受け取り（不在は正常であり、その場合
  spec ↔ design のトレーサビリティ検査は not applicable として報告する）、廃止された階層構造チェックの
  代わりにチケットスコープを検査し、後の `adr/` エントリに必要な却下代替案を求め、v4.x の設計書は
  補助入力としてレビューする
- **`/check-spec` が他チケットの設計ドラフトを比較に混入させなくなった** - ヘルパースクリプトが `task/`
  配下の `design-draft.md` を全件収集していたため、複数チケットが並行していると別チケットの設計が補助
  入力として渡され、無関係な機能に対してモジュール構成の警告を出していた。ドラフトの選定は
  `--ticket <番号>` が与えられていればそれ、次にドラフトの `depends-on` が対象 spec の id と一致するもの、
  次にプロジェクト内でドラフトが1件だけならそれ、という順になった。候補が複数残り根拠が無い場合は1件も
  採用せず、候補を列挙して `--ticket` 付きでの再実行を勧める。同じスクリプトは先頭のフラグを機能名と
  誤認しなくなった（従来は `/check-spec --full` が `--full` という名前の spec を探していた）
- **`/check-spec` が降格した乖離の件数を報告するようになった** - `impl-status` による Critical の降格は
  黙って行われ、かつ v4.x のドキュメントには `impl-status` が存在しないため、レポート全体が降格された
  うえで「Critical 0件」と読まれうる状態だった。Warning への降格（フィールド不在）と Info への降格
  （`not-implemented` / `in-progress`）の件数を、0件でも常に出力し、降格した項目は解決済みではないことを
  明記するようになった。判定不能ケースの案内も、存在しない `impl-status` の自動付与を指すのをやめ、
  「列挙 → 実装の実態を確認 → 自分で記入」の手順を説明する。また、デフォルト実行でも `--full` でも
  `adr/` と実装の乖離は検出されない（`--full` は spec ↔ adr の文書整合のみ）ため、レポートに
  `adr ↔ Implementation: Not checked` と手動確認手順を出し、スキル側にも既知の制約として明記した
- **`/check-spec --full` が、約束していた spec ↔ adr レビューを実際に行うようになった** - このモードは
  「各 spec を対応する決定ログと比較する」と説明されていたが、どの spec にどのログが対応するかを解決する
  処理が無く、委譲先のレビュー観点も定義されておらず、英語の出力テンプレートには結果欄そのものが
  無かった（日本語版にのみ行があった）。`/check-spec` は spec ごとに決定ログを解決するようになった —
  spec の `specification/` 配下での位置を `adr/` に写した名前一致（`adr/{feature}.md` と旧形式の
  `adr/{feature}-decisions.md`）、それが無い場合は front matter の `depends-on` がその spec を指す `adr`
  ドキュメント。`directories.adr` のカスタム名も尊重し、解決したパスを `spec-reviewer` に渡す。
  レビュー観点は、spec が記述する振る舞いの背後にある決定が記録されているか、現行の決定（後続エントリに
  覆されていない最新エントリ）が spec と一致するか、spec が覆された決定に依拠していないか、エントリが
  参照する spec 要素が現存するか、エントリが必須項目を備えているか、用語が一貫しているか。矛盾の修正は
  spec の修正か、`Supersedes` リンク付きの新規エントリの追記のいずれかで、記録済みエントリの編集や
  ファイルレベル front matter フィールドの利用は行わない。決定ログを解決できなかった機能は
  **該当なし**として報告し、整合とは報告しない。`adr/` ディレクトリが存在しないプロジェクトはエラーでも
  警告でもない。これはドキュメント同士のレビューであり、`adr/` と実装の乖離は対象外（上記の制約のとおり）
- **`recommend-front-matter` が設計ドラフトに正しい id を推奨するようになった** - id 生成に design の
  例外が無かったため、`task/{ticket-number}/design-draft.md` にはどの相互参照も解決できない feature
  スコープの id が付いていた。`design-{ticket-number}` になった（機能名を含めず、チケットディレクトリを
  階層の親として扱わない）。v4.x の `specification/*_design.md` は従来の feature スコープ形を維持する。
  task / 実装ログの `depends-on` 推論は同一 `task/{ticket-number}/` のドラフトを第一候補とし、無ければ
  v4.x の設計書にフォールバックし、どちらも無いことを正常な結果として扱う。欠落していた
  `adr` -> `spec` の推論手順も追加した
- **`sdd-init` の Migration Support が、実際には行わない作業を説明しなくなった** - 「再実行すると
  `${SDD_ROOT}/AI-SDD-PRINCIPLES.md` が無ければ生成する」と主張していたが、このファイル（および
  `.claude/rules/ai-sdd-instructions.md`）は SessionStart フックの責務であり毎セッション再同期され、
  スクリプトは一切触らない。さらに移行が必要かどうかの判定条件もそのファイルの不在としており、フックが
  常に作るため成立しない状態だった。判定条件を `ADR_TEMPLATE.md` の不在（`adr/` ドキュメントモデル導入
  前の初期化）に変更し、テンプレート一覧を4件に更新し、v4.x プロジェクトを v5 のドキュメントモデルへ
  移行する手順の節を新設した
- **`/constitution sync` に、同期対象として挙げている ADR テンプレートの手順が加わった** -
  `ADR_TEMPLATE.md` は `CONSTITUTION.md` と同期するファイルの一覧に載っていたが、その下の手順は spec /
  design テンプレートからタスクテンプレートへ飛んでおり、名前を挙げただけで一度も触られていなかった。
  手順にこの項目を追加した: エントリ形式への原則参照の追加と用語の同期を行い、必須エントリ項目
  （Decision / Rationale / Rejected alternatives）はスキルが機械的に読むため維持し、sync が触るのは
  テンプレートのみで、`${SDD_ADR_PATH}/{feature-name}.md` に記録済みのエントリは追記専用のため
  書き換えない
- **生成される `.claude/rules/ai-sdd-instructions.md` のディレクトリ図に `ADR_TEMPLATE.md` が載った** -
  フラット図・階層図のいずれも PRD / spec / design のテンプレートは挙げているのに、`/sdd-init` がその隣に
  作る決定ログのテンプレートだけが欠けていた。このファイルは SessionStart フックが毎セッション各
  プロジェクトへ再同期し、`.sdd/` 配下の作業では常にロードされるため、実際の初期化結果と食い違う
  `${SDD_ROOT}/` を提示していた
- **`checklist` の spec 表が、自身の命名注記と矛盾しなくなった** - 表は `{feature-name}_spec.md`
  （階層構造の親は `index_spec.md`）を required としていたが、その下の注記は `specification/` 配下では
  サフィックスが任意だと述べていた。どちらの形式でも required 行を満たすようになった
- **`/constitution validate` がサフィックス無しの spec を取りこぼさなくなった** - 事前スキャンが
  `specification/**/*_spec.md` を glob していたが、本リリースで同ディレクトリの `_spec` は任意になったため、
  `{feature-name}.md` という名前の spec がスキャン対象から漏れ、原則準拠の検証が黙って行われていなかった。
  `specification/` 配下の `.md` から v4.x の `*_design.md`（従来どおり別リストに載る）を除いた全件を
  スキャンするようになった
- **憲章テンプレートが永続設計書を必須と書かなくなった** - 配布される `CONSTITUTION.md` テンプレート
  （および `/constitution` の例・レポートテンプレート）が、すべての実装に `specification/*_design.md` を
  要求していた（本リリースで永続ドキュメントではなくなった文書）。該当行を v5 のドキュメント構成
  （抽象仕様書（サフィックス任意）・チケットの一時 `task/{ticket-number}/design-draft.md`・確定した決定の
  `adr/{feature-name}.md`）に更新した
- **PRD テンプレート・実装ログ・vibe-detector レポートに残っていた v4 世代のドキュメント表** - PRD
  テンプレートのドキュメント比較表、実装ログの「統合内容」節、`vibe-detector` の仕様書ステータス表が
  いずれも `xxx_design.md` を永続の技術ドキュメントとして説明し続けていたため、それを読んだプロジェクトは
  ワークフローが保持しないファイルに決定を書き続けることになっていた。spec / design-draft / 決定ログの
  3分割を示すようにし、実装ログの統合チェックリストは各項目を対応する `adr/` エントリの項目
  （Decision / Rationale / Rejected alternatives）に向けるようにした
- **出力テンプレートが存在しないコマンド名を提示しなくなった** - `task-breakdown`・`clarify`・
  `check-spec`・`implement`・`constitution`・`vibe-detector` のテンプレートや例が、`/check_spec`・
  `/generate_spec`・`/task_cleanup` というアンダースコア表記（v4 でハイフンへ改名されて以降は
  有効なコマンド名ではない）の実行を案内し続けていた。実在するコマンド名（`/check-spec`・
  `/generate-spec`・`/task-cleanup`）を提示するようになった
- **`sdd-init` の「このコマンドが行うこと」が `CONSTITUTION.md` を作ると主張しなくなった** -
  項目2が「`${SDD_ROOT}/CONSTITUTION.md` が無ければ作成する」と書いており、同ファイル内の後続3箇所と、
  意図的にコピー対象外にしている `init-structure.py` に矛盾していた。不足を報告して
  `/constitution init` を案内する内容に修正した
- **`run-checklist` が、チェックリスト不在時に「何も検証していない」まま報告しなくなった** -
  Error Handling はテスト失敗とツール不在のみを扱い、チェックリスト自体が見つからない場合の規定が無かった。
  解決したパス、チケットの解決経路（引数か機能名由来か）、および2つの対処（チケット番号付きで再実行する／
  `/checklist` で生成する）を報告するようになり、読み込めていないチェックリストに対する検証結果は
  報告しない
- **PRDレベルの要求ID形式が、ハードコードではなく `id_conventions` から解決されるようになった** -
  `analyze-requirements`・`prd-reviewer`・`generate-requirements-diagram` がハイフン表記
  （`UR-xxx` / `FR-xxx` / `NFR-xxx`）をハードコードしていた一方、同梱のPRDテンプレートと
  パイプラインの他の部分は既に `UR_001` / `FR_001` を生成していた。そのため
  `.sdd-config.json` に `id_conventions` を設定していても該当3件では無視され、既定設定の
  プロジェクトでも要求分析が出すIDが自身のPRDテンプレートが書くIDと一致しなかった。
  3件とも `shared/references/id_conventions_config.md` § PRD-Level ID Format Resolution に従って
  形式を解決し、未設定時は `UR_xxx` / `FR_xxx` / `NFR_xxx` にフォールバックするようになったため、
  設定した規約が端から端まで尊重される
- **`check-spec` が、唯一の設計ドラフトが実は別チケットのものだった場合に誤って添付しなくなった** -
  `find-spec-docs.py` の sole-draft フォールバックは、ディスク上に唯一存在するドラフトを、その
  `depends-on` front matter が明確に別の仕様を指している場合でも採用してしまっていた（これは
  「たまたま1件しかない無タグのドラフト」ではなく「別機能に属するという積極的な証拠」）。
  該当ドラフトは sole-draft の例外から除外され、`unscoped`（または残った無タグのドラフトがあれば
  そちらへのフォールバック）になるようにした
- **`check-spec` / `constitution validate` が、`api_design.md` のようなspecをv4.x永続design docと
  誤判定しなくなった** - `specification/` 配下では `_spec` 接尾辞が任意化されているため、`_design` で
  終わる正規のspec名が新設される可能性があるが、ファイル名だけのヒューリスティックはこれを区別できず、
  両コマンドの出力から黙って除外していた。front matter の `type` フィールドが宣言されている場合は
  そちらをヒューリスティックより優先するようにした
- **`post-tool-use.py` のspec同期リマインダが、globメタ文字を含むソースファイル名でも文字通りに
  マッチするようになった** - `find_spec_doc` / `find_legacy_design_doc` がファイルの語幹を未エスケープ
  のまま `rglob` パターンに埋め込んでいたため、`parse[v2].py` のようなファイルは `[v2]` がワイルドカード
  の文字クラスとして解釈され、実在するspecへのリマインダが出なくなっていた。同じ修正を`check-spec`の
  CLIターゲット引数（部分一致フォールバック）にも適用した
- **`run-checklist` の検証スクリプトが、対象カテゴリの候補ツールが全て未インストールの場合に
  `SKIPPED` を返さなくなった** - SKILL.md がこのケース用に定義済みの `TOOL_NOT_FOUND` を正しく返す
  ようにした（`SKIPPED` は「このカテゴリにコマンドが定義されていない」「ツールは実行されたが検証対象が
  無かった」の2ケース専用として残す）
- **`run-checklist` の検証スクリプトが、非UTF-8のツール出力デコードで未捕捉のクラッシュを起こす
  リスクをなくした** - `subprocess.run` のデコードをロケール既定から `errors="replace"` に変更した。
  従来はロケールが非UTF-8（`LANG=C` のCIコンテナ等）の場合に `UnicodeDecodeError` が発生し、
  スキルが期待するJSON結果を返さずスクリプトが異常終了することがあった
- **`evaluate-skills` の安全ガード監査が、あるキーワードの最初の出現が否定文脈だった場合に、
  それ以降の本物の違反を検査しなくなる問題を修正した** - `audit_run_artifacts.py` は各キーワードの
  最初の出現位置だけを見ており、それが否定文脈（「...確認をスキップしてはならない...」）に該当すると、
  同一キーワードの後続の本物の違反を検査していなかった
- **`evaluate-skills` のskill-creatorパス解決が、キャッシュが一度も存在しない場合に無言で異常終了
  しなくなった** - `set -euo pipefail` の下で、存在しないキャッシュディレクトリへの `find` が
  「未インストール」という親切なエラーメッセージより先にスクリプトを終了させていた。また、複数バージョンが
  キャッシュされている場合に誤った「最新版」を選んでしまう問題も修正した——キャッシュディレクトリ名は
  ソート可能なバージョン番号ではなくインストール時のハッシュのため、辞書順ソートには順序としての意味が
  無く、代わりに更新日時（mtime）で最新を判定するようにした

### Changed

#### Naming

- **`specification/`・`adr/` の `_spec`/`_design`/`-decisions` サフィックスが任意になった** - いずれも
  単一種別ディレクトリ（配下は抽象仕様書のみ／決定ログのみ）であるため、命名規則強制フックはこれらの
  ディレクトリでサフィックスを必須としなくなった。既存のサフィックス付きファイルは引き続き有効。
  `requirement/` は変更なし（`_spec`/`_design` サフィックスは引き続き禁止）
- **生成スキルが新規ADRファイルのデフォルトを `adr/{feature}.md`（`-decisions` サフィックス無し）に統一** -
  `task-cleanup`・`generate-spec`・`render-adr-review`・`doc-consistency-checker`・`sdd-init`・
  `implement`・共有の `document_dependencies.md` の参照例が、新規決定ログ作成時のデフォルトとして
  サフィックス無しのファイル名を示すようになった。既存の `-decisions.md` ファイルは引き続き有効で、
  そのまま検出・編集される。`naming.py` のバリデーションに変更はない

#### Hooks

- **編集後リマインダの参照先が技術設計書から spec に変更** - ソースファイル編集後、`PostToolUse` フックは
  `specification/` 配下の対応する spec（`{stem}_spec.md` → `{stem}.md` の順）を探索し、spec の同期を促す
  ようになった。従来は `{stem}_design.md` を探索していたため、永続ドキュメントとして存在しなくなった
  v5.0.0 ではリマインダが発火しなかった。`.sdd/` ドキュメント編集時のリマインダも PRD ↔ spec ↔ adr を
  参照するようになった
- **v4.x の設計書しか持たない機能でもリマインダが出るようになった** - 探索先を spec に移した結果、
  `specification/{stem}_design.md` しかドキュメントが無い機能のソースを編集しても何も出力されず、
  そうしたプロジェクトが従来受け取っていたリマインダが黙って消えていた。このケースには専用の文言を
  出すようになった: 設計書は有効な補助入力として読むこと、その決定は `adr/{feature-name}.md` に
  属すること、移行が済むまで削除しないこと。手順の在り処は「プラグインの README を参照」ではなく、
  実際に開けるパスとして示す — `<plugin root>/README.md` の「Migration from v4.x」配下の
  「Extracting Existing `*_design.md` Files into `adr/`」節。spec が
  存在する場合は従来と同一の spec 同期リマインダを使い、出力されるメッセージは常に1件のみ
- **`adr/` 配下の編集にもリマインダが出るようになった** - 決定ログを編集しても従来は何も出力されなかった。
  追記専用（過去エントリを書き換えない）であることと、仕様を変える決定は spec に反映する必要があることを
  促すようになった

#### Skills

- **下流スキルが技術設計書を `task/{ticket-number}/design-draft.md` から読むようになった** -
  `task-breakdown`・`implement`・`checklist`・`clarify` が、`/generate-spec` が生成しなくなった旧
  `specification/{feature}_design.md` を参照し続けていた。そのため `/generate-spec` →
  `/task-breakdown` → `/implement` と順に辿るとデッドロックし、下流スキルが必須とする設計書が
  永久に作られない状態だった。4スキルすべてがチケット単位の固定パスを参照するようになり、この
  パスは抽象仕様書のフラット／階層構造とは独立している
- **`checklist`・`clarify` は設計ドラフトを任意入力として扱うようになった** - 設計ドラフトは実装完了時に
  削除されるため、不在でもこれらのスキルは停止せず、抽象仕様書（および存在する場合は PRD・`tasks.md`）
  のみで続行する。`clarify` は設計ドラフトの位置を特定するための任意引数 `ticket-number` を受け取る。
  ドラフトが無く、v4.x の `specification/{feature-name}_design.md`（階層構造の親は `index_design.md`）が
  残っているプロジェクトでは、設計レベルの質問と設計レビュー項目をその設計書から導出する（省略ではなく）
- **`task-breakdown`・`implement` の `depends-on` がチケット単位の design ID になった** - 設計ドラフト
  自身の `id` は `design-{ticket-number}` であるのに、指示は `design-{feature-name}` のままで、
  `front-matter-reviewer` の cross-reference 検査が必ず失敗していた。両スキルが
  `["design-{ticket-number}"]` を指示するようになり、`shared/references/front_matter_reference.md` の
  `type: "design"` スキーマも同じ形式に修正した
- **`implement` が `_spec` サフィックス有無の両方の抽象仕様書を受け付けるようになった** -
  `specification/` 配下でサフィックスが任意になったにもかかわらず前提条件チェックは
  `{feature}_spec.md` のみを要求していた。`{feature}.md` / `{feature}_spec.md` のいずれでも満たせる
- **`/plan-refactor` が決定を `adr/` へ引き継ぐ導線を提示** - 完了出力で `/task-cleanup` を案内し、設計ドラフト
  （およびそこに含まれるリファクタリング計画）が削除される前に、確定した決定を `adr/{feature-name}.md` へ
  追記するよう促す。本スキル自身は `adr/` に書き込まない — 計画は提案であり、追記専用ログに載せるのは
  確定した決定のみとするため
- **`doc-consistency-checker` の PRD 更新推奨の導線が `/generate-prd --amend` を案内するようになった** -
  spec の変更が PRD の要求と矛盾し、人間が PRD 更新を選んだ場合、従来は手段を指定していなかったが、
  `/generate-prd --amend` を案内するようになった
- **チケット番号を取るすべてのスキルで `--ticket <番号>` と `--ticket=<番号>` のどちらでも渡せる** -
  スキルごとに一方の
  書式しか記載していなかったため、あるスキルで覚えた書き方が他のスキルに通じなかった。
  チケット番号を受け取る10スキル — `/generate-spec`・`/plan-refactor`・`/task-breakdown`・`/implement`・
  `/checklist`・`/run-checklist`・`/clarify`・`/task-cleanup`・`/check-spec`・`/render-adr-review` —
  のすべてが両書式を同義として受理することを明記し、番号が位置引数のスキルではフラグ形式が位置引数の
  スロットを消費しないことも明記した。とくに `/render-adr-review` は、位置に捕まったフラグを値として
  扱わなくなり、`/render-adr-review adr/x.md --ticket=123` の出力ファイル名が
  `--ticket=123-review.html` になることが無くなった。`/generate-spec` の `argument-hint` にも、従来は補完に出て
  いなかった `--ticket`・`--ci`・`--amend` を列挙した。`--ci` モードでチケット番号が欠けている場合は、
  読み書きを一切行う前に停止し、欠落している引数と修正した実行例を提示する（プレースホルダの番号や
  `task/unknown/` ディレクトリを勝手に作らない）
- **チケット番号を省略できるスキルが、解決したパスを明示するようになった** - `/implement`・
  `/checklist`・`/run-checklist`・`/clarify`・`/task-cleanup` は機能名（または `task/` 全体）に
  フォールバックするため、読み書き先が黙って変わる。各スキルが解決したパスを出力に明示し、そこに
  何も無い場合はそのパス・チケット番号の省略が原因である可能性・2つの対処を報告するようになった
  （他の task ディレクトリを探し回ったり、必要なドキュメント無しで作業を始めたりしない）。`/clarify`
  は PRD・spec・および v4.x の設計書のみで分析したことも明示するため、設計関連の質問カバレッジが
  下がっていることが見える
- **`recommend-front-matter` は `impl-status` が欠けている spec を列挙し、このフィールドを書き込まない** -
  `--apply` は従来、front matter を既に持つ spec に `impl-status: "not-implemented"` を追記し、front
  matter が無いドキュメントに書き込むブロックにもこれを含めていた。この値は実装についての主張であり、
  このスキルは実装を確認しない。さらに実装済みの spec に `not-implemented` を刻むと、`/check-spec` の
  退行検知（Critical）が「意図した先行」（Info）に変わってしまう — このフィールドが検出するために存在する
  まさにその失敗である。front matter を既に持つドキュメントは一切変更せず、書き込むブロックからも
  `impl-status` を外し、フィールドが欠けている spec を列挙するだけにした。実装の実態を確認して
  `implemented` / `in-progress` / `not-implemented` を自分で記入する運用になる。承認ダイアログの件数も
  「front matter が無いドキュメント」のみになった
- **`task-cleanup` の決定ログ追記が確定したエントリ形式に従うようになった** - 指示は「末尾に追記する」
  「既存エントリの構造に合わせる」程度で、見出しの形も項目名も運任せだった。決定1件 = `## YYYY-MM-DD
  {decision title}` エントリ1件とし、Decision / Rationale / Rejected alternatives（該当が無ければ
  `None considered`。捏造は禁止）を必須、同一ファイル内の過去エントリへの `Supersedes` リンクを任意と
  した。既存エントリの書き換え・並べ替え・削除は禁止、覆された側のエントリは一切編集せず、覆しを
  ファイルレベルの `supersedes` / `superseded-by` front matter フィールドに書いてはならない
- **`task-cleanup` が削除する技術知見の退避先を示すようになった** - 実装のコツ・トラブルシューティング
  メモ・パフォーマンス知見は、退避先が定義されないまま「削除可能」と分類されていたため単に失われていた。
  知見は決定ではないので `adr/` のエントリにはならない（決定の Rationale の一部としてなら入る）。
  削除する各項目について退避先 — コードコメント／振る舞いを固定するテスト／`*_spec.md` — を必須とし、
  どこへ退避したかを報告するようになった
- **`/plan-refactor` の技術的負債の観察に永続的な退避先が定義された** - 従来は設計ドラフトに書かれるだけで、
  ドラフトとともに失われていた。各観察に3つの退避先のいずれかを割り当てるようになった: 今回のリファクタで
  解消する負債は `/task-cleanup` が追記する `adr/` エントリの Rationale へ、意識的に見送る負債は
  トラッカー item（その id を計画に記録。見送り自体が決定である場合は cleanup で独自エントリにもなる）へ、
  実装が spec の記述と矛盾している負債は人間が承認する `*_spec.md` の修正提案へ。負債用の新規ドキュメントは
  作らない（v5 に常設の負債台帳は無く、`adr/` は決定の記録である）。完了出力には退避先が未定の観察を
  列挙する
- **`/plan-refactor` が、逆生成した分析のうちどこまでがチケットを越えて残るかを明示するようになった** -
  Case B では既存実装の棚卸し結果を設計ドラフトに書き出すが、ドラフトはクリーンアップで削除されるため、
  棚卸しのどの項目が永続ドキュメントに到達すべきなのかがどこにも書かれておらず、結果として毎チケット
  丸ごと失われていた。境界を明文化し、逆生成テンプレート側に永続する項目の置き場所を用意した:
  外部から観測できるデータフローは逆生成 spec の新設「振る舞いとデータフロー」節へ、他のコードが依存する
  モジュール境界は同 spec の「内部インターフェース」節へ（契約のみ。背後のファイル構成は書かない）、
  アーキテクチャのパターン名は同 spec の実装ノートへ。一方、コンポーネント内訳・ディレクトリ構成・
  コンポーネント間依存・内部の呼び出し順序・主要アルゴリズムの解説・状態管理の内部・テストカバレッジの
  数値は**意図的に永続させない**（コードから再導出でき、ドキュメント側の複製は必ずずれていくため。
  spec テンプレート自身もこれらを除外している）。Case B の完了出力は、spec に引き継いだ項目と意図的に
  破棄した項目をそれぞれ提示するようになった。`/task-cleanup` も同じ理由で同種の構造記述を削除可能に
  分類し、退避先を求めない — ただし構造に関する*決定*は従来どおり `adr/` エントリとして残る

#### Documentation

- **`AI-SDD-PRINCIPLES.md`** - Consistency Checking 表に恒久的な実装チェックとして `spec ↔ Implementation`
  行を追加し、`design ↔ Implementation` を「設計ドラフトが存在する実装中のみ有効」と位置づけ直した。
  `adr/` ディレクトリと `design-draft.md` のライフサイクルを明文化し、
  `requirement/`（PRD）は spec/design/実装側の変更から自動更新されないこと — 矛盾は人間の判断に委ね、
  無断で書き戻さないことを明記した
- **`shared/references/document_dependencies.md`** - `adr/` モデルに整合するよう更新（それまで
  `specification/*_design.md` を永続扱いとする旧記述のまま、再設計に追随していなかった）
- **`check-spec` の front-matter-reviewer への委任が、実行できなかった場合に明示するようになった** -
  従来はエージェント委任ができない実行環境では front matter 検証が黙ってスキップされ、それでも
  チェック完了として報告されていた。今後はその旨を明示し、人間による手動レビュー項目として一覧化する
- **`generate-prd` の prd-reviewer / front-matter-reviewer への委任も同様の明示的フォールバックを持つ** -
  上記と同じ修正を両方の呼び出し箇所（新規生成・`--amend`）に適用した
- **`checklist` の各項目が根拠を開示するようになった** - 各項目がどの文書のどの記述から導出されたかを
  明記し、文書からの引用ではなく実装コンポーネントの存在から推論した場合は
  `synthesized from: {コンポーネント名}` と記載する。これにより「抽出」と「創作」をレビュアーが
  区別できる
- **`clarify` が9カテゴリすべてについて Clear/Partial/Missing の分類を記録するようになった** -
  質問化しなかったカテゴリも含め、分析が実際にどこまで網羅されたかが出力から見えるようになった
- **`generate-requirements-diagram` が、網羅性と10〜15要求の可読性ガイドラインが衝突する場合の
  優先順位を明示するようになった** - 網羅性が優先され、まずサブシステム別の図分割を検討する。
  分割が適用できない場合のみサブ要求を1つの注記付きノードへ圧縮してよいが、どのサブ要求を
  なぜ圧縮したかを明示しなければならない
- **`clarify` が、NFR/制約を曖昧と判定する前に実装コードを確認するようになった** - 対象機能の
  `impl-status` が `implemented` の場合、未定義に見える閾値やタイムアウトが実は実装コード側にのみ
  記録された決定済みの値（`TIMEOUT_SECONDS` 定数など）である場合がある。仕様書の記述だけで
  「未定義」と判断する前に、実装済みの値を確認するようにした
- **`generate-requirements-diagram` が、要求図節の欠落を対象文書への直接編集で補わなくなった** -
  「テキストのみ返す」契約に、節が欠落している場合でも `Write`/`Edit` で「親切に」補ってはならない
  ことを明記した。要求図は常にテキストとして返し、書き込むかどうかの判断は呼び出し元に委ねる
- **`checklist` が全カテゴリの全項目に優先度付与を必須化した** - 標準9カテゴリ以外の自作カテゴリ
  （原則適合カテゴリ等）を含む。加えて優先度体系の出所明示が、テンプレートの定型文の丸写しではなく
  SKILL.md本文とテンプレートの実際の比較記録を要求するようになった
- **`check-spec` がNFRもFRと同様に個別に実装と突き合わせるようになった** - NFRについて結論部の
  一文で済ませる報告はこの突き合わせ要件を満たさなくなった。重大度分類にも、重大度は検出確度ではなく
  実質的な影響（公開インターフェース・観測可能な振る舞い・データモデルへの影響か、内部詳細のみか）に
  基づくことを明記した
- **`task-cleanup` のADRエントリ形式の指示が、`AI-SDD-PRINCIPLES.md` に既に定義済みの全項目テーブルを
  丸ごと再掲しなくなった** - そのテーブルを正典として参照するようになり、cleanup固有の補足（見出しの
  日付の取得元、「None considered」の文言）だけをローカルに残した。これにより2つのコピーが黙って
  食い違うことがなくなる
- **`PreToolUse` フックが `.sdd-config.json` をツール呼び出しごとに1回だけ読み込むようになった
  （従来は2回）** - パス解決とnaming除外パターンの参照が、それぞれ独立してファイルをopen・parseして
  いた
- **`PostToolUse` フックのspec同期リマインダが、ソースファイル1件の編集ごとに `specification/` を
  1回だけ走査するようになった（従来は最大3回）** - `find_spec_doc` の2つの接尾辞候補と、別途行われて
  いた `find_legacy_design_doc` へのフォールバックを、1回のディレクトリ一覧取得から解決するようにした

## [4.1.0] - 2026-08-19

### Added

#### Configuration

- **`.sdd-config.json` に `naming.ignore_patterns` を追加** - `"*_test.md"` のような glob パターンをファイル名
  （basename）に照合し、一致したファイルを `requirement`/`specification` の命名規則チェックから除外できるように
  なった。テスト用ファイル等、意図的に規則外の命名をしたい場合にブロックされなくなる

## [4.0.1] - 2026-07-28

### Changed

#### Permissions

- **書き込みを無制限に事前承認しないようにした** - スキルの `allowed-tools` は「*確認を尋ねずに*
  使えるツール」を与えるもので、制限ではなく事前承認である。11スキルがベアな `Write` / `Edit` を
  列挙しており、任意のパスへの書き込みが無確認で通る状態だった。書き込み先を `Edit(<path>)` 形式で
  限定し、`Edit(.sdd/**)` を基本に、必要なスキルにのみ `Edit(CLAUDE.md)` /
  `Edit(.sdd-config.json)` / `Edit(.claude/rules/**)` を与えた。範囲外への書き込みは確認が入る。
  なお `Write(<path>)` は有効な形式ではなく、`Edit(<path>)` が全ファイル編集ツールをカバーする
- **シェル実行を同梱スクリプトに限定した** - 10スキルがベアな `Bash` を列挙し、任意のコマンドが
  無確認で通る状態だった。同梱ヘルパーのみを実行する7スキルは対象を明示する形にした。例:
  `Bash(python3 "${CLAUDE_PLUGIN_ROOT}/skills/check-spec/scripts/find-design-docs.py" *)`
- **3スキルから `Bash` を外した** - `implement` と `run-checklist` はプロジェクトの任意のテスト・
  リンター・スキャナを実行し、`task-cleanup` は `git rm` / `git rm -r` を実行する。いずれも
  事前承認すべきではないため、コマンド実行前に確認が入るようにした
- `.sdd-config.json` でカスタム `root` を設定しているプロジェクトでは書き込み時に確認が入る。
  `${SDD_ROOT}` は `allowed-tools` では展開されないため。カスタム root を事前承認する設定例は
  README を参照

#### Plugin Layout

- **エージェントのサポートファイルを `agents/` 外へ移動** - `agents/references/`・`agents/examples/`・
  `agents/templates/{en,ja}/` を `shared/` 配下（`shared/references/`・`shared/examples/`・
  `shared/templates/{en,ja}/`）に移し、`agents/` にはエージェント定義6件のみを残した。
  `claude plugin validate --strict` は `agents/**` を再帰走査してマニフェストの `agents` 配列を無視するため、
  そこに置かれたサポートファイルはすべて「front matter の無いエージェント」として報告されていた
- **エージェントの参照パスを絶対パス化** - エージェントプロンプト内の参照資料・利用例・テンプレートへの
  33箇所を、ベアな相対パスから `${CLAUDE_PLUGIN_ROOT}/shared/...` 形式に変更した。従来の形式は
  エージェント定義ファイルからの相対解決に依存していたが、このプレースホルダは agent content の
  どこでも展開されるため参照先が一意に定まる
- `agents/references/` にあった `shared/references/` を指す symlink 5本を削除。エージェントは
  実ファイルを直接参照する

### Fixed

#### Agents

- **ツール制限が効いていなかった** - 6つのエージェントすべてが許可ツールを `allowed-tools:` で宣言していたが、
  これはスキル専用の front matter キーである。サブエージェントが解釈するのは `tools:` / `disallowedTools:` の
  ため宣言は警告なく無視され、全エージェントが `Write` / `Edit` / `Bash` を含む**すべてのツール**を継承していた。
  キーを `tools:` に修正し、意図していた読み取り専用の範囲（`Read`, `Glob`, `Grep`, `AskUserQuestion`）を回復した

#### Skills

- **モデル指定が効いていなかった** - 8つのスキルが `agent: sonnet` / `agent: haiku` でモデルを指定していた。
  `agent` フィールドは*サブエージェント型名*の指定で `context: fork` 設定時のみ有効なため、モデル名を書いても
  警告なく無視され `general-purpose` にフォールバックしていた。fork の有無に関わらず有効な `model:`
  フィールドに変更した

#### Hooks

- **インストールパスに空白があるとフックが起動しなかった** - 4つのフックコマンドすべてで
  `${CLAUDE_PLUGIN_ROOT}` が未クォートだったため、パスが単語分割され（`$HOME` に空白を含む環境などで）
  全フックが起動に失敗していた。変数をクォートした
- **matcher の陳腐化したツール名** - `PreToolUse` / `PostToolUse` の matcher が `Write|Edit|MultiEdit`
  だったが、`MultiEdit` は現在の Claude Code のツールではない。`Write|Edit` に絞った

#### Plugin Manifest

- **フックの二重ロード** - `plugin.json` から `"hooks": "./hooks/hooks.json"` の宣言を削除。Claude Code は
  プラグインルート直下の `hooks/hooks.json` を自動検出し、manifest のパスは既定パスを上書きせず補完するため、
  標準パスを明示すると同一ファイルが二重にロードされ、プラグイン読み込み時に `Duplicate hooks file detected`
  エラーが表示されていた。フック自体の動作は変わらない
- **冗長な skills 宣言** - `"skills": "./skills"` を削除。既定の `skills/` ディレクトリは常に走査され、
  `skills` フィールドはその走査に*加算*するだけなので、標準パスの宣言は無意味だった。19スキルはすべて
  引き続き読み込まれる

#### Documentation

- **日本語 README が英語版と乖離していた** - `README.ja.md` はエージェントを5件（実際は6件）、フックを1件
  （実際は4件）と記載し、`SDD_LANG` と `.sdd-config.json` の `lang` のデフォルトを `ja`（実際は `en`）と
  記述し、`scripts/` 配下10ファイルのうち1件しか載せていなかった。両 README を同期した

## [4.0.0] - 2026-07-16

### Added

#### Agents

- **`cross-prd-reviewer`** - 複数 PRD 間の整合性をレビューする新規エージェント
    - カテゴリ境界の整合（スコープ外の相互参照）、用語集間の用語統一、構成・記法スタイルの一貫性、
      CONSTITUTION.md 原則参照カバレッジ、front matter の付け方の整合を検査
    - 指摘は [must]/[recommend]/[nits] で分類。単一 PRD の品質レビューは従来どおり prd-reviewer が担当
    - 出力テンプレート `templates/{en,ja}/cross_prd_review_output.md` を追加

#### Configuration

- **`.sdd-config.json` の `index`** - セッション開始時に構築される `.sdd` ドキュメント圧縮インデックスを
  制御する真偽値の設定を追加。トークン消費を削減する
    - **デフォルトで有効**（`true`）。`"index": false` で無効化できる
    - 自動生成される `.sdd-config.json` にも発見性向上のため `"index": true` を明示的に含める
    - **インデックス抽出の拡充** - インデックスが SysML 要求図とデータモデルのフィールドまでカバー
      するようになり、従来は生 Read が必要だった SysML trace 軸もトークン削減インデックスの対象になった

### Changed

#### Configuration

- **`.sdd-config.json` の `index`** - 値の形式を**真偽値専用**（`true`/`false`）に統一。従来の文字列形式
  （`"on"`/`"off"`）は非対応となった。真偽値以外の値は警告を出して既定（on）にフォールバックする
    - デフォルトを **off から on** に変更。トークン削減インデックスが標準で構築される

#### Hooks

- **`PreToolUse`** - Write/Edit 対象が実装コードの場合に `.sdd/CONSTITUTION.md` の原則を
  `additionalContext` として注入
    - コンテキスト肥大化を防ぐため、注入はプロジェクト内のソースファイル編集に限定し、
      セッションごとに最大1回、3000文字で切り詰めて注入する
    - CONSTITUTION.md が存在しない場合は何も注入しない

#### Agents

- **`front-matter-reviewer`** - `model` を `sonnet` から `haiku` に変更
    - ルールベースのフォーマット検証は複雑な推論を必要としないため、軽量モデルによりコストとレイテンシを削減
    - 他のエージェント（prd-reviewer, spec-reviewer, requirement-analyzer, clarification-assistant）は
      ドキュメント横断の整合性推論が必要なため `sonnet` を維持

#### Skills

- **モデルティア** - 機械的・ルールベースのスキルのモデルを引き下げ、コストとレイテンシを削減
    - `generate-requirements-diagram` / `generate-usecase-diagram` - `agent` を `sonnet` から `haiku` に変更
    - `recommend-front-matter` / `run-checklist` / `sdd-init` / `task-cleanup` - `agent: haiku` を宣言
- **`sdd-init`** / **SessionStart フック** - 常時ロードされる `CLAUDE.md` から AI-SDD 詳細ガイドを
  パススコープ付きルール `.claude/rules/ai-sdd-instructions.md`（`.sdd/**` に触れたときのみロード）へ移行し、
  `.sdd/` 以外の作業時のコンテキスト消費を削減
    - `CLAUDE.md` には宣言・トリガー条件・ルールへのポインタのみを残し、約90行のディレクトリ構造・
      命名規則・リンク規約ブロックをルールファイルへ移動
    - ルールファイルは SessionStart フック（`session-start.py`）が自動生成・バージョン同期する。
      `/sdd-init`（`update-claude-md.sh`）は最小化された `CLAUDE.md` セクションのみを管理
    - ルールは `SDD_LANG` に関わらず英語の単一ファイル（人間向けではなく AI 向けガイダンス）とし、
      言語別ファイルが同時にロードされる問題を回避

#### Skills

- `arguments` frontmatter フィールドによる名前付きスキル引数を導入（Claude Code v2.1.199+）
    - 8スキル（`task-breakdown`, `implement`, `clarify`, `check-spec`, `checklist`, `run-checklist`,
      `task-cleanup`, `plan-refactor`）が `feature-name` / `ticket-number` を名前付き位置引数として宣言し、
      本文で `$name` 置換構文により参照するよう移行
    - 自由文入力のスキル（`generate-spec`, `generate-prd` 等）は従来どおり `$ARGUMENTS` 全体を解釈
    - 各スキル本文にフォールバックを明記: 値が空・未置換・位置的に捕捉されたフラグ（`--...`）の場合は
      引数文字列全体の解釈または対話的な確認にフォールバックし、v2.1.199 未満の挙動を維持

### Added

#### Hooks

- `hooks.json` を `SessionStart` 以外に拡張
    - **`UserPromptSubmit`** (`scripts/user-prompt-submit.py`) - ユーザープロンプト中の Vibe Coding 兆候
      （「いい感じに」等の曖昧な指示）を検知し、vibe-detector スタイルの明確化フローを促す追加コンテキストを注入
      （検知のみで、ブロックは行わない）
    - **`PreToolUse`** (`scripts/pre-tool-use.py`, matcher `Write|Edit|MultiEdit`) - `.sdd/` 配下への書き込み前に
      AI-SDD ファイル命名規則（requirement: サフィックスなし、specification: `_spec.md` / `_design.md` 必須）を
      検証し、違反する書き込みをブロック
    - **`PostToolUse`** (`scripts/post-tool-use.py`, matcher `Write|Edit|MultiEdit`) - ドキュメント更新漏れの
      可能性を検知: `.sdd/` ドキュメント編集後に整合性チェックの実行を促し、対応する `*_design.md` を持つ
      ソースファイル編集後に設計書の同期を促す

#### Agents

- **`requirement-analyzer`** - ID採番バリデーションを追加（`--validate-ids`、`--analyze` の一部としても実行）
    - 設定可能な正規表現パターン（`.sdd-config.json` の `id_conventions` セクション）による命名規約検証
    - ID順序の乱れに対する移動提案を含む昇順検証
    - 採番の欠番検出とリネーム後の旧ID残存検出
    - `requirement_analysis_output` テンプレート（en/ja）に「ID採番バリデーション」セクションを追加

#### Documentation

- **`AI-SDD-PRINCIPLES`** - `.sdd-config.json` のオプション `id_conventions` セクションを文書化

#### Skills

- **`check-spec`** (v3.1.0) - 整合性チェックをリテラル値まで拡張
    - 仕様書の「値域・閾値レジストリ」（Schema Registry）セクションが存在する場合はそれをパースし、ない場合は
      spec/design 本文からのリテラル値抽出にフォールバック
    - 実装側のリテラル値を設定ファイル、ORM の CHECK 制約、バリデーション制約（例: Pydantic）、
      言語固有の enum / 定数から抽出
    - spec / design / 実装間の値の乖離を検出し Warning として報告
      （例: spec `0.7` vs `config.py` `0.6`）
    - enum / CHECK 制約のメンバー集合の完全性と要求IDトレースの完全性（PRD <-> spec <-> design）を検証
    - 出力テンプレート（en/ja）に値乖離セクションを追加
- **`generate-spec`** - 設計書テンプレート（`templates/{en,ja}/design_template.md`）に「Pseudocode完全性ルール」セクションを追加
    - 設計書の擬似コードをそのままコピー可能に保つための言語別ガイダンス（Python 汎用 / Pydantic v2 / SQLAlchemy & alembic）
    - 追加言語（TypeScript / Go / Rust 等）向けに拡張可能なサブセクション構造

### Fixed

- **`.sdd-config.json` の `root`（およびディレクトリ名）のカスタム設定がプラグイン全体で尊重されるようになった。** 従来は多くのパスが既定の `.sdd/` にハードコードされており、カスタム root を使うプロジェクトで暗黙的に壊れていた。
    - `session-start.py` が生成するパススコープ付きルールの `paths:` グロブに設定 root を置換。カスタム root（例: `.ai-docs/`）配下でも `.claude/rules/ai-sdd-instructions.md` が自動ロードされる（グロブが `.sdd/**` 固定だったリグレッションも解消）
    - `update-claude-md.sh` が生成する `CLAUDE.md` セクションに設定 root を置換
    - skill/agent プロンプトと出力テンプレートは、リテラル `.sdd/...` ではなく `${SDD_ROOT}` / `${SDD_*_PATH}` で SDD パスを解決
    - `find-design-docs.sh` / `validate-files.sh` はキャッシュを設定 root 配下に出力。`pre-tool-use.py` の命名違反メッセージは設定ディレクトリパスを表示
- **`post-tool-use.py`** - `.sdd/requirement/` または `.sdd/specification/` 配下のファイル編集後に表示される
  advisory ヒントが、`doc-consistency-checker` スキルに加えて `/constitution validate` の実行も提案するよう
  になり、生成・編集後に CONSTITUTION.md の原則違反を検知しやすくなった
- **`doc-consistency-checker`** - `design ↔ 実装` チェック（旧 spec FR-004）を削除。`impl-spec-check`
  （`/check-spec`）と責務が重複しており、親 PRD が明示的にスコープ外と定義していた領域と矛盾していた。
  `design ↔ 実装` の整合性チェックは `/check-spec` に一本化される
- **生成成果物へのセクション必須度マーカー残留を防止** - 著者向けのセクション必須度マーカー
  （`<MUST>` / `<RECOMMENDED>` / `<OPTIONAL>`）が生成ドキュメントに残らないようにした。`generate-spec` は
  最終出力の見出しからこれらを除去し、`prd-reviewer` / `spec-reviewer` に残留マーカーを検出する
  「No Marker Residue」チェックを追加

## [3.3.0] - 2026-03-02

### Changed

#### Hooks

- **`session-start`** - `session-start.sh`（Bash）を `session-start.py`（Python 3.7+）に移行
    - Python 標準の `json` モジュールの使用により `jq` 依存を排除
    - `--default-lang` 引数により `sdd-workflow` と `sdd-workflow-ja` でスクリプトを統一
    - `sdd-workflow-ja/scripts/` は `sdd-workflow/scripts/` へのシンボリックリンクに変更（重複排除）
    - 不正な `.sdd-config.json` に対するエラーハンドリングを追加（デフォルト値への graceful fallback）
    - Python 3.7+ が必要（`dataclasses` と `subprocess.run(capture_output=True)` のため）

#### Documentation

- `sdd-workflow` プラグインの日本語 README として `README.ja.md` を追加
- 独立した `sdd-workflow-ja/README.md` を削除（現在は `sdd-workflow/README.ja.md` へのシンボリックリンク）
- ルート `README.md` に CI バッジとライセンスバッジを追加

## [3.2.1] - 2026-02-26

### Fixed

#### Hooks

- **`hooks.json`** - Claude Code Issue [#24529](https://github.com/anthropics/claude-code/issues/24529) のワークアラウンド
    - フック実行時に `CLAUDE_PLUGIN_ROOT` が環境変数として設定されない問題
    - フックコマンド内で `CLAUDE_PLUGIN_ROOT` を明示的に設定し、`session-start.sh` 内で利用可能に
    - 変更前: `source ${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh`
    - 変更後: `CLAUDE_PLUGIN_ROOT=${CLAUDE_PLUGIN_ROOT} source ${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh`

## [3.2.0] - 2026-02-25

### Added

#### Skills

- **`recommend-front-matter`** - 既存ドキュメントへの YAML front matter 追加を推奨する新スキル
    - すべての AI-SDD ドキュメント（PRD, spec, design, task）の front matter 有無をスキャン
    - 推定メタデータ（id, title, type, status, depends-on, tags, category）付きの推奨を生成
    - ユーザー確認後の `--apply` オプションによる自動適用をサポート
    - バイリンガルのレポートテンプレート（en/ja）を提供
    - ドキュメントスキャンスクリプト（`scan-documents.sh`）を同梱

#### Agents

- **`front-matter-reviewer`** - AI-SDD ドキュメントの YAML front matter を検証する新エージェント
    - フィールド形式、依存方向、ステータス値、種別固有フィールドをチェック
    - 相互参照の整合性と id の一意性を検証
    - ドキュメント生成後や整合性チェック時に使用

#### Shared References

- **`shared/references/`** - YAML front matter リファレンスドキュメントを追加
    - `front_matter_reference.md` - front matter フィールドの包括的リファレンス
    - `front_matter_prd.md` - PRD 固有の front matter ガイド
    - `front_matter_spec_design.md` - spec/design 固有の front matter ガイド
    - `front_matter_task.md` - タスク固有の front matter ガイド
    - `front_matter_impl.md` - 実装ログ固有の front matter ガイド

### Removed

#### Skills

- **`sdd-migrate`** - レガシーマイグレーションスキルを削除（v1.x → v2.0.0 ディレクトリ構造移行用）
    - 現在のユーザーにはマイグレーション機能が不要になったため
    - メンテナンスコストとコードの複雑さを削減

#### Hooks

- **`session-start.sh`** - レガシーディレクトリ構造の検出と自動マイグレーションロジックを削除
    - `.sdd-config.json` の生成をデフォルト値のみに簡素化
    - 29〜82行目（レガシー検出とマイグレーション警告）を削除

#### Documentation

- **`sdd-init/SKILL.md`** - v3.0.0 マイグレーション（`lang` フィールド追加）への参照を削除

## [3.1.1] - 2026-02-23

### Changed

#### Hooks

- **`session-start.sh`** - POSIX 互換性と堅牢性を改善
    - スクリプト冒頭に `CLAUDE_PLUGIN_ROOT` のガードチェックを追加
    - `&> /dev/null` を POSIX 互換の `>/dev/null 2>&1` に置換
    - echo 文から不要な `>&2` リダイレクトを削除
    - principles コピー時の `CLAUDE_PLUGIN_ROOT` 存在チェックを簡素化

#### Skills

- **`plan-refactor`** - テンプレート/リファレンスファイルのパス参照を snake_case に修正
    - `refactor-plan-section.md` → `refactor_plan_section.md`
    - `reverse-design-template.md` → `reverse_design_template.md`
    - `reverse-spec-template.md` → `reverse_spec_template.md`
    - `design-doc-integration.md` → `design_doc_integration.md`
    - `templates/` と `references/` の実ファイル名も一致するようにリネーム

## [3.1.0] - 2026-02-15

### Added

- **plan-refactor スキル** - 既存機能のリファクタリング計画を支援する新スキル
    - 現在の実装を分析し、リファクタリング計画を含む設計書を作成・更新
    - 2つのシナリオをサポート: ケースA（既存ドキュメントあり）とケースB（ドキュメントなし）
    - 日英両言語のテンプレート、サンプル、リファレンスドキュメントを提供
    - リファクタリングパターンのリファレンス（Extract Interface, Dependency Injection 等）を同梱
    - 実装ファイル検索スクリプト（`find-implementation-files.sh`）
    - 既存ドキュメントスキャンスクリプト（`scan-existing-docs.sh`）
- **エージェントのサンプルとリファレンスドキュメント** - 使いやすさを改善
    - `clarification-assistant`: 使用例と明確化ワークフローのリファレンスを追加
    - `prd-reviewer`: 使用例を追加
    - `requirement-analyzer`: 使用例を追加
    - `spec-reviewer`: 使用例を追加
    - 全エージェント向けに stop report フォーマットテンプレート（en/ja）を追加
    - ディレクトリ構造リファレンスと修正提案フローリファレンスを追加
- **SKILL.md の argument-hint** - 全スキルに `argument-hint` フィールドを追加し引数仕様を明確化

### Changed

- **/constitution init** - 非対話モード初期化用のコンテキスト引数を追加
    - `[context]` 引数を指定すると、対話なしでプロジェクトコンテキストに基づく原則を生成
    - 引数なしの場合は従来どおり対話モードで実行
- **エージェント設定ファイル** - コードブロック抽出精度を高めるため Markdown 形式を改善
    - clarification-assistant: 冗長な説明を削減しより簡潔な構造に（103行削減）
    - prd-reviewer: ワークフロー説明を整理
    - requirement-analyzer: 分析フロー説明を改善
    - spec-reviewer: レビュープロセス説明を整理

### Fixed

- **plan-refactor テンプレートの言語中立化** - 特定技術への依存を排除
    - `reverse-design-template.md`: TypeScript, React, PostgreSQL 等の具体例を削除
    - `reverse-design-template.md`: 言語固有のコードブロック（typescript, sql）を削除
    - API エンドポイントセクション: サンプル行を削除しテーブルヘッダーのみに簡素化
    - データベーススキーマセクション: 実装からの逆生成が不可能なため完全に削除
    - 関数シグネチャセクション: TypeScript 固有の内容のため完全に削除
    - プレースホルダーを説明的なガイダンス形式に変更（例: `{e.g., TypeScript}` →
      `{Programming language used in the project}`）

## [3.0.2] - 2026-02-09

### Fixed

- **`sdd-init`** - `.sdd-config.json` からの言語設定継承を修正
    - `update-claude-md.sh` が環境変数に依存せず `.sdd-config.json` から直接 `SDD_LANG` を読み取るように変更
    - 従来、`.sdd-config.json` に `lang: "ja"` が設定されていても、`CLAUDE.md` の `## AI-SDD Instructions`
      セクションが誤って英語で生成されていた
    - 根本原因: `init-structure.sh` による `CLAUDE_ENV_FILE` への書き込みが、同一シェルセッション内で
      `update-claude-md.sh` 実行時に反映されていなかった

## [3.0.1] - 2026-02-09

### Added

#### 新スキル（PRD 生成ワークフロー）

- **`/generate-usecase-diagram`** - ユースケース図生成スキル
    - ビジネス要求から Mermaid flowchart ベースのユースケース図を生成
    - コンテキスト分離のための `context: fork`
    - 対話モードと CI（`--ci`）モードをサポート
    - テキストのみを返す（ファイル書き込みなし）

- **`/analyze-requirements`** - 要求分析スキル
    - UR（ユーザー要求）、FR（機能要求）、NFR（非機能要求）を抽出
    - コンテキスト分離のための `context: fork`
    - MoSCoW 優先度付けとリスク評価をサポート
    - テキストのみを返す（ファイル書き込みなし）

- **`/generate-requirements-diagram`** - SysML 要求図生成スキル
    - 要求分析から Mermaid requirementDiagram を生成
    - コンテキスト分離のための `context: fork`
    - 要求間関係（contains, derives, traces）をサポート
    - テキストのみを返す（ファイル書き込みなし）

- **`/finalize-prd`** - PRD 統合スキル
    - ユースケース図、要求分析、要求図を統合して完全な PRD を生成
    - コンテキスト分離のための `context: fork`
    - PRD テンプレート構造に準拠
    - テキストのみを返す（ファイル書き込みなし）

#### スキル強化

- **`sdd-init`** - `.sdd-config.json` の `lang` フィールドの自動管理を追加
    - 設定ファイルが存在しない場合: デフォルト設定（`lang: "en"` を含む）で作成
    - 設定ファイルが存在するが `lang` フィールドがない場合（v3.0.0 からの移行）: `lang: "en"` を追加
    - 実行フローにステップ 1.5「設定ファイルの管理」を追加
    - シェルスクリプトを追加: `init-structure.sh`, `update-claude-md.sh`

- **`check-spec`** - ファイルスキャン用シェルスクリプトを追加
    - `scripts/find-design-docs.sh` - 設計書を事前スキャンし Claude の Glob/Grep オーバーヘッドを削減

- **`constitution`** - 検証用シェルスクリプトを追加
    - `scripts/validate-files.sh` - 検証用に requirement/spec/design ファイルを事前スキャン

- **`generate-spec`** - 準備用シェルスクリプトを追加
    - `scripts/prepare-spec.sh` - 仕様書生成用にファイルを前処理

#### Documentation

- **Mermaid 記法ガイドに注記を追加**
    - `<` と `>` を含むラベル（`<<include>>` 等）は HTML エンティティでエスケープが必要
    - 例: `<<include>>` を表示するには `&lt;&lt;include&gt;&gt;` と記述する

- **Progressive Disclosure 用のリファレンスファイルを追加**
    - `clarify/references/nine_category_analysis.md` - 9カテゴリ分析の定義
    - `constitution/references/best_practices.md` - Constitution のベストプラクティス
    - `constitution/examples/validation_report.md` - 検証レポートの例

### Changed

#### スキルアーキテクチャ

- **`generate-prd`** - オーケストレーターパターンにリファクタリング
    - 4つのサブスキルをオーケストレート: `/generate-usecase-diagram`, `/analyze-requirements`,
      `/generate-requirements-diagram`, `/finalize-prd`
    - サブスキルはコンテキスト分離のため `context: fork` で実行
    - サブスキルはテキストのみを返し、ファイル書き込みは `generate-prd` が担当
    - SKILL.md を 374 行から 140 行に削減
    - ワークフロー追跡用の Progress Checklist を追加

- **全スキル** - Claude Code Skills ベストプラクティスへの準拠
    - 全スキルに `$ARGUMENTS` プレースホルダーと `## Input` セクションを追加
    - `allowed-tools` が未設定のフロントマターに追加
    - 出力前の `Quality Checks` セクションを追加
    - SKILL.md ファイルを 500 行以下に維持（Progressive Disclosure パターン）
    - 詳細な内容を `references/` および `examples/` ディレクトリに移動

- **`constitution`** - 558 行から 392 行に削減
    - 検証レポートの例を `examples/validation_report.md` に移動
    - ベストプラクティスを `references/best_practices.md` に移動

- **`clarify`** - 行数を削減
    - 9カテゴリ分析を `references/nine_category_analysis.md` に移動

#### Shared References

- **`usecase_diagram_guide.md`** - ユースケース図の関係記法を UML 標準に修正
    - 関連（Association）: `-->` → `---`（実線・双方向）
    - 包含（Include）: `-. include .->` → `-.->|"<<include>>"|`（ステレオタイプラベル付き点線矢印）
    - 拡張（Extend）: `-. extend .->` → `-.->|"<<extend>>"|`（ステレオタイプラベル付き点線矢印）
    - Common Mistakes テーブルを更新
    - すべての Mermaid コード例を新記法に更新

- **`mermaid_notation_rules.md`** - ユースケース図記法を更新
    - 関連の記法を `---` に修正
    - Include/Extend のラベル形式を更新
    - Common Mistakes セクションを更新

#### Templates

- **`generate-prd`** - PRD テンプレートのユースケース図記法を修正
    - `templates/en/prd_template.md`: 関連、Include、Extend の記法を更新
    - `templates/ja/prd_template.md`: 同様の修正（日本語ラベル `<<包含>>`、`<<拡張>>` を維持）

## [3.0.0] - 2026-02-06

### Added

#### 新スキル

- **`/run-checklist`** - 品質検証自動化スキル
    - `/checklist` で生成されたチェックリスト項目の検証コマンドを自動実行
    - テスト、リンター、セキュリティスキャナー、仕様整合性チェックを実行
    - カテゴリ（`--category`）と優先度（`--priority`）によるフィルタリングをサポート
    - 進捗追跡のための TaskList 統合
    - チェックリストファイルに結果をタイムスタンプ付きで直接記録
    - `.sdd/task/{ticket}/verification_report.md` に検証レポートを生成

#### Shared References

- **`shared/references/`** - リファレンスドキュメントの一元化
    - `mermaid_notation_rules.md` - 包括的な Mermaid 構文ガイド（1100行以上）
        - フローチャート、シーケンス図、クラス図、状態遷移図、ER図、要求図、ガント図の構文
        - エスケープルール、スタイリング、よくある落とし穴
    - `usecase_diagram_guide.md` - Mermaid 用ユースケース図ガイド（750行以上）
        - アクター、ユースケース、システム境界の定義
        - 関係の種類（関連、包含、拡張、汎化）
        - スタイリングとレイアウトのベストプラクティス
    - `requirements_diagram_components.md` - SysML 要求図コンポーネント（800行以上）
        - 属性付き要求要素の定義（id, text, risk, verifyMethod）
        - 関係の種類（containment, derivation, refinement, satisfaction, verification）
        - Mermaid 構文の例とテンプレート
    - `document_dependencies.md` - ドキュメント依存チェーンのリファレンス
    - `prerequisites_directory_paths.md` - SDD 環境変数リファレンス
    - `prerequisites_plugin_update.md` - プラグイン更新チェック手順
    - `prerequisites_principles.md` - AI-SDD 原則リファレンス

#### エージェント構造の改善

- **エージェント出力テンプレート** - 全エージェント向けの言語別テンプレート
    - `agents/templates/en/` - 英語出力テンプレート
    - `agents/templates/ja/` - 日本語出力テンプレート
    - テンプレート: `clarification_analysis_output.md`, `clarification_question_template.md`, `prd_review_output.md`,
      `requirement_analysis_output.md`, `spec_review_output.md`
- **エージェントリファレンス** - 再利用可能なリファレンスドキュメント
    - `agents/references/ambiguity_patterns.md` - 曖昧表現パターン
    - `agents/references/document_link_convention.md` - Markdown リンク規約
    - `agents/references/sysml_requirements_theory.md` - SysML 要求理論
    - 共有リファレンスへのシンボリックリンク: `mermaid_notation_rules.md`, `requirements_diagram_components.md`,
      `usecase_diagram_guide.md`
- **エージェント使用例** - 使用例の追加
    - `agents/examples/clarification_questions.md` - 明確化質問の例

#### スキル構造の改善

- 全スキルに共有リファレンスへのシンボリックリンクを持つ **`references/` ディレクトリを追加**
    - スキル間で一貫した前提条件の取り扱いを実現
    - 前提条件ドキュメントの重複を削減
- 使用例を持つスキルに **`examples/` ディレクトリを追加**
    - `check-spec/examples/` - scope_confirmation.md, serena_symbol_analysis.md
    - `checklist/examples/` - checklist_full_example.md
    - `constitution/examples/` - constitution_as_code.json, constitution_file_structure.md, principle_template.md
    - `generate-spec/examples/` - compliance_check_design.md, compliance_check_spec.md, prd_reference_section.md
    - `implement/examples/` - implementation_progress_log.md, input_format.md, option_* ファイル, output_* ファイル
    - `task-breakdown/examples/` - requirement_coverage.md, serena_analysis.md, task_list_format.md
    - `task-cleanup/examples/` - scope_confirmation.md

### Changed

#### Skills

- **全スキルをリファクタリング** し、シンボリックリンク経由で共有リファレンスを使用
    - 前提条件は `references/prerequisites_*.md` シンボリックリンクを参照
    - メンテナンスコストを削減し一貫性を確保
- **`implement` スキル** - リファレンスとテンプレートファイルを大幅追加
    - `references/commit_strategy.md`, `five_phases_overview.md`, `tdd_principles.md` 等
    - `templates/{en,ja}/phase_*.md` - フェーズ実行テンプレート
    - `templates/{en,ja}/tasklist_patterns.md` - TaskList 統合パターン
- **`generate-prd` スキル** - Mermaid 図のリファレンスを追加
    - `mermaid_notation_rules.md`, `usecase_diagram_guide.md`, `requirements_diagram_components.md` へのリンク
- **`doc-consistency-checker` スキル** - ドキュメント依存関係リファレンスを追加

#### Agents

- **全エージェントを Progressive Disclosure パターンでリファクタリング**
    - エージェント Markdown ファイルは大きなコンテンツに `@reference` インポートを使用
    - 出力テンプレートを `templates/{en,ja}/` に外部化
- **`spec-reviewer`** - リファレンス活用により 566 行から約 200 行に簡素化
- **`prd-reviewer`** - リファレンス活用により 328 行から約 150 行に簡素化
- **`requirement-analyzer`** - リファレンス活用により 420 行から約 150 行に簡素化
- **`clarification-assistant`** - リファレンス活用により 626 行から約 200 行に簡素化

### Removed

#### Skills

- **`sdd-templates`** - 共有リファレンスと各スキルのテンプレートに統合
- **`output-templates`** - テンプレートを各スキルディレクトリに移動

#### レガシーコマンド

- **`commands/` ディレクトリを完全削除**
    - `commands/checklist.md` - `skills/checklist/SKILL.md` に移行
    - `commands/implement.md` - `skills/implement/SKILL.md` に移行
    - `commands/sdd_init.md` - `skills/sdd-init/SKILL.md` に移行

---

## [3.0.0-alpha] - 2026-02-03

### Breaking Changes

#### プラグイン統合

- **`sdd-workflow-ja` と `sdd-workflow` を単一の統合プラグイン（`sdd-workflow`）にマージ**
    - `SDD_LANG` 環境変数による言語選択（`.sdd-config.json` の `lang` フィールドから、デフォルト: `en`）
    - テンプレートを言語別に分割: `templates/ja/` と `templates/en/`
    - SKILL.md とエージェントファイルは英語のみ
    - `sdd-workflow-ja` プラグインを完全に削除

#### コマンドのスキル化

- **全 11 コマンドを `user-invocable: true` のスキルに移行**
    - `commands/` ディレクトリを完全に削除
    - すべてのコマンドは `skills/{name}/SKILL.md` 配下に配置

#### コマンド名の変更（アンダースコア → ハイフン）

| 旧 (v2.x)          | 新 (v3.0.0)        |
|:------------------|:------------------|
| `/sdd_init`       | `/sdd-init`       |
| `/generate_spec`  | `/generate-spec`  |
| `/generate_prd`   | `/generate-prd`   |
| `/check_spec`     | `/check-spec`     |
| `/task_breakdown` | `/task-breakdown` |
| `/task_cleanup`   | `/task-cleanup`   |
| `/sdd_migrate`    | `/sdd-migrate`    |

### Added

#### 多言語対応

- **`SDD_LANG` 環境変数** - テンプレート言語の選択を制御
    - `.sdd-config.json` の `lang` フィールドで設定
    - サポート値: `en`（デフォルト）、`ja`
    - `session-start.sh` が設定から `lang` を読み取り `SDD_LANG` をエクスポート

#### 言語別テンプレート

- 既存 4 スキルすべてに言語別テンプレートを追加:
    - `sdd-templates/templates/{en,ja}/`
    - `vibe-detector/templates/{en,ja}/`
    - `doc-consistency-checker/templates/{en,ja}/`
    - `output-templates/templates/{en,ja}/`
- 日本語テンプレートは旧 `sdd-workflow-ja` プラグインからコピー

### Changed

#### Skills

- **旧コマンドから 11 の新スキルを作成**:
    - `sdd-init`, `constitution`, `generate-spec`, `generate-prd`, `check-spec`
    - `task-breakdown`, `implement`, `clarify`, `task-cleanup`, `sdd-migrate`, `checklist`
    - 各スキルに適切な `allowed-tools`、`user-invocable: true`、必要に応じて `disable-model-invocation` を設定
- **既存 4 スキルを言語設定対応の v3.0.0 に更新**
    - 動的な `SDD_LANG` コンテキスト注入を行う `## Language Configuration` セクションを追加
    - テンプレートパス参照を `templates/en/` 形式に更新

#### Agents

- **spec-reviewer** - `skills` フィールドを追加: `["sdd-workflow:sdd-templates", "sdd-workflow:doc-consistency-checker"]`
- **prd-reviewer** - `skills` フィールドを追加: `["sdd-workflow:sdd-templates"]`
- 全 4 エージェントをハイフン形式のコマンド名参照に更新
- 全エージェントの説明を新コマンド名参照に更新

#### Configuration

- **`.sdd-config.json`** - 言語設定用の `lang` フィールドを追加
- **`session-start.sh`** - `SDD_LANG` の読み取りとエクスポートを追加
- **`plugin.json`** - 統合プラグインの説明とともに v3.0.0 に更新
- **`marketplace.json`** - `sdd-workflow-ja` エントリを削除、`sdd-workflow` を v3.0.0 に更新

#### Documentation

- **`CLAUDE.md`** - スキルを持つ単一プラグインを反映するようリポジトリ構成を更新
- **`README.md`** - v2.x からの移行ガイドを追加、全コマンド参照を更新

### Removed

- **`plugins/sdd-workflow-ja/`** - 日本語プラグインディレクトリ全体（`sdd-workflow` に統合）
- **`plugins/sdd-workflow/commands/`** - commands ディレクトリ全体（スキルに移行）

## [2.4.2] - 2026-01-26

### Fixed

#### プラグインマニフェスト

- **plugin.json から skills フィールドを削除** - プラグインインストールエラーを修正
    - Claude Code の plugin.json スキーマでサポートされていない `skills` フィールドを削除
    - スキルは `skills/` ディレクトリから自動検出される
    - インストール時の「Invalid input」エラーを解消

## [2.4.1] - 2026-01-26

### Fixed

#### Commands

- **argument-hint の修正と引数説明の追加** - 引数仕様を実際の使い方に合わせて修正
    - `argument-hint` の表現を統一（"file-path" → "feature-name" の修正）
    - 各コマンドに引数説明テーブルを追加（引数名、必須/任意、説明）
    - 対象コマンド:
        - `task_breakdown`: `<design-doc-path>` → `<feature-name> [ticket-number]`
        - `check_spec`: `<design-doc-path>` → `[feature-name] [--full]`
        - `checklist`: `<file-path>` → `<feature-name> [ticket-number]`
        - `clarify`: `[spec-file-path]` → `<feature-name> [--interactive]`
        - `constitution`: `<init|update|check>` → `<subcommand> [arguments]`（サブコマンド詳細テーブルを追加）
        - `generate_prd`: `<feature-name> [requirements-description]` → `<requirements-description>`
        - `generate_spec`: `<feature-name> [prd-file-path]` → `<requirements-description>`
        - `implement`: `<task-file-path>` → `<feature-name> [ticket-number]`
        - `task_cleanup`: `<ticket-number>` → `[ticket-number]`（任意に変更）
    - コマンド実行時に正しい引数形式を把握できるように

## [2.4.0] - 2026-01-25

### Added

#### Documentation

- **PLUGIN.md** - Claude Code プラグインとマーケットプレイス作成の包括的ガイド
    - プラグイン基本構造（ディレクトリレイアウト、マーケットプレイス構成）
    - マニフェストファイル（plugin.json, marketplace.json の詳細）
    - コマンド、エージェント、スキルの実装（フロントマター、ベストプラクティス）
    - MCP サーバー統合（外部ツール連携）
    - フック実装（イベント駆動の自動化）
    - マーケットプレイス公開プロセス（品質基準、配布モデル）
- **CLAUDE.md** - PLUGIN.md への参照を追加（PLUGIN_AGENTS.md と同様の構成）

#### Skills

- 全スキルに `version: 2.3.1` と `license: MIT` フィールドを追加
    - vibe-detector
    - doc-consistency-checker
    - sdd-templates
- **output-templates** - コマンド出力フォーマットを提供する新スキル
    - `init_output.md` - 初期化完了メッセージ
    - `prd_output.md` - PRD 生成完了メッセージ
    - `spec_output.md` - 仕様書・設計書生成完了メッセージ
    - `breakdown_output.md` - タスク分解結果
    - `cleanup_output.md` - クリーンアップ確認
    - `clarification_output.md` - 仕様明確化レポート
    - `check_spec_output.md` - 整合性チェック結果
    - `migrate_output.md` - マイグレーション結果
    - `constitution_output.md` - Constitution 管理結果

#### Commands

- 全コマンドに `argument-hint` フィールドを追加し使いやすさを改善
    - generate_spec: `<feature-name> [prd-file-path]`
    - generate_prd: `<feature-name> [requirements-description]`
    - check_spec: `<design-doc-path>`
    - task_breakdown: `<design-doc-path> [ticket-number]`
    - task_cleanup: `<ticket-number>`
    - constitution: `<init|update|check>`
    - implement: `<task-file-path>`
    - clarify: `[spec-file-path]`
    - checklist: `<file-path>`

### Changed

#### アーキテクチャ

- **出力フォーマットの分離** - コマンド出力フォーマットを `skills/output-templates/` に分離
    - コマンド md ファイルは Claude 向けの指示のみを含む
    - 出力フォーマットは独立したテンプレートファイルとして管理
    - 新スキル: `output-templates`（9 テンプレートファイルを含む）
    - 既存の `sdd-templates` スキルはプロジェクトドキュメントテンプレート専用に

#### Commands

- **implement** - TaskList ベースの進捗管理を追加
    - 各フェーズ開始時に TaskCreate でタスクを作成
    - フェーズ実行中に TaskUpdate でタスクステータスを更新（pending → in_progress → completed）
    - 依存関係を設定し、前フェーズ完了後にのみ次フェーズを開始
    - `/tasks` コマンドで実装進捗を確認可能
    - TaskList が利用できない場合は従来の Markdown 進捗表示にフォールバック

#### Marketplace

- **marketplace.json** の改善
    - `author.url` を追加（作成者の帰属表示）
    - `category: "development"` を追加（マーケットプレイスのフィルタリング）
    - `tags` 配列を追加（検索での発見性向上）
        - "specification-driven-development"
        - "japanese" / "english"
        - "workflow"
        - "sysml"
        - "requirements"
        - "documentation"

#### Agents

- 全エージェントの `description` を使用シナリオが明確になるよう改善
    - 機能説明スタイルから「いつ使うか」スタイルに変更
    - 具体的なトリガーフレーズを追加（例: "review spec", "check spec"）
    - コマンドとの関係を明示（例: /check_spec や /generate_spec 実行後）
    - 必要な入力情報を明記（例: 仕様書ファイルパスが必要）
    - 自己言及的な「agent」という表現を削除
    - 対象エージェント: spec-reviewer, requirement-analyzer, prd-reviewer, clarification-assistant

#### Skills

- 全スキルの `description` を実行コンテキストが明確になるよう改善
    - 実行タイミングを明記（例: 実装前に自動実行、コマンドから呼び出し）
    - 検知内容の詳細を明記（例: 「いい感じに」「なんとなく」等の曖昧表現）
    - トレーサビリティ保証を明示
    - フォールバック動作の詳細な説明
    - 対象スキル: vibe-detector, doc-consistency-checker, sdd-templates

### Fixed

#### Commands

- **プロンプト表現の統一** - ユーザー向け説明を削除し、Claude 向けの明確な指示に統一
    - 「Next Steps」リスト項目を削除（「Post-Generation Actions」セクション内のプレーンテキストから）
    - 「Recommended Manual Verification」セクションを削除（出力テンプレートに移動）
    - 「manually」表現を Claude 向けの指示に変更（例: 「ユーザーに手動検証を推奨する」）
    - 出力フォーマット参照方法を統一（ファイルパスからスキル参照へ）
    - 対象コマンド: `sdd_init`, `generate_prd`, `generate_spec`, `task_breakdown`, `task_cleanup`, `clarify`,
      `check_spec`, `sdd_migrate`, `constitution`

#### Agents

- **プロンプト表現の統一** - 「recommended」表現を指示形に変更
    - spec-reviewer: "recommended to be added" → "need to be added"
    - clarification-assistant: "Supplementation recommended" → "Supplementation needed"
    - clarification-assistant: "Recommended Clarity Scores" → "Clarity Score Evaluation Criteria"

## [2.3.1] - 2026-01-14

### Fixed

#### Hooks

- `session-start.sh` - 一時ファイル存在チェックによるエラーハンドリングの改善
    - sed コマンド失敗時の `mv: No such file or directory` エラーを修正
    - mv 実行前に一時ファイルの存在を確認する `&& [ -f "$TEMP_FILE" ]` を追加
    - フォールバック処理が正しく動作するよう改善
    - 日本語版との一貫性のため、英語版に警告ファイル削除処理（else 節）を追加

## [2.3.0] - 2026-01-09

### Changed

#### Agents

- **役割分離**: `sdd-workflow` エージェントを `AI-SDD-PRINCIPLES.md` にリネーム
    - 原則定義を独立したドキュメントに分離
    - 全コマンド、エージェント、スキルの参照を `../AI-SDD-PRINCIPLES.md` に更新
    - AI-SDD 原則を一元化しメンテナンス性を向上

- `spec-reviewer` - ドキュメントトレーサビリティチェック機能を追加
    - **PRD ↔ spec トレーサビリティチェック**: PRD の要求が spec で適切にカバーされているかを検証
        - 要求 ID（UR/FR/NFR）のマッピング検証
        - カバレッジ率の計算（80% 閾値チェック）
        - 部分的/未カバーの分類
    - **spec ↔ design 整合性チェック**: spec の内容が design で適切に詳細化されているかを検証
        - API 定義の詳細化チェック
        - 型定義の整合性チェック
        - 制約の考慮チェック
    - `allowed-tools` に `Edit` を追加（自動修正サポート用）
    - 入力フォーマットと出力フォーマットを明確化（`--summary` オプションをサポート）

#### Commands

- `/check_spec` - **design ↔ 実装の整合性チェックに特化**
    - **[BREAKING]** ドキュメント間の整合性チェック（PRD↔spec, spec↔design）を `spec-reviewer` に委譲
        - **変更前 (v2.2.0)**: すべての整合性チェックを実行（CONSTITUTION↔docs, PRD↔spec, spec↔design,
          design↔実装）
        - **変更後 (v2.3.0)**: design↔実装の整合性チェックのみ実行（パフォーマンス改善）
        - **移行方法**:
            - ドキュメント間の整合性チェックが必要な場合: `/check_spec --full` を使用
            - design↔実装のみで十分な場合: 従来どおり `/check_spec` を使用（コマンドは同じ）
        - **影響**: CI/CD パイプラインで `/check_spec` を使用している場合は `--full` オプションの追加を検討
    - `--full` オプションを追加: 整合性チェックに加えて `spec-reviewer` による包括的レビューを実行
    - 対象ドキュメントを `*_design.md` に限定
    - 出力フォーマットを簡素化（design↔実装に焦点）

- `/sdd_init` - 参照パスを更新
    - エージェント参照を `AI-SDD-PRINCIPLES.md` に変更

### Added

#### Documentation

- `AI-SDD-PRINCIPLES.md` - AI-SDD 原則を定義する独立ドキュメント
    - 従来 `sdd-workflow` エージェントに含まれていた原則定義を分離
    - コマンド、エージェント、スキルから共通で参照

#### README

- Windows プラットフォーム非対応を文書化
    - プラットフォームサポートマトリクスを追加（macOS/Linux: ✅、Windows: ❌）
    - Windows ユーザー向けの代替案を記載（WSL, Git Bash）
    - 今後のサポート計画（PowerShell 版、クロスプラットフォーム実装を検討中）

## [2.2.0] - 2026-01-06

### Added

#### Agents

- `prd-reviewer` - PRD（要求仕様書）レビューエージェント
    - CONSTITUTION.md 準拠チェック（最重要機能）
    - 原則カテゴリのチェック（ビジネス、アーキテクチャ、開発、技術的制約）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - SysML 要求図フォーマットの検証
    - 曖昧表現の検出と改善提案

### Changed

#### Agents

- `spec-reviewer` - CONSTITUTION.md 準拠チェック機能を追加
    - Read ツールで CONSTITUTION.md を読み込む準備手順を追加
    - spec 向けの原則カテゴリチェック（アーキテクチャ原則を重視）
    - design 向けの原則カテゴリチェック（技術的制約を重視）
    - 自動修正フロー（違反検出時に自動修正を試行）
    - レビュー出力フォーマットに CONSTITUTION.md 準拠チェック結果を追加

#### Commands

- `/generate_prd` - CONSTITUTION.md 準拠の生成フローを追加
    - 生成フローに CONSTITUTION.md 読み込みステップを追加（Step 2）
    - prd-reviewer による原則準拠チェックを必須化（Step 6）
    - PRD 向けの原則カテゴリ影響テーブルを追加
    - チェック結果の出力テンプレートを追加

- `/generate_spec` - CONSTITUTION.md 準拠の生成フローを追加
    - 生成フローに CONSTITUTION.md 読み込みステップを追加（Step 2）
    - spec-reviewer による原則準拠チェックを必須化（Steps 6, 8）
    - spec と design doc 両方のチェック結果出力テンプレートを追加

## [2.1.1] - 2025-12-23

### Changed

- 全コマンドとエージェントから自動 git commit の指示を削除
    - `task_cleanup` - クリーンアップワークフローからコミットステップを削除
    - `implement` - 継続的検証フローからコミット指示を削除
    - `generate_spec` - 生成フローからコミットステップを削除
    - `sdd-workflow` エージェント - ワークフローフェーズからコミットステップを削除
    - `clarify` - 統合モードからコミット指示を削除
    - `task_breakdown` - 生成後アクションからコミットステップを削除
    - `generate_prd` - 生成後アクションからコミットステップを削除
    - `sdd_migrate` - コミット指示とコミットメッセージ例を削除
    - `sdd_init` - 初期化フローからコミットステップを削除

## [2.1.0] - 2025-12-12

### Added

#### Commands

- `/clarify` - 仕様明確化コマンド
    - 9 カテゴリ（機能スコープ、データモデル、フロー、非機能要件、連携、
      エッジケース、制約、用語、完了基準）で仕様をスキャン
    - 不明確な項目を Clear/Partial/Missing に分類
    - 影響度の高い明確化質問を最大 5 件生成
    - 回答を段階的に `*_spec.md` に統合
    - `vibe-detector` スキルと補完関係
- `/implement` - TDD ベースの実装実行コマンド
    - tasks.md のチェックリスト完了率を検証
    - 5 フェーズを順番に実行（Setup→Tests→Core→Integration→Polish）
    - テストファースト（TDD）アプローチ
    - tasks.md の進捗を自動マーキング
    - 完了検証（全タスク完了、テスト合格、仕様整合性）
- `/checklist` - 品質チェックリスト生成コマンド
    - 仕様書と計画から 9 カテゴリのチェックリストを自動生成
    - CHK-{カテゴリ番号}{連番} 形式で ID を採番
    - 優先度レベル（P1/P2/P3）を自動設定
- `/constitution` - プロジェクト憲法管理コマンド
    - プロジェクトの交渉不可能な原則を定義（ビジネス、アーキテクチャ、開発方法論、技術的制約）
    - セマンティックバージョニング（MAJOR/MINOR/PATCH）
    - 仕様書・設計書との同期検証

#### Agents

- `clarification-assistant` - 仕様明確化アシスタントエージェント
    - 9 カテゴリでユーザー要求を体系的に分析
    - 影響度の高い明確化質問を生成
    - 回答を仕様書に統合
    - `/clarify` コマンドのバックエンド役

#### Templates

- `checklist_template.md` - 品質チェックリストテンプレート
    - 9 カテゴリの品質チェック項目
    - 優先度レベル（P1/P2/P3）
    - 各項目の検証方法
- `constitution_template.md` - プロジェクト憲法テンプレート
    - 原則の階層（ビジネス → アーキテクチャ → 開発方法論 → 技術的制約）
    - 各原則の検証方法、違反例、準拠例
    - バージョン履歴と改定プロセス
- `implementation_log_template.md` - 実装ログテンプレート
    - セッション単位の実装判断記録
    - 課題と解決策の追跡
    - 技術的発見とパフォーマンス指標

#### Skills

- `sdd-templates` - 新テンプレートへの参照を追加

## [2.0.1] - 2025-12-12

### Added

#### Agents

- 全エージェントにドキュメントリンク規約を追加
    - `sdd-workflow` - ファイル/ディレクトリの Markdown リンク形式を定義
    - `spec-reviewer` - リンク規約のチェックポイントを追加
    - `requirement-analyzer` - 要求図向けのリンク規約を追加
    - ファイルリンク: `[filename.md](path)` 形式
    - ディレクトリリンク: `[directory-name](path/index.md)` 形式

### Removed

#### Agents

- `sdd-workflow` - コミットメッセージ規約セクションを削除
    - Claude Code 標準のコミット規約に委ねる方針に変更

## [2.0.0] - 2025-12-09

### Breaking Changes

#### ディレクトリ構造の変更

- **ルートディレクトリ**: `.docs/` → `.sdd/`
- **要求ディレクトリ**: `requirement-diagram/` → `requirement/`
- **タスクログディレクトリ**: `review/` → `task/`

#### コマンドのリネーム

- `/review_cleanup` → `/task_cleanup`

#### マイグレーション

レガシーバージョン（v1.x）からの移行には `/sdd_migrate` コマンドを使用:

- **オプション A**: ディレクトリをリネームして新構造に移行
- **オプション B**: `.sdd-config.json` を生成してレガシー構造を維持

### Added

#### Commands

- `/sdd_init` - AI-SDD ワークフロー初期化コマンド
    - プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
    - `.sdd/` ディレクトリ構造（requirement/, specification/, task/）を作成
    - `sdd-templates` スキルでテンプレートファイルを生成
- `/sdd_migrate` - レガシーバージョンからのマイグレーションコマンド
    - レガシー構造（`.docs/`, `requirement-diagram/`, `review/`）を検出
    - 新構造への移行か互換設定の生成かを選択可能

#### Agents

- `requirement-analyzer` - 要求分析エージェント
    - SysML 要求図ベースの分析
    - 要求の追跡と検証

#### Skills

- `sdd-templates` - AI-SDD テンプレートスキル
    - PRD、仕様書、設計書のフォールバックテンプレートを提供
    - プロジェクトテンプレートの優先ルールを明確化

#### Hooks

- `session-start` - セッション開始時の初期化フック
    - `.sdd-config.json` から設定を読み込み環境変数を設定
    - レガシー構造を自動検出しマイグレーションガイダンスを表示

#### 設定ファイル

- `.sdd-config.json` - プロジェクト設定ファイルのサポート
    - `root`: ルートディレクトリ（デフォルト: `.sdd`）
    - `directories.requirement`: 要求ディレクトリ（デフォルト: `requirement`）
    - `directories.specification`: 仕様ディレクトリ（デフォルト: `specification`）
    - `directories.task`: タスクログディレクトリ（デフォルト: `task`）

### Changed

#### プラグイン設定

- `plugin.json` - author フィールドを強化
    - `author.url` フィールドを追加

#### Commands

- 全コマンドに `allowed-tools` フィールドを追加
    - 各コマンドで利用可能なツールを明示
    - セキュリティと明確性を向上
- 全コマンドが `.sdd-config.json` 設定ファイルをサポート

#### Skills

- スキルディレクトリ構造を改善
    - `skill-name.md` から `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosure パターンを適用
    - テンプレートファイルを外部化し SKILL.md を簡素化

### Removed

#### Hooks

- `check-spec-exists` - 削除
    - 仕様書の作成は任意であり、存在しないことは一般的な正常ケースのため
- `check-commit-prefix` - 削除
    - コミットメッセージ規約はプラグイン機能で使用されないため

## [1.1.0] - 2025-12-06

### Added

#### Commands

- `/sdd_init` - AI-SDD ワークフロー初期化コマンド
    - プロジェクトの `CLAUDE.md` に AI-SDD Instructions セクションを追加
    - `.docs/` ディレクトリ構造（requirement-diagram/, specification/, review/）を作成
    - `sdd-templates` スキルでテンプレートファイルを生成

#### Skills

- `sdd-templates` - AI-SDD テンプレートスキル
    - PRD、仕様書、設計書のフォールバックテンプレートを提供
    - プロジェクトテンプレートの優先ルールを明確化

### Changed

#### プラグイン設定

- `plugin.json` - author フィールドを強化
    - `author.url` フィールドを追加

#### Commands

- 全コマンドに `allowed-tools` フィールドを追加
    - 各コマンドで利用可能なツールを明示
    - セキュリティと明確性を向上

#### Skills

- スキルディレクトリ構造を改善
    - `skill-name.md` から `skill-name/SKILL.md` + `templates/` 構造に移行
    - Progressive Disclosure パターンを適用
    - テンプレートファイルを外部化し SKILL.md を簡素化

## [1.0.1] - 2025-12-04

### Changed

#### Agents

- `spec-reviewer` - 前提条件セクションを追加
    - 実行前に `sdd-workflow:sdd-workflow` エージェントの内容を読む指示を追加
    - AI-SDD 原則、ドキュメント構造、永続化ルール、Vibe Coding 防止の理解を促進

#### Commands

- 全コマンドに前提条件セクションを追加
    - `generate_prd`, `generate_spec`, `check_spec`, `task_breakdown`, `review_cleanup`
    - 実行前に `sdd-workflow:sdd-workflow` エージェントの内容を読む指示を追加
    - sdd-workflow エージェントの原則に従う一貫した動作を保証

#### Skills

- 全スキルに前提条件セクションを追加
    - `vibe-detector`, `doc-consistency-checker`
    - 実行前に `sdd-workflow:sdd-workflow` エージェントの内容を読む指示を追加

#### Hooks

- `check-spec-exists.sh` - パス解決を改善
    - `git rev-parse --show-toplevel` でリポジトリルートを動的に取得
    - git リポジトリでない場合はカレントディレクトリにフォールバック
- `check-spec-exists.sh` - テストファイル除外パターンを拡張
    - Jest: `__tests__/`, `__mocks__/`
    - Storybook: `*.stories.*`
    - E2E: `/e2e/`, `/cypress/`
- `settings.example.json` - セットアップ手順をコメントとして追加
    - パスを `./hooks/` 形式に修正

#### Skills

- `vibe-detector` - `allowed-tools` に `AskUserQuestion` を追加
    - ユーザー確認フローをサポート
- `doc-consistency-checker` - `allowed-tools` に `Bash` を追加
    - ディレクトリ構造の検証をサポート

## [1.0.0] - 2024-12-03

### Added

#### Agents

- `sdd-workflow` - AI-SDD 開発フロー管理エージェント
    - フェーズ判定（Specify → Plan → Tasks → Implement & Review）
    - Vibe Coding 防止（曖昧な指示の検出と明確化の促進）
    - ドキュメント整合性チェック
- `spec-reviewer` - 仕様書品質レビューエージェント
    - 曖昧な記述の検出
    - 不足セクションの特定
    - SysML 準拠チェック

#### Commands

- `/generate_prd` - ビジネス要求から SysML 要求図形式の PRD（要求仕様書）を生成
- `/generate_spec` - 入力から抽象仕様書と技術設計書を生成
    - PRD 整合性レビュー機能
- `/check_spec` - 実装コードと仕様書の整合性をチェック
    - 多層チェック: PRD ↔ spec ↔ design ↔ 実装
- `/task_breakdown` - 技術設計書からタスクを分解
    - 要求カバレッジの検証
- `/review_cleanup` - 実装後に review/ ディレクトリをクリーンアップ

#### Skills

- `vibe-detector` - Vibe Coding（曖昧な指示）の自動検出
- `doc-consistency-checker` - ドキュメント間の整合性自動チェック

#### Integration

- Serena MCP のオプション統合
    - セマンティックコード解析による機能強化
    - 30 以上のプログラミング言語をサポート
    - 未設定時はテキストベース検索にフォールバック
