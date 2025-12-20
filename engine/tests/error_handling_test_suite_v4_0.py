# C:/Valesco_System/engine/tests/error_handling_test_suite_v4.0.py
# Error-Handling Test Suite v4.0
#
# Validates:
#   - Structured error object creation
#   - Deterministic behaviour of wrap() and safe_call()
#   - Strict exception filtering
#   - No mutation of context
#   - Correct propagation of unexpected exceptions
#   - Runtime-layer isolation (no CE/Estimator interference)
#
# Required: 12 tests

import unittest
import copy

from engine.modules.error_handling_v4_0 import (
    wrap,
    safe_call,
    _build_error_object,
)


class TestErrorHandlingErrorObject(unittest.TestCase):
    # ------------------------------------------------------------------ #
    # GROUP A — Error Object Construction (3 tests)                      #
    # ------------------------------------------------------------------ #

    def test_1_error_object_type_message_context_correct(self):
        exc = ValueError("example message")
        context = {"stage": "test", "details": {"x": 1}}
        err = _build_error_object(exc, context)

        # Exact keys
        self.assertEqual(set(err.keys()), {"error", "type", "message", "context"})
        self.assertTrue(err["error"])
        self.assertEqual(err["type"], "ValueError")
        self.assertEqual(err["message"], "example message")

        # Deep copy of context (no shared references)
        self.assertIsNot(err["context"], context)
        self.assertEqual(err["context"], context)
        self.assertIsNot(err["context"]["details"], context["details"])

    def test_2_context_none_results_in_context_none(self):
        exc = KeyError("missing key")
        err = _build_error_object(exc, None)
        self.assertTrue(err["error"])
        self.assertEqual(err["type"], "KeyError")
        self.assertEqual(err["message"], "'missing key'")
        self.assertIsNone(err["context"])

    def test_3_error_object_has_no_extra_fields(self):
        exc = TypeError("wrong type")
        context = {"stage": "unit-test"}
        err = _build_error_object(exc, context)

        self.assertEqual(set(err.keys()), {"error", "type", "message", "context"})


class TestErrorHandlingWrap(unittest.TestCase):
    # ------------------------------------------------------------------ #
    # GROUP B — wrap() behaviour (5 tests)                               #
    # ------------------------------------------------------------------ #

    def test_4_successful_operation_passes_through_result(self):
        def op():
            return 42

        result = wrap(op)
        self.assertEqual(result, 42)

    def test_5_handled_exception_returns_error_object(self):
        def op():
            raise ValueError("bad value")

        result = wrap(op, context={"stage": "wrap-test"})
        self.assertIsInstance(result, dict)
        self.assertTrue(result["error"])
        self.assertEqual(result["type"], "ValueError")
        self.assertEqual(result["message"], "bad value")
        self.assertEqual(result["context"], {"stage": "wrap-test"})

    def test_6_only_approved_exceptions_are_caught(self):
        def op():
            raise RuntimeError("unexpected")

        with self.assertRaises(RuntimeError):
            wrap(op, context={"stage": "wrap-runtime"})

    def test_7_context_deep_copied_in_wrap(self):
        ctx = {"stage": "wrap", "meta": {"x": 1}}

        def op():
            raise ValueError("fail")

        result = wrap(op, context=ctx)
        # mutate original after call
        ctx["meta"]["x"] = 999
        ctx["new"] = "added"

        self.assertEqual(result["context"], {"stage": "wrap", "meta": {"x": 1}})
        # Confirm no shared reference
        self.assertIsNot(result["context"]["meta"], ctx["meta"])

    def test_8_wrap_does_not_mutate_or_infer_context(self):
        ctx = {"stage": "wrap", "info": {"y": 2}}

        def op():
            raise KeyError("missing")

        before = copy.deepcopy(ctx)
        result = wrap(op, context=ctx)

        # Original context unchanged
        self.assertEqual(ctx, before)

        # Error context equals original at time of call
        self.assertEqual(result["context"], before)


class TestErrorHandlingSafeCall(unittest.TestCase):
    # ------------------------------------------------------------------ #
    # GROUP C — safe_call() behaviour (4 tests)                          #
    # ------------------------------------------------------------------ #

    def test_9_successful_safe_call_returns_result(self):
        def add(a, b):
            return a + b

        result = safe_call(add, 2, 3)
        self.assertEqual(result, 5)

    def test_10_safe_call_catches_allowed_exceptions(self):
        def op(a):
            raise ValueError(f"bad {a}")

        result = safe_call(op, "input", context={"stage": "safe-call"})
        self.assertIsInstance(result, dict)
        self.assertTrue(result["error"])
        self.assertEqual(result["type"], "ValueError")
        self.assertEqual(result["message"], "bad input")
        self.assertEqual(result["context"], {"stage": "safe-call"})

    def test_11_safe_call_propagates_unexpected_exceptions(self):
        def op():
            raise RuntimeError("unexpected safe_call")

        with self.assertRaises(RuntimeError):
            safe_call(op, context={"stage": "safe-call-unexpected"})

    def test_12_safe_call_passes_context_correctly_and_not_mutated(self):
        ctx = {"stage": "safe_call", "data": {"z": 3}}

        def op():
            raise KeyError("missing")

        before = copy.deepcopy(ctx)
        result = safe_call(op, context=ctx)

        # Original context must be unchanged
        self.assertEqual(ctx, before)

        # Context in error object is deep copy of original
        self.assertEqual(result["context"], before)
        self.assertIsNot(result["context"], ctx)
        self.assertIsNot(result["context"]["data"], ctx["data"])


if __name__ == "__main__":
    unittest.main()
