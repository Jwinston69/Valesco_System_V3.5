# C:/Valesco_System/engine/scripts/mvp_runner_v2.2.py
# Valesco MVP Runner v2.2 — Quantity + Pricing Integration
#
# Thin orchestrator for:
#   User → CE Retrieval → Router → Architect → Validator
#   → Estimator Runtime → Merge Agent → Material Manager → Pricing
#
# Enhancements over v2.1:
#   - Quantity assignment via REPL commands
#   - Pricing display for the current estimate
#   - Estimate-level cost summary
#
# No CE logic changes. No estimator behaviour changes. No quantity inference.

import sys
import json
import os
import shlex
import subprocess
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

# Embeddable Python runs with an isolated sys.path; ensure repo root is importable.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.scripts.ready_gate_v3_5 import assert_ready_or_exit, evaluate_ready

_READY_OK: bool | None = None
_READY_REPORT: list[str] | None = None


def _force_utf8_stdio() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass


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


from engine.modules.router_v2_1 import route
from engine.modules.architect_v2_1 import build_architect_payload
from engine.modules.validator_v2_1 import validate
from engine.modules.estimator_runtime_v2_1 import estimator_runtime_step
from engine.modules.merge_agent_v2_1 import (
    init_estimate,
    add_catalog_item,
    add_provisional_item,
    get_estimate_snapshot,
    ESTIMATE_MODEL,
)
from engine.modules.material_manager_v2_1 import get_metadata
from engine.modules.pricing_logic_v2_1 import price_estimate
from engine.modules.quantity_logic_v2_1 import set_quantity, clear_quantity, apply_quantities
from engine.modules import pack_registry_v3_5 as pack_registry


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_CE_BACKEND_CMD_ENV = "VALESCO_CE_BACKEND_CMD"
_CE_BACKEND_SCRIPT_ENV = "VALESCO_CE_BACKEND_SCRIPT"


def _ce_backend_command() -> List[str]:
    cmd = os.environ.get(_CE_BACKEND_CMD_ENV, "").strip()
    if cmd:
        return shlex.split(cmd)
    script = os.environ.get(_CE_BACKEND_SCRIPT_ENV, "").strip()
    if script:
        return [sys.executable, script]
    raise RuntimeError(
        "CE backend command not configured. Set VALESCO_CE_BACKEND_CMD or VALESCO_CE_BACKEND_SCRIPT."
    )


