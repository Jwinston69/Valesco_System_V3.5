# C:/Valesco_System/engine/tests/performance_optimisation_test_suite_v4.2.py
# Performance Optimisation Test Suite v4.2
#
# Validates:
#   - cached_deepcopy correctness and per-call cache isolation
#   - sort_by_id determinism and non-mutation
#   - batch_apply ordering, determinism, non-mutation, and exception propagation
#   - No inference, no behavioural change, no CE/Estimator impact
#
# Required test count: 12

import unittest
import copy

from engine.modules.performance_optimisation_v4_2 import (
    cached_deepcopy,
    sort_by_id,
    batch_apply,
)


# ---------------------------------------------------------------------------
# GROUP A — cached_deepcopy (5 tests)
# ---------------------------------------------------------------------------

class TestCachedDeepcopy(unittest.TestCase):

    def test_1_primitives_return_themselves(self):
        # Primitive immutables should return themselves
        self.assertIs(cached_deepcopy(5), 5)
        self.assertIs(cached_deepcopy(2.5), 2.5)
        self.assertIs(cached_deepcopy("abc"), "abc")
        self.assertIs(cached_deepcopy(True), True)
        self.assertIs(cached_deepcopy(None), None)

    def test_2_tuple_deepcopy_with_caching(self):
        t = (1, (2, 3), (2, 3))
        result = cached_deepcopy(t)

        # Structure correct
        self.assertEqual(result, t)
        # Tuple is new object
        self.assertIsNot(result, t)
        # Sub-elements deep-copied but identical structure
        self.assertEqual(result[1], t[1])
        self.assertIsNot(result[1], t[1])
        # Repeated inner tuples should be identical objects within a *single call*
        # because of caching: (result[1] is result[2])
        self.assertIs(result[1], result[2])

    def test_3_frozenset_deepcopy(self):
        fs = frozenset([1, 2, 3])
        out = cached_deepcopy(fs)
        self.assertEqual(out, fs)
        self.assertIsNot(out, fs)

    def test_4_mutable_structures_bypass_cache(self):
        l = [1, 2, 3]
        d = {"a": 1}
        s = {1, 2}

        l_out = cached_deepcopy(l)
        d_out = cached_deepcopy(d)
        s_out = cached_deepcopy(s)

        self.assertEqual(l_out, l)
        self.assertIsNot(l_out, l)

        self.assertEqual(d_out, d)
        self.assertIsNot(d_out, d)

        self.assertEqual(s_out, s)
        self.assertIsNot(s_out, s)

    def test_5_no_cache_leak_between_calls(self):
        t = (1, (2, 3))
        a = cached_deepcopy(t)
        b = cached_deepcopy(t)
        # fresh call cache, so repeated sub-tuples should not share identity across calls
        self.assertEqual(a, b)
        self.assertIsNot(a, b)
        self.assertIsNot(a[1], b[1])


# ---------------------------------------------------------------------------
# GROUP B — sort_by_id (4 tests)
# ---------------------------------------------------------------------------

class TestSortById(unittest.TestCase):

    def test_6_sorted_deterministically(self):
        records = [
            {"id": "C"},
            {"id": "A"},
            {"id": "B"},
        ]
        sorted_records = sort_by_id(records)
        self.assertEqual([r["id"] for r in sorted_records], ["A", "B", "C"])

    def test_7_missing_id_raises(self):
        with self.assertRaises(ValueError):
            sort_by_id([{"name": "bad"}])

    def test_8_non_dict_element_raises(self):
        with self.assertRaises(ValueError):
            sort_by_id([{"id": "OK"}, "not_a_dict"])

    def test_9_input_list_not_mutated(self):
        records = [{"id": "B"}, {"id": "A"}]
        original = copy.deepcopy(records)
        sort_by_id(records)
        self.assertEqual(records, original)


# ---------------------------------------------------------------------------
# GROUP C — batch_apply (3 tests)
# ---------------------------------------------------------------------------

class TestBatchApply(unittest.TestCase):

    def test_10_applies_function_in_order(self):
        items = [1, 2, 3]
        out = batch_apply(lambda x: x * 2, items)
        self.assertEqual(out, [2, 4, 6])

    def test_11_does_not_mutate_input(self):
        items = [1, 2, 3]
        orig = items[:]
        batch_apply(lambda x: x + 10, items)
        self.assertEqual(items, orig)

    def test_12_exceptions_propagate(self):
        def boom(x):
            raise RuntimeError("fail")

        with self.assertRaises(RuntimeError):
            batch_apply(boom, [1, 2])



if __name__ == "__main__":
    unittest.main()
