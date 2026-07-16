# 推定仕様書（フォールバック形式）

`templates/${SDD_LANG:-en}/assumed_spec.md` が存在しない場合にのみ、以下の構造を使用する:

```markdown
# Assumed Specification (Inferred)

⚠️ **WARNING**: This specification was inferred from vague requirements and may not match user intent.

**Created**: {YYYY-MM-DD}
**Based on**: {Original user request}

## Assumptions Made

1. {Assumption with reasoning}
2. {Assumption...}

## Inferred Requirements

### Functional Requirements

- {Inferred requirement}
- {Inferred requirement...}

### Non-Functional Requirements

- {Inferred NFR if any}

## Items Requiring Verification

- [ ] {Item to verify with user}
- [ ] {Item to verify...}

## Known Risks

- {Risk from assumption}
- {Risk...}
```

**Save Location**: `${CLAUDE_PROJECT_DIR}/${SDD_TASK_PATH}/{ticket}/assumed-spec.md`
