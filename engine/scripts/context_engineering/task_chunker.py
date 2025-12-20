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

def chunk_tasks(data, source_file: str):
    tasks = data.get("tasks", [])
    for idx, task in enumerate(tasks):
        tid = task.get("id", f"task_{idx}")
        chunk_id = f"task:{source_file}:{tid}"

        parts = []

        # Core identifiers
        if "id" in task:
            parts.append(f"id: {task['id']}")
        if "name" in task:
            parts.append(f"name: {task['name']}")
        if "unit" in task:
            parts.append(f"unit: {task['unit']}")

        # Productivity fields
        prod = task.get("productivity", {})
        if isinstance(prod, dict):
            for key, val in prod.items():
                parts.append(f"{key}: {val}")

        # Rate fields
        rates = task.get("rates", {})
        if isinstance(rates, dict):
            for key, val in rates.items():
                parts.append(f"{key}: {val}")

        # Tags
        tags = task.get("tags", [])
        if isinstance(tags, list) and tags:
            parts.append(f"tags: {', '.join(str(t) for t in tags)}")

        # Materials (if present)
        materials = task.get("materials", [])
        material_codes = []
        if isinstance(materials, list):
            for m in materials:
                if not isinstance(m, dict):
                    continue
                code = m.get("code")
                if code:
                    material_codes.append(str(code))

        if material_codes:
            parts.append(f"materials: {', '.join(material_codes)}")

        text = " | ".join(parts)

        chunk = {
            "id": chunk_id,
            "type": "task",
            "source_file": source_file,
            "path": f"tasks[{idx}]",
            "text": text,
            "meta": task,
        }

        # Add explicit links section if there are material codes
        if material_codes:
            chunk["links"] = {"material_codes": material_codes}

        yield chunk

def main():
    parser = argparse.ArgumentParser(description="Schema-aware task chunker (refined)")
    parser.add_argument("--input", required=True, help="Input tasks YAML file")
    parser.add_argument("--output", required=True, help="Output JSONL chunk file")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_yaml(in_path)
    source_file = os.path.normpath(str(in_path))

    chunks = chunk_tasks(data, source_file)

    ensure_output_dir(out_path)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} task chunks to {out_path}")

if __name__ == "__main__":
    main()
