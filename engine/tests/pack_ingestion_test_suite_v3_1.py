# C:/Valesco_System/engine/tests/pack_ingestion_test_suite_v3.1.py
# Pack Ingestion Test Suite v3.1
#
# Validates:
#   - External schema correctness
#   - Normalization correctness
#   - Deterministic ordering
#   - Deduplication (first-wins)
#   - Persistence round-trip
#   - CE-safety (no inference, no enrichment)
#
# Required tests: 12

import unittest
import tempfile
import os
import json
import copy

from engine.modules.pack_ingestion_v3_1 import (
    load_raw_packs,
    build_internal_pack_library,
    save_internal_pack_library,
    load_internal_pack_library,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _valid_pack():
    return {
        "id": "PACK001",
        "name": "Basic Timber Wall Pack",
        "items": [
            {"catalog_id": "A001", "multiplier": 1.0},
            {"catalog_id": "A002", "multiplier": 0.4},
        ],
    }


class TestPackIngestionV31(unittest.TestCase):

    # ----------------------------------------------------------------------
    # GROUP A — External Format Validation
    # ----------------------------------------------------------------------

    def test_valid_pack_normalizes_correctly(self):
        raw = [_valid_pack()]
        normalized = load_raw_packs(raw)
        self.assertEqual(len(normalized), 1)
        n0 = normalized[0]
        expected = {
            "id": "PACK001",
            "name": "Basic Timber Wall Pack",
            "items": [
                {"catalog_id": "A001", "multiplier": 1.0},
                {"catalog_id": "A002", "multiplier": 0.4},
            ],
        }
        self.assertEqual(n0, expected)

    def test_missing_keys_raises_value_error(self):
        base = _valid_pack()
        for key in ("id", "name", "items"):
            with self.subTest(key=key):
                bad = copy.deepcopy(base)
                bad.pop(key)
                with self.assertRaises(ValueError):
                    load_raw_packs([bad])

    def test_empty_items_list_raises(self):
        bad = copy.deepcopy(_valid_pack())
        bad["items"] = []
        with self.assertRaises(ValueError):
            load_raw_packs([bad])

    def test_extra_top_level_keys_raises(self):
        bad = copy.deepcopy(_valid_pack())
        bad["extra"] = "not allowed"
        with self.assertRaises(ValueError):
            load_raw_packs([bad])

    def test_invalid_item_schema_raises(self):
        # missing "catalog_id"
        bad1 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"multiplier": 1.0}],
        }
        with self.assertRaises(ValueError):
            load_raw_packs([bad1])

        # missing "multiplier"
        bad2 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"catalog_id": "A001"}],
        }
        with self.assertRaises(ValueError):
            load_raw_packs([bad2])

        # wrong item type
        bad3 = {
            "id": "PACK001",
            "name": "Pack",
            "items": ["not-a-dict"],
        }
        with self.assertRaises(ValueError):
            load_raw_packs([bad3])

    def test_invalid_multiplier_raises(self):
        # non-numeric
        bad1 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"catalog_id": "A001", "multiplier": "abc"}],
        }
        with self.assertRaises(ValueError):
            load_raw_packs([bad1])

        # negative
        bad2 = {
            "id": "PACK001",
            "name": "Pack",
            "items": [{"catalog_id": "A001", "multiplier": -1}],
        }
        with self.assertRaises(ValueError):
            load_raw_packs([bad2])

    # ----------------------------------------------------------------------
    # GROUP B — Normalization & Ordering
    # ----------------------------------------------------------------------

    def test_normalization_preserves_catalog_id_and_casts_multiplier(self):
        raw = [
            {
                "id": "PACK001",
                "name": "Test Pack",
                "items": [
                    {"catalog_id": "A123", "multiplier": 2},
                    {"catalog_id": "A456", "multiplier": 3.7},
                ],
            }
        ]
        normalized = load_raw_packs(raw)
        items = normalized[0]["items"]
        self.assertEqual(items[0]["catalog_id"], "A123")
        self.assertEqual(items[0]["multiplier"], 2.0)
        self.assertEqual(items[1]["catalog_id"], "A456")
        self.assertEqual(items[1]["multiplier"], 3.7)

    def test_deduplication_first_wins(self):
        raw = [
            {
                "id": "PACK001",
                "name": "First Version",
                "items": [{"catalog_id": "A001", "multiplier": 1.0}],
            },
            {
                "id": "PACK001",
                "name": "Second Version",
                "items": [{"catalog_id": "A002", "multiplier": 2.0}],
            },
        ]
        normalized = load_raw_packs(raw)
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]["name"], "First Version")

    def test_sorted_ascending_by_id(self):
        raw = [
            {
                "id": "PACK003",
                "name": "Pack C",
                "items": [{"catalog_id": "A001", "multiplier": 1.0}],
            },
            {
                "id": "PACK001",
                "name": "Pack A",
                "items": [{"catalog_id": "A002", "multiplier": 1.0}],
            },
            {
                "id": "PACK002",
                "name": "Pack B",
                "items": [{"catalog_id": "A003", "multiplier": 1.0}],
            },
        ]
        normalized = load_raw_packs(raw)
        ids = [p["id"] for p in normalized]
        self.assertEqual(ids, ["PACK001", "PACK002", "PACK003"])

    def test_determinism_repeated_runs_identical_output(self):
        raw = [
            {
                "id": "PACK002",
                "name": "Pack B",
                "items": [{"catalog_id": "A001", "multiplier": 1.0}],
            },
            {
                "id": "PACK001",
                "name": "Pack A",
                "items": [{"catalog_id": "A002", "multiplier": 1.0}],
            },
        ]
        out1 = load_raw_packs(raw)
        out2 = load_raw_packs(raw)
        self.assertEqual(out1, out2)

    # ----------------------------------------------------------------------
    # GROUP C — Persistence Layer
    # ----------------------------------------------------------------------

    def test_save_load_validate_deep_equal(self):
        raw = [
            {
                "id": "PACK002",
                "name": "Pack B",
                "items": [{"catalog_id": "A001", "multiplier": 1.0}],
            },
            {
                "id": "PACK001",
                "name": "Pack A",
                "items": [{"catalog_id": "A002", "multiplier": 1.0}],
            },
        ]

        normalized = load_raw_packs(raw)
        library = build_internal_pack_library(normalized)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "packs.json")
            save_internal_pack_library(library, path)

            loaded = load_internal_pack_library(path)
            self.assertEqual(library, loaded)

    def test_invalid_json_or_invalid_schema_on_load_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # invalid JSON
            path = os.path.join(tmpdir, "invalid.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{invalid json")
            with self.assertRaises(ValueError):
                load_internal_pack_library(path)

        with tempfile.TemporaryDirectory() as tmpdir:
            # wrong root type
            path = os.path.join(tmpdir, "wrong.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(["not-a-dict"], f)
            with self.assertRaises(ValueError):
                load_internal_pack_library(path)


if __name__ == "__main__":
    unittest.main()
