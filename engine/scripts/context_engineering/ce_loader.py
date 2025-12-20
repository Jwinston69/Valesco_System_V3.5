#!/usr/bin/env python
"""
ce_loader.py

Valesco v2.0 — CE Bundle Loader + Sparse Retriever

Purpose:
- Load the Valesco CE Bundle ZIP (produced by bundle_generator.py).
- Expose a read-only API to access chunk datasets.
- Provide a simple CLI for keyword-style sparse retrieval (no vector DB).

Design constraints:
- Read-only: never modifies underlying project files.
- Works entirely off the CE bundle (ZIP) for the "Air Gap".
- No semantic/vector search, only deterministic keyword-based scoring.
"""

import argparse
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------


@dataclass
class Chunk:
    id: str
    type: str
    source_file: str
    path: str
    text: str
    meta: dict

    @classmethod
    def from_json(cls, obj: dict) -> "Chunk":
        return cls(
            id=str(obj.get("id", "")),
            type=str(obj.get("type", "")),
            source_file=str(obj.get("source_file", "")),
            path=str(obj.get("path", "")),
            text=str(obj.get("text", "")),
            meta=obj.get("meta", {}) or {},
        )


@dataclass
class CEBundle:
    """
    In-memory representation of a CE bundle.
    Only uses chunks/ for retrieval; governance/library files are loaded by
    higher-level tools when needed.
    """

    bundle_path: Path
    materials: List[Chunk]
    tasks: List[Chunk]
    pack: List[Chunk]
    subs: List[Chunk]
    meta: dict

    def all_domains(self) -> Dict[str, List[Chunk]]:
        return {
            "materials": self.materials,
            "tasks": self.tasks,
            "pack": self.pack,
            "subs": self.subs,
        }


# ----------------------------------------------------------------------
# Bundle loading
# ----------------------------------------------------------------------


def _load_jsonl_from_zip(zf: zipfile.ZipFile, inner_path: str) -> List[dict]:
    """
    Load a JSONL file from inside the ZIP.
    Returns a list of decoded JSON objects.
    """
    try:
        with zf.open(inner_path, "r") as f:
            raw = f.read().decode("utf-8", errors="replace")
    except KeyError:
        # File not present in the bundle
        return []

    items: List[dict] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            items.append(obj)
        except json.JSONDecodeError:
            # Skip malformed lines rather than failing the whole load
            continue
    return items


def _load_json_from_zip(zf: zipfile.ZipFile, inner_path: str) -> Optional[dict]:
    try:
        with zf.open(inner_path, "r") as f:
            raw = f.read().decode("utf-8", errors="replace")
        return json.loads(raw)
    except KeyError:
        return None
    except json.JSONDecodeError:
        return None


def load_ce_bundle(bundle_path: Path) -> CEBundle:
    """
    Load CE bundle chunks + metadata from a ZIP created by bundle_generator.py.

    Expected structure:
      chunks/materials.jsonl
      chunks/tasks.jsonl
      chunks/pack.jsonl
      chunks/subs.jsonl
      meta/version_info.json  (optional but expected)
    """
    bundle_path = bundle_path.resolve()

    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")

    with zipfile.ZipFile(bundle_path, "r") as zf:
        mats_jsonl = _load_jsonl_from_zip(zf, "chunks/materials.jsonl")
        tasks_jsonl = _load_jsonl_from_zip(zf, "chunks/tasks.jsonl")
        pack_jsonl = _load_jsonl_from_zip(zf, "chunks/pack.jsonl")
        subs_jsonl = _load_jsonl_from_zip(zf, "chunks/subs.jsonl")

        mats_chunks = [Chunk.from_json(obj) for obj in mats_jsonl]
        task_chunks = [Chunk.from_json(obj) for obj in tasks_jsonl]
        pack_chunks = [Chunk.from_json(obj) for obj in pack_jsonl]
        subs_chunks = [Chunk.from_json(obj) for obj in subs_jsonl]

        meta = _load_json_from_zip(zf, "meta/version_info.json") or {}

    return CEBundle(
        bundle_path=bundle_path,
        materials=mats_chunks,
        tasks=task_chunks,
        pack=pack_chunks,
        subs=subs_chunks,
        meta=meta,
    )


