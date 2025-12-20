import ast
import inspect
import unittest

import engine.modules.resource_builder as resource_builder


class TestResourceBuilderV10(unittest.TestCase):
    def _eli_record(self, excerpt: str, gap_type: str, line_ref: str) -> dict:
        return {
            "source_ref": {
                "source": "boq",
                "section": "General",
                "line_ref": line_ref,
                "line_index": int(line_ref.lstrip("L")),
                "segment_index": 1,
            },
            "detected_gap_type": gap_type,
            "missing_item_state": "A",
            "provisional_resource_hint": f"HINT (provisional): clarify details for '{excerpt}'.",
            "confidence_flag": "medium",
            "traceability_note": f"Gap detected for '{excerpt}'.",
            "provisional": True,
        }

    def test_nominal_resource_build_from_eli(self) -> None:
        eli_output = [
            self._eli_record("Install timber framing", "missing_unit", "L1"),
            self._eli_record("Mobile crane lift", "missing_quantity", "L2"),
            self._eli_record("Concrete block wall", "ambiguous_description", "L3"),
        ]

        output = resource_builder.build_resources(eli_output)

        self.assertTrue(output["all_provisional"])
        self.assertEqual(len(output["labour"]), 1)
        self.assertEqual(len(output["plant"]), 1)
        self.assertEqual(len(output["materials"]), 1)
        self.assertEqual(len(output["assumptions"]), 3)

        for entry in output["labour"] + output["plant"] + output["materials"]:
            self.assertTrue(entry["provisional"])
            self.assertIn("category", entry)
            self.assertIn("traceability", entry)

    def test_deterministic_repeatability(self) -> None:
        eli_output = [
            self._eli_record("Install timber framing", "missing_unit", "L1"),
            self._eli_record("Mobile crane lift", "missing_quantity", "L2"),
        ]

        first = resource_builder.build_resources(eli_output)
        second = resource_builder.build_resources(eli_output)
        self.assertEqual(first, second)

    def test_prohibition_no_forbidden_imports(self) -> None:
        source = inspect.getsource(resource_builder)
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
            "engine.modules.estimator_runtime_v2_1",
            "engine.modules.material_manager_v2_1",
            "engine.modules.merge_agent_v2_1",
            "engine.modules.pricing_engine_v3_4",
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

    def test_schema_and_ordering(self) -> None:
        eli_output = [
            self._eli_record("Install doors", "missing_unit", "L1"),
            self._eli_record("Install windows", "missing_unit", "L2"),
        ]

        output = resource_builder.build_resources(eli_output)

        self.assertEqual(
            list(output.keys()),
            ["labour", "plant", "materials", "assumptions", "all_provisional"],
        )
        self.assertTrue(output["all_provisional"])

        expected_resource_keys = {
            "category",
            "description",
            "indicative_range",
            "traceability",
            "provisional",
        }
        expected_assumption_keys = {"assumption", "traceability", "provisional"}

        for entry in output["labour"]:
            self.assertEqual(set(entry.keys()), expected_resource_keys)
            self.assertTrue(entry["provisional"])

        for entry in output["assumptions"]:
            self.assertEqual(set(entry.keys()), expected_assumption_keys)
            self.assertTrue(entry["provisional"])

        self.assertEqual(
            output["labour"][0]["traceability"]["eli_source_ref"]["line_ref"],
            "L1",
        )
        self.assertEqual(
            output["labour"][1]["traceability"]["eli_source_ref"]["line_ref"],
            "L2",
        )

        blocked_keys = {
            "price",
            "rate",
            "cost",
            "total",
            "sku",
            "library_id",
            "quantity",
            "qty",
        }

        def _assert_no_blocked_keys(value: object) -> None:
            if isinstance(value, dict):
                for key, nested in value.items():
                    self.assertNotIn(key, blocked_keys)
                    _assert_no_blocked_keys(nested)
            elif isinstance(value, list):
                for item in value:
                    _assert_no_blocked_keys(item)

        _assert_no_blocked_keys(output)


if __name__ == "__main__":
    unittest.main()
