# C:/Valesco_System/engine/modules/pack_ingestion_v3.1.py
# Pack Ingestion Pipeline v3.1
#
# Purpose:
#   - Ingest external pack (simple assembly) definitions
#   - Validate and normalize into deterministic internal schema
#   - Provide safe, CE-compatible structures for:
#       * Assembly/Pack resolver
#       * Pricing engine
#       * CE backend metadata
#       * Material Manager extensions
#
# Behaviour:
#   - No inference
#   - No enrichment
#   - No interaction with pricing or CE backends
#   - Pure ingestion, validation, normalization, persistence
#
# Public API:
#   load_raw_packs(json_list: list) -> list
#   build_internal_pack_library(normalized_list: list) -> dict
#   save_internal_pack_library(pack_dict: dict, path: str) -> None
#   load_internal_pack_library(path: str) -> dict

from typing import Any, Dict, List
import json
import os
import copy


ExternalPack = Dict[str, Any]
NormalizedPack = Dict[str, Any]
PackLibrary = Dict[str, NormalizedPack]


# ---------------------------------------------------------------------------
# Internal helpers — validation & normalization
# ---------------------------------------------------------------------------

def _validate_external_pack(raw: ExternalPack) -> None:
    """
    Validate a raw external pack definition:

        {
          "id": "PACK001",
          "name": "Basic Timber Wall Pack",
          "items": [
            {"catalog_id": "A001", "multiplier": 1.0},
            {"catalog_id": "A002", "multiplier": 0.4}
          ]
        }

    Rules:
        - id: required string
        - name: required string
        - items: required non-empty list
        - Each item: {"catalog_id": str, "multiplier": numeric >= 0}
        - No unsupported top-level keys
        - No unsupported item keys
        - No inference or defaults
    """
    if not isinstance(raw, dict):
        raise ValueError("Pack definition must be a dict.")

    required_keys = {"id", "name", "items"}
    if not required_keys.issubset(raw.keys()):
        missing = required_keys - set(raw.keys())
        raise ValueError(f"Pack missing required keys: {missing}")

    extra_top = set(raw.keys()) - required_keys
    if extra_top:
        raise ValueError(f"Pack has unsupported top-level keys: {extra_top}")

    pack_id = raw["id"]
    name = raw["name"]
    items = raw["items"]

    if not isinstance(pack_id, str) or not pack_id:
        raise ValueError("Pack 'id' must be a non-empty string.")
    if not isinstance(name, str) or not name:
        raise ValueError(f"Pack '{pack_id}' 'name' must be a non-empty string.")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError(f"Pack '{pack_id}' 'items' must be a non-empty list.")

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item #{idx} in pack '{pack_id}' must be a dict.")

        required_item_keys = {"catalog_id", "multiplier"}
        if set(item.keys()) != required_item_keys:
            raise ValueError(
                f"Item #{idx} in pack '{pack_id}' must have keys {required_item_keys}, "
                f"found {set(item.keys())}."
            )

        catalog_id = item["catalog_id"]
        multiplier = item["multiplier"]

        if not isinstance(catalog_id, str) or not catalog_id:
            raise ValueError(
                f"Item #{idx} in pack '{pack_id}' has invalid 'catalog_id'."
            )

        if not isinstance(multiplier, (int, float)):
            raise ValueError(
                f"Item #{idx} in pack '{pack_id}' has non-numeric multiplier."
            )
        if multiplier < 0:
            raise ValueError(
                f"Item #{idx} in pack '{pack_id}' has negative multiplier."
            )

        # Ensure JSON-serializable (defensive)
        try:
            json.dumps(item)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Item #{idx} in pack '{pack_id}' is not JSON-serializable."
            ) from exc


def _normalize_pack(raw: ExternalPack) -> NormalizedPack:
    """
    Normalize a validated external pack into internal schema:

        {
            "id": str,
            "name": str,
            "items": [
                {"catalog_id": str, "multiplier": float},
                ...
            ]
        }

    Rules:
        - Multipliers cast to float
        - catalog_id preserved exactly
    """
    pack_id = raw["id"]
    name = raw["name"]
    items = raw["items"]

    normalized_items: List[Dict[str, Any]] = []
    for item in items:
        normalized_items.append(
            {
                "catalog_id": item["catalog_id"],
                "multiplier": float(item["multiplier"]),
            }
        )

    return {
        "id": pack_id,
        "name": name,
        "items": normalized_items,
    }


