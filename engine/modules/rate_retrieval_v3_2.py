# C:/Valesco_System/engine/modules/rate_retrieval_v3.2.py
# Production Rate Retrieval Layer v3.2
#
# Purpose:
#   Deterministic, read-only access layer for the internal rate library.
#   - No build-up logic
#   - No arithmetic
#   - No inference or enrichment
#   - Pure retrieval of normalized rate records
#
# API:
#   load_rate_library(path: str) -> dict
#   get_rate_record(rate_library: dict, rate_id: str) -> dict | None
#   list_rate_records(rate_library: dict) -> list
#
# This behaves analogously to the CE Retrieval Layer, but for pricing rates.

from typing import Any, Dict, List, Optional
import copy

from engine.modules.rate_library_ingestion_v3_1 import (
    load_internal_rate_library,
)


# ---------------------------------------------------------------------------
# 1. load_rate_library
# ---------------------------------------------------------------------------

def load_rate_library(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load and validate an internal rate library from disk using
    load_internal_rate_library.

    Additional shallow schema checks:
        - keys must be strings
        - each record must contain: "id", "description", "components"
        - "components" must contain the four component keys:
              material, labour, plant, overhead

    Returns:
        dict[str, dict] — validated, unmodified internal library.
    """
    library = load_internal_rate_library(path)

    if not isinstance(library, dict):
        raise ValueError("Rate library must be a dict of id → record.")

    for rid, record in library.items():
        if not isinstance(rid, str) or not rid:
            raise ValueError("Rate library keys must be non-empty strings.")

        # Required top-level fields
        if set(record.keys()) != {"id", "description", "components"}:
            raise ValueError(
                f"Rate record '{rid}' missing required keys "
                f"{ {'id','description','components'} }."
            )

        components = record.get("components")
        if not isinstance(components, dict):
            raise ValueError(f"Rate record '{rid}' has invalid 'components'.")

        required_component_keys = {"material", "labour", "plant", "overhead"}
        if set(components.keys()) != required_component_keys:
            raise ValueError(
                f"Rate record '{rid}' components must contain keys "
                f"{required_component_keys}."
            )

    return library


# ---------------------------------------------------------------------------
# 2. get_rate_record
# ---------------------------------------------------------------------------

def get_rate_record(
    rate_library: Dict[str, Dict[str, Any]],
    rate_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a deep copy of the rate record for the given rate_id.

    Returns:
        dict (deep copy of record) or None if not found.

    Requirements:
        - Must not modify the original library
        - Must perform no inference or enrichment
        - Must preserve all component fields exactly
    """
    if rate_id not in rate_library:
        return None
    return copy.deepcopy(rate_library[rate_id])


# ---------------------------------------------------------------------------
# 3. list_rate_records
# ---------------------------------------------------------------------------

def list_rate_records(
    rate_library: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Return a list of deep-copy rate records sorted by ID ascending.

    Requirements:
        - Must not mutate internal structures
        - Must not infer missing components
        - Must return deep copies of each record
    """
    if not isinstance(rate_library, dict):
        raise ValueError("rate_library must be a dict.")

    sorted_ids = sorted(rate_library.keys())
    return [copy.deepcopy(rate_library[rid]) for rid in sorted_ids]


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import tempfile
    import os
    from engine.modules.rate_library_ingestion_v3_1 import (
        load_raw_rate_library,
        build_internal_rate_library,
        save_internal_rate_library,
    )

    # Create a small example library
    external_rates = [
        {
            "id": "R002",
            "description": "Example rate 2",
            "components": {
                "material": {"rate": 4.2, "unit": "m2"},
                "labour": {"rate": 6.5, "unit": "m2"},
            },
        },
        {
            "id": "R001",
            "description": "Example rate 1",
            "components": {
                "material": {"rate": 3.1, "unit": "m2"},
            },
        },
    ]

    normalized = load_raw_rate_library(external_rates)
    library = build_internal_rate_library(normalized)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "rates.json")
        save_internal_rate_library(library, path)

        loaded = load_rate_library(path)
        print("Loaded:", loaded)

        print("Record R001:", get_rate_record(loaded, "R001"))
        print("Record R003:", get_rate_record(loaded, "R003"))
        print("All Records:", list_rate_records(loaded))
