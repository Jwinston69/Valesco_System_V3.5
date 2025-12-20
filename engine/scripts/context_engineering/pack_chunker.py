#!/usr/bin/env python
import argparse
import json
import os
from pathlib import Path
import yaml

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_output_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def make_id(source_file: str, category: str, key: str):
    key_sanitised = key.replace(" ", "_").replace("/", "_")
    return f"pack:{category}:{source_file}:{key_sanitised}"

# ----------------------------------------------------
# META
# ----------------------------------------------------
def chunk_meta(meta: dict, source: str):
    yield {
        "id": make_id(source, "meta", "meta"),
        "type": "pack_meta",
        "source_file": source,
        "path": "meta",
        "text": f"pack meta | name: {meta.get('pack_name','')} | version: {meta.get('pack_version','')} | date: {meta.get('date','')}",
        "meta": meta,
    }

# ----------------------------------------------------
# LABOUR  (list)
# ----------------------------------------------------
def chunk_labour(labour_list: list, source: str):
    for idx, item in enumerate(labour_list):
        t = item.get("type", f"labour_{idx}")
        text = f"labour | {t} | unit: {item.get('unit')} | rate_per_unit: {item.get('rate_per_unit')}"
        yield {
            "id": make_id(source, "labour", t),
            "type": "pack_labour",
            "source_file": source,
            "path": f"labour[{idx}]",
            "text": text,
            "meta": item,
        }

# ----------------------------------------------------
# PLANT  (list)
# ----------------------------------------------------
def chunk_plant(plant_list: list, source: str):
    for idx, item in enumerate(plant_list):
        t = item.get("type", f"plant_{idx}")
        text = f"plant | {t} | unit: {item.get('unit')} | rate_per_unit: {item.get('rate_per_unit')}"
        yield {
            "id": make_id(source, "plant", t),
            "type": "pack_plant",
            "source_file": source,
            "path": f"plant[{idx}]",
            "text": text,
            "meta": item,
        }

# ----------------------------------------------------
# PRELIMS STRUCTURE (multiple nested groups)
# ----------------------------------------------------
def chunk_prelims(prelims: dict, source: str):
    percent = prelims.get("percent")
    apply_once = prelims.get("apply_once")
    order = prelims.get("order", [])

    # Top-level prelims entry
    yield {
        "id": make_id(source, "prelims", "prelims_root"),
        "type": "pack_prelims_root",
        "source_file": source,
        "path": "prelims",
        "text": f"prelims root | percent: {percent} | apply_once: {apply_once}",
        "meta": {"percent": percent, "apply_once": apply_once, "order": order},
    }

    # Iterate through group names listed in prelims.order
    for group_name in order:
        group = prelims.get(group_name)
        if not group:
            continue

        items = group.get("items", [])
        for idx, item in enumerate(items):
            t = item.get("type", f"{group_name}_{idx}")
            text = f"prelim | group: {group_name} | type: {t} | unit: {item.get('unit')} | rate_per_unit: {item.get('rate_per_unit')}"
            cid = f"{group_name}_{idx}"

            yield {
                "id": make_id(source, "prelim", cid),
                "type": "pack_prelim",
                "source_file": source,
                "path": f"prelims.{group_name}.items[{idx}]",
                "text": text,
                "meta": item,
            }

# ----------------------------------------------------
# WASTE STRUCTURE
# ----------------------------------------------------
def chunk_waste(waste_dict: dict, source: str):
    for waste_key, waste_entry in waste_dict.items():
        items = waste_entry.get("items", [])
        for idx, item in enumerate(items):
            t = item.get("type", f"{waste_key}_{idx}")
            text = f"waste | category: {waste_key} | type: {t} | unit: {item.get('unit')} | rate: {item.get('rate')}"
            cid = f"{waste_key}_{idx}"

            yield {
                "id": make_id(source, "waste", cid),
                "type": "pack_waste",
                "source_file": source,
                "path": f"waste.{waste_key}.items[{idx}]",
                "text": text,
                "meta": item,
            }

# ----------------------------------------------------
# PRODUCTIVITY STRUCTURE
# ----------------------------------------------------
def chunk_productivity(prod: dict, source: str):
    desc = prod.get("description")
    if desc:
        yield {
            "id": make_id(source, "productivity", "description"),
            "type": "pack_productivity_info",
            "source_file": source,
            "path": "productivity.description",
            "text": f"productivity description | {desc}",
            "meta": desc,
        }

    items = prod.get("items", [])
    for idx, item in enumerate(items):
        act = item.get("activity", f"activity_{idx}")
        text_parts = [f"activity: {act}"]
        for k, v in item.items():
            if k != "activity":
                text_parts.append(f"{k}: {v}")
        text = " | ".join(text_parts)

        yield {
            "id": make_id(source, "productivity", act),
            "type": "pack_productivity",
            "source_file": source,
            "path": f"productivity.items[{idx}]",
            "text": text,
            "meta": item,
        }

# ----------------------------------------------------
# RULES
# ----------------------------------------------------
def chunk_rules(rules_list: list, source: str):
    for idx, rule in enumerate(rules_list):
        text = f"rule | {rule}"
        yield {
            "id": make_id(source, "rules", f"rule_{idx}"),
            "type": "pack_rule",
            "source_file": source,
            "path": f"rules[{idx}]",
            "text": text,
            "meta": rule,
        }

# ----------------------------------------------------
# MAIN
# ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Schema-aware Pack Chunker v2")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_yaml(in_path)
    source_file = os.path.normpath(str(in_path))

    chunks = []

    meta = data.get("meta")
    if isinstance(meta, dict):
        chunks.extend(list(chunk_meta(meta, source_file)))

    prelims = data.get("prelims")
    if isinstance(prelims, dict):
        chunks.extend(list(chunk_prelims(prelims, source_file)))

    labour = data.get("labour")
    if isinstance(labour, list):
        chunks.extend(list(chunk_labour(labour, source_file)))

    plant = data.get("plant")
    if isinstance(plant, list):
        chunks.extend(list(chunk_plant(plant, source_file)))

    waste = data.get("waste")
    if isinstance(waste, dict):
        chunks.extend(list(chunk_waste(waste, source_file)))

    productivity = data.get("productivity")
    if isinstance(productivity, dict):
        chunks.extend(list(chunk_productivity(productivity, source_file)))

    rules = data.get("rules")
    if isinstance(rules, list):
        chunks.extend(list(chunk_rules(rules, source_file)))

    ensure_output_dir(out_path)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} pack chunks to {out_path}")

if __name__ == "__main__":
    main()
