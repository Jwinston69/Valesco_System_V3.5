#!/usr/bin/env python
"""
bundle_generator.py

Valesco v2.0 — CE Bundle Generator

Hybrid design:
- Uses existing validation tooling for schema + cross-file checks.
- Implements its own consistency checks for chunks, hashing, and bundling.

Run from C:\Valesco_System, e.g.:

    engine\python_runtime\python.exe engine\scripts\context_engineering\bundle_generator.py ^
        --output "workspace/outputs/VALESCO_CE_BUNDLE.zip" ^
        --regenerate-chunks

Options:
    --snapshot-id <id>      (reserved for future use)
    --regenerate-chunks     Rebuild all JSONL chunk files before bundling.
    --dry-run               Run all checks but do not write ZIP file.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml


ROOT = Path(".").resolve()


# ----------------------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------------------


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as f:
        return f.read()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_jsonl(path: Path) -> List[dict]:
    items: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def prefer_existing_path(*relative_paths: str) -> Path:
    for rel in relative_paths:
        candidate = ROOT / rel
        if candidate.exists():
            return candidate
    return ROOT / relative_paths[-1]


# ----------------------------------------------------------------------
# Chunk expectations (mirrors chunkers)
# ----------------------------------------------------------------------


def expected_material_count(materials_yaml: dict) -> int:
    return len(materials_yaml.get("materials", []))


def expected_task_count(tasks_yaml: dict) -> int:
    return len(tasks_yaml.get("tasks", []))


def expected_subcontractor_count(subs_yaml: dict) -> int:
    total = 0
    for _, group_val in subs_yaml.get("groups", {}).items():
        items = group_val.get("items", [])
        if isinstance(items, list):
            total += len(items)
    return total


def expected_pack_ids(pack_yaml: dict) -> List[str]:
    """
    Build expected IDs that EXACTLY match pack_chunker.py output.
    Chunker ID pattern:
        pack:<category>:<source_file>:<sanitised_key>

    Audit normalised to:
        <category>:<sanitised_key>
    """

    def sanitise(s: str) -> str:
        return (
            str(s)
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

    ids = []

    # META
    ids.append("meta:meta")

    # PRELIMS ROOT
    ids.append("prelims:prelims_root")

    # PRELIMS
    prelims = pack_yaml.get("prelims", {})
    order = prelims.get("order", [])
    for group_name in order:
        group = prelims.get(group_name, {})
        items = group.get("items", [])
        for idx, _ in enumerate(items):
            key = f"{group_name}_{idx}"
            ids.append(f"prelim:{sanitise(key)}")

    # LABOUR
    labour_list = pack_yaml.get("labour", [])
    for idx, item in enumerate(labour_list):
        t = item.get("type", f"labour_{idx}")
        key = sanitise(t)
        ids.append(f"labour:{key}")

    # PLANT
    plant_list = pack_yaml.get("plant", [])
    for idx, item in enumerate(plant_list):
        t = item.get("type", f"plant_{idx}")
        key = sanitise(t)
        ids.append(f"plant:{key}")

    # WASTE
    waste = pack_yaml.get("waste", {})
    for waste_key, waste_val in waste.items():
        items = waste_val.get("items", [])
        for idx, _ in enumerate(items):
            key = f"{waste_key}_{idx}"
            ids.append(f"waste:{sanitise(key)}")

    # PRODUCTIVITY
    prod = pack_yaml.get("productivity", {})
    if prod.get("description"):
        ids.append("productivity:description")

    items = prod.get("items", [])
    for item in items:
        act = str(item.get("activity"))
        key = sanitise(act)
        ids.append(f"productivity:{key}")

    # RULES
    rules = pack_yaml.get("rules", [])
    for idx, _ in enumerate(rules):
        key = f"rule_{idx}"
        ids.append(f"rules:{sanitise(key)}")

    return ids


def actual_pack_ids_from_chunks(pack_chunks: List[dict]) -> List[str]:
    """
    Convert chunk IDs from pack_chunker.py to the same "category:key" form
    used by expected_pack_ids(), correctly handling Windows paths.

    Chunker ID pattern:
        pack:<category>:<source_file>:<sanitised_key>

    But because <source_file> contains "C:\" this introduces extra colons.
    Therefore:
        parts[0] = "pack"
        parts[1] = <category>
        parts[2..-2] = <source_file split incorrectly>
        parts[-1] = <key>
    """

    ids: List[str] = []
    for ch in pack_chunks:
        cid = str(ch.get("id", ""))
        parts = cid.split(":")
        if len(parts) < 3:
            continue

        category = parts[1]
        key = parts[-1]     # ALWAYS take the last segment as the key

        ids.append(f"{category}:{key}")

    return ids


def chunk_count_audit(
    mats_yaml: dict,
    tasks_yaml: dict,
    subs_yaml: dict,
    pack_yaml: dict,
    mats_chunks: List[dict],
    task_chunks: List[dict],
    subs_chunks: List[dict],
    pack_chunks: List[dict],
) -> Tuple[bool, List[str]]:
    """
    Returns (ok, messages). ok=False if any mismatch.
    """
    messages: List[str] = []
    ok = True

    # Materials
    exp_mats = expected_material_count(mats_yaml)
    got_mats = len(mats_chunks)
    if exp_mats != got_mats:
        ok = False
        messages.append(f"MATERIALS mismatch: YAML={exp_mats}, chunks={got_mats}")
    else:
        messages.append(f"MATERIALS OK: {exp_mats} items")

    # Tasks
    exp_tasks = expected_task_count(tasks_yaml)
    got_tasks = len(task_chunks)
    if exp_tasks != got_tasks:
        ok = False
        messages.append(f"TASKS mismatch: YAML={exp_tasks}, chunks={got_tasks}")
    else:
        messages.append(f"TASKS OK: {exp_tasks} items")

    # Subcontractors
    exp_subs = expected_subcontractor_count(subs_yaml)
    got_subs = len(subs_chunks)
    if exp_subs != got_subs:
        ok = False
        messages.append(f"SUBCONTRACTORS mismatch: YAML={exp_subs}, chunks={got_subs}")
    else:
        messages.append(f"SUBCONTRACTORS OK: {exp_subs} items")

    # Generate expected and actual IDs
    exp_pack_ids = expected_pack_ids(pack_yaml)
    act_pack_ids = actual_pack_ids_from_chunks(pack_chunks)

    exp_set = set(exp_pack_ids)
    act_set = set(act_pack_ids)

    if len(exp_set) != len(exp_pack_ids):
        messages.append(
            f"PACK WARNING: expected ID list contains duplicates (size={len(exp_pack_ids)}, unique={len(exp_set)})."
        )
    if len(act_set) != len(act_pack_ids):
        messages.append(
            f"PACK WARNING: actual chunk ID list contains duplicates (size={len(act_pack_ids)}, unique={len(act_set)})."
        )

    missing = exp_set - act_set
    extra = act_set - exp_set

    if missing or extra:
        ok = False
        messages.append(
            f"PACK mismatch: expected={len(exp_pack_ids)}, chunks={len(act_pack_ids)}, missing={len(missing)}, extra={len(extra)}"
        )
        if missing:
            messages.append(f"  Missing IDs (sample): {sorted(list(missing))[:10]}")
        if extra:
            messages.append(f"  Extra IDs (sample): {sorted(list(extra))[:10]}")
    else:
        messages.append(f"PACK OK: {len(exp_pack_ids)} items")

    return ok, messages


# ----------------------------------------------------------------------
# Validation integration
# ----------------------------------------------------------------------


def run_validator() -> bool:
    """
    Run the existing validation entrypoint.
    Hybrid approach: we trust validator.py to enforce schemas + rules.

    Returns True if validation passed (exit code 0), else False.
    """
    # Assume we are already running under engine\python_runtime\python.exe
    # and CWD is project root.
    validate_py = ROOT / "engine" / "scripts" / "validate.py"
    if not validate_py.exists():
        print(
            f"[{datetime.utcnow().isoformat()}] | WARN | CE-BUNDLE | code=VALIDATOR-NOT-FOUND | message='validate.py not found at {validate_py}'"
        )
        # If validator is missing, we treat this as failure to be safe.
        return False

    cmd = [sys.executable, str(validate_py)]
    print(
        f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=VALIDATOR-RUN | message='Running validator via: {cmd}'"
    )
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(
            f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=VALIDATION-FAILED | message='Validator returned non-zero exit code {result.returncode}'"
        )
        return False

    print(
        f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=VALIDATION-PASS | message='Validation succeeded.'"
    )
    return True


# ----------------------------------------------------------------------
# Chunk regeneration
# ----------------------------------------------------------------------


def regenerate_chunks() -> bool:
    """
    Re-run the four chunker scripts to refresh JSONL files.
    Returns True on success, False if any failed.
    """
    scripts = [
        (
            "engine/scripts/context_engineering/material_chunker.py",
            "library/core/valesco_materials.yaml",
            "workspace/vector_input/materials.jsonl",
        ),
        (
            "engine/scripts/context_engineering/task_chunker.py",
            "library/core/valesco_tasks.yaml",
            "workspace/vector_input/tasks.jsonl",
        ),
        (
            "engine/scripts/context_engineering/pack_chunker.py",
            "library/packs/valesco_pack.yaml",
            "workspace/vector_input/pack.jsonl",
        ),
        (
            "engine/scripts/context_engineering/subcontractor_chunker.py",
            "library/core/valesco_subcontractors.yaml",
            "workspace/vector_input/subs.jsonl",
        ),
    ]

    for script_rel, input_rel, output_rel in scripts:
        script_path = ROOT / script_rel
        input_path = ROOT / input_rel
        output_path = ROOT / output_rel

        if not script_path.exists():
            print(
                f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=CHUNKER-MISSING | message='Chunker script not found: {script_path}'"
            )
            return False
        if not input_path.exists():
            print(
                f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=CHUNKER-INPUT-MISSING | message='Chunker input not found: {input_path}'"
            )
            return False

        ensure_parent_dir(output_path)
        cmd = [
            sys.executable,
            str(script_path),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ]
        print(
            f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=CHUNKER-RUN | message='Running chunker: {cmd}'"
        )
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(
                f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=CHUNKER-FAILED | message='Chunker failed: {script_path} (exit {result.returncode})'"
            )
            return False

    print(
        f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=CHUNKER-OK | message='All chunkers completed successfully.'"
    )
    return True


# ----------------------------------------------------------------------
# Version metadata extraction
# ----------------------------------------------------------------------


def extract_versions(
    materials_yaml: dict,
    tasks_yaml: dict,
    subs_yaml: dict,
    pack_yaml: dict,
    allocator_yaml: Optional[dict],
) -> Dict[str, str]:
    versions: Dict[str, str] = {}

    # Materials
    meta_m = materials_yaml.get("meta", {})
    versions["materials_version"] = str(meta_m.get("materials_version", ""))

    # Tasks
    meta_t = tasks_yaml.get("meta", {})
    versions["tasks_version"] = str(meta_t.get("tasks_version", ""))

    # Subcontractors
    meta_s = subs_yaml.get("meta", {})
    # key name may vary; we handle generically
    subs_ver = meta_s.get("subcontractors_version") or meta_s.get("subs_version") or ""
    versions["subcontractors_version"] = str(subs_ver)

    # Pack
    meta_p = pack_yaml.get("meta", {})
    versions["pack_version"] = str(meta_p.get("pack_version", ""))

    # Allocator
    if allocator_yaml is not None:
        meta_a = allocator_yaml.get("meta", {})
        alloc_ver = meta_a.get("version") or meta_a.get("allocator_version") or ""
        versions["allocator_version"] = str(alloc_ver)
    else:
        versions["allocator_version"] = ""

    return versions


# ----------------------------------------------------------------------
# Bundle creation
# ----------------------------------------------------------------------


def build_file_map() -> List[Tuple[Path, str]]:
    """
    Returns list of (source_path, archive_name).
    Paths are relative to ROOT.
    Archive names use forward slashes.
    """
    mapping: List[Tuple[Path, str]] = []

    # Governance
    manifest_src = prefer_existing_path(
        "docs/_archive/v1.x/VALESCO_SYSTEM_MANIFEST_v1.9.1.md",
        "docs/VALESCO_SYSTEM_MANIFEST_v1.9.1.md",
    )
    governance_files = [
        ("docs/governance/valesco_instructions.txt", "governance/valesco_instructions.txt"),
        ("docs/governance/VALESCO_TRUTH_HIERARCHY.md", "governance/VALESCO_TRUTH_HIERARCHY.md"),
        ("docs/governance/VALESCO_DEVELOPER_CHECKLIST.md", "governance/VALESCO_DEVELOPER_CHECKLIST.md"),
        (manifest_src, "governance/manifest.md"),
    ]


    # Allocator
    allocator_files = [
        ("engine/config/materials_allocator.yaml", "allocator/materials_allocator.yaml"),
    ]

    # Library
    library_files = [
        ("library/core/valesco_materials.yaml", "library/valesco_materials.yaml"),
        ("library/core/valesco_tasks.yaml", "library/valesco_tasks.yaml"),
        ("library/core/valesco_subcontractors.yaml", "library/valesco_subcontractors.yaml"),
    ]

    # Pack
    pack_files = [
        ("library/packs/valesco_pack.yaml", "pack/valesco_pack.yaml"),
    ]

    # Chunks
    chunk_files = [
        ("workspace/vector_input/materials.jsonl", "chunks/materials.jsonl"),
        ("workspace/vector_input/tasks.jsonl", "chunks/tasks.jsonl"),
        ("workspace/vector_input/pack.jsonl", "chunks/pack.jsonl"),
        ("workspace/vector_input/subs.jsonl", "chunks/subs.jsonl"),
    ]

    for src, arc in (
        governance_files + allocator_files + library_files + pack_files + chunk_files
    ):
        src_path = src if isinstance(src, Path) else ROOT / src
        mapping.append((src_path, arc))

    return mapping


def generate_bundle(
    output_path: Path,
    snapshot_id: Optional[str] = None,
    dry_run: bool = False,
) -> int:
    """
    Returns exit code:
      0: success
      2: validation failed
      3: config/path failure
      4: chunk mismatch
      1: generic failure
    """
    # Phase 1: existence check
    file_map = build_file_map()
    missing_files: List[Path] = []
    for src, _ in file_map:
        if not src.exists():
            missing_files.append(src)

    if missing_files:
        for mf in missing_files:
            print(
                f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=CONFIG-MISSING-FILE | message='Required file missing: {mf}'"
            )
        return 3

    # Load YAMLs
    materials_yaml = load_yaml(ROOT / "library/core/valesco_materials.yaml")
    tasks_yaml = load_yaml(ROOT / "library/core/valesco_tasks.yaml")
    subs_yaml = load_yaml(ROOT / "library/core/valesco_subcontractors.yaml")
    pack_yaml = load_yaml(ROOT / "library/packs/valesco_pack.yaml")
    allocator_yaml = None
    alloc_path = ROOT / "engine/config/materials_allocator.yaml"
    if alloc_path.exists():
        allocator_yaml = load_yaml(alloc_path)

    # Phase 2: validation gate
    if not run_validator():
        return 2

    # Phase 3: chunk consistency
    mats_chunks = load_jsonl(ROOT / "workspace/vector_input/materials.jsonl")
    task_chunks = load_jsonl(ROOT / "workspace/vector_input/tasks.jsonl")
    subs_chunks = load_jsonl(ROOT / "workspace/vector_input/subs.jsonl")
    pack_chunks = load_jsonl(ROOT / "workspace/vector_input/pack.jsonl")

    ok, messages = chunk_count_audit(
        materials_yaml,
        tasks_yaml,
        subs_yaml,
        pack_yaml,
        mats_chunks,
        task_chunks,
        subs_chunks,
        pack_chunks,
    )
    for msg in messages:
        print(
            f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=CHUNK-AUDIT | message='{msg}'"
        )
    if not ok:
        print(
            f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=CHUNK-AUDIT-FAILED | message='Chunk audit failed; bundle not produced.'"
        )
        return 4

    # Phase 4: hashing & version metadata
    file_hashes: Dict[str, str] = {}
    for src, arc in file_map:
        rel_arc = arc.replace("\\", "/")
        file_hashes[rel_arc] = file_sha256(src)

    versions = extract_versions(
        materials_yaml,
        tasks_yaml,
        subs_yaml,
        pack_yaml,
        allocator_yaml,
    )

    created_utc = datetime.now(timezone.utc).isoformat()
    bundle_meta = {
        "bundle_version": "v2.0",
        "created_utc": created_utc,
        "materials_version": versions.get("materials_version", ""),
        "tasks_version": versions.get("tasks_version", ""),
        "subcontractors_version": versions.get("subcontractors_version", ""),
        "pack_version": versions.get("pack_version", ""),
        "allocator_version": versions.get("allocator_version", ""),
        "snapshot_id": snapshot_id or "",
        "sha256": file_hashes,
    }

    # Prepare meta files in memory
    version_info_bytes = json.dumps(bundle_meta, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    sha_lines = [f"{h}  {p}" for p, h in sorted(file_hashes.items(), key=lambda x: x[0])]
    sha256_all_bytes = ("\n".join(sha_lines) + "\n").encode("utf-8")

    # Phase 5: packaging
    if dry_run:
        print(
            f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=DRY-RUN | message='Dry run successful; bundle not written.'"
        )
        return 0

    ensure_parent_dir(output_path)

    try:
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # Add all mapped files
            for src, arc in file_map:
                arcname = arc.replace("\\", "/")
                zf.write(src, arcname)

            # Add meta/version_info.json
            zf.writestr("meta/version_info.json", version_info_bytes)

            # Add meta/sha256_all.txt
            zf.writestr("meta/sha256_all.txt", sha256_all_bytes)

            # Snapshot meta placeholder if snapshot_id present
            if snapshot_id:
                snap_meta = {
                    "snapshot_id": snapshot_id,
                    "note": "Snapshot integration to be implemented in v2.1+.",
                }
                zf.writestr(
                    "meta/snapshot_meta.json",
                    json.dumps(snap_meta, indent=2, sort_keys=True).encode("utf-8"),
                )

    except Exception as exc:
        print(
            f"[{datetime.utcnow().isoformat()}] | ERROR | CE-BUNDLE | code=ZIP-WRITE-FAILED | message='Failed to write bundle: {exc}'"
        )
        return 1

    bundle_hash = file_sha256(output_path)
    print(
        f"[{datetime.utcnow().isoformat()}] | INFO | CE-BUNDLE | code=BUNDLE-WRITTEN | message='Bundle written to {output_path} with SHA256={bundle_hash}'"
    )
    return 0


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Valesco v2.0 CE Bundle Generator")
    parser.add_argument(
        "--output",
        required=True,
        help="Output ZIP path, e.g. workspace/outputs/VALESCO_CE_BUNDLE.zip",
    )
    parser.add_argument(
        "--snapshot-id",
        help="Optional snapshot identifier to embed in bundle metadata.",
    )
    parser.add_argument(
        "--regenerate-chunks",
        action="store_true",
        help="Rebuild materials/tasks/pack/subs chunks before bundling.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation and audits only; do not write ZIP.",
    )

    args = parser.parse_args()

    output_path = ROOT / args.output

    # Optional chunk regeneration
    if args.regenerate_chunks:
        if not regenerate_chunks():
            sys.exit(4)

    exit_code = generate_bundle(
        output_path=output_path,
        snapshot_id=args.snapshot_id,
        dry_run=args.dry_run,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
