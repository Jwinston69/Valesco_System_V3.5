# C:/Valesco_System/engine/tests/pricing_integration_test_suite_v2.2.py
# Full-System Pricing Integration Test Suite v2.2 — End-to-End
#
# Validates the pipeline:
# Quantity → Merge Agent → Pricing → Runner (programmatic)
#
# Focus:
#   - Deterministic behaviour
#   - No inference of quantities
#   - Correct catalog vs provisional handling
#   - Alignment between logic layers and runner

import unittest
import copy
import os
import tempfile
import textwrap
from pathlib import Path

from engine.modules.merge_agent_v2_1 import (
    init_estimate,
    add_catalog_item,
    add_provisional_item,
    get_estimate_snapshot,
)
from engine.modules.pricing_logic_v2_1 import price_estimate, MOCK_PRICING
from engine.modules.quantity_logic_v2_1 import set_quantity, clear_quantity, apply_quantities
from engine.modules.material_manager_v2_1 import get_metadata

from engine.scripts.mvp_runner_v2_2 import run_mvp_case_programmatic


def _write_ce_backend_stub(path: Path) -> None:
    stub = textwrap.dedent(
        """
        import json
        import sys

        MOCK_ITEMS = {
            "clean_match": [
                {"id": "A001", "name": "Single Clean-Match Item", "category": "core", "score": 0.98}
            ],
            "ambiguous": [
                {"id": "B001", "name": "Ambiguous Item 1", "category": "core", "score": 0.72},
                {"id": "B002", "name": "Ambiguous Item 2", "category": "core", "score": 0.71},
                {"id": "B003", "name": "Ambiguous Item 3", "category": "core", "score": 0.70},
            ],
            "insufficient": [
                {"id": "C001", "name": "Weak Coverage Item", "category": "misc", "score": 0.40}
            ],
            "compatible": [
                {"id": "E001", "name": "Compatible Item 1", "category": "alt", "score": 0.65},
                {"id": "E002", "name": "Compatible Item 2", "category": "alt", "score": 0.63},
            ],
            "empty": [],
        }

        PROFILE_MAP = {
            "clean": "clean_match",
            "exact": "clean_match",
            "single": "clean_match",
            "ambiguous": "ambiguous",
            "three": "ambiguous",
            "close": "ambiguous",
            "insufficient": "insufficient",
            "unclear": "insufficient",
            "weak": "insufficient",
            "none": "empty",
            "missing": "empty",
            "nomatch": "empty",
            "compatible": "compatible",
            "alternative": "compatible",
            "alt": "compatible",
        }

        def _select_profile(description: str) -> str:
            text = description.lower()
            for key, profile in PROFILE_MAP.items():
                if key in text:
                    return profile
            return "ambiguous"

        def _build_signals(profile, items):
            hit_count = len(items)
            if hit_count == 0:
                return {
                    "hit_count": 0,
                    "top_score": None,
                    "score_gap_to_next": None,
                    "coverage_flags": {"none": True, "weak": False, "strong": False},
                    "retrieved_items": [],
                }

            ordered = sorted(items, key=lambda x: x["score"], reverse=True)
            top_score = ordered[0]["score"]
            score_gap = None
            if hit_count > 1:
                score_gap = top_score - ordered[1]["score"]

            if profile == "clean_match":
                coverage = {"strong": True, "weak": False, "conflicting": False}
            elif profile == "ambiguous":
                coverage = {"strong": True, "weak": False, "conflicting": False}
            elif profile == "insufficient":
                coverage = {"strong": False, "weak": True, "conflicting": False}
            elif profile == "compatible":
                coverage = {"strong": True, "compatible": True}
            else:
                coverage = {"weak": True}

            return {
                "hit_count": hit_count,
                "top_score": top_score,
                "score_gap_to_next": score_gap,
                "coverage_flags": coverage,
                "retrieved_items": ordered,
            }

        def main():
            payload = json.load(sys.stdin)
            description = payload.get("description", "")
            profile = _select_profile(description)
            items = MOCK_ITEMS.get(profile, [])
            output = _build_signals(profile, list(items))
            json.dump(output, sys.stdout)

        if __name__ == "__main__":
            main()
        """
    ).lstrip()
    path.write_text(stub, encoding="utf-8")


class TestFullSystemPricingIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._backend_tmp = tempfile.TemporaryDirectory()
        cls._backend_script = Path(cls._backend_tmp.name) / "ce_backend_stub.py"
        _write_ce_backend_stub(cls._backend_script)
        cls._prev_backend_cmd = os.environ.get("VALESCO_CE_BACKEND_CMD")
        cls._prev_backend_script = os.environ.get("VALESCO_CE_BACKEND_SCRIPT")
        os.environ["VALESCO_CE_BACKEND_SCRIPT"] = str(cls._backend_script)
        if "VALESCO_CE_BACKEND_CMD" in os.environ:
            del os.environ["VALESCO_CE_BACKEND_CMD"]

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._prev_backend_cmd is None:
            os.environ.pop("VALESCO_CE_BACKEND_CMD", None)
        else:
            os.environ["VALESCO_CE_BACKEND_CMD"] = cls._prev_backend_cmd
        if cls._prev_backend_script is None:
            os.environ.pop("VALESCO_CE_BACKEND_SCRIPT", None)
        else:
            os.environ["VALESCO_CE_BACKEND_SCRIPT"] = cls._prev_backend_script
        cls._backend_tmp.cleanup()

    # ------------------------------------------------------------------
    # GROUP A — Basic Pricing Integration
    # ------------------------------------------------------------------

    def test_1_single_catalog_item_with_quantity(self):
        """Single catalog item with quantity → correct total cost."""
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Single Clean-Match Item"})
        snapshot = get_estimate_snapshot()

        # Set quantity on line 0
        snapshot_q = set_quantity(0, 10.0, snapshot)

        # Price estimate directly with snapshot having quantity
        priced = price_estimate(snapshot_q)
        line = priced["items"][0]["pricing"]

        self.assertEqual(line["item_id"], "A001")
        self.assertEqual(line["quantity"], 10.0)
        self.assertEqual(line["unit"], MOCK_PRICING["A001"]["unit"])
        self.assertEqual(line["unit_rate"], MOCK_PRICING["A001"]["unit_rate"])
        self.assertAlmostEqual(line["total_cost"], 10.0 * 12.50)

    def test_2_catalog_item_without_quantity(self):
        """Catalog item without quantity → quantity_required."""
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Single Clean-Match Item"})
        snapshot = get_estimate_snapshot()

        priced = price_estimate(snapshot)
        entry = priced["items"][0]["pricing"]
        self.assertEqual(entry, {"pricing": "quantity_required"})

    def test_3_provisional_item_present(self):
        """Provisional item → user-supplied only."""
        init_estimate()
        add_provisional_item("Custom non-standard item")
        snapshot = get_estimate_snapshot()

        priced = price_estimate(snapshot)
        entry = priced["items"][0]["pricing"]
        self.assertEqual(entry, {"pricing": "user-supplied only"})

    # ------------------------------------------------------------------
    # GROUP B — Multi-Item Integration
    # ------------------------------------------------------------------

    def test_4_mixed_catalog_and_provisional_with_quantities(self):
        """
        Mixed:
          - catalog with quantity → priced
          - provisional → user-supplied only
          - catalog without quantity → quantity_required
        """
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})
        add_provisional_item("Custom item")
        add_catalog_item({"id": "B002", "name": "Item B2"})

        snapshot = get_estimate_snapshot()
        snapshot = set_quantity(0, 5.0, snapshot)  # catalog with qty
        # line 1 provisional → no quantity
        # line 2 catalog → missing quantity

        priced = price_estimate(snapshot)
        items = priced["items"]

        # Catalog with quantity
        p0 = items[0]["pricing"]
        self.assertEqual(p0["item_id"], "A001")
        self.assertAlmostEqual(p0["total_cost"], 5.0 * MOCK_PRICING["A001"]["unit_rate"])

        # Provisional
        p1 = items[1]["pricing"]
        self.assertEqual(p1, {"pricing": "user-supplied only"})

        # Catalog missing quantity
        p2 = items[2]["pricing"]
        self.assertEqual(p2, {"pricing": "quantity_required"})

    def test_5_mixed_catalog_items_all_quantified(self):
        """Three catalog items, all with quantities → correct per-line and aggregate totals."""
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})
        add_catalog_item({"id": "B001", "name": "Item B1"})
        add_catalog_item({"id": "B003", "name": "Item B3"})

        snapshot = get_estimate_snapshot()
        snapshot = set_quantity(0, 2.0, snapshot)
        snapshot = set_quantity(1, 3.0, snapshot)
        snapshot = set_quantity(2, 4.0, snapshot)

        priced = price_estimate(snapshot)
        items = priced["items"]

        # Per-line checks
        p0 = items[0]["pricing"]
        p1 = items[1]["pricing"]
        p2 = items[2]["pricing"]

        self.assertAlmostEqual(p0["total_cost"], 2.0 * MOCK_PRICING["A001"]["unit_rate"])
        self.assertAlmostEqual(p1["total_cost"], 3.0 * MOCK_PRICING["B001"]["unit_rate"])
        self.assertAlmostEqual(p2["total_cost"], 4.0 * MOCK_PRICING["B003"]["unit_rate"])

        # Aggregate
        total = (
            p0["total_cost"]
            + p1["total_cost"]
            + p2["total_cost"]
        )
        expected_total = (
            2.0 * MOCK_PRICING["A001"]["unit_rate"]
            + 3.0 * MOCK_PRICING["B001"]["unit_rate"]
            + 4.0 * MOCK_PRICING["B003"]["unit_rate"]
        )
        self.assertAlmostEqual(total, expected_total)

    # ------------------------------------------------------------------
    # GROUP C — Runner Integration Scenarios
    # ------------------------------------------------------------------

    def test_6_runner_clean_match_quantity_pricing(self):
        """
        Runner: clean match (State A), confirm, then apply quantity and price.
        """
        # Clean match runner case
        snapshot = run_mvp_case_programmatic("clean item description", ["yes"])

        self.assertEqual(len(snapshot.get("items", [])), 1)
        line = snapshot["items"][0]
        self.assertEqual(line["item_id"], "A001")

        # Apply quantity via quantity_logic
        snapshot_q = set_quantity(0, 8.0, snapshot)
        snapshot_q = apply_quantities(snapshot_q)

        priced = price_estimate(snapshot_q)
        p0 = priced["items"][0]["pricing"]
        self.assertEqual(p0["item_id"], "A001")
        self.assertAlmostEqual(p0["total_cost"], 8.0 * MOCK_PRICING["A001"]["unit_rate"])

    def test_7_runner_ambiguous_selection_pricing(self):
        """
        Runner: ambiguous selection (State B), choose item 2, then price.
        """
        snapshot = run_mvp_case_programmatic("ambiguous item requiring choice", ["2"])

        self.assertEqual(len(snapshot.get("items", [])), 1)
        line = snapshot["items"][0]
        self.assertEqual(line["item_id"], "B002")

        snapshot_q = set_quantity(0, 3.0, snapshot)
        snapshot_q = apply_quantities(snapshot_q)

        priced = price_estimate(snapshot_q)
        p0 = priced["items"][0]["pricing"]
        self.assertEqual(p0["item_id"], "B002")
        self.assertAlmostEqual(p0["total_cost"], 3.0 * MOCK_PRICING["B002"]["unit_rate"])

    def test_8_runner_clarification_to_clean_match_pricing(self):
        """
        Runner: State C → clarification → State A → confirm → quantity → pricing.
        """
        # C → A via clarification "clean"
        snapshot = run_mvp_case_programmatic("insufficient description", ["clean", "yes"])

        self.assertEqual(len(snapshot.get("items", [])), 1)
        line = snapshot["items"][0]
        self.assertEqual(line["item_id"], "A001")

        snapshot_q = set_quantity(0, 6.0, snapshot)
        snapshot_q = apply_quantities(snapshot_q)

        priced = price_estimate(snapshot_q)
        p0 = priced["items"][0]["pricing"]
        self.assertEqual(p0["item_id"], "A001")
        self.assertAlmostEqual(p0["total_cost"], 6.0 * MOCK_PRICING["A001"]["unit_rate"])

    # ------------------------------------------------------------------
    # GROUP D — Edge Cases
    # ------------------------------------------------------------------

    def test_9_invalid_quantity_non_numeric(self):
        """Non-numeric quantity → ValueError."""
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})
        snapshot = get_estimate_snapshot()

        with self.assertRaises(ValueError):
            set_quantity(0, "abc", snapshot)  # type: ignore[arg-type]

    def test_10_invalid_index(self):
        """Invalid item index → IndexError."""
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})
        snapshot = get_estimate_snapshot()

        with self.assertRaises(IndexError):
            set_quantity(5, 10.0, snapshot)

        with self.assertRaises(IndexError):
            clear_quantity(5, snapshot)

    def test_11_metadata_integrity_after_pricing(self):
        """Material Manager metadata must not be mutated by pricing operations."""
        meta_before = get_metadata("A001")
        meta_copy = copy.deepcopy(meta_before)

        # Build snapshot that references metadata, then price it
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})
        snapshot = get_estimate_snapshot()
        snapshot = set_quantity(0, 4.0, snapshot)

        priced = price_estimate(snapshot)  # noqa: F841  # result unused, only side-effect check

        meta_after = get_metadata("A001")
        self.assertEqual(meta_before, meta_copy)
        self.assertEqual(meta_after, meta_copy)

    def test_12_determinism_under_repeated_pricing(self):
        """Same snapshot priced repeatedly must yield identical results."""
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})
        add_catalog_item({"id": "B001", "name": "Item B1"})

        snapshot = get_estimate_snapshot()
        snapshot = set_quantity(0, 2.0, snapshot)
        snapshot = set_quantity(1, 5.0, snapshot)
        snapshot = apply_quantities(snapshot)

        r1 = price_estimate(snapshot)
        r2 = price_estimate(snapshot)
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main()
