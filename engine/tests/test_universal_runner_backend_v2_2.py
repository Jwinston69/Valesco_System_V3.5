import os
import tempfile
import textwrap
import unittest
from contextlib import contextmanager
from pathlib import Path

from engine.scripts.mvp_runner_v2_2 import run_mvp_case_programmatic


def _write_ce_backend_stub(path: Path) -> None:
    stub = textwrap.dedent(
        """
        import json
        import os
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
            marker = os.environ.get("VALESCO_CE_BACKEND_MARKER")
            if marker:
                with open(marker, "w", encoding="utf-8") as handle:
                    handle.write(description)
            json.dump(output, sys.stdout)

        if __name__ == "__main__":
            main()
        """
    ).lstrip()
    path.write_text(stub, encoding="utf-8")


@contextmanager
def _temporary_env(overrides: dict) -> None:
    original = dict(os.environ)
    for key, value in overrides.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


class TestUniversalRunnerBackendV22(unittest.TestCase):
    def test_backend_invocation_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            backend_script = tmp_path / "ce_backend_stub.py"
            marker_file = tmp_path / "backend_marker.txt"
            _write_ce_backend_stub(backend_script)

            with _temporary_env(
                {
                    "VALESCO_CE_BACKEND_SCRIPT": str(backend_script),
                    "VALESCO_CE_BACKEND_CMD": None,
                    "VALESCO_CE_BACKEND_MARKER": str(marker_file),
                }
            ):
                snapshot = run_mvp_case_programmatic("clean item description", ["yes"])

            self.assertTrue(marker_file.exists())
            self.assertEqual(marker_file.read_text(encoding="utf-8"), "clean item description")
            items = snapshot.get("items", [])
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["item_id"], "A001")

    def test_backend_required_no_mock_fallback(self) -> None:
        with _temporary_env(
            {
                "VALESCO_CE_BACKEND_SCRIPT": None,
                "VALESCO_CE_BACKEND_CMD": None,
                "VALESCO_CE_BACKEND_MARKER": None,
            }
        ):
            with self.assertRaises(RuntimeError):
                run_mvp_case_programmatic("clean item description", ["yes"])


if __name__ == "__main__":
    unittest.main()
