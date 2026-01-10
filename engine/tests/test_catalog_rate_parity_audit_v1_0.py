import subprocess
import sys
import unittest
from pathlib import Path


class TestCatalogRateParityAuditV1_0(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.script_path = cls.repo_root / "engine" / "scripts" / "catalog_rate_parity_audit_v1_0.py"
        cls.fixtures_root = cls.repo_root / "engine" / "tests" / "fixtures" / "parity"

    def _run_audit(self, fixture_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(self.script_path),
                "--internal-catalog",
                str(fixture_dir / "catalog_internal.json"),
                "--ce-catalog",
                str(fixture_dir / "catalog_ce.json"),
                "--rate-library",
                str(fixture_dir / "rate_library.json"),
            ],
            capture_output=True,
            text=True,
            cwd=self.repo_root,
        )

    def test_aligned_fixture_passes(self) -> None:
        fixture_dir = self.fixtures_root / "aligned"
        result = self._run_audit(fixture_dir)
        self.assertEqual(result.returncode, 0)
        self.assertIn("PARITY_OK", result.stdout)

    def test_mismatched_fixture_fails(self) -> None:
        fixture_dir = self.fixtures_root / "mismatched"
        result = self._run_audit(fixture_dir)
        self.assertEqual(result.returncode, 2)
        self.assertIn("PARITY_VIOLATIONS", result.stdout)
        self.assertIn("missing_in_ce", result.stdout)
        self.assertIn("missing_in_internal", result.stdout)
        self.assertIn("missing_in_rates", result.stdout)
        self.assertIn("orphan_rate_ids", result.stdout)
        self.assertIn("B002", result.stdout)
        self.assertIn("C003", result.stdout)
        self.assertIn("D004", result.stdout)


if __name__ == "__main__":
    unittest.main()
