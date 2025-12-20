# C:/Valesco_System/engine/modules/architect_v2.1.py
# Architect v2.1 — Deterministic State-Conformant Payload Construction
#
# Pure, deterministic Architect implementation for CE missing-item flows.
# Consumes Router output and produces a flat, JSON-like structure for Validator.

from typing import Any, Dict, List, Optional


def build_architect_payload(router_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct a structured, state-conformant payload for the Validator.

    Input (Router output):
        {
            "state_id": "A" | "B" | "C" | "D" | "E",
            "rationale_token": str,
            "retrieved_items": list[dict],
            "compatibility_metadata": dict | None
        }

    Output (Architect payload):
        {
            "state_id": "A" | "B" | "C" | "D" | "E",
            "estimator_message": str,
            "items_presented": list[dict],
            "required_estimator_action": str,
            "compatibility_metadata": dict | None
        }

    Behaviour is strictly deterministic and state-driven. No inference or enrichment
    of items is performed.
    """

    state_id: str = router_output.get("state_id", "")
    retrieved_items: List[Dict[str, Any]] = router_output.get("retrieved_items", []) or []
    compatibility_metadata: Optional[Dict[str, Any]] = router_output.get("compatibility_metadata")

    # Default outputs (will be overwritten per state).
    estimator_message: str
    items_presented: List[Dict[str, Any]]
    required_estimator_action: str

    # -----------------------------------------------------------------------
    # State A — Clean Match
    # -----------------------------------------------------------------------
    if state_id == "A":
        estimator_message = "Single high-confidence match identified."
        # Present exactly the first item if available; no modification or enrichment.
        items_presented = retrieved_items[:1]
        required_estimator_action = "CONFIRM_MATCH"

    # -----------------------------------------------------------------------
    # State B — Top-3 Ambiguous
    # -----------------------------------------------------------------------
    elif state_id == "B":
        estimator_message = "Multiple close matches identified. Selection required."
        # Present up to three items, preserving Router order.
        items_presented = retrieved_items[:3]
        required_estimator_action = "CHOOSE_ITEM"

    # -----------------------------------------------------------------------
    # State C — Insufficient Context
    # -----------------------------------------------------------------------
    elif state_id == "C":
        estimator_message = "Additional detail required to classify this item safely."
        # No items presented.
        items_presented = []
        required_estimator_action = "PROVIDE_CLARIFICATION"

    # -----------------------------------------------------------------------
    # State D — No Internal Match
    # -----------------------------------------------------------------------
    elif state_id == "D":
        estimator_message = "No matching catalog item found. Description revision required."
        # No items presented.
        items_presented = []
        required_estimator_action = "REVISE_DESCRIPTION"

    # -----------------------------------------------------------------------
    # State E — Compatible Alternatives
    # -----------------------------------------------------------------------
    elif state_id == "E":
        estimator_message = "Compatible alternatives available. Selection required."
        # Present only Router-provided compatible items; Architect does not filter or enrich.
        items_presented = retrieved_items
        required_estimator_action = "CHOOSE_ITEM"

    # -----------------------------------------------------------------------
    # Fallback (should not occur if Router is correct, but kept deterministic)
    # Treat unknown state as no-op with empty items; this is expected to be
    # caught by Validator as invalid.
    # -----------------------------------------------------------------------
    else:
        estimator_message = "Unsupported state. No items can be presented."
        items_presented = []
        required_estimator_action = "REVISE_DESCRIPTION"

    return {
        "state_id": state_id,
        "estimator_message": estimator_message,
        "items_presented": items_presented,
        "required_estimator_action": required_estimator_action,
        "compatibility_metadata": compatibility_metadata,
    }
