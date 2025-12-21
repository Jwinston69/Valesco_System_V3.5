# C:/Valesco_System/engine/modules/catalog_ce_adapter_v3.1.py
# Catalog → CE Backend Adapter v3.1
#
# Purpose:
#   Translate the internal normalized catalog (from ingestion v3.0) into
#   the CE backend–ready catalog format defined in the CE Backend Integration Plan v3.0.
#
# This module:
#   - Adds no metadata
#   - Performs no inference
#   - Is fully deterministic
#   - Only transforms structure by removing score_placeholder and sorting by ID
#
# Expected Input (internal catalog dict):
#   {
#       "A001": {
#           "id": "A001",
#           "name": "Item A",
#           "category": "core",
#           "attributes": {...},
#           "score_placeholder": 0.0
#       },
#       "B002": {...}
#   }
#
# Expected Output (for CE backend):
#   [
#       {
#           "id": "A001",
#           "name": "Item A",
#           "category": "core",
#           "attributes": {...}
#       },
#       ...
#   ]
#
# No enrichment, no compatibility inference, no similarity fields.

from typing import Any, Dict, List
import json
import os


# ---------------------------------------------------------------------------
# 1. catalog_to_ce_backend_format
# ---------------------------------------------------------------------------

def catalog_to_ce_backend_format(internal_catalog: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert internal ingestion output into CE-backend-ready list format.
    - Drops score_placeholder
    - Preserves all other fields exactly
    - Sorts ascending by ID
    - No enrichment
    """
    if not isinstance(internal_catalog, dict):
        raise ValueError("internal_catalog must be a dict {id: item_dict}.")

    for key in internal_catalog.keys():
        if not isinstance(key, str):
            raise ValueError("Catalog keys (ids) must be strings.")

    # Collect IDs deterministically
    sorted_ids = sorted(internal_catalog.keys())

    output: List[Dict[str, Any]] = []
    for item_id in sorted_ids:
        item = internal_catalog[item_id]

        # Validate minimal expected structure from ingestion
        if not isinstance(item, dict):
            raise ValueError(f"Catalog item for id '{item_id}' must be a dict.")
        for key in ("id", "name", "category", "attributes"):
            if key not in item:
                raise ValueError(f"Catalog item '{item_id}' missing field '{key}'.")

        if not isinstance(item["id"], str):
            raise ValueError(f"Catalog item '{item_id}' has invalid 'id' type.")
        if not isinstance(item["name"], str):
            raise ValueError(f"Catalog item '{item_id}' has invalid 'name' type.")
        if not isinstance(item["category"], str):
            raise ValueError(f"Catalog item '{item_id}' has invalid 'category' type.")
        if not isinstance(item["attributes"], dict):
            raise ValueError(f"Catalog item '{item_id}' has invalid 'attributes' type.")

        # Construct backend-ready item (drop score_placeholder)
        backend_item = {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "attributes": item["attributes"],
        }
        output.append(backend_item)

    return output


# ---------------------------------------------------------------------------
# 2. validate_ce_backend_catalog
# ---------------------------------------------------------------------------

def validate_ce_backend_catalog(output_list: List[Dict[str, Any]]) -> bool:
    """
    Validate that output_list conforms exactly to CE backend schema:
    - List of dicts
    - Keys: ["id", "name", "category", "attributes"]
    - Unique IDs
    - Sorted ascending by ID
    - attributes must be JSON-serializable dict
    """

    if not isinstance(output_list, list):
        raise ValueError("CE backend catalog must be a list.")

    required_keys = ["id", "name", "category", "attributes"]
    seen_ids = []

    # Validate structure, types, and JSON-serializability
    for idx, item in enumerate(output_list):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {idx} must be a dict.")

        # Must contain exactly required keys
        if set(item.keys()) != set(required_keys):
            raise ValueError(f"Item at index {idx} has incorrect keys: {set(item.keys())}")

        # Validate types
        if not isinstance(item["id"],    str): raise ValueError(f"Item at index {idx} has invalid id.")
        if not isinstance(item["name"],  str): raise ValueError(f"Item at index {idx} has invalid name.")
        if not isinstance(item["category"], str): raise ValueError(f"Item at index {idx} has invalid category.")
        if not isinstance(item["attributes"], dict): raise ValueError(f"Item at index {idx} has invalid attributes.")

        # Check JSON-serializable attributes (deep check by dumping)
        try:
            json.dumps(item["attributes"])
        except Exception:
            raise ValueError(f"Item at index {idx} contains non-serializable attributes.")

        seen_ids.append(item["id"])

    # Check ID uniqueness
    if len(seen_ids) != len(set(seen_ids)):
        raise ValueError("Duplicate IDs found in CE backend catalog.")

    # Check sorted ascending
    if seen_ids != sorted(seen_ids):
        raise ValueError("CE backend catalog items must be sorted ascending by ID.")

    return True


# ---------------------------------------------------------------------------
# 3. export_ce_backend_catalog
# ---------------------------------------------------------------------------

def export_ce_backend_catalog(output_list: List[Dict[str, Any]], path: str) -> None:
    """
    Write CE backend catalog to disk with:
    - Deterministic JSON serialization
    - Sorted keys
    - No additional metadata
    """

    # Validate before writing
    validate_ce_backend_catalog(output_list)

    # Ensure directory exists
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            output_list,
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,  # Deterministic field ordering
        )


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    internal_catalog = {
        "B002": {
            "id": "B002",
            "name": "Product B",
            "category": "core",
            "attributes": {"finish": "primer"},
            "score_placeholder": 0.0,
        },
        "A001": {
            "id": "A001",
            "name": "Product A",
            "category": "core",
            "attributes": {"thickness": "100mm"},
            "score_placeholder": 0.0,
        },
    }

    ce_list = catalog_to_ce_backend_format(internal_catalog)
    print("Backend List:", ce_list)
    print("Validation:", validate_ce_backend_catalog(ce_list))
