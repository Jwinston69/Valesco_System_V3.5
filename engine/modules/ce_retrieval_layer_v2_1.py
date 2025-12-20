# C:/Valesco_System/engine/modules/ce_retrieval_layer_v2.1.py
# CE Retrieval Layer v2.1 (MVP Deterministic Mock Implementation)
# Deterministic, dependency-free, signal-only retrieval mock for Router/Architect/Validator tests.

"""
CE Retrieval Layer v2.1 — MVP Mock

This module provides a minimal deterministic retrieval mechanism suitable for
testing the missing-item subsystem. It returns only:

    hit_count: int
    top_score: float | None
    score_gap_to_next: float | None
    coverage_flags: dict
    retrieved_items: list[dict]

No embeddings, vectors, similarity functions, or external dependencies are used.
All behaviour is static and lookup-based.
"""

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Mock Catalog Dataset (Static, Deterministic)
# ---------------------------------------------------------------------------

MOCK_ITEMS = {
    "clean_match": [
        {
            "id": "A001",
            "name": "Single Clean-Match Item",
            "category": "core",
            "score": 0.98,
        }
    ],
    "ambiguous": [
        {
            "id": "B001",
            "name": "Ambiguous Item 1",
            "category": "core",
            "score": 0.72,
        },
        {
            "id": "B002",
            "name": "Ambiguous Item 2",
            "category": "core",
            "score": 0.71,
        },
        {
            "id": "B003",
            "name": "Ambiguous Item 3",
            "category": "core",
            "score": 0.70,
        },
    ],
    "insufficient": [
        {
            "id": "C001",
            "name": "Weak Coverage Item",
            "category": "misc",
            "score": 0.40,
        }
    ],
    "compatible": [
        {
            "id": "E001",
            "name": "Compatible Item 1",
            "category": "alt",
            "score": 0.65,
        },
        {
            "id": "E002",
            "name": "Compatible Item 2",
            "category": "alt",
            "score": 0.63,
        },
    ],
    "empty": [],  # Used for State D
}


# ---------------------------------------------------------------------------
# Deterministic Routing Map (Keyword → Retrieval Profile)
# ---------------------------------------------------------------------------

PROFILE_MAP = {
    "clean": "clean_match",
    "exact": "clean_match",
    "single": "clean_match",

    "ambiguous": "ambiguous",
    "three": "ambiguous",
    "close": "ambiguous",

    "insufficient": "insufficient",
    "unclear": "insufficient",
    "weak": "insufficient",

    "none": "empty",
    "missing": "empty",
    "nomatch": "empty",

    "compatible": "compatible",
    "alternative": "compatible",
    "alt": "compatible",
}


# ---------------------------------------------------------------------------
# Helper: Map description text → retrieval profile (deterministic)
# ---------------------------------------------------------------------------

def _select_profile(description: str) -> str:
    text = description.lower()
    for key, profile in PROFILE_MAP.items():
        if key in text:
            return profile
    # Default ambiguous profile if nothing matches
    return "ambiguous"


# ---------------------------------------------------------------------------
# Signal Construction Logic (All deterministic, static thresholds)
# ---------------------------------------------------------------------------

def _build_signals(profile: str, items: List[Dict]) -> Dict:
    """
    Construct CE signals deterministically based on the chosen profile.
    Scores are taken directly from MOCK_ITEMS.
    """

    hit_count = len(items)

    if hit_count == 0:
        return {
            "hit_count": 0,
            "top_score": None,
            "score_gap_to_next": None,
            "coverage_flags": {"none": True, "weak": False, "strong": False},
        }

    # Order by provided score (descending)
    ordered = sorted(items, key=lambda x: x["score"], reverse=True)
    top_score = ordered[0]["score"]
    score_gap = None

    if hit_count > 1:
        score_gap = top_score - ordered[1]["score"]

    # Deterministic coverage flag patterns per profile
    if profile == "clean_match":
        coverage = {"strong": True, "weak": False, "conflicting": False}
    elif profile == "ambiguous":
        coverage = {"strong": True, "weak": False, "conflicting": False}
    elif profile == "insufficient":
        coverage = {"strong": False, "weak": True, "conflicting": False}
    elif profile == "compatible":
        coverage = {"strong": True, "compatible": True}
    else:
        coverage = {"weak": True}

    return {
        "hit_count": hit_count,
        "top_score": top_score,
        "score_gap_to_next": score_gap,
        "coverage_flags": coverage,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def retrieve(description: str) -> Dict:
    """
    Deterministic CE retrieval mock.
    Input:
        description: natural-language item description (string)
    Output:
        {
            "hit_count": int,
            "top_score": float | None,
            "score_gap_to_next": float | None,
            "coverage_flags": dict,
            "retrieved_items": list[dict]
        }
    """

    profile = _select_profile(description)
    items = MOCK_ITEMS.get(profile, [])

    signals = _build_signals(profile, items)

    return {
        **signals,
        "retrieved_items": items,
    }


# ---------------------------------------------------------------------------
# Minimal Self-Test (Non-executing placeholder for harness integration)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        "clean item description",
        "ambiguous selection",
        "weak unclear insufficient info",
        "no match none",
        "compatible alternative option",
    ]
    for t in tests:
        print(t, "→", retrieve(t))
