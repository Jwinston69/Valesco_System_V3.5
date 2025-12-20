#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List


REQUIRED_KEYS = ["id", "type", "source_file", "path", "text", "meta"]


def validate_file(path: Path) -> None:
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return

    total_lines = 0
    valid_lines = 0
    invalid_lines = 0
    missing_keys_counts: Dict[str, int] = {}

    samples_first: List[Dict[str, Any]] = []
    samples_last: List[Dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                invalid_lines += 1
                continue

            valid_lines += 1

            # Track missing required keys
            for key in REQUIRED_KEYS:
                if key not in obj:
                    missing_keys_counts[key] = missing_keys_counts.get(key, 0) + 1

            # Sample first 3
            if len(samples_first) < 3:
                samples_first.append(obj)
            else:
                # Maintain last 3
                if len(samples_last) < 3:
                    samples_last.append(obj)
                else:
                    samples_last.pop(0)
                    samples_last.append(obj)

    print("==================================================")
    print(f"File        : {path}")
    print(f"Total lines : {total_lines}")
    print(f"Valid JSON  : {valid_lines}")
    print(f"Invalid JSON: {invalid_lines}")

    if missing_keys_counts:
        print("\nMissing required keys (per key):")
        for key, count in missing_keys_counts.items():
            print(f"  {key}: {count} lines missing")
    else:
        print("\nAll required keys present on all valid lines (or file was empty).")

    print("\n--- Sample: first up to 3 chunks ---")
    for obj in samples_first:
        print(f"- id   : {obj.get('id')}")
        print(f"  type : {obj.get('type')}")
        print(f"  text : {obj.get('text')}")
        print("")

    print("--- Sample: last up to 3 chunks ---")
    for obj in samples_last:
        print(f"- id   : {obj.get('id')}")
        print(f"  type : {obj.get('type')}")
        print(f"  text : {obj.get('text')}")
        print("")

    print("==================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description="JSONL structural validator for Valesco chunks.")
    parser.add_argument(
        "--file",
        required=True,
        help="Path to JSONL file (e.g. workspace/vector_input/materials.jsonl).",
    )
    args = parser.parse_args()
    validate_file(Path(args.file))


if __name__ == "__main__":
    main()
