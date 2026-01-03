# C:/Valesco_System/engine/tests/test_catalog_ingestion_v3_0.py
# Catalog Ingestion Test Suite v3.0
#
# Validates deterministic normalization, serialization, and error handling.

import os
import tempfile
import unittest

from engine.modules import catalog_ingestion_v3_0 as catalog_ingestion


class TestCatalogIngestionV30(unittest.TestCase):
    def _sample_external_items(self):
        return [
            {
                "id": "B002",
                "name": "Item B",
                "category": "secondary",
                "attributes": {"size": "L"},
            },
            {
                "id": "A001",
                "name": "Item A",
                "category": "primary",
                "attributes": {"size": "S"},
            },
            {
                "id": "A001",
                "name": "Duplicate Item A",
                "category": "primary",
                "attributes": {"size": "XL"},
            },
        ]

    def test_nominal_normalization_is_deterministic(self):
        normalized = catalog_ingestion.load_raw_catalog(self._sample_external_items())

        self.assertEqual([item["id"] for item in normalized], ["A001", "B002"])
        self.assertEqual(normalized[0]["name"], "Item A")
        self.assertEqual(
            list(normalized[0].keys()),
            ["id", "name", "category", "attributes", "score_placeholder"],
        )
        self.assertEqual(normalized[0]["score_placeholder"], 0.0)

    def test_idempotent_normalization_and_catalog(self):
        external_items = self._sample_external_items()
        first = catalog_ingestion.load_raw_catalog(external_items)
        second = catalog_ingestion.load_raw_catalog(external_items)

        self.assertEqual(first, second)

        catalog_first = catalog_ingestion.build_internal_catalog(first)
        catalog_second = catalog_ingestion.build_internal_catalog(second)

        self.assertEqual(catalog_first, catalog_second)

    def test_serialization_is_deterministic(self):
        normalized = catalog_ingestion.load_raw_catalog(self._sample_external_items())
        catalog = catalog_ingestion.build_internal_catalog(normalized)

        with tempfile.TemporaryDirectory() as tmpdir:
            path_one = os.path.join(tmpdir, "catalog_one.json")
            path_two = os.path.join(tmpdir, "catalog_two.json")

            catalog_ingestion.save_internal_catalog(catalog, path_one)
            catalog_ingestion.save_internal_catalog(catalog, path_two)

            with open(path_one, "rb") as first_handle:
                first_bytes = first_handle.read()
            with open(path_two, "rb") as second_handle:
                second_bytes = second_handle.read()

            self.assertEqual(first_bytes, second_bytes)

            loaded = catalog_ingestion.load_internal_catalog(path_one)
            self.assertEqual(loaded, catalog)

    def test_invalid_input_type_raises(self):
        with self.assertRaisesRegex(ValueError, "json_list must be a list"):
            catalog_ingestion.load_raw_catalog("invalid")

    def test_missing_required_key_raises(self):
        bad_input = [
            {"id": "A001", "name": "Item A", "category": "primary"},
        ]
        with self.assertRaisesRegex(ValueError, "Missing required key 'attributes'"):
            catalog_ingestion.load_raw_catalog(bad_input)


if __name__ == "__main__":
    unittest.main()
