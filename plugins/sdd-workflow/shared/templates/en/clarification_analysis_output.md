## Specification Clarification Report

### Target Document

- `${SDD_SPECIFICATION_PATH}/[{parent}/]{feature}_spec.md`

* For hierarchical structure, parent features use `index_spec.md`

### Clarity Score

| Category | Clear | Partial | Missing | N/A | Score |
|:--|--:|--:|--:|--:|--:|
| Functional Scope | 3 | 1 | 0 | 0 | 75% |
| Data Model | 2 | 2 | 1 | 0 | 40% |
| Flow | 4 | 0 | 0 | 1 | 100% |
| Non-Functional Requirements | 0 | 2 | 2 | 0 | 0% |
| Integration | 1 | 0 | 1 | 0 | 50% |
| Edge Cases | 1 | 2 | 1 | 0 | 25% |
| Constraints | 2 | 0 | 0 | 0 | 100% |
| Terminology | 3 | 1 | 0 | 0 | 75% |
| Completion Signals | 0 | 1 | 2 | 0 | 0% |
| **Total** | **16** | **9** | **7** | **1** | **50%** |

**Clarity score** = Clear items ÷ (all items − N/A items), counted per item. Partial and Missing stay in the denominator, never in the numerator. Definition: `${CLAUDE_PLUGIN_ROOT}/skills/clarify/references/nine_category_analysis.md`.

### 🔴 Missing (Undefined) Items

#### Category: {Category Name}

**Item**: {Undefined item}

**Current Description**: Not specified

**Impact**: {Impact if unclear}

---

### 🟡 Partial Items

#### Category: {Category Name}

**Item**: {Partial item}

**Current Description**: "{Current description}"

**Unclear Points**: {What is unclear}

---

### Priority Questions (Max 5)

#### Q1. [High Priority] {Question Title}

**Category**: {Category Name}

**Questions**:

- {Specific question 1}
- {Specific question 2}

**Impact**: {Impact if unclear}

**Suggested Answer Format**:

```
{Answer template}
```

---

### Next Actions

1. **Answer questions**: Please answer the above questions
2. **Update specification**: Specification will be updated based on answers
3. **Re-scan**: Re-run clarification analysis to verify clarity
4. **Target**: Overall score of 80% or higher recommended before implementation

---

## Specification Update Complete

### Updated Sections

- `## {Section Name}` section: {Description of update}

### Clarity Score After Update

**Previous**: {previous_score}%
**Current**: {current_score}%
**Improvement**: +{improvement}%

### Remaining Unclear Points

(If any) List remaining unclear points

### Next Actions

- Clarity score 80% or above -> Ready to start implementation
- Clarity score below 80% -> Answer additional questions
