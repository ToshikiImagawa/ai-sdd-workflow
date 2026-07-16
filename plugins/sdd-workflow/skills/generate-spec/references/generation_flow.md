# Generation Flow

```
1. Analyze input content
   |
2. Load project principles (Required)
   |- If CONSTITUTION.md exists:
   |   |- Read ${CLAUDE_PROJECT_DIR}/${SDD_ROOT}/CONSTITUTION.md using Read tool
   |   |- Understand principle categories (B-xxx, A-xxx, D-xxx, T-xxx)
   |- If not exists: Skip (note this in output)
   |
3. Vibe Coding risk assessment (skip if --ci)
   |- High: Confirm missing info with user -> Resume after response
   |- Medium: Confirm ambiguous points -> Resume after response
   |- Low: Proceed to next step
   |
4. Check existing documents
   |- If PRD exists: Pre-load and understand requirements
   |- If spec/design exists: Confirm overwrite (auto-approve if --ci)
   |
5. Generate and save abstract specification (Specify)
   |
6. Spec principle compliance check with spec-reviewer (skip if --ci)
   |- Call spec-reviewer agent (--summary option)
   |- **Target**: {feature-name}_spec.md only (Design Doc not yet generated)
   |- Check CONSTITUTION.md compliance (Architecture/Development principles focus)
   |- On violation detection: Review fix proposals and apply approved fixes (main agent)
   |- After fix, re-check
   |
6a. Front matter validation with front-matter-reviewer (skip if --ci)
   |- Call front-matter-reviewer agent
   |- **Target**: {feature-name}_spec.md
   |- On issue detection: Apply fixes (main agent)
   |
7. Confirm Design Doc generation (always generate if --ci)
   |- Technical info present: Generate and save (Plan)
   |- No technical info: Confirm whether to skip
   |
8. Design Doc principle compliance check with spec-reviewer (skip if --ci)
   |- Call spec-reviewer agent (--summary option)
   |- **Target**: {feature-name}_design.md only (Spec already checked in step 6)
   |- Check CONSTITUTION.md compliance (Technical constraints/Architecture focus)
   |- On violation detection: Review fix proposals and apply approved fixes (main agent)
   |- After fix, re-check
   |
8a. Front matter validation with front-matter-reviewer (skip if --ci)
   |- Call front-matter-reviewer agent
   |- **Target**: {feature-name}_design.md
   |- On issue detection: Apply fixes (main agent)
```
