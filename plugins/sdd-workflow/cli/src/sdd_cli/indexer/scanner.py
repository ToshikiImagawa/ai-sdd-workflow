"""Document scanner for SDD directories."""

import os
from pathlib import Path
from typing import List, Dict, Any


class DocumentScanner:
    """Scans SDD directory structure and collects document metadata."""

    def __init__(self, root: Path):
        """Initialize scanner with SDD root directory.

        Args:
            root: Path to SDD root directory (e.g., .sdd)
        """
        self.root = root
        self.requirement_dir = root / os.environ.get("SDD_REQUIREMENT_DIR", "requirement")
        self.specification_dir = root / os.environ.get("SDD_SPECIFICATION_DIR", "specification")
        self.task_dir = root / os.environ.get("SDD_TASK_DIR", "task")

    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan all directories and return document metadata.

        Returns:
            List of document metadata dictionaries with keys:
                - file_path: str (relative to SDD root)
                - file_name: str (without extension)
                - directory: str (requirement/specification/task)
                - full_path: Path (absolute path)
        """
        documents = []

        # Task directory: only index.md and tasks.md are managed
        _TASK_MANAGED_FILES = {"index.md", "tasks.md"}

        # Scan each directory type
        for dir_name, dir_path in [
            ("requirement", self.requirement_dir),
            ("specification", self.specification_dir),
            ("task", self.task_dir),
        ]:
            if not dir_path.exists():
                continue

            # Recursively find all .md files
            for md_file in dir_path.rglob("*.md"):
                if md_file.name.startswith("."):
                    continue  # Skip hidden files

                # Task directory: only managed files (index.md, tasks.md)
                if dir_name == "task" and md_file.name not in _TASK_MANAGED_FILES:
                    continue

                rel_path = md_file.relative_to(self.root)
                file_name = md_file.stem

                documents.append({
                    "file_path": str(rel_path),
                    "file_name": file_name,
                    "directory": dir_name,
                    "full_path": md_file,
                })

        return documents

    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Scan specific directory type.

        Args:
            directory: Directory type (requirement/specification/task)

        Returns:
            List of document metadata dictionaries
        """
        dir_map = {
            "requirement": self.requirement_dir,
            "specification": self.specification_dir,
            "task": self.task_dir,
        }

        dir_path = dir_map.get(directory)
        if not dir_path or not dir_path.exists():
            return []

        documents = []
        for md_file in dir_path.rglob("*.md"):
            if md_file.name.startswith("."):
                continue

            # Task directory: only managed files (index.md, tasks.md)
            if directory == "task" and md_file.name not in {"index.md", "tasks.md"}:
                continue

            rel_path = md_file.relative_to(self.root)
            file_name = md_file.stem

            documents.append({
                "file_path": str(rel_path),
                "file_name": file_name,
                "directory": directory,
                "full_path": md_file,
            })

        return documents
