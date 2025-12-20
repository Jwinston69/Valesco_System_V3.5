# C:/Valesco_System/engine/modules/ce_backend_adapter_v3.2.py
# CE Backend Adapter v3.2
#
# Purpose:
#   Convert internal Valesco catalog items into the exact input format
#   required by the real CE backend retrieval API.
#
# Behaviour:
#   - Pure translation layer
#   - No inference or enrichment
#   - No interaction with CE routing/logic
#   - Deterministic and deep-copy safe
#
# Public API:
#   to_ce_backend_item(catalog_item: dict) -> dict
#   to_ce_backend_catalog(catalog_dict: dict) -> list
#   validate_ce_backend_input(item: dict) -> None
#   export_ce_backend_payload(catalog_list: list, path: str) -> None

from typing import Any, Dict, List
import json
import os
import copy


InternalCatalogItem = Dict[str, Any]
CEBackendItem = Dict[str, Any]
InternalCatalogDict = Dict[str, InternalCatalogItem]


# ---------------------------------------------------------------------------
# Internal helpers — validation of internal catalog items
# ---------------------------------------------------------------------------

def _validate_internal_catalog_item(item_id: str, item: InternalCatalogItem) -> None:
    """
    Validate that an internal catalog item conforms to the expected schema:

        {
          "id": str,
          "name": str,
          "category": str,
          "attributes": dict,
          "score_placeholder": float
        }

    Rules:
        - All keys required and no extras.
        - 'id' must match item_id and be a non-empty string.
        - 'name' and 'category' must be non-empty strings.
        - 'attributes' must be a dict and JSON-serializable.
        - 'score_placeholder' must be numeric (int/float).
    """
    if not isinstance(item, dict):
        raise ValueError(f"Internal catalog item '{item_id}' must be a dict.")

    required_keys = {"id", "name", "category", "attributes", "score_placeholder"}
    if set(item.keys()) != required_keys:
        raise ValueError(
            f"Internal catalog item '{item_id}' must contain exactly keys "
            f"{required_keys}, got {set(item.keys())}."
        )

    if not isinstance(item["id"], str) or not item["id"]:
        raise ValueError(f"Internal catalog item '{item_id}' has invalid 'id'.")

    if item["id"] != item_id:
        raise ValueError(
            f"Internal catalog item key '{item_id}' does not match item['id'] '{item['id']}'."
        )

    if not isinstance(item["name"], str) or not item["name"]:
        raise ValueError(f"Internal catalog item '{item_id}' has invalid 'name'.")

    if not isinstance(item["category"], str) or not item["category"]:
        raise ValueError(f"Internal catalog item '{item_id}' has invalid 'category'.")

    attrs = item["attributes"]
    if not isinstance(attrs, dict):
        raise ValueError(f"Internal catalog item '{item_id}' 'attributes' must be a dict.")
    # Ensure JSON-serializable attributes
    try:
        json.dumps(attrs)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(
            f"Internal catalog item '{item_id}' 'attributes' not JSON-serializable."
        ) from exc

    score_placeholder = item["score_placeholder"]
    if not isinstance(score_placeholder, (int, float)):
        raise ValueError(
            f"Internal catalog item '{item_id}' 'score_placeholder' must be numeric."
        )


# ---------------------------------------------------------------------------
# API Function 3 — CE backend input validation
# ---------------------------------------------------------------------------

def validate_ce_backend_input(item: CEBackendItem) -> None:
    """
    Validate that a CE backend item exactly matches the backend requirements:

        {
          "id": str,
          "name": str,
          "category": str,
          "attributes": dict
        }

    Rules:
        - Required keys only: id, name, category, attributes.
        - No extra keys permitted.
        - All values correct types.
        - attributes JSON-serializable.
    """
    if not isinstance(item, dict):
        raise ValueError("CE backend item must be a dict.")

    required_keys = {"id", "name", "category", "attributes"}
    if set(item.keys()) != required_keys:
        raise ValueError(
            f"CE backend item must contain exactly keys {required_keys}, "
            f"got {set(item.keys())}."
        )

    if not isinstance(item["id"], str) or not item["id"]:
        raise ValueError("CE backend item 'id' must be a non-empty string.")

    if not isinstance(item["name"], str) or not item["name"]:
        raise ValueError("CE backend item 'name' must be a non-empty string.")

    if not isinstance(item["category"], str) or not item["category"]:
        raise ValueError("CE backend item 'category' must be a non-empty string.")

    attrs = item["attributes"]
    if not isinstance(attrs, dict):
        raise ValueError("CE backend item 'attributes' must be a dict.")
    try:
        json.dumps(attrs)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("CE backend item 'attributes' not JSON-serializable.") from exc


