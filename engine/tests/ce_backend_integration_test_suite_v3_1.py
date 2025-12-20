# C:/Valesco_System/engine/tests/ce_backend_integration_test_suite_v3.1.py
# CE Backend Integration Test Suite v3.1 — Deterministic Adapter Tests
#
# Validates:
#   - Adapter input validation (internal catalog → CE format)
#   - Output schema validation
#   - Deterministic ordering and deduplication
#   - Persistence round-trip correctness
#   - No enrichment / no inference

import unittest
import tempfile
import os
import json
import copy

from engine.modules.catalog_ingestion_v3_0 import (
    load_raw_catalog,
    build_internal_catalog,
)
from engine.modules.catalog_ce_adapter_v3_1 import (
    catalog_to_ce_backend_format,
    validate_ce_backend_catalog,
    export_ce_backend_catalog,
)


class TestCEBackendIntegrationV31(unittest.TestCase):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_sample_internal_catalog(self):
        external = [
            {
                "id": "B002",
                "name": "Product B",
                "category": "core",
                "attributes": {"finish": "primer"},
            },
            {
                "id": "A001",
                "name": "Product A",
                "category": "primary",
                "attributes": {"thickness": "100mm"},
            },
            {
                "id": "C003",
                "name": "Product C",
                "category": "secondary",
                "attributes": {"rating": "standard"},
            },
        ]
        normalized = load_raw_catalog(external)
        return build_internal_catalog(normalized)

    # ------------------------------------------------------------------
    # GROUP A — Input Validation
    # ------------------------------------------------------------------

    def test_1_valid_internal_catalog_to_valid_ce_format(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        # Ensure sorted by id ascending
        ids = [item["id"] for item in ce_list]
        self.assertEqual(ids, sorted(ids))

        # Ensure expected fields and no score_placeholder
        for item in ce_list:
            self.assertEqual(
                set(item.keys()),
                {"id", "name", "category", "attributes"},
            )
            self.assertNotIn("score_placeholder", item)

    def test_2_missing_required_key_in_internal_catalog(self):
        internal_catalog = self._build_sample_internal_catalog()
        # Remove 'name' from one item
        any_id = next(iter(internal_catalog.keys()))
        internal_catalog[any_id] = {
            "id": internal_catalog[any_id]["id"],
            # 'name' missing
            "category": internal_catalog[any_id]["category"],
            "attributes": internal_catalog[any_id]["attributes"],
            "score_placeholder": 0.0,
        }

        with self.assertRaises(ValueError):
            catalog_to_ce_backend_format(internal_catalog)

    def test_3_wrong_type_in_internal_catalog(self):
        internal_catalog = self._build_sample_internal_catalog()
        # attributes not dict
        any_id = next(iter(internal_catalog.keys()))
        broken = copy.deepcopy(internal_catalog)
        broken[any_id]["attributes"] = "not-a-dict"
        with self.assertRaises(ValueError):
            catalog_to_ce_backend_format(broken)

        # id not string
        broken = copy.deepcopy(internal_catalog)
        # Replace key and inner id type
        first_key = next(iter(broken.keys()))
        item = broken.pop(first_key)
        item["id"] = 123  # wrong type
        broken[123] = item  # wrong key type for adapter
        with self.assertRaises(ValueError):
            catalog_to_ce_backend_format(broken)

    # ------------------------------------------------------------------
    # GROUP B — Output Validation (Adapter + Validator)
    # ------------------------------------------------------------------

    def test_4_validate_ce_backend_catalog_accepts_correct_output(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)
        result = validate_ce_backend_catalog(ce_list)
        self.assertTrue(result)

    def test_5_detect_incorrect_keys(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        # Inject an extra key into the first item
        ce_list[0]["extra"] = "illegal"
        with self.assertRaises(ValueError):
            validate_ce_backend_catalog(ce_list)

    def test_6_detect_unsorted_ids(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        # Reverse list to break sort order
        ce_list_unsorted = list(reversed(ce_list))
        with self.assertRaises(ValueError):
            validate_ce_backend_catalog(ce_list_unsorted)

    def test_7_detect_duplicate_ids(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        # Duplicate the first item
        ce_list_dup = ce_list + [copy.deepcopy(ce_list[0])]
        with self.assertRaises(ValueError):
            validate_ce_backend_catalog(ce_list_dup)

    def test_8_detect_non_serializable_attributes(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        # Insert a non-serializable object into attributes
        class Dummy:
            pass

        ce_list_bad = copy.deepcopy(ce_list)
        ce_list_bad[0]["attributes"]["bad"] = Dummy()
        with self.assertRaises(ValueError):
            validate_ce_backend_catalog(ce_list_bad)

    # ------------------------------------------------------------------
    # GROUP C — Round-Trip Stability
    # ------------------------------------------------------------------

    def test_9_export_load_validate_roundtrip(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "ce_catalog.json")
            export_ce_backend_catalog(ce_list, path)

            # Load raw JSON
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

        # Validate loaded data
        self.assertTrue(validate_ce_backend_catalog(loaded))
        # Deep equality with original adapter output
        self.assertEqual(ce_list, loaded)

    def test_10_invalid_file_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad_ce_catalog.json")
            # Write invalid JSON
            with open(path, "w", encoding="utf-8") as f:
                f.write("{invalid json")

            # Loader (json.load) should raise a ValueError-derived exception
            with open(path, "r", encoding="utf-8") as f:
                with self.assertRaises(ValueError):
                    json.load(f)

    # ------------------------------------------------------------------
    # GROUP D — Determinism
    # ------------------------------------------------------------------

    def test_11_deterministic_adaptation(self):
        internal_catalog = self._build_sample_internal_catalog()
        ce_list_1 = catalog_to_ce_backend_format(internal_catalog)
        ce_list_2 = catalog_to_ce_backend_format(internal_catalog)
        self.assertEqual(ce_list_1, ce_list_2)

    def test_12_deterministic_ordering_after_deduplication(self):
        # Use ingestion pipeline to create internal catalog from duplicated + scrambled IDs
        external = [
            {
                "id": "B002",
                "name": "Product B",
                "category": "core",
                "attributes": {"finish": "primer"},
            },
            {
                "id": "A001",
                "name": "Product A (first)",
                "category": "primary",
                "attributes": {"thickness": "100mm"},
            },
            {
                "id": "A001",
                "name": "Product A (duplicate)",
                "category": "primary",
                "attributes": {"thickness": "150mm"},
            },
        ]

        normalized = load_raw_catalog(external)  # first A001 wins, sorted by id
        internal_catalog = build_internal_catalog(normalized)
        ce_list = catalog_to_ce_backend_format(internal_catalog)

        # IDs must be sorted and first A001 retained
        ids = [item["id"] for item in ce_list]
        self.assertEqual(ids, sorted(ids))
        # Expect two unique IDs: A001 and B002
        self.assertEqual(ids, ["A001", "B002"])
        # A001 should correspond to first occurrence
        a_item = ce_list[0]
        self.assertEqual(a_item["name"], "Product A (first)")
        self.assertEqual(a_item["attributes"]["thickness"], "100mm")


if __name__ == "__main__":
    unittest.main()
