#!/usr/bin/env python
"""
retrieval_simulator.py

Purpose:
    Simple keyword-based retrieval simulator over the generated JSONL chunk files in
    workspace/vector_input/.

    This is a development-only helper used during the v1.9.1 → v2.0 context engineering phase.
    It does NOT modify any source data and is not part of the production runtime.

Usage examples (from C:\Valesco_System):

    engine\python_runtime\python.exe engine\scripts\context_engineering\retrieval_simulator.py ^
        --file workspace/vector_input/materials.jsonl ^
        --query "concrete" ^
        --top_k 5

    engine\python_runtime\python.exe engine\scripts\context_engineering\retrieval_simulator.py ^
        --file workspace/vector_input/pack.jsonl ^
        --query "labour" ^
        --top_k 3
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple


def load_chunks(path: Path) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                chunks.append(obj)
            except json.JSONDecodeError:
                # Skip malformed lines gracefully
                continue
    return chunks


def simple_score(text: str, query: str) -> int:
    """
    Very simple scoring:
    - Lowercase both text and query
    - Count how many times the query string appears in the text
    """
    text_l = text.lower()
    query_l = query.lower()
    if not query_l:
        return 0
    count = 0
    start = 0
    while True:
        idx = text_l.find(query_l, start)
        if idx == -1:
            break
        count += 1
        start = idx + len(query_l)
    return count


def rank_chunks(chunks: List[Dict[str, Any]], query: str, top_k: int) -> List[Tuple[int, Dict[str, Any]]]:
    scored: List[Tuple[int, Dict[str, Any]]] = []
    for chunk in chunks:
        text = str(chunk.get("text", ""))
        score = simple_score(text, query)
        if score > 0:
            scored.append((score, chunk))

    # Sort by score descending
    scored.sort(key=lambda pair: pair[0], reverse=True)
    if top_k > 0:
        scored = scored[:top_k]
    return scored


def print_results(results: List[Tuple[int, Dict[str, Any]]]) -> None:
    if not results:
        print("No matches found.")
        return

    print(f"Found {len(results)} matching chunks:\n")
    for score, chunk in results:
        cid = chunk.get("id", "<no id>")
        ctype = chunk.get("type", "<no type>")
        source = chunk.get("source_file", "<no source>")
        path = chunk.get("path", "<no path>")
        text = chunk.get("text", "")

        print("------------------------------------------------------------")
        print(f"Score   : {score}")
        print(f"ID      : {cid}")
        print(f"Type    : {ctype}")
        print(f"Source  : {source}")
        print(f"Path    : {path}")
        print(f"Text    : {text}")
    print("------------------------------------------------------------")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple retrieval simulator over JSONL chunks.")
    parser.add_argument(
        "--file",
        required=True,
        help="Path to JSONL chunk file (e.g. workspace/vector_input/materials.jsonl).",
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Text fragment to search for.",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=10,
        help="Maximum number of results to show (default: 10).",
    )

    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        raise SystemExit(f"Chunk file not found: {file_path}")

    chunks = load_chunks(file_path)
    if not chunks:
        print(f"No chunks loaded from {file_path}")
        return

    results = rank_chunks(chunks, args.query, args.top_k)
    print_results(results)


if __name__ == "__main__":
    main()
