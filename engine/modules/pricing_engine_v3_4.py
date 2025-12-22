# C:/Valesco_System/engine/modules/pricing_engine_v3.4.py
# Pricing Engine v3.4 — Deterministic Production Pricing Integration
#
# Purpose:
#   Integrate:
#     - Rate Retrieval Layer v3.2
#     - Rate Build-Up Layer v3.3
#     - Merge Agent snapshot structure
#     - Quantity Logic v2.1 (via attached quantities)
#     - Pricing Logic v2.1 constraints
#
# Behaviour:
#   - Pure, deterministic cost assembly
#   - No inference, no enrichment
#   - No modification of estimator behaviour or CE routing
#
# Public API:
#   price_line_item(item: dict, rate_library: dict) -> dict
#   price_estimate_snapshot(snapshot: dict, rate_library: dict) -> dict
#   price_estimate_for_runner(rate_library_path: str) -> callable

from typing import Any, Callable, Dict, List, Optional

import copy

from engine.modules.rate_retrieval_v3_2 import (
    load_rate_library,
    get_rate_record,
)
from engine.modules import rate_build_up_v3_3 as rate_build_up
from engine.modules import pack_registry_v3_5 as pack_registry


LineItem = Dict[str, Any]
RateLibrary = Dict[str, Dict[str, Any]]
PricingResult = Dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_pack_registry() -> None:
    try:
        pack_registry.require_registry()
    except Exception as exc:
        raise RuntimeError("Pricing blocked: pack registry incomplete.") from exc


def _get_quantity_from_item(item: LineItem) -> Optional[float]:
    """
    Extract a numeric quantity from a line item if present.

    Rules:
        - If 'quantity' is missing → None
        - If present but not numeric → None (treated as quantity_required)
    """
    if "quantity" not in item:
        return None
    q = item["quantity"]
    if isinstance(q, (int, float)):
        return float(q)
    return None


def _is_provisional(item: LineItem) -> bool:
    """
    Determine if a line item is provisional based on the Merge Agent schema.
    """
    return item.get("source") == "provisional"


def _is_catalog(item: LineItem) -> bool:
    """
    Determine if a line item is a catalog item.
    """
    return item.get("source") == "catalog"


# ---------------------------------------------------------------------------
# 1. price_line_item
# ---------------------------------------------------------------------------

def price_line_item(item: LineItem, rate_library: RateLibrary) -> PricingResult:
    """
    Price a single line item from the Merge Agent snapshot.

    Behaviour:
        - Provisional line:
            {"pricing": "user-supplied only"}

        - Catalog line:
            * Extract item_id from item["item_id"]
            * Retrieve rate record via get_rate_record(rate_library, rate_id)
            * If no rate record → {"pricing": "no_pricing_defined"}
            * If quantity missing or non-numeric → {"pricing": "quantity_required"}
            * Build rate via build_up_rate(rate_record)
            * If built["unit"] is None (no components) and quantity exists → error
            * Compute:
                {
                    "item_id": item_id,
                    "unit": built["unit"],
                    "unit_rate": built["total_rate"],
                    "quantity": quantity,
                    "total_cost": quantity * built["total_rate"],
                }

    Rules:
        - No inference of quantity
        - No fallback substitutions
        - No dimensional conversions
        - If built["unit"] is None but quantity exists → ValueError
        - If built["total_rate"] is None but quantity exists → treated as no_pricing_defined
    """
    _require_pack_registry()
    # Provisional items: never internally priced.
    if _is_provisional(item):
        return {"pricing": "user-supplied only"}

    # Non-catalog (unknown) sources: do not attempt pricing.
    if not _is_catalog(item):
        return {"pricing": "no_pricing_defined"}

    item_id = item.get("item_id")
    if not isinstance(item_id, str) or not item_id:
        # Without a valid item_id we cannot look up a rate.
        return {"pricing": "no_pricing_defined"}

    # Retrieve rate record from library
    rate_record = get_rate_record(rate_library, item_id)
    if rate_record is None:
        return {"pricing": "no_pricing_defined"}

    # Extract quantity (no inference)
    quantity = _get_quantity_from_item(item)
    if quantity is None:
        # Quantity is required but not supplied or invalid
        return {"pricing": "quantity_required"}

    # Build up rate from components (may raise ValueError for mismatched units, etc.)
    built = rate_build_up.build_up_rate(rate_record)

    unit = built.get("unit")
    total_rate = built.get("total_rate")

    # If no unit but we have a quantity, pricing is not defined
    if unit is None:
        raise ValueError(
            f"Built rate for item '{item_id}' has no unit while quantity is provided."
        )

    # If no total rate but we have a quantity, treat as missing pricing
    if total_rate is None:
        return {"pricing": "no_pricing_defined"}

    # Deterministic arithmetic
    total_cost = quantity * float(total_rate)

    return {
        "item_id": item_id,
        "unit": unit,
        "unit_rate": float(total_rate),
        "quantity": quantity,
        "total_cost": total_cost,
    }


