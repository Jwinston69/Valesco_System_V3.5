# C:/Valesco_System/engine/modules/material_manager_v2.1.py
# Material Manager v2.1 — Deterministic Raw Metadata Provider
#
# Provides raw, unmodified catalog metadata for the MVP system.
# No inference, no substitutes, no compatibility logic, no enrichment.

from typing import Any, Dict, List, Optional
import copy

# ---------------------------------------------------------------------------
# Static Mock Catalog (MUST match CE Retrieval Layer definitions)
# ---------------------------------------------------------------------------

MOCK_CATALOG: Dict[str, Dict[str, Any]] = {
    "A001": {"id": "A001", "name": "Single Clean-Match Item", "category": "core", "score": 0.98},
    "B001": {"id": "B001", "name": "Ambiguous Item 1", "category": "core", "score": 0.72},
    "B002": {"id": "B002", "name": "Ambiguous Item 2", "category": "core", "score": 0.71},
    "B003": {"id": "B003", "name": "Ambiguous Item 3", "category": "core", "score": 0.70},
    "C001": {"id": "C001", "name": "Weak Coverage Item", "category": "misc", "score": 0.40},
    "E001": {"id": "E001", "name": "Compatible Item 1", "category": "alt", "score": 0.65},
    "E002": {"id": "E002", "name": "Compatible Item 2", "category": "alt", "score": 0.63},
}

# ---------------------------------------------------------------------------
# API FUNCTIONS
# ---------------------------------------------------------------------------

def get_metadata(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Return raw catalog metadata for an item ID, or None if unknown.
    Must not modify or enrich the metadata.
    """
    item = MOCK_CATALOG.get(item_id)
    return copy.deepcopy(item) if item is not None else None


def list_all_items() -> List[Dict[str, Any]]:
    """
    Return a list containing copies of all catalog entries.
    """
    return [copy.deepcopy(v) for v in MOCK_CATALOG.values()]


def exists(item_id: str) -> bool:
    """
    Deterministic existence check against the static catalog.
    """
    return item_id in MOCK_CATALOG


# ---------------------------------------------------------------------------
# Minimal Smoke Test (Optional)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(get_metadata("A001"))
    print(exists("C001"))
    print(list_all_items())
