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
            # Try flat file structure first
            spec_path = f"specification/{feature_id}_spec.md"
            if self._document_exists(spec_path):
                deps.append(spec_path)
            else:
                # Try hierarchical structure: specification/{feature_id}/index_spec.md
                spec_path_hierarchical = f"specification/{feature_id}/index_spec.md"
                if self._document_exists(spec_path_hierarchical):
                    deps.append(spec_path_hierarchical)

        # Pattern 2: *_spec → *_design
        elif file_path.endswith("_spec.md"):
            # Try flat file structure first
            design_path = file_path.replace("_spec.md", "_design.md")
            if self._document_exists(design_path):
                deps.append(design_path)
            else:
                # Try hierarchical structure: index_spec.md → index_design.md (same directory)
                if file_path.endswith("/index_spec.md"):
                    design_path_hierarchical = file_path.replace("/index_spec.md", "/index_design.md")
                    if self._document_exists(design_path_hierarchical):
                        deps.append(design_path_hierarchical)

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

    def get_split_dependency_graphs(
        self,
        filter_dir: str = None,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Get dependency graphs split by PRD existence.

        Args:
            filter_dir: Filter by directory type

        Returns:
            Tuple of (prd_based_graph, direct_graph) where:
                - prd_based_graph: Documents with requirements (PRD)
                - direct_graph: Documents without requirements (direct from CONSTITUTION)
        """
        # Filter documents
        filtered_docs = self.documents
        if filter_dir:
            filtered_docs = [d for d in filtered_docs if d["directory"] == filter_dir]

        # Separate documents by PRD existence
        prd_based_docs = []
        direct_docs = []

        # First pass: classify requirements and specs
        spec_classification = {}  # feature_id -> "prd" or "direct"

        for doc in filtered_docs:
            file_path = doc["file_path"]
            feature_id = doc.get("feature_id", "")

            if doc["directory"] == "requirement":
                # All requirements go to PRD-based graph
                prd_based_docs.append(doc)
            elif doc["directory"] == "specification":
                # Spec docs: check if corresponding requirement exists
                if file_path.endswith("_spec.md") or file_path.endswith("/index_spec.md"):
                    has_requirement = self._has_requirement(feature_id)
                    if has_requirement:
                        # Has requirement → PRD-based graph
                        prd_based_docs.append(doc)
                        spec_classification[feature_id] = "prd"
                    else:
                        # No requirement → Direct graph (from CONSTITUTION)
                        direct_docs.append(doc)
                        spec_classification[feature_id] = "direct"
            elif doc["directory"] == "task":
                # Task docs: check if corresponding requirement exists
                has_requirement = self._has_requirement(feature_id)
                if has_requirement:
                    prd_based_docs.append(doc)
                else:
                    direct_docs.append(doc)

        # Second pass: classify design docs based on their spec's classification
        for doc in filtered_docs:
            file_path = doc["file_path"]
            feature_id = doc.get("feature_id", "")

            if doc["directory"] == "specification":
                # Design docs: follow their spec's classification
                if file_path.endswith("_design.md") or file_path.endswith("/index_design.md"):
                    # Check if we classified the corresponding spec
                    if feature_id in spec_classification:
                        if spec_classification[feature_id] == "prd":
                            prd_based_docs.append(doc)
                        else:
                            direct_docs.append(doc)
                    else:
                        # No spec found, check if spec exists at all
                        has_spec = self._has_spec(feature_id)
                        if has_spec:
                            # Spec exists but wasn't classified (shouldn't happen)
                            prd_based_docs.append(doc)
                        else:
                            # No spec → Direct graph (from CONSTITUTION)
                            direct_docs.append(doc)

        # Build PRD-based graph
        prd_graph = self._build_graph_from_docs(prd_based_docs, include_constitution=True)

        # Add CONSTITUTION dependencies for PRD-based graph
        for doc in prd_based_docs:
            if doc["directory"] == "requirement":
                # Add CONSTITUTION → requirement dependency
                prd_graph["edges"].append({
                    "source": "CONSTITUTION.md",
                    "target": doc["file_path"],
                    "type": "implicit",
                })

        # Build direct graph (CONSTITUTION → specs without PRD)
        direct_graph = self._build_graph_from_docs(direct_docs, include_constitution=True)

        # Add CONSTITUTION dependencies for direct graph
        for doc in direct_docs:
            file_path = doc["file_path"]
            if doc["directory"] == "specification":
                # Only add CONSTITUTION → spec dependency (not design)
                if file_path.endswith("_spec.md") or file_path.endswith("/index_spec.md"):
                    direct_graph["edges"].append({
                        "source": "CONSTITUTION.md",
                        "target": file_path,
                        "type": "implicit",
                    })

        return prd_graph, direct_graph

    def _has_requirement(self, feature_id: str) -> bool:
        """Check if a feature has a corresponding requirement document.

        Args:
            feature_id: Feature ID to check

        Returns:
            True if requirement exists
        """
        for doc in self.documents:
            if doc["directory"] == "requirement" and doc.get("feature_id") == feature_id:
                return True
        return False

    def _has_spec(self, feature_id: str) -> bool:
        """Check if a feature has a corresponding spec document.

        Args:
            feature_id: Feature ID to check

        Returns:
            True if spec exists
        """
        for doc in self.documents:
            file_path = doc["file_path"]
            if (doc["directory"] == "specification" and
                doc.get("feature_id") == feature_id and
                (file_path.endswith("_spec.md") or file_path.endswith("/index_spec.md"))):
                return True
        return False

    def _build_graph_from_docs(
        self,
        docs: List[Dict[str, Any]],
        include_constitution: bool = False,
    ) -> Dict[str, Any]:
        """Build graph from filtered documents.

        Args:
            docs: List of document metadata
            include_constitution: Whether to include CONSTITUTION node

        Returns:
            Dictionary with nodes and edges
        """
        if not docs:
            return {"nodes": [], "edges": []}

        # Extract filtered paths
        filtered_paths = {doc["file_path"] for doc in docs}

        # Add CONSTITUTION if requested
        if include_constitution:
            filtered_paths.add("CONSTITUTION.md")

        # Filter dependencies
        filtered_deps = [
            (src, tgt, link_type)
            for src, tgt, link_type in self.dependencies
            if src in filtered_paths and tgt in filtered_paths
        ]

        # Build graph
        nodes = []
        for doc in docs:
            nodes.append({
                "id": doc["file_path"],
                "title": doc.get("title", doc["file_name"]),
                "directory": doc["directory"],
                "feature_id": doc.get("feature_id", ""),
            })

        # Add CONSTITUTION node if requested
        if include_constitution:
            nodes.insert(0, {
                "id": "CONSTITUTION.md",
                "title": "CONSTITUTION.md",
                "directory": "",
                "feature_id": "",
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