# ---------------------------------------------------------------------------
# 2. price_estimate_snapshot
# ---------------------------------------------------------------------------

def price_estimate_snapshot(snapshot: Dict[str, Any], rate_library: RateLibrary) -> Dict[str, Any]:
    """
    Price an entire estimate snapshot produced by the Merge Agent.

    Expected snapshot shape (from ESTIMATE_MODEL):

        {
            "items": [
                {
                    "item_id": str | None,
                    "source": "catalog" | "provisional",
                    "display_name": str,
                    "metadata": dict,
                    "status": "confirmed",
                    # Optional:
                    # "quantity": float
                    # "allowance": ...
                },
                ...
            ]
        }

    Output structure:

        {
            "lines": [ per-line pricing results in order ],
            "total_cost": float
        }

    Rules:
        - Apply price_line_item to each item in order.
        - Provisional lines:
            * "pricing": "user-supplied only"
            * Do not contribute to total_cost.
        - Lines with "quantity_required":
            * Included in 'lines' as such, do not contribute to total_cost.
        - Lines with "no_pricing_defined":
            * Included, do not contribute.
        - Lines with numeric pricing:
            * total_cost is sum of their 'total_cost'.
        - Deterministic ordering preserved.
    """
    _require_pack_registry()
    items: List[LineItem] = snapshot.get("items", [])
    if not isinstance(items, list):
        raise ValueError("snapshot['items'] must be a list.")

    lines: List[PricingResult] = []
    total_cost: float = 0.0

    for item in items:
        # Use a shallow copy to avoid any accidental mutation
        line_item = copy.deepcopy(item)
        priced = price_line_item(line_item, rate_library)
        lines.append(priced)

        # Sum only fully priced catalog items with numeric totals
        if (
            isinstance(priced, dict)
            and "total_cost" in priced
            and isinstance(priced["total_cost"], (int, float))
        ):
            total_cost += float(priced["total_cost"])

    return {
        "lines": lines,
        "total_cost": float(total_cost),
    }


# ---------------------------------------------------------------------------
# 3. price_estimate_for_runner
# ---------------------------------------------------------------------------

def price_estimate_for_runner(rate_library_path: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Prepare a pricing function for use by a Runner (v3.x).

    Behaviour:
        - Loads the rate library once, from rate_library_path, via load_rate_library.
        - Returns a callable fn(snapshot) which:
            * Applies price_estimate_snapshot(snapshot, rate_library)
            * Returns the pricing result.

    This function:
        - Does not alter snapshot structures.
        - Does not introduce side effects beyond reading the rate library.
    """
    rate_library = load_rate_library(rate_library_path)

    def _price_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
        return price_estimate_snapshot(snapshot, rate_library)

    return _price_snapshot


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # This block is for ad-hoc manual verification only.
    # It will not be used in automated builds and contains no non-determinism.
    from engine.modules.rate_library_ingestion_v3_1 import (
        load_raw_rate_library,
        build_internal_rate_library,
        save_internal_rate_library,
    )
    import tempfile
    import os

    # Create a small example rate library and snapshot
    example_rates = [
        {
            "id": "A001",
            "description": "Example assembled rate",
            "components": {
                "material": {"rate": 4.2, "unit": "m2"},
                "labour": {"rate": 6.5, "unit": "m2"},
            },
        }
    ]

    normalized = load_raw_rate_library(example_rates)
    library = build_internal_rate_library(normalized)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "rates.json")
        save_internal_rate_library(library, path)

        price_fn = price_estimate_for_runner(path)

        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Example Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 10.0,
                },
                {
                    "item_id": None,
                    "source": "provisional",
                    "display_name": "Custom Item",
                    "metadata": {},
                    "status": "confirmed",
                },
            ]
        }

        result = price_fn(snapshot)
        print("Pricing result:", result)
