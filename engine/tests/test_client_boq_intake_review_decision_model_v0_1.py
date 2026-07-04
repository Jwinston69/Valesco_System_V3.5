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


def decision_for(summary):
    return intake.build_client_boq_intake_review_decision(summary)


class TestClientBOQIntakeReviewDecisionModelV01(unittest.TestCase):
    def test_clean_summary_decision_import_clean_pricing_blocked(self):
        decision = decision_for(summary_for("valid_minimal_client_boq.xlsx"))

        self.assertEqual(decision["decision_status"], "import_clean_pricing_blocked")
        self.assertEqual(
            decision["reason_codes"],
            ["import_clean", "pricing_blocked", "export_blocked", "client_return_blocked"],
        )

    def test_failed_summary_decision_import_failed_pricing_blocked(self):
        decision = decision_for(summary_for("missing_required_fields_client_boq.xlsx"))

        self.assertEqual(decision["decision_status"], "import_failed_pricing_blocked")
        self.assertIn("summary_failed", decision["reason_codes"])
        self.assertIn("blocked_rows_present", decision["reason_codes"])

    def test_missing_or_blank_summary_status_fails_closed(self):
        missing_status = clean_summary()
        del missing_status["summary_status"]
        blank_status = clean_summary()
        blank_status["summary_status"] = ""

        self.assertEqual(
            decision_for(missing_status)["decision_status"],
            "import_failed_pricing_blocked",
        )
        self.assertIn("summary_status_missing", decision_for(missing_status)["reason_codes"])
        self.assertEqual(
            decision_for(blank_status)["decision_status"],
            "import_failed_pricing_blocked",
        )
        self.assertIn("summary_status_missing", decision_for(blank_status)["reason_codes"])

    def test_unknown_and_not_checked_summary_statuses_fail_closed(self):
        for status in ("unknown", "not_checked", "not checked"):
            summary = clean_summary()
            summary["summary_status"] = status

            decision = decision_for(summary)

            self.assertEqual(decision["decision_status"], "import_failed_pricing_blocked")
            self.assertIn("summary_status_unknown", decision["reason_codes"])

    def test_missing_or_malformed_required_summary_evidence_fails_closed(self):
        missing_counts = clean_summary()
        del missing_counts["row_counts"]
        malformed_references = clean_summary()
        malformed_references["row_references"] = []
        malformed_messages = clean_summary()
        malformed_messages["validation_messages_for_estimator_review"] = []

        self.assertEqual(
            decision_for(missing_counts)["decision_status"],
            "import_failed_pricing_blocked",
        )
        self.assertIn("row_counts_missing", decision_for(missing_counts)["reason_codes"])
        self.assertEqual(
            decision_for(malformed_references)["decision_status"],
            "import_failed_pricing_blocked",
        )
        self.assertEqual(
            decision_for(malformed_messages)["decision_status"],
            "import_failed_pricing_blocked",
        )

    def test_excluded_rows_decision_unless_failure_exists(self):
        summary = clean_summary()
        summary["summary_status"] = "review_required"
        summary["row_counts"]["passed_rows"] = 1
        summary["row_counts"]["excluded_rows"] = 1
        summary["row_counts"]["review_required_rows"] = 1
        summary["row_references"]["excluded"] = [row_reference(3)]
        summary["row_references"]["review_required"] = [row_reference(3)]

        decision = decision_for(summary)

        self.assertEqual(decision["decision_status"], "excluded_or_partial_review_required")
        self.assertIn("excluded_rows_present", decision["reason_codes"])

        summary["summary_status"] = "fail"
        summary["row_counts"]["blocked_rows"] = 1

        failed_decision = decision_for(summary)

        self.assertEqual(failed_decision["decision_status"], "import_failed_pricing_blocked")
        self.assertIn("summary_failed", failed_decision["reason_codes"])
        self.assertIn("blocked_rows_present", failed_decision["reason_codes"])

    def test_review_required_summary_without_exclusion_or_failure(self):
        summary = clean_summary()
        summary["summary_status"] = "review_required"
        summary["column_mapping_status"] = "review required"
        summary["row_counts"]["review_required_rows"] = 1
        summary["row_references"]["review_required"] = [row_reference(2)]

        decision = decision_for(summary)

        self.assertEqual(decision["decision_status"], "review_required_pricing_blocked")
        self.assertEqual(
            decision["reason_codes"],
            [
                "review_required_rows_present",
                "column_mapping_review_required",
                "pricing_blocked",
                "export_blocked",
                "client_return_blocked",
            ],
        )

    def test_decision_preserves_summary_evidence(self):
        summary = summary_for("ambiguous_mapping_client_boq.xlsx")

        decision = decision_for(summary)

        self.assertEqual(decision["summary_status"], summary["summary_status"])
        self.assertEqual(decision["row_counts"], summary["row_counts"])
        self.assertEqual(decision["row_references"], summary["row_references"])
        self.assertEqual(
            decision["validation_messages_for_estimator_review"],
            summary["validation_messages_for_estimator_review"],
        )

    def test_readiness_guards_remain_false(self):
        decision = decision_for(summary_for("valid_minimal_client_boq.xlsx"))

        self.assertFalse(decision["pricing_approval"])
        self.assertFalse(decision["pricing_ready"])
        self.assertFalse(decision["export_ready"])
        self.assertFalse(decision["client_return_ready"])

    def test_input_summary_is_not_mutated(self):
        summary = summary_for("hidden_or_merged_structure_client_boq.xlsx")
        before = deepcopy(summary)

        decision_for(summary)

        self.assertEqual(summary, before)

    def test_deterministic_reason_code_ordering(self):
        summary = clean_summary()
        summary["summary_status"] = "fail"
        summary["column_mapping_status"] = "review required"
        summary["row_counts"].update(
            {
                "passed_rows": 0,
                "blocked_rows": 1,
                "warning_rows": 1,
                "excluded_rows": 1,
                "review_required_rows": 1,
            }
        )

        decision = decision_for(summary)

        self.assertEqual(
            decision["reason_codes"],
            [
                "summary_failed",
                "blocked_rows_present",
                "warning_rows_present",
                "excluded_rows_present",
                "review_required_rows_present",
                "column_mapping_review_required",
                "pricing_blocked",
                "export_blocked",
                "client_return_blocked",
            ],
        )

    def test_decision_function_does_not_import_or_call_prohibited_modules(self):
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


def clean_summary():
    return {
        "source_file_ref": "synthetic_client_boq.xlsx",
        "workbook_status": "pass",
        "selected_worksheet": {"worksheet_name": "Client BOQ", "worksheet_index": 1},
        "column_mapping_status": "pass",
        "summary_status": "pass",
        "row_counts": {
            "total_rows": 2,
            "passed_rows": 2,
            "blocked_rows": 0,
            "warning_rows": 0,
            "excluded_rows": 0,
            "review_required_rows": 0,
        },
        "row_references": {
            "passed": [row_reference(2), row_reference(3)],
            "blocked": [],
            "warning": [],
            "excluded": [],
            "review_required": [],
        },
        "validation_messages_for_estimator_review": {
            "workbook": [],
            "column_mapping": [],
            "rows": [],
        },
        "pricing_approval": False,
        "pricing_ready": False,
        "export_ready": False,
    }


def row_reference(row_number):
    return {
        "source_file_ref": "synthetic_client_boq.xlsx",
        "source_sheet_name": "Client BOQ",
        "source_row_number": row_number,
    }


if __name__ == "__main__":
    unittest.main()
