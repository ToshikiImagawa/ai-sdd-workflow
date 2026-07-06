# テストと検証

- プラグインJSON構文チェック: `cat plugins/*/.claude-plugin/*.json | jq .`
- session-start.py ユニットテスト: `python3 -m pytest tests/ -v`（要 `pip install pytest`。CI の `test` ジョブでも実行）
- Markdownリンクの整合性: 各ドキュメント内の相対リンクが有効か確認
- **IMPORTANT**: 新規エージェント/スキル追加時は `plugin.json` への登録を忘れずに
- プラグインデバッグ: `claude --debug` でプラグインの読み込み、フック実行、エージェント呼び出しの詳細ログを確認
- ローカルテスト: `claude --plugin-dir ./plugins/sdd-workflow` でローカルのプラグインを直接テスト
