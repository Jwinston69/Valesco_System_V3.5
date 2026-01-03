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

from typing import Any, Dict, List, Optional
import copy

import engine.modules.resource_builder as resource_builder
import engine.modules.pricing_logic_v2_1 as pricing_logic


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

    pricing_output = pricing_logic.price_estimate(resources)
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
