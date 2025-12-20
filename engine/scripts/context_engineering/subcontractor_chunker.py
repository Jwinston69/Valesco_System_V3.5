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

def make_id(source_file: str, group: str, idx: int):
    group_clean = group.replace(" ", "_")
    return f"subs:{source_file}:{group_clean}:{idx}"

def chunk_subcontractors(data, source_file: str):
    """
    Expected structure:

    meta:
      ...
    groups:
      carpentry:
        items:
          - description: ...
            unit: ...
            rate: ...
          - ...
      tree_surgery:
        items: [...]
    """
    groups = data.get("groups", {})
    if not isinstance(groups, dict):
        return

    for group_name, group_val in groups.items():
        items = group_val.get("items", [])
        if not isinstance(items, list):
            continue

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            # Build retrieval text
            parts = [f"group: {group_name}"]

            for key in ("description", "unit", "rate", "method"):
                if key in item:
                    parts.append(f"{key}: {item[key]}")

            text = " | ".join(parts)

            yield {
                "id": make_id(source_file, group_name, idx),
                "type": "subcontractor",
                "source_file": source_file,
                "path": f"groups.{group_name}.items[{idx}]",
                "text": text,
                "meta": item,
            }

def main():
    parser = argparse.ArgumentParser(description="Schema-aware subcontractor chunker")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_yaml(in_path)
    source_file = os.path.normpath(str(in_path))

    chunks = chunk_subcontractors(data, source_file)

    ensure_output_dir(out_path)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} subcontractor chunks to {out_path}")

if __name__ == "__main__":
    main()
