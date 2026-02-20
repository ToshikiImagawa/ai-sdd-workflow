"""SDD CLI - AI-SDD Workflow Document Management Tool."""

import hashlib
from pathlib import Path

__version__ = "0.1.0"


def get_project_hash(project_root: Path) -> str:
    """Generate a unique hash for the project based on its absolute path.

    Args:
        project_root: Absolute path to the project root

    Returns:
        8-character hexadecimal hash
    """
    abs_path = project_root.resolve().as_posix()
    return hashlib.sha256(abs_path.encode()).hexdigest()[:8]


def get_cache_dir(project_root: Path) -> Path:
    """Get the cache directory for the given project.

    Uses XDG Base Directory specification with GitHub Copilot-style naming:
    ~/.cache/sdd-cli/{project-name}.{short-hash}/

    This provides:
    - Human-readable project identification
    - Easy cleanup of unused projects
    - Collision avoidance via hash suffix

    Args:
        project_root: Path to the project root (will be resolved to absolute)

    Returns:
        Path to the cache directory (created if it doesn't exist)
    """
    cache_base = Path.home() / ".cache" / "sdd-cli"

    # Resolve to absolute path first
    abs_project_root = project_root.resolve()
    project_name = abs_project_root.name
    project_hash = get_project_hash(abs_project_root)

    # Format: {project-name}.{8-char-hash}
    cache_dir = cache_base / f"{project_name}.{project_hash}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
