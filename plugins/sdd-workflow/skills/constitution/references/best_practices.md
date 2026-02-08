# Constitution Best Practices

## When to Create Constitution

| Project Stage        | Recommended Action                         |
|:---------------------|:-------------------------------------------|
| **New Project**      | Create constitution in setup phase         |
| **Existing Project** | Create constitution to formalize practices |
| **Team Scaling**     | Create constitution to ensure consistency  |
| **Quality Issues**   | Create constitution to raise standards     |

## Principle Design Guidelines

**Good Principles Are**:

- Clear and unambiguous
- Enforceable (can be checked)
- Justified (has clear rationale)
- Practical (can be followed)
- Specific (not vague)

**Bad Principles Are**:

- Vague ("Write good code")
- Unenforceable ("Be creative")
- Unjustified ("Because I said so")
- Impractical ("100% coverage on everything")
- Contradictory (conflicts with other principles)

## Constitution vs. Style Guide

| Document         | Purpose                   | Examples                            |
|:-----------------|:--------------------------|:------------------------------------|
| **Constitution** | Non-negotiable principles | TDD, Spec-first, Security standards |
| **Style Guide**  | Coding conventions        | Naming, formatting, comment style   |

Both are important, but constitution takes precedence.

## Advanced Features

### Principle Templates

Common principle templates you can adapt:

**Reference**: `examples/principle_template.md`

### Constitution as Code

Export constitution to machine-readable format:

```
/constitution export --format json
```

Output: `${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/constitution.json`

For an example JSON format, see: `examples/constitution_as_code.json`

Use in CI/CD pipelines for automated validation.

## Key Recommendations

- Constitution file should be placed directly under `${SDD_ROOT}/` (`${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md`)
- Constitution is a living document, updated as team learns
- Version all changes to track evolution
- Major version changes may require code migration
- Keep principles few (3-7) and high-impact
- Too many principles = ignored principles
- Review constitution quarterly for relevance
- Constitution applies to AI-generated code too
- Use `/constitution validate` in PR checks
- Constitution violations should block merge (with explicit override process)
- Constitution changes should be made with team-wide consensus
- Always consider impact on existing specs/designs
- Explicitly state "why this principle is necessary"
- Define principles in verifiable form
- Constitution versioning follows semantic versioning
