## AI-SDD Instructions (v{PLUGIN_VERSION})

<!-- sdd-workflow version: "{PLUGIN_VERSION}" -->

このプロジェクトは AI-SDD（AI駆動仕様駆動開発）ワークフローに従います。

### ドキュメント操作

`.sdd/` ディレクトリ配下のファイルを操作する際は、`.sdd/AI-SDD-PRINCIPLES.md` を参照し、AI-SDDワークフローに準拠してください。

**トリガー条件**:

- `.sdd/` 配下のファイルの読み取りまたは変更
- 新しい仕様書、設計書、要求仕様書の作成
- `.sdd/` ドキュメントを参照する機能の実装

### ディレクトリ構造

フラット構造と階層構造の両方をサポートしています。

**フラット構造（小〜中規模プロジェクト向け）**:

    .sdd/
    |- CONSTITUTION.md               # プロジェクト原則（最上位）
    |- PRD_TEMPLATE.md               # PRDテンプレート
    |- SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート
    |- DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート
    |- requirement/                  # PRD（要求仕様書）
    |   |- {feature-name}.md
    |- specification/                # 仕様書・設計書
    |   |- {feature-name}_spec.md    # 抽象仕様書
    |   |- {feature-name}_design.md  # 技術設計書
    |- task/                         # 一時タスクログ
        |- {ticket-number}/

**階層構造（中〜大規模プロジェクト向け）**:

    .sdd/
    |- CONSTITUTION.md               # プロジェクト原則（最上位）
    |- PRD_TEMPLATE.md               # PRDテンプレート
    |- SPECIFICATION_TEMPLATE.md     # 抽象仕様書テンプレート
    |- DESIGN_DOC_TEMPLATE.md        # 技術設計書テンプレート
    |- requirement/                  # PRD（要求仕様書）
    |   |- {feature-name}.md         # トップレベル機能
    |   |- {parent-feature}/         # 親機能ディレクトリ
    |       |- index.md              # 親機能概要・要求一覧
    |       |- {child-feature}.md    # 子機能要求仕様
    |- specification/                # 仕様書・設計書
    |   |- {feature-name}_spec.md    # トップレベル機能
    |   |- {feature-name}_design.md
    |   |- {parent-feature}/         # 親機能ディレクトリ
    |       |- index_spec.md         # 親機能抽象仕様書
    |       |- index_design.md       # 親機能技術設計書
    |       |- {child-feature}_spec.md   # 子機能抽象仕様書
    |       |- {child-feature}_design.md # 子機能技術設計書
    |- task/                         # 一時タスクログ
        |- {ticket-number}/

### ファイル命名規則（重要）

**注意: requirement と specification でサフィックスの有無が異なります。混同しないでください。**

| ディレクトリ            | ファイル種別 | 命名パターン                                 | 例                                         |
|:------------------|:-------|:---------------------------------------|:------------------------------------------|
| **requirement**   | 全ファイル  | `{name}.md`（サフィックスなし）                  | `user-login.md`, `index.md`               |
| **specification** | 抽象仕様書  | `{name}_spec.md`（`_spec` サフィックス必須）     | `user-login_spec.md`, `index_spec.md`     |
| **specification** | 技術設計書  | `{name}_design.md`（`_design` サフィックス必須） | `user-login_design.md`, `index_design.md` |

#### 命名パターン早見表

```
# 正しい命名
requirement/auth/index.md              # 親機能概要（サフィックスなし）
requirement/auth/user-login.md         # 子機能要求仕様（サフィックスなし）
specification/auth/index_spec.md       # 親機能抽象仕様書（_spec 必須）
specification/auth/index_design.md     # 親機能技術設計書（_design 必須）
specification/auth/user-login_spec.md  # 子機能抽象仕様書（_spec 必須）
specification/auth/user-login_design.md # 子機能技術設計書（_design 必須）

# 誤った命名（使用しないこと）
requirement/auth/index_spec.md         # requirement に _spec は不要
specification/auth/user-login.md       # specification には _spec/_design が必須
specification/auth/index.md            # specification には _spec/_design が必須
```

### ドキュメントリンク規約

ドキュメント内のマークダウンリンクは以下の形式に従ってください:

| リンク先       | 形式                                    | リンクテキスト   | 例                                                    |
|:-----------|:--------------------------------------|:----------|:-----------------------------------------------------|
| **ファイル**   | `[filename.md](パスまたはURL)`             | ファイル名を含める | `[user-login.md](../requirement/auth/user-login.md)` |
| **ディレクトリ** | `[directory-name](パスまたはURL/index.md)` | ディレクトリ名のみ | `[auth](../requirement/auth/index.md)`               |

この規約により、リンク先がファイルかディレクトリかが視覚的に明確になります。
