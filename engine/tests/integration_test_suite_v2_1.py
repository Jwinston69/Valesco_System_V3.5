# C:/Valesco_System/engine/tests/integration_test_suite_v2.1.py
# Integration Test Battery v2.1 — Automated Functional Tests
#
# Fully automated, deterministic integration tests for the MVP pipeline:
# User → CE Retrieval → Router → Architect → Validator → Estimator Runtime
# → Merge Agent → Material Manager

import io
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import Callable, Iterator, Optional

from engine.scripts.mvp_runner_v2_1 import run_mvp_case_programmatic
from engine.modules.material_manager_v2_1 import get_metadata
from engine.scripts.ready_gate_v3_5 import (
    READY_SUMMARY_LINE,
    assert_ready_or_exit,
    evaluate_ready,
)

# Additional runtime imports for targeted assertions (no new logic)
from engine.modules.ce_retrieval_layer_v2_1 import retrieve as retrieve_signals
from engine.modules.router_v2_1 import route


def _write_ce_backend_stub(path: Path) -> None:
    stub = textwrap.dedent(
        """
        import json
        import sys

        MOCK_ITEMS = {
            "clean_match": [
                {"id": "A001", "name": "Single Clean-Match Item", "category": "core", "score": 0.98}
            ],
            "ambiguous": [
                {"id": "B001", "name": "Ambiguous Item 1", "category": "core", "score": 0.72},
                {"id": "B002", "name": "Ambiguous Item 2", "category": "core", "score": 0.71},
                {"id": "B003", "name": "Ambiguous Item 3", "category": "core", "score": 0.70},
            ],
            "insufficient": [
                {"id": "C001", "name": "Weak Coverage Item", "category": "misc", "score": 0.40}
            ],
            "compatible": [
                {"id": "E001", "name": "Compatible Item 1", "category": "alt", "score": 0.65},
                {"id": "E002", "name": "Compatible Item 2", "category": "alt", "score": 0.63},
            ],
            "empty": [],
        }

        PROFILE_MAP = {
            "clean": "clean_match",
            "exact": "clean_match",
            "single": "clean_match",
            "ambiguous": "ambiguous",
            "three": "ambiguous",
            "close": "ambiguous",
            "insufficient": "insufficient",
            "unclear": "insufficient",
            "weak": "insufficient",
            "none": "empty",
            "missing": "empty",
            "nomatch": "empty",
            "compatible": "compatible",
            "alternative": "compatible",
            "alt": "compatible",
        }

        def _select_profile(description: str) -> str:
            text = description.lower()
            for key, profile in PROFILE_MAP.items():
                if key in text:
                    return profile
            return "ambiguous"

        def _build_signals(profile, items):
            hit_count = len(items)
            if hit_count == 0:
                return {
                    "hit_count": 0,
                    "top_score": None,
                    "score_gap_to_next": None,
                    "coverage_flags": {"none": True, "weak": False, "strong": False},
                    "retrieved_items": [],
                }

            ordered = sorted(items, key=lambda x: x["score"], reverse=True)
            top_score = ordered[0]["score"]
            score_gap = None
            if hit_count > 1:
                score_gap = top_score - ordered[1]["score"]

            if profile == "clean_match":
                coverage = {"strong": True, "weak": False, "conflicting": False}
            elif profile == "ambiguous":
                coverage = {"strong": True, "weak": False, "conflicting": False}
            elif profile == "insufficient":
                coverage = {"strong": False, "weak": True, "conflicting": False}
            elif profile == "compatible":
                coverage = {"strong": True, "compatible": True}
            else:
                coverage = {"weak": True}

            return {
                "hit_count": hit_count,
                "top_score": top_score,
                "score_gap_to_next": score_gap,
                "coverage_flags": coverage,
                "retrieved_items": ordered,
            }

        def main():
            payload = json.load(sys.stdin)
            description = payload.get("description", "")
            profile = _select_profile(description)
            items = MOCK_ITEMS.get(profile, [])
            output = _build_signals(profile, list(items))
            json.dump(output, sys.stdout)

        if __name__ == "__main__":
            main()
        """
    ).lstrip()
    path.write_text(stub, encoding="utf-8")


