# C:/Valesco_System/engine/modules/merge_agent_v2.1.py
# Merge Agent v2.1 — Deterministic Integration of Confirmed User Decisions
#
# This module maintains a simple in-memory estimate model.
# It:
#   - never classifies items,
#   - never enriches catalog metadata,
#   - never applies CE logic,
#   - only records Estimator-confirmed decisions in a deterministic structure.

from typing import Any, Dict, List, Optional
import copy

# ---------------------------------------------------------------------------
# In-Memory Estimate Model
# ---------------------------------------------------------------------------

ESTIMATE_MODEL: Dict[str, List[Dict[str, Any]]] = {
    "items": []
}


# ---------------------------------------------------------------------------
# API FUNCTIONS
# ---------------------------------------------------------------------------

def init_estimate() -> None:
    """
    Reset the in-memory estimate model to an empty state.
    """
    ESTIMATE_MODEL["items"] = []


def add_catalog_item(item: Dict[str, Any]) -> None:
    """
    Add a CE-approved catalog item into the estimate.

    The item must come directly from items_presented (Estimator Runtime output).
    Metadata must not be modified or enriched.
    """
    entry = {
        "item_id": item.get("id"),
        "source": "catalog",
        "display_name": item.get("name", ""),
        "metadata": item,      # store raw item dict
        "status": "confirmed",
    }
    ESTIMATE_MODEL["items"].append(entry)


def add_provisional_item(description: str) -> None:
    """
    Used when user indicates the item is non-standard or not found in catalog.
    No metadata, no enrichment.
    """
    entry = {
        "item_id": None,
        "source": "provisional",
        "display_name": description,
        "metadata": {},
        "status": "confirmed",
    }
    ESTIMATE_MODEL["items"].append(entry)


def update_provisional_allowance(index: int, allowance: Any) -> None:
    """
    Attaches an allowance to an existing provisional line item.

    This is a simple setter. No inference or interpretation is performed.
    """
    if 0 <= index < len(ESTIMATE_MODEL["items"]):
        ESTIMATE_MODEL["items"][index]["allowance"] = allowance


def get_estimate_snapshot() -> Dict[str, Any]:
    """
    Return a deep copy of the current estimate model.
    """
    return copy.deepcopy(ESTIMATE_MODEL)


# ---------------------------------------------------------------------------
# Minimal smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_estimate()
    add_catalog_item({"id": "A001", "name": "Clean Item", "score": 0.98})
    add_provisional_item("Non-standard bracket")
    update_provisional_allowance(1, "15%")
    print(get_estimate_snapshot())
