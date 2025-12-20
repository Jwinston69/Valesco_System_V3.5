#!/usr/bin/env python3

import os
import sys
import traceback

# ------------------------------------------------------------
# Force-load Valesco project
# ------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ENGINE = os.path.join(PROJECT_ROOT, "engine")
MODULES = os.path.join(ENGINE, "modules")

if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)
if MODULES not in sys.path:
    sys.path.insert(0, MODULES)

# READY v3.5 fail-closed gate (governance)
from engine.scripts.ready_gate_v3_5 import evaluate_ready


def safe_import(module, symbol=None):
    try:
        mod = __import__(module, fromlist=['*'])
        return getattr(mod, symbol) if symbol else mod
    except Exception:
        print(f"\nIMPORT FAILURE: {module}")
        traceback.print_exc()
        sys.exit(1)


# ------------------------------------------------------------
# Load CE + Router + Architect + Validator + Estimator Runtime
# ------------------------------------------------------------

retrieve_signals = safe_import("engine.modules.ce_retrieval_layer_v2_1", "retrieve")
route = safe_import("engine.modules.router_v2_1", "route")
build_arch = safe_import("engine.modules.architect_v2_1", "build_architect_payload")
validate_fn = safe_import("engine.modules.validator_v2_1", "validate")
runtime_step = safe_import("engine.modules.estimator_runtime_v2_1", "estimator_runtime_step")

# Material Manager = raw metadata only
mm = safe_import("engine.modules.material_manager_v2_1")

# Merge Agent = estimate model manager
merge_agent = safe_import("engine.modules.merge_agent_v2_1")


# ------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------

def _print_ready_summary_line_safely(ready_summary_line):
    try:
        print(ready_summary_line)
    except UnicodeEncodeError:
        print(
            "Valesco Pack [OK] / Materials [OK] / Tasks [OK] / Subcontractors [OK] - Ready to proceed."
        )


def main():
    # Refuse to start the REPL unless governance READY passes.
    ok, report_lines, ready_summary_line = evaluate_ready(PROJECT_ROOT)

    verbose = os.environ.get("VALESCO_VERBOSE", "").strip() == "1"

    if verbose:
        for line in report_lines:
            print(line)
    else:
        # Default UX: suppress INFO diagnostics (keep WARN/ERROR).
        for line in report_lines:
            if " | INFO | " in line:
                continue
            print(line)

    if not ok:
        sys.exit(1)

    _print_ready_summary_line_safely(ready_summary_line)

    print("\n===============================================")
    print("     V A L E S C O   U N I V E R S A L   R E P L")
    print("===============================================\n")
    print("Type item descriptions. Type 'exit' to quit.\n")

    # Reset model each run
    merge_agent.init_estimate()

    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Shutdown.")
            return

        try:
            # 1. CE retrieval
            ce_output = retrieve_signals(user_input)

            # 2. Router
            router_output = route(ce_output)

            # 3. Architect
            architect_output = build_arch(router_output)

            # 4. Validator
            validator_output = validate_fn(ce_output, router_output, architect_output)

            if not validator_output.get("valid"):
                print("\nVALIDATION FAILURE:", validator_output)
                continue

            # Runtime wants payload packaged inside Validator output
            validator_output = {
                "valid": True,
                "violation_code": None,
                "message": "OK",
                "payload": architect_output,
            }

            # 5. Estimator Runtime (phase 1)
            runtime_out = runtime_step(validator_output)

            print("\n--- SYSTEM MESSAGE --------------------------------")
            print(runtime_out.get("estimator_message", ""))
            items = runtime_out.get("items", [])
            if items:
                print("Items:")
                for i, item in enumerate(items, 1):
                    print(f"  {i}. {item}")

            next_action = runtime_out.get("next_action")

            # If estimator needs user decision
            if next_action in ("AWAIT_CONFIRMATION", "AWAIT_SELECTION", "AWAIT_CLARIFICATION", "AWAIT_REVISION"):
                user_reply = input(f"[{next_action}] > ").strip()
                decision = runtime_step(validator_output, user_reply)

                # Handle decision
                if decision.get("user_decision") == "CONFIRMED":
                    # Add selected catalog item (state A)
                    item = architect_output["items_presented"][0]
                    merge_agent.add_catalog_item(item)
                    print("Added:", item["id"])

                elif decision.get("user_decision") == "SELECTED":
                    item_id = decision.get("item_id")
                    item = mm.get_metadata(item_id)
                    merge_agent.add_catalog_item(item)
                    print("Selected:", item_id)

                elif decision.get("user_decision") == "REJECTED":
                    merge_agent.add_provisional_item(user_input)
                    print("Added provisional item.")

                elif "user_clarification" in decision:
                    print("Clarification received:", decision["user_clarification"])

                elif "user_revision" in decision:
                    print("Revision received:", decision["user_revision"])

            # Show snapshot after every item
            snapshot = merge_agent.get_estimate_snapshot()
            print("\n--- ESTIMATE SNAPSHOT ---------------------------")
            print(snapshot)
            print("--------------------------------------------------\n")

        except Exception:
            print("\nUNCAUGHT ERROR IN PIPELINE:")
            traceback.print_exc()


if __name__ == "__main__":
    main()
