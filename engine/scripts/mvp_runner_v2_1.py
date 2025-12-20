# C:/Valesco_System/engine/scripts/mvp_runner_v2.1.py
# Valesco MVP Runner v2.1 — Full-System Integration REPL
#
# Thin orchestrator for:
#   User → CE Retrieval → Router → Architect → Validator
#   → Estimator Runtime → Merge Agent → Material Manager
#
# This script:
#   - loads all runtime modules,
#   - provides a minimal CLI / REPL,
#   - allows manual exercise of all MVP flows,
#   - introduces no new CE logic and does not modify metadata.

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Embeddable Python runs with an isolated sys.path; ensure repo root is importable.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.scripts.ready_gate_v3_5 import assert_ready_or_exit, evaluate_ready

_READY_OK: bool | None = None
_READY_REPORT: list[str] | None = None


def _assert_ready_v3_5_silent_on_success() -> None:
    """Fail closed without printing on success (keeps test output clean)."""
    global _READY_OK, _READY_REPORT
    if _READY_OK is None:
        ok, report_lines, _ = evaluate_ready(str(REPO_ROOT))
        _READY_OK = ok
        _READY_REPORT = report_lines

    if not _READY_OK:
        for line in (_READY_REPORT or []):
            print(line)
        raise SystemExit(1)


