# C:/Valesco_System/engine/modules/rate_library_ingestion_v3.1.py
# Rate Library Ingestion v3.1 — Deterministic Structured Rate Pipeline
#
# Purpose:
#   - Ingest external structured rate records
#   - Validate and normalize into an internal rate library schema
#   - Provide deterministic, CE-safe storage for future pricing engine use
#
# Constraints:
#   - No inference or enrichment
#   - No productivity or behaviour logic
#   - No stochastic ordering
#   - Pure translation → validation → normalization → deterministic storage

from typing import Any, Dict, List
import json
import os
import copy


ExternalRateRecord = Dict[str, Any]
NormalizedRateRecord = Dict[str, Any]
RateLibraryDict = Dict[str, NormalizedRateRecord]


# ---------------------------------------------------------------------------
# Helpers — Validation and Normalization
# ---------------------------------------------------------------------------

_ALLOWED_COMPONENT_KEYS = {"material", "labour", "plant", "overhead"}
_INTERNAL_COMPONENT_KEYS = ["material", "labour", "plant", "overhead"]


def _validate_external_rate_record(raw: ExternalRateRecord) -> None:
    """
    Validate that a raw external rate record matches the required schema:

        {
          "id": "R001",
          "description": "100mm insulation labour rate",
          "components": {
              "material": {"rate": 4.20, "unit": "m2"},
              "labour":   {"rate": 6.50, "unit": "m2"},
              "plant":    {"rate": 0.00, "unit": "m2"}
          }
        }

    Rules:
        - id: required, non-empty string
        - description: required string
        - components: dict of zero or more of {material, labour, plant, overhead}
        - No extra top-level fields
        - Component dicts:
            * keys: "rate", "unit" only
            * "rate": numeric (int/float)
            * "unit": non-empty string
            * JSON-serializable
    """
    if not isinstance(raw, dict):
        raise ValueError("Rate record must be a dict.")

    required_keys = {"id", "description", "components"}
    if not required_keys.issubset(raw.keys()):
        missing = required_keys - set(raw.keys())
        raise ValueError(f"Rate record missing required keys: {missing}")

    # No extra fields beyond required ones
    extra_top = set(raw.keys()) - required_keys
    if extra_top:
        raise ValueError(f"Rate record has unexpected top-level keys: {extra_top}")

    rate_id = raw["id"]
    desc = raw["description"]
    components = raw["components"]

    if not isinstance(rate_id, str) or not rate_id:
        raise ValueError("Rate record 'id' must be a non-empty string.")
    if not isinstance(desc, str):
        raise ValueError("Rate record 'description' must be a string.")
    if not isinstance(components, dict):
        raise ValueError("Rate record 'components' must be a dict.")

    # Validate components subset and types
    for comp_name, comp_value in components.items():
        if comp_name not in _ALLOWED_COMPONENT_KEYS:
            raise ValueError(f"Unsupported component '{comp_name}' in rate record '{rate_id}'.")

        if comp_value is None:
            # Explicit None is allowed, though unusual; treat as invalid here
            raise ValueError(f"Component '{comp_name}' in '{rate_id}' must be a dict, not None.")

        if not isinstance(comp_value, dict):
            raise ValueError(f"Component '{comp_name}' in '{rate_id}' must be a dict.")

        # Must have exactly 'rate' and 'unit'
        if set(comp_value.keys()) != {"rate", "unit"}:
            raise ValueError(
                f"Component '{comp_name}' in '{rate_id}' must have keys ['rate', 'unit'] only."
            )

        rate_val = comp_value["rate"]
        unit_val = comp_value["unit"]

        if not isinstance(rate_val, (int, float)):
            raise ValueError(f"Component '{comp_name}' in '{rate_id}' has non-numeric rate.")
        if not isinstance(unit_val, str) or not unit_val:
            raise ValueError(f"Component '{comp_name}' in '{rate_id}' has invalid unit.")

        # Ensure JSON-serializable
        try:
            json.dumps(comp_value)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(f"Component '{comp_name}' in '{rate_id}' not JSON-serializable.") from exc


def _normalize_rate_record(raw: ExternalRateRecord) -> NormalizedRateRecord:
    """
    Normalize validated external rate record to internal schema:

        {
            "id": str,
            "description": str,
            "components": {
                "material": {"rate": float, "unit": str} | None,
                "labour":   {"rate": float, "unit": str} | None,
                "plant":    {"rate": float, "unit": str} | None,
                "overhead": {"rate": float, "unit": str} | None
            }
        }

    Missing components are set to None. No arithmetic, no inference.
    """
    rate_id = raw["id"]
    desc = raw["description"]
    components = raw["components"]

    # Build deterministic components dict with all four keys
    internal_components: Dict[str, Any] = {}
    for key in _INTERNAL_COMPONENT_KEYS:
        if key in components:
            comp = components[key]
            # Safe to cast; validated already
            internal_components[key] = {
                "rate": float(comp["rate"]),
                "unit": str(comp["unit"]),
            }
        else:
            internal_components[key] = None

    normalized: NormalizedRateRecord = {
        "id": rate_id,
        "description": desc,
        "components": internal_components,
    }
    return normalized


