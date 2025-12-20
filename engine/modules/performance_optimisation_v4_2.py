# C:/Valesco_System/engine/modules/performance_optimisation_v4.2.py
# Performance Optimisation Layer v4.2
#
# Purpose:
#   Deterministic micro-optimisations for Valesco runtime operations.
#   This module:
#     - Does NOT change estimator behaviour
#     - Does NOT change CE behaviour
#     - Does NOT change pricing, resolver, or ingestion logic
#     - Does NOT alter test semantics
#
# Public API:
#   cached_deepcopy(obj, _cache=None) -> Any
#   sort_by_id(records: list) -> list
#   batch_apply(fn, items: list) -> list
#
# Constraints:
#   - No global/persistent caches (cache lifetime is per-call only).
#   - No concurrency, inference, approximation, or mutation of caller data.
#   - Pure helper utilities only.

from typing import Any, Callable, Dict, List, Optional
import copy


__all__ = [
    "cached_deepcopy",
    "sort_by_id",
    "batch_apply",
]


# ---------------------------------------------------------------------------
# 1. Cached Deep Copy Utility
# ---------------------------------------------------------------------------

def cached_deepcopy(obj: Any, _cache: Optional[Dict[int, Any]] = None) -> Any:
    """
    Deterministic, safe deep-copy cache for repeated structures.

    Behaviour:
        - Cache is keyed by Python id(obj).
        - Cache lifetime is local to this call (no leakage across calls).
        - Only used for immutable or read-only structures:
            * Primitive scalars: int, float, bool, str, None
            * Tuples and frozensets (recursively processed)
        - For all other types, falls back to copy.deepcopy without caching.
        - Input is never mutated.

    Notes:
        - For immutable primitives, the "copy" is simply the object itself.
        - For tuples/frozensets, caching avoids re-copying shared subgraphs
          within a single call while preserving semantics.
    """
    # Initialise per-call cache if not provided
    if _cache is None:
        _cache = {}

    obj_id = id(obj)

    # Immutable primitive types: safe to reuse as-is
    if isinstance(obj, (int, float, bool, str, type(None))):
        # No need to cache primitives; identity and immutability are guaranteed.
        return obj

    # Immutable containers that we treat as read-only and cacheable
    if isinstance(obj, tuple):
        if obj_id in _cache:
            return _cache[obj_id]
        copied_items = tuple(cached_deepcopy(item, _cache=_cache) for item in obj)
        _cache[obj_id] = copied_items
        return copied_items

    if isinstance(obj, frozenset):
        if obj_id in _cache:
            return _cache[obj_id]
        copied_items = frozenset(cached_deepcopy(item, _cache=_cache) for item in obj)
        _cache[obj_id] = copied_items
        return copied_items

    # For all other (potentially mutable) types, fall back to standard deepcopy
    # without caching to avoid behavioural changes.
    return copy.deepcopy(obj)


# ---------------------------------------------------------------------------
# 2. Fast Sorting Helper
# ---------------------------------------------------------------------------

def sort_by_id(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deterministically sort a list of record dicts by record["id"].

    Behaviour:
        - Returns a NEW list (original input list is not mutated).
        - Sort key is record["id"].
        - Validates that each record has an "id" key.
        - Raises ValueError if any record is missing "id".

    Notes:
        - Elements in the returned list are the same objects as in the input
          (no deep copy), so caller must treat them as read-only if needed.
    """
    if not isinstance(records, list):
        raise ValueError("records must be a list.")

    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise ValueError(f"Record at index {idx} must be a dict.")
        if "id" not in rec:
            raise ValueError(f"Record at index {idx} is missing required 'id' key.")

    # Return a new list, sorted deterministically by "id".
    return sorted(records, key=lambda r: r["id"])


# ---------------------------------------------------------------------------
# 3. Batch Processing Utility
# ---------------------------------------------------------------------------

def batch_apply(fn: Callable[[Any], Any], items: List[Any]) -> List[Any]:
    """
    Apply a function to each item in a list, returning a list of results.

    Behaviour:
        - Applies fn to items in order.
        - Returns list of results in the same order.
        - Does NOT mutate the input list.
        - Does NOT catch any exceptions — they propagate to caller.
        - Deterministic ordering and behaviour.

    Example:
        results = batch_apply(lambda x: x * 2, [1, 2, 3])
        # results == [2, 4, 6]
    """
    if not isinstance(items, list):
        raise ValueError("items must be a list.")

    # Do not mutate input; simply iterate and collect results.
    return [fn(item) for item in items]


# ---------------------------------------------------------------------------
# Optional local smoke test (no side effects outside this module)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # cached_deepcopy smoke test
    t = (1, (2, 3))
    copy1 = cached_deepcopy(t)
    copy2 = cached_deepcopy(t)
    print("cached_deepcopy works:", copy1 == copy2, copy1 is not t)

    # sort_by_id smoke test
    records = [{"id": "B"}, {"id": "A"}]
    print("sort_by_id:", sort_by_id(records))

    # batch_apply smoke test
    print("batch_apply:", batch_apply(lambda x: x * 2, [1, 2, 3]))
