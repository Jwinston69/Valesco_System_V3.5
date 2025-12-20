# C:/Valesco_System/engine/modules/assembly_pack_resolver_v3.2.py
# Assembly / Pack Resolver Engine v3.2
#
# Purpose:
#   Deterministic resolver for expanding packs (simple assemblies) into
#   explicit catalog-line components for downstream quantity and pricing.
#
# Behaviour:
#   - Pure transformation layer
#   - No pricing, no estimation
#   - No CE, no metadata lookups
#   - No inference or enrichment
#
# Public API:
#   validate_pack_structure(pack: dict) -> None
#   resolve_pack(pack: dict, base_quantity: float) -> list[dict]
#   resolve_multiple_packs(pack_library: dict, selections: list[dict]) -> list[dict]

from typing import Any, Dict, List
import copy


NormalizedPack = Dict[str, Any]
PackLibrary = Dict[str, NormalizedPack]
ResolvedComponent = Dict[str, Any]


# ---------------------------------------------------------------------------
# API Function 3 — Validation
# ---------------------------------------------------------------------------

def validate_pack_structure(pack: NormalizedPack) -> None:
    """
    Validate that a pack conforms to the normalized internal schema:

        {
            "id": str,
            "name": str,
            "items": [
                {"catalog_id": str, "multiplier": float},
                ...
            ]
        }

    Raises ValueError on:
        - Missing / extra keys
        - Empty items list
        - Non-numeric multiplier
        - Negative multiplier
        - Invalid catalog_id
    """
    if not isinstance(pack, dict):
        raise ValueError("Pack must be a dict.")

    required_keys = {"id", "name", "items"}
    if set(pack.keys()) != required_keys:
        raise ValueError(
            f"Pack must contain exactly keys {required_keys}, got {set(pack.keys())}."
        )

    pack_id = pack["id"]
    name = pack["name"]
    items = pack["items"]

    if not isinstance(pack_id, str) or not pack_id:
        raise ValueError("Pack 'id' must be a non-empty string.")
    if not isinstance(name, str) or not name:
        raise ValueError(f"Pack '{pack_id}' 'name' must be a non-empty string.")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError(f"Pack '{pack_id}' 'items' must be a non-empty list.")

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item #{idx} in pack '{pack_id}' must be a dict.")

        if set(item.keys()) != {"catalog_id", "multiplier"}:
            raise ValueError(
                f"Item #{idx} in pack '{pack_id}' must have keys "
                f"{{'catalog_id','multiplier'}}, got {set(item.keys())}."
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


# ---------------------------------------------------------------------------
# API Function 1 — Single Pack Resolution
# ---------------------------------------------------------------------------

def resolve_pack(pack: NormalizedPack, base_quantity: float) -> List[ResolvedComponent]:
    """
    Resolve a single normalized pack record into expanded catalog components.

    Input:
        pack          : normalized pack dict (validated)
        base_quantity : user-supplied numeric quantity

    Output:
        [
            {
                "catalog_id": str,
                "derived_quantity": float,   # base_quantity × multiplier
                "multiplier": float
            },
            ...
        ]

    Rules:
        - base_quantity must be numeric (int/float)
        - multipliers must be >= 0 (enforced by validation)
        - derived_quantity = base_quantity * multiplier
        - no inference, no CE/pricing interaction
        - must not mutate input pack
    """
    validate_pack_structure(pack)

    if not isinstance(base_quantity, (int, float)):
        raise ValueError("base_quantity must be numeric (int or float).")

    base_quantity_f = float(base_quantity)

    items = pack["items"]
    resolved: List[ResolvedComponent] = []

    # Deterministic: iterate in the given items order
    for item in items:
        multiplier = float(item["multiplier"])
        # multiplier >= 0 already enforced by validate_pack_structure
        derived_quantity = base_quantity_f * multiplier

        resolved.append(
            {
                "catalog_id": item["catalog_id"],
                "derived_quantity": derived_quantity,
                "multiplier": multiplier,
            }
        )

    return resolved


# ---------------------------------------------------------------------------
# API Function 2 — Multiple Pack Resolution
# ---------------------------------------------------------------------------

def resolve_multiple_packs(
    pack_library: PackLibrary,
    selections: List[Dict[str, Any]],
) -> List[ResolvedComponent]:
    """
    Resolve multiple pack selections against a pack library.

    pack_library:
        { pack_id: NormalizedPack }

    selections:
        [
            {"pack_id": "PACK001", "quantity": 12.0},
            {"pack_id": "PACK002", "quantity": 5.0},
            ...
        ]

    Output:
        Flattened list of expanded components in deterministic order:
        - Selections processed in list order
        - Within each selection, pack items resolved in pack.items order
        [
            {"catalog_id": ..., "derived_quantity": ..., "multiplier": ...},
            ...
        ]

    Rules:
        - Missing pack_id in library → ValueError
        - quantity must be numeric (int/float)
        - No mutation of pack_library or selections
        - Deterministic concatenation of per-pack results
    """
    if not isinstance(pack_library, dict):
        raise ValueError("pack_library must be a dict of pack_id → pack.")

    if not isinstance(selections, list):
        raise ValueError("selections must be a list of selection dicts.")

    expanded: List[ResolvedComponent] = []

    # Deterministic: iterate selections as given
    for idx, selection in enumerate(selections):
        if not isinstance(selection, dict):
            raise ValueError(f"Selection #{idx} must be a dict.")

        if "pack_id" not in selection or "quantity" not in selection:
            raise ValueError(
                f"Selection #{idx} must contain 'pack_id' and 'quantity'."
            )

        pack_id = selection["pack_id"]
        quantity = selection["quantity"]

        if not isinstance(pack_id, str) or not pack_id:
            raise ValueError(f"Selection #{idx} has invalid 'pack_id'.")

        if not isinstance(quantity, (int, float)):
            raise ValueError(
                f"Selection #{idx} for pack '{pack_id}' has non-numeric quantity."
            )

        if pack_id not in pack_library:
            raise ValueError(f"Pack '{pack_id}' not found in pack_library.")

        # Deep-copy the pack to ensure no accidental mutation
        pack_copy = copy.deepcopy(pack_library[pack_id])

        resolved_for_pack = resolve_pack(pack_copy, float(quantity))
        expanded.extend(resolved_for_pack)

    return expanded


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example normalized packs
    pack1 = {
        "id": "PACK001",
        "name": "Basic Timber Wall Pack",
        "items": [
            {"catalog_id": "A001", "multiplier": 1.0},
            {"catalog_id": "A002", "multiplier": 0.4},
        ],
    }

    pack2 = {
        "id": "PACK002",
        "name": "Alt Timber Wall Pack",
        "items": [
            {"catalog_id": "A003", "multiplier": 2.0},
        ],
    }

    print("Resolve single pack:", resolve_pack(pack1, 10.0))

    library = {
        "PACK001": pack1,
        "PACK002": pack2,
    }

    selections = [
        {"pack_id": "PACK001", "quantity": 10.0},
        {"pack_id": "PACK002", "quantity": 5.0},
    ]

    print("Resolve multiple packs:", resolve_multiple_packs(library, selections))
