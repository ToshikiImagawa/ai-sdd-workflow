# Requirement Analyzer Usage Examples

## Basic Analysis

sdd-workflow:requirement-analyzer .sdd/requirement/user-auth.md --analyze

## Traceability Verification

sdd-workflow:requirement-analyzer .sdd/requirement/user-auth.md --trace

## Impact Analysis

sdd-workflow:requirement-analyzer .sdd/requirement/user-auth.md --impact FR_001

## ID Numbering Validation

sdd-workflow:requirement-analyzer .sdd/requirement/user-auth.md --validate-ids

## Add New Requirement (Interactive)

sdd-workflow:requirement-analyzer .sdd/requirement/user-auth.md --add-requirement

## ID Numbering Validation Output Example

    [must] ID convention violation:
      File: .sdd/specification/auth_spec.md:99
      Found: FR-AI-001'
      Expected pattern: FR-AI-{PRD#}'
      Hint: This refines FR_AI_002, so it should be FR-AI-002'

    [recommend] Non-ascending ID order:
      File: .sdd/requirement/infrastructure.md
      Sequence: IR_INFRA_001 ... IR_INFRA_007 → IR_INFRA_009 → IR_INFRA_008
      Suggestion: Move IR_INFRA_009 section after IR_INFRA_008
