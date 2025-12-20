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

def material_chunks(data, source_file: str):
    materials = data.get("materials", [])
    for idx, mat in enumerate(materials):
        code = mat.get("code", f"index_{idx}")
        chunk_id = f"material:{source_file}:{code}"

        text_parts = []
        if "code" in mat:
            text_parts.append(f"code: {mat['code']}")
        if "description" in mat:
            text_parts.append(f"description: {mat['description']}")
        if "unit" in mat:
            text_parts.append(f"unit: {mat['unit']}")
        if "rate" in mat:
            text_parts.append(f"rate: {mat['rate']}")

        text = " | ".join(text_parts)

        yield {
            "id": chunk_id,
            "type": "material",
            "source_file": source_file,
            "path": f"materials[{idx}]",
            "text": text,
            "meta": mat,
        }

def generic_chunks(data, source_file: str, chunk_type: str):
    if not isinstance(data, dict):
        return

    for key, value in data.items():
        chunk_id = f"{chunk_type}:{source_file}:{key}"
        text = f"{chunk_type} node {key}"

        yield {
            "id": chunk_id,
            "type": chunk_type,
            "source_file": source_file,
            "path": str(key),
            "text": text,
            "meta": value,
        }

def main():
    parser = argparse.ArgumentParser(description="YAML-aware chunker")
    parser.add_argument("--input", required=True, help="Input YAML file")
    parser.add_argument("--type", required=True,
                        choices=["materials", "tasks", "subs", "pack", "generic"])
    parser.add_argument("--output", required=True, help="Output JSONL file")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_yaml(in_path)
    source_file = os.path.normpath(str(in_path))

    if args.type == "materials":
        chunks = material_chunks(data, source_file)
    else:
        chunks = generic_chunks(data, source_file, args.type)

    ensure_output_dir(out_path)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} chunks to {out_path}")

if __name__ == "__main__":
    main()
