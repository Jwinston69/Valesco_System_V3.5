# C:/Valesco_System/engine/modules/validator_v2.1.py
# Validator v2.1 — Pure, Blocking-Only Validation for CE Missing-Item Flows
#
# This module validates consistency between:
#   - CE Retrieval signals (ce_output)
#   - Router output (router_output)
#   - Architect payload (architect_output)
#
# The Validator:
#   - Only passes or blocks (never mutates inputs, never auto-corrects)
#   - Returns deterministic violation codes
#   - Performs no CE reasoning beyond pattern validation

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Static Thresholds (must match Router logic for consistency)
# ---------------------------------------------------------------------------

CLEAN_MATCH_SCORE_MIN: float = 0.90
CLEAN_MATCH_GAP_MIN: float = 0.10
LOW_CONFIDENCE_SCORE_MAX: float = 0.85

# Allowed CE keys (signals + retrieved_items)
ALLOWED_CE_KEYS = {
    "hit_count",
    "top_score",
    "score_gap_to_next",
    "coverage_flags",
    "retrieved_items",
}

# Allowed Architect output keys
ALLOWED_ARCH_KEYS = {
    "state_id",
    "estimator_message",
    "items_presented",
    "required_estimator_action",
    "compatibility_metadata",
}


# ---------------------------------------------------------------------------
# Helper Predicates (mirror Router logic)
# ---------------------------------------------------------------------------

def _has_strong_coverage(flags: Dict[str, Any]) -> bool:
    return bool(flags.get("strong"))


def _has_weak_or_conflicting_coverage(flags: Dict[str, Any]) -> bool:
    return bool(flags.get("weak") or flags.get("conflicting"))


def _has_compatibility(flags: Dict[str, Any]) -> bool:
    return bool(flags.get("compatible"))


def _signals_inconsistent(
    hit_count: int,
    top_score: Optional[float],
    score_gap_to_next: Optional[float],
    coverage_flags: Dict[str, Any],
) -> bool:
    # Negative hit_count is structurally invalid.
    if hit_count < 0:
        return True

    # hit_count == 0 → scores and gaps must not be present/used.
    if hit_count == 0:
        if top_score is not None or score_gap_to_next is not None:
            return True

    # hit_count > 0 → top_score must be present.
    if hit_count > 0 and top_score is None:
        return True

    # hit_count > 1 → score_gap_to_next must be present.
    if hit_count > 1 and score_gap_to_next is None:
        return True

    # Strong and weak/conflicting coverage at the same time is inconsistent.
    if coverage_flags.get("strong") and (
        coverage_flags.get("weak") or coverage_flags.get("conflicting")
    ):
        return True

    return False


def _is_clean_match(
    hit_count: int,
    top_score: Optional[float],
    score_gap_to_next: Optional[float],
    coverage_flags: Dict[str, Any],
) -> bool:
    if hit_count < 1:
        return False
    if not _has_strong_coverage(coverage_flags):
        return False
    if top_score is None or top_score < CLEAN_MATCH_SCORE_MIN:
        return False
    if score_gap_to_next is None:
        # No second item → acceptable clean match if other predicates hold.
        return True
    return score_gap_to_next >= CLEAN_MATCH_GAP_MIN


def _item_confidence_low(top_score: Optional[float]) -> bool:
    if top_score is None:
        return True
    return top_score < CLEAN_MATCH_SCORE_MIN and top_score <= LOW_CONFIDENCE_SCORE_MAX


def _is_compatible_alternatives(
    hit_count: int,
    top_score: Optional[float],
    coverage_flags: Dict[str, Any],
) -> bool:
    if hit_count < 1:
        return False
    # Strong or category-compatible coverage required.
    if not (_has_strong_coverage(coverage_flags) or _has_compatibility(coverage_flags)):
        return False
    # Simulate availability of compatibility rules via flag.
    if not _has_compatibility(coverage_flags):
        return False
    # Require low item-level confidence.
    if not _item_confidence_low(top_score):
        return False
    return True


def _expected_state_from_signals(
    hit_count: int,
    top_score: Optional[float],
    score_gap_to_next: Optional[float],
    coverage_flags: Dict[str, Any],
) -> str:
    """
    Compute expected state based on CE signals, mirroring Router's ordered logic:
    D → C → A → E → B
    """
    if hit_count == 0:
        return "D"

    if _has_weak_or_conflicting_coverage(coverage_flags) or _signals_inconsistent(
        hit_count, top_score, score_gap_to_next, coverage_flags
    ):
        return "C"

    if _is_clean_match(hit_count, top_score, score_gap_to_next, coverage_flags):
        return "A"

    if _is_compatible_alternatives(hit_count, top_score, coverage_flags):
        return "E"

    return "B"


# ---------------------------------------------------------------------------
# Core Validation Checks
# ---------------------------------------------------------------------------

