#!/usr/bin/env python3
"""
scan-existing-docs.py
Scan for existing PRD/spec/design documents
Usage: scan-existing-docs.py <feature-name>

Ports scan-existing-docs.sh to Python (find/sed/jq/grep free) for
cross-platform support. Behavior, cache placement, and JSON output are
kept identical to the original shell script.
"""

import json
import os
import sys
from pathlib import Path


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[scan-existing-docs] {message}", file=sys.stderr)


def main() -> None:
    """Main execution"""
    if len(sys.argv) < 2 or not sys.argv[1]:
        log("ERROR: feature-name required")
        sys.exit(1)

    feature_name = sys.argv[1]

    # Environment variables (with defaults)
    sdd_root = os.environ.get("SDD_ROOT", ".sdd")
    sdd_requirement_dir = os.environ.get("SDD_REQUIREMENT_DIR", "requirement")
    sdd_specification_dir = os.environ.get("SDD_SPECIFICATION_DIR", "specification")
    sdd_requirement_path = os.environ.get(
        "SDD_REQUIREMENT_PATH", f"{sdd_root}/{sdd_requirement_dir}"
    )
    sdd_specification_path = os.environ.get(
        "SDD_SPECIFICATION_PATH", f"{sdd_root}/{sdd_specification_dir}"
    )
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

    project_root = Path(project_dir)
    requirement_root = project_root / sdd_requirement_path
    specification_root = project_root / sdd_specification_path

    # Create cache directory
    cache_dir = project_root / sdd_root / ".cache" / "plan-refactor"
    cache_dir.mkdir(parents=True, exist_ok=True)

    log(f"Scanning for: {feature_name}")
    log(f"SDD_ROOT: {sdd_root}")
    log(f"SDD_REQUIREMENT_PATH: {sdd_requirement_path}")
    log(f"SDD_SPECIFICATION_PATH: {sdd_specification_path}")

    # Initialize results
    prd_exists = False
    spec_exists = False
    design_exists = False
    prd_path = ""
    spec_path = ""
    design_path = ""
    structure = "none"

    # Check flat structure
    flat_prd = requirement_root / f"{feature_name}.md"
    flat_spec = specification_root / f"{feature_name}_spec.md"
    flat_design = specification_root / f"{feature_name}_design.md"

    log("Checking flat structure...")
    log(f"  PRD: {flat_prd}")
    log(f"  Spec: {flat_spec}")
    log(f"  Design: {flat_design}")

    if flat_prd.is_file() or flat_spec.is_file() or flat_design.is_file():
        structure = "flat"
        if flat_prd.is_file():
            prd_exists = True
            prd_path = str(flat_prd)
            log(f"  ✓ PRD found: {flat_prd}")
        if flat_spec.is_file():
            spec_exists = True
            spec_path = str(flat_spec)
            log(f"  ✓ Spec found: {flat_spec}")
        if flat_design.is_file():
            design_exists = True
            design_path = str(flat_design)
            log(f"  ✓ Design found: {flat_design}")

    # Check hierarchical structure (if feature-name contains '/')
    if "/" in feature_name:
        parent_feature = feature_name.rsplit("/", 1)[0]
        child_feature = feature_name.rsplit("/", 1)[1]

        log("Checking hierarchical structure...")
        log(f"  Parent: {parent_feature}, Child: {child_feature}")

        # Check child feature documents
        hier_prd = requirement_root / parent_feature / f"{child_feature}.md"
        hier_spec = specification_root / parent_feature / f"{child_feature}_spec.md"
        hier_design = specification_root / parent_feature / f"{child_feature}_design.md"

        log(f"  Child PRD: {hier_prd}")
        log(f"  Child Spec: {hier_spec}")
        log(f"  Child Design: {hier_design}")

        if hier_prd.is_file() or hier_spec.is_file() or hier_design.is_file():
            structure = "hierarchical"
            if hier_prd.is_file():
                prd_exists = True
                prd_path = str(hier_prd)
                log(f"  ✓ Child PRD found: {hier_prd}")
            if hier_spec.is_file():
                spec_exists = True
                spec_path = str(hier_spec)
                log(f"  ✓ Child Spec found: {hier_spec}")
            if hier_design.is_file():
                design_exists = True
                design_path = str(hier_design)
                log(f"  ✓ Child Design found: {hier_design}")

        # Also check parent index documents
        parent_prd = requirement_root / parent_feature / "index.md"
        parent_spec = specification_root / parent_feature / "index_spec.md"
        parent_design = specification_root / parent_feature / "index_design.md"

        if parent_prd.is_file():
            log(f"  ℹ Parent PRD found: {parent_prd}")
        if parent_spec.is_file():
            log(f"  ℹ Parent Spec found: {parent_spec}")
        if parent_design.is_file():
            log(f"  ℹ Parent Design found: {parent_design}")
    else:
        # Check if this might be a parent feature (check for index files)
        index_prd = requirement_root / feature_name / "index.md"
        index_spec = specification_root / feature_name / "index_spec.md"
        index_design = specification_root / feature_name / "index_design.md"

        if index_prd.is_file() or index_spec.is_file() or index_design.is_file():
            structure = "hierarchical-parent"
            if index_prd.is_file():
                prd_exists = True
                prd_path = str(index_prd)
                log(f"  ✓ Parent PRD found: {index_prd}")
            if index_spec.is_file():
                spec_exists = True
                spec_path = str(index_spec)
                log(f"  ✓ Parent Spec found: {index_spec}")
            if index_design.is_file():
                design_exists = True
                design_path = str(index_design)
                log(f"  ✓ Parent Design found: {index_design}")

    # Output JSON
    result = {
        "prd_exists": prd_exists,
        "spec_exists": spec_exists,
        "design_exists": design_exists,
        "prd_path": prd_path,
        "spec_path": spec_path,
        "design_path": design_path,
        "structure": structure,
        "feature_name": feature_name,
    }
    output_path = cache_dir / "existing-docs.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n")

    log(f"Results saved to: {output_path}")
    log(f"Structure: {structure}")
    log(
        f"PRD: {str(prd_exists).lower()}, "
        f"Spec: {str(spec_exists).lower()}, "
        f"Design: {str(design_exists).lower()}"
    )

    # Determine case
    if design_exists or spec_exists:
        log("Case: A (Existing documents)")
    else:
        log("Case: B (No documents, reverse-engineering needed)")


if __name__ == "__main__":
    main()