from engine.modules.ce_retrieval_layer_v2_1 import retrieve as retrieve_signals
from engine.modules.router_v2_1 import route
from engine.modules.architect_v2_1 import build_architect_payload
from engine.modules.validator_v2_1 import validate
from engine.modules.estimator_runtime_v2_1 import estimator_runtime_step
from engine.modules.merge_agent_v2_1 import (
    init_estimate,
    add_catalog_item,
    add_provisional_item,
    get_estimate_snapshot,
)
from engine.modules.material_manager_v2_1 import get_metadata


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _wrap_validator_output(core_result: Dict[str, Any], architect_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attach Architect payload to Validator result for Estimator Runtime,
    without changing the validation decision.
    """
    if core_result.get("valid"):
        wrapped = dict(core_result)
        wrapped["payload"] = architect_output
        return wrapped
    return core_result


def _print_current_estimate_snapshot() -> None:
    """
    Print a compact snapshot of the current estimate model.
    """
    snapshot = get_estimate_snapshot()
    items = snapshot.get("items", [])
    if not items:
        print("Current Estimate: [empty]")
        return

    print("Current Estimate:")
    for idx, line in enumerate(items, start=1):
        item_id = line.get("item_id")
        source = line.get("source")
        name = line.get("display_name", "")
        if source == "catalog" and item_id:
            print(f"{idx}. {item_id} — {name}")
        else:
            print(f'{idx}. PROVISIONAL — "{name}"')


def _run_single_item(description: str) -> None:
    """
    Run a single end-to-end item flow, including any required CE re-runs
    for clarification/revision, until it resolves as a catalog or provisional item.
    """
    current_description = description

    while True:
        # --------------------------------------------------------------
        # CE → Router → Architect → Validator
        # --------------------------------------------------------------
        ce_output = retrieve_signals(current_description)
        router_output = route(ce_output)
        architect_output = build_architect_payload(router_output)
        validator_core = validate(ce_output, router_output, architect_output)
        validator_output = _wrap_validator_output(validator_core, architect_output)

        # --------------------------------------------------------------
        # Invalid pipeline → error to Estimator and stop this item
        # --------------------------------------------------------------
        if not validator_core.get("valid"):
            runtime_error = estimator_runtime_step(validator_output)
            print(f"Estimator: {runtime_error.get('estimator_message', 'I cannot proceed with that item.')}")
            return

        # --------------------------------------------------------------
        # Estimator Runtime: UI-facing step
        # --------------------------------------------------------------
        runtime_ui = estimator_runtime_step(validator_output)
        estimator_message = runtime_ui.get("estimator_message", "")
        items = runtime_ui.get("items", [])
        next_action = runtime_ui.get("next_action")

        # Display estimator-facing message and options only
        print(f"Estimator: {estimator_message}")
        if items:
            print("Options:")
            for idx, item in enumerate(items, start=1):
                item_id = item.get("id", "")
                name = item.get("name", "")
                print(f"  {idx}. {item_id} — {name}")

        # If no action required or error, stop
        if next_action == "ERROR" or next_action is None:
            print("No further action can be taken for this item.")
            return

        # --------------------------------------------------------------
        # Interactive handling per next_action
        # --------------------------------------------------------------
        if next_action == "AWAIT_CONFIRMATION":
            # Single yes/no style confirmation
            user_reply = input("Confirm this item? (yes/no): ").strip()
            decision = estimator_runtime_step(validator_output, user_reply=user_reply)
            if decision.get("user_decision") == "CONFIRMED":
                if items:
                    add_catalog_item(items[0])
                    print("Item confirmed and added to estimate.")
                else:
                    print("No item available to confirm.")
                return
            else:
                # Treat rejection as provisional for MVP
                add_provisional_item(current_description)
                print("Match rejected. Provisional item added to estimate.")
                return

        elif next_action == "AWAIT_SELECTION":
            # Allow repeated attempts until a valid selection is made
            while True:
                user_reply = input("Select an option by index or ID: ").strip()
                decision = estimator_runtime_step(validator_output, user_reply=user_reply)
                if decision.get("user_decision") == "SELECTED":
                    item_id = decision.get("item_id")
                    selected_item: Optional[Dict[str, Any]] = None
                    for item in items:
                        if item.get("id") == item_id:
                            selected_item = item
                            break
                    if selected_item is not None:
                        add_catalog_item(selected_item)
                        print(f"Item {item_id} added to estimate.")
                    else:
                        print("Selected item not found; no item added.")
                    return
                else:
                    print("Invalid selection. Please try again.")

        elif next_action == "AWAIT_CLARIFICATION":
            user_reply = input("Provide clarification: ").strip()
            decision = estimator_runtime_step(validator_output, user_reply=user_reply)
            clarification = decision.get("user_clarification", "")
            # Append clarification to description and re-run pipeline
            current_description = f"{current_description} {clarification}".strip()
            continue  # loop back with updated description

        elif next_action == "AWAIT_REVISION":
            user_reply = input("Provide a revised description or type 'provisional': ").strip()
            decision = estimator_runtime_step(validator_output, user_reply=user_reply)
            revision = decision.get("user_revision", "").strip()
            lower_rev = revision.lower()

            if lower_rev in {"provisional", "non-standard", "nonstandard"}:
                add_provisional_item(current_description)
                print("Provisional item added to estimate.")
                return
            else:
                # Use revision as new description and re-run pipeline
                current_description = revision
                continue  # loop back with revised description

        else:
            # Unknown action; treat as terminal error for safety
            print("Unexpected estimator action. Cannot proceed with this item.")
            return


def run_mvp_case_programmatic(description: str, user_responses: List[str]) -> Dict[str, Any]:
    """
    Programmatic entry point for automated tests or scripts.

    This mirrors the interactive flow but consumes a fixed list of user_responses
    instead of reading from stdin, and returns the final estimate snapshot.
    """
    _assert_ready_v3_5_silent_on_success()

    init_estimate()
    current_description = description
    response_index = 0

    while True:
        ce_output = retrieve_signals(current_description)
        router_output = route(ce_output)
        architect_output = build_architect_payload(router_output)
        validator_core = validate(ce_output, router_output, architect_output)
        validator_output = _wrap_validator_output(validator_core, architect_output)

        if not validator_core.get("valid"):
            estimator_runtime_step(validator_output)
            break

        runtime_ui = estimator_runtime_step(validator_output)
        items = runtime_ui.get("items", [])
        next_action = runtime_ui.get("next_action")

        if next_action in {None, "ERROR"}:
            break

        # No more user responses available → stop
        if response_index >= len(user_responses):
            break

        user_reply = user_responses[response_index]
        response_index += 1
        decision = estimator_runtime_step(validator_output, user_reply=user_reply)

        if next_action == "AWAIT_CONFIRMATION":
            if decision.get("user_decision") == "CONFIRMED":
                if items:
                    add_catalog_item(items[0])
            else:
                add_provisional_item(current_description)
            break

        elif next_action == "AWAIT_SELECTION":
            if decision.get("user_decision") == "SELECTED":
                item_id = decision.get("item_id")
                selected_item: Optional[Dict[str, Any]] = None
                for item in items:
                    if item.get("id") == item_id:
                        selected_item = item
                        break
                if selected_item is not None:
                    add_catalog_item(selected_item)
            break

        elif next_action == "AWAIT_CLARIFICATION":
            clarification = decision.get("user_clarification", "")
            current_description = f"{current_description} {clarification}".strip()
            continue

        elif next_action == "AWAIT_REVISION":
            revision = decision.get("user_revision", "").strip()
            if revision.lower() in {"provisional", "non-standard", "nonstandard"}:
                add_provisional_item(current_description)
                break
            current_description = revision
            continue

        else:
            break

    return get_estimate_snapshot()


# ---------------------------------------------------------------------------
# CLI / REPL
# ---------------------------------------------------------------------------

def main() -> None:
    assert_ready_or_exit(str(REPO_ROOT))

    print("Welcome to Valesco MVP Runner v2.1")
    print("Type an item description to start CE handling.")
    print("Commands: 'show', 'meta <id>', 'reset', 'exit'.")

    # Initialize estimate on first run
    init_estimate()

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Valesco MVP Runner v2.1.")
            break

        if not line:
            continue

        if line.lower() == "exit":
            print("Exiting Valesco MVP Runner v2.1.")
            break

        if line.lower() == "show":
            _print_current_estimate_snapshot()
            continue

        if line.lower().startswith("meta "):
            _, _, item_id = line.partition(" ")
            item_id = item_id.strip()
            if not item_id:
                print("Usage: meta <id>")
                continue
            meta = get_metadata(item_id)
            if meta is None:
                print(f"No metadata found for item_id '{item_id}'.")
            else:
                print(f"Metadata for {item_id}:")
                print(meta)
            continue

        if line.lower() == "reset":
            init_estimate()
            print("Estimate reset.")
            continue

        # Treat any other input as an item description
        _run_single_item(line)
        _print_current_estimate_snapshot()


if __name__ == "__main__":
    main()
