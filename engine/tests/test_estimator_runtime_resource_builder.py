import ast
import inspect
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import engine.modules.eli as eli
import engine.modules.resource_builder as resource_builder
import engine.modules.estimator_runtime_v2_1 as estimator_runtime
from engine.modules import pack_registry_v3_5 as pack_registry
from engine.modules.rate_library_ingestion_v3_1 import (
    load_raw_rate_library,
    build_internal_rate_library,
    save_internal_rate_library,
)


class TestEstimatorRuntimeResourceBuilderV10(unittest.TestCase):
    def _eli_output(self) -> list[dict]:
        lines = [
            "Install timber framing qty 5",
            "Mobile crane lift qty 2",
            "Concrete block wall qty 10",
        ]
        return eli.analyze_boq(lines, {"source": "boq", "section": "General"})

    def _pricing_result(self, snapshot: dict) -> dict:
        count = len(snapshot.get("items", []))
        return {
            "lines": [{"pricing": "user-supplied only"} for _ in range(count)],
            "total_cost": 0.0,
        }

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

    def test_nominal_orchestration_with_eli(self) -> None:
        eli_output = self._eli_output()
        resources = resource_builder.build_resources(eli_output)
        pricing_snapshot = estimator_runtime._build_pricing_snapshot_from_resources(resources)
        pricing_result = self._pricing_result(pricing_snapshot)
        expected_pricing = estimator_runtime._merge_pricing(pricing_snapshot, pricing_result)

        with patch("engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"), patch(
            "engine.modules.estimator_runtime_v2_1.pricing_engine.price_estimate_snapshot",
            return_value=pricing_result,
        ):
            output = estimator_runtime.estimator_runtime_resource_step(eli_output)

        self.assertIn("pricing", output)
        self.assertEqual(output["pricing"], expected_pricing)
        self.assertTrue(output["all_provisional"])
        self.assertGreaterEqual(len(output["labour"]), 1)
        self.assertGreaterEqual(len(output["plant"]), 1)
        self.assertGreaterEqual(len(output["materials"]), 1)
        self.assertEqual(len(output["assumptions"]), len(eli_output))

        for entry in output["labour"] + output["plant"] + output["materials"]:
            self.assertTrue(entry["provisional"])
            self.assertIn("traceability", entry)

    def test_deterministic_repeatability(self) -> None:
        eli_output = self._eli_output()
        resources = resource_builder.build_resources(eli_output)
        pricing_snapshot = estimator_runtime._build_pricing_snapshot_from_resources(resources)
        pricing_result = self._pricing_result(pricing_snapshot)

        with patch("engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"), patch(
            "engine.modules.estimator_runtime_v2_1.pricing_engine.price_estimate_snapshot",
            return_value=pricing_result,
        ):
            first = estimator_runtime.estimator_runtime_resource_step(eli_output)
            second = estimator_runtime.estimator_runtime_resource_step(eli_output)
        self.assertEqual(first, second)

    def test_schema_pass_through(self) -> None:
        eli_output = self._eli_output()
        ce_output = {"context": "reference-only"}

        direct = resource_builder.build_resources(eli_output, ce_output=ce_output)
        pricing_snapshot = estimator_runtime._build_pricing_snapshot_from_resources(direct)
        pricing_result = self._pricing_result(pricing_snapshot)
        expected_pricing = estimator_runtime._merge_pricing(pricing_snapshot, pricing_result)

        with patch("engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"), patch(
            "engine.modules.estimator_runtime_v2_1.pricing_engine.price_estimate_snapshot",
            return_value=pricing_result,
        ) as mock_price:
            orchestrated = estimator_runtime.estimator_runtime_resource_step(
                eli_output,
                ce_output=ce_output,
            )

        resources_only = {key: orchestrated[key] for key in direct.keys()}
        self.assertEqual(direct, resources_only)
        mock_price.assert_called_once_with(pricing_snapshot, rate_library={})
        self.assertEqual(orchestrated["pricing"], expected_pricing)

    def test_nominal_pricing_invoked_once(self) -> None:
        eli_output = self._eli_output()
        expected_resources = resource_builder.build_resources(eli_output)
        pricing_snapshot = estimator_runtime._build_pricing_snapshot_from_resources(expected_resources)
        pricing_result = self._pricing_result(pricing_snapshot)
        expected_pricing = estimator_runtime._merge_pricing(pricing_snapshot, pricing_result)

        with patch("engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"), patch(
            "engine.modules.estimator_runtime_v2_1.pricing_engine.price_estimate_snapshot",
            return_value=pricing_result,
        ) as mock_price:
            output = estimator_runtime.estimator_runtime_resource_step(eli_output)

        mock_price.assert_called_once()
        self.assertEqual(mock_price.call_args[0][0], pricing_snapshot)
        self.assertEqual(output["pricing"], expected_pricing)

    def test_invalid_resource_input_raises(self) -> None:
        with patch(
            "engine.modules.estimator_runtime_v2_1.pack_registry.require_registry",
        ) as mock_registry, patch(
            "engine.modules.estimator_runtime_v2_1.pricing_engine.price_estimate_snapshot",
        ) as mock_price:
            with self.assertRaisesRegex(RuntimeError, "invalid resource input"):
                estimator_runtime.estimator_runtime_resource_step("invalid")

        mock_registry.assert_not_called()
        mock_price.assert_not_called()

    def test_empty_pricing_output_raises(self) -> None:
        eli_output = self._eli_output()
        resources = resource_builder.build_resources(eli_output)
        pricing_snapshot = estimator_runtime._build_pricing_snapshot_from_resources(resources)
        pricing_result = {"lines": [], "total_cost": 0.0}

        with patch("engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"), patch(
            "engine.modules.estimator_runtime_v2_1.pricing_engine.price_estimate_snapshot",
            return_value=pricing_result,
        ) as mock_price:
            with self.assertRaisesRegex(RuntimeError, "output invalid"):
                estimator_runtime.estimator_runtime_resource_step(eli_output)

        mock_price.assert_called_once()

    def test_price_snapshot_requires_pack_registry(self) -> None:
        snapshot = {"items": [{"item_id": "A001"}]}
        with patch(
            "engine.modules.estimator_runtime_v2_1.pack_registry.require_registry",
            side_effect=RuntimeError("Pack registry missing."),
        ):
            with self.assertRaisesRegex(RuntimeError, "Pack registry missing"):
                estimator_runtime.estimator_runtime_price_snapshot(
                    snapshot, rate_library_path="rates.json"
                )

    def test_price_snapshot_requires_rate_library_path(self) -> None:
        snapshot = {"items": [{"item_id": "A001"}]}
        with patch("engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"), patch.dict(
            os.environ, {}, clear=True
        ):
            with self.assertRaisesRegex(RuntimeError, "rate library path"):
                estimator_runtime.estimator_runtime_price_snapshot(snapshot)

    def test_price_snapshot_fails_when_registry_initialized_but_missing_required_authority_pack(
        self,
    ) -> None:
        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Test Item A001",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 1.0,
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            rate_path = os.path.join(tmpdir, "rates.json")
            self._write_rate_library(rate_path)

            with patch.dict(
                os.environ, {"VALESCO_RATE_LIBRARY_PATH": rate_path}, clear=False
            ), patch(
                "engine.modules.estimator_runtime_v2_1.pack_registry.require_registry"
            ), patch(
                "engine.modules.pricing_engine_v3_4.pack_registry.is_initialized",
                return_value=True,
            ), patch(
                "engine.modules.pricing_engine_v3_4.pack_registry.get_registry_root",
                return_value=Path("C:/tmp/valesco_registry_root"),
            ), patch(
                "engine.modules.pricing_engine_v3_4.pack_registry.get_pack",
                return_value={"meta": {"pack": "ok"}},
            ), patch(
                "engine.modules.pricing_engine_v3_4.pack_registry.get_materials",
                side_effect=KeyError("materials missing"),
            ), patch(
                "engine.modules.pricing_engine_v3_4.pack_registry.get_subcontractors",
                return_value={"meta": {"subcontractors": "ok"}},
            ):
                with self.assertRaisesRegex(RuntimeError, "missing required authority pack"):
                    estimator_runtime.estimator_runtime_price_snapshot(snapshot)

    def test_price_snapshot_maps_pricing_engine_output(self) -> None:
        pack_registry.initialize_registry(log=False)
        snapshot = {
            "items": [
                {
                    "item_id": "A001",
                    "source": "catalog",
                    "display_name": "Test Item A001",
                    "metadata": {},
                    "status": "confirmed",
                    "quantity": 2.0,
                },
                {
                    "item_id": None,
                    "source": "provisional",
                    "display_name": "Custom Item",
                    "metadata": {},
                    "status": "confirmed",
                },
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            rate_path = os.path.join(tmpdir, "rates.json")
            self._write_rate_library(rate_path)
            priced = estimator_runtime.estimator_runtime_price_snapshot(
                snapshot, rate_library_path=rate_path
            )

        self.assertEqual(len(priced["items"]), 2)
        first = priced["items"][0]["pricing"]
        self.assertEqual(first["item_id"], "A001")
        self.assertEqual(first["quantity"], 2.0)
        self.assertIn("total_cost", first)
        second = priced["items"][1]["pricing"]
        self.assertEqual(second, {"pricing": "user-supplied only"})

    def test_prohibition_no_forbidden_imports(self) -> None:
        source = inspect.getsource(estimator_runtime)
        tree = ast.parse(source)
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
                for alias in node.names:
                    imports.add(f"{node.module}.{alias.name}")

        forbidden = {
            "engine.modules.architect_v2_1",
            "engine.modules.cortex_v1_0",
            "engine.modules.material_manager_v2_1",
            "engine.modules.merge_agent_v2_1",
            "engine.modules.pricing_logic_v2_1",
            "engine.modules.rate_build_up_v3_3",
            "engine.modules.rate_library_ingestion_v3_1",
            "engine.modules.rate_retrieval_v3_2",
            "engine.modules.router_v2_1",
            "engine.modules.validator_v2_1",
        }

        for module_name in sorted(imports):
            for blocked in forbidden:
                self.assertFalse(
                    module_name == blocked or module_name.startswith(f"{blocked}."),
                    f"Forbidden dependency detected: {module_name}",
                )


if __name__ == "__main__":
    unittest.main()