def _normalize_ce_output(ce_output: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(ce_output, dict):
        raise RuntimeError("CE backend output must be a dict.")

    required_keys = {
        "hit_count",
        "top_score",
        "score_gap_to_next",
        "coverage_flags",
        "retrieved_items",
    }
    extra_keys = set(ce_output.keys()) - required_keys
    missing_keys = required_keys - set(ce_output.keys())
    if missing_keys or extra_keys:
        raise RuntimeError(
            f"CE backend output keys invalid. Missing: {sorted(missing_keys)} Extra: {sorted(extra_keys)}"
        )

    hit_count = ce_output["hit_count"]
    if not isinstance(hit_count, int):
        raise RuntimeError("CE backend hit_count must be an int.")

    top_score = ce_output["top_score"]
    if top_score is not None and not isinstance(top_score, (int, float)):
        raise RuntimeError("CE backend top_score must be numeric or None.")

    score_gap = ce_output["score_gap_to_next"]
    if score_gap is not None and not isinstance(score_gap, (int, float)):
        raise RuntimeError("CE backend score_gap_to_next must be numeric or None.")

    coverage_flags = ce_output["coverage_flags"]
    if not isinstance(coverage_flags, dict):
        raise RuntimeError("CE backend coverage_flags must be a dict.")

    retrieved_items = ce_output["retrieved_items"]
    if not isinstance(retrieved_items, list):
        raise RuntimeError("CE backend retrieved_items must be a list.")

    if hit_count != len(retrieved_items):
        raise RuntimeError("CE backend hit_count must match retrieved_items length.")

    normalized_items: List[Dict[str, Any]] = []
    for item in retrieved_items:
        if not isinstance(item, dict):
            raise RuntimeError("CE backend retrieved_items entries must be dicts.")
        if not all(key in item for key in ("id", "name", "category")):
            raise RuntimeError("CE backend retrieved_items must include id, name, category.")
        normalized_items.append(item)

    def _sort_key(item: Dict[str, Any]) -> tuple:
        score = item.get("score")
        if not isinstance(score, (int, float)):
            score = 0.0
        return (-float(score), str(item.get("id", "")), str(item.get("name", "")))

    normalized_items = sorted(normalized_items, key=_sort_key)

    return {
        "hit_count": hit_count,
        "top_score": float(top_score) if isinstance(top_score, (int, float)) else None,
        "score_gap_to_next": float(score_gap) if isinstance(score_gap, (int, float)) else None,
        "coverage_flags": coverage_flags,
        "retrieved_items": normalized_items,
    }


def _retrieve_signals(description: str) -> Dict[str, Any]:
    command = _ce_backend_command()
    payload = {"description": description}
    result = subprocess.run(
        command,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "CE backend invocation failed with exit code "
            f"{result.returncode}: {result.stderr.strip()}"
        )
    try:
        ce_output = json.loads(result.stdout)
    except ValueError as exc:
        raise RuntimeError("CE backend output was not valid JSON.") from exc
    return _normalize_ce_output(ce_output)


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
        qty = line.get("quantity")
        qty_str = f" (qty={qty})" if isinstance(qty, (int, float)) else " (quantity not set)"
        if source == "catalog" and item_id:
            print(f"{idx}. {item_id} — {name}{qty_str}")
        else:
            print(f'{idx}. PROVISIONAL — "{name}"{qty_str}')


def _print_item_resolution_snapshot(line: Dict[str, Any]) -> None:
    """
    After an item is resolved and merged, show details and note that quantity is not set yet.
    """
    item_id = line.get("item_id")
    source = line.get("source")
    display_name = line.get("display_name")
    print("\n[ITEM RESOLVED]")
    print(f"  item_id: {item_id}")
    print(f"  source: {source}")
    print(f"  display_name: {display_name!r}")
    if source == "catalog" and item_id:
        meta = get_metadata(item_id)
        print("  raw_metadata:", meta)
    qty = line.get("quantity")
    if isinstance(qty, (int, float)):
        print(f"  quantity: {float(qty)}")
    else:
        print("  note: Quantity not set")


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
        ce_output = _retrieve_signals(current_description)
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
            user_reply = input("Confirm this item? (yes/no): ").strip()
            decision = estimator_runtime_step(validator_output, user_reply=user_reply)
            if decision.get("user_decision") == "CONFIRMED":
                if items:
                    add_catalog_item(items[0])
                    print("Item confirmed and added to estimate.")
                    snapshot = get_estimate_snapshot()
                    _print_item_resolution_snapshot(snapshot["items"][-1])
                else:
                    print("No item available to confirm.")
                return
            else:
                add_provisional_item(current_description)
                print("Match rejected. Provisional item added to estimate.")
                snapshot = get_estimate_snapshot()
                _print_item_resolution_snapshot(snapshot["items"][-1])
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
                        snapshot = get_estimate_snapshot()
                        _print_item_resolution_snapshot(snapshot["items"][-1])
                    else:
                        print("Selected item not found; no item added.")
                    return
                else:
                    print("Invalid selection. Please try again.")

        elif next_action == "AWAIT_CLARIFICATION":
            user_reply = input("Provide clarification: ").strip()
            decision = estimator_runtime_step(validator_output, user_reply=user_reply)
            clarification = decision.get("user_clarification", "")
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
                snapshot = get_estimate_snapshot()
                _print_item_resolution_snapshot(snapshot["items"][-1])
                return
            else:
                current_description = revision
                continue  # loop back with revised description

        else:
            # Unknown action; treat as terminal error for safety
            print("Unexpected estimator action. Cannot proceed with this item.")
            return


def run_mvp_case_programmatic(description: str, user_responses: List[str]) -> Dict[str, Any]:
    """
    Programmatic entry point for automated tests or scripts.

    Mirrors the interactive flow but consumes a fixed list of user_responses
    instead of reading from stdin, and returns the final estimate snapshot.
    Quantity handling is not invoked here; it remains a separate concern.
    """
    _assert_ready_v3_5_silent_on_success()
    pack_registry.initialize_registry(log=False)

    init_estimate()
    current_description = description
    response_index = 0

    while True:
        ce_output = _retrieve_signals(current_description)
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
# Pricing-related helpers
# ---------------------------------------------------------------------------

def _apply_snapshot_and_write_back(updated_snapshot: Dict[str, Any]) -> None:
    """
    Write a modified snapshot back into the Merge Agent's in-memory model.
    This is required so that pricing and future operations see updated quantities.
    """
    ESTIMATE_MODEL["items"] = updated_snapshot.get("items", [])


def _print_pricing() -> None:
    """
    Apply quantities, run pricing, and print per-line pricing and total cost.
    """
    raw_snapshot = get_estimate_snapshot()
    if not raw_snapshot.get("items"):
        print("No items in estimate. Nothing to price.")
        return

    snapshot_with_quantities = apply_quantities(raw_snapshot)
    pricing_result = price_estimate(snapshot_with_quantities)
    items = pricing_result.get("items", [])

    print("Pricing:")
    total_cost = 0.0
    for idx, line in enumerate(items, start=1):
        item_id = line.get("item_id")
        name = line.get("display_name")
        source = line.get("source")
        qty = line.get("quantity")
        pricing = line.get("pricing")

        header = f"{idx}. source={source}, item_id={item_id}, name={name!r}"
        if isinstance(qty, (int, float)):
            header += f", quantity={qty}"
        else:
            header += ", quantity=not set"

        print(header)
        print("   pricing:", pricing)

        if isinstance(pricing, dict) and "total_cost" in pricing:
            cost = pricing["total_cost"]
            if isinstance(cost, (int, float)):
                total_cost += float(cost)

    print(f"Total catalog cost (provisional excluded): {total_cost:.2f}")


# ---------------------------------------------------------------------------
# CLI / REPL
# ---------------------------------------------------------------------------

def main() -> None:
    _force_utf8_stdio()
    assert_ready_or_exit(str(REPO_ROOT))
    pack_registry.initialize_registry(log=True)

    print("Welcome to Valesco MVP Runner v2.2")
    print("Type an item description to start CE handling.")
    print("Commands: 'show', 'meta <id>', 'reset', 'qty <index> <value>', 'clearqty <index>', 'price', 'exit'.")

    init_estimate()

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Valesco MVP Runner v2.2.")
            break

        if not line:
            continue

        lower = line.lower()

        if lower == "exit":
            print("Exiting Valesco MVP Runner v2.2.")
            break

        if lower == "show":
            _print_current_estimate_snapshot()
            continue

        if lower.startswith("meta "):
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

        if lower == "reset":
            init_estimate()
            print("Estimate reset.")
            continue

        if lower.startswith("qty "):
            parts = line.split()
            if len(parts) != 3:
                print("Usage: qty <index> <value>")
                continue
            try:
                index = int(parts[1]) - 1  # user-facing index is 1-based
                value = float(parts[2])
            except ValueError:
                print("Error: index must be integer and value must be numeric.")
                continue

            snapshot = get_estimate_snapshot()
            try:
                updated_snapshot = set_quantity(index, value, snapshot)
            except IndexError:
                print("Error: line index out of range.")
                continue
            except ValueError as e:
                print(f"Error: {e}")
                continue

            _apply_snapshot_and_write_back(updated_snapshot)
            print("Quantity updated.")
            _print_current_estimate_snapshot()
            continue

        if lower.startswith("clearqty "):
            parts = line.split()
            if len(parts) != 2:
                print("Usage: clearqty <index>")
                continue
            try:
                index = int(parts[1]) - 1
            except ValueError:
                print("Error: index must be integer.")
                continue

            snapshot = get_estimate_snapshot()
            try:
                updated_snapshot = clear_quantity(index, snapshot)
            except IndexError:
                print("Error: line index out of range.")
                continue

            _apply_snapshot_and_write_back(updated_snapshot)
            print("Quantity cleared.")
            _print_current_estimate_snapshot()
            continue

        if lower == "price":
            _print_pricing()
            continue

        # Treat any other input as an item description
        try:
            _run_single_item(line)
        except RuntimeError as exc:
            print(f"CE backend error: {exc}")
            raise SystemExit(1)
        _print_current_estimate_snapshot()


if __name__ == "__main__":
    main()
