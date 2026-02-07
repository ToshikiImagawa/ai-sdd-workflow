# 要求図 出力フォーマット

**重要: このスキルはテキストのみを返します。ファイルへの書き込みは行いません。**

以下のセクションを返してください：

## 要求図 (SysML)

```mermaid
%%{init: {'theme': 'dark'}}%%
requirementDiagram
    requirement System_Requirement {
        id: REQ_001
        text: "システム全体の要求"
        risk: high
        verifymethod: demonstration
    }

    functionalRequirement Create_Task {
        id: FR_001
        text: "ユーザーはタスクを作成できる"
        risk: high
        verifymethod: test
    }

    functionalRequirement Edit_Task {
        id: FR_002
        text: "ユーザーはタスクを編集できる"
        risk: medium
        verifymethod: test
    }

    performanceRequirement Response_Time {
        id: NFR_001
        text: "応答時間は1秒以内"
        risk: medium
        verifymethod: test
    }

    System_Requirement - contains -> Create_Task
    System_Requirement - contains -> Edit_Task
    System_Requirement - contains -> Response_Time
    Response_Time - traces -> Create_Task
```

## 図の構造

### 要求階層

```
REQ_001 (システム要求)
├── FR_001 (タスク作成)
├── FR_002 (タスク編集)
└── NFR_001 (応答時間)
    └── traces -> FR_001
```

### 関係性サマリー

| ソース   | 関係性    | ターゲット | 根拠                       |
|:--------|:---------|:---------|:--------------------------|
| REQ_001 | contains | FR_001   | コア機能                    |
| REQ_001 | contains | FR_002   | コア機能                    |
| NFR_001 | traces   | FR_001   | パフォーマンスはタスク作成に適用 |
