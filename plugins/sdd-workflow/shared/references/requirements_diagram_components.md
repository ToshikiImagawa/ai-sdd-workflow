# Requirements Diagram Components

## 1. Requirement Types

| Type                     | Description               | Example                           |
|:-------------------------|:--------------------------|:----------------------------------|
| `requirement`            | General requirement       | Overall system requirements       |
| `functionalRequirement`  | Functional requirement    | Display function, operation function |
| `performanceRequirement` | Performance requirement   | Response time, throughput         |
| `interfaceRequirement`   | Interface requirement     | API design, UI components         |
| `designConstraint`       | Design constraint         | Technology stack, architecture constraints |

## 2. Attributes

- **id**: Unique identifier for requirement (e.g., `REQ_001`, `FR_001`, `PR_001`)
- **text**: Requirement description
- **risk**: Risk level (`high`, `medium`, `low`) *written in lowercase*
- **verifymethod**: Verification method (`test`, `analysis`, `demonstration`, `inspection`) *written in lowercase*

## 3. Relationships Between Requirements

| Relationship | Notation                           | Meaning                                           |
|:-------------|:-----------------------------------|:--------------------------------------------------|
| `contains`   | `Parent Req - contains -> Child Req` | Containment (parent contains child)              |
| `derives`    | `Concrete Req - derives -> Abstract Req` | Derivation (concrete requirement derives from abstract) |
| `satisfies`  | `Implementation - satisfies -> Req` | Satisfaction (implementation satisfies requirement) |
| `verifies`   | `Test Case - verifies -> Req`      | Verification (test verifies requirement)          |
| `refines`    | `Detailed Req - refines -> Req`    | Refinement (defines requirement in more detail)   |
| `traces`     | `Req A - traces -> Req B`          | Traceability (shows traceability between requirements) |

## 4. SysML Standard Relationships

Requirements diagrams describe how requirements are interrelated.

### Containment

- **Notation**: Expressed as nested structure in diagram (in Mermaid: `contains`)
- **Meaning**: When parent requirement is required, **all child requirements in containment relationship must also be realized**
- **Characteristics**: Children are typically more detailed, and a child cannot be contained by multiple parents

### Derive Dependency

- **Stereotype**: `《deriveReqt》` (SysML standard)
- **Notation**: Dotted arrow from source (concrete requirement B) to target (abstract requirement A)
- **Meaning**: One requirement (A) concretely represents another requirement (B). Changes to A affect B, but changes to B don't affect A
- **Use**: System requirements are derived from business requirements

### Tracing Relationships

**Refine Dependency - Relationship with Use Case Diagrams**

- **Stereotype**: `《refine》`
- **Connected Element**: Use Case
- **Notation**: Dashed arrow connects from use case to requirement
- **Meaning**: **Behavior** (function) to realize requirement is described in detail in use case
- **Use**: Clarify means of realizing requirement, confirm use cases are neither excessive nor insufficient

**Satisfy Dependency - Relationship with Block Definition Diagrams**

- **Stereotype**: `《satisfy》`
- **Connected Element**: Block
- **Notation**: Dashed arrow connects from block to requirement
- **Meaning**: Explicitly shows **hardware or software elements (blocks)** that realize requirement
- **Use**: Clarify scope of impact from requirement changes, verify all necessary blocks are modeled
