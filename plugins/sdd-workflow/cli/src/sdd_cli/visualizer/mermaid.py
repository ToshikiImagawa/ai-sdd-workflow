"""Mermaid diagram generator for dependency graphs."""

from typing import Dict, Any, List
import re


class MermaidGenerator:
    """Generates Mermaid diagrams from dependency graphs."""

    # File type color mapping
    FILE_TYPE_COLORS = {
        "requirement": "#bbf",  # Light blue
        "spec": "#bfb",  # Light green
        "design": "#bff",  # Light cyan
        "task": "#ffb",  # Light yellow
    }

    # Edge style mapping
    EDGE_STYLES = {
        "explicit": "-->",  # Solid arrow
        "implicit": "-.->",  # Dashed arrow
        "link": "-->",  # Solid arrow
    }

    def __init__(self, graph: Dict[str, Any]):
        """Initialize generator with dependency graph.

        Args:
            graph: Dependency graph with nodes and edges
        """
        self.graph = graph
        self.node_ids = {}  # Map file_path to sanitized node ID

    def generate(self) -> str:
        """Generate Mermaid diagram.

        Returns:
            Mermaid diagram as string
        """
        lines = []
        lines.append("graph TD")
        lines.append("")

        # Add CONSTITUTION node if not filtered
        has_constitution = any(
            node["id"] == "CONSTITUTION.md" for node in self.graph["nodes"]
        )
        if not has_constitution and len(self.graph["nodes"]) > 0:
            # Add CONSTITUTION as root if there are nodes
            lines.append("    CONSTITUTION[CONSTITUTION.md]")
            lines.append("")

        # Generate node definitions
        for node in self.graph["nodes"]:
            node_def = self._generate_node_definition(node)
            lines.append(f"    {node_def}")

        lines.append("")

        # Generate edges
        edges_added = set()
        for edge in self.graph["edges"]:
            edge_def = self._generate_edge_definition(edge)
            if edge_def and edge_def not in edges_added:
                lines.append(f"    {edge_def}")
                edges_added.add(edge_def)

        # Add implicit edges from CONSTITUTION if not filtered
        if not has_constitution and len(self.graph["nodes"]) > 0:
            requirement_nodes = [
                node for node in self.graph["nodes"]
                if node.get("file_type") == "requirement"
            ]
            for node in requirement_nodes:
                node_id = self._sanitize_node_id(node["id"])
                edge_def = f"CONSTITUTION -.-> {node_id}"
                if edge_def not in edges_added:
                    lines.append(f"    {edge_def}")
                    edges_added.add(edge_def)

        lines.append("")

        # Generate styles
        for node in self.graph["nodes"]:
            style_def = self._generate_style_definition(node)
            if style_def:
                lines.append(f"    {style_def}")

        # Add CONSTITUTION style
        if not has_constitution and len(self.graph["nodes"]) > 0:
            lines.append("    style CONSTITUTION fill:#f9f,stroke:#333")

        return "\n".join(lines)

    def _sanitize_node_id(self, path: str) -> str:
        """Sanitize file path to valid Mermaid node ID.

        Args:
            path: File path

        Returns:
            Sanitized node ID
        """
        if path in self.node_ids:
            return self.node_ids[path]

        # Replace special characters
        node_id = re.sub(r"[^a-zA-Z0-9_]", "_", path)
        self.node_ids[path] = node_id
        return node_id

    def _generate_node_definition(self, node: Dict[str, Any]) -> str:
        """Generate Mermaid node definition.

        Args:
            node: Node metadata

        Returns:
            Node definition string
        """
        node_id = self._sanitize_node_id(node["id"])
        title = node.get("title", node["id"])
        file_type = node.get("file_type", "")

        # Escape special characters in title
        title = title.replace('"', '\\"')

        # Use different shapes based on file type
        if file_type == "requirement":
            return f'{node_id}["{title}"]'
        elif file_type == "spec":
            return f'{node_id}["{title}"]'
        elif file_type == "design":
            return f'{node_id}["{title}"]'
        elif file_type == "task":
            return f'{node_id}["{title}"]'
        else:
            return f'{node_id}["{title}"]'

    def _generate_edge_definition(self, edge: Dict[str, Any]) -> str:
        """Generate Mermaid edge definition.

        Args:
            edge: Edge metadata

        Returns:
            Edge definition string
        """
        source_id = self._sanitize_node_id(edge["source"])
        target_id = self._sanitize_node_id(edge["target"])
        edge_style = self.EDGE_STYLES.get(edge["type"], "-->")

        return f"{source_id} {edge_style} {target_id}"

    def _generate_style_definition(self, node: Dict[str, Any]) -> str:
        """Generate Mermaid style definition.

        Args:
            node: Node metadata

        Returns:
            Style definition string
        """
        node_id = self._sanitize_node_id(node["id"])

        # Special handling for CONSTITUTION node
        if node["id"] == "CONSTITUTION.md":
            color = "#f9f"  # Pink for CONSTITUTION
        else:
            file_type = node.get("file_type", "")
            color = self.FILE_TYPE_COLORS.get(file_type, "#ddd")

        return f"style {node_id} fill:{color},stroke:#333"
