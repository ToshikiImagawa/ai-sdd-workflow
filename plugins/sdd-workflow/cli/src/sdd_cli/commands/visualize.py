"""Visualize command implementation."""

from pathlib import Path
from typing import Optional
from sdd_cli import get_cache_dir
from sdd_cli.indexer.db import IndexDB
from sdd_cli.visualizer.analyzer import DependencyAnalyzer
from sdd_cli.visualizer.mermaid import MermaidGenerator


def generate_visualization(
    root: Path,
    output: Path,
    filter_dir: Optional[str] = None,
    feature_id: Optional[str] = None,
):
    """Generate dependency graph visualization.

    Args:
        root: SDD root directory
        output: Output file path
        filter_dir: Filter by directory type
        feature_id: Filter by feature ID

    Raises:
        Exception: If visualization generation fails
    """
    # Check if index exists in XDG cache directory
    project_root = root.parent if root.name == ".sdd" else root
    cache_dir = get_cache_dir(project_root)
    db_path = cache_dir / "index.db"
    if not db_path.exists():
        raise ValueError(
            f"Index not found at {db_path}. Please run 'sdd-cli index' first."
        )

    # Get all documents from index
    with IndexDB(db_path) as db:
        documents = db.get_all_documents()

    if not documents:
        raise ValueError("No documents found in index.")

    # Analyze dependencies
    analyzer = DependencyAnalyzer(documents, root)
    analyzer.analyze()

    # Get filtered dependency graph
    graph = analyzer.get_dependency_graph(
        filter_dir=filter_dir,
        feature_id=feature_id,
    )

    # Generate Mermaid diagram
    generator = MermaidGenerator(graph)
    mermaid_diagram = generator.generate()

    # Write to output file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(mermaid_diagram, encoding="utf-8")
