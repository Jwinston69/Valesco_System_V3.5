# C:/Valesco_System/engine/modules/quantity_logic_v2.1.py
# Quantity Logic v2.1 — Deterministic, Minimal Quantity Handling Layer
#
# Purpose:
#   - Allow users or upstream processes to set or clear quantities on items.
#   - Provide stable, deterministic quantity snapshots for pricing.
#   - Never infer, calculate, or derive quantities.
#
# Constraints:
#   - No geometric interpretation.
#   - No default quantities.
#   - No unit conversions.
#   - No modification of catalog metadata.
#   - Deterministic behaviour only.

from typing import Any, Dict, List, Optional
import copy


def set_quantity(item_index: int, quantity: float, estimate_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assign a numeric quantity to the specified item.

    Requirements:
        - quantity must be numeric (int or float)
        - item_index must exist
        - item may be catalog or provisional
        - metadata must not be altered
    """
    if not isinstance(quantity, (int, float)):
        raise ValueError("Quantity must be numeric.")

    items = estimate_snapshot.get("items", [])
    if not (0 <= item_index < len(items)):
        raise IndexError("Item index out of range.")

    # Deep copy to avoid mutating the input snapshot.
    updated = copy.deepcopy(estimate_snapshot)
    updated["items"][item_index]["quantity"] = float(quantity)

    return updated


def clear_quantity(item_index: int, estimate_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove the 'quantity' field from the specified item, if present.
    No inference or replacement value is applied.
    """
    items = estimate_snapshot.get("items", [])
    if not (0 <= item_index < len(items)):
        raise IndexError("Item index out of range.")

    updated = copy.deepcopy(estimate_snapshot)
    updated["items"][item_index].pop("quantity", None)

    return updated


def apply_quantities(estimate_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identity-style pass-through function.

    Ensures each item has a quantity field of either:
        - numeric quantity, or
        - no 'quantity' field (None implied)

    No inference or creation of missing fields. Only validate and copy.
    """
    copied = copy.deepcopy(estimate_snapshot)
    for item in copied.get("items", []):
        q = item.get("quantity")
        if not isinstance(q, (int, float)):
            # Leave it unset (None implied), but do not set anything new.
            if "quantity" in item:
                # Remove non-numeric or invalid quantity field safely.
                item.pop("quantity", None)
    return copied


# ---------------------------------------------------------------------------
# Optional Smoke Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    snap = {
        "items": [
            {"item_id": "A001", "source": "catalog", "display_name": "Clean", "metadata": {}, "status": "confirmed"},
            {"item_id": None, "source": "provisional", "display_name": "Custom", "metadata": {}, "status": "confirmed"},
        ]
    }

    s1 = set_quantity(0, 5.0, snap)
    s2 = set_quantity(1, 3.25, s1)
    s3 = clear_quantity(0, s2)
    s4 = apply_quantities(s3)
    print(s4)
