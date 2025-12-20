# C:/Valesco_System/engine/tests/mvp_test_harness_v2.1.py
# MVP Test Harness v2.1
#
# Deterministic end-to-end harness:
# User → CE Retrieval → Router → Architect → Validator → Estimator Runtime
# → Merge Agent → Material Manager
#
# This harness is intended for console-based/manual inspection and MVP
# integration testing. It introduces no new CE logic and uses static,
# deterministic behaviour only.

from typing import Any, Dict, List

# NOTE: Import paths and function names are specified by the DIB.
# They are assumed to exist in the runtime environment.
from engine.modules.ce_retrieval_layer_v2_1 import retrieve as retrieve_signals
from engine.modules.router_v2_1 import route
from engine.modules.architect_v2_1 import build_architect_payload as build_architect_output
from engine.modules.validator_v2_1 import validate
from engine.modules.estimator_runtime_v2_1 import estimator_runtime_step
from engine.modules.merge_agent_v2_1 import (
    init_estimate,
    add_catalog_item,
    add_provisional_item,
    get_estimate_snapshot,
)
from engine.modules.material_manager_v2_1 import get_metadata


def _wrap_validator_output(core_result: Dict[str, Any], architect_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attach Architect payload to Validator result for Estimator Runtime,
    without modifying the original validation decision.
    """
    if core_result.get("valid"):
        wrapped = dict(core_result)
        wrapped["payload"] = architect_output
        return wrapped
    return core_result


def run_mvp_test_case(description: str, user_responses: List[str]) -> Dict[str, Any]:
    """
    Simulate the entire system on a single item description and a sequence
    of user replies. Returns the final merged estimate snapshot.

    Flow:
      description → CE → Router → Architect → Validator → Estimator Runtime
      → (optional CE re-run based on clarification/revision) → Merge Agent.
    """

    print("\n======================================================")
    print(f"Running MVP Test Case for description: {description!r}")
    print("======================================================")

    # Ensure a clean estimate for this test case
    init_estimate()

    current_description = description
    response_index = 0

    while True:
        # --------------------------------------------------------------
        # CE Retrieval
        # --------------------------------------------------------------
        signals = retrieve_signals(current_description)
        print("\n[CE RETRIEVAL]")
        print("Input description:", current_description)
        print("Signals:", signals)

        # --------------------------------------------------------------
        # Router
        # --------------------------------------------------------------
        router_out = route(signals)
        print("\n[ROUTER]")
        print("Router state_id:", router_out.get("state_id"))
        print("Router output:", router_out)

        # --------------------------------------------------------------
        # Architect
        # --------------------------------------------------------------
        arch_out = build_architect_output(router_out)
        print("\n[ARCHITECT]")
        print("Architect output:", arch_out)

        # --------------------------------------------------------------
        # Validator
        # --------------------------------------------------------------
        val_core = validate(signals, router_out, arch_out)
        print("\n[VALIDATOR]")
        print("Validator core result:", val_core)

        val_out = _wrap_validator_output(val_core, arch_out)

        # If invalid, stop here; Estimator will be in error mode.
        if not val_core.get("valid"):
            runtime_error = estimator_runtime_step(val_out)
            print("\n[ESTIMATOR RUNTIME] (Invalid pipeline)")
            print("Runtime output:", runtime_error)
            break

        # --------------------------------------------------------------
        # Estimator Runtime (UI-facing step)
        # --------------------------------------------------------------
        runtime_ui = estimator_runtime_step(val_out)
        print("\n[ESTIMATOR RUNTIME] (UI Instruction)")
        print("Runtime output:", runtime_ui)

        next_action = runtime_ui.get("next_action")

        if next_action == "ERROR":
            # Defensive; should not occur for valid==True.
            print("\n[ESTIMATOR RUNTIME] Error next_action; terminating.")
            break

        # If no more user responses are available, stop the scenario.
        if response_index >= len(user_responses):
            print("\n[HARNESS] No more user responses; stopping scenario.")
            break

        user_reply = user_responses[response_index]
        response_index += 1
        print("\n[USER] Reply:", user_reply)

        # --------------------------------------------------------------
        # Estimator Runtime (Decision from reply)
        # --------------------------------------------------------------
        decision = estimator_runtime_step(val_out, user_reply=user_reply)
        print("[ESTIMATOR RUNTIME] Decision:", decision)

        # --------------------------------------------------------------
        # Handle decisions deterministically based on next_action
        # --------------------------------------------------------------
        if next_action == "AWAIT_CONFIRMATION":
            # State A path (or rejection → provisional)
            if decision.get("user_decision") == "CONFIRMED":
                items = runtime_ui.get("items", [])
                if items:
                    add_catalog_item(items[0])
                    print("\n[MERGE AGENT] Catalog item confirmed and merged:", items[0])
                else:
                    print("\n[MERGE AGENT] No items to merge despite confirmation.")
                break
            else:
                # Rejection: treat as provisional for MVP harness.
                add_provisional_item(current_description)
                print("\n[MERGE AGENT] Match rejected; provisional item added.")
                break

        elif next_action == "AWAIT_SELECTION":
            # States B/E path
            user_decision = decision.get("user_decision")
            if user_decision == "SELECTED":
                item_id = decision.get("item_id")
                selected_item = None
                for item in runtime_ui.get("items", []):
                    if item.get("id") == item_id:
                        selected_item = item
                        break
                if selected_item is not None:
                    add_catalog_item(selected_item)
                    print("\n[MERGE AGENT] Selected catalog item merged:", selected_item)
                else:
                    print("\n[MERGE AGENT] Selected item_id not found in items; no merge.")
                break
            else:
                print("\n[MERGE AGENT] Invalid selection; no merge performed.")
                break

        elif next_action == "AWAIT_CLARIFICATION":
            # State C path: clarification → re-run CE with augmented description
            clarification = decision.get("user_clarification", "")
            current_description = f"{current_description} {clarification}".strip()
            print("\n[HARNESS] Clarification captured; re-running pipeline with updated description.")
            # Loop continues with updated description

        elif next_action == "AWAIT_REVISION":
            # State D path: revision → either new description or provisional
            revision = decision.get("user_revision", "")
            lower_rev = revision.strip().lower()
            if lower_rev in {"provisional", "non-standard", "nonstandard"}:
                # User elects non-standard → provisional line
                add_provisional_item(current_description)
                print("\n[MERGE AGENT] Provisional item added (user elected non-standard).")
                break
            else:
                current_description = revision
                print("\n[HARNESS] Revision supplied; re-running pipeline with revised description.")
                # Loop continues with revised description
        else:
            # Defensive fallback
            print("\n[HARNESS] Unknown next_action; terminating.")
            break

    # --------------------------------------------------------------
    # Final snapshot and optional metadata dump
    # --------------------------------------------------------------
    snapshot = get_estimate_snapshot()
    print("\n[FINAL ESTIMATE SNAPSHOT]")
    print(snapshot)

    print("\n[FINAL METADATA VIA MATERIAL MANAGER]")
    for idx, line in enumerate(snapshot.get("items", [])):
        src = line.get("source")
        item_id = line.get("item_id")
        print(f"Line {idx}: source={src}, item_id={item_id}, display_name={line.get('display_name')!r}")
        if src == "catalog" and item_id:
            meta = get_metadata(item_id)
            print("  Raw catalog metadata:", meta)

    print("======================================================\n")
    return snapshot


# ---------------------------------------------------------------------------
# Scenario Definitions
# ---------------------------------------------------------------------------

def _scenario_a_clean_match():
    """
    Scenario A — Clean Match (A → Confirm → Merge)
    Description triggers a clean match. User says "yes".
    """
    description = "clean item description"
    user_responses = ["yes"]
    return run_mvp_test_case(description, user_responses)


def _scenario_b_ambiguous():
    """
    Scenario B — Ambiguous (B → Select → Merge)
    Description triggers top-3 items. User selects item 2.
    """
    description = "ambiguous item requiring choice"
    user_responses = ["2"]
    return run_mvp_test_case(description, user_responses)


def _scenario_c_insufficient_then_resolve():
    """
    Scenario C — Insufficient (C → Clarify → A/B/E → Confirm/Select)
    Start with insufficient detail; user clarifies; system re-runs and resolves
    to a final state (here designed to become a clean match).
    """
    description = "insufficient description"
    # First: clarification to push towards "clean" behaviour, then confirm "yes"
    user_responses = ["clean details added", "yes"]
    return run_mvp_test_case(description, user_responses)


def _scenario_d_no_match_provisional():
    """
    Scenario D — No Match → Provisional
    User elects not to refine; provisional line is added.
    """
    description = "no match none"
    # User answers "provisional" to mark as non-standard
    user_responses = ["provisional"]
    return run_mvp_test_case(description, user_responses)


def _scenario_e_compatible_alternatives():
    """
    Scenario E — Compatible Alternatives
    State E triggered. User selects one alternative.
    """
    description = "compatible alternative option"
    # User selects the second compatible item
    user_responses = ["2"]
    return run_mvp_test_case(description, user_responses)


# ---------------------------------------------------------------------------
# Main Harness Execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== MVP Test Harness v2.1 ===")

    scenario_results = {
        "Scenario A — Clean Match": _scenario_a_clean_match(),
        "Scenario B — Ambiguous": _scenario_b_ambiguous(),
        "Scenario C — Insufficient → Resolved": _scenario_c_insufficient_then_resolve(),
        "Scenario D — No Match → Provisional": _scenario_d_no_match_provisional(),
        "Scenario E — Compatible Alternatives": _scenario_e_compatible_alternatives(),
    }

    print("\n=== Summary of Final Estimate Snapshots ===")
    for name, snapshot in scenario_results.items():
        print(f"\n{name}:")
        print(snapshot)
