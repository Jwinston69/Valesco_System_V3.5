#!/usr/bin/env python
import argparse
import json
import os
from pathlib import Path
import yaml
import re

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_output_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

CODE_PATTERN = re.compile(r"MAT\.STD\.(\d{2})\.(\d{2})\.(\d{3})")

def parse_code_components(code: str):
    """
    Extract CAT, GRP, NNN from MAT.STD.CC.GG.NNN pattern.
    If not recognised, return None values.
    """
    match = CODE_PATTERN.fullmatch(code)
    if not match:
        return None, None, None
    cat, grp, num = match.groups()
    return cat, grp, num

def chunk_materials(data, source_file: str):
    materials = data.get("materials", [])
    for idx, mat in enumerate(materials):
        code = mat.get("code", f"index_{idx}")
        chunk_id = f"material:{source_file}:{code}"

        # Parse code → category / group / item number
        cat, grp, num = parse_code_components(code)

        parts = []

        # Core fields
        if "code" in mat:
            parts.append(f"code: {mat['code']}")
        if "description" in mat:
            parts.append(f"description: {mat['description']}")
        if "unit" in mat:
            parts.append(f"unit: {mat['unit']}")
        if "rate" in mat:
            parts.append(f"rate: {mat['rate']}")

        # Allocator-derived metadata
        if cat:
            parts.append(f"category: {cat}")
        if grp:
            parts.append(f"group: {grp}")

        # Enriched text output
        text = " | ".join(parts)

        chunk = {
            "id": chunk_id,
            "type": "material",
            "source_file": source_file,
            "path": f"materials[{idx}]",
            "text": text,
            "meta": mat,
        }

        # Add separate metadata field for allocator components
        if cat or grp or num:
            chunk["code_components"] = {
                "category": cat,
                "group": grp,
                "number": num,
            }

        yield chunk

def main():
    parser = argparse.ArgumentParser(description="Refined material chunker")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")

    data = load_yaml(in_path)
    source_file = os.path.normpath(str(in_path))

    chunks = chunk_materials(data, source_file)

    ensure_output_dir(out_path)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} material chunks to {out_path}")

if __name__ == "__main__":
    main()
