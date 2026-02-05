### Document Dependencies

#### Creation Order

Documents are created in the following order, where each document references its upstream documents:

```
CONSTITUTION.md → requirement/ (PRD) → specification/*_spec.md → specification/*_design.md → task/ → Implementation
```

**Direction meaning**: `A → B` means "B is created referencing A". Upstream documents serve as the source of truth for downstream documents.

- `CONSTITUTION.md`: Project principles (top-level, all documents must comply)
- `requirement/`: PRD/Requirements documents (created following CONSTITUTION)
- `specification/*_spec.md`: Abstract specifications (derived from requirements)
- `specification/*_design.md`: Technical design documents (detailed from specifications)
- `task/`: Task logs (broken down from designs, temporary)
- `Implementation`: Source code (implemented according to tasks/designs)

#### Verification Direction

Consistency checks verify in the reverse direction — from downstream back to upstream:

```
Implementation → task/ → specification/*_design.md → specification/*_spec.md → requirement/ → CONSTITUTION.md
```

Each downstream document is checked against its upstream source of truth. When inconsistencies are found, prioritize upstream documents (PRD > spec > design).

#### Document Persistence

| Document | Persistence | Rules |
|:--|:--|:--|
| `CONSTITUTION.md` | **Persistent** | Project principles. Updated only through `/constitution` |
| `requirement/*.md` | **Persistent** | PRD/Requirements. Updated when business requirements change |
| `specification/*_spec.md` | **Persistent** | Abstract specifications. Updated when requirements change |
| `specification/*_design.md` | **Persistent** | Technical designs. Integrate important decisions from task/ |
| `task/` | **Temporary** | **Delete after implementation complete**. Migrate important design decisions to `specification/*_design.md` before deletion |

#### Change Propagation

When an upstream document changes, downstream documents may need updates:

| Changed Document | Impact Scope | Update Condition |
|:--|:--|:--|
| `CONSTITUTION.md` | All downstream | Principle changes affect all documents |
| `requirement/` | `specification/*_spec.md`, `specification/*_design.md` | New/changed/deleted requirements must be reflected |
| `specification/*_spec.md` | `specification/*_design.md`, `task/` | API signature, data model, or behavior changes |
| `specification/*_design.md` | `task/`, Implementation | Architecture or interface changes |

**When updates are NOT needed**:

- Internal implementation optimization (no interface changes)
- Bug fixes (correcting deviations from specifications)
- Refactoring (no behavior changes)

#### Cross-Reference Rules

Documents reference each other using requirement IDs to maintain traceability:

| ID Format | Type | Example |
|:--|:--|:--|
| `UR-xxx` | User Requirements | `UR-001`: User can log in |
| `FR-xxx` | Functional Requirements | `FR-001`: Authenticate via OAuth |
| `NFR-xxx` | Non-Functional Requirements | `NFR-001`: Response time < 200ms |

**Traceability chain**:

```
requirement/ (defines UR/FR/NFR) → specification/*_spec.md (references FR/NFR) → specification/*_design.md (implements FR/NFR) → task/ (covers FR/NFR)
```

- `specification/*_spec.md` must reference PRD requirement IDs in its "Functional Requirements" section
- `specification/*_design.md` must trace design decisions back to spec requirements
- `task/` must cover all functional requirements (FR-xxx) and consider non-functional requirements (NFR-xxx)
