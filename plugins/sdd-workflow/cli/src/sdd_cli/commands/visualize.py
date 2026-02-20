"""Visualize command implementation."""

import json
import re
from pathlib import Path
from typing import Optional
from sdd_cli import get_cache_dir
from sdd_cli.indexer.db import IndexDB
from sdd_cli.visualizer.analyzer import DependencyAnalyzer
from sdd_cli.visualizer.mermaid import MermaidGenerator
from sdd_cli.visualizer.server import start_server
from sdd_cli.commands.index import build_index


def generate_visualization(
    root: Path,
    output: Path,
    filter_dir: Optional[str] = None,
    feature_id: Optional[str] = None,
    html: bool = False,
    serve: bool = False,
    split_by_prd: bool = False,
):
    """Generate dependency graph visualization.

    Args:
        root: SDD root directory
        output: Output file path
        filter_dir: Filter by directory type
        feature_id: Filter by feature ID
        html: Generate HTML instead of .mmd
        serve: Start local server and open browser (requires html=True)
        split_by_prd: Split graphs by PRD existence (PRD-based vs direct from CONSTITUTION)

    Raises:
        Exception: If visualization generation fails
    """
    # Check if index exists in XDG cache directory
    project_root = root.parent if root.name == ".sdd" else root
    cache_dir = get_cache_dir(project_root)
    db_path = cache_dir / "index.db"
    if not db_path.exists():
        # Auto-generate index if it doesn't exist
        print(f"Index not found. Generating index...")
        build_index(root, quiet=False)
        print()

    # Get all documents from index
    with IndexDB(db_path) as db:
        documents = db.get_all_documents()

    if not documents:
        raise ValueError("No documents found in index.")

    # Analyze dependencies
    analyzer = DependencyAnalyzer(documents, root)
    analyzer.analyze()

    if split_by_prd:
        # Generate two separate graphs: PRD-based and direct
        prd_graph, direct_graph = analyzer.get_split_dependency_graphs(filter_dir=filter_dir)

        # Generate PRD-based graph
        _generate_graph_file(
            root, cache_dir, prd_graph,
            cache_dir / "prd-based-graph",
            "PRD-Based Dependency Graph",
            "Documents with requirements (PRD)",
            serve
        )

        # Generate direct graph
        _generate_graph_file(
            root, cache_dir, direct_graph,
            cache_dir / "direct-graph",
            "Direct Dependency Graph",
            "Documents without requirements (direct from CONSTITUTION)",
            serve
        )

        # If serve is requested, start server with split view
        if serve:
            start_server(cache_dir, "split")
    else:
        # Get filtered dependency graph
        graph = analyzer.get_dependency_graph(
            filter_dir=filter_dir,
            feature_id=feature_id,
        )

        # Generate single graph
        title = "SDD Dependency Graph"
        subtitle = "Interactive dependency graph visualization"
        if filter_dir:
            subtitle += f" (filtered by directory: {filter_dir})"
        if feature_id:
            subtitle += f" (filtered by feature: {feature_id})"

        _generate_graph_file(root, cache_dir, graph, output, title, subtitle, False)

        # Start server if requested
        if serve:
            start_server(cache_dir, output.stem)


def _generate_graph_file(
    root: Path,
    cache_dir: Path,
    graph: dict,
    output: Path,
    title: str,
    subtitle: str,
    is_split: bool,
):
    """Generate graph JSON file.

    Args:
        root: SDD root directory
        cache_dir: Cache directory
        graph: Dependency graph data
        output: Output file path
        title: Graph title
        subtitle: Graph subtitle
        is_split: Whether this is part of a split graph
    """
    # Build complete graph data with metadata
    graph_data = {
        "title": title,
        "subtitle": subtitle,
        "nodes": graph["nodes"],
        "edges": graph["edges"],
    }

    # Write graph JSON (browser will generate Mermaid code from this)
    output.parent.mkdir(parents=True, exist_ok=True)
    json_output = output.parent / f"{output.stem}.json"
    json_output.write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")
