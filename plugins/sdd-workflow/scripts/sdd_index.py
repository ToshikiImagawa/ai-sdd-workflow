#!/usr/bin/env python3
"""sdd_index.py - Build a compressed index of .sdd/ documents.

Scans .sdd/ documents, extracts structured content (front matter, requirement
IDs, SysML relationships, data models, API signatures) into a
local SQLite database (.sdd/.cache/index.sqlite) and derives a compact table-
format index (.cache/index.md) that readers consume with a single Read instead
of raw Glob/Grep/Read over the whole tree.

Writer entry points:
- session-start hook: full rebuild via rebuild_all(project_root)
- post-tool-use hook: incremental update via update_one(project_root, rel_path)
- CLI: python3 sdd_index.py --rebuild / --update <relpath>
"""

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_common import load_sdd_paths, resolve_project_root  # noqa: E402,F401
from fm_parser import (  # noqa: E402,F401
    LIST_KEYS,
    _strip_scalar,
    parse_front_matter,
    split_front_matter,
)
from doc_walker import iter_target_files  # noqa: E402,F401

SCHEMA_VERSION = "1"


# --- path helpers ---------------------------------------------------------

def cache_dir(project_root: str, sdd_root: str) -> str:
    return str(Path(project_root) / sdd_root / ".cache")


def db_path(project_root: str, sdd_root: str) -> str:
    return str(Path(cache_dir(project_root, sdd_root)) / "index.sqlite")


def json_path(project_root: str, sdd_root: str) -> str:
    return str(Path(cache_dir(project_root, sdd_root)) / "index.json")


def md_path(project_root: str, sdd_root: str) -> str:
    return str(Path(cache_dir(project_root, sdd_root)) / "index.md")


# --- schema ---------------------------------------------------------------

def connect(db_file: str) -> sqlite3.Connection:
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _get_schema_version(conn: sqlite3.Connection) -> Optional[str]:
    try:
        row = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'"
        ).fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None


def init_schema(conn: sqlite3.Connection) -> None:
    existing = _get_schema_version(conn)
    if existing == SCHEMA_VERSION:
        return
    if existing is not None and existing != SCHEMA_VERSION:
        conn.executescript(
            "DROP TABLE IF EXISTS literals;"
            "DROP TABLE IF EXISTS data_model_fields;"
            "DROP TABLE IF EXISTS sysml_elements;"
            "DROP TABLE IF EXISTS api_signatures;"
            "DROP TABLE IF EXISTS data_models;"
            "DROP TABLE IF EXISTS sysml_relationships;"
            "DROP TABLE IF EXISTS ids;"
            "DROP TABLE IF EXISTS tags;"
            "DROP TABLE IF EXISTS dependencies;"
            "DROP TABLE IF EXISTS documents;"
            "DROP TABLE IF EXISTS meta;"
        )
    conn.executescript(f"""
        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
        INSERT OR REPLACE INTO meta VALUES('schema_version', '{SCHEMA_VERSION}');

        CREATE TABLE IF NOT EXISTS documents (
            path         TEXT PRIMARY KEY,
            content_hash TEXT,
            doc_id       TEXT,
            title        TEXT,
            type         TEXT,
            category     TEXT,
            status       TEXT,
            sdd_phase    TEXT,
            impl_status  TEXT,
            priority     TEXT,
            risk         TEXT,
            created      TEXT,
            updated      TEXT,
            mtime        REAL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_doc_id
            ON documents(doc_id) WHERE doc_id IS NOT NULL AND doc_id != '';

        CREATE TABLE IF NOT EXISTS dependencies (
            path       TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            depends_on TEXT NOT NULL,
            PRIMARY KEY (path, depends_on)
        );

        CREATE TABLE IF NOT EXISTS tags (
            path TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            tag  TEXT NOT NULL,
            PRIMARY KEY (path, tag)
        );

        CREATE TABLE IF NOT EXISTS ids (
            path    TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            req_id  TEXT NOT NULL,
            kind    TEXT NOT NULL,
            section TEXT,
            line    INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_ids_req ON ids(req_id, kind);

        CREATE TABLE IF NOT EXISTS sysml_relationships (
            path      TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            source_id TEXT NOT NULL,
            rel_type  TEXT NOT NULL,
            target_id TEXT NOT NULL,
            section   TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_sysml_src ON sysml_relationships(source_id);
        CREATE INDEX IF NOT EXISTS idx_sysml_tgt ON sysml_relationships(target_id);

        CREATE TABLE IF NOT EXISTS data_models (
            path    TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            section TEXT,
            lang    TEXT,
            body    TEXT
        );

        CREATE TABLE IF NOT EXISTS api_signatures (
            path      TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            section   TEXT,
            signature TEXT
        );

        CREATE TABLE IF NOT EXISTS sysml_elements (
            path      TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            kind      TEXT NOT NULL,
            keyword   TEXT,
            name      TEXT NOT NULL,
            req_id    TEXT,
            elem_type TEXT,
            section   TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_sysml_elem_name ON sysml_elements(name);
        CREATE INDEX IF NOT EXISTS idx_sysml_elem_req ON sysml_elements(req_id);

        CREATE TABLE IF NOT EXISTS data_model_fields (
            path          TEXT NOT NULL REFERENCES documents(path) ON DELETE CASCADE,
            model_section TEXT,
            field_name    TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_dmf_field ON data_model_fields(field_name);

    """)
    conn.commit()


