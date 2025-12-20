# C:/Valesco_System/engine/tests/ce_backend_adapter_test_suite_v3.2.py
# CE Backend Adapter Test Suite v3.2
#
# Validates:
#   - Single-item conversion correctness
#   - Schema correctness for internal + CE backend formats
#   - Determinism
#   - Deep-copy safety
#   - Export payload correctness
#   - No inference / no enrichment
#
# Required: 12 tests.

import unittest
import tempfile
import os
import json
import copy

from engine.modules.ce_backend_adapter_v3_2 import (
    to_ce_backend_item,
    to_ce_backend_catalog,
    validate_ce_backend_input,
    export_ce_backend_payload,
)


# ---------------------------------------------------------------------------
# Helper internal catalog item
# ---------------------------------------------------------------------------

def _valid_internal_item():
    return {
        "id": "A001",
        "name": "Example Item",
        "category": "wall",
        "attributes": {"finish": "galvanised", "thickness": "100mm"},
        "score_placeholder": 0.0,
    }


class TestCEBackendAdapterV32(unittest.TestCase):

    # ----------------------------------------------------------------------
    # GROUP A — Single Item Conversion (4 tests)
    # ----------------------------------------------------------------------

    def test_1_valid_internal_item_converts_correctly(self):
        internal = _valid_internal_item()
        converted = to_ce_backend_item(internal)

        expected = {
            "id": "A001",
            "name": "Example Item",
            "category": "wall",
            "attributes": {"finish": "galvanised", "thickness": "100mm"},
        }
        self.assertEqual(converted, expected)

        # Ensure score_placeholder is dropped
        self.assertNotIn("score_placeholder", converted)

        # Ensure deep-copy of attributes
        self.assertIsNot(converted["attributes"], internal["attributes"])

    def test_2_malformed_internal_schema_raises(self):
        bad = _valid_internal_item()
        bad.pop("attributes")
        with self.assertRaises(ValueError):
            to_ce_backend_item(bad)

    def test_3_ce_backend_item_schema_validated_correctly(self):
        # Proper CE backend item
        item = {
            "id": "A001",
            "name": "Example Item",
            "category": "wall",
            "attributes": {"finish": "galvanised"},
        }
        # This should not raise
        validate_ce_backend_input(item)

        # Extra field → must fail
        bad = dict(item)
        bad["extra"] = 123
        with self.assertRaises(ValueError):
            validate_ce_backend_input(bad)

    def test_4_no_mutation_of_internal_item(self):
        internal = _valid_internal_item()
        before = copy.deepcopy(internal)
        _ = to_ce_backend_item(internal)
        self.assertEqual(internal, before)

    # ----------------------------------------------------------------------
    # GROUP B — Full Catalog Conversion (4 tests)
    # ----------------------------------------------------------------------

    def test_5_catalog_dict_sorted_conversion(self):
        catalog = {
            "B002": {
                "id": "B002",
                "name": "Item B",
                "category": "catB",
                "attributes": {"x": 1},
                "score_placeholder": 0.0,
            },
            "A001": _valid_internal_item(),
        }
        ce_list = to_ce_backend_catalog(catalog)
        ids = [item["id"] for item in ce_list]
        self.assertEqual(ids, ["A001", "B002"])

    def test_6_malformed_items_in_catalog_raise(self):
        bad_catalog = {
            "A001": _valid_internal_item(),
            "B002": {
                "id": "B002",
                "name": "Bad Item",
                # missing "category", "attributes", "score_placeholder"
            },
        }
        with self.assertRaises(ValueError):
            to_ce_backend_catalog(bad_catalog)

    def test_7_deterministic_repeated_conversion(self):
        catalog = {
            "B002": {
                "id": "B002",
                "name": "Item B",
                "category": "catB",
                "attributes": {"x": 1},
                "score_placeholder": 0.0,
            },
            "A001": _valid_internal_item(),
        }
        out1 = to_ce_backend_catalog(catalog)
        out2 = to_ce_backend_catalog(catalog)
        self.assertEqual(out1, out2)

    def test_8_deep_copy_protection_on_catalog_conversion(self):
        catalog = {
            "A001": _valid_internal_item(),
        }
        converted = to_ce_backend_catalog(catalog)
        converted[0]["attributes"]["finish"] = "changed"
        # Original must remain unchanged
        self.assertEqual(
            catalog["A001"]["attributes"]["finish"],
            "galvanised"
        )

    # ----------------------------------------------------------------------
    # GROUP C — Export Payload (4 tests)
    # ----------------------------------------------------------------------

    def test_9_valid_ce_list_save_and_reload(self):
        ce_list = [
            {
                "id": "A001",
                "name": "Example Item",
                "category": "wall",
                "attributes": {"finish": "galvanised"},
            },
            {
                "id": "A002",
                "name": "Item 2",
                "category": "wall",
                "attributes": {"thickness": "50mm"},
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "ce_catalog.json")
            export_ce_backend_payload(ce_list, path)

            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

        # Must match exactly, sorted by ID
        expected_sorted_ids = ["A001", "A002"]
        self.assertEqual([x["id"] for x in loaded], expected_sorted_ids)

        # Attributes preserved
        self.assertEqual(loaded[0]["attributes"], {"finish": "galvanised"})

    def test_10_export_sorts_items_deterministically(self):
        ce_list = [
            {
                "id": "C003",
                "name": "C Item",
                "category": "wall",
                "attributes": {"a": 1},
            },
            {
                "id": "A001",
                "name": "A Item",
                "category": "wall",
                "attributes": {"b": 2},
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sorted.json")
            export_ce_backend_payload(ce_list, path)

            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

        self.assertEqual([item["id"] for item in loaded], ["A001", "C003"])

    def test_11_invalid_ce_input_structure_raises(self):
        bad_ce_list = [
            {
                "id": "A001",
                "name": "Item",
                "category": "wall",
                "attributes": {"finish": "galv"},
                "extra": "not allowed",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "invalid.json")
            with self.assertRaises(ValueError):
                export_ce_backend_payload(bad_ce_list, path)

    def test_12_non_serializable_attributes_raises(self):
        ce_list = [
            {
                "id": "A001",
                "name": "Item",
                "category": "wall",
                "attributes": {"obj": object()},  # not JSON serializable
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "invalid_attrs.json")
            with self.assertRaises(ValueError):
                export_ce_backend_payload(ce_list, path)


if __name__ == "__main__":
    unittest.main()