def _validate_internal_rate_record(item_id: str, record: NormalizedRateRecord) -> None:
    """
    Validate internal schema correctness for use in load/save operations.
    """
    if not isinstance(record, dict):
        raise ValueError(f"Internal rate record for id '{item_id}' must be a dict.")

    if set(record.keys()) != {"id", "description", "components"}:
        raise ValueError(f"Internal rate record '{item_id}' has incorrect keys: {set(record.keys())}")

    if not isinstance(record["id"], str) or not record["id"]:
        raise ValueError(f"Internal rate record '{item_id}' has invalid 'id'.")
    if not isinstance(record["description"], str):
        raise ValueError(f"Internal rate record '{item_id}' has invalid 'description'.")

    comps = record["components"]
    if not isinstance(comps, dict):
        raise ValueError(f"Internal rate record '{item_id}' has invalid 'components' field.")

    if set(comps.keys()) != set(_INTERNAL_COMPONENT_KEYS):
        raise ValueError(
            f"Internal rate record '{item_id}' components must have keys {_INTERNAL_COMPONENT_KEYS}."
        )

    for comp_name in _INTERNAL_COMPONENT_KEYS:
        comp_val = comps[comp_name]
        if comp_val is None:
            continue
        if not isinstance(comp_val, dict):
            raise ValueError(f"Component '{comp_name}' in '{item_id}' must be a dict or None.")
        if set(comp_val.keys()) != {"rate", "unit"}:
            raise ValueError(
                f"Component '{comp_name}' in '{item_id}' must contain exactly ['rate', 'unit']."
            )
        if not isinstance(comp_val["rate"], (int, float)):
            raise ValueError(f"Component '{comp_name}' in '{item_id}' has non-numeric rate.")
        if not isinstance(comp_val["unit"], str) or not comp_val["unit"]:
            raise ValueError(f"Component '{comp_name}' in '{item_id}' has invalid unit.")
        # JSON-serializable check
        try:
            json.dumps(comp_val)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(
                f"Component '{comp_name}' in '{item_id}' contains non-serializable values."
            ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_raw_rate_library(json_list: List[ExternalRateRecord]) -> List[NormalizedRateRecord]:
    """
    Load and normalize a list of external rate records.

    Steps:
        - Validate each raw entry.
        - Normalize to internal schema.
        - Deduplicate by first-encountered ID (stable).
        - Sort resulting records by ID ascending.

    Returns:
        List[NormalizedRateRecord]
    """
    if not isinstance(json_list, list):
        raise ValueError("Rate library input must be a list of rate records.")

    seen: Dict[str, NormalizedRateRecord] = {}
    order: List[str] = []

    for raw in json_list:
        _validate_external_rate_record(raw)
        rate_id = raw["id"]
        if rate_id in seen:
            # First occurrence wins for deduplication.
            continue
        normalized = _normalize_rate_record(raw)
        seen[rate_id] = normalized
        order.append(rate_id)

    # Deterministic sort by ID ascending
    sorted_ids = sorted(order)
    return [seen[rid] for rid in sorted_ids]


def build_internal_rate_library(normalized_list: List[NormalizedRateRecord]) -> RateLibraryDict:
    """
    Build an internal rate library dict from normalized records:

        { id: NormalizedRateRecord }

    Requirements:
        - IDs must be unique.
        - Input normalized_list is assumed validated, but we perform a safety check.
    """
    if not isinstance(normalized_list, list):
        raise ValueError("normalized_list must be a list of normalized rate records.")

    library: RateLibraryDict = {}
    for record in normalized_list:
        if not isinstance(record, dict):
            raise ValueError("Each normalized rate record must be a dict.")
        rate_id = record.get("id")
        if not isinstance(rate_id, str) or not rate_id:
            raise ValueError("Normalized rate record missing valid 'id'.")
        if rate_id in library:
            raise ValueError(f"Duplicate rate id '{rate_id}' in normalized list.")

        # Validate internal schema before insertion
        _validate_internal_rate_record(rate_id, record)
        library[rate_id] = record

    return library


def save_internal_rate_library(library_dict: RateLibraryDict, path: str) -> None:
    """
    Persist the internal rate library to disk as JSON.

    Requirements:
        - Deterministic JSON serialization
        - Sorted keys at top-level and within records

    Note:
        - Assumes library_dict has been built via build_internal_rate_library.
    """
    if not isinstance(library_dict, dict):
        raise ValueError("library_dict must be a dict of rate records.")

    # Validate all records prior to saving
    for rid, record in library_dict.items():
        _validate_internal_rate_record(rid, record)

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # For determinism, ensure we write items in sorted ID order
    ordered_library: Dict[str, Any] = {}
    for rid in sorted(library_dict.keys()):
        # Deep copy to avoid accidental mutation
        ordered_library[rid] = copy.deepcopy(library_dict[rid])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            ordered_library,
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,  # sort inner dict keys for determinism
        )


def load_internal_rate_library(path: str) -> RateLibraryDict:
    """
    Load an internal rate library from disk and validate its schema.

    Returns:
        RateLibraryDict (id → NormalizedRateRecord)
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Internal rate library file must contain a dict keyed by rate id.")

    # Validate each record structurally
    library: RateLibraryDict = {}
    for rid, record in data.items():
        if not isinstance(rid, str) or not rid:
            raise ValueError("Rate library keys (ids) must be non-empty strings.")
        _validate_internal_rate_record(rid, record)
        if rid in library:
            raise ValueError(f"Duplicate rate id '{rid}' in loaded library.")
        library[rid] = record

    return library


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    example_rates = [
        {
            "id": "R002",
            "description": "Example labour + material",
            "components": {
                "material": {"rate": 4.20, "unit": "m2"},
                "labour": {"rate": 6.50, "unit": "m2"},
            },
        },
        {
            "id": "R001",
            "description": "Material only rate",
            "components": {
                "material": {"rate": 3.10, "unit": "m2"},
                "plant": {"rate": 0.00, "unit": "m2"},
            },
        },
    ]

    normalized = load_raw_rate_library(example_rates)
    library = build_internal_rate_library(normalized)
    print("Normalized:", normalized)
    print("Library:", library)
