# C:/Valesco_System/engine/tests/assembly_pack_resolver_test_suite_v3.2.py
# Assembly / Pack Resolver Integration Test Suite v3.2
#
# Validates:
#   - Pack structure validation
#   - Single-pack deterministic expansion
#   - Multi-pack deterministic expansion
#   - CE-safety (no inference, no mutation)
#   - Deep-copy integrity
#
# Required: 14 tests.

import unittest
import copy

from engine.modules.assembly_pack_resolver_v3_2 import (
    validate_pack_structure,
    resolve_pack,
    resolve_multiple_packs,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _normalized_pack():
    return {
        "id": "PACK001",
        "name": "Test Pack",
        "items": [
            {"catalog_id": "A001", "multiplier": 1.0},
            {"catalog_id": "A002", "multiplier": 0.5},
        ],
    }


class TestAssemblyPackResolverV32(unittest.TestCase):

    # ----------------------------------------------------------------------
    # GROUP A — Validation Tests (5 tests)
    # ----------------------------------------------------------------------

    def test_1_valid_pack_passes_validation(self):
        pack = _normalized_pack()
        validate_pack_structure(pack)  # should not raise

    def test_2_missing_required_keys(self):
        pack = _normalized_pack()
        for key in ("id", "name", "items"):
            with self.subTest(key=key):
                bad = copy.deepcopy(pack)
                bad.pop(key)
                with self.assertRaises(ValueError):
                    validate_pack_structure(bad)

    def test_3_empty_items_list(self):
        pack = _normalized_pack()
        pack["items"] = []
        with self.assertRaises(ValueError):
            validate_pack_structure(pack)

    def test_4_invalid_item_schema(self):
        # Item missing catalog_id
        bad1 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"multiplier": 1.0}],
        }
        with self.assertRaises(ValueError):
            validate_pack_structure(bad1)

        # Item missing multiplier
        bad2 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"catalog_id": "A001"}],
        }
        with self.assertRaises(ValueError):
            validate_pack_structure(bad2)

        # Item wrong type
        bad3 = {
            "id": "PACK001",
            "name": "Pack",
            "items": ["not-a-dict"],
        }
        with self.assertRaises(ValueError):
            validate_pack_structure(bad3)

    def test_5_negative_or_non_numeric_multiplier(self):
        # Negative
        bad1 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"catalog_id": "A001", "multiplier": -1}],
        }
        with self.assertRaises(ValueError):
            validate_pack_structure(bad1)

        # Non-numeric
        bad2 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"catalog_id": "A001", "multiplier": "abc"}],
        }
        with self.assertRaises(ValueError):
            validate_pack_structure(bad2)

    # ----------------------------------------------------------------------
    # GROUP B — Single Pack Resolution (5 tests)
    # ----------------------------------------------------------------------

    def test_6_resolve_pack_base_quantity_10(self):
        pack = _normalized_pack()
        result = resolve_pack(pack, 10.0)
        # Expected:
        # A001 → 1.0 * 10 → 10
        # A002 → 0.5 * 10 → 5
        expected = [
            {"catalog_id": "A001", "derived_quantity": 10.0, "multiplier": 1.0},
            {"catalog_id": "A002", "derived_quantity": 5.0, "multiplier": 0.5},
        ]
        self.assertEqual(result, expected)

    def test_7_zero_multiplier(self):
        pack = {
            "id": "PACK001",
            "name": "Zero Mult Pack",
            "items": [
                {"catalog_id": "A001", "multiplier": 0.0},
            ],
        }
        result = resolve_pack(pack, 10.0)
        self.assertEqual(
            result,
            [{"catalog_id": "A001", "derived_quantity": 0.0, "multiplier": 0.0}],
        )

    def test_8_multiple_items_mixed_multipliers(self):
        pack = {
            "id": "PACK001",
            "name": "Mixed Mult Pack",
            "items": [
                {"catalog_id": "A005", "multiplier": 2.0},
                {"catalog_id": "A010", "multiplier": 0.25},
                {"catalog_id": "A020", "multiplier": 1.0},
            ],
        }
        result = resolve_pack(pack, 8.0)
        expected = [
            {"catalog_id": "A005", "derived_quantity": 16.0, "multiplier": 2.0},
            {"catalog_id": "A010", "derived_quantity": 2.0, "multiplier": 0.25},
            {"catalog_id": "A020", "derived_quantity": 8.0, "multiplier": 1.0},
        ]
        self.assertEqual(result, expected)

    def test_9_non_numeric_base_quantity_raises(self):
        pack = _normalized_pack()
        with self.assertRaises(ValueError):
            resolve_pack(pack, "abc")

    def test_10_no_mutation_of_input_pack(self):
        pack = _normalized_pack()
        pack_before = copy.deepcopy(pack)
        _ = resolve_pack(pack, 10.0)
        self.assertEqual(pack, pack_before)

    # ----------------------------------------------------------------------
    # GROUP C — Multiple Pack Resolution (4 tests)
    # ----------------------------------------------------------------------

    def test_11_resolve_multiple_packs_deterministic_order(self):
        pack1 = {
            "id": "PACK001",
            "name": "Pack 1",
            "items": [
                {"catalog_id": "A001", "multiplier": 1.0},
                {"catalog_id": "A002", "multiplier": 2.0},
            ],
        }
        pack2 = {
            "id": "PACK002",
            "name": "Pack 2",
            "items": [
                {"catalog_id": "A010", "multiplier": 0.5},
            ],
        }

        library = {
            "PACK001": pack1,
            "PACK002": pack2,
        }

        selections = [
            {"pack_id": "PACK001", "quantity": 10.0},
            {"pack_id": "PACK002", "quantity": 4.0},
        ]

        result = resolve_multiple_packs(library, selections)

        expected = [
            {"catalog_id": "A001", "derived_quantity": 10.0, "multiplier": 1.0},
            {"catalog_id": "A002", "derived_quantity": 20.0, "multiplier": 2.0},
            {"catalog_id": "A010", "derived_quantity": 2.0, "multiplier": 0.5},
        ]

        self.assertEqual(result, expected)

    def test_12_missing_pack_id_raises(self):
        library = {"PACK001": _normalized_pack()}
        selections = [
            {"pack_id": "PACK999", "quantity": 10.0},
        ]
        with self.assertRaises(ValueError):
            resolve_multiple_packs(library, selections)

    def test_13_invalid_quantity_type_raises(self):
        library = {"PACK001": _normalized_pack()}
        selections = [
            {"pack_id": "PACK001", "quantity": "abc"},
        ]
        with self.assertRaises(ValueError):
            resolve_multiple_packs(library, selections)

    def test_14_no_mutation_of_pack_library(self):
        pack1 = _normalized_pack()
        pack2 = {
            "id": "PACK002",
            "name": "Pack 2",
            "items": [{"catalog_id": "A010", "multiplier": 0.5}],
        }

        library = {
            "PACK001": copy.deepcopy(pack1),
            "PACK002": copy.deepcopy(pack2),
        }
        before = copy.deepcopy(library)

        selections = [
            {"pack_id": "PACK001", "quantity": 10.0},
            {"pack_id": "PACK002", "quantity": 2.0},
        ]

        _ = resolve_multiple_packs(library, selections)
        self.assertEqual(library, before)


if __name__ == "__main__":
    unittest.main()
