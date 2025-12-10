---
description: "Migrate legacy AI-SDD directory structure (v1.x) to new structure (v2.0.0)."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# SDD Migrate - AI-SDD Migration

A command to migrate legacy AI-SDD directory structure (v1.x) to the new version (v2.0.0).

## Command Features

1. **Structure Detection**: Automatically detect current directory structure
2. **Migration Options**: Choose between migrating to new structure or generating compatibility config
3. **Safe Migration**: Rename via Git or generate configuration file

## Breaking Changes Overview (v1.x → v2.0.0)

| Legacy (v1.x)          | New (v2.0.0)    | Description                     |
|:-----------------------|:----------------|:--------------------------------|
| `.docs/`               | `.sdd/`         | Root directory                  |
| `requirement-diagram/` | `requirement/`  | Requirement documents directory |
| `review/`              | `task/`         | Task log directory              |
| `/review_cleanup`      | `/task_cleanup` | Cleanup command                 |

## Execution Flow

```
1. Detect current directory structure
   ├─ Does .docs/ exist?
   ├─ Does requirement-diagram/ exist?
   └─ Does review/ exist?
   ↓
2. Display detection results
   ├─ If legacy structure detected: Present migration options
   └─ If new structure or configured: Notify no migration needed
   ↓
3. Present options to user
   ├─ A: Migrate to new structure (rename directories)
   └─ B: Keep legacy structure (generate .sdd-config.json)
   ↓
4. Execute based on selection
   ├─ A: Rename directories via git mv
   └─ B: Generate .sdd-config.json
   ↓
5. Update CLAUDE.md (if necessary)
   ↓
6. Display migration completion report
```

## Option Details

### Option A: Migrate to New Structure

**Recommended**: For early-stage projects or when unified naming conventions are desired

Process:

1. `git mv .docs .sdd` to rename root directory
2. `git mv .sdd/requirement-diagram .sdd/requirement` to rename requirement directory
3. `git mv .sdd/review .sdd/task` to rename task directory
4. Update path references in CLAUDE.md
5. Commit changes

**Benefits**:

- Full compatibility with new plugin version
- Simpler document references

**Note**:

- May require updating existing references or scripts
- Tracked as rename in Git history

### Option B: Keep Legacy Structure

**Recommended**: For existing projects with many references or when avoiding breaking changes

Process:

1. Generate `.sdd-config.json` with legacy directory names
2. Plugin operates based on configuration file

**Generated configuration file example**:

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

**Benefits**:

- No changes to existing structure
- Existing references and scripts continue to work

**Note**:

- New documents will use legacy directory names
- Configuration file management required

## Detection Logic

Legacy structure is detected under these conditions:

1. **Legacy docs root**: `.docs/` exists and `.sdd/` doesn't exist
2. **Legacy requirement directory**: `{root}/requirement-diagram/` exists
3. **Legacy task directory**: `{root}/review/` exists and `{root}/task/` doesn't exist

## Output Examples

### When Legacy Structure Detected

```markdown
## AI-SDD Migration

### Detected Structure

| Item | Current Value | New Recommended Value |
|:---|:---|:---|
| Root Directory | `.docs` | `.sdd` |
| Requirement Directory | `requirement-diagram` | `requirement` |
| Task Directory | `review` | `task` |

### Migration Options

**A: Migrate to New Structure**

- Rename directories to align with new naming conventions
- Recommended: For new or early-stage projects

**B: Keep Legacy Structure**

- Generate `.sdd-config.json` to maintain current structure
- Recommended: For existing projects with many external references

Which option would you like to choose?
```

### After Migration Complete (Option A)

```markdown
## Migration Complete

### Executed Changes

- [x] Renamed `.docs/` → `.sdd/`
- [x] Renamed `requirement-diagram/` → `requirement/`
- [x] Renamed `review/` → `task/`
- [x] Updated path references in CLAUDE.md

### Next Steps

1. Review existing scripts and references, update as needed
2. Check changes with `git status`
3. Commit changes (recommended message: `[docs] Migrate to AI-SDD v2.0.0 structure`)
```

### After Migration Complete (Option B)

```markdown
## Migration Complete

### Generated Files

- [x] Created `.sdd-config.json`

### Configuration Content

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
2. Commit changes (recommended message: `[docs] Add AI-SDD compatibility config`)

```

## Error Handling

### Project Not Under Git

```

⚠️ This project is not under Git management.

If you choose Option A (directory rename),
manual backup is recommended.

Continue?

```

### Already Using New Structure

```

✅ This project is already using the new structure.

No migration needed.

Current structure:

- Root directory: .sdd
- Requirement: requirement
- Task: task

```

### .sdd-config.json Already Exists

```

ℹ️ `.sdd-config.json` already exists.

Current settings:

- root: {current value}
- directories.requirement: {current value}
- directories.task: {current value}

The plugin will operate based on this configuration.
To modify settings, manually edit `.sdd-config.json`.

```

## Commit

After migration complete:

### For Option A

```

[docs] Migrate to AI-SDD v2.0.0 structure

- Renamed .docs/ → .sdd/
- Renamed requirement-diagram/ → requirement/
- Renamed review/ → task/

```

### For Option B

```

[docs] Add AI-SDD compatibility config

- Generated .sdd-config.json
- Maintained legacy directory structure

```
