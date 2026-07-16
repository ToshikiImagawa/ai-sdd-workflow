#!/usr/bin/env python3
"""
find-design-docs.py
Find design documents and related files for /check-spec
Reduces Claude's Glob/Grep overhead by pre-scanning file structure
"""

import json
import sys
from pathlib import Path

# Shared modules live in plugins/sdd-workflow/scripts (three levels up + scripts).
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from hook_common import resolve_project_root  # noqa: E402
from env_export import rewrite_exports  # noqa: E402


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[find-design-docs] {message}", file=sys.stderr)


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(resolve_project_root())


def read_config(project_root: Path) -> dict:
    """Read .sdd-config.json (paths only)"""
    config_file = project_root / ".sdd-config.json"
    if not config_file.exists():
        print("ERROR: .sdd-config.json not found", file=sys.stderr)
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    directories = config.get("directories", {})
    return {
        "root": config.get("root", ".sdd"),
        "requirement": directories.get("requirement", "requirement"),
        "specification": directories.get("specification", "specification"),
    }


def sorted_matches(base: Path, pattern: str) -> list:
    """Return regular files under base matching pattern, sorted by path string"""
    matches = [str(p) for p in base.rglob(pattern) if p.is_file()]
    matches.sort()
    return matches


def write_lines(path: Path, lines: list) -> None:
    """Write lines to a file, one per line (mirrors `... > file`)"""
    content = "".join(f"{line}\n" for line in lines)
    path.write_text(content, encoding="utf-8")


def find_design_documents(
    specification_path: Path,
    feature_name: str,
    design_files: Path,
    spec_files: Path,
) -> None:
    """Phase 1: locate design and spec documents"""
    log("Scanning design documents...")

    if not specification_path.is_dir():
        log(f"ERROR: Specification directory not found: {specification_path}")
        sys.exit(1)

    if feature_name:
        log(f"Searching for feature: {feature_name}")

        # Try flat structure first
        flat_design = specification_path / f"{feature_name}_design.md"
        flat_spec = specification_path / f"{feature_name}_spec.md"

        # Try hierarchical structure
        hier_design = specification_path / feature_name / "index_design.md"
        hier_spec = specification_path / feature_name / "index_spec.md"

        if flat_design.is_file():
            write_lines(design_files, [str(flat_design)])
            if flat_spec.is_file():
                write_lines(spec_files, [str(flat_spec)])
            log(f"Found flat structure: {feature_name}_design.md")
        elif hier_design.is_file():
            write_lines(design_files, [str(hier_design)])
            if hier_spec.is_file():
                write_lines(spec_files, [str(hier_spec)])
            log(f"Found hierarchical structure: {feature_name}/index_design.md")
        else:
            # Search for partial matches
            design_matches = sorted_matches(
                specification_path, f"*{feature_name}*_design.md"
            )
            spec_matches = sorted_matches(
                specification_path, f"*{feature_name}*_spec.md"
            )
            write_lines(design_files, design_matches)
            write_lines(spec_files, spec_matches)

            if not design_matches:
                log(f"WARNING: No design document found for: {feature_name}")
            else:
                log(f"Found {len(design_matches)} matching design file(s)")
    else:
        # All design documents
        log("Searching for all design documents...")
        design_matches = sorted_matches(specification_path, "*_design.md")
        spec_matches = sorted_matches(specification_path, "*_spec.md")
        write_lines(design_files, design_matches)
        write_lines(spec_files, spec_matches)

        log(f"Found {len(design_matches)} design documents")
        log(f"Found {len(spec_matches)} specification documents")


def generate_mapping(design_files: Path, mapping_file: Path) -> None:
    """Phase 2: build design -> spec -> feature mapping JSON"""
    documents = []

    if design_files.exists():
        for line in design_files.read_text(encoding="utf-8").splitlines():
            design_file = line.strip()
            if not design_file:
                continue

            design_path = Path(design_file)
            # Strip the "_design.md" suffix to recover the feature name
            basename = design_path.name[: -len("_design.md")]
            dirname = design_path.parent

            spec_candidate = dirname / f"{basename}_spec.md"
            spec_file = str(spec_candidate) if spec_candidate.is_file() else ""

            documents.append(
                {
                    "design": design_file,
                    "spec": spec_file,
                    "feature_name": basename,
                }
            )

    mapping = {"design_documents": documents}
    mapping_file.write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    log("File mapping generated")


def export_env_vars(
    output_dir: Path,
    design_files: Path,
    spec_files: Path,
    mapping_file: Path,
) -> None:
    """Phase 3: export metadata to CLAUDE_ENV_FILE"""
    wrote = rewrite_exports("CHECK_SPEC_", [
        f'export CHECK_SPEC_CACHE_DIR="{output_dir}"',
        f'export CHECK_SPEC_DESIGN_FILES="{design_files}"',
        f'export CHECK_SPEC_SPEC_FILES="{spec_files}"',
        f'export CHECK_SPEC_MAPPING="{mapping_file}"',
    ])
    if wrote:
        log("Environment variables exported to CLAUDE_ENV_FILE")


def main() -> None:
    """Main execution"""
    try:
        project_root = get_project_root()
        config = read_config(project_root)

        specification_path = (
            project_root / config["root"] / config["specification"]
        )

        # Target feature name (optional argument)
        feature_name = sys.argv[1] if len(sys.argv) > 1 else ""

        output_dir = project_root / config["root"] / ".cache" / "check-spec"
        output_dir.mkdir(parents=True, exist_ok=True)

        design_files = output_dir / "design_files.txt"
        spec_files = output_dir / "spec_files.txt"
        mapping_file = output_dir / "file_mapping.json"

        find_design_documents(
            specification_path, feature_name, design_files, spec_files
        )
        generate_mapping(design_files, mapping_file)
        export_env_vars(output_dir, design_files, spec_files, mapping_file)

        log("Scan complete")
        log(f"Cache location: {output_dir}")

    except SystemExit:
        raise
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
