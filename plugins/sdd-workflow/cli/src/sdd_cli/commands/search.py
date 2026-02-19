"""Search command implementation (Phase 2)."""

from pathlib import Path
from typing import Optional
from sdd_cli import get_cache_dir
from sdd_cli.indexer.db import IndexDB
import json


def search_documents(
    root: Path,
    query: Optional[str] = None,
    feature_id: Optional[str] = None,
    tag: Optional[str] = None,
    directory: Optional[str] = None,
    output_format: str = "text",
    limit: int = 10,
) -> str:
    """Search SDD documents.

    Args:
        root: SDD root directory
        query: Full-text search query
        feature_id: Filter by feature ID
        tag: Filter by tag
        directory: Filter by directory type
        output_format: Output format (text or json)
        limit: Maximum number of results

    Returns:
        Formatted search results

    Raises:
        Exception: If search fails
    """
    # Check if index exists in XDG cache directory
    project_root = root.parent if root.name == ".sdd" else root
    cache_dir = get_cache_dir(project_root)
    db_path = cache_dir / "index.db"
    if not db_path.exists():
        raise ValueError(
            f"Index not found at {db_path}. Please run 'sdd-cli index' first."
        )

    # Search database
    with IndexDB(db_path) as db:
        results = db.search(
            query=query,
            feature_id=feature_id,
            tag=tag,
            directory=directory,
            limit=limit,
        )

    # Format output
    if output_format == "json":
        return json.dumps(results, indent=2, ensure_ascii=False)
    else:
        return _format_text_results(results, query)


def _format_text_results(results: list, query: Optional[str]) -> str:
    """Format search results as text.

    Args:
        results: List of search results
        query: Original search query

    Returns:
        Formatted text output
    """
    if not results:
        return "No results found."

    lines = []
    lines.append(f"Found {len(results)} result(s)")
    if query:
        lines.append(f"Query: {query}")
    lines.append("")

    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result['title']}")
        lines.append(f"   Path: {result['file_path']}")
        lines.append(f"   Feature ID: {result['feature_id']}")

        if result.get("tags"):
            tags_str = ", ".join(result["tags"])
            lines.append(f"   Tags: {tags_str}")

        if result.get("snippet"):
            snippet = result["snippet"].replace("\n", " ")
            lines.append(f"   Snippet: {snippet}")

        lines.append("")

    return "\n".join(lines)
