# C:/Valesco_System/engine/modules/router_v2.1.py
# Router v2.1 — Deterministic A–E State Selection
#
# This module implements a pure, deterministic Router that consumes CE Retrieval
# Layer output and produces a single behaviour state (A–E) plus metadata for
# downstream Architect consumption. It follows the strict ordered transition
# logic specified for missing-item behaviour.

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Configurable Thresholds (Static for MVP)
# ---------------------------------------------------------------------------

# Minimum score required to qualify as a clean match.
CLEAN_MATCH_SCORE_MIN: float = 0.90

# Minimum score gap between top and second item to treat the top item as clearly dominant.
CLEAN_MATCH_GAP_MIN: float = 0.10

# Maximum score to still be considered "low confidence" for item-level certainty.
LOW_CONFIDENCE_SCORE_MAX: float = 0.85


# ---------------------------------------------------------------------------
# Helper Predicates
# ---------------------------------------------------------------------------

def _has_strong_coverage(flags: Dict[str, Any]) -> bool:
    return bool(flags.get("strong"))


def _has_weak_or_conflicting_coverage(flags: Dict[str, Any]) -> bool:
    return bool(flags.get("weak") or flags.get("conflicting"))


def _has_compatibility(flags: Dict[str, Any]) -> bool:
    # Used to simulate category-compatibility and availability of compatibility rules.
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

    # When hit_count is zero, scores and gaps must not be used.
    if hit_count == 0:
        if top_score is not None or score_gap_to_next is not None:
            return True

    # When there are hits, top_score must be present.
    if hit_count > 0 and top_score is None:
        return True

    # When hit_count > 1, score_gap_to_next must be defined.
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
        # No second item → acceptable as clean match if other predicates hold.
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


# ---------------------------------------------------------------------------
# Public Router API
# ---------------------------------------------------------------------------

def route(ce_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic Router entry point.

    Input (from CE Retrieval Layer):
        {
            "hit_count": int,
            "top_score": float | None,
            "score_gap_to_next": float | None,
            "coverage_flags": dict,
            "retrieved_items": list[dict]
        }

    Output:
        {
            "state_id": "A" | "B" | "C" | "D" | "E",
            "rationale_token": str,
            "retrieved_items": list[dict],
            "compatibility_metadata": dict | None
        }
    """

    hit_count: int = int(ce_output.get("hit_count", 0))
    top_score: Optional[float] = ce_output.get("top_score")
    score_gap_to_next: Optional[float] = ce_output.get("score_gap_to_next")
    coverage_flags: Dict[str, Any] = ce_output.get("coverage_flags", {}) or {}
    retrieved_items: List[Dict[str, Any]] = ce_output.get("retrieved_items", []) or []

    # -----------------------------------------------------------------------
    # Ordered Transition Logic (D → C → A → E → B)
    # -----------------------------------------------------------------------

    # State D — No Internal Match
    if hit_count == 0:
        state_id = "D"
        rationale_token = "HIT0"
        compatibility_metadata: Optional[Dict[str, Any]] = None

    # State C — Insufficient Retrieval Context
    elif _has_weak_or_conflicting_coverage(coverage_flags) or _signals_inconsistent(
        hit_count, top_score, score_gap_to_next, coverage_flags
    ):
        state_id = "C"
        rationale_token = "INSUFFICIENT_CONTEXT"
        compatibility_metadata = None

    # State A — Clean Match
    elif _is_clean_match(hit_count, top_score, score_gap_to_next, coverage_flags):
        state_id = "A"
        rationale_token = "CLEAN_MATCH"
        compatibility_metadata = None

    # State E — Compatible Alternatives
    elif _is_compatible_alternatives(hit_count, top_score, coverage_flags):
        state_id = "E"
        rationale_token = "COMPATIBLE_ALTERNATIVES"
        compatibility_metadata = {"compatibility_rules_available": True}

    # State B — Closest Internal Matches (Top 3)
    else:
        state_id = "B"
        rationale_token = "TOP3_AMBIGUOUS"
        compatibility_metadata = None

    # Router must not modify retrieved_items; it is passed through as-is.
    return {
        "state_id": state_id,
        "rationale_token": rationale_token,
        "retrieved_items": retrieved_items,
        "compatibility_metadata": compatibility_metadata,
    }
