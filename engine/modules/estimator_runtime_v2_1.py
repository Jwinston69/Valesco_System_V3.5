# C:/Valesco_System/engine/modules/estimator_runtime_v2.1.py
# Estimator Runtime Integration Layer v2.1
#
# This module implements the Estimator’s runtime engine for missing-item flows.
# It:
#   - consumes Validator-approved Router/Architect payloads,
#   - produces operation-level instructions for UI/frontend/test harness,
#   - never accesses CE internals,
#   - never modifies catalog items,
#   - never applies missing-item decision logic.
#
# Behaviour is strictly deterministic.

from typing import Any, Dict, List, Optional, Callable
import copy
import os
from pathlib import Path

import engine.modules.resource_builder as resource_builder
from engine.modules import pack_registry_v3_5 as pack_registry
from engine.modules import pricing_engine_v3_4 as pricing_engine


_RATE_LIBRARY_ENV = "VALESCO_RATE_LIBRARY_PATH"
_PRICING_FN: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
_PRICING_FN_PATH: Optional[str] = None


def _map_required_action_to_next_action(required_action: str) -> Optional[str]:
    """
    Map Architect-level required_estimator_action to runtime next_action.
    """
    if required_action == "CONFIRM_MATCH":
        return "AWAIT_CONFIRMATION"
    if required_action == "CHOOSE_ITEM":
        return "AWAIT_SELECTION"
    if required_action == "PROVIDE_CLARIFICATION":
        return "AWAIT_CLARIFICATION"
    if required_action == "REVISE_DESCRIPTION":
        return "AWAIT_REVISION"
    return None


def _handle_confirmation_reply(user_reply: str) -> Dict[str, Any]:
    """
    Deterministic interpretation of confirmation replies.
    """
    reply = (user_reply or "").strip().lower()
    affirmative = {"yes", "y", "confirm", "ok", "okay", "accepted", "accept", "true", "1"}
    if reply in affirmative:
        return {"user_decision": "CONFIRMED"}
    return {"user_decision": "REJECTED"}


def _handle_selection_reply(items: List[Dict[str, Any]], user_reply: str) -> Dict[str, Any]:
    """
    Deterministic interpretation of selection replies.
    Matches either 1-based index or exact item 'id'.
    """
    reply = (user_reply or "").strip()

    # Try 1-based numeric index
    if reply.isdigit():
        idx = int(reply)
        if 1 <= idx <= len(items):
            item = items[idx - 1]
            item_id = item.get("id")
            return {"user_decision": "SELECTED", "item_id": item_id}

    # Try direct ID match
    for item in items:
        if str(item.get("id")) == reply:
            return {"user_decision": "SELECTED", "item_id": item.get("id")}

    return {"user_decision": "INVALID_SELECTION"}


def _require_pricing_output(pricing_output: Any) -> Dict[str, Any]:
    """
    Enforce the pricing output contract for Estimator Runtime.
    """
    if pricing_output is None:
        raise RuntimeError("Pricing failed: output missing.")
    if not isinstance(pricing_output, dict):
        raise RuntimeError("Pricing failed: output invalid.")
    items = pricing_output.get("items")
    if not isinstance(items, list):
        raise RuntimeError("Pricing failed: output invalid.")
    if not items:
        raise RuntimeError("Pricing failed: output empty.")
    for entry in items:
        if not isinstance(entry, dict):
            raise RuntimeError("Pricing failed: output invalid.")
    return pricing_output


def _resolve_rate_library_path(rate_library_path: Optional[str] = None) -> str:
    raw = rate_library_path or os.environ.get(_RATE_LIBRARY_ENV, "")
    path = raw.strip()
    if not path:
        raise RuntimeError("Pricing failed: rate library path not configured.")
    resolved = Path(path).expanduser()
    if not resolved.is_file():
        raise RuntimeError(f"Pricing failed: rate library not found at {resolved}.")
    return str(resolved)


