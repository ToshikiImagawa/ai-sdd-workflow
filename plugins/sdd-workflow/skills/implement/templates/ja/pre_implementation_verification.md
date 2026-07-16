# 実装前検証

## ドキュメントの読み込みと検証

```
1. タスク分解を読み込み: ${SDD_TASK_PATH}/{ticket}/tasks.md
2. 設計書を読み込み: ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_design.md
3. 抽象仕様書を読み込み: ${SDD_SPECIFICATION_PATH}/[{path}/]{feature}_spec.md
4. PRDを読み込み（存在する場合）: ${SDD_REQUIREMENT_PATH}/[{path}/]{feature}.md
```

**命名規則の違いに注意**:

- **requirement 配下**: サフィックスなし（`index.md`, `{feature-name}.md`）
- **specification 配下**: `_spec` または `_design` サフィックス必須（`index_spec.md`, `{feature-name}_spec.md`）