# --- hashing --------------------------------------------------------------

def file_hash(abs_path: str) -> str:
    h = hashlib.sha256()
    with open(abs_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# --- front matter ---------------------------------------------------------
# Parsing lives in fm_parser (shared with the recommend-front-matter skill).
# Re-exported here so existing callers/tests keep using sdd_index.split_front_matter.


# --- body extraction ------------------------------------------------------

REQ_ID_RE = re.compile(r"\b([A-Z]{2,3}[-_]\d{3}(?:_\d{2})*)\b")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]*)\s*$")
DATA_MODEL_LANGS = {"json", "ts", "tsx", "typescript", "yaml", "yml", "sql", "python", "py"}
TABLE_ROW_ID_RE = re.compile(r"^\|\s*\**\s*([A-Z]{2,3}[-_]\d{3}(?:_\d{2})*)\s*\**\s*\|")
DEFINE_HINT_RE = re.compile(r"\bid\s*[:=]", re.IGNORECASE)
HTTP_RE = re.compile(r"\b(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)")

SYSML_REL_RE = re.compile(
    r"(\S+)\s+-\s+(deriveReqt|refine|satisfy|verify|trace|containment|copy)\s+->\s+(\S+)"
)

# SysML requirementDiagram node definitions:
#   requirement "User Login" { id: UR-001; text: ...; risk: high; verifymethod: test }
#   element component_a { type: simulation; docref: doc.md }
SYSML_NODE_RE = re.compile(
    r"(requirement|functionalRequirement|performanceRequirement|"
    r"interfaceRequirement|physicalRequirement|designConstraint|element)\s+"
    r'("[^"]*"|[^\s{]+)\s*\{([^}]*)\}',
    re.DOTALL,
)

# Data model field-name extraction (lightweight, per language).
JSON_KEY_RE = re.compile(r'"([\w][\w -]*)"\s*:')
TS_FIELD_RE = re.compile(r"^\s*(?:readonly\s+)?([A-Za-z_]\w*)\??\s*:")
YAML_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*)\s*:")
SQL_COL_RE = re.compile(r'^\s*["`]?([A-Za-z_]\w*)["`]?\s+[A-Za-z]')
PY_FIELD_RE = re.compile(r"^\s+([A-Za-z_]\w*)\s*[:=]")
SQL_NON_COLUMN = {
    "primary", "foreign", "constraint", "unique", "key", "check",
    "index", "create", "table",
}


def _clean_heading(text: str) -> str:
    text = re.sub(r"`?<(MUST|OPTIONAL|RECOMMENDED)>`?", "", text)
    return text.strip()


