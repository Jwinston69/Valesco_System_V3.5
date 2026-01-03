# C:/Valesco_System/engine/tests/pricing_engine_test_suite_v3.4.py
# Pricing Engine Test Suite v3.4
#
# Validates:
#   - Line-level pricing behaviour
#   - Snapshot-level pricing and totals
#   - Runner integration
#   - Determinism and deep-copy safety
#   - No inference, no enrichment, no mutation
#
# Tested module:
#   engine.modules.pricing_engine_v3_4

import unittest
from unittest.mock import patch
import tempfile
import os
import copy
import json

from engine.modules.pricing_engine_v3_4 import (
    price_line_item,
    price_estimate_snapshot,
    price_estimate_for_runner,
)
from engine.modules import pack_registry_v3_5 as pack_registry
from engine.modules.rate_library_ingestion_v3_1 import (
    load_raw_rate_library,
    build_internal_rate_library,
    save_internal_rate_library,
)


def _build_rate_library(external_rates):
    """Helper: build an internal rate library dict from external definitions."""
    normalized = load_raw_rate_library(external_rates)
    return build_internal_rate_library(normalized)


class TestPricingEngineV34(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pack_registry.initialize_registry(log=False)

    # ------------------------------------------------------------------
    # GROUP A — Line-Level Pricing (8 tests)
    # ------------------------------------------------------------------

    def test_1_provisional_item_user_supplied_only(self):
        rate_library = {}
        item = {
            "item_id": None,
            "source": "provisional",
            "display_name": "Custom Item",
            "metadata": {},
            "status": "confirmed",
        }

        result = price_line_item(item, rate_library)
        self.assertEqual(result, {"pricing": "user-supplied only"})

    def test_2_catalog_item_with_valid_rate_and_quantity(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Material + labour",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                    "labour": {"rate": 6.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        item = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Example Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": 5.0,
        }

        result = price_line_item(item, rate_library)
        self.assertEqual(result["item_id"], "A001")
        self.assertEqual(result["unit"], "m2")
        self.assertEqual(result["unit_rate"], 10.0)
        self.assertEqual(result["quantity"], 5.0)
        self.assertEqual(result["total_cost"], 50.0)

    def test_3_missing_quantity_quantity_required(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Material only",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        # No quantity
        item_no_qty = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Item",
            "metadata": {},
            "status": "confirmed",
        }
        result_no_qty = price_line_item(item_no_qty, rate_library)
        self.assertEqual(result_no_qty, {"pricing": "quantity_required"})

        # Invalid quantity value
        item_bad_qty = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": "abc",
        }
        result_bad_qty = price_line_item(item_bad_qty, rate_library)
        self.assertEqual(result_bad_qty, {"pricing": "quantity_required"})

    def test_4_no_rate_record_no_pricing_defined(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Rate present",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        item = {
            "item_id": "Z999",
            "source": "catalog",
            "display_name": "Unknown Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": 5.0,
        }

        result = price_line_item(item, rate_library)
        self.assertEqual(result, {"pricing": "no_pricing_defined"})

    def test_5_built_rate_has_no_unit_raises_value_error(self):
        # Library entry with all components None → build_up_rate yields unit=None
        # and total_rate=None, which must raise ValueError when quantity is present.
        rate_library = {
            "A001": {
                "id": "A001",
                "description": "No components",
                "components": {
                    "material": None,
                    "labour": None,
                    "plant": None,
                    "overhead": None,
                },
            }
        }

        item = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": 3.0,
        }

        with self.assertRaises(ValueError):
            price_line_item(item, rate_library)

    def test_6_built_rate_has_no_total_rate_no_pricing_defined(self):
        # For this test, simulate a built rate with unit but no total_rate
        # by temporarily patching build_up_rate.
        from engine.modules import rate_build_up_v3_3 as rb

        external_rates = [
            {
                "id": "A001",
                "description": "Dummy rate",
                "components": {
                    "material": {"rate": 0.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        item = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": 5.0,
        }

        original_build_up_rate = rb.build_up_rate

        def fake_build_up_rate(rec):
            built = original_build_up_rate(rec)
            built["total_rate"] = None
            built["unit"] = "m2"
            return built

        rb.build_up_rate = fake_build_up_rate
        try:
            from engine.modules import pricing_engine_v3_4 as pe

            result = pe.price_line_item(item, rate_library)
            self.assertEqual(result, {"pricing": "no_pricing_defined"})
        finally:
            rb.build_up_rate = original_build_up_rate

    def test_7_mixed_components_some_none(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Material + overhead",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                    "overhead": {"rate": 1.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        item = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": 2.0,
        }

        result = price_line_item(item, rate_library)
        # total_rate should be 4.0 + 1.0 = 5.0
        self.assertEqual(result["unit_rate"], 5.0)
        self.assertEqual(result["total_cost"], 10.0)

    def test_8_determinism_for_identical_item(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Material only",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        item = {
            "item_id": "A001",
            "source": "catalog",
            "display_name": "Item",
            "metadata": {},
            "status": "confirmed",
            "quantity": 3.0,
        }

        result1 = price_line_item(item, rate_library)
        result2 = price_line_item(item, rate_library)
        self.assertEqual(result1, result2)

        result1["unit_rate"] = 999.0
        self.assertNotEqual(result1["unit_rate"], result2["unit_rate"])

    # ------------------------------------------------------------------
    # GROUP B — Snapshot-Level Pricing (4 tests)
    # ------------------------------------------------------------------

    def test_9_multi_item_snapshot_mixed_outcomes(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Material only",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Priced Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 2.0,
                },
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Needs Quantity",
                    "metadata": {},
                    "status": "confirmed",
                },
                {
                    "item_id": "Z999",
                    "source": "catalog",
                    "display_name": "No Rate",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 1.0,
                },
                {
                    "item_id": None,
                    "source": "provisional",
                    "display_name": "Provisional",
                    "metadata": {},
                    "status": "confirmed",
                },
            ]
        }

        result = price_estimate_snapshot(snapshot, rate_library)
        lines = result["lines"]

        self.assertEqual(len(lines), 4)

        self.assertIn("total_cost", lines[0])
        self.assertEqual(lines[0]["total_cost"], 8.0)

        self.assertEqual(lines[1], {"pricing": "quantity_required"})
        self.assertEqual(lines[2], {"pricing": "no_pricing_defined"})
        self.assertEqual(lines[3], {"pricing": "user-supplied only"})

        self.assertEqual(result["total_cost"], 8.0)

    def test_10_deterministic_snapshot_pricing(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Material only",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 3.0,
                }
            ]
        }

        result1 = price_estimate_snapshot(snapshot, rate_library)
        result2 = price_estimate_snapshot(snapshot, rate_library)
        self.assertEqual(result1, result2)

    def test_11_correct_ordering_preserved(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Rate 1",
                "components": {
                    "material": {"rate": 1.0, "unit": "m2"},
                },
            },
            {
                "id": "A002",
                "description": "Rate 2",
                "components": {
                    "material": {"rate": 2.0, "unit": "m2"},
                },
            },
        ]
        rate_library = _build_rate_library(external_rates)

        snapshot = {
            "items": [
                {
                    "item_id": "A002",
                    "source": "catalog",
                    "display_name": "Second",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 1.0,
                },
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "First",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 1.0,
                },
            ]
        }

        result = price_estimate_snapshot(snapshot, rate_library)
        self.assertEqual(len(result["lines"]), 2)
        self.assertEqual(result["lines"][0]["item_id"], "A002")
        self.assertEqual(result["lines"][1]["item_id"], "A001")

    def test_12_snapshot_not_mutated(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Rate",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        rate_library = _build_rate_library(external_rates)

        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Item",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 2.0,
                }
            ]
        }
        snapshot_before = copy.deepcopy(snapshot)

        _ = price_estimate_snapshot(snapshot, rate_library)
        self.assertEqual(snapshot, snapshot_before)

    # ------------------------------------------------------------------
    # GROUP C — Runner-Ready Pricing Function (2 tests)
    # ------------------------------------------------------------------

    def test_13_price_estimate_for_runner_loads_and_prices_correctly(self):
        external_rates = [
            {
                "id": "A001",
                "description": "Rate",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            }
        ]
        normalized = load_raw_rate_library(external_rates)
        library = build_internal_rate_library(normalized)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rates.json")
            save_internal_rate_library(library, path)

            snapshot = {
                "items": [
                    {
                        "item_id": "A001",
                        "source": "catalog",
                        "display_name": "Item",
                        "metadata": {},
                        "status": "confirmed",
                        "quantity": 3.0,
                    }
                ]
            }

            price_fn = price_estimate_for_runner(path)
            result1 = price_fn(snapshot)
            result2 = price_fn(snapshot)

            self.assertEqual(result1["total_cost"], 12.0)
            self.assertEqual(result1, result2)

    def test_14_invalid_rate_library_path_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "invalid_rates.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{invalid json")

            with self.assertRaises(ValueError):
                _ = price_estimate_for_runner(path)
                # load_rate_library/load_internal_rate_library should raise

    # ------------------------------------------------------------------
    # GROUP D - Pack Registry Authority (2 tests)
    # ------------------------------------------------------------------

    def test_15_registry_not_initialized_raises(self):
        item = {
            "item_id": None,
            "source": "provisional",
            "display_name": "Custom Item",
            "metadata": {},
            "status": "confirmed",
        }

        with patch(
            "engine.modules.pricing_engine_v3_4.pack_registry.is_initialized",
            return_value=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "Pack registry not initialized"):
                price_line_item(item, {})

    def test_16_missing_authority_pack_raises(self):
        item = {
            "item_id": None,
            "source": "provisional",
            "display_name": "Custom Item",
            "metadata": {},
            "status": "confirmed",
        }

        with patch(
            "engine.modules.pricing_engine_v3_4.pack_registry.get_subcontractors",
            side_effect=KeyError("subcontractors"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "library/core/valesco_subcontractors.yaml",
            ):
                price_line_item(item, {})


if __name__ == "__main__":
    unittest.main()
