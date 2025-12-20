#!/usr/bin/env python
import yaml
import json
from pathlib import Path

ROOT = Path(".")

def load_yaml(path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_chunks(path):
    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                chunks.append(json.loads(line))
            except Exception:
                pass
    return chunks

# ---------------------------------------------------------------------
# MATERIALS
# ---------------------------------------------------------------------
def expected_material_ids(mats_yaml):
    ids = []
    for idx, mat in enumerate(mats_yaml.get("materials", [])):
        code = mat.get("code", f"index_{idx}")
        ids.append(code)
    return ids

def chunk_material_ids(chunks):
    ids = []
    for c in chunks:
        cid = c["id"].split(":")[-1]  # last section = material code
        ids.append(cid)
    return ids

# ---------------------------------------------------------------------
# TASKS
# ---------------------------------------------------------------------
def expected_task_ids(tasks_yaml):
    ids = []
    for t in tasks_yaml.get("tasks", []):
        ids.append(t.get("id"))
    return ids

def chunk_task_ids(chunks):
    ids = []
    for c in chunks:
        cid = c["id"].split(":")[-1]
        ids.append(cid)
    return ids

# ---------------------------------------------------------------------
# SUBCONTRACTORS
# ---------------------------------------------------------------------
def expected_sub_ids(subs_yaml):
    ids = []
    for group, val in subs_yaml.get("groups", {}).items():
        items = val.get("items", [])
        for idx, _ in enumerate(items):
            ids.append(f"{group}:{idx}")
    return ids

def chunk_sub_ids(chunks):
    ids = []
    for c in chunks:
        parts = c["id"].split(":")
        group = parts[-2]
        idx = parts[-1]
        ids.append(f"{group}:{idx}")
    return ids

# ---------------------------------------------------------------------
# PACK
# ---------------------------------------------------------------------

def expected_pack_ids(pack_yaml):
    ids = []

    # meta
    ids.append("meta:meta")

    # prelims root
    ids.append("prelims:prelims_root")

    prelims = pack_yaml.get("prelims", {})
    order = prelims.get("order", [])

    # prelims.<group>.items[*]
    for g in order:
        items = prelims.get(g, {}).get("items", [])
        for idx, _ in enumerate(items):
            ids.append(f"prelim:{g}_{idx}")

    # labour
    for idx, item in enumerate(pack_yaml.get("labour", [])):
        t = item.get("type", f"labour_{idx}")
        ids.append(f"labour:{t}")

    # plant
    for idx, item in enumerate(pack_yaml.get("plant", [])):
        t = item.get("type", f"plant_{idx}")
        ids.append(f"plant:{t}")

    # waste
    for wk, wv in pack_yaml.get("waste", {}).items():
        for idx, _ in enumerate(wv.get("items", [])):
            ids.append(f"waste:{wk}_{idx}")

    # productivity description
    if pack_yaml.get("productivity", {}).get("description"):
        ids.append("productivity:description")

    # productivity items
    for item in pack_yaml.get("productivity", {}).get("items", []):
        act = item.get("activity")
        ids.append(f"productivity:{act}")

    # rules
    for idx, _ in enumerate(pack_yaml.get("rules", [])):
        ids.append(f"rules:rule_{idx}")

    return ids

def chunk_pack_ids(chunks):
    ids = []
    for c in chunks:
        parts = c["id"].split(":")
        # Format: pack:category:source:key
        category = parts[-2]
        key = parts[-1]
        ids.append(f"{category}:{key}")
    return ids


# ---------------------------------------------------------------------
# DIFF UTILITY
# ---------------------------------------------------------------------
def diff_lists(expected, actual):
    exp = set(expected)
    act = set(actual)
    missing = exp - act
    extra = act - exp
    return missing, extra

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Chunk completeness audit")
    parser.add_argument("--diff", action="store_true", help="Show missing and extra items")
    args = parser.parse_args()

    # Load YAML
    mats_yaml = load_yaml(ROOT/"library/core/valesco_materials.yaml")
    tasks_yaml = load_yaml(ROOT/"library/core/valesco_tasks.yaml")
    subs_yaml = load_yaml(ROOT/"library/core/valesco_subcontractors.yaml")
    pack_yaml = load_yaml(ROOT/"library/packs/valesco_pack.yaml")

    # Load chunks
    mats_chunks = load_chunks(ROOT/"workspace/vector_input/materials.jsonl")
    task_chunks = load_chunks(ROOT/"workspace/vector_input/tasks.jsonl")
    subs_chunks = load_chunks(ROOT/"workspace/vector_input/subs.jsonl")
    pack_chunks_list = load_chunks(ROOT/"workspace/vector_input/pack.jsonl")

    # Expected IDs
    exp_mats = expected_material_ids(mats_yaml)
    exp_tasks = expected_task_ids(tasks_yaml)
    exp_subs = expected_sub_ids(subs_yaml)
    exp_pack = expected_pack_ids(pack_yaml)

    # Chunk IDs
    act_mats = chunk_material_ids(mats_chunks)
    act_tasks = chunk_task_ids(task_chunks)
    act_subs = chunk_sub_ids(subs_chunks)
    act_pack = chunk_pack_ids(pack_chunks_list)

    print("=== MATERIALS ===")
    print("Expected:", len(exp_mats), "Chunks:", len(act_mats))
    if args.diff:
        missing, extra = diff_lists(exp_mats, act_mats)
        print("Missing:", missing)
        print("Extra:", extra)
    print()

    print("=== TASKS ===")
    print("Expected:", len(exp_tasks), "Chunks:", len(act_tasks))
    if args.diff:
        missing, extra = diff_lists(exp_tasks, act_tasks)
        print("Missing:", missing)
        print("Extra:", extra)
    print()

    print("=== SUBCONTRACTORS ===")
    print("Expected:", len(exp_subs), "Chunks:", len(act_subs))
    if args.diff:
        missing, extra = diff_lists(exp_subs, act_subs)
        print("Missing:", missing)
        print("Extra:", extra)
    print()

    print("=== PACK ===")
    print("Expected:", len(exp_pack), "Chunks:", len(act_pack))
    if args.diff:
        missing, extra = diff_lists(exp_pack, act_pack)
        print("Missing:", missing)
        print("Extra:", extra)

if __name__ == "__main__":
    main()
