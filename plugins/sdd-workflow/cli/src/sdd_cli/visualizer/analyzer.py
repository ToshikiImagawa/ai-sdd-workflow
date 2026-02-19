"""Dependency analyzer for SDD documents."""

import re
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple


class DependencyAnalyzer:
    """Analyzes dependencies between SDD documents."""

    def __init__(self, documents: List[Dict[str, Any]], root: Path):
        """Initialize analyzer with document list.

        Args:
            documents: List of document metadata from IndexDB
            root: SDD root directory
        """
        self.documents = documents
        self.root = root
        self.dependencies = []

    def analyze(self) -> List[Tuple[str, str, str]]:
        """Analyze all dependencies.

        Returns:
            List of (source, target, link_type) tuples where:
                - source: Source document path
                - target: Target document path
                - link_type: Type of dependency (explicit/implicit/link)
        """
        self.dependencies = []

        for doc in self.documents:
            file_path = doc["file_path"]

            # 1. Explicit dependencies from frontmatter
            if doc.get("depends_on"):
                for dep in doc["depends_on"]:
                    target = self._resolve_feature_id_to_path(dep)
                    if target:
                        self.dependencies.append((file_path, target, "explicit"))

            # 2. Implicit dependencies based on naming convention
            implicit_deps = self._infer_implicit_dependencies(doc)
            for target in implicit_deps:
                self.dependencies.append((file_path, target, "implicit"))

            # 3. Dependencies from markdown links
            if doc.get("links"):
                for link in doc["links"]:
                    target = self._resolve_relative_link(file_path, link)
                    if target:
                        self.dependencies.append((file_path, target, "link"))

        return self.dependencies

    def _resolve_feature_id_to_path(self, feature_id: str) -> str:
        """Resolve feature ID to document path.

        Args:
            feature_id: Feature ID to resolve

        Returns:
            Document path or None if not found
        """
        for doc in self.documents:
            if doc.get("feature_id") == feature_id:
                return doc["file_path"]
        return None

    def _infer_implicit_dependencies(self, doc: Dict[str, Any]) -> List[str]:
        """Infer implicit dependencies based on naming conventions.

        Args:
            doc: Document metadata

        Returns:
            List of inferred dependency paths
        """
        deps = []
        file_path = doc["file_path"]
        feature_id = doc.get("feature_id", "")

        # Pattern 1: requirement → *_spec
        if file_path.startswith("requirement/"):
            spec_path = f"specification/{feature_id}_spec.md"
            if self._document_exists(spec_path):
                deps.append(spec_path)

        # Pattern 2: *_spec → *_design
        elif file_path.endswith("_spec.md"):
            design_path = file_path.replace("_spec.md", "_design.md")
            if self._document_exists(design_path):
                deps.append(design_path)

        # Pattern 3: *_design → task/
        elif file_path.endswith("_design.md"):
            task_prefix = f"task/{feature_id}"
            for task_doc in self.documents:
                if task_doc["file_path"].startswith(task_prefix):
                    deps.append(task_doc["file_path"])

        return deps

    def _resolve_relative_link(self, source_path: str, link: str) -> str:
        """Resolve relative markdown link to absolute path.

        Args:
            source_path: Source document path
            link: Relative link

        Returns:
            Resolved document path or None
        """
        try:
            source_dir = Path(source_path).parent
            target_path = (source_dir / link).resolve()
            rel_path = target_path.relative_to(self.root)
            rel_path_str = str(rel_path)

            if self._document_exists(rel_path_str):
                return rel_path_str
        except:
            pass

        return None

    def _document_exists(self, path: str) -> bool:
        """Check if document exists in the indexed documents.

        Args:
            path: Document path to check

        Returns:
            True if document exists
        """
        for doc in self.documents:
            if doc["file_path"] == path:
                return True
        return False

    def get_dependency_graph(
        self,
        filter_dir: str = None,
        feature_id: str = None,
    ) -> Dict[str, Any]:
        """Get dependency graph as structured data.

        Args:
            filter_dir: Filter by directory type
            feature_id: Filter by feature ID

        Returns:
            Dictionary with nodes and edges
        """
        # Filter documents
        filtered_docs = self.documents
        if filter_dir:
            filtered_docs = [d for d in filtered_docs if d["directory"] == filter_dir]
        if feature_id:
            filtered_docs = [d for d in filtered_docs if d.get("feature_id") == feature_id]

        # Extract filtered paths
        filtered_paths = {doc["file_path"] for doc in filtered_docs}

        # Filter dependencies
        filtered_deps = [
            (src, tgt, link_type)
            for src, tgt, link_type in self.dependencies
            if src in filtered_paths and tgt in filtered_paths
        ]

        # Build graph
        nodes = []
        for doc in filtered_docs:
            nodes.append({
                "id": doc["file_path"],
                "title": doc.get("title", doc["file_name"]),
                "directory": doc["directory"],
                "feature_id": doc.get("feature_id", ""),
            })

        edges = []
        for src, tgt, link_type in filtered_deps:
            edges.append({
                "source": src,
                "target": tgt,
                "type": link_type,
            })

        return {
            "nodes": nodes,
            "edges": edges,
        }
