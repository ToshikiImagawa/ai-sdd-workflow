# Security Policy

## 脆弱性の報告 / Reporting a Vulnerability

本リポジトリのプラグインは、フック（`hooks.json`）を通じてシェルコマンドや Python スクリプトを実行します。
そのため、脆弱性の報告は迅速かつ非公開に取り扱います。

Plugins in this repository execute shell commands and Python scripts via hooks (`hooks.json`).
Vulnerability reports are therefore handled promptly and privately.

### 報告方法 / How to Report

**公開の Issue や Pull Request で脆弱性を報告しないでください。**
**Do NOT report vulnerabilities via public issues or pull requests.**

1. GitHub の [Security Advisories](https://github.com/ToshikiImagawa/ai-sdd-workflow/security/advisories/new)
   から「Report a vulnerability」で非公開報告を作成してください
2. 上記が利用できない場合は、[@ToshikiImagawa](https://github.com/ToshikiImagawa) に直接連絡してください

Use GitHub's private vulnerability reporting (link above). If unavailable, contact
[@ToshikiImagawa](https://github.com/ToshikiImagawa) directly.

### 報告に含めてほしい情報 / What to Include

- 脆弱性の種類と影響範囲 / Type of vulnerability and its impact
- 再現手順（対象ファイル・設定・実行コマンド）/ Steps to reproduce (files, configuration, commands)
- 影響を受けるバージョン / Affected versions
- 可能であれば修正案 / Suggested fix, if any

### 対応プロセス / Response Process

| ステップ / Step | 目安 / Target |
|:---|:---|
| 受領確認 / Acknowledgement | 7日以内 / Within 7 days |
| 初期評価 / Initial assessment | 14日以内 / Within 14 days |
| 修正リリース / Fix release | 深刻度に応じて対応 / Depends on severity |

修正が公開されるまで、報告内容の公開は控えてください。
Please refrain from public disclosure until a fix is released.

## サポート対象バージョン / Supported Versions

最新リリースのみサポート対象です。脆弱性修正は最新バージョンに対して行われます。

Only the latest release is supported. Security fixes are applied to the latest version.

## 利用者向けの注意 / Notes for Users

- 本プラグインのフックは `plugins/sdd-workflow/scripts/` 配下のスクリプトをローカルで実行します。
  インストール前に内容を確認することを推奨します
- Hooks in this plugin execute scripts under `plugins/sdd-workflow/scripts/` locally.
  We recommend reviewing them before installation.
