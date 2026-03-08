# CLI / Fallback JSON Output Specification

## Common Output Contract

Both CLI and fallback (non-CLI) paths should produce equivalent information for downstream processing.
The CLI path produces structured JSON directly; the fallback path constructs equivalent data through Glob/Grep/Read.

## Document Discovery Output

### CLI Path

```bash
sdd-cli search --dir specification --format json
```

```json
{
  "documents": [
    {
      "path": ".sdd/specification/user-auth_design.md",
      "type": "design",
      "id": "design-user-auth",
      "title": "User Authentication Design",
      "status": "approved",
      "depends_on": ["spec-user-auth"]
    },
    {
      "path": ".sdd/specification/user-auth_spec.md",
      "type": "spec",
      "id": "spec-user-auth",
      "title": "User Authentication Specification",
      "status": "approved",
      "depends_on": ["prd-user-auth"]
    }
  ],
  "total": 2
}
```

### Fallback Path (Equivalent)

Using Glob to find files, then Read to extract front matter:

```
1. Glob: ${SDD_SPECIFICATION_PATH}/**/*_design.md
2. Glob: ${SDD_SPECIFICATION_PATH}/**/*_spec.md
3. Read each file's YAML front matter
4. Construct equivalent document list
```

## Lint / Validation Output

### CLI Path

```bash
sdd-cli lint --json
```

```json
{
  "results": [
    {
      "file": ".sdd/specification/user-auth_design.md",
      "valid": true,
      "errors": [],
      "warnings": [],
      "front_matter": {
        "id": "design-user-auth",
        "type": "design",
        "status": "approved",
        "depends_on": ["spec-user-auth"]
      },
      "dependencies": {
        "upstream": ["spec-user-auth"],
        "downstream": ["task-user-auth"]
      }
    }
  ],
  "summary": {
    "total": 5,
    "valid": 5,
    "errors": 0,
    "warnings": 0
  }
}
```

### Fallback Path (Equivalent)

Using Glob/Grep/Read to manually validate:

```
1. Find all SDD documents via Glob
2. Read and parse YAML front matter from each
3. Validate required fields (id, type, status)
4. Check depends-on references resolve to existing documents
5. Report missing references as errors
```

## Feature Search Output

### CLI Path

```bash
sdd-cli search --feature-id user-auth --format json
```

```json
{
  "documents": [
    {
      "path": ".sdd/requirement/user-auth.md",
      "type": "prd",
      "id": "prd-user-auth"
    },
    {
      "path": ".sdd/specification/user-auth_spec.md",
      "type": "spec",
      "id": "spec-user-auth"
    },
    {
      "path": ".sdd/specification/user-auth_design.md",
      "type": "design",
      "id": "design-user-auth"
    },
    {
      "path": ".sdd/task/user-auth/tasks.md",
      "type": "task",
      "id": "task-user-auth"
    }
  ],
  "total": 4
}
```

### Fallback Path (Equivalent)

```
1. Glob: ${SDD_REQUIREMENT_PATH}/**/user-auth*.md
2. Glob: ${SDD_SPECIFICATION_PATH}/**/user-auth*.md
3. Glob: ${SDD_TASK_PATH}/**/user-auth*/**
4. Combine results into document list
```
