# C:/Valesco_System/engine/tests/rate_build_up_test_suite_v3.3.py
# Rate Build-Up Test Suite v3.3
#
# Validates:
#   - Correct arithmetic aggregation
#   - Proper handling of None components
#   - Strict unit-consistency enforcement
#   - Rejection of invalid inputs
#   - Determinism and deep equality
#   - No inference, no enrichment
#
# This suite tests the module:
#     engine.modules.rate_build_up_v3_3
#
# Required tests: 12 (Groups A–D)

import unittest
import copy

from engine.modules.rate_build_up_v3_3 import (
    build_up_rate,
    build_up_library,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_rate_record(material=None, labour=None, plant=None, overhead=None):
    """Utility to generate a normalized rate record quickly."""
    return {
        "id": "R001",
        "description": "desc",
        "components": {
            "material": material,
            "labour": labour,
            "plant": plant,
            "overhead": overhead,
        },
    }


class TestRateBuildUpV33(unittest.TestCase):

    # ----------------------------------------------------------------------
    # GROUP A — Valid Build-Up Cases
    # ----------------------------------------------------------------------

    def test_1_material_only(self):
        rec = _make_rate_record(material={"rate": 4.2, "unit": "m2"})
        out = build_up_rate(rec)
        self.assertEqual(out["total_rate"], 4.2)
        self.assertEqual(out["unit"], "m2")

    def test_2_labour_only(self):
        rec = _make_rate_record(labour={"rate": 6.5, "unit": "m2"})
        out = build_up_rate(rec)
        self.assertEqual(out["total_rate"], 6.5)
        self.assertEqual(out["unit"], "m2")

    def test_3_material_plus_labour_same_unit(self):
        rec = _make_rate_record(
            material={"rate": 4.2, "unit": "m2"},
            labour={"rate": 6.5, "unit": "m2"},
        )
        out = build_up_rate(rec)
        self.assertEqual(out["total_rate"], 10.7)
        self.assertEqual(out["unit"], "m2")

    def test_4_all_components_same_unit(self):
        rec = _make_rate_record(
            material={"rate": 1.0, "unit": "m2"},
            labour={"rate": 2.0, "unit": "m2"},
            plant={"rate": 3.0, "unit": "m2"},
            overhead={"rate": 4.0, "unit": "m2"},
        )
        out = build_up_rate(rec)
        self.assertEqual(out["total_rate"], 10.0)
        self.assertEqual(out["unit"], "m2")

    # ----------------------------------------------------------------------
    # GROUP B — Missing / All-None Conditions
    # ----------------------------------------------------------------------

    def test_5_all_components_none(self):
        rec = _make_rate_record()
        out = build_up_rate(rec)
        self.assertIsNone(out["total_rate"])
        self.assertIsNone(out["unit"])

    def test_6_mixed_some_none(self):
        rec = _make_rate_record(
            material={"rate": 4.0, "unit": "m2"},
            plant=None,
            labour=None,
            overhead=None,
        )
        out = build_up_rate(rec)
        self.assertEqual(out["total_rate"], 4.0)
        self.assertEqual(out["unit"], "m2")

    # ----------------------------------------------------------------------
    # GROUP C — Invalid Inputs
    # ----------------------------------------------------------------------

    def test_7_negative_rate(self):
        rec = _make_rate_record(material={"rate": -1.0, "unit": "m2"})
        with self.assertRaises(ValueError):
            build_up_rate(rec)

    def test_8_non_numeric_rate(self):
        rec = _make_rate_record(material={"rate": "abc", "unit": "m2"})
        with self.assertRaises(ValueError):
            build_up_rate(rec)

    def test_9_invalid_unit(self):
        # empty string unit
        rec = _make_rate_record(material={"rate": 4.0, "unit": ""})
        with self.assertRaises(ValueError):
            build_up_rate(rec)

        # wrong type
        rec = _make_rate_record(material={"rate": 4.0, "unit": 123})
        with self.assertRaises(ValueError):
            build_up_rate(rec)

    def test_10_mismatched_units(self):
        rec = _make_rate_record(
            material={"rate": 4.0, "unit": "m2"},
            labour={"rate": 6.0, "unit": "m"},
        )
        with self.assertRaises(ValueError):
            build_up_rate(rec)

    # ----------------------------------------------------------------------
    # GROUP D — Determinism & Integrity
    # ----------------------------------------------------------------------

    def test_11_determinism_for_same_record(self):
        rec = _make_rate_record(
            material={"rate": 4.2, "unit": "m2"},
            labour={"rate": 6.5, "unit": "m2"},
        )
        out1 = build_up_rate(rec)
        out2 = build_up_rate(rec)
        self.assertEqual(out1, out2)

        # Ensure deep-copy behaviour: modifying out1 must not affect out2
        out1["components"]["material"]["rate"] = 999
        self.assertNotEqual(out1["components"]["material"]["rate"],
                            out2["components"]["material"]["rate"])

    def test_12_library_build_up_determinism(self):
        # Library with scrambled ID order
        library = {
            "R003": _make_rate_record(material={"rate": 3.0, "unit": "m2"}),
            "R001": _make_rate_record(material={"rate": 1.0, "unit": "m2"}),
            "R002": _make_rate_record(material={"rate": 2.0, "unit": "m2"}),
        }

        out1 = build_up_library(library)
        out2 = build_up_library(library)

        self.assertEqual(out1, out2)
        # IDs must appear sorted in output
        self.assertEqual(list(out1.keys()), ["R001", "R002", "R003"])


if __name__ == "__main__":
    unittest.main()