# ---------------------------------------------------------------------------
# API Function 1 — single item conversion
# ---------------------------------------------------------------------------

def to_ce_backend_item(catalog_item: InternalCatalogItem) -> CEBackendItem:
    """
    Convert a single internal catalog item into the CE backend format.

    Internal format:

        {
          "id": str,
          "name": str,
          "category": str,
          "attributes": dict,
          "score_placeholder": float
        }

    CE backend format:

        {
          "id": str,
          "name": str,
          "category": str,
          "attributes": dict
        }

    Rules:
        - Drop 'score_placeholder'.
        - Preserve all other fields exactly.
        - No modification of attributes.
        - No enrichment.
    """
    if not isinstance(catalog_item, dict):
        raise ValueError("catalog_item must be a dict.")

    item_id = catalog_item.get("id")
    if not isinstance(item_id, str) or not item_id:
        raise ValueError("Internal catalog_item must contain a valid 'id'.")

    # Validate internal schema first
    _validate_internal_catalog_item(item_id, catalog_item)

    # Build CE backend item (deep copy attributes to avoid mutation)
    ce_item: CEBackendItem = {
        "id": catalog_item["id"],
        "name": catalog_item["name"],
        "category": catalog_item["category"],
        "attributes": copy.deepcopy(catalog_item["attributes"]),
    }

    # Validate CE backend schema as a final check
    validate_ce_backend_input(ce_item)

    return ce_item


# ---------------------------------------------------------------------------
# API Function 2 — full catalog conversion
# ---------------------------------------------------------------------------

def to_ce_backend_catalog(catalog_dict: InternalCatalogDict) -> List[CEBackendItem]:
    """
    Convert an internal catalog dictionary into a deterministically ordered
    list of CE backend-ready items.

    Input (internal):

        {
          "A001": { "id": "A001", "name": ..., "category": ..., "attributes": ..., "score_placeholder": ... },
          "B002": { ... },
          ...
        }

    Output (CE backend list, sorted by id):

        [
          {"id": "A001", "name": ..., "category": ..., "attributes": {...}},
          {"id": "B002", "name": ..., "category": ..., "attributes": {...}},
          ...
        ]

    Rules:
        - Sort ascending by 'id'.
        - Validate each internal item before conversion.
        - Validate each CE item after conversion.
        - Produce deep copies (no linkage to input catalog_dict).
        - Raise ValueError on malformed entries.
    """
    if not isinstance(catalog_dict, dict):
        raise ValueError("catalog_dict must be a dict of id → internal catalog item.")

    ce_items: List[CEBackendItem] = []

    for item_id in sorted(catalog_dict.keys()):
        internal_item = catalog_dict[item_id]
        # Validate and convert using single-item adapter
        ce_item = to_ce_backend_item(internal_item)
        ce_items.append(ce_item)

    return ce_items


# ---------------------------------------------------------------------------
# API Function 4 — export CE backend payload
# ---------------------------------------------------------------------------

def export_ce_backend_payload(catalog_list: List[CEBackendItem], path: str) -> None:
    """
    Write the CE-ready catalog list to disk deterministically.

    Requirements:
        - catalog_list must be a list of CE backend items.
        - Pre-validate each item using validate_ce_backend_input.
        - Sort by 'id' ascending before writing.
        - Use deterministic JSON serialization with sorted keys.
        - No added metadata.
    """
    if not isinstance(catalog_list, list):
        raise ValueError("catalog_list must be a list of CE backend items.")

    validated_items: List[CEBackendItem] = []
    for item in catalog_list:
        validate_ce_backend_input(item)
        validated_items.append(copy.deepcopy(item))

    # Deterministic ordering by id
    sorted_items = sorted(validated_items, key=lambda x: x["id"])

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            sorted_items,
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example internal catalog dict
    internal_catalog = {
        "A002": {
            "id": "A002",
            "name": "Example Item 2",
            "category": "wall",
            "attributes": {"thickness": "100mm"},
            "score_placeholder": 0.0,
        },
        "A001": {
            "id": "A001",
            "name": "Example Item 1",
            "category": "wall",
            "attributes": {"finish": "galvanised"},
            "score_placeholder": 0.0,
        },
    }

    backend_list = to_ce_backend_catalog(internal_catalog)
    print("CE backend list:", backend_list)

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "ce_catalog.json")
        export_ce_backend_payload(backend_list, out_path)
        with open(out_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        print("Loaded CE catalog:", loaded)
