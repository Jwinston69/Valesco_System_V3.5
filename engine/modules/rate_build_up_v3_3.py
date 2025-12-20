# C:/Valesco_System/engine/modules/rate_build_up_v3.3.py
# Rate Build-Up Layer v3.3
#
# Purpose:
#   Production-safe build-up engine that converts normalized rate records
#   into explicit, deterministic assembled rates for pricing.
#
# Behaviour:
#   - Pure arithmetic aggregation of existing components
#   - No inference of missing components
#   - No unit conversion or substitution
#   - No CE, Estimator, or catalog access
#
# Public API:
#   build_up_rate(rate_record: dict) -> dict
#   build_up_library(rate_library: dict) -> dict

from typing import Any, Dict
import copy


NormalizedRateRecord = Dict[str, Any]
BuiltUpRateRecord = Dict[str, Any]
RateLibraryDict = Dict[str, NormalizedRateRecord]
BuiltUpRateLibraryDict = Dict[str, BuiltUpRateRecord]

_COMPONENT_KEYS = ("material", "labour", "plant", "overhead")


# ---------------------------------------------------------------------------
# Internal validation helpers
# ---------------------------------------------------------------------------

def _validate_normalized_rate_record(rate_record: NormalizedRateRecord) -> None:
    """
    Validate that rate_record conforms to the expected normalized schema:

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

    Also enforces:
        - Non-negative numeric rates
        - Proper units for non-None components
    """
    if not isinstance(rate_record, dict):
        raise ValueError("rate_record must be a dict.")

    required_top = {"id", "description", "components"}
    if set(rate_record.keys()) != required_top:
        raise ValueError(
            f"rate_record must contain exactly keys {required_top}, got {set(rate_record.keys())}."
        )

    rid = rate_record["id"]
    desc = rate_record["description"]
    comps = rate_record["components"]

    if not isinstance(rid, str) or not rid:
        raise ValueError("rate_record 'id' must be a non-empty string.")
    if not isinstance(desc, str):
        raise ValueError(f"rate_record '{rid}' 'description' must be a string.")
    if not isinstance(comps, dict):
        raise ValueError(f"rate_record '{rid}' 'components' must be a dict.")

    if set(comps.keys()) != set(_COMPONENT_KEYS):
        raise ValueError(
            f"rate_record '{rid}' components must contain keys {_COMPONENT_KEYS}."
        )

    for comp_name in _COMPONENT_KEYS:
        comp_val = comps[comp_name]
        if comp_val is None:
            continue

        if not isinstance(comp_val, dict):
            raise ValueError(
                f"Component '{comp_name}' in rate_record '{rid}' must be dict or None."
            )

        if set(comp_val.keys()) != {"rate", "unit"}:
            raise ValueError(
                f"Component '{comp_name}' in rate_record '{rid}' must have keys ['rate','unit']."
            )

        rate_val = comp_val["rate"]
        unit_val = comp_val["unit"]

        if not isinstance(rate_val, (int, float)):
            raise ValueError(
                f"Component '{comp_name}' in rate_record '{rid}' has non-numeric rate."
            )
        if rate_val < 0:
            raise ValueError(
                f"Component '{comp_name}' in rate_record '{rid}' has negative rate."
            )
        if not isinstance(unit_val, str) or not unit_val:
            raise ValueError(
                f"Component '{comp_name}' in rate_record '{rid}' has invalid unit."
            )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_up_rate(rate_record: NormalizedRateRecord) -> BuiltUpRateRecord:
    """
    Build up a single normalized rate record into an assembled rate:

    Input (normalized):

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

    Output (built-up):

        {
            "id": str,
            "description": str,
            "components": { ... same shape as input ... },
            "total_rate": float | None,
            "unit": str | None
        }

    Rules:
        - total_rate = sum of all non-None component rates
        - units of all non-None components must match
        - if units mismatch → ValueError
        - if no components present → total_rate = None, unit = None
        - no unit inference or conversion
        - no mutation of input record
    """
    # Validate input structure and values
    _validate_normalized_rate_record(rate_record)

    # Work on a deep copy to ensure no mutation of input
    rec_copy: NormalizedRateRecord = copy.deepcopy(rate_record)
    rid = rec_copy["id"]
    comps = rec_copy["components"]

    total_rate: float = 0.0
    any_component = False
    units_seen = set()

    for comp_name in _COMPONENT_KEYS:
        comp_val = comps[comp_name]
        if comp_val is None:
            continue

        any_component = True
        rate_val = float(comp_val["rate"])
        unit_val = comp_val["unit"]

        units_seen.add(unit_val)
        total_rate += rate_val

    if not any_component:
        # No components with rates: no total_rate, no unit
        unit: Any = None
        total: Any = None
    else:
        if len(units_seen) > 1:
            raise ValueError(
                f"Rate record '{rid}' has mismatched units across components: {units_seen}."
            )
        unit = next(iter(units_seen))
        total = float(total_rate)

    built: BuiltUpRateRecord = {
        "id": rec_copy["id"],
        "description": rec_copy["description"],
        # Ensure components dict is present and a deep copy
        "components": rec_copy["components"],
        "total_rate": total,
        "unit": unit,
    }
    return built


def build_up_library(rate_library: RateLibraryDict) -> BuiltUpRateLibraryDict:
    """
    Apply build_up_rate to every entry in the rate library.

    Input:
        rate_library: {id: normalized_rate_record}

    Output:
        {id: built_up_rate_record}

    Requirements:
        - Deterministic ordering (insertion by sorted id)
        - No mutation of input library
        - Deep copies of all data
    """
    if not isinstance(rate_library, dict):
        raise ValueError("rate_library must be a dict of id → rate_record.")

    built_library: BuiltUpRateLibraryDict = {}

    for rid in sorted(rate_library.keys()):
        record = rate_library[rid]
        built_library[rid] = build_up_rate(record)

    return built_library


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    example_rate = {
        "id": "R001",
        "description": "Material + labour example",
        "components": {
            "material": {"rate": 4.2, "unit": "m2"},
            "labour": {"rate": 6.5, "unit": "m2"},
            "plant": None,
            "overhead": None,
        },
    }

    built = build_up_rate(example_rate)
    print("Built-up rate:", built)

    library = {
        "R001": example_rate,
        "R002": {
            "id": "R002",
            "description": "Material only",
            "components": {
                "material": {"rate": 3.1, "unit": "m2"},
                "labour": None,
                "plant": None,
                "overhead": None,
            },
        },
    }

    built_lib = build_up_library(library)
    print("Built-up library:", built_lib)