def extract_sections_and_scan(body: str) -> Dict[str, List[Dict[str, Any]]]:
    req_ids: Dict[str, Dict[str, Any]] = {}
    data_models: List[Dict[str, Any]] = []
    data_model_fields: List[Dict[str, Any]] = []
    api_sigs: List[Dict[str, Any]] = []
    sysml_rels: List[Dict[str, Any]] = []
    sysml_elems: List[Dict[str, Any]] = []

    section = ""
    in_fence = False
    fence_lang = ""
    fence_section = ""
    fence_lines: List[str] = []

    lines = body.splitlines()
    for idx, line in enumerate(lines, start=1):
        fence_m = FENCE_RE.match(line.strip())
        if fence_m:
            if not in_fence:
                in_fence = True
                fence_lang = fence_m.group(1).lower()
                fence_section = section
                fence_lines = []
            else:
                block = "\n".join(fence_lines)
                if fence_lang == "mermaid":
                    _extract_sysml_relationships(
                        block, fence_section, sysml_rels
                    )
                    _extract_sysml_elements(
                        block, fence_section, sysml_elems
                    )
                elif fence_lang in DATA_MODEL_LANGS and block.strip():
                    data_models.append({
                        "section": fence_section, "lang": fence_lang,
                        "body": block,
                    })
                    for fname in _extract_data_model_fields(fence_lang, block):
                        data_model_fields.append({
                            "model_section": fence_section, "field_name": fname,
                        })
                for fl in fence_lines:
                    _collect_api(fl, fence_section, api_sigs)
                in_fence = False
                fence_lang = ""
                fence_lines = []
            continue

        if in_fence:
            fence_lines.append(line)
            _collect_req_ids(line, section, idx, req_ids)
            continue

        heading_m = HEADING_RE.match(line)
        if heading_m:
            section = _clean_heading(heading_m.group(2))
            _collect_req_ids(line, section, idx, req_ids, heading=True)
            continue

        _collect_req_ids(line, section, idx, req_ids)
        _collect_api(line, section, api_sigs)

    return {
        "req_ids": list(req_ids.values()),
        "data_models": data_models,
        "data_model_fields": data_model_fields,
        "api_signatures": api_sigs,
        "sysml_relationships": sysml_rels,
        "sysml_elements": sysml_elems,
    }


def _extract_sysml_relationships(
        block: str, section: str, acc: List[Dict[str, Any]]
) -> None:
    if "requirementDiagram" not in block:
        return
    for line in block.splitlines():
        m = SYSML_REL_RE.search(line)
        if m:
            acc.append({
                "source_id": m.group(1),
                "rel_type": m.group(2),
                "target_id": m.group(3),
                "section": section,
            })


def _extract_sysml_elements(
        block: str, section: str, acc: List[Dict[str, Any]]
) -> None:
    if "requirementDiagram" not in block:
        return
    for m in SYSML_NODE_RE.finditer(block):
        keyword = m.group(1)
        name = m.group(2).strip().strip('"')
        fields = _parse_node_body(m.group(3))
        kind = "element" if keyword == "element" else "requirement"
        acc.append({
            "kind": kind,
            "keyword": keyword,
            "name": name,
            "req_id": fields.get("id", ""),
            "elem_type": fields.get("type", ""),
            "section": section,
        })


