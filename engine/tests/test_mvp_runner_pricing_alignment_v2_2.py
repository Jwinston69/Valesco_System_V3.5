import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from engine.modules import estimator_runtime_v2_1 as estimator_runtime
from engine.modules import pack_registry_v3_5 as pack_registry
from engine.modules.merge_agent_v2_1 import (
    add_catalog_item,
    get_estimate_snapshot,
    init_estimate,
)
from engine.modules.quantity_logic_v2_1 import set_quantity
from engine.modules.rate_library_ingestion_v3_1 import (
    build_internal_rate_library,
    load_raw_rate_library,
    save_internal_rate_library,
)
from engine.scripts import mvp_runner_v2_2


class TestMvpRunnerPricingAlignmentV22(unittest.TestCase):
    def setUp(self) -> None:
        estimator_runtime._PRICING_FN = None
        estimator_runtime._PRICING_FN_PATH = None

    def _write_rate_library(self, path: str) -> None:
        external_rates = [
            {
                "id": "A001",
                "description": "Test rate A001",
                "components": {"material": {"rate": 12.5, "unit": "m2"}},
            }
        ]
        normalized = load_raw_rate_library(external_rates)
        library = build_internal_rate_library(normalized)
        save_internal_rate_library(library, path)

    def _seed_estimate(self) -> None:
        init_estimate()
        add_catalog_item({"id": "A001", "name": "Item A001"})
        snapshot = get_estimate_snapshot()
        snapshot = set_quantity(0, 2.0, snapshot)
        mvp_runner_v2_2._apply_snapshot_and_write_back(snapshot)

    def test_price_command_uses_pricing_engine(self) -> None:
        self._seed_estimate()
        pack_registry.initialize_registry(log=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            rate_path = os.path.join(tmpdir, "rates.json")
            self._write_rate_library(rate_path)

            def _fake_price_for_runner(path: str):
                def _price(snapshot: dict) -> dict:
                    count = len(snapshot.get("items", []))
                    return {
                        "lines": [{"pricing": "user-supplied only"} for _ in range(count)],
                        "total_cost": 0.0,
                    }

                return _price

            with patch.dict(
                os.environ, {"VALESCO_RATE_LIBRARY_PATH": rate_path}, clear=False
            ), patch(
                "engine.modules.pricing_engine_v3_4.price_estimate_for_runner",
                side_effect=_fake_price_for_runner,
            ) as mock_price_for_runner:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    mvp_runner_v2_2._print_pricing()

            mock_price_for_runner.assert_called_once_with(rate_path)

    def test_price_command_fails_without_pack_registry(self) -> None:
        self._seed_estimate()

        with tempfile.TemporaryDirectory() as tmpdir:
            rate_path = os.path.join(tmpdir, "rates.json")
            self._write_rate_library(rate_path)

            with patch.dict(
                os.environ, {"VALESCO_RATE_LIBRARY_PATH": rate_path}, clear=False
            ), patch(
                "engine.modules.estimator_runtime_v2_1.pack_registry.require_registry",
                side_effect=RuntimeError(
                    "Pack registry missing required authority packs: library/packs/valesco_pack.yaml"
                ),
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    with self.assertRaisesRegex(RuntimeError, "Pack registry missing required authority packs"):
                        mvp_runner_v2_2._print_pricing()


if __name__ == "__main__":
    unittest.main()
