#!/usr/bin/env python3
"""
find-implementation-files.py
Find implementation files related to feature
Usage: find-implementation-files.py <feature-name> [scope-dir]

Ports find-implementation-files.sh to Python (find/grep free) for
cross-platform support. Behavior, cache placement, and JSON output are
kept identical to the original shell script.
"""

import fnmatch
import json
import os
import re
import sys
from pathlib import Path

# Directories excluded during the filename search (Step 1). Mirrors the
# `! -path "*/<name>/*"` predicates of the original `find` invocation.
NAME_EXCLUDE_SEGMENTS = (
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    "coverage",
    ".cache",
)

# Directories excluded during the content search (Step 2). Mirrors grep's
# --exclude-dir options.
CONTENT_EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    "coverage",
    ".cache",
}

# File name globs excluded during the content search. Mirrors grep's
# --exclude options.
CONTENT_EXCLUDE_FILES = ("*.min.js", "*.min.css", "*.map")

# Common source directories searched for content when no scope is given.
DEFAULT_CONTENT_DIRS = ("src", "lib", "app", "components", "services", "modules")

TEST_FILE_RE = re.compile(r"\.(test|spec)\.(ts|tsx|js|jsx|py)$")
CONFIG_FILE_RE = re.compile(r"\.(json|yml|yaml|toml|lock)$")


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[find-implementation-files] {message}", file=sys.stderr)


def find_by_name(search_dir: str, feature_name: str, name_exclude_substrings) -> list:
    """Step 1: match files whose name contains the feature name.

    Equivalent to `find <search_dir> -type f -name "*<feature>*"` with the
    excluded-path predicates applied.
    """
    results = []
    for dirpath, dirnames, filenames in os.walk(search_dir):
        # Prune excluded directories in-place for efficiency.
        dirnames[:] = [d for d in dirnames if d not in NAME_EXCLUDE_SEGMENTS]
        for filename in filenames:
            if feature_name not in filename:
                continue
            full_path = os.path.join(dirpath, filename)
            if any(sub in full_path for sub in name_exclude_substrings):
                continue
            results.append(full_path)
    return results


def find_by_content(content_dir: str, feature_lower: str) -> list:
    """Step 2: match files whose content contains the feature name.

    Equivalent to `grep -ril <feature> <content_dir>` with grep's
    --exclude-dir / --exclude options applied. Matching is a case-insensitive
    literal substring search.
    """
    results = []
    for dirpath, dirnames, filenames in os.walk(content_dir):
        dirnames[:] = [d for d in dirnames if d not in CONTENT_EXCLUDE_DIRS]
        for filename in filenames:
            if any(fnmatch.fnmatch(filename, pat) for pat in CONTENT_EXCLUDE_FILES):
                continue
            full_path = os.path.join(dirpath, filename)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue
            if feature_lower in content.lower():
                results.append(full_path)
    return results


def categorize(files: list):
    """Step 4: separate files into implementation / test / config buckets."""
    impl_files = []
    test_files = []
    config_files = []
    for file in files:
        if (
            TEST_FILE_RE.search(file)
            or "/__tests__/" in file
            or re.search(r"/tests?/", file)
        ):
            test_files.append(file)
        elif (
            CONFIG_FILE_RE.search(file)
            or file.endswith("package.json")
            or file.endswith("tsconfig.json")
        ):
            config_files.append(file)
        else:
            impl_files.append(file)
    return impl_files, test_files, config_files


def write_lines(path: Path, lines: list) -> None:
    """Write one entry per line (each terminated by a newline)."""
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")


def main() -> None:
    """Main execution"""
    if len(sys.argv) < 2 or not sys.argv[1]:
        log("ERROR: feature-name required")
        sys.exit(1)

    feature_name = sys.argv[1]
    scope_dir = sys.argv[2] if len(sys.argv) > 2 else ""

    # Environment variables
    sdd_root = os.environ.get("SDD_ROOT", ".sdd")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    search_dir = project_dir

    if scope_dir:
        search_dir = f"{project_dir}/{scope_dir}"
        log(f"Limiting search to: {scope_dir}")
    else:
        log("Searching entire project (excluding common directories)")

    # Create cache directory
    cache_dir = Path(project_dir) / sdd_root / ".cache" / "plan-refactor"
    cache_dir.mkdir(parents=True, exist_ok=True)

    log(f"Searching for: {feature_name}")

    # Path-exclusion substrings for Step 1 (mirrors find's -path predicates).
    name_exclude_substrings = [f"/{seg}/" for seg in NAME_EXCLUDE_SEGMENTS]
    name_exclude_substrings.append(f"/{sdd_root}/")

    # Step 1: File name matching (fast)
    log("Step 1: Filename matching...")
    files_by_name = find_by_name(search_dir, feature_name, name_exclude_substrings)
    write_lines(cache_dir / "files-by-name.txt", files_by_name)
    file_by_name_count = len(files_by_name)
    log(f"  Found {file_by_name_count} files by name")

    # Step 2: File content matching (slower, limited to source directories)
    log("Step 2: Content matching...")

    if not scope_dir:
        # Default: search only common source directories
        content_search_dirs = [
            f"{project_dir}/{d}"
            for d in DEFAULT_CONTENT_DIRS
            if Path(f"{project_dir}/{d}").is_dir()
        ]
        if not content_search_dirs:
            # Fallback: search entire project if no common directories found
            content_search_dirs = [project_dir]
    else:
        content_search_dirs = [search_dir]

    feature_lower = feature_name.lower()
    files_by_content = []
    for content_dir in content_search_dirs:
        if Path(content_dir).is_dir():
            log(f"  Searching in: {content_dir}")
            files_by_content.extend(find_by_content(content_dir, feature_lower))

    write_lines(cache_dir / "files-by-content.txt", files_by_content)
    file_by_content_count = len(files_by_content)
    log(f"  Found {file_by_content_count} files by content")

    # Step 3: Merge and deduplicate
    all_files = sorted(set(files_by_name) | set(files_by_content))
    write_lines(cache_dir / "all-files.txt", all_files)
    file_count = len(all_files)

    # Step 4: Separate by file type
    impl_files, test_files, config_files = categorize(all_files)
    write_lines(cache_dir / "implementation-files.txt", impl_files)
    write_lines(cache_dir / "test-files.txt", test_files)
    write_lines(cache_dir / "config-files.txt", config_files)

    impl_count = len(impl_files)
    test_count = len(test_files)
    config_count = len(config_files)

    # Output JSON
    result = {
        "feature_name": feature_name,
        "file_count": file_count,
        "implementation_count": impl_count,
        "test_count": test_count,
        "config_count": config_count,
        "scope_dir": scope_dir if scope_dir else "all",
        "files_list_path": f"{cache_dir}/all-files.txt",
        "implementation_list_path": f"{cache_dir}/implementation-files.txt",
        "test_list_path": f"{cache_dir}/test-files.txt",
        "config_list_path": f"{cache_dir}/config-files.txt",
        "files_by_name_count": file_by_name_count,
        "files_by_content_count": file_by_content_count,
    }
    output_path = cache_dir / "implementation-files.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n")

    log(f"Results saved to: {output_path}")
    log(f"Total: {file_count} files")
    log(f"  Implementation: {impl_count}")
    log(f"  Tests: {test_count}")
    log(f"  Config: {config_count}")

    # Warning if too many files
    if file_count > 20:
        log(
            f"⚠ WARNING: {file_count} files found. "
            "Consider narrowing scope with --scope argument."
        )


if __name__ == "__main__":
    main()
