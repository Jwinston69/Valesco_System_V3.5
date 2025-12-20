"""Valesco portable test runner (ops/tooling only).

Goal:
- Make test execution reproducible under the embeddable Python runtime by
  bootstrapping sys.path to include the repository root.

Non-goals:
- No changes to any test logic.
- No reliance on PYTHONPATH.
- No external dependencies.

Usage (recommended):
  engine\python_runtime\python.exe engine\scripts\run_tests_portable.py

Optional:
  Set VALESCO_TEST_PATTERN to override discovery pattern.
"""

from __future__ import annotations

import os
import sys
import unittest


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main() -> int:
    repo_root = _repo_root()

    # Ensure deterministic working directory (some suites may assume relative paths).
    os.chdir(repo_root)

    # Embeddable Python runs with an isolated sys.path; explicitly add repo root.
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    start_dir = os.path.join(repo_root, "engine", "tests")
    # Default to the documented canonical MVP integration suite.
    # Override via VALESCO_TEST_PATTERN when you intentionally want broader coverage.
    pattern = os.environ.get("VALESCO_TEST_PATTERN", "integration_test_suite_v2_1.py")

    # Use default discovery semantics (do not require engine/tests to be a package).
    # We already add repo_root to sys.path above, so imports like `engine.modules.*`
    # remain resolvable without relying on PYTHONPATH.
    suite = unittest.defaultTestLoader.discover(
        start_dir=start_dir,
        pattern=pattern,
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