# ----------------------------------------------------------------------
# Sparse keyword retrieval
# ----------------------------------------------------------------------


def _tokenise(text: str) -> List[str]:
    """
    Very simple tokeniser: split on whitespace and punctuation boundaries.
    Case-insensitive.
    """
    import re

    text = text.lower()
    tokens = re.split(r"[^a-z0-9_]+", text)
    return [t for t in tokens if t]


def _score_chunk(chunk: Chunk, query_tokens: List[str]) -> int:
    """
    Deterministic sparse scoring:
    - Tokenise the chunk's `text` and `id`.
    - Score = number of query tokens that appear in the chunk tokens.
    - No semantic expansion, no fuzzy matching.
    """
    corpus_tokens = set(_tokenise(chunk.text) + _tokenise(chunk.id))
    score = 0
    for qt in query_tokens:
        if qt in corpus_tokens:
            score += 1
    return score


def search_chunks(
    bundle: CEBundle,
    query: str,
    domain: str = "all",
    top_k: int = 10,
) -> List[Tuple[Chunk, int]]:
    """
    Search chunks using simple token-overlap scoring.
    domain ∈ {"materials","tasks","pack","subs","all"}.
    Returns list of (Chunk, score), sorted by score desc then id asc.
    """
    query = query.strip()
    if not query:
        return []

    qtoks = _tokenise(query)

    domain = domain.lower()
    domains = bundle.all_domains()

    if domain == "all":
        candidates: List[Chunk] = []
        for lst in domains.values():
            candidates.extend(lst)
    else:
        if domain not in domains:
            raise ValueError(f"Unknown domain '{domain}'. Valid: materials, tasks, pack, subs, all.")
        candidates = domains[domain]

    scored: List[Tuple[Chunk, int]] = []
    for ch in candidates:
        score = _score_chunk(ch, qtoks)
        if score > 0:
            scored.append((ch, score))

    # Sort by score desc, then ID asc for determinism
    scored.sort(key=lambda cs: (-cs[1], cs[0].id))
    return scored[:top_k]


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valesco v2.0 CE Bundle Loader + Sparse Retriever"
    )
    parser.add_argument(
        "--bundle",
        required=True,
        help="Path to CE bundle ZIP, e.g. workspace/outputs/VALESCO_CE_BUNDLE.zip",
    )
    parser.add_argument(
        "--query",
        help="Free-text query to run against the bundle chunks. If omitted, info only.",
    )
    parser.add_argument(
        "--domain",
        default="all",
        help="Domain to search: materials|tasks|pack|subs|all (default: all).",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="Maximum number of results to return (default: 5).",
    )

    args = parser.parse_args()
    bundle_path = Path(args.bundle)

    # Load bundle
    ce = load_ce_bundle(bundle_path)

    # If no query, just print bundle summary
    if not args.query:
        print("CE Bundle loaded.")
        print(f"  Path         : {ce.bundle_path}")
        print(f"  Materials    : {len(ce.materials)} chunks")
        print(f"  Tasks        : {len(ce.tasks)} chunks")
        print(f"  Pack         : {len(ce.pack)} chunks")
        print(f"  Subcontractors: {len(ce.subs)} chunks")
        if ce.meta:
            print("  Meta:")
            for k in sorted(ce.meta.keys()):
                print(f"    {k}: {ce.meta[k]}")
        return

    # Otherwise, perform search
    results = search_chunks(ce, args.query, domain=args.domain, top_k=args.top_k)

    if not results:
        print("No matching chunks found.")
        return

    print(f"Found {len(results)} matching chunks:\n")
    for chunk, score in results:
        print("------------------------------------------------------------")
        print(f"Score   : {score}")
        print(f"ID      : {chunk.id}")
        print(f"Type    : {chunk.type}")
        print(f"Source  : {chunk.source_file}")
        print(f"Path    : {chunk.path}")
        print(f"Text    : {chunk.text[:400]}")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    main()
