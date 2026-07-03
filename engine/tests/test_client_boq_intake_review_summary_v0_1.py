import ast
import inspect
import unittest
from copy import deepcopy
from pathlib import Path

import engine.modules.client_boq_intake_v0_1 as intake


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "phase_2" / "client_boq_intake"


def fixture_path(name):
    return FIXTURE_DIR / name


def summary_for(name):
    result = intake.import_client_boq_workbook(str(fixture_path(name)))
    return intake.build_client_boq_intake_review_summary(result)


class TestClientBOQIntakeReviewSummaryV01(unittest.TestCase):
    def test_valid_workbook_summary_passes_but_pricing_and_export_remain_blocked(self):
        summary = summary_for("valid_minimal_client_boq.xlsx")

        self.assertEqual(summary["summary_status"], "pass")
        self.assertEqual(summary["workbook_status"], "pass")
        self.assertEqual(summary["column_mapping_status"], "pass")
        self.assertEqual(summary["source_file_ref"], "valid_minimal_client_boq.xlsx")
        self.assertEqual(
            summary["selected_worksheet"],
            {"worksheet_name": "Client BOQ", "worksheet_index": 1},
        )
        self.assertEqual(
            summary["row_counts"],
            {
                "total_rows": 2,
                "passed_rows": 2,
                "blocked_rows": 0,
                "warning_rows": 0,
                "excluded_rows": 0,
                "review_required_rows": 0,
            },
        )
        self.assertFalse(summary["pricing_approval"])
        self.assertFalse(summary["pricing_ready"])
        self.assertFalse(summary["export_ready"])

    def test_missing_required_fields_summary_fails_and_blocked_rows_are_visible(self):
        summary = summary_for("missing_required_fields_client_boq.xlsx")

        self.assertEqual(summary["summary_status"], "fail")
        self.assertEqual(summary["row_counts"]["total_rows"], 3)
        self.assertEqual(summary["row_counts"]["blocked_rows"], 3)
        self.assertEqual(
            [row["source_row_number"] for row in summary["row_references"]["blocked"]],
            [2, 3, 4],
        )
        messages = _flatten_row_messages(summary)
        self.assertIn("Description is required and is blank or missing.", messages)
        self.assertIn("Unit is required and is blank or missing.", messages)
        self.assertIn("Quantity is required and is blank or missing.", messages)

    def test_invalid_quantity_summary_fails_and_validation_messages_are_surfaced(self):
        summary = summary_for("invalid_quantity_client_boq.xlsx")

        self.assertEqual(summary["summary_status"], "fail")
        self.assertEqual(summary["row_counts"]["blocked_rows"], 2)
        messages = _flatten_row_messages(summary)
        self.assertIn("Quantity is not numeric: many.", messages)
        self.assertIn("Quantity must not be negative: -1.", messages)

    def test_ambiguous_mapping_summary_requires_review_and_surfaces_mapping_messages(self):
        summary = summary_for("ambiguous_mapping_client_boq.xlsx")

        self.assertEqual(summary["summary_status"], "review_required")
        self.assertEqual(summary["column_mapping_status"], "review required")
        self.assertEqual(summary["row_counts"]["passed_rows"], 1)
        mapping_messages = " ".join(
            summary["validation_messages_for_estimator_review"]["column_mapping"]
        )
        self.assertIn("Ambiguous column mapping for description", mapping_messages)
        workbook_messages = " ".join(
            summary["validation_messages_for_estimator_review"]["workbook"]
        )
        self.assertIn("Column mapping requires review before pricing readiness.", workbook_messages)

    def test_hidden_merged_excluded_summary_shows_warning_excluded_and_review_required_rows(self):
        summary = summary_for("hidden_or_merged_structure_client_boq.xlsx")

        self.assertEqual(summary["summary_status"], "fail")
        self.assertEqual(summary["row_counts"]["total_rows"], 4)
        self.assertEqual(summary["row_counts"]["warning_rows"], 2)
        self.assertEqual(summary["row_counts"]["blocked_rows"], 1)
        self.assertEqual(summary["row_counts"]["excluded_rows"], 1)
        self.assertEqual(summary["row_counts"]["review_required_rows"], 4)
        self.assertEqual(
            [row["source_row_number"] for row in summary["row_references"]["warning"]],
            [2, 3],
        )
        self.assertEqual(
            [row["source_row_number"] for row in summary["row_references"]["blocked"]],
            [4],
        )
        self.assertEqual(
            [row["source_row_number"] for row in summary["row_references"]["excluded"]],
            [5],
        )
        self.assertEqual(
            [row["source_row_number"] for row in summary["row_references"]["review_required"]],
            [2, 3, 4, 5],
        )

    def test_row_references_include_source_file_sheet_and_row_number(self):
        summary = summary_for("valid_minimal_client_boq.xlsx")

        self.assertEqual(
            summary["row_references"]["passed"],
            [
                {
                    "source_file_ref": "valid_minimal_client_boq.xlsx",
                    "source_sheet_name": "Client BOQ",
                    "source_row_number": 2,
                },
                {
                    "source_file_ref": "valid_minimal_client_boq.xlsx",
                    "source_sheet_name": "Client BOQ",
                    "source_row_number": 3,
                },
            ],
        )

    def test_deterministic_output_order(self):
        first = summary_for("hidden_or_merged_structure_client_boq.xlsx")
        second = summary_for("hidden_or_merged_structure_client_boq.xlsx")

        self.assertEqual(first, second)
        self.assertEqual(
            list(first.keys()),
            [
                "source_file_ref",
                "workbook_status",
                "selected_worksheet",
                "column_mapping_status",
                "summary_status",
                "row_counts",
                "row_references",
                "validation_messages_for_estimator_review",
                "pricing_approval",
                "pricing_ready",
                "export_ready",
            ],
        )
        self.assertEqual(
            list(first["row_references"].keys()),
            ["passed", "blocked", "warning", "excluded", "review_required"],
        )

    def test_unknown_blank_and_not_checked_statuses_fail_closed_in_summary(self):
        result = intake.import_client_boq_workbook(str(fixture_path("valid_minimal_client_boq.xlsx")))
        mutated = deepcopy(result)
        mutated["workbook_status"] = "not_checked"
        mutated["column_mapping_status"] = ""
        mutated["rows"][0]["validation_status"] = "unknown"

        summary = intake.build_client_boq_intake_review_summary(mutated)

        self.assertEqual(summary["summary_status"], "fail")
        self.assertEqual(summary["row_counts"]["blocked_rows"], 1)
        self.assertEqual(summary["row_counts"]["passed_rows"], 1)
        self.assertEqual(summary["workbook_status"], "not checked")
        self.assertEqual(summary["column_mapping_status"], "")

    def test_summary_function_does_not_import_or_call_prohibited_modules(self):
        source = inspect.getsource(intake)
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
            "engine.modules.ce_backend_adapter_v3_2",
            "engine.modules.ce_retrieval_layer_v2_1",
            "engine.modules.estimator_runtime_v2_1",
            "engine.modules.merge_agent_v2_1",
            "engine.modules.pricing_engine_v3_4",
            "engine.modules.pricing_logic_v2_1",
            "engine.modules.router_v2_1",
            "engine.modules.validator_v2_1",
            "engine.scripts.mvp_runner_v2_1",
            "engine.scripts.mvp_runner_v2_2",
        }

        for module_name in sorted(imports):
            for blocked in forbidden:
                self.assertFalse(
                    module_name == blocked or module_name.startswith(f"{blocked}."),
                    f"Forbidden dependency detected: {module_name}",
                )


def _flatten_row_messages(summary):
    return [
        message
        for row_entry in summary["validation_messages_for_estimator_review"]["rows"]
        for message in row_entry["messages"]
    ]


if __name__ == "__main__":
    unittest.main()
