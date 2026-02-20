"""SQLite FTS5 index manager for SDD documents."""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class IndexDB:
    """Manages SQLite FTS5 index for document search."""

    def __init__(self, db_path: Path):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create FTS5 table and metadata table."""
        cursor = self.conn.cursor()

        # Create FTS5 virtual table for full-text search
        # Use trigram tokenizer for better Japanese support
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                file_path,
                file_name,
                directory,
                file_type,
                title,
                feature_id,
                tags,
                content,
                tokenize = 'trigram'
            )
        """)

        # Create metadata table for structured data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents_meta (
                file_path TEXT PRIMARY KEY,
                file_type TEXT,
                feature_id TEXT,
                parent_feature_id TEXT,
                tags TEXT,
                depends_on TEXT,
                links TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on feature_id for faster filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature_id
            ON documents_meta(feature_id)
        """)

        self.conn.commit()

    def clear(self):
        """Clear all indexed documents."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM documents_fts")
        cursor.execute("DELETE FROM documents_meta")
        self.conn.commit()

    def index_document(self, doc_info: Dict[str, Any], parsed_data: Dict[str, Any]):
        """Index a single document.

        Args:
            doc_info: Document info from scanner (file_path, file_name, directory)
            parsed_data: Parsed metadata from parser (title, feature_id, tags, file_type, parent_feature_id, etc.)
        """
        cursor = self.conn.cursor()

        # Prepare tags as searchable text
        tags_text = " ".join(parsed_data["tags"])

        # Insert into FTS5 table
        cursor.execute("""
            INSERT INTO documents_fts (
                file_path, file_name, directory, file_type, title,
                feature_id, tags, content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_info["file_path"],
            doc_info["file_name"],
            doc_info["directory"],
            parsed_data["file_type"],
            parsed_data["title"],
            parsed_data["feature_id"],
            tags_text,
            parsed_data["content"],
        ))

        # Insert into metadata table
        cursor.execute("""
            INSERT OR REPLACE INTO documents_meta (
                file_path, file_type, feature_id, parent_feature_id, tags, depends_on, links
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_info["file_path"],
            parsed_data["file_type"],
            parsed_data["feature_id"],
            parsed_data.get("parent_feature_id"),
            json.dumps(parsed_data["tags"]),
            json.dumps(parsed_data["depends_on"]),
            json.dumps(parsed_data["links"]),
        ))

        self.conn.commit()

    def search(
        self,
        query: Optional[str] = None,
        feature_id: Optional[str] = None,
        tag: Optional[str] = None,
        directory: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search indexed documents.

        Args:
            query: Full-text search query
            feature_id: Filter by feature ID
            tag: Filter by tag
            directory: Filter by directory type
            limit: Maximum number of results

        Returns:
            List of matching documents with metadata
        """
        cursor = self.conn.cursor()

        # Build query
        conditions = []
        params = []

        if query:
            # FTS5 search
            sql = """
                SELECT
                    fts.file_path,
                    fts.file_name,
                    fts.directory,
                    fts.file_type,
                    fts.title,
                    fts.feature_id,
                    meta.parent_feature_id,
                    meta.tags,
                    snippet(documents_fts, 7, '...', '...', '', 50) as snippet,
                    rank
                FROM documents_fts fts
                LEFT JOIN documents_meta meta ON fts.file_path = meta.file_path
                WHERE documents_fts MATCH ?
            """
            params.append(query)
        else:
            # Non-FTS search
            sql = """
                SELECT
                    fts.file_path,
                    fts.file_name,
                    fts.directory,
                    fts.file_type,
                    fts.title,
                    fts.feature_id,
                    meta.parent_feature_id,
                    meta.tags,
                    substr(fts.content, 1, 150) as snippet
                FROM documents_fts fts
                LEFT JOIN documents_meta meta ON fts.file_path = meta.file_path
                WHERE 1=1
            """

        # Add filters
        if feature_id:
            sql += " AND fts.feature_id = ?"
            params.append(feature_id)

        if tag:
            sql += " AND fts.tags LIKE ?"
            params.append(f"%{tag}%")

        if directory:
            sql += " AND fts.directory = ?"
            params.append(directory)

        # Add ordering and limit
        if query:
            sql += " ORDER BY rank"
        else:
            sql += " ORDER BY fts.file_path"

        sql += " LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # Convert to dictionaries
        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON fields
            if result.get("tags"):
                try:
                    result["tags"] = json.loads(result["tags"])
                except:
                    result["tags"] = []
            results.append(result)

        return results

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all indexed documents with metadata.

        Returns:
            List of all documents with metadata
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                fts.file_path,
                fts.file_name,
                fts.directory,
                fts.file_type,
                fts.title,
                fts.feature_id,
                meta.parent_feature_id,
                meta.tags,
                meta.depends_on,
                meta.links
            FROM documents_fts fts
            LEFT JOIN documents_meta meta ON fts.file_path = meta.file_path
            ORDER BY fts.file_path
        """)

        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse JSON fields
            for field in ["tags", "depends_on", "links"]:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except:
                        result[field] = []
            results.append(result)

        return results

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
