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


def packet_for(summary):
    return intake.build_client_boq_intake_review_packet(summary, decision_for(summary))


class TestClientBOQIntakeReviewPacketV01(unittest.TestCase):
    def test_clean_decision_maps_to_clean_packet(self):
        packet = packet_for(summary_for("valid_minimal_client_boq.xlsx"))

        self.assertEqual(packet["review_packet_status"], "review_packet_clean_pricing_blocked")
        self.assertEqual(packet["decision_status"], "import_clean_pricing_blocked")

    def test_review_required_decision_maps_to_review_required_packet(self):
        packet = packet_for(summary_for("ambiguous_mapping_client_boq.xlsx"))

        self.assertEqual(packet["review_packet_status"], "review_packet_review_required_pricing_blocked")
        self.assertEqual(packet["decision_status"], "review_required_pricing_blocked")

    def test_failed_decision_maps_to_failed_packet(self):
        packet = packet_for(summary_for("missing_required_fields_client_boq.xlsx"))

        self.assertEqual(packet["review_packet_status"], "review_packet_failed_pricing_blocked")
        self.assertEqual(packet["decision_status"], "import_failed_pricing_blocked")

    def test_excluded_partial_decision_maps_to_excluded_partial_packet(self):
        summary = clean_summary()
        summary["summary_status"] = "review_required"
        summary["row_counts"]["passed_rows"] = 1
        summary["row_counts"]["excluded_rows"] = 1
        summary["row_counts"]["review_required_rows"] = 1
        summary["row_references"]["excluded"] = [row_reference(3)]
        summary["row_references"]["review_required"] = [row_reference(3)]

        packet = packet_for(summary)

        self.assertEqual(packet["review_packet_status"], "review_packet_excluded_or_partial_review_required")
        self.assertEqual(packet["decision_status"], "excluded_or_partial_review_required")

    def test_unknown_blank_missing_or_not_checked_decision_status_invalidates_packet(self):
        for status in ("unknown", "", "not_checked", "not checked"):
            summary = clean_summary()
            decision = decision_for(summary)
            decision["decision_status"] = status

            packet = intake.build_client_boq_intake_review_packet(summary, decision)

            self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
            self.assertIn("packet_invalid", packet["reason_codes"])

        summary = clean_summary()
        decision = decision_for(summary)
        del decision["decision_status"]

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
        self.assertIn("decision_status_missing", packet["reason_codes"])

    def test_missing_or_malformed_summary_invalidates_packet(self):
        valid_decision = decision_for(clean_summary())

        for summary in (None, []):
            packet = intake.build_client_boq_intake_review_packet(summary, valid_decision)

            self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
            self.assertIn("summary_missing", packet["reason_codes"])

    def test_missing_or_malformed_decision_invalidates_packet(self):
        summary = clean_summary()

        for decision in (None, []):
            packet = intake.build_client_boq_intake_review_packet(summary, decision)

            self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
            self.assertIn("decision_missing", packet["reason_codes"])

    def test_mismatched_summary_status_invalidates_packet(self):
        summary = clean_summary()
        decision = decision_for(summary)
        decision["summary_status"] = "review_required"

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
        self.assertIn("summary_decision_status_mismatch", packet["reason_codes"])

    def test_mismatched_row_counts_invalidates_packet(self):
        summary = clean_summary()
        decision = decision_for(summary)
        decision["row_counts"] = dict(decision["row_counts"], passed_rows=1)

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
        self.assertIn("row_counts_mismatch", packet["reason_codes"])

    def test_mismatched_row_references_invalidates_packet(self):
        summary = clean_summary()
        decision = decision_for(summary)
        decision["row_references"] = dict(decision["row_references"], passed=[])

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
        self.assertIn("row_references_mismatch", packet["reason_codes"])

    def test_mismatched_validation_messages_invalidates_packet(self):
        summary = clean_summary()
        decision = decision_for(summary)
        decision["validation_messages_for_estimator_review"] = {
            "workbook": ["changed"],
            "column_mapping": [],
            "rows": [],
        }

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
        self.assertIn("validation_messages_mismatch", packet["reason_codes"])

    def test_invalid_readiness_guards_invalidate_packet(self):
        for owner, key, value in (
            ("summary", "pricing_ready", True),
            ("summary", "export_ready", None),
            ("decision", "client_return_ready", True),
            ("decision", "pricing_approval", "false"),
        ):
            summary = clean_summary()
            decision = decision_for(summary)
            target = summary if owner == "summary" else decision
            target[key] = value

            packet = intake.build_client_boq_intake_review_packet(summary, decision)

            self.assertEqual(packet["review_packet_status"], "review_packet_invalid_pricing_blocked")
            self.assertIn("readiness_guard_invalid", packet["reason_codes"])

    def test_packet_preserves_summary_and_decision_evidence(self):
        summary = summary_for("ambiguous_mapping_client_boq.xlsx")
        decision = decision_for(summary)

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(packet["source_file_ref"], summary["source_file_ref"])
        self.assertEqual(packet["selected_worksheet"], summary["selected_worksheet"])
        self.assertEqual(packet["workbook_status"], summary["workbook_status"])
        self.assertEqual(packet["column_mapping_status"], summary["column_mapping_status"])
        self.assertEqual(packet["summary_status"], summary["summary_status"])
        self.assertEqual(packet["decision_status"], decision["decision_status"])
        self.assertEqual(packet["reason_codes"], decision["reason_codes"])
        self.assertEqual(packet["row_counts"], summary["row_counts"])
        self.assertEqual(packet["row_references"], summary["row_references"])
        self.assertEqual(
            packet["validation_messages_for_estimator_review"],
            summary["validation_messages_for_estimator_review"],
        )

    def test_packet_has_deterministic_review_packet_sections(self):
        packet = packet_for(summary_for("valid_minimal_client_boq.xlsx"))

        self.assertEqual(
            list(packet["review_packet_sections"].keys()),
            ["source", "statuses", "row_evidence", "messages", "readiness_guards"],
        )
        self.assertEqual(
            list(packet["review_packet_sections"]["readiness_guards"].keys()),
            ["pricing_approval", "pricing_ready", "export_ready", "client_return_ready"],
        )

    def test_readiness_guards_remain_false(self):
        packet = packet_for(summary_for("valid_minimal_client_boq.xlsx"))

        self.assertFalse(packet["pricing_approval"])
        self.assertFalse(packet["pricing_ready"])
        self.assertFalse(packet["export_ready"])
        self.assertFalse(packet["client_return_ready"])

    def test_input_summary_and_decision_are_not_mutated(self):
        summary = summary_for("hidden_or_merged_structure_client_boq.xlsx")
        decision = decision_for(summary)
        before_summary = deepcopy(summary)
        before_decision = deepcopy(decision)

        intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(summary, before_summary)
        self.assertEqual(decision, before_decision)

    def test_deterministic_reason_code_ordering_for_invalid_packet(self):
        summary = clean_summary()
        decision = decision_for(summary)
        decision["decision_status"] = "unknown"
        decision["summary_status"] = "review_required"
        decision["row_counts"] = dict(decision["row_counts"], passed_rows=1)
        decision["row_references"] = dict(decision["row_references"], passed=[])
        decision["validation_messages_for_estimator_review"] = {
            "workbook": ["changed"],
            "column_mapping": [],
            "rows": [],
        }
        decision["pricing_ready"] = True

        packet = intake.build_client_boq_intake_review_packet(summary, decision)

        self.assertEqual(
            packet["reason_codes"],
            [
                "decision_status_unknown",
                "summary_decision_status_mismatch",
                "row_counts_mismatch",
                "row_references_mismatch",
                "validation_messages_mismatch",
                "readiness_guard_invalid",
                "packet_invalid",
                "pricing_blocked",
                "export_blocked",
                "client_return_blocked",
            ],
        )

    def test_packet_function_does_not_import_or_call_prohibited_modules(self):
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
