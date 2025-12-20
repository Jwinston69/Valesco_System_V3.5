import ast
import inspect
import unittest

import engine.modules.eli as eli


class TestELIV10(unittest.TestCase):
    def test_nominal_parsing_with_metadata(self) -> None:
        lines = [
            "Install 10 m2 tile flooring",
            "Paint walls qty 5",
        ]
        metadata = [
            {"source": "boq", "section": "Finishes", "line_ref": "L1"},
            {"source": "boq", "section": "Finishes", "line_ref": "L2"},
        ]

        outputs = eli.analyze_boq(lines, metadata)
        self.assertEqual(len(outputs), 1)
        item = outputs[0]
        self.assertEqual(item["detected_gap_type"], "missing_unit")
        self.assertEqual(item["source_ref"]["source"], "boq")
        self.assertEqual(item["source_ref"]["section"], "Finishes")
        self.assertEqual(item["source_ref"]["line_ref"], "L2")
        self.assertEqual(item["source_ref"]["line_index"], 2)
        self.assertEqual(item["source_ref"]["segment_index"], 1)
        self.assertTrue(item["provisional"])

    def test_missing_item_detection(self) -> None:
        lines = [
            "Tile adhesive m2",
            "Install 12",
            "Miscellaneous works as required",
            "Paint finish TBD",
        ]

        outputs = eli.analyze_boq(lines, {"source": "boq"})
        gap_types = {item["detected_gap_type"] for item in outputs}
        self.assertTrue(
            {
                "missing_quantity",
                "missing_unit",
                "ambiguous_description",
                "undefined_specification",
            }.issubset(gap_types)
        )

    def test_deterministic_repeatability(self) -> None:
        text = "Install 12"
        first = eli.analyze_boq(text)
        second = eli.analyze_boq(text)
        self.assertEqual(first, second)

    def test_missing_item_state_coverage(self) -> None:
        lines = [
            "Ceramic tile m2",
            "Tile or stone flooring 20",
            "Install 12",
            "TBD",
            "Concrete blocks or equivalent qty 10",
        ]

        outputs = eli.analyze_boq(lines)
        states = {item["missing_item_state"] for item in outputs}
        self.assertTrue({"A", "B", "C", "D", "E"}.issubset(states))

    def test_prohibition_no_forbidden_imports(self) -> None:
        source = inspect.getsource(eli)
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

    def test_output_schema_and_provisional(self) -> None:
        outputs = eli.analyze_boq("Install 12")
        expected_keys = {
            "source_ref",
            "detected_gap_type",
            "missing_item_state",
            "provisional_resource_hint",
            "confidence_flag",
            "traceability_note",
            "provisional",
        }

        for item in outputs:
            self.assertEqual(set(item.keys()), expected_keys)
            self.assertTrue(item["provisional"])
            self.assertIn(item["confidence_flag"], {"low", "medium"})
            self.assertIn(item["missing_item_state"], {"A", "B", "C", "D", "E"})
            self.assertNotIn("price", item)
            self.assertNotIn("sku", item)
            self.assertNotIn("rate", item)
            self.assertNotIn("cost", item)

    def test_stable_output_order(self) -> None:
        outputs = eli.analyze_boq("Paint finish TBD qty")
        gap_types = [item["detected_gap_type"] for item in outputs]
        self.assertEqual(
            gap_types,
            ["missing_quantity", "ambiguous_description", "undefined_specification"],
        )


if __name__ == "__main__":
    unittest.main()
