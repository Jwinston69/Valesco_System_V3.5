# C:/Valesco_System/engine/tests/live_sync_pipeline_test_suite_v3.3.py
# Live Sync Pipeline Test Suite v3.3
#
# Validates:
#   - Catalog sync pipeline (ingestion → internal build → CE export)
#   - Rate sync pipeline (ingestion → internal build → persistence)
#   - Combined sync determinism
#   - File-level determinism & round-trip integrity
#   - Strict CE-safety and non-inference
#
# Required: 14 tests

import unittest
import tempfile
import os
import json
import copy

from engine.modules.live_sync_pipeline_v3_3 import (
    sync_catalog,
    sync_rate_library,
    sync_all,
)

# Import ingestion validators to compare structures indirectly
from engine.modules.catalog_ingestion_v3_0 import load_raw_catalog, build_internal_catalog
from engine.modules.rate_library_ingestion_v3_1 import load_raw_rate_library, build_internal_rate_library
from engine.modules.ce_backend_adapter_v3_2 import validate_ce_backend_input


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_raw_catalog():
    return [
        {
            "id": "A001",
            "name": "Item 1",
            "category": "wall",
            "attributes": {"finish": "galvanised"},
        },
        {
            "id": "A002",
            "name": "Item 2",
            "category": "floor",
            "attributes": {"thickness": "50mm"},
        },
    ]


def _valid_raw_rates():
    return [
        {
            "id": "R001",
            "description": "Rate 1",
            "components": {
                "material": {"rate": 4.2, "unit": "m2"},
                "labour": {"rate": 6.5, "unit": "m2"},
                "plant": {"rate": 0.0, "unit": "m2"},
            },
        },
        {
            "id": "R002",
            "description": "Rate 2",
            "components": {
                "material": {"rate": 2.0, "unit": "each"},
                "labour": {"rate": 1.0, "unit": "each"},
            },
        },
    ]


# ---------------------------------------------------------------------------
# GROUP A — Catalog Sync (6 tests)
# ---------------------------------------------------------------------------

class TestCatalogSync(unittest.TestCase):

    def test_1_valid_catalog_sync_produces_correct_internal_catalog(self):
        raw = _valid_raw_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")
            internal = sync_catalog(raw, path)

            # Compare to ingestion pipeline output
            normalized = load_raw_catalog(raw)
            expected_internal = build_internal_catalog(normalized)

            self.assertEqual(internal, expected_internal)
            self.assertEqual(list(internal.keys()), ["A001", "A002"])  # sorted order

    def test_2_ce_payload_generated_correctly(self):
        raw = _valid_raw_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")
            sync_catalog(raw, path)

            ce_path = f"{path}_ce.json"
            self.assertTrue(os.path.exists(ce_path))

            with open(ce_path, "r", encoding="utf-8") as f:
                ce_list = json.load(f)

            # Validate CE schema for each item
            for item in ce_list:
                validate_ce_backend_input(item)
                # score_placeholder must not be present
                self.assertNotIn("score_placeholder", item)

    def test_3_invalid_raw_catalog_input_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")
            with self.assertRaises(ValueError):
                sync_catalog("not-a-list", path)

    def test_4_malformed_catalog_item(self):
        raw = [
            {
                "id": "A001",
                "name": "Item",
                # Missing category, attributes
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")
            with self.assertRaises(ValueError):
                sync_catalog(raw, path)

    def test_5_internal_catalog_saved_correctly_roundtrip(self):
        raw = _valid_raw_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")
            internal = sync_catalog(raw, path)

            # Reload catalog.json
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            # Compare with internal
            self.assertEqual(loaded, internal)

    def test_6_ce_payload_saved_deterministically(self):
        raw = _valid_raw_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")

            sync_catalog(raw, path)
            with open(f"{path}_ce.json", "r", encoding="utf-8") as f:
                first_run = f.read()

            # Run again to same path
            sync_catalog(raw, path)
            with open(f"{path}_ce.json", "r", encoding="utf-8") as f:
                second_run = f.read()

            self.assertEqual(first_run, second_run)


# ---------------------------------------------------------------------------
# GROUP B — Rate Library Sync (4 tests)
# ---------------------------------------------------------------------------

class TestRateSync(unittest.TestCase):

    def test_7_valid_rate_sync_produces_correct_internal_rate_library(self):
        raw = _valid_raw_rates()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rates.json")
            internal = sync_rate_library(raw, path)

            normalized = load_raw_rate_library(raw)
            expected_internal = build_internal_rate_library(normalized)

            self.assertEqual(internal, expected_internal)
            # IDs sorted in expected_internal per ingestion spec
            self.assertEqual(list(internal.keys()), ["R001", "R002"])

    def test_8_invalid_rate_input_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rates.json")
            with self.assertRaises(ValueError):
                sync_rate_library("not-a-list", path)

    def test_9_malformed_rate_record(self):
        raw = [
            {
                "id": "R001",
                "description": "Bad rate",
                # Missing components dict
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rates.json")
            with self.assertRaises(ValueError):
                sync_rate_library(raw, path)

    def test_10_rate_library_saved_deterministically_roundtrip(self):
        raw = _valid_raw_rates()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rates.json")
            internal = sync_rate_library(raw, path)

            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            self.assertEqual(loaded, internal)


# ---------------------------------------------------------------------------
# GROUP C — Combined Sync (4 tests)
# ---------------------------------------------------------------------------

class TestCombinedSync(unittest.TestCase):

    def test_11_sync_all_produces_correct_composite(self):
        raw_cat = _valid_raw_catalog()
        raw_rates = _valid_raw_rates()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "bundle")

            combined = sync_all(raw_cat, raw_rates, base)

            # Compare with isolated runs
            cat_path = f"{base}_catalog.json"
            rate_path = f"{base}_rates.json"

            isolated_cat = sync_catalog(raw_cat, cat_path)
            isolated_rates = sync_rate_library(raw_rates, rate_path)

            self.assertEqual(combined["catalog"], isolated_cat)
            self.assertEqual(combined["rates"], isolated_rates)

    def test_12_deterministic_combined_sync_output(self):
        raw_cat = _valid_raw_catalog()
        raw_rates = _valid_raw_rates()

        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "bundle")

            out1 = sync_all(raw_cat, raw_rates, base)
            out2 = sync_all(raw_cat, raw_rates, base)

            self.assertEqual(out1, out2)

    def test_13_invalid_base_output_path(self):
        raw_cat = _valid_raw_catalog()
        raw_rates = _valid_raw_rates()

        with self.assertRaises(ValueError):
            sync_all(raw_cat, raw_rates, "")

    def test_14_directory_auto_creation(self):
        raw_cat = _valid_raw_catalog()
        raw_rates = _valid_raw_rates()

        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "nested", "deep", "bundle")

            result = sync_all(raw_cat, raw_rates, nested)

            # Check directories and files
            self.assertTrue(os.path.exists(os.path.dirname(nested)))

            cat_path = f"{nested}_catalog.json"
            rate_path = f"{nested}_rates.json"
            ce_path = f"{cat_path}_ce.json"

            self.assertTrue(os.path.exists(cat_path))
            self.assertTrue(os.path.exists(rate_path))
            self.assertTrue(os.path.exists(ce_path))


if __name__ == "__main__":
    unittest.main()