def _parse_node_body(body: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for raw in re.split(r"[;\n]", body):
        if ":" in raw:
            key, _, value = raw.partition(":")
            key = key.strip().lower()
            if key:
                fields[key] = value.strip()
    return fields


def _extract_data_model_fields(lang: str, block: str) -> List[str]:
    fields: List[str] = []

    def add(name: str) -> None:
        if name and name not in fields:
            fields.append(name)

    if lang == "json":
        for m in JSON_KEY_RE.finditer(block):
            add(m.group(1).strip())
    elif lang in ("ts", "tsx", "typescript"):
        for ln in block.splitlines():
            m = TS_FIELD_RE.match(ln)
            if m:
                add(m.group(1))
    elif lang in ("yaml", "yml"):
        for ln in block.splitlines():
            m = YAML_KEY_RE.match(ln)
            if m:
                add(m.group(1))
    elif lang == "sql":
        for ln in block.splitlines():
            m = SQL_COL_RE.match(ln)
            if m and m.group(1).lower() not in SQL_NON_COLUMN:
                add(m.group(1))
    elif lang in ("python", "py"):
        for ln in block.splitlines():
            m = PY_FIELD_RE.match(ln)
            if m:
                add(m.group(1))
    return fields


def _collect_req_ids(line: str, section: str, line_no: int,
                     acc: Dict[str, Dict[str, Any]],
                     heading: bool = False) -> None:
    matches = REQ_ID_RE.findall(line)
    if not matches:
        return
    is_def_ctx = (
            heading
            or bool(TABLE_ROW_ID_RE.match(line.strip()))
            or bool(DEFINE_HINT_RE.search(line))
    )
    for rid in matches:
        kind = "def" if is_def_ctx else "ref"
        existing = acc.get(rid)
        if existing is None:
            acc[rid] = {"req_id": rid, "kind": kind, "section": section, "line": line_no}
        elif kind == "def" and existing["kind"] != "def":
            existing["kind"] = "def"
            existing["section"] = section
            existing["line"] = line_no


def _collect_api(line: str, section: str, acc: List[Dict[str, Any]]) -> None:
    for m in HTTP_RE.finditer(line):
        acc.append({"section": section, "signature": f"{m.group(1)} {m.group(2)}"})


# --- per-file + orchestration --------------------------------------------

def scan_document(abs_path: str, project_root: str, sdd_root: str,
                  precomputed_hash: str = "") -> Dict[str, Any]:
    rel = str(Path(abs_path).relative_to(Path(project_root) / sdd_root))
    with open(abs_path, "rb") as fb:
        raw = fb.read()
    content_hash = precomputed_hash or hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8", errors="replace")
    fm_text, body = split_front_matter(text)
    fm = parse_front_matter(fm_text)
    extracted = extract_sections_and_scan(body)
    return {
        "path": rel,
        "content_hash": content_hash,
        "doc_id": fm.get("id", ""),
        "title": fm.get("title", ""),
        "type": fm.get("type", ""),
        "category": fm.get("category", ""),
        "status": fm.get("status", ""),
        "sdd_phase": fm.get("sdd-phase", ""),
        "impl_status": fm.get("impl-status", ""),
        "priority": fm.get("priority", ""),
        "risk": fm.get("risk", ""),
        "created": fm.get("created", ""),
        "updated": fm.get("updated", ""),
        "depends_on": fm.get("depends-on", []),
        "tags": fm.get("tags", []),
        "mtime": Path(abs_path).stat().st_mtime,
        **extracted,
    }


def upsert_document(conn: sqlite3.Connection, rec: Dict[str, Any]) -> None:
    path = rec["path"]
    conn.execute("DELETE FROM documents WHERE path = ?", (path,))
    conn.execute(
        "INSERT INTO documents (path, content_hash, doc_id, title, type, category, "
        "status, sdd_phase, impl_status, priority, risk, created, updated, mtime) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (path, rec["content_hash"], rec["doc_id"], rec["title"], rec["type"],
         rec["category"], rec["status"], rec["sdd_phase"], rec["impl_status"],
         rec["priority"], rec["risk"], rec["created"], rec["updated"], rec["mtime"]),
    )
    for dep in rec["depends_on"]:
        conn.execute(
            "INSERT OR IGNORE INTO dependencies (path, depends_on) VALUES (?,?)",
            (path, dep),
        )
    for tag in rec.get("tags", []):
        conn.execute(
            "INSERT OR IGNORE INTO tags (path, tag) VALUES (?,?)",
            (path, tag),
        )
    for r in rec["req_ids"]:
        conn.execute(
            "INSERT INTO ids (path, req_id, kind, section, line) VALUES (?,?,?,?,?)",
            (path, r["req_id"], r["kind"], r["section"], r["line"]),
        )
    for sr in rec.get("sysml_relationships", []):
        conn.execute(
            "INSERT INTO sysml_relationships (path, source_id, rel_type, target_id, section) "
            "VALUES (?,?,?,?,?)",
            (path, sr["source_id"], sr["rel_type"], sr["target_id"], sr["section"]),
        )
    for d in rec["data_models"]:
        conn.execute(
            "INSERT INTO data_models (path, section, lang, body) VALUES (?,?,?,?)",
            (path, d["section"], d["lang"], d["body"]),
        )
    for f in rec.get("data_model_fields", []):
        conn.execute(
            "INSERT INTO data_model_fields (path, model_section, field_name) "
            "VALUES (?,?,?)",
            (path, f["model_section"], f["field_name"]),
        )
    for a in rec["api_signatures"]:
        conn.execute(
            "INSERT INTO api_signatures (path, section, signature) VALUES (?,?,?)",
            (path, a["section"], a["signature"]),
        )
    for se in rec.get("sysml_elements", []):
        conn.execute(
            "INSERT INTO sysml_elements "
            "(path, kind, keyword, name, req_id, elem_type, section) "
            "VALUES (?,?,?,?,?,?,?)",
            (path, se["kind"], se["keyword"], se["name"], se["req_id"],
             se["elem_type"], se["section"]),
        )


