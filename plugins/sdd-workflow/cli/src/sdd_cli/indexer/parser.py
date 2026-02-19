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
