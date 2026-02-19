"""Index command implementation."""

from pathlib import Path
from sdd_cli import get_cache_dir
from sdd_cli.indexer.scanner import DocumentScanner
from sdd_cli.indexer.parser import DocumentParser
from sdd_cli.indexer.db import IndexDB


def build_index(root: Path, quiet: bool = False):
    """Build document index.

    Args:
        root: SDD root directory
        quiet: Suppress output messages

    Raises:
        Exception: If indexing fails
    """
    if not root.exists():
        raise ValueError(f"SDD root directory not found: {root}")

    # Initialize scanner
    scanner = DocumentScanner(root)

    # Get all documents
    documents = scanner.scan_all()

    if not quiet:
        print(f"Found {len(documents)} documents to index...")

    # Initialize database using XDG cache directory
    # Project root is used to generate unique hash for multi-project support
    project_root = root.parent if root.name == ".sdd" else root
    cache_dir = get_cache_dir(project_root)
    db_path = cache_dir / "index.db"

    with IndexDB(db_path) as db:
        # Clear existing index
        db.clear()

        # Index each document
        indexed_count = 0
        for doc_info in documents:
            try:
                # Parse document
                parsed_data = DocumentParser.parse(doc_info["full_path"])

                # Index document
                db.index_document(doc_info, parsed_data)

                indexed_count += 1

                if not quiet and indexed_count % 10 == 0:
                    print(f"  Indexed {indexed_count}/{len(documents)} documents...")

            except Exception as e:
                if not quiet:
                    print(f"  Warning: Failed to index {doc_info['file_path']}: {e}")

        if not quiet:
            print(f"Indexed {indexed_count}/{len(documents)} documents")

    # Save metadata
    import json
    import datetime

    metadata = {
        "indexed_at": datetime.datetime.now().isoformat(),
        "document_count": indexed_count,
        "root": str(root),
    }

    metadata_path = cache_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
