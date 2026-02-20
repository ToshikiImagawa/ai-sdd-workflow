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

            # 3. Parent-child nesting (parent → child direction)
            parent_feature_id = doc.get("parent_feature_id")
            if parent_feature_id:
                parent_doc = self._find_document_by_feature_id(
                    parent_feature_id, doc.get("file_type", "")
                )
                if parent_doc:
                    self.dependencies.append((parent_doc["file_path"], file_path, "implicit"))

            # 4. Dependencies from markdown links (task files only)
            # Task files use links to reference their parent spec/requirement docs.
            # Other file types already have implicit edges from the SDD hierarchy.
            if doc.get("file_type") == "task" and doc.get("links"):
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
        """Infer implicit dependencies based on file type and feature ID.

        Dependency flow:
            CONSTITUTION → requirement → spec → design → task

        Args:
            doc: Document metadata

        Returns:
            List of inferred dependency paths
        """
        deps = []
        file_type = doc.get("file_type", "")
        feature_id = doc.get("feature_id", "")

        # Pattern 1: requirement → spec (if spec exists)
        if file_type == "requirement":
            spec_doc = self._find_document_by_feature_id(feature_id, "spec")
            if spec_doc:
                deps.append(spec_doc["file_path"])

        # Pattern 2: spec → design (if design exists)
        elif file_type == "spec":
            design_doc = self._find_document_by_feature_id(feature_id, "design")
            if design_doc:
                deps.append(design_doc["file_path"])

        # Pattern 3: design → task (if task exists with same feature_id)
        elif file_type == "design":
            for task_doc in self.documents:
                if task_doc.get("file_type") == "task" and task_doc.get("feature_id") == feature_id:
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
        # 1. Try file-relative resolution (for ../../path/to/file.md)
        try:
            source_dir = self.root / Path(source_path).parent
            target_path = (source_dir / link).resolve()
            rel_path = target_path.relative_to(self.root)
            rel_path_str = str(rel_path)

            if self._document_exists(rel_path_str):
                return rel_path_str
        except:
            pass

        # 2. Try root-relative resolution (for backtick paths like specification/xxx.md)
        if self._document_exists(link):
            return link

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

    def _find_document_by_feature_id(self, feature_id: str, file_type: str) -> Dict[str, Any]:
        """Find document by feature ID and file type.

        Args:
            feature_id: Feature ID to search
            file_type: File type to match (requirement/spec/design/task)

        Returns:
            Document metadata or None if not found
        """
        for doc in self.documents:
            if doc.get("feature_id") == feature_id and doc.get("file_type") == file_type:
                return doc
        return None

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
        filtered_docs = self.documents
        if filter_dir:
            filtered_docs = [d for d in filtered_docs if d["directory"] == filter_dir]
        if feature_id:
            filtered_docs = [d for d in filtered_docs if d.get("feature_id") == feature_id]
        graph = self._build_graph_from_docs(filtered_docs, include_constitution=True)
        self._add_constitution_edges(graph, filtered_docs, {"requirement", "spec"})
        return graph

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
            file_type = doc.get("file_type", "")
            feature_id = doc.get("feature_id", "")

            if file_type == "requirement":
                # All requirements go to PRD-based graph
                prd_based_docs.append(doc)
            elif file_type == "spec":
                # Spec docs: check if corresponding requirement exists
                has_requirement = self._has_requirement(feature_id)
                if has_requirement:
                    # Has requirement → PRD-based graph
                    prd_based_docs.append(doc)
                    spec_classification[feature_id] = "prd"
                else:
                    # No requirement → Direct graph (from CONSTITUTION)
                    direct_docs.append(doc)
                    spec_classification[feature_id] = "direct"
            elif file_type == "task":
                # Task docs: classify based on link targets
                # If any link resolves to a requirement or PRD-classified spec, it's PRD-based
                task_is_prd = self._task_has_prd_link(doc, spec_classification)
                if task_is_prd:
                    prd_based_docs.append(doc)
                else:
                    direct_docs.append(doc)

        # Second pass: classify design docs based on their spec's classification
        for doc in filtered_docs:
            file_type = doc.get("file_type", "")
            feature_id = doc.get("feature_id", "")

            if file_type == "design":
                # Design docs: follow their spec's classification
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
        self._add_constitution_edges(prd_graph, prd_based_docs, {"requirement"})

        # Build direct graph (CONSTITUTION → specs without PRD)
        direct_graph = self._build_graph_from_docs(direct_docs, include_constitution=True)
        self._add_constitution_edges(direct_graph, direct_docs, {"spec"})

        return prd_graph, direct_graph

    def _add_constitution_edges(
        self,
        graph: Dict[str, Any],
        docs: List[Dict[str, Any]],
        file_types: Set[str],
    ) -> None:
        """Add implicit CONSTITUTION edges for top-level nodes without incoming edges.

        Args:
            graph: Graph dict to modify in-place
            docs: Documents to check
            file_types: Set of file_type values eligible for CONSTITUTION edges
        """
        # Only count implicit/explicit edges as hierarchy incoming (not task link edges)
        nodes_with_incoming = {
            edge["target"] for edge in graph["edges"]
            if edge["type"] in ("implicit", "explicit")
        }
        for doc in docs:
            if doc.get("file_type") in file_types and doc["file_path"] not in nodes_with_incoming:
                graph["edges"].append({
                    "source": "CONSTITUTION.md",
                    "target": doc["file_path"],
                    "type": "implicit",
                })

    def _has_requirement(self, feature_id: str) -> bool:
        """Check if a feature has a corresponding requirement document.

        Args:
            feature_id: Feature ID to check

        Returns:
            True if requirement exists
        """
        for doc in self.documents:
            if doc.get("file_type") == "requirement" and doc.get("feature_id") == feature_id:
                return True
        return False

    def _task_has_prd_link(self, doc: Dict[str, Any], spec_classification: Dict[str, str]) -> bool:
        """Check if a task document links to any requirement or PRD-classified document.

        Args:
            doc: Task document metadata
            spec_classification: Classification map of feature_id -> "prd"/"direct"

        Returns:
            True if any link target is a requirement or PRD-classified spec
        """
        for link in doc.get("links", []):
            resolved = self._resolve_relative_link(doc["file_path"], link)
            if not resolved:
                continue
            target_doc = next((d for d in self.documents if d["file_path"] == resolved), None)
            if not target_doc:
                continue
            if target_doc.get("file_type") == "requirement":
                return True
            if target_doc.get("feature_id") in spec_classification:
                if spec_classification[target_doc["feature_id"]] == "prd":
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
            if doc.get("file_type") == "spec" and doc.get("feature_id") == feature_id:
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
                "file_type": doc.get("file_type", ""),
                "feature_id": doc.get("feature_id", ""),
            })

        # Add CONSTITUTION node if requested
        if include_constitution:
            nodes.insert(0, {
                "id": "CONSTITUTION.md",
                "title": "CONSTITUTION.md",
                "directory": "",
                "file_type": "",
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
