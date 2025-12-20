# C:/Valesco_System/engine/tests/rate_library_test_suite_v3.1.py
# Rate Library Test Suite v3.1 — Deterministic Ingestion Validation
#
# Validates:
#   - External rate schema and normalization
#   - Deduplication and deterministic ordering
#   - Internal library construction
#   - Persistence round-trip
#   - No inference or enrichment

import unittest
import tempfile
import os
import json
import copy

from engine.modules.rate_library_ingestion_v3_1 import (
    load_raw_rate_library,
    build_internal_rate_library,
    save_internal_rate_library,
    load_internal_rate_library,
)


class TestRateLibraryIngestionV31(unittest.TestCase):

    # ------------------------------------------------------------------
    # GROUP A — External Schema Validation
    # ------------------------------------------------------------------

    def test_1_valid_external_rate_record_normalization(self):
        external = [
            {
                "id": "R001",
                "description": "100mm insulation labour rate",
                "components": {
                    "material": {"rate": 4.20, "unit": "m2"},
                    "labour": {"rate": 6.50, "unit": "m2"},
                },
            }
        ]

        normalized_list = load_raw_rate_library(external)
        self.assertEqual(len(normalized_list), 1)
        rec = normalized_list[0]

        expected = {
            "id": "R001",
            "description": "100mm insulation labour rate",
            "components": {
                "material": {"rate": 4.20, "unit": "m2"},
                "labour": {"rate": 6.50, "unit": "m2"},
                "plant": None,
                "overhead": None,
            },
        }

        self.assertEqual(rec, expected)

    def test_2_missing_required_keys(self):
        base = {
            "id": "R001",
            "description": "Test rate",
            "components": {},
        }

        for missing in ("description", "components"):
            with self.subTest(missing=missing):
                broken = copy.deepcopy(base)
                broken.pop(missing)
                with self.assertRaises(ValueError):
                    load_raw_rate_library([broken])

    def test_3_wrong_component_type(self):
        # components not dict
        external_bad_components = [
            {
                "id": "R001",
                "description": "Bad components type",
                "components": "not-a-dict",
            }
        ]
        with self.assertRaises(ValueError):
            load_raw_rate_library(external_bad_components)

        # component entry missing rate
        external_missing_rate = [
            {
                "id": "R002",
                "description": "Missing rate",
                "components": {
                    "material": {"unit": "m2"},
                },
            }
        ]
        with self.assertRaises(ValueError):
            load_raw_rate_library(external_missing_rate)

        # component entry missing unit
        external_missing_unit = [
            {
                "id": "R003",
                "description": "Missing unit",
                "components": {
                    "material": {"rate": 4.2},
                },
            }
        ]
        with self.assertRaises(ValueError):
            load_raw_rate_library(external_missing_unit)

        # non-numeric rate
        external_non_numeric_rate = [
            {
                "id": "R004",
                "description": "Non-numeric rate",
                "components": {
                    "material": {"rate": "4.2", "unit": "m2"},
                },
            }
        ]
        with self.assertRaises(ValueError):
            load_raw_rate_library(external_non_numeric_rate)

    def test_4_unsupported_component_name(self):
        external = [
            {
                "id": "R005",
                "description": "Unsupported component",
                "components": {
                    "special": {"rate": 1.0, "unit": "m2"},
                },
            }
        ]
        with self.assertRaises(ValueError):
            load_raw_rate_library(external)

    # ------------------------------------------------------------------
    # GROUP B — Deduplication & Ordering
    # ------------------------------------------------------------------

    def test_5_duplicate_ids_first_wins(self):
        external = [
            {
                "id": "R001",
                "description": "First version",
                "components": {
                    "material": {"rate": 4.0, "unit": "m2"},
                },
            },
            {
                "id": "R001",
                "description": "Second version",
                "components": {
                    "material": {"rate": 9.9, "unit": "m2"},
                },
            },
        ]

        normalized_list = load_raw_rate_library(external)
        self.assertEqual(len(normalized_list), 1)
        rec = normalized_list[0]
        self.assertEqual(rec["id"], "R001")
        self.assertEqual(rec["description"], "First version")
        self.assertEqual(rec["components"]["material"]["rate"], 4.0)

    def test_6_sorted_ascending_by_id(self):
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

        normalized_list = load_raw_rate_library(external)
        ids = [r["id"] for r in normalized_list]
        self.assertEqual(ids, ["R001", "R002", "R003"])

    def test_7_determinism_across_repeated_runs(self):
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

        r1 = load_raw_rate_library(external)
        r2 = load_raw_rate_library(external)
        self.assertEqual(r1, r2)

    # ------------------------------------------------------------------
    # GROUP C — Internal Library Construction
    # ------------------------------------------------------------------

    def test_8_build_internal_library_keyed_by_id(self):
        external = [
            {
                "id": "R001",
                "description": "Material only",
                "components": {
                    "material": {"rate": 3.1, "unit": "m2"},
                },
            },
            {
                "id": "R002",
                "description": "Material + labour",
                "components": {
                    "material": {"rate": 4.2, "unit": "m2"},
                    "labour": {"rate": 6.5, "unit": "m2"},
                },
            },
        ]

        normalized_list = load_raw_rate_library(external)
        library = build_internal_rate_library(normalized_list)

        self.assertEqual(set(library.keys()), {"R001", "R002"})
        self.assertEqual(library["R001"], normalized_list[0])
        self.assertEqual(library["R002"], normalized_list[1])

    def test_9_duplicate_ids_in_normalized_input(self):
        normalized_list = [
            {
                "id": "R001",
                "description": "First",
                "components": {
                    "material": {"rate": 1.0, "unit": "m2"},
                    "labour": None,
                    "plant": None,
                    "overhead": None,
                },
            },
            {
                "id": "R001",
                "description": "Duplicate",
                "components": {
                    "material": {"rate": 2.0, "unit": "m2"},
                    "labour": None,
                    "plant": None,
                    "overhead": None,
                },
            },
        ]

        with self.assertRaises(ValueError):
            build_internal_rate_library(normalized_list)

    # ------------------------------------------------------------------
    # GROUP D — Persistence Layer
    # ------------------------------------------------------------------

    def test_10_save_load_validate_roundtrip(self):
        external = [
            {
                "id": "R001",
                "description": "Material + labour",
                "components": {
                    "material": {"rate": 4.2, "unit": "m2"},
                    "labour": {"rate": 6.5, "unit": "m2"},
                },
            },
            {
                "id": "R002",
                "description": "Material only",
                "components": {
                    "material": {"rate": 3.1, "unit": "m2"},
                },
            },
        ]

        normalized_list = load_raw_rate_library(external)
        library = build_internal_rate_library(normalized_list)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rate_library.json")
            save_internal_rate_library(library, path)
            loaded = load_internal_rate_library(path)

        self.assertEqual(library, loaded)

    def test_11_invalid_json_content_on_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "corrupt.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{invalid json")

            with self.assertRaises(ValueError):
                load_internal_rate_library(path)

    # ------------------------------------------------------------------
    # GROUP E — No Enrichment / No Inference
    # ------------------------------------------------------------------

    def test_12_no_extra_fields_no_inferred_values(self):
        external = [
            {
                "id": "R001",
                "description": "Material + labour",
                "components": {
                    "material": {"rate": 4.2, "unit": "m2"},
                    "labour": {"rate": 6.5, "unit": "m2"},
                },
            }
        ]

        normalized_list = load_raw_rate_library(external)
        self.assertEqual(len(normalized_list), 1)
        rec = normalized_list[0]

        # Only three top-level keys
        self.assertEqual(set(rec.keys()), {"id", "description", "components"})

        comps = rec["components"]
        # Component matrix must contain all four keys
        self.assertEqual(
            set(comps.keys()),
            {"material", "labour", "plant", "overhead"},
        )

        # Provided components preserved exactly, no extra fields
        self.assertEqual(comps["material"], {"rate": 4.2, "unit": "m2"})
        self.assertEqual(comps["labour"], {"rate": 6.5, "unit": "m2"})

        # Missing components must be None (no inferred values)
        self.assertIsNone(comps["plant"])
        self.assertIsNone(comps["overhead"])

        # No calculated or inferred fields like total_rate, etc.
        for comp_name in ("material", "labour"):
            self.assertEqual(set(comps[comp_name].keys()), {"rate", "unit"})


if __name__ == "__main__":
    unittest.main()
