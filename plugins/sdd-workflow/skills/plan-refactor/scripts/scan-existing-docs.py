#!/usr/bin/env python3
"""
scan-existing-docs.py
Scan for existing PRD/spec documents and the ticket-scoped design draft
Usage: scan-existing-docs.py <feature-name> [ticket-number]

The processing case is decided by the presence of a **spec**, not a design
document: technical design documents are no longer persisted under
specification/ (they live at task/{ticket-number}/design-draft.md and are
deleted after implementation), so their absence is the normal state.

A legacy persisted design doc (specification/{feature}_design.md, v4.x) is
still detected, but only as supplementary reading context for projects mid
migration - it never influences the case decision.
"""

import json
import os
import sys
from pathlib import Path


def log(message: str) -> None:
    """Print log message to stderr"""
    print(f"[scan-existing-docs] {message}", file=sys.stderr)


def resolve_spec(directory: Path, base: str):
    """Return the spec file for base under directory, or None.

    The `_spec` suffix is optional under specification/ (single-type
    directory), so both `{base}_spec.md` and `{base}.md` are valid. The
    suffixed form wins when both exist.
    """
    for name in (f"{base}_spec.md", f"{base}.md"):
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def scan_layout(label: str, prd: Path, spec_dir: Path, spec_base: str):
    """Look for one PRD / spec / legacy-design triple in a single layout.

    `label` prefixes the log lines ("", "Child", "Parent"). Returns a dict of
    the paths that exist, or None when the layout holds none of them (the
    caller then leaves `structure` untouched).
    """
    prefix = f"{label} " if label else ""
    spec = resolve_spec(spec_dir, spec_base)
    legacy_design = spec_dir / f"{spec_base}_design.md"

    log(f"  {prefix}PRD: {prd}")
    log(f"  {prefix}Spec: {spec_dir / f'{spec_base}_spec.md'} (or without the _spec suffix)")
    log(f"  {prefix}Legacy design: {legacy_design}")

    if not (prd.is_file() or spec is not None or legacy_design.is_file()):
        return None

    found = {}
    if prd.is_file():
        found["prd_path"] = str(prd)
        log(f"  ✓ {prefix}PRD found: {prd}")
    if spec is not None:
        found["spec_path"] = str(spec)
        log(f"  ✓ {prefix}Spec found: {spec}")
    if legacy_design.is_file():
        found["legacy_design_path"] = str(legacy_design)
        log(f"  ℹ {prefix}Legacy design doc found (context only): {legacy_design}")
    return found


def main() -> None:
    """Main execution"""
    if len(sys.argv) < 2 or not sys.argv[1]:
        log("ERROR: feature-name required")
        sys.exit(1)

    feature_name = sys.argv[1]
    ticket_number = sys.argv[2] if len(sys.argv) > 2 else ""

    # Environment variables (with defaults)
    sdd_root = os.environ.get("SDD_ROOT", ".sdd")
    sdd_requirement_dir = os.environ.get("SDD_REQUIREMENT_DIR", "requirement")
    sdd_specification_dir = os.environ.get("SDD_SPECIFICATION_DIR", "specification")
    sdd_task_dir = os.environ.get("SDD_TASK_DIR", "task")
    sdd_requirement_path = os.environ.get(
        "SDD_REQUIREMENT_PATH", f"{sdd_root}/{sdd_requirement_dir}"
    )
    sdd_specification_path = os.environ.get(
        "SDD_SPECIFICATION_PATH", f"{sdd_root}/{sdd_specification_dir}"
    )
    sdd_task_path = os.environ.get("SDD_TASK_PATH", f"{sdd_root}/{sdd_task_dir}")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

    project_root = Path(project_dir)
    requirement_root = project_root / sdd_requirement_path
    specification_root = project_root / sdd_specification_path
    task_root = project_root / sdd_task_path

    # Create cache directory
    cache_dir = project_root / sdd_root / ".cache" / "plan-refactor"
    cache_dir.mkdir(parents=True, exist_ok=True)

    log(f"Scanning for: {feature_name}")
    log(f"SDD_ROOT: {sdd_root}")
    log(f"SDD_REQUIREMENT_PATH: {sdd_requirement_path}")
    log(f"SDD_SPECIFICATION_PATH: {sdd_specification_path}")
    log(f"SDD_TASK_PATH: {sdd_task_path}")

    # Initialize results. Layouts are merged per field (a later layout wins for
    # the paths it has, an earlier one keeps the rest), and `structure` names the
    # last layout that matched anything.
    found = {}
    structure = "none"

    log("Checking flat structure...")
    flat = scan_layout(
        "", requirement_root / f"{feature_name}.md", specification_root, feature_name
    )
    if flat is not None:
        structure = "flat"
        found.update(flat)

    # Check hierarchical structure (if feature-name contains '/')
    if "/" in feature_name:
        parent_feature, child_feature = feature_name.rsplit("/", 1)
        hier_dir = specification_root / parent_feature

        log("Checking hierarchical structure...")
        log(f"  Parent: {parent_feature}, Child: {child_feature}")

        child = scan_layout(
            "Child",
            requirement_root / parent_feature / f"{child_feature}.md",
            hier_dir,
            child_feature,
        )
        if child is not None:
            structure = "hierarchical"
            found.update(child)

        # Also report the parent index documents (context only, no state)
        parent_prd = requirement_root / parent_feature / "index.md"
        parent_spec = resolve_spec(hier_dir, "index")
        if parent_prd.is_file():
            log(f"  ℹ Parent PRD found: {parent_prd}")
        if parent_spec is not None:
            log(f"  ℹ Parent Spec found: {parent_spec}")
    else:
        # Check if this might be a parent feature (check for index files)
        parent = scan_layout(
            "Parent",
            requirement_root / feature_name / "index.md",
            specification_root / feature_name,
            "index",
        )
        if parent is not None:
            structure = "hierarchical-parent"
            found.update(parent)

    # Check the ticket-scoped design draft (supplementary input for Case A)
    design_draft_path = ""
    if ticket_number:
        draft = task_root / ticket_number / "design-draft.md"
        log(f"Checking design draft: {draft}")
        if draft.is_file():
            design_draft_path = str(draft)
            log(f"  ✓ Design draft found: {draft}")
    else:
        log("No ticket-number given; skipping design draft check")

    prd_path = found.get("prd_path", "")
    spec_path = found.get("spec_path", "")
    legacy_design_path = found.get("legacy_design_path", "")

    prd_exists = bool(prd_path)
    spec_exists = bool(spec_path)
    legacy_design_exists = bool(legacy_design_path)
    design_draft_exists = bool(design_draft_path)

    # Case A when a spec exists, Case B otherwise. A design doc is never part
    # of this decision (see module docstring).
    case = "A" if spec_exists else "B"

    # Output JSON
    result = {
        "prd_exists": prd_exists,
        "spec_exists": spec_exists,
        "design_draft_exists": design_draft_exists,
        "legacy_design_exists": legacy_design_exists,
        "prd_path": prd_path,
        "spec_path": spec_path,
        "design_draft_path": design_draft_path,
        "legacy_design_path": legacy_design_path,
        "structure": structure,
        "feature_name": feature_name,
        "ticket_number": ticket_number,
        "case": case,
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
        f"DesignDraft: {str(design_draft_exists).lower()}, "
        f"LegacyDesign: {str(legacy_design_exists).lower()}"
    )

    if case == "A":
        log("Case: A (Spec exists)")
    else:
        log("Case: B (No spec, reverse-engineering needed)")


if __name__ == "__main__":
    main()
