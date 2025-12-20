# C:/Valesco_System/engine/tests/logging_telemetry_test_suite_v4.1.py
# Logging & Telemetry Test Suite v4.1
#
# Validates:
#   - Log record structure
#   - Deep-copy behaviour
#   - Level validation
#   - JSON serializability checks
#   - Ordering & determinism
#   - log_error integration from the error-handling layer
#   - No mutation of inputs
#   - No external side effects
#
# Required: 12 tests

import unittest
import copy
import json

from engine.modules.logging_telemetry_v4_1 import (
    log_event,
    get_logs,
    clear_logs,
    log_error,
)


# ---------------------------------------------------------------------------
# GROUP A — Log Event Structure (4 tests)
# ---------------------------------------------------------------------------

class TestLogEventStructure(unittest.TestCase):

    def setUp(self):
        clear_logs()

    def test_1_valid_info_event_structure(self):
        details = {"x": 1, "y": {"z": 2}}
        record = log_event("INFO", "test_event", details)

        # Required keys
        self.assertEqual(
            set(record.keys()),
            {"timestamp", "level", "event", "details"}
        )

        self.assertEqual(record["level"], "INFO")
        self.assertEqual(record["event"], "test_event")
        self.assertIsInstance(record["timestamp"], str)

        # Deep-copy safety: details inside record must not be same object
        self.assertIsNot(record["details"], details)
        self.assertEqual(record["details"], details)
        self.assertIsNot(record["details"]["y"], details["y"])

    def test_2_details_none_allowed(self):
        record = log_event("INFO", "no_details", None)
        self.assertIsNone(record["details"])

    def test_3_invalid_log_level_raises(self):
        with self.assertRaises(ValueError):
            log_event("BADLEVEL", "event", {"x": 1})

    def test_4_non_dict_details_raises(self):
        with self.assertRaises(ValueError):
            log_event("INFO", "bad_details", ["not-a-dict"])


# ---------------------------------------------------------------------------
# GROUP B — Ordering, Determinism, and Buffer Behaviour (4 tests)
# ---------------------------------------------------------------------------

class TestLoggingOrderingDeterminism(unittest.TestCase):

    def setUp(self):
        clear_logs()

    def test_5_chronological_order_preserved(self):
        r1 = log_event("INFO", "e1", {"i": 1})
        r2 = log_event("WARNING", "e2", {"i": 2})
        r3 = log_event("ERROR", "e3", {"i": 3})

        logs = get_logs()
        self.assertEqual(
            [logs[0]["event"], logs[1]["event"], logs[2]["event"]],
            ["e1", "e2", "e3"]
        )

    def test_6_clear_logs_resets_buffer(self):
        log_event("INFO", "first")
        self.assertGreater(len(get_logs()), 0)

        clear_logs()
        self.assertEqual(get_logs(), [])

    def test_7_get_logs_returns_deep_copies(self):
        log_event("INFO", "alpha", {"a": 1})
        logs_copy = get_logs()

        # Mutate returned logs; internal buffer must stay unchanged
        logs_copy[0]["details"]["a"] = 999

        internal_after = get_logs()
        self.assertEqual(internal_after[0]["details"]["a"], 1)

    def test_8_repeated_logging_deterministic(self):
        # First run
        clear_logs()
        log_event("INFO", "a", {"x": 1})
        log_event("WARNING", "b", {"y": 2})
        first = copy.deepcopy(get_logs())

        # Second run
        clear_logs()
        log_event("INFO", "a", {"x": 1})
        log_event("WARNING", "b", {"y": 2})
        second = copy.deepcopy(get_logs())

        self.assertEqual(first, second)


# ---------------------------------------------------------------------------
# GROUP C — JSON Serializability & Error Integration (4 tests)
# ---------------------------------------------------------------------------

class TestLoggingJSONAndErrorIntegration(unittest.TestCase):

    def setUp(self):
        clear_logs()

    def test_9_non_serializable_details_raises(self):
        class NotSerializable:
            pass

        with self.assertRaises(ValueError):
            log_event("INFO", "bad_json", {"obj": NotSerializable()})

    def test_10_log_error_produces_correct_error_event(self):
        err_obj = {
            "error": True,
            "type": "ValueError",
            "message": "bad input",
            "context": {"stage": "test"},
        }
        log_error(err_obj)

        logs = get_logs()
        self.assertEqual(len(logs), 1)
        record = logs[0]

        self.assertEqual(record["level"], "ERROR")
        self.assertEqual(record["event"], "runtime_exception")

        # details must be deep-copied from err_obj
        self.assertEqual(record["details"], err_obj)
        self.assertIsNot(record["details"], err_obj)

    def test_11_log_error_does_not_mutate_input(self):
        err_obj = {
            "error": True,
            "type": "IOError",
            "message": "missing file",
            "context": {"file": "abc.txt"},
        }
        before = copy.deepcopy(err_obj)

        log_error(err_obj)
        self.assertEqual(err_obj, before)

    def test_12_mixed_logging_deterministic(self):
        log_event("INFO", "start", {"k": 1})
        log_error({
            "error": True,
            "type": "ValueError",
            "message": "oops",
            "context": None,
        })
        log_event("WARNING", "halfway", {"m": 2})

        logs1 = copy.deepcopy(get_logs())

        # Repeat identical sequence
        clear_logs()
        log_event("INFO", "start", {"k": 1})
        log_error({
            "error": True,
            "type": "ValueError",
            "message": "oops",
            "context": None,
        })
        log_event("WARNING", "halfway", {"m": 2})

        logs2 = copy.deepcopy(get_logs())

        self.assertEqual(logs1, logs2)


if __name__ == "__main__":
    unittest.main()
