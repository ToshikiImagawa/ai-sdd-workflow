"""Markdown frontmatter parser for SDD documents."""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import frontmatter


class DocumentParser:
    """Parses SDD Markdown documents and extracts metadata."""

    @staticmethod
    def parse(file_path: Path) -> Dict[str, Any]:
        """Parse a Markdown document and extract metadata.

        Args:
            file_path: Path to the Markdown file

        Returns:
            Dictionary with keys:
                - title: str (from frontmatter or first heading)
                - feature_id: str (from frontmatter or inferred from filename)
                - file_type: str (requirement/spec/design/task)
                - parent_feature_id: str or None (inferred from directory nesting)
                - tags: List[str] (from frontmatter)
                - depends_on: List[str] (from frontmatter)
                - content: str (Markdown body without code blocks)
                - links: List[str] (relative links to other documents)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            metadata = post.metadata
            content = post.content

            # Extract title
            title = DocumentParser._extract_title(metadata, content)

            # Extract or infer feature ID
            feature_id = DocumentParser._extract_feature_id(metadata, file_path)

            # Infer file type
            file_type = DocumentParser._infer_file_type(file_path)

            # Infer parent feature ID from directory nesting
            parent_feature_id = DocumentParser._infer_parent_feature_id(file_path)

            # Extract tags
            tags = DocumentParser._extract_tags(metadata)

            # Extract dependencies
            depends_on = DocumentParser._extract_dependencies(metadata)

            # Extract content (remove code blocks for better search)
            clean_content = DocumentParser._remove_code_blocks(content)

            # Extract relative links
            links = DocumentParser._extract_links(content)

            return {
                "title": title,
                "feature_id": feature_id,
                "file_type": file_type,
                "parent_feature_id": parent_feature_id,
                "tags": tags,
                "depends_on": depends_on,
                "content": clean_content,
                "links": links,
            }

        except Exception as e:
            # Return minimal metadata on error
            return {
                "title": file_path.stem,
                "feature_id": file_path.stem,
                "file_type": "unknown",
                "parent_feature_id": None,
                "tags": [],
                "depends_on": [],
                "content": "",
                "links": [],
            }

    @staticmethod
    def _extract_title(metadata: Dict[str, Any], content: str) -> str:
        """Extract title from frontmatter or first heading."""
        # First try frontmatter
        if "title" in metadata:
            return str(metadata["title"])

        # Then try first H1 heading
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return "Untitled"

    @staticmethod
    def _extract_feature_id(metadata: Dict[str, Any], file_path: Path) -> str:
        """Extract feature ID from frontmatter or infer from filename."""
        # Try frontmatter variants
        for key in ["feature-id", "feature_id", "id"]:
            if key in metadata:
                return str(metadata[key])

        # Infer from filename (remove _spec or _design suffix)
        name = file_path.stem
        name = re.sub(r"_(spec|design)$", "", name)

        # If filename is "index", use parent directory name as feature-id
        # This handles cases like: requirement/{feature-name}/index.md
        if name == "index":
            parent_name = file_path.parent.name
            # Avoid using directory names like "requirement", "specification", "task"
            if parent_name not in ["requirement", "specification", "task"]:
                return parent_name

        return name

    @staticmethod
    def _extract_tags(metadata: Dict[str, Any]) -> List[str]:
        """Extract tags from frontmatter."""
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            # Handle comma-separated string
            return [t.strip() for t in tags.split(",")]
        elif isinstance(tags, list):
            return [str(t) for t in tags]
        return []

    @staticmethod
    def _extract_dependencies(metadata: Dict[str, Any]) -> List[str]:
        """Extract dependencies from frontmatter."""
        for key in ["depends-on", "depends_on", "dependencies"]:
            if key in metadata:
                deps = metadata[key]
                if isinstance(deps, str):
                    return [d.strip() for d in deps.split(",")]
                elif isinstance(deps, list):
                    return [str(d) for d in deps]
        return []

    @staticmethod
    def _remove_code_blocks(content: str) -> str:
        """Remove code blocks from content for better search."""
        # Remove fenced code blocks
        content = re.sub(r"```[\s\S]*?```", "", content)
        # Remove inline code
        content = re.sub(r"`[^`]+`", "", content)
        return content.strip()

    @staticmethod
    def _extract_links(content: str) -> List[str]:
        """Extract relative Markdown links."""
        links = []
        # Match [text](path) format
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", content):
            link = match.group(2)
            # Only keep relative links to .md files
            if link.endswith(".md") and not link.startswith("http"):
                links.append(link)
        return links

    @staticmethod
    def _infer_file_type(file_path: Path) -> str:
        """Infer file type from file path and name.

        Args:
            file_path: Path to the file

        Returns:
            File type: 'requirement', 'spec', 'design', or 'task'
        """
        path_str = str(file_path)
        file_name = file_path.name

        # Check if file is in task directory
        if "/task/" in path_str or path_str.startswith("task/"):
            return "task"

        # Check if file ends with _design.md or is index_design.md
        if file_name.endswith("_design.md") or file_name == "index_design.md":
            return "design"

        # Check if file ends with _spec.md or is index_spec.md
        if file_name.endswith("_spec.md") or file_name == "index_spec.md":
            return "spec"

        # Check if file is in requirement directory
        if "/requirement/" in path_str or path_str.startswith("requirement/"):
            return "requirement"

        # Default fallback
        return "unknown"

    @staticmethod
    def _infer_parent_feature_id(file_path: Path) -> Optional[str]:
        """Infer parent feature ID from directory nesting.

        Args:
            file_path: Path to the file

        Returns:
            Parent feature ID or None if no parent exists

        Examples:
            requirement/auth/login/index.md → 'auth'
            requirement/user-login.md → None
            specification/auth/login/index_spec.md → 'auth'
            task/TICKET-123/index.md → None (task uses ticket ID, not feature hierarchy)
        """
        parts = file_path.parts

        # Find the base directory (requirement, specification, task)
        base_dir_index = None
        for i, part in enumerate(parts):
            if part in ["requirement", "specification", "task"]:
                base_dir_index = i
                break

        if base_dir_index is None:
            return None

        # For task directories, we don't infer parent from path
        # (ticket ID is not feature hierarchy)
        if parts[base_dir_index] == "task":
            return None

        # Calculate depth from base directory
        # Example cases:
        #   requirement/user-login.md
        #     parts = ['requirement', 'user-login.md']
        #     depth = 1 → No parent (flat structure)
        #
        #   requirement/context-display/index.md
        #     parts = ['requirement', 'context-display', 'index.md']
        #     depth = 2, is_index = True → No parent (index.md defines the feature itself)
        #
        #   requirement/context-display/context-behavior.md
        #     parts = ['requirement', 'context-display', 'context-behavior.md']
        #     depth = 2, is_index = False → parent = 'context-display'
        #
        #   requirement/auth/login/index.md
        #     parts = ['requirement', 'auth', 'login', 'index.md']
        #     depth = 3, is_index = True → parent = 'auth' (parent of the feature directory)
        depth_from_base = len(parts) - base_dir_index - 1
        is_index = file_path.name in ["index.md", "index_spec.md", "index_design.md"]

        # If depth >= 2, there's at least one directory between base and file
        if depth_from_base >= 2:
            if is_index:
                # index.md defines the feature itself, so parent is one level up
                # Example: requirement/auth/login/index.md → parent = 'auth'
                if depth_from_base >= 3:
                    # Multi-level nesting: parent is two directories up
                    parent_dir = parts[base_dir_index + depth_from_base - 2]
                    return parent_dir
                else:
                    # Single-level nesting: no parent (index.md defines top-level feature)
                    return None
            else:
                # Non-index file: parent is the immediate parent directory
                # Example: requirement/context-display/context-behavior.md → parent = 'context-display'
                parent_dir = parts[base_dir_index + depth_from_base - 1]
                return parent_dir

        # Flat structure (file directly under base directory)
        return None