def _validate_signals(ce_output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """A. Signal Legality and Structural Consistency."""
    # Only allowed CE keys present.
    for key in ce_output.keys():
        if key not in ALLOWED_CE_KEYS:
            return {
                "valid": False,
                "violation_code": "ILLEGAL_SIGNAL",
                "message": "Invalid Router/Architect output",
            }

    hit_count: int = int(ce_output.get("hit_count", 0))
    top_score: Optional[float] = ce_output.get("top_score")
    score_gap_to_next: Optional[float] = ce_output.get("score_gap_to_next")
    coverage_flags: Dict[str, Any] = ce_output.get("coverage_flags", {}) or {}

    # hit_count < 0
    if hit_count < 0:
        return {
            "valid": False,
            "violation_code": "SIGNAL_STRUCTURE_ERROR",
            "message": "Invalid Router/Architect output",
        }

    if _signals_inconsistent(hit_count, top_score, score_gap_to_next, coverage_flags):
        return {
            "valid": False,
            "violation_code": "SIGNAL_STRUCTURE_ERROR",
            "message": "Invalid Router/Architect output",
        }

    return None  # OK


def _validate_router_state(
    ce_output: Dict[str, Any],
    router_output: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """B. Router-State Validation against CE signals."""
    hit_count: int = int(ce_output.get("hit_count", 0))
    top_score: Optional[float] = ce_output.get("top_score")
    score_gap_to_next: Optional[float] = ce_output.get("score_gap_to_next")
    coverage_flags: Dict[str, Any] = ce_output.get("coverage_flags", {}) or {}

    router_state: str = router_output.get("state_id", "")

    expected_state = _expected_state_from_signals(
        hit_count, top_score, score_gap_to_next, coverage_flags
    )

    if router_state not in {"A", "B", "C", "D", "E"}:
        return {
            "valid": False,
            "violation_code": "UNKNOWN_STATE_ID",
            "message": "Invalid Router/Architect output",
        }

    if router_state != expected_state:
        return {
            "valid": False,
            "violation_code": f"STATE_MISMATCH_{router_state}",
            "message": "Invalid Router/Architect output",
        }

    return None  # OK


def _validate_architect_structure(
    ce_output: Dict[str, Any],
    router_output: Dict[str, Any],
    architect_output: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """C. Architect Structural Validation per state."""
    state_id: str = router_output.get("state_id", "")
    arch_state: str = architect_output.get("state_id", "")

    # Architect must not override Router state.
    if arch_state != state_id:
        return {
            "valid": False,
            "violation_code": "ARCHITECT_STATE_OVERRIDE",
            "message": "Invalid Router/Architect output",
        }

    # Architect must not add extra top-level fields.
    for key in architect_output.keys():
        if key not in ALLOWED_ARCH_KEYS:
            return {
                "valid": False,
                "violation_code": "ARCHITECT_EXTRA_FIELDS",
                "message": "Invalid Router/Architect output",
            }

    items_presented: List[Dict[str, Any]] = architect_output.get("items_presented", []) or []
    required_action: str = architect_output.get("required_estimator_action", "")
    compatibility_metadata = architect_output.get("compatibility_metadata")

    ce_items: List[Dict[str, Any]] = ce_output.get("retrieved_items", []) or []

    # Ensure Architect items are not invented/modified: each presented item must
    # exist within CE retrieved_items as an identical dict.
    for item in items_presented:
        if item not in ce_items:
            return {
                "valid": False,
                "violation_code": "METADATA_SAFETY_ERROR",
                "message": "Invalid Router/Architect output",
            }

    # State-specific structural rules.
    if state_id == "A":
        if len(items_presented) != 1:
            return {
                "valid": False,
                "violation_code": "ARCH_ITEMS_STATE_A",
                "message": "Invalid Router/Architect output",
            }
        if required_action != "CONFIRM_MATCH":
            return {
                "valid": False,
                "violation_code": "ARCH_ACTION_STATE_A",
                "message": "Invalid Router/Architect output",
            }
        if compatibility_metadata is not None:
            return {
                "valid": False,
                "violation_code": "COMPAT_METADATA_NOT_ALLOWED_A",
                "message": "Invalid Router/Architect output",
            }

    elif state_id == "B":
        if not (1 <= len(items_presented) <= 3):
            return {
                "valid": False,
                "violation_code": "ARCH_ITEMS_STATE_B",
                "message": "Invalid Router/Architect output",
            }
        if required_action != "CHOOSE_ITEM":
            return {
                "valid": False,
                "violation_code": "ARCH_ACTION_STATE_B",
                "message": "Invalid Router/Architect output",
            }
        if compatibility_metadata is not None:
            return {
                "valid": False,
                "violation_code": "COMPAT_METADATA_NOT_ALLOWED_B",
                "message": "Invalid Router/Architect output",
            }

    elif state_id == "C":
        if len(items_presented) != 0:
            return {
                "valid": False,
                "violation_code": "ARCH_ITEMS_STATE_C",
                "message": "Invalid Router/Architect output",
            }
        if required_action != "PROVIDE_CLARIFICATION":
            return {
                "valid": False,
                "violation_code": "ARCH_ACTION_STATE_C",
                "message": "Invalid Router/Architect output",
            }
        if compatibility_metadata is not None:
            return {
                "valid": False,
                "violation_code": "COMPAT_METADATA_NOT_ALLOWED_C",
                "message": "Invalid Router/Architect output",
            }

    elif state_id == "D":
        if len(items_presented) != 0:
            return {
                "valid": False,
                "violation_code": "ARCH_ITEMS_STATE_D",
                "message": "Invalid Router/Architect output",
            }
        if required_action != "REVISE_DESCRIPTION":
            return {
                "valid": False,
                "violation_code": "ARCH_ACTION_STATE_D",
                "message": "Invalid Router/Architect output",
            }
        if compatibility_metadata is not None:
            return {
                "valid": False,
                "violation_code": "COMPAT_METADATA_NOT_ALLOWED_D",
                "message": "Invalid Router/Architect output",
            }

    elif state_id == "E":
        # All compatible items must be presented (i.e., equal to CE items list).
        if len(items_presented) != len(ce_items):
            return {
                "valid": False,
                "violation_code": "ARCH_ITEMS_STATE_E",
                "message": "Invalid Router/Architect output",
            }
        for item in ce_items:
            if item not in items_presented:
                return {
                    "valid": False,
                    "violation_code": "ARCH_ITEMS_STATE_E",
                    "message": "Invalid Router/Architect output",
                }
        if required_action != "CHOOSE_ITEM":
            return {
                "valid": False,
                "violation_code": "ARCH_ACTION_STATE_E",
                "message": "Invalid Router/Architect output",
            }
        # compatibility_metadata only allowed in State E; must be present or None?
        # Here we only ensure it's not forbidden; presence is allowed.
    else:
        # Unknown state should have been caught earlier.
        return {
            "valid": False,
            "violation_code": "UNKNOWN_STATE_ID",
            "message": "Invalid Router/Architect output",
        }

    # For states other than E, compatibility_metadata must be None (enforced above).
    return None  # OK


def _validate_metadata_safety(
    state_id: str,
    architect_output: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """D. Metadata & Safety Validation (no inferred attributes, etc.)."""
    compatibility_metadata = architect_output.get("compatibility_metadata")
    # compatibility_metadata only allowed in State E.
    if state_id != "E" and compatibility_metadata is not None:
        return {
            "valid": False,
            "violation_code": "COMPAT_METADATA_NOT_ALLOWED",
            "message": "Invalid Router/Architect output",
        }

    # At this layer, we assume item dicts are raw library objects. We have already
    # enforced that items_presented ⊆ ce_output.retrieved_items, which prevents
    # invention of new items or attributes relative to CE.
    return None  # OK


# ---------------------------------------------------------------------------
# Public Validator API
# ---------------------------------------------------------------------------

def validate(
    ce_output: Dict[str, Any],
    router_output: Dict[str, Any],
    architect_output: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate consistency between CE signals, Router output, and Architect payload.

    Inputs:
        ce_output: dict — CE Retrieval output
        router_output: dict — Router state selection output
        architect_output: dict — Architect structured payload

    Output:
        {
            "valid": True | False,
            "violation_code": None | str,
            "message": str
        }
    """

    # A. Signal Legality
    result = _validate_signals(ce_output)
    if result is not None:
        return result

    # B. Router-State Validation
    result = _validate_router_state(ce_output, router_output)
    if result is not None:
        return result

    # C. Architect Structural Validation
    result = _validate_architect_structure(ce_output, router_output, architect_output)
    if result is not None:
        return result

    # D. Metadata & Safety Validation
    state_id = router_output.get("state_id", "")
    result = _validate_metadata_safety(state_id, architect_output)
    if result is not None:
        return result

    # If all checks pass:
    return {
        "valid": True,
        "violation_code": None,
        "message": "OK",
    }


if __name__ == "__main__":
    # Minimal sanity smoke-test stub for manual/local runs only.
    # This is deterministic and has no side effects beyond printing.
    sample_ce = {
        "hit_count": 0,
        "top_score": None,
        "score_gap_to_next": None,
        "coverage_flags": {"none": True},
        "retrieved_items": [],
    }
    sample_router = {
        "state_id": "D",
        "rationale_token": "HIT0",
        "retrieved_items": [],
        "compatibility_metadata": None,
    }
    sample_arch = {
        "state_id": "D",
        "estimator_message": "No matching catalog item found. Description revision required.",
        "items_presented": [],
        "required_estimator_action": "REVISE_DESCRIPTION",
        "compatibility_metadata": None,
    }
    print(validate(sample_ce, sample_router, sample_arch))
