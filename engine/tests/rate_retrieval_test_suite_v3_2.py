# C:/Valesco_System/engine/tests/rate_retrieval_test_suite_v3.2.py
# Rate Retrieval Test Suite v3.2 — Deterministic, Read-Only Verification
#
# Validates:
#   - Loading & schema correctness
#   - Safe record retrieval
#   - Deterministic sorted listing
#   - No mutation, no inference, no enrichment
#   - Stable deterministic behaviour across runs

import unittest
import tempfile
import os
import json
import copy

from engine.modules.rate_library_ingestion_v3_1 import (
    load_raw_rate_library,
    build_internal_rate_library,
    save_internal_rate_library,
)
from engine.modules.rate_retrieval_v3_2 import (
    load_rate_library,
    get_rate_record,
    list_rate_records,
)


class TestRateRetrievalV32(unittest.TestCase):

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------
    def _create_temp_library_file(self, records):
        """
        Utility: take raw external rate records, normalize & build internal
        library, then save to temp file. Returns path.
        """
        normalized = load_raw_rate_library(records)
        library = build_internal_rate_library(normalized)

        tmpdir = tempfile.TemporaryDirectory()
        path = os.path.join(tmpdir.name, "rates.json")
        save_internal_rate_library(library, path)

        # return both temp directory and path so directory stays alive
        return tmpdir, path, library

    # ----------------------------------------------------------------------
    # GROUP A — Loading & Schema Validation
    # ----------------------------------------------------------------------

    def test_1_valid_rate_library_loads_correctly(self):
        external = [
            {
                "id": "R002",
                "description": "Example rate 2",
                "components": {
                    "material": {"rate": 4.2, "unit": "m2"},
                    "labour": {"rate": 6.5, "unit": "m2"},
                },
            },
            {
                "id": "R001",
                "description": "Example rate 1",
                "components": {
                    "material": {"rate": 3.1, "unit": "m2"},
                },
            },
        ]

        tmpdir, path, internal_library = self._create_temp_library_file(external)
        loaded = load_rate_library(path)

        # Structure must match ingestion output exactly
        self.assertEqual(loaded, internal_library)

        tmpdir.cleanup()

    def test_2_missing_required_keys(self):
        # Remove "description"
        bad_library = {
            "R001": {
                "id": "R001",
                "components": {"material": {"rate": 1.0, "unit": "m2"},
                               "labour": None, "plant": None, "overhead": None}
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(bad_library, f)

            with self.assertRaises(ValueError):
                load_rate_library(path)

        # Remove "components"
        bad_library = {
            "R001": {
                "id": "R001",
                "description": "desc",
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad2.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(bad_library, f)

            with self.assertRaises(ValueError):
                load_rate_library(path)

    def test_3_incorrect_types(self):
        # components not a dict
        bad_library = {
            "R001": {
                "id": "R001",
                "description": "desc",
                "components": "not-a-dict",
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad3.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(bad_library, f)
            with self.assertRaises(ValueError):
                load_rate_library(path)

        # components missing required component keys
        bad_library = {
            "R001": {
                "id": "R001",
                "description": "desc",
                "components": {"material": {"rate": 1.0, "unit": "m2"}}
                # Missing labour, plant, overhead
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad4.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(bad_library, f)
            with self.assertRaises(ValueError):
                load_rate_library(path)

    # ----------------------------------------------------------------------
    # GROUP B — Record Retrieval
    # ----------------------------------------------------------------------

    def test_4_retrieve_existing_id_deep_copy(self):
        external = [
            {
                "id": "R001",
                "description": "desc",
                "components": {"material": {"rate": 1.0, "unit": "m2"}},
            }
        ]

        tmpdir, path, internal_library = self._create_temp_library_file(external)
        loaded = load_rate_library(path)

        record = get_rate_record(loaded, "R001")
        self.assertIsNotNone(record)

        # mutate returned record
        record["description"] = "changed"
        record["components"]["material"]["rate"] = 999

        # original must remain unchanged
        self.assertNotEqual(record["description"], loaded["R001"]["description"])
        self.assertNotEqual(record["components"]["material"]["rate"],
                            loaded["R001"]["components"]["material"]["rate"])

        tmpdir.cleanup()

    def test_5_retrieve_missing_id_none(self):
        external = [
            {
                "id": "R001",
                "description": "desc",
                "components": {"material": {"rate": 1.0, "unit": "m2"}},
            }
        ]
        tmpdir, path, _ = self._create_temp_library_file(external)
        loaded = load_rate_library(path)

        self.assertIsNone(get_rate_record(loaded, "R999"))
        tmpdir.cleanup()

    # ----------------------------------------------------------------------
    # GROUP C — Listing Records
    # ----------------------------------------------------------------------

    def test_6_sorted_record_list(self):
        external = [
            {
                "id": "R003",
                "description": "Third",
                "components": {},
            },
            {
                "id": "R001",
                "description": "First",
                "components": {},
            },
            {
                "id": "R002",
                "description": "Second",
                "components": {},
            },
        ]

        tmpdir, path, _ = self._create_temp_library_file(external)
        loaded = load_rate_library(path)

        lst = list_rate_records(loaded)
        ids = [rec["id"] for rec in lst]
        self.assertEqual(ids, ["R001", "R002", "R003"])

        tmpdir.cleanup()

    def test_7_list_returns_deep_copies(self):
        external = [
            {
                "id": "R001",
                "description": "desc",
                "components": {"material": {"rate": 1.0, "unit": "m2"}},
            }
        ]

        tmpdir, path, internal_library = self._create_temp_library_file(external)
        loaded = load_rate_library(path)

        record_list = list_rate_records(loaded)
        self.assertEqual(len(record_list), 1)

        # mutate returned row
        record_list[0]["description"] = "changed"
        record_list[0]["components"]["material"]["rate"] = 999

        # ensure no mutation occurred to internal library
        self.assertNotEqual(record_list[0]["description"],
                            loaded["R001"]["description"])
        self.assertNotEqual(record_list[0]["components"]["material"]["rate"],
                            loaded["R001"]["components"]["material"]["rate"])

        tmpdir.cleanup()

    # ----------------------------------------------------------------------
    # GROUP D — Determinism
    # ----------------------------------------------------------------------

    def test_8_deterministic_ordering(self):
        external = [
            {
                "id": "R002",
                "description": "Rate 2",
                "components": {},
            },
            {
                "id": "R001",
                "description": "Rate 1",
                "components": {},
            },
        ]

        tmpdir, path, _ = self._create_temp_library_file(external)

        loaded1 = load_rate_library(path)
        loaded2 = load_rate_library(path)

        lst1 = list_rate_records(loaded1)
        lst2 = list_rate_records(loaded2)

        self.assertEqual(lst1, lst2)
        tmpdir.cleanup()

    def test_9_deterministic_retrieval(self):
        external = [
            {
                "id": "R001",
                "description": "desc",
                "components": {},
            }
        ]

        tmpdir, path, _ = self._create_temp_library_file(external)
        loaded = load_rate_library(path)

        rec1 = get_rate_record(loaded, "R001")
        rec2 = get_rate_record(loaded, "R001")

        self.assertEqual(rec1, rec2)
        # ensure they are not the same object (deep copy requirement)
        self.assertIsNot(rec1, rec2)

        tmpdir.cleanup()

    # ----------------------------------------------------------------------
    # GROUP E — Error Handling
    # ----------------------------------------------------------------------

    def test_10_invalid_library_structure(self):
        # Test non-dict root
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(["not", "a", "dict"], f)
            with self.assertRaises(ValueError):
                load_rate_library(path)

        # Test corrupt JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "corrupt.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{invalid json")
            with self.assertRaises(ValueError):
                # json.load triggers ValueError or JSONDecodeError (subclass)
                load_rate_library(path)


if __name__ == "__main__":
    unittest.main()
