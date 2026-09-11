# CLI Usage Examples

Example invocations of `/plan-refactor`:

```
/plan-refactor auth
/plan-refactor user-list "無限スクロール化してパフォーマンス改善"
/plan-refactor auth "依存性注入を導入してテスト容易性を向上"
/plan-refactor user-profile --scope=src/profile
/plan-refactor auth --ticket=68
/plan-refactor auth --ticket 68
/plan-refactor auth/login --ticket=68 --ci
/plan-refactor payment-service "Strangler Figパターンで段階的にマイクロサービス化" --scope=src/services --ticket=68
```

`--ticket` locates the Design Doc draft (`task/{ticket-number}/design-draft.md`) the refactoring plan is written
into. Both `--ticket <number>` and `--ticket=<number>` are accepted and mean the same thing. It is resolved
interactively when omitted, and **required** in `--ci` mode.
