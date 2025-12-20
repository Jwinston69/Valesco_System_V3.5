# C:/Valesco_System/engine/tests/catalog_ingestion_test_suite_v3.0.py
# Catalog Ingestion Test Suite v3.0 — Deterministic Automated Tests
#
# Validates:
#   - External schema validation
#   - Normalization behaviour
#   - Deduplication and ordering
#   - Internal catalog construction
#   - Persistence round-trips
#   - No inference / no enrichment guarantees

import unittest
import tempfile
import os
import json
import copy

from engine.modules.catalog_ingestion_v3_0 import (
    load_raw_catalog,
    build_internal_catalog,
    save_internal_catalog,
    load_internal_catalog,
)


class TestCatalogIngestionV30(unittest.TestCase):

    # ------------------------------------------------------------------
    # GROUP A — External Schema Validation
    # ------------------------------------------------------------------

    def test_1_valid_external_item_normalized_correctly(self):
        external = [
            {
                "id": "A001",
                "name": "Product Name",
                "category": "core",
                "attributes": {
                    "thickness": "100mm",
                    "finish": "galvanised",
                    "rating": "standard",
                },
            }
        ]

        normalized_list = load_raw_catalog(external)
        self.assertEqual(len(normalized_list), 1)
        item = normalized_list[0]

        expected = {
            "id": "A001",
            "name": "Product Name",
            "category": "core",
            "attributes": {
                "thickness": "100mm",
                "finish": "galvanised",
                "rating": "standard",
            },
            "score_placeholder": 0.0,
        }

        self.assertEqual(item, expected)

    def test_2_missing_required_field(self):
        base_item = {
            "id": "A001",
            "name": "Product Name",
            "category": "core",
            "attributes": {},
        }

        for missing in ("id", "name", "category", "attributes"):
            with self.subTest(missing=missing):
                item = copy.deepcopy(base_item)
                item.pop(missing)
                with self.assertRaises(ValueError):
                    load_raw_catalog([item])

    def test_3_wrong_types(self):
        # id not string
        bad_id = {
            "id": 123,
            "name": "Product Name",
            "category": "core",
            "attributes": {},
        }
        with self.assertRaises(ValueError):
            load_raw_catalog([bad_id])

        # attributes not dict
        bad_attr = {
            "id": "A001",
            "name": "Product Name",
            "category": "core",
            "attributes": "not-a-dict",
        }
        with self.assertRaises(ValueError):
            load_raw_catalog([bad_attr])

    # ------------------------------------------------------------------
    # GROUP B — Deduplication & Ordering
    # ------------------------------------------------------------------

    def test_4_duplicate_ids_first_wins(self):
        external = [
            {
                "id": "A001",
                "name": "First Product",
                "category": "core",
                "attributes": {"thickness": "100mm"},
            },
            {
                "id": "A001",
                "name": "Second Product",
                "category": "core",
                "attributes": {"thickness": "150mm"},
            },
        ]

        normalized_list = load_raw_catalog(external)
        self.assertEqual(len(normalized_list), 1)
        item = normalized_list[0]
        self.assertEqual(item["id"], "A001")
        self.assertEqual(item["name"], "First Product")
        self.assertEqual(item["attributes"], {"thickness": "100mm"})

    def test_5_sorted_ascending_by_id(self):
        external = [
            {
                "id": "C003",
                "name": "Product C",
                "category": "core",
                "attributes": {},
            },
            {
                "id": "A001",
                "name": "Product A",
                "category": "core",
                "attributes": {},
            },
            {
                "id": "B002",
                "name": "Product B",
                "category": "core",
                "attributes": {},
            },
        ]

        normalized_list = load_raw_catalog(external)
        ids = [item["id"] for item in normalized_list]
        self.assertEqual(ids, ["A001", "B002", "C003"])

    def test_6_determinism_of_sorting(self):
        external = [
            {
                "id": "B002",
                "name": "Product B",
                "category": "core",
                "attributes": {},
            },
            {
                "id": "A001",
                "name": "Product A",
                "category": "core",
                "attributes": {},
            },
        ]

        r1 = load_raw_catalog(external)
        r2 = load_raw_catalog(external)
        self.assertEqual(r1, r2)

    # ------------------------------------------------------------------
    # GROUP C — Internal Catalog Construction
    # ------------------------------------------------------------------

    def test_7_build_internal_catalog(self):
        normalized_list = [
            {
                "id": "A001",
                "name": "Product A",
                "category": "core",
                "attributes": {},
                "score_placeholder": 0.0,
            },
            {
                "id": "B002",
                "name": "Product B",
                "category": "alt",
                "attributes": {"finish": "primer"},
                "score_placeholder": 0.0,
            },
        ]

        catalog = build_internal_catalog(normalized_list)
        self.assertEqual(set(catalog.keys()), {"A001", "B002"})
        self.assertEqual(catalog["A001"], normalized_list[0])
        self.assertEqual(catalog["B002"], normalized_list[1])

    def test_8_duplicate_ids_in_normalized_input(self):
        normalized_list = [
            {
                "id": "A001",
                "name": "Product A1",
                "category": "core",
                "attributes": {},
                "score_placeholder": 0.0,
            },
            {
                "id": "A001",
                "name": "Product A2",
                "category": "core",
                "attributes": {},
                "score_placeholder": 0.0,
            },
        ]

        with self.assertRaises(ValueError):
            build_internal_catalog(normalized_list)

    # ------------------------------------------------------------------
    # GROUP D — Persistence Layer
    # ------------------------------------------------------------------

    def test_9_save_and_load_internal_catalog_roundtrip(self):
        normalized_list = [
            {
                "id": "A001",
                "name": "Product A",
                "category": "core",
                "attributes": {"thickness": "100mm"},
                "score_placeholder": 0.0,
            },
            {
                "id": "B002",
                "name": "Product B",
                "category": "alt",
                "attributes": {"finish": "galvanised"},
                "score_placeholder": 0.0,
            },
        ]
        catalog = build_internal_catalog(normalized_list)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog.json")
            save_internal_catalog(catalog, path)
            loaded = load_internal_catalog(path)

        self.assertEqual(catalog, loaded)

    def test_10_invalid_file_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "catalog_invalid.json")
            # Write a list instead of a dict
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

            with self.assertRaises(ValueError):
                load_internal_catalog(path)

    # ------------------------------------------------------------------
    # GROUP E — No Inference / No Enrichment
    # ------------------------------------------------------------------

    def test_11_attributes_unchanged(self):
        attrs = {
            "thickness": "100mm",
            "finish": "galvanised",
            "rating": "standard",
            "nested": {"k": "v"},
        }
        external = [
            {
                "id": "A001",
                "name": "Product A",
                "category": "core",
                "attributes": copy.deepcopy(attrs),
            }
        ]

        normalized_list = load_raw_catalog(external)
        item = normalized_list[0]
        self.assertEqual(item["attributes"], attrs)

    def test_12_no_extra_fields_added(self):
        external = [
            {
                "id": "A001",
                "name": "Product A",
                "category": "core",
                "attributes": {},
            }
        ]

        normalized_list = load_raw_catalog(external)
        item = normalized_list[0]
        self.assertEqual(
            set(item.keys()),
            {"id", "name", "category", "attributes", "score_placeholder"},
        )


if __name__ == "__main__":
    unittest.main()
