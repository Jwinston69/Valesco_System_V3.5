# C:/Valesco_System/engine/tests/quantity_test_suite_v2.1.py
# Quantity Test Suite v2.1 — Automated, Deterministic Tests
#
# Validates that quantity logic:
#   - Sets quantities deterministically
#   - Clears quantities safely
#   - Never infers quantities
#   - Preserves catalog metadata integrity
#   - Integrates cleanly with Merge Agent + pricing
#   - Produces deterministic output

import unittest
import copy

from engine.modules.quantity_logic_v2_1 import (
    set_quantity,
    clear_quantity,
    apply_quantities,
)

from engine.modules.material_manager_v2_1 import get_metadata
from engine.modules.merge_agent_v2_1 import (
    init_estimate,
    add_catalog_item,
    add_provisional_item,
    get_estimate_snapshot,
)
from engine.modules.pricing_logic_v2_1 import price_estimate


class TestQuantityLogic(unittest.TestCase):

    # ------------------------------------------------------------------
    # 1. Test Set Quantity
    # ------------------------------------------------------------------
    def test_set_quantity(self):
        snapshot = {
            "items": [
                {"item_id": "A001", "source": "catalog", "display_name": "A", "metadata": {}, "status": "confirmed"},
                {"item_id": "B001", "source": "catalog", "display_name": "B", "metadata": {}, "status": "confirmed"},
            ]
        }
        original = copy.deepcopy(snapshot)

        updated = set_quantity(0, 5.0, snapshot)

        # Original snapshot must be untouched
        self.assertEqual(snapshot, original)

        # Quantity applied correctly
        self.assertEqual(updated["items"][0].get("quantity"), 5.0)

        # Other items untouched
        self.assertNotIn("quantity", updated["items"][1])

    # ------------------------------------------------------------------
    # 2. Test Set Quantity (Invalid Non-Numeric)
    # ------------------------------------------------------------------
    def test_set_quantity_invalid_non_numeric(self):
        snapshot = {"items": [{"item_id": "A001", "source": "catalog", "metadata": {}, "status": "confirmed"}]}
        with self.assertRaises(ValueError):
            set_quantity(0, "abc", snapshot)

    # ------------------------------------------------------------------
    # 3. Test Set Quantity (Invalid Index)
    # ------------------------------------------------------------------
    def test_set_quantity_invalid_index(self):
        snapshot = {"items": []}
        with self.assertRaises(IndexError):
            set_quantity(0, 5.0, snapshot)

    # ------------------------------------------------------------------
    # 4. Test Clear Quantity
    # ------------------------------------------------------------------
    def test_clear_quantity(self):
        snapshot = {
            "items": [
                {"item_id": "A001", "source": "catalog", "metadata": {}, "status": "confirmed", "quantity": 10.0}
            ]
        }
        updated = clear_quantity(0, snapshot)

        # Quantity removed
        self.assertNotIn("quantity", updated["items"][0])

        # Metadata untouched
        self.assertEqual(updated["items"][0]["metadata"], snapshot["items"][0]["metadata"])

    # ------------------------------------------------------------------
    # 5. Test Apply Quantities (Identity)
    # ------------------------------------------------------------------
    def test_apply_quantities_identity(self):
        snapshot = {
            "items": [
                {"item_id": "A001", "source": "catalog", "quantity": 4.5},
                {"item_id": "B001", "source": "catalog"},  # Missing quantity
                {"item_id": "C001", "source": "catalog", "quantity": "invalid"},  # Invalid
            ]
        }

        updated = apply_quantities(snapshot)

        # Numeric quantity preserved
        self.assertEqual(updated["items"][0].get("quantity"), 4.5)

        # Missing quantity remains missing
        self.assertNotIn("quantity", updated["items"][1])

        # Invalid quantity removed
        self.assertNotIn("quantity", updated["items"][2])

        # Original snapshot remains unchanged
        self.assertEqual(snapshot["items"][0]["quantity"], 4.5)
        self.assertEqual(snapshot["items"][1].get("quantity"), None)
        self.assertEqual(snapshot["items"][2].get("quantity"), "invalid")

    # ------------------------------------------------------------------
    # 6. Test Determinism
    # ------------------------------------------------------------------
    def test_determinism(self):
        snapshot = {
            "items": [
                {"item_id": "A001", "source": "catalog", "quantity": 3.0},
                {"item_id": "B001", "source": "catalog"},
            ]
        }

        r1 = apply_quantities(snapshot)
        r2 = apply_quantities(snapshot)
        self.assertEqual(r1, r2)

    # ------------------------------------------------------------------
    # 7. Test Merge Agent Compatibility
    # ------------------------------------------------------------------
    def test_merge_agent_compatibility(self):
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A"})

        snapshot = get_estimate_snapshot()
        self.assertEqual(snapshot["items"][0]["item_id"], "A001")

        # Set quantity
        updated = set_quantity(0, 6.0, snapshot)

        # Price estimate
        priced = price_estimate(updated)
        line = priced["items"][0]["pricing"]

        # Correct total cost
        self.assertEqual(line["quantity"], 6.0)
        self.assertEqual(
            line["total_cost"],
            6.0 * line["unit_rate"],
        )

    # ------------------------------------------------------------------
    # 8. Test No Metadata Mutation
    # ------------------------------------------------------------------
    def test_no_metadata_mutation(self):
        meta_before = get_metadata("A001")
        meta_copy = copy.deepcopy(meta_before)

        # Run quantity logic
        snapshot = {
            "items": [
                {"item_id": "A001", "source": "catalog", "metadata": meta_before, "status": "confirmed"}
            ]
        }

        updated = set_quantity(0, 4.0, snapshot)
        updated = clear_quantity(0, updated)
        updated = apply_quantities(updated)

        meta_after = get_metadata("A001")

        # Metadata must not be mutated
        self.assertEqual(meta_before, meta_copy)
        self.assertEqual(meta_after, meta_copy)


if __name__ == "__main__":
    unittest.main()
