import ast
import inspect
import unittest
from unittest.mock import patch

import engine.modules.eli as eli
import engine.modules.resource_builder as resource_builder
import engine.modules.estimator_runtime_v2_1 as estimator_runtime


class TestEstimatorRuntimeResourceBuilderV10(unittest.TestCase):
    def _eli_output(self) -> list[dict]:
        lines = [
            "Install timber framing qty 5",
            "Mobile crane lift qty 2",
            "Concrete block wall qty 10",
        ]
        return eli.analyze_boq(lines, {"source": "boq", "section": "General"})

    def _pricing_output(self) -> dict:
        return {"items": [{"pricing": "user-supplied only"}]}

    def test_nominal_orchestration_with_eli(self) -> None:
        eli_output = self._eli_output()
        sentinel = self._pricing_output()

        with patch(
            "engine.modules.estimator_runtime_v2_1.pricing_logic.price_estimate",
            return_value=sentinel,
        ):
            output = estimator_runtime.estimator_runtime_resource_step(eli_output)

        self.assertIn("pricing", output)
        self.assertEqual(output["pricing"], sentinel)
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
        sentinel = self._pricing_output()

        with patch(
            "engine.modules.estimator_runtime_v2_1.pricing_logic.price_estimate",
            return_value=sentinel,
        ):
            first = estimator_runtime.estimator_runtime_resource_step(eli_output)
            second = estimator_runtime.estimator_runtime_resource_step(eli_output)
        self.assertEqual(first, second)

    def test_schema_pass_through(self) -> None:
        eli_output = self._eli_output()
        ce_output = {"context": "reference-only"}
        sentinel = self._pricing_output()

        direct = resource_builder.build_resources(eli_output, ce_output=ce_output)

        with patch(
            "engine.modules.estimator_runtime_v2_1.pricing_logic.price_estimate",
            return_value=sentinel,
        ) as mock_price:
            orchestrated = estimator_runtime.estimator_runtime_resource_step(
                eli_output,
                ce_output=ce_output,
            )

        resources_only = {key: orchestrated[key] for key in direct.keys()}
        self.assertEqual(direct, resources_only)
        mock_price.assert_called_once_with(direct)
        self.assertEqual(orchestrated["pricing"], sentinel)

    def test_nominal_pricing_invoked_once(self) -> None:
        eli_output = self._eli_output()
        expected_resources = resource_builder.build_resources(eli_output)
        sentinel = {"items": [{"pricing": "user-supplied only"}]}

        with patch(
            "engine.modules.estimator_runtime_v2_1.pricing_logic.price_estimate",
            return_value=sentinel,
        ) as mock_price:
            output = estimator_runtime.estimator_runtime_resource_step(eli_output)

        mock_price.assert_called_once()
        self.assertEqual(mock_price.call_args[0][0], expected_resources)
        self.assertEqual(output["pricing"], sentinel)

    def test_invalid_resource_input_raises(self) -> None:
        with patch(
            "engine.modules.estimator_runtime_v2_1.pricing_logic.price_estimate",
        ) as mock_price:
            with self.assertRaisesRegex(RuntimeError, "invalid resource input"):
                estimator_runtime.estimator_runtime_resource_step("invalid")

        mock_price.assert_not_called()

    def test_empty_pricing_output_raises(self) -> None:
        eli_output = self._eli_output()
        sentinel = {"items": []}

        with patch(
            "engine.modules.estimator_runtime_v2_1.pricing_logic.price_estimate",
            return_value=sentinel,
        ) as mock_price:
            with self.assertRaisesRegex(RuntimeError, "output empty"):
                estimator_runtime.estimator_runtime_resource_step(eli_output)

        mock_price.assert_called_once()

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
            "engine.modules.pricing_engine_v3_4",
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
