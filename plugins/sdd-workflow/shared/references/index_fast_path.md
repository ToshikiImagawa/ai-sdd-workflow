# Index Fast Path (shared)

Common contract for the agents and skills that read the `.sdd/` compressed index instead of scanning documents
one by one. Each caller keeps only what is specific to it: **which index tables it uses**, **when it falls
back to a raw Read**, and any extra rule (named in its own `### Index Fast Path` section).

## When `SDD_INDEX` is `on`

A pre-built compressed index exists at `${SDD_ROOT}/.cache/index.md`.

1. Read it **once** (a single `Read` call). Do not re-read it or Read it in pieces during the same run.
2. Use only the tables the caller names. The tables the index can contain are `Metadata`,
   `Requirement IDs`, `SysML Relationships`, `Data Models`, `API Signatures`.
3. The index replaces the multiple Glob/Grep/Read calls over `.sdd/` that would otherwise be needed to
   discover documents, IDs and relationships.
4. Fall back to a raw Read of a **specific file** only when the caller's fall-back condition holds (typically:
   the check needs full section text that the index does not carry). Never fall back to scanning the whole tree.

## When `SDD_INDEX` is unset or `off`

Use the existing Glob/Grep/Read flow.
