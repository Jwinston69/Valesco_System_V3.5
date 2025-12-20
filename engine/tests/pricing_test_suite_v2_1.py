# C:/Valesco_System/engine/tests/pricing_test_suite_v2.1.py
# Pricing Test Suite v2.1 — Deterministic Automated Tests
#
# Validates pricing logic:
#   - Deterministic unit-rate retrieval
#   - No inference
#   - Correct pricing of catalog items
#   - Provisional item handling
#   - Estimate-level pricing correctness
#   - Integrity with Material Manager metadata
#   - Deterministic repeated runs
#   - Compatibility with Merge Agent snapshot formats

import unittest
import copy

from engine.modules.pricing_logic_v2_1 import (
    get_unit_rate,
    price_item,
    price_estimate,
    MOCK_PRICING,
)

from engine.modules.material_manager_v2_1 import get_metadata
from engine.modules.merge_agent_v2_1 import (
    init_estimate,
    add_catalog_item,
    add_provisional_item,
    get_estimate_snapshot,
)


class TestPricingLogic(unittest.TestCase):

    # ----------------------------------------------------------------------
    # 1. Test Unit Rate Lookup
    # ----------------------------------------------------------------------
    def test_unit_rate_lookup(self):
        rate = get_unit_rate("A001")
        self.assertIsNotNone(rate)
        self.assertEqual(rate["unit_rate"], 12.50)
        self.assertEqual(rate["unit"], "m2")

    # ----------------------------------------------------------------------
    # 2. Test Unknown Unit Rate
    # ----------------------------------------------------------------------
    def test_unknown_unit_rate(self):
        self.assertIsNone(get_unit_rate("Z999"))

    # ----------------------------------------------------------------------
    # 3. Test Single Item Pricing
    # ----------------------------------------------------------------------
    def test_single_item_pricing(self):
        result = price_item("A001", 4.0)
        self.assertIsNotNone(result)
        self.assertEqual(result["item_id"], "A001")
        self.assertEqual(result["quantity"], 4.0)
        self.assertEqual(result["unit"], "m2")
        self.assertEqual(result["unit_rate"], 12.50)
        self.assertEqual(result["total_cost"], 4.0 * 12.50)

    # ----------------------------------------------------------------------
    # 4. Test Missing Quantity → “quantity_required”
    # ----------------------------------------------------------------------
    def test_missing_quantity(self):
        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Single Clean-Match Item",
                    "metadata": {},
                    "status": "confirmed",
                    # No quantity provided
                }
            ]
        }

        priced = price_estimate(snapshot)
        entry = priced["items"][0]["pricing"]
        self.assertEqual(entry, {"pricing": "quantity_required"})

    # ----------------------------------------------------------------------
    # 5. Test Provisional Item → “user-supplied only”
    # ----------------------------------------------------------------------
    def test_provisional_item(self):
        snapshot = {
            "items": [
                {
                    "item_id": None,
                    "source": "provisional",
                    "display_name": "Non-standard",
                    "metadata": {},
                    "status": "confirmed",
                }
            ]
        }

        priced = price_estimate(snapshot)
        entry = priced["items"][0]["pricing"]
        self.assertEqual(entry, {"pricing": "user-supplied only"})

    # ----------------------------------------------------------------------
    # 6. Test No Pricing Defined
    # ----------------------------------------------------------------------
    def test_no_pricing_defined(self):
        # Create snapshot using an ID missing from MOCK_PRICING
        snapshot = {
            "items": [
                {
                    "item_id": "X999",
                    "source": "catalog",
                    "display_name": "Unknown Catalog Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 10.0,
                }
            ]
        }

        priced = price_estimate(snapshot)
        entry = priced["items"][0]["pricing"]
        self.assertEqual(entry, {"pricing": "no_pricing_defined"})

    # ----------------------------------------------------------------------
    # 7. Test Full Estimate Pricing
    # ----------------------------------------------------------------------
    def test_full_estimate_pricing(self):
        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Match Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 2.0,
                },
                {
                    "item_id": "B002",
                    "source": "catalog",
                    "display_name": "Ambiguous Item 2",
                    "metadata": {},
                    "status": "confirmed",
                    # Missing quantity
                },
                {
                    "item_id": None,
                    "source": "provisional",
                    "display_name": "Custom Spec",
                    "metadata": {},
                    "status": "confirmed",
                },
            ]
        }

        priced = price_estimate(snapshot)
        items = priced["items"]

        # A001 priced
        a = items[0]["pricing"]
        self.assertAlmostEqual(a["total_cost"], 2.0 * MOCK_PRICING["A001"]["unit_rate"])
        self.assertEqual(a["unit"], MOCK_PRICING["A001"]["unit"])

        # B002 requires quantity
        b = items[1]["pricing"]
        self.assertEqual(b, {"pricing": "quantity_required"})

        # Provisional
        p = items[2]["pricing"]
        self.assertEqual(p, {"pricing": "user-supplied only"})

    # ----------------------------------------------------------------------
    # 8. Test Determinism
    # ----------------------------------------------------------------------
    def test_determinism(self):
        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Match Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 3.0,
                }
            ]
        }

        r1 = price_estimate(snapshot)
        r2 = price_estimate(snapshot)
        self.assertEqual(r1, r2)

    # ----------------------------------------------------------------------
    # 9. Test Integrity Against Material Manager
    # ----------------------------------------------------------------------
    def test_integrity_against_material_manager(self):
        # Fetch metadata
        meta_before = get_metadata("A001")
        meta_copy = copy.deepcopy(meta_before)

        # Call pricing functions
        _ = get_unit_rate("A001")
        _ = price_item("A001", 2.0)

        # Ensure metadata not mutated
        meta_after = get_metadata("A001")
        self.assertEqual(meta_before, meta_copy)
        self.assertEqual(meta_after, meta_copy)

    # ----------------------------------------------------------------------
    # 10. Smoke Test — Integration with Merge Agent Snapshot
    # ----------------------------------------------------------------------
    def test_integration_with_merge_agent_snapshot(self):
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Single Clean-Match Item"})
        snapshot = get_estimate_snapshot()

        # Attach quantity
        snapshot["items"][0]["quantity"] = 4.0

        priced = price_estimate(snapshot)
        line = priced["items"][0]["pricing"]

        self.assertEqual(line["unit_rate"], MOCK_PRICING["A001"]["unit_rate"])
        self.assertEqual(line["quantity"], 4.0)
        self.assertAlmostEqual(
            line["total_cost"],
            4.0 * MOCK_PRICING["A001"]["unit_rate"],
        )


if __name__ == "__main__":
    unittest.main()