def _validate_internal_pack(pack_id: str, pack: NormalizedPack) -> None:
    """
    Validate a pack against the internal normalized schema.
    """
    if not isinstance(pack, dict):
        raise ValueError(f"Internal pack '{pack_id}' must be a dict.")

    if set(pack.keys()) != {"id", "name", "items"}:
        raise ValueError(
            f"Internal pack '{pack_id}' must contain exactly 'id', 'name', 'items'."
        )

    if not isinstance(pack["id"], str) or not pack["id"]:
        raise ValueError(f"Internal pack '{pack_id}' has invalid 'id'.")
    if not isinstance(pack["name"], str) or not pack["name"]:
        raise ValueError(f"Internal pack '{pack_id}' has invalid 'name'.")

    items = pack["items"]
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError(f"Internal pack '{pack_id}' 'items' must be a non-empty list.")

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(
                f"Internal pack '{pack_id}' item #{idx} must be a dict."
            )
        if set(item.keys()) != {"catalog_id", "multiplier"}:
            raise ValueError(
                f"Internal pack '{pack_id}' item #{idx} must have keys "
                f"{{'catalog_id','multiplier'}}, got {set(item.keys())}."
            )

        catalog_id = item["catalog_id"]
        multiplier = item["multiplier"]

        if not isinstance(catalog_id, str) or not catalog_id:
            raise ValueError(
                f"Internal pack '{pack_id}' item #{idx} has invalid 'catalog_id'."
            )
        if not isinstance(multiplier, (int, float)):
            raise ValueError(
                f"Internal pack '{pack_id}' item #{idx} has non-numeric multiplier."
            )
        if multiplier < 0:
            raise ValueError(
                f"Internal pack '{pack_id}' item #{idx} has negative multiplier."
            )

        # Ensure JSON-serializable (defensive)
        try:
            json.dumps(item)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Internal pack '{pack_id}' item #{idx} not JSON-serializable."
            ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_raw_packs(json_list: List[ExternalPack]) -> List[NormalizedPack]:
    """
    Load and normalize a list of external pack definitions.

    Steps:
        - Validate each raw pack schema.
        - Normalize to internal schema.
        - Deduplicate by 'id' (first-wins).
        - Sort by 'id' ascending.

    Returns:
        List[NormalizedPack]
    """
    if not isinstance(json_list, list):
        raise ValueError("Pack list input must be a list.")

    seen: Dict[str, NormalizedPack] = {}
    order: List[str] = []

    for raw in json_list:
        _validate_external_pack(raw)
        pack_id = raw["id"]
        if pack_id in seen:
            # First occurrence wins.
            continue
        normalized = _normalize_pack(raw)
        seen[pack_id] = normalized
        order.append(pack_id)

    # Deterministic: sorted by ID
    sorted_ids = sorted(order)
    return [seen[pid] for pid in sorted_ids]


def build_internal_pack_library(normalized_list: List[NormalizedPack]) -> PackLibrary:
    """
    Build an internal pack library:

        { id: NormalizedPack }

    Requirements:
        - normalized_list must contain valid normalized packs.
        - IDs must be unique.
        - Deterministic ordering (by sorted id keys).
    """
    if not isinstance(normalized_list, list):
        raise ValueError("normalized_list must be a list of normalized packs.")

    library: PackLibrary = {}
    for pack in normalized_list:
        if not isinstance(pack, dict):
            raise ValueError("Each normalized pack must be a dict.")
        pack_id = pack.get("id")
        if not isinstance(pack_id, str) or not pack_id:
            raise ValueError("Normalized pack missing valid 'id'.")

        if pack_id in library:
            raise ValueError(f"Duplicate pack id '{pack_id}' in normalized list.")

        # Validate internal schema before insertion
        _validate_internal_pack(pack_id, pack)
        library[pack_id] = copy.deepcopy(pack)

    return library


def save_internal_pack_library(pack_dict: PackLibrary, path: str) -> None:
    """
    Save an internal pack library to disk with deterministic JSON serialization.

    Requirements:
        - pack_dict is a dict[id → NormalizedPack]
        - Validate all packs before saving.
        - Write with sorted keys at all levels.
    """
    if not isinstance(pack_dict, dict):
        raise ValueError("pack_dict must be a dict of id → pack.")

    for pid, pack in pack_dict.items():
        _validate_internal_pack(pid, pack)

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Ensure deterministic pack ordering by ID
    ordered: Dict[str, Any] = {}
    for pid in sorted(pack_dict.keys()):
        ordered[pid] = copy.deepcopy(pack_dict[pid])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            ordered,
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,  # inner dict keys sorted
        )


def load_internal_pack_library(path: str) -> PackLibrary:
    """
    Load an internal pack library from disk and validate schema.

    Returns:
        PackLibrary (id → NormalizedPack)
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Internal pack library file must contain a dict keyed by pack id.")

    library: PackLibrary = {}
    for pid, pack in data.items():
        if not isinstance(pid, str) or not pid:
            raise ValueError("Pack library keys (ids) must be non-empty strings.")
        _validate_internal_pack(pid, pack)

        if pid in library:
            raise ValueError(f"Duplicate pack id '{pid}' in loaded library.")

        library[pid] = copy.deepcopy(pack)

    return library


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    example_packs = [
        {
            "id": "PACK002",
            "name": "Wall Pack B",
            "items": [
                {"catalog_id": "A001", "multiplier": 1.0},
                {"catalog_id": "A002", "multiplier": 0.4},
            ],
        },
        {
            "id": "PACK001",
            "name": "Wall Pack A",
            "items": [
                {"catalog_id": "A010", "multiplier": 0.5},
            ],
        },
    ]

    normalized = load_raw_packs(example_packs)
    print("Normalized packs:", normalized)

    library = build_internal_pack_library(normalized)
    print("Library:", library)

    # Round-trip save/load
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "packs.json")
        save_internal_pack_library(library, path)
        loaded = load_internal_pack_library(path)
        print("Loaded:", loaded)
