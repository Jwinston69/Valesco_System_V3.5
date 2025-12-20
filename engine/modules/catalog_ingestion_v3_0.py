# C:/Valesco_System/engine/modules/catalog_ingestion_v3.0.py
# Catalog Ingestion v3.0 — Deterministic Material Catalog Pipeline
#
# Purpose:
#   - Ingest external manufacturer/supplier catalog data
#   - Normalize to the internal catalog schema used by:
#       * CE backend
#       * Material Manager
#       * Validator
#       * Pricing Logic (future)
#       * Estimator (via structured metadata only)
#
# Constraints:
#   - No inference, enrichment, or interpretation
#   - No CE logic
#   - No compatibility tagging or similarity metadata
#   - Deterministic deduplication and ordering

from typing import Any, Dict, List
from collections import OrderedDict
import json
import os


# ---------------------------------------------------------------------------
# Internal Types
# ---------------------------------------------------------------------------

ExternalItem = Dict[str, Any]
NormalizedItem = Dict[str, Any]
CatalogDict = Dict[str, NormalizedItem]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_external_item(item: ExternalItem) -> None:
    """
    Validate that an external catalog item conforms to the expected schema:

        {
          "id": "A001",
          "name": "Product Name",
          "category": "string",
          "attributes": { ... }
        }

    Raises ValueError if invalid.
    """
    if not isinstance(item, dict):
        raise ValueError("External item must be a dict.")

    required_keys = ("id", "name", "category", "attributes")
    for key in required_keys:
        if key not in item:
            raise ValueError(f"Missing required key '{key}' in external item.")

    if not isinstance(item["id"], str) or not item["id"]:
        raise ValueError("Item 'id' must be a non-empty string.")
    if not isinstance(item["name"], str):
        raise ValueError("Item 'name' must be a string.")
    if not isinstance(item["category"], str):
        raise ValueError("Item 'category' must be a string.")
    if not isinstance(item["attributes"], dict):
        raise ValueError("Item 'attributes' must be a dict.")


def _normalize_item(item: ExternalItem) -> NormalizedItem:
    """
    Normalize a validated external item to the internal schema:

        {
            "id": str,
            "name": str,
            "category": str,
            "attributes": dict,     # raw, not enriched
            "score_placeholder": 0.0
        }

    No enrichment, no interpretation, no extra fields.
    """
    # Explicit key insertion order to preserve JSON ordering downstream.
    normalized: "OrderedDict[str, Any]" = OrderedDict()
    normalized["id"] = item["id"]
    normalized["name"] = item["name"]
    normalized["category"] = item["category"]
    normalized["attributes"] = item["attributes"]
    normalized["score_placeholder"] = 0.0
    return normalized  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_raw_catalog(json_list: List[ExternalItem]) -> List[NormalizedItem]:
    """
    Accept a list of raw external catalog items and return a normalized list.

    Behaviour:
        - Validates each item against the external schema.
        - Deduplicates by ID in a stable way (first occurrence wins).
        - Sorts resulting unique items by ID ascending.
        - Produces items conforming to the internal schema.

    No inference, no enrichment, no CE logic.
    """
    if not isinstance(json_list, list):
        raise ValueError("json_list must be a list of external items.")

    # Stable deduplication by ID: first occurrence wins.
    seen: Dict[str, NormalizedItem] = {}
    order: List[str] = []

    for raw in json_list:
        _validate_external_item(raw)
        item_id = raw["id"]
        if item_id in seen:
            # Duplicate ID found; ignore later entries to preserve stability.
            continue
        normalized = _normalize_item(raw)
        seen[item_id] = normalized
        order.append(item_id)

    # Sort IDs ascending while preserving mapping to normalized items.
    sorted_ids = sorted(order)
    normalized_list = [seen[item_id] for item_id in sorted_ids]
    return normalized_list


def build_internal_catalog(normalized_list: List[NormalizedItem]) -> CatalogDict:
    """
    Build the internal catalog dict:

        { id: item_dict }

    Requirements:
        - All items must already conform to the internal schema.
        - IDs must be unique.
        - Resulting dict must be deterministic.

    Deduplication is assumed to have been done in load_raw_catalog.
    """
    catalog: CatalogDict = {}
    for item in normalized_list:
        if not isinstance(item, dict):
            raise ValueError("Normalized item must be a dict.")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ValueError("Normalized item missing valid 'id'.")
        if item_id in catalog:
            # This should not happen if load_raw_catalog was used correctly.
            raise ValueError(f"Duplicate id '{item_id}' in normalized list.")
        catalog[item_id] = item
    return catalog


def save_internal_catalog(catalog_dict: CatalogDict, path: str) -> None:
    """
    Persist the internal catalog dict to disk as JSON.

    Requirements:
        - Preserve JSON key ordering within each item as inserted.
        - No additional fields are introduced.
        - Deterministic output for the same catalog_dict.

    Note: Python 3.7+ preserves dict insertion order; we rely on the
    normalized items having keys inserted in the desired order.
    """
    # Ensure directory exists if path includes directories.
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Write with stable formatting.
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            catalog_dict,
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_internal_catalog(path: str) -> CatalogDict:
    """
    Load an internal catalog previously written by save_internal_catalog.

    Returns:
        {id: item_dict}

    No transformation is applied; the catalog is returned as-is.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Internal catalog file must contain a dict of items.")

    # Simple structural check; deep validation is a responsibility of upstream processes.
    for item_id, item in data.items():
        if not isinstance(item_id, str):
            raise ValueError("Catalog keys (ids) must be strings.")
        if not isinstance(item, dict):
            raise ValueError(f"Catalog item for id '{item_id}' must be a dict.")
    return data  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example external catalog list
    external_catalog = [
        {
            "id": "B002",
            "name": "Example Product B002",
            "category": "secondary",
            "attributes": {"thickness": "50mm", "finish": "primer"},
        },
        {
            "id": "A001",
            "name": "Example Product A001",
            "category": "primary",
            "attributes": {"thickness": "100mm", "finish": "galvanised"},
        },
        # Duplicate id (ignored, first wins)
        {
            "id": "A001",
            "name": "Duplicate Product A001",
            "category": "primary",
            "attributes": {"thickness": "100mm", "finish": "galvanised"},
        },
    ]

    normalized = load_raw_catalog(external_catalog)
    catalog = build_internal_catalog(normalized)

    # Display in deterministic order
    print("Normalized list:", normalized)
    print("Internal catalog:", catalog)
