"""Cache management command implementation."""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


def get_cache_base() -> Path:
    """Get the base cache directory."""
    return Path.home() / ".cache" / "sdd-cli"


def list_cache_projects() -> List[Dict]:
    """List all cached projects.

    Returns:
        List of project information dictionaries
    """
    cache_base = get_cache_base()

    if not cache_base.exists():
        return []

    projects = []

    for cache_dir in cache_base.iterdir():
        if not cache_dir.is_dir():
            continue

        # Parse directory name: {project-name}.{hash}
        dir_name = cache_dir.name
        if "." not in dir_name:
            continue

        project_name, project_hash = dir_name.rsplit(".", 1)

        # Get metadata
        metadata_file = cache_dir / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass

        # Calculate size
        total_size = sum(
            f.stat().st_size for f in cache_dir.rglob("*") if f.is_file()
        )

        # Get last modified time
        mtime = cache_dir.stat().st_mtime
        last_modified = datetime.fromtimestamp(mtime)

        projects.append({
            "name": project_name,
            "hash": project_hash,
            "directory": str(cache_dir),
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "last_modified": last_modified.isoformat(),
            "document_count": metadata.get("document_count", 0),
            "indexed_at": metadata.get("indexed_at", ""),
            "project_root": metadata.get("root", ""),
        })

    # Sort by last modified (newest first)
    projects.sort(key=lambda p: p["last_modified"], reverse=True)

    return projects


def format_cache_list(projects: List[Dict]) -> str:
    """Format cache list as text.

    Args:
        projects: List of project information

    Returns:
        Formatted text output
    """
    if not projects:
        return "No cached projects found."

    lines = []
    lines.append(f"Found {len(projects)} cached project(s)\n")

    total_size = sum(p["size_bytes"] for p in projects)
    lines.append(f"Total cache size: {round(total_size / (1024 * 1024), 2)} MB\n")

    for i, proj in enumerate(projects, 1):
        lines.append(f"{i}. {proj['name']}.{proj['hash']}")
        lines.append(f"   Size: {proj['size_mb']} MB")
        lines.append(f"   Documents: {proj['document_count']}")
        lines.append(f"   Last modified: {proj['last_modified']}")
        if proj.get("project_root"):
            lines.append(f"   Project root: {proj['project_root']}")
        lines.append("")

    return "\n".join(lines)


def clean_cache(
    project_pattern: Optional[str] = None,
    all_projects: bool = False,
    dry_run: bool = False
) -> str:
    """Clean cache directories.

    Args:
        project_pattern: Project name pattern to match (supports wildcards)
        all_projects: Delete all cached projects
        dry_run: Show what would be deleted without actually deleting

    Returns:
        Result message
    """
    cache_base = get_cache_base()

    if not cache_base.exists():
        return "No cache directory found."

    projects = list_cache_projects()

    if not projects:
        return "No cached projects found."

    # Filter projects to delete
    to_delete = []

    if all_projects:
        to_delete = projects
    elif project_pattern:
        import fnmatch
        for proj in projects:
            if fnmatch.fnmatch(proj["name"], project_pattern):
                to_delete.append(proj)
    else:
        return "Please specify --all or --project <pattern>"

    if not to_delete:
        return f"No projects matching '{project_pattern}' found."

    # Execute deletion
    deleted_count = 0
    deleted_size = 0
    errors = []

    for proj in to_delete:
        cache_dir = Path(proj["directory"])

        if dry_run:
            print(f"[DRY RUN] Would delete: {proj['name']}.{proj['hash']} ({proj['size_mb']} MB)")
            deleted_count += 1
            deleted_size += proj["size_bytes"]
        else:
            try:
                shutil.rmtree(cache_dir)
                print(f"✓ Deleted: {proj['name']}.{proj['hash']} ({proj['size_mb']} MB)")
                deleted_count += 1
                deleted_size += proj["size_bytes"]
            except Exception as e:
                errors.append(f"Failed to delete {proj['name']}.{proj['hash']}: {e}")

    # Summary
    summary = []
    if dry_run:
        summary.append(f"\n[DRY RUN] Would delete {deleted_count} project(s)")
    else:
        summary.append(f"\n✓ Deleted {deleted_count} project(s)")

    summary.append(f"Freed {round(deleted_size / (1024 * 1024), 2)} MB")

    if errors:
        summary.append("\nErrors:")
        summary.extend(f"  - {err}" for err in errors)

    return "\n".join(summary)