def _get_pricing_fn(rate_library_path: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    global _PRICING_FN, _PRICING_FN_PATH
    if _PRICING_FN is None or _PRICING_FN_PATH != rate_library_path:
        _PRICING_FN = pricing_engine.price_estimate_for_runner(rate_library_path)
        _PRICING_FN_PATH = rate_library_path
    return _PRICING_FN


def _merge_pricing(snapshot: Dict[str, Any], pricing_result: Dict[str, Any]) -> Dict[str, Any]:
    items = snapshot.get("items", [])
    lines = pricing_result.get("lines", [])
    if not isinstance(items, list) or not isinstance(lines, list) or len(items) != len(lines):
        raise RuntimeError("Pricing failed: output invalid.")
    priced_items: List[Dict[str, Any]] = []
    for item, line_pricing in zip(items, lines):
        quantity = item.get("quantity")
        priced_items.append(
            {
                "item_id": item.get("item_id"),
                "display_name": item.get("display_name", ""),
                "source": item.get("source"),
                "quantity": float(quantity) if isinstance(quantity, (int, float)) else None,
                "pricing": line_pricing,
            }
        )
    return {"items": priced_items}


def _build_pricing_snapshot_from_resources(resources: Dict[str, Any]) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for bucket in ("labour", "plant", "materials"):
        entries = resources.get(bucket, [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            items.append(
                {
                    "item_id": None,
                    "source": "provisional",
                    "display_name": entry.get("description", ""),
                    "metadata": entry.get("traceability", {}),
                    "status": "confirmed",
                }
            )
    return {"items": items}


def estimator_runtime_price_snapshot(
    snapshot: Dict[str, Any],
    rate_library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Price a Merge Agent snapshot using the Pricing Engine, preserving MVP output shape.
    """
    pack_registry.require_registry()
    resolved_path = _resolve_rate_library_path(rate_library_path)
    pricing_fn = _get_pricing_fn(resolved_path)
    pricing_result = pricing_fn(snapshot)
    merged = _merge_pricing(snapshot, pricing_result)
    return _require_pricing_output(merged)


def estimator_runtime_step(validator_output: Dict[str, Any], user_reply: Optional[str] = None) -> Dict[str, Any]:
    """
    Processes a Validator-approved payload and produces the Estimator's next
    user-facing message and execution directive.

    Expected VALID validator_output:
        {
            "valid": True,
            "violation_code": None,
            "message": "OK",
            "payload": {
                "state_id": "...",
                "estimator_message": "...",
                "items_presented": [...],
                "required_estimator_action": "...",
                "compatibility_metadata": ...
            }
        }

    If valid == False (or payload missing/invalid), returns:
        {
            "estimator_message": "I cannot proceed with that item.",
            "next_action": "ERROR"
        }

    Special handling when user_reply is provided:
      - For AWAIT_CONFIRMATION  → {"user_decision": "CONFIRMED" | "REJECTED"}
      - For AWAIT_SELECTION     → {"user_decision": "SELECTED" | "INVALID_SELECTION", "item_id": ...?}
      - For AWAIT_CLARIFICATION → {"user_clarification": user_reply}
      - For AWAIT_REVISION      → {"user_revision": user_reply}
    """

    # -----------------------------------------------------------------------
    # Guard: invalid validator output → error
    # -----------------------------------------------------------------------
    if not validator_output.get("valid"):
        return {
            "estimator_message": "I cannot proceed with that item.",
            "next_action": "ERROR",
        }

    payload = validator_output.get("payload")
    if not isinstance(payload, dict):
        return {
            "estimator_message": "I cannot proceed with that item.",
            "next_action": "ERROR",
        }

    estimator_message: str = payload.get("estimator_message", "")
    items_presented: List[Dict[str, Any]] = payload.get("items_presented", []) or []
    required_action: str = payload.get("required_estimator_action", "")

    next_action = _map_required_action_to_next_action(required_action)
    if next_action is None:
        # Unknown or unsupported required_estimator_action
        return {
            "estimator_message": "I cannot proceed with that item.",
            "next_action": "ERROR",
        }

    # -----------------------------------------------------------------------
    # Phase 1: No user_reply → produce UI-facing instructions
    # -----------------------------------------------------------------------
    if user_reply is None:
        if next_action == "AWAIT_CONFIRMATION":
            return {
                "estimator_message": estimator_message,
                "items": items_presented,
                "next_action": "AWAIT_CONFIRMATION",
            }

        if next_action == "AWAIT_SELECTION":
            return {
                "estimator_message": estimator_message,
                "items": items_presented,
                "next_action": "AWAIT_SELECTION",
            }

        if next_action == "AWAIT_CLARIFICATION":
            return {
                "estimator_message": estimator_message,
                "items": [],
                "next_action": "AWAIT_CLARIFICATION",
            }

        if next_action == "AWAIT_REVISION":
            return {
                "estimator_message": estimator_message,
                "items": [],
                "next_action": "AWAIT_REVISION",
            }

        # Fallback (should not occur)
        return {
            "estimator_message": "I cannot proceed with that item.",
            "next_action": "ERROR",
        }

    # -----------------------------------------------------------------------
    # Phase 2: user_reply provided → interpret deterministically
    # -----------------------------------------------------------------------
    if next_action == "AWAIT_CONFIRMATION":
        return _handle_confirmation_reply(user_reply)

    if next_action == "AWAIT_SELECTION":
        return _handle_selection_reply(items_presented, user_reply)

    if next_action == "AWAIT_CLARIFICATION":
        return {"user_clarification": user_reply}

    if next_action == "AWAIT_REVISION":
        return {"user_revision": user_reply}

    # Fallback (defensive; should not be reachable)
    return {
        "estimator_message": "I cannot proceed with that item.",
        "next_action": "ERROR",
    }


def estimator_runtime_resource_step(eli_output: Any, ce_output: Optional[Any] = None) -> Dict[str, Any]:
    """
    Orchestrate provisional resources from ELI output via Resource Builder
    and invoke Pricing exactly once.
    """
    try:
        resources = resource_builder.build_resources(eli_output, ce_output=ce_output)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Estimator Runtime halted: invalid resource input.") from exc

    pack_registry.require_registry()
    pricing_snapshot = _build_pricing_snapshot_from_resources(resources)
    pricing_result = pricing_engine.price_estimate_snapshot(pricing_snapshot, rate_library={})
    pricing_output = _merge_pricing(pricing_snapshot, pricing_result)
    pricing_output = _require_pricing_output(pricing_output)

    if resources.get("all_provisional") is not True:
        resources = copy.deepcopy(resources)
        resources["all_provisional"] = True

    output = dict(resources)
    output["pricing"] = pricing_output
    return output


if __name__ == "__main__":
    # Minimal, deterministic smoke test
    sample_validator_output = {
        "valid": True,
        "violation_code": None,
        "message": "OK",
        "payload": {
            "state_id": "B",
            "estimator_message": "Multiple close matches identified. Selection required.",
            "items_presented": [
                {"id": "B001", "name": "Ambiguous Item 1"},
                {"id": "B002", "name": "Ambiguous Item 2"},
            ],
            "required_estimator_action": "CHOOSE_ITEM",
            "compatibility_metadata": None,
        },
    }

    # Phase 1: get instructions
    print(estimator_runtime_step(sample_validator_output))

    # Phase 2: simulate a user selection by index
    print(estimator_runtime_step(sample_validator_output, user_reply="2"))

    # Phase 2: simulate a user selection by ID
    print(estimator_runtime_step(sample_validator_output, user_reply="B001"))