def rebuild_all(project_root: str) -> None:
    sdd_root, req_dir, spec_dir = load_sdd_paths(project_root)
    conn = connect(db_path(project_root, sdd_root))
    try:
        init_schema(conn)
        existing_hashes: Dict[str, str] = {}
        try:
            for row in conn.execute("SELECT path, content_hash FROM documents"):
                existing_hashes[row[0]] = row[1]
        except sqlite3.OperationalError:
            pass

        target_files = iter_target_files(project_root, sdd_root, req_dir, spec_dir)
        current_paths = set()
        changed = False

        for abs_path in target_files:
            try:
                rel = str(Path(abs_path).relative_to(Path(project_root) / sdd_root))
                current_paths.add(rel)
                new_hash = file_hash(abs_path)
                if existing_hashes.get(rel) == new_hash:
                    continue
                rec = scan_document(abs_path, project_root, sdd_root,
                                    precomputed_hash=new_hash)
                upsert_document(conn, rec)
                changed = True
            except OSError:
                continue

        stale = set(existing_hashes.keys()) - current_paths
        for path in stale:
            conn.execute("DELETE FROM documents WHERE path = ?", (path,))
            changed = True
        if changed or stale:
            conn.commit()

        if changed or not existing_hashes:
            derive_index(conn, project_root, sdd_root)
    finally:
        conn.close()


def update_one(project_root: str, rel_path: str) -> None:
    sdd_root, _req_dir, _spec_dir = load_sdd_paths(project_root)
    db_file = db_path(project_root, sdd_root)
    if not Path(db_file).is_file():
        return
    rel = Path(rel_path)
    sdd_rel = str(rel.relative_to(sdd_root)) if rel.is_relative_to(sdd_root) else rel_path
    abs_path = str(Path(project_root) / sdd_root / sdd_rel)

    conn = connect(db_file)
    try:
        init_schema(conn)
        if not Path(abs_path).is_file() or Path(abs_path).suffix != ".md":
            row = conn.execute(
                "SELECT 1 FROM documents WHERE path = ?", (sdd_rel,)
            ).fetchone()
            if row:
                conn.execute("DELETE FROM documents WHERE path = ?", (sdd_rel,))
                conn.commit()
                derive_index(conn, project_root, sdd_root)
            return

        new_hash = file_hash(abs_path)
        existing = conn.execute(
            "SELECT content_hash FROM documents WHERE path = ?", (sdd_rel,)
        ).fetchone()
        if existing and existing[0] == new_hash:
            return

        rec = scan_document(abs_path, project_root, sdd_root,
                            precomputed_hash=new_hash)
        upsert_document(conn, rec)
        conn.commit()
        derive_index(conn, project_root, sdd_root)
    finally:
        conn.close()


