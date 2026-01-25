## AI-SDD Migration

### Detected Configuration

| Item            | Current Value         | New Recommended Value |
|:----------------|:----------------------|:----------------------|
| Root Directory  | `.docs`               | `.sdd`                |
| Requirement Dir | `requirement-diagram` | `requirement`         |
| Task Directory  | `review`              | `task`                |

### Migration Options

**A: Migrate to New Configuration**

- Rename directories to new naming convention
- Recommended: New projects or early-stage projects

**B: Keep Legacy Configuration**

- Generate `.sdd-config.json` to maintain current configuration
- Recommended: Existing projects with many external references

Which option would you like to choose?

---

## Migration Complete

### Changes Executed

- [x] Renamed `.docs/` → `.sdd/`
- [x] Renamed `requirement-diagram/` → `requirement/`
- [x] Renamed `review/` → `task/`
- [x] Updated CLAUDE.md path references

### Next Steps

1. Review existing scripts and references, update as needed
2. Verify changes with `git status`

### Recommended Manual Verification

- [ ] Verify changes with `git status`
- [ ] Update if existing scripts or CI/CD pipelines reference directory paths
- [ ] Verify CLAUDE.md path references are correctly updated
- [ ] Verify links in other documents are correct

### Verification Commands

```bash
# Verify git change status
git status

# Verify directory structure
ls -la .sdd/

# Verify AI-SDD commands work correctly
/check_spec
```

---

## Migration Complete

### Generated Files

- [x] Created `.sdd-config.json`

### Configuration Contents

```json
{
  "root": ".docs",
  "directories": {
    "requirement": "requirement-diagram",
    "specification": "specification",
    "task": "review"
  }
}
```

### Next Steps

1. Add `.sdd-config.json` to version control

---

⚠️ This project is not under Git management.

If choosing Option A (directory rename),
manual backup is recommended.

Continue?

---

✅ This project is already using the new configuration.

Migration is not necessary.

Current configuration:

- Root directory: .sdd
- Requirements: requirement
- Tasks: task

---

ℹ️ `.sdd-config.json` already exists.

Current settings:

- root: {current value}
- directories.requirement: {current value}
- directories.task: {current value}

The plugin will operate based on these settings.
To change settings, manually edit `.sdd-config.json`.