class TestValescoMVPIntegration(unittest.TestCase):
    """End-to-end integration tests for Valesco MVP v2.1."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._backend_tmp = tempfile.TemporaryDirectory()
        cls._backend_script = Path(cls._backend_tmp.name) / "ce_backend_stub.py"
        _write_ce_backend_stub(cls._backend_script)
        cls._prev_backend_cmd = os.environ.get("VALESCO_CE_BACKEND_CMD")
        cls._prev_backend_script = os.environ.get("VALESCO_CE_BACKEND_SCRIPT")
        os.environ["VALESCO_CE_BACKEND_SCRIPT"] = str(cls._backend_script)
        if "VALESCO_CE_BACKEND_CMD" in os.environ:
            del os.environ["VALESCO_CE_BACKEND_CMD"]

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._prev_backend_cmd is None:
            os.environ.pop("VALESCO_CE_BACKEND_CMD", None)
        else:
            os.environ["VALESCO_CE_BACKEND_CMD"] = cls._prev_backend_cmd
        if cls._prev_backend_script is None:
            os.environ.pop("VALESCO_CE_BACKEND_SCRIPT", None)
        else:
            os.environ["VALESCO_CE_BACKEND_SCRIPT"] = cls._prev_backend_script
        cls._backend_tmp.cleanup()

    # ------------------------------------------------------------------
    # Helper: determinism check
    # ------------------------------------------------------------------
    def _assert_deterministic_snapshot(self, description, user_responses):
        snap1 = run_mvp_case_programmatic(description, user_responses)
        snap2 = run_mvp_case_programmatic(description, user_responses)
        self.assertEqual(snap1, snap2)
        return snap1

    def _get_single_item(self, snapshot):
        items = snapshot.get("items", [])
        self.assertEqual(len(items), 1)
        return items[0]

    # ------------------------------------------------------------------
    # Test 1 — Clean Match (State A)
    # ------------------------------------------------------------------
    def test_clean_match_state_a(self):
        description = "clean item description"
        user_responses = ["yes"]

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        self.assertEqual(line["item_id"], "A001")
        self.assertEqual(line["status"], "confirmed")

    # ------------------------------------------------------------------
    # Test 2 — Ambiguous Top-3 (State B)
    # ------------------------------------------------------------------
    def test_ambiguous_state_b(self):
        description = "ambiguous item requiring choice"
        user_responses = ["2"]  # select second item

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        # Ambiguous profile is B001/B002/B003; index 2 → B002
        self.assertEqual(line["item_id"], "B002")

    # ------------------------------------------------------------------
    # Test 3 — Clarification Flow (State C → A)
    # ------------------------------------------------------------------
    def test_clarification_flow_c_to_a(self):
        # Initial description triggers insufficient context (State C)
        # Clarification text includes "clean" to drive next pass to State A.
        description = "insufficient description"
        user_responses = ["clean", "yes"]

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        self.assertEqual(line["item_id"], "A001")

    # ------------------------------------------------------------------
    # Test 4 — Clarification Flow (State C → E)
    # ------------------------------------------------------------------
    def test_clarification_flow_c_to_e(self):
        # Verify that the CE/Router combination can realise a conceptual
        # C → E path: an initially insufficient description followed by
        # a compatible/alternative-focused description.
        initial_desc = "insufficient description"
        ce_initial = retrieve_signals(initial_desc)
        router_initial = route(ce_initial)
        self.assertEqual(router_initial["state_id"], "C")

        clarified_desc = "compatible alternative option"
        ce_clarified = retrieve_signals(clarified_desc)
        router_clarified = route(ce_clarified)
        self.assertEqual(router_clarified["state_id"], "E")

        # End-to-end: selection of a compatible alternative via harness
        description = "compatible alternative option"
        user_responses = ["1"]  # select first compatible alternative
        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        self.assertIn(line["item_id"], {"E001", "E002"})

    # ------------------------------------------------------------------
    # Test 5 — Clarification Flow (State C → B)
    # ------------------------------------------------------------------
    def test_clarification_flow_c_to_b(self):
        # Start at State C, then clarification drives to ambiguous State B.
        description = "insufficient description"
        # Clarifier includes "ambiguous" keyword to switch profile on second run.
        user_responses = ["ambiguous", "2"]

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        self.assertEqual(line["item_id"], "B002")

    # ------------------------------------------------------------------
    # Test 6 — No Match (State D → provisional)
    # ------------------------------------------------------------------
    def test_no_match_state_d_to_provisional(self):
        description = "no match none"
        user_responses = ["provisional"]

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "provisional")
        self.assertIsNone(line["item_id"])
        self.assertEqual(line["status"], "confirmed")

    # ------------------------------------------------------------------
    # Test 7 — Revised Description (State D → CE success)
    # ------------------------------------------------------------------
    def test_revised_description_d_to_success(self):
        description = "no match none"
        # First pass: D (no match); revision: clean item; then confirm.
        user_responses = ["clean item description", "yes"]

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        self.assertEqual(line["item_id"], "A001")

    # ------------------------------------------------------------------
    # Test 8 — Compatible Alternatives (State E)
    # ------------------------------------------------------------------
    def test_compatible_alternatives_state_e(self):
        description = "compatible alternative option"
        user_responses = ["1"]  # choose first alternative

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)

        self.assertEqual(line["source"], "catalog")
        self.assertEqual(line["item_id"], "E001")

    # ------------------------------------------------------------------
    # Test 9 — Invalid Selection Handling
    # ------------------------------------------------------------------
    def test_invalid_selection_handling(self):
        # User provides an invalid selection; system must not merge any catalog item.
        description = "ambiguous item requiring choice"
        user_responses = ["99"]  # invalid index

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        items = snapshot.get("items", [])
        self.assertEqual(len(items), 0)

    # ------------------------------------------------------------------
    # Test 10 — Metadata Retrieval Integrity
    # ------------------------------------------------------------------
    def test_metadata_retrieval_integrity(self):
        # Drive a clean-match selection to ensure catalog item A001 is in play.
        description = "clean item description"
        user_responses = ["yes"]

        snapshot = self._assert_deterministic_snapshot(description, user_responses)
        line = self._get_single_item(snapshot)
        self.assertEqual(line["item_id"], "A001")

        # Raw metadata must match the mock catalog exactly.
        expected_metadata = {
            "id": "A001",
            "name": "Single Clean-Match Item",
            "category": "core",
            "score": 0.98,
        }
        meta = get_metadata("A001")
        self.assertEqual(meta, expected_metadata)


# ------------------------------------------------------------------
# READY v3.5 Gate — enforcement tests (governance integrity)
# ------------------------------------------------------------------


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@contextmanager
def _with_file_contents(path: Path, new_contents: str) -> Iterator[None]:
    """Temporarily replace file contents and restore them exactly afterwards."""
    original: Optional[str] = None
    existed = path.exists()
    if existed:
        original = path.read_text(encoding="utf-8")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_contents, encoding="utf-8")

    try:
        yield
    finally:
        if existed and original is not None:
            path.write_text(original, encoding="utf-8")
        else:
            try:
                path.unlink()
            except FileNotFoundError:
                pass


@contextmanager
def _mutate_file(path: Path, transform: Callable[[str], str]) -> Iterator[None]:
    """Temporarily mutate a file in-place, restoring original bytes on exit."""
    original = path.read_text(encoding="utf-8")
    path.write_text(transform(original), encoding="utf-8")
    try:
        yield
    finally:
        path.write_text(original, encoding="utf-8")


def _parse_report_line(line: str) -> dict[str, str]:
    parts = line.split(" | ", 7)
    if len(parts) != 8:
        raise AssertionError(f"Unexpected report line format (expected 8 fields): {line!r}")
    return {
        "timestamp": parts[0],
        "severity": parts[1],
        "system": parts[2],
        "file": parts[3],
        "path": parts[4],
        "code": parts[5],
        "rule": parts[6],
        "message": parts[7],
    }


class TestReadyGateV35(unittest.TestCase):
    def setUp(self) -> None:
        self.root = _repo_root()

    def test_ready_passes_and_summary_line_exact(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert_ready_or_exit(str(self.root))
        out_lines = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip()]
        self.assertTrue(out_lines, "Expected some output from READY gate.")
        self.assertEqual(out_lines[-1], READY_SUMMARY_LINE)

    def test_schema_violation_unknown_top_level_key_emits_schema_validation_error(self):
        tasks_path = self.root / "library/core/valesco_tasks.yaml"

        def add_unknown_top_level_key(text: str) -> str:
            # Add a root-level key (YAML still parses; schema must reject additionalProperties).
            if not text.endswith("\n"):
                text += "\n"
            return text + "bad_key: true\n"

        with _mutate_file(tasks_path, add_unknown_top_level_key):
            ok, report_lines, _ = evaluate_ready(str(self.root))

        self.assertFalse(ok, "Expected READY to fail on schema violation.")

        schema_errors = [
            _parse_report_line(l)
            for l in report_lines
            if " | ERROR | " in l and " | SCHEMA-VALIDATION | " in l
        ]
        self.assertTrue(schema_errors, "Expected at least one SCHEMA-VALIDATION error line.")

        e = schema_errors[0]
        self.assertEqual(e["system"], "validator")
        self.assertEqual(e["file"], "library/core/valesco_tasks.yaml")
        self.assertEqual(e["code"], "READY_SCHEMA_FAIL")
        self.assertEqual(e["rule"], "SCHEMA-VALIDATION")
        self.assertRegex(e["timestamp"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_each_nr_synonym_allows_derived_unit_rate_each_when_only_nr_declared(self):
        """Proves 'each' is accepted as canonical 'nr' without rewriting source files."""
        tasks_path = self.root / "library/core/valesco_tasks.yaml"

        def transform(text: str) -> str:
            # Remove 'each' from meta.units (keep 'nr'), and use derived_unit_rate_each once.
            updated = text.replace(
                "units: [m, m2, m3, lm, hr, nr, day, item, t, l, kg, each]",
                "units: [m, m2, m3, lm, hr, nr, day, item, t, l, kg]",
            )
            # Replace exactly one derived rate key to ensure the synonym logic is exercised.
            updated = updated.replace("derived_unit_rate_m3", "derived_unit_rate_each", 1)
            return updated

        with _mutate_file(tasks_path, transform):
            before = tasks_path.read_text(encoding="utf-8")
            ok, report_lines, _ = evaluate_ready(str(self.root))
            after = tasks_path.read_text(encoding="utf-8")

        self.assertEqual(before, after, "READY gate must not rewrite source files.")
        self.assertTrue(ok, "Expected READY to pass with each/nr synonym normalization.")
        self.assertFalse(any(" | ERROR | " in l for l in report_lines), "No ERROR lines expected.")

    def test_docs_conflict_fails_and_ready_summary_not_printed(self):
        docs_path = self.root / "workspace/inputs/_ACTIVE_DOCS.yaml"
        conflict_yaml = "- name: demo_doc\n  conflict: true\n"

        with _with_file_contents(docs_path, conflict_yaml):
            ok, report_lines, _ = evaluate_ready(str(self.root))
            self.assertFalse(ok, "Expected READY to fail when docs conflict=true is present.")

            conflict_errors = [
                _parse_report_line(l)
                for l in report_lines
                if " | ERROR | " in l and " | DOCS-CONFLICT | " in l
            ]
            self.assertTrue(conflict_errors, "Expected a DOCS-CONFLICT error line.")

            buf = io.StringIO()
            with self.assertRaises(SystemExit):
                with redirect_stdout(buf):
                    assert_ready_or_exit(str(self.root))

            self.assertNotIn(
                READY_SUMMARY_LINE,
                buf.getvalue(),
                "READY summary line must not be printed on failure.",
            )

    def test_boq_coherence_check_is_info_and_non_failing(self):
        ok, report_lines, _ = evaluate_ready(str(self.root))
        self.assertTrue(ok, "Expected READY to pass in baseline repo state.")

        info_lines = [_parse_report_line(l) for l in report_lines if " | INFO | " in l]
        coherence = [
            e
            for e in info_lines
            if e["rule"] == "UNIT-COHERENCE-FAIL" and "skipped (no BoQ context)" in e["message"]
        ]
        self.assertTrue(coherence, "Expected UNIT-COHERENCE-FAIL INFO skip line.")

    def test_entrypoints_fail_closed_when_ready_fails_docs_conflict(self):
        """Proves entrypoint wiring is intact by exercising actual main paths."""
        docs_path = self.root / "workspace/inputs/_ACTIVE_DOCS.yaml"
        conflict_yaml = "- name: demo_doc\n  conflict: true\n"

        entrypoints = [
            ("run_valesco.py", self.root / "run_valesco.py"),
            ("mvp_runner_v2_1.py", self.root / "engine/scripts/mvp_runner_v2_1.py"),
            ("mvp_runner_v2_2.py", self.root / "engine/scripts/mvp_runner_v2_2.py"),
        ]

        with _with_file_contents(docs_path, conflict_yaml):
            for name, script_path in entrypoints:
                proc = subprocess.run(
                    [sys.executable, str(script_path)],
                    input="exit\n",
                    text=True,
                    capture_output=True,
                    cwd=str(self.root),
                    timeout=20,
                )

                out = (proc.stdout or "") + (proc.stderr or "")

                self.assertNotEqual(
                    proc.returncode,
                    0,
                    f"{name} must fail closed when READY fails (exit non-zero). Output:\n{out}",
                )
                self.assertNotIn(
                    READY_SUMMARY_LINE,
                    out,
                    f"{name} must not print READY summary line on failure. Output:\n{out}",
                )
                self.assertIn(
                    " | DOCS-CONFLICT | ",
                    out,
                    f"{name} must surface DOCS-CONFLICT from READY gate. Output:\n{out}",
                )


if __name__ == "__main__":
    unittest.main()