# --- derived compact index (v2: table format) -----------------------------

def _truncate_block(body: str, max_lines: int = 12) -> str:
    lines = [ln for ln in body.splitlines() if ln.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + "\n    ... (truncated)"


def derive_index(conn: sqlite3.Connection, project_root: str, sdd_root: str) -> None:
    Path(cache_dir(project_root, sdd_root)).mkdir(parents=True, exist_ok=True)

    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]

    out: List[str] = []
    out.append(f"# .sdd Index (v{SCHEMA_VERSION}, {doc_count} docs)")
    out.append("")
    out.append("Structured facts extracted from front matter and body. "
               "Read this instead of raw Glob/Grep/Read over .sdd/.")
    out.append("")

    # -- pre-fetch dependencies for reuse --
    deps_by_path: Dict[str, List[str]] = {}
    for dep_path, dep_on in conn.execute(
            "SELECT path, depends_on FROM dependencies ORDER BY path, depends_on"
    ).fetchall():
        deps_by_path.setdefault(dep_path, []).append(dep_on)

    # -- Metadata table --
    out.append("## Metadata")
    out.append("| doc_id | type | path | status | impl-status | depends-on | category |")
    out.append("|--------|------|------|--------|-------------|------------|----------|")
    rows = conn.execute(
        "SELECT path, doc_id, type, status, impl_status, category "
        "FROM documents ORDER BY path"
    ).fetchall()
    for path, doc_id, dtype, status, impl_st, category in rows:
        label = doc_id if doc_id else f"({path})"
        deps = ", ".join(deps_by_path.get(path, []))
        out.append(
            f"| {label} | {dtype or ''} | {path} | {status or ''} "
            f"| {impl_st or ''} | {deps} | {category or ''} |"
        )
    out.append("")

    # -- Requirement IDs table --
    id_rows = conn.execute(
        "SELECT i.req_id, i.kind, d.doc_id, i.path, i.section "
        "FROM ids i JOIN documents d ON i.path = d.path "
        "ORDER BY i.req_id, i.kind"
    ).fetchall()
    if id_rows:
        out.append("## Requirement IDs")
        out.append("| req_id | kind | doc_id | section |")
        out.append("|--------|------|--------|---------|")
        for req_id, kind, doc_id, path, section in id_rows:
            label = doc_id if doc_id else f"({path})"
            out.append(f"| {req_id} | {kind} | {label} | {section or ''} |")
        out.append("")

    # -- SysML Relationships table --
    sysml_rows = conn.execute(
        "SELECT s.source_id, s.rel_type, s.target_id, d.doc_id, s.path "
        "FROM sysml_relationships s JOIN documents d ON s.path = d.path "
        "ORDER BY s.source_id, s.rel_type"
    ).fetchall()
    if sysml_rows:
        out.append("## SysML Relationships")
        out.append("| source | rel | target | doc_id |")
        out.append("|--------|-----|--------|--------|")
        for src, rel, tgt, doc_id, path in sysml_rows:
            label = doc_id if doc_id else f"({path})"
            out.append(f"| {src} | {rel} | {tgt} | {label} |")
        out.append("")

    # -- SysML Elements table (requirementDiagram node definitions) --
    elem_rows = conn.execute(
        "SELECT e.name, e.kind, e.keyword, e.req_id, e.elem_type, d.doc_id, e.path, e.section "
        "FROM sysml_elements e JOIN documents d ON e.path = d.path "
        "ORDER BY e.kind, e.name"
    ).fetchall()
    if elem_rows:
        out.append("## SysML Elements")
        out.append("| name | kind | keyword | req_id | type | doc_id | section |")
        out.append("|------|------|---------|--------|------|--------|---------|")
        for name, kind, keyword, req_id, elem_type, doc_id, path, section in elem_rows:
            label = doc_id if doc_id else f"({path})"
            out.append(
                f"| {name} | {kind} | {keyword or ''} | {req_id or ''} "
                f"| {elem_type or ''} | {label} | {section or ''} |"
            )
        out.append("")

    # -- API Signatures table --
    api_rows = conn.execute(
        "SELECT DISTINCT a.signature, d.doc_id, a.path, a.section "
        "FROM api_signatures a JOIN documents d ON a.path = d.path "
        "ORDER BY a.path, a.section"
    ).fetchall()
    if api_rows:
        out.append("## API Signatures")
        out.append("| signature | doc_id | section |")
        out.append("|-----------|--------|---------|")
        for sig, doc_id, path, section in api_rows:
            label = doc_id if doc_id else f"({path})"
            out.append(f"| {sig} | {label} | {section or ''} |")
        out.append("")

    # -- Data Models (per-document, body content needs grouping) --
    dm_rows = conn.execute(
        "SELECT dm.path, d.doc_id, dm.section, dm.lang, dm.body "
        "FROM data_models dm JOIN documents d ON dm.path = d.path "
        "ORDER BY dm.path, dm.section"
    ).fetchall()
    if dm_rows:
        out.append("## Data Models")
        for path, doc_id, section, lang, body in dm_rows:
            label = doc_id if doc_id else f"({path})"
            sect = f" [{section}]" if section else ""
            out.append(f"### {label}{sect}")
            out.append(f"```{lang}")
            for ln in _truncate_block(body).splitlines():
                out.append(ln)
            out.append("```")
            out.append("")

    # -- Data Model Fields table --
    dmf_rows = conn.execute(
        "SELECT DISTINCT f.field_name, d.doc_id, f.path, f.model_section "
        "FROM data_model_fields f JOIN documents d ON f.path = d.path "
        "ORDER BY f.path, f.model_section, f.field_name"
    ).fetchall()
    if dmf_rows:
        out.append("## Data Model Fields")
        out.append("| field | doc_id | section |")
        out.append("|-------|--------|---------|")
        for field_name, doc_id, path, section in dmf_rows:
            label = doc_id if doc_id else f"({path})"
            out.append(f"| {field_name} | {label} | {section or ''} |")
        out.append("")

    # -- JSON form --
    docs_json = []
    for path, doc_id, dtype, status, impl_st, category in rows:
        d: Dict[str, Any] = {
            "path": path, "doc_id": doc_id or "", "type": dtype or "",
            "status": status or "", "impl_status": impl_st or "",
            "category": category or "",
        }
        d["depends_on"] = deps_by_path.get(path, [])
        d["req_ids"] = {
            "def": [r[0] for r in conn.execute(
                "SELECT DISTINCT req_id FROM ids WHERE path=? AND kind='def'", (path,))],
            "ref": [r[0] for r in conn.execute(
                "SELECT DISTINCT req_id FROM ids WHERE path=? AND kind='ref'", (path,))],
        }
        docs_json.append(d)

    payload = {"schema": f"sdd-index/{SCHEMA_VERSION}",
               "document_count": doc_count, "documents": docs_json}
    json_target = Path(json_path(project_root, sdd_root))
    tmp = json_target.with_name(json_target.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(json_target)

    md_target = Path(md_path(project_root, sdd_root))
    tmp_md = md_target.with_name(md_target.name + ".tmp")
    tmp_md.write_text("\n".join(out) + "\n", encoding="utf-8")
    tmp_md.replace(md_target)


# --- CLI ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build the .sdd document index.")
    parser.add_argument("--project-root", default="",
                        help="Project root (defaults to env/git/cwd)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rebuild", action="store_true", help="Full rebuild (default)")
    group.add_argument("--update", metavar="RELPATH",
                       help="Incremental update of a single file")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    if args.update:
        update_one(project_root, args.update)
    else:
        rebuild_all(project_root)


if __name__ == "__main__":
    main()
