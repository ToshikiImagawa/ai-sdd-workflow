"""doc_walker.py - Shared AI-SDD document discovery.

Single source of truth for the target-selection rule that was duplicated between
sdd_index.iter_target_files and scan-documents.collect_documents:

- requirement/: every ``.md`` file
- specification/: only ``*_spec.md`` / ``*_design.md`` files (see naming.has_spec_suffix)
- task/: every ``.md`` file

Also hosts find_design_doc (used by the post-tool-use hook). All traversal is
pathlib-based for cross-platform behavior.
"""

import sys
from pathlib import Path
from typing import List, Union

# Ensure sibling shared modules resolve even when doc_walker is loaded directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from naming import has_spec_suffix  # noqa: E402

PathLike = Union[str, Path]


def iter_requirement_docs(req_path: PathLike) -> List[Path]:
    """Every ``.md`` file under a requirement directory, sorted."""
    p = Path(req_path)
    return sorted(p.rglob("*.md")) if p.is_dir() else []


def iter_specification_docs(spec_path: PathLike) -> List[Path]:
    """Only ``*_spec.md`` / ``*_design.md`` files under a specification directory, sorted."""
    p = Path(spec_path)
    if not p.is_dir():
        return []
    return sorted(f for f in p.rglob("*.md") if has_spec_suffix(f.name[:-3]))


def iter_all_markdown(path: PathLike) -> List[Path]:
    """Every ``.md`` file under a directory, sorted."""
    p = Path(path)
    return sorted(p.rglob("*.md")) if p.is_dir() else []


def iter_target_files(project_root: str, sdd_root: str,
                      req_dir: str, spec_dir: str) -> List[str]:
    """Indexer targets: requirement (all) + specification (_spec/_design), globally sorted."""
    base = Path(project_root) / sdd_root
    files = iter_requirement_docs(base / req_dir) + iter_specification_docs(base / spec_dir)
    return sorted(str(f) for f in files)


def collect_documents(sdd_dir: PathLike, requirement_dir: str,
                      specification_dir: str, task_dir: str) -> List[Path]:
    """Scan targets: requirement (all) + specification (_spec/_design) + task (all).

    Returned in section order (requirement, then specification, then task), each
    section sorted internally.
    """
    base = Path(sdd_dir)
    docs = iter_requirement_docs(base / requirement_dir)
    docs += iter_specification_docs(base / specification_dir)
    docs += iter_all_markdown(base / task_dir)
    return docs


def find_design_doc(spec_dir: PathLike, stem: str) -> str:
    """Return the path of the first ``{stem}_design.md`` under spec_dir, or ''."""
    for match in Path(spec_dir).rglob(f"{stem}_design.md"):
        return str(match)
    return ""
