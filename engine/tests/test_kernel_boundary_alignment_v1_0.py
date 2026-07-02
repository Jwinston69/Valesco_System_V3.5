import ast
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _module_ast(relative_path: str) -> ast.Module:
    return ast.parse((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


def _function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Function {name!r} not found")


def _load_function(relative_path: str, name: str):
    function_def = _function_node(_module_ast(relative_path), name)
    module = ast.Module(body=[function_def], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"Dict": dict, "Any": object}
    exec(compile(module, relative_path, "exec"), namespace)
    return namespace[name]


def _called_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


def _imported_module_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[-1])
            for alias in node.names:
                roots.add(alias.name)
    return roots


class TestKernelBoundaryAlignmentV10(unittest.TestCase):
    def test_valid_validator_output_wrapped_consistently_with_payload(self) -> None:
        run_valesco_wrap = _load_function("run_valesco.py", "_wrap_validator_output")
        mvp_wrap = _load_function("engine/scripts/mvp_runner_v2_2.py", "_wrap_validator_output")
        core_result = {"valid": True, "violation_code": None, "message": "OK"}
        architect_output = {"state_id": "A", "items_presented": []}

        expected = {
            "valid": True,
            "violation_code": None,
            "message": "OK",
            "payload": architect_output,
        }

        self.assertEqual(run_valesco_wrap(core_result, architect_output), expected)
        self.assertEqual(mvp_wrap(core_result, architect_output), expected)

    def test_invalid_validator_output_is_not_overwritten(self) -> None:
        run_valesco_wrap = _load_function("run_valesco.py", "_wrap_validator_output")
        mvp_wrap = _load_function("engine/scripts/mvp_runner_v2_2.py", "_wrap_validator_output")
        invalid_result = {
            "valid": False,
            "violation_code": "STATE_MISMATCH_A",
            "message": "Invalid Router/Architect output",
        }
        architect_output = {"state_id": "A"}

        self.assertIs(run_valesco_wrap(invalid_result, architect_output), invalid_result)
        self.assertIs(mvp_wrap(invalid_result, architect_output), invalid_result)

    def test_estimator_runtime_step_does_not_invoke_pre_or_post_kernel_layers(self) -> None:
        tree = _module_ast("engine/modules/estimator_runtime_v2_1.py")
        runtime_step = _function_node(tree, "estimator_runtime_step")

        forbidden_calls = {
            "retrieve",
            "retrieve_signals",
            "set_quantity",
            "clear_quantity",
            "apply_quantities",
            "price_line_item",
            "price_estimate_snapshot",
            "price_estimate_for_runner",
            "estimator_runtime_price_snapshot",
            "estimator_runtime_resource_step",
        }

        self.assertTrue(forbidden_calls.isdisjoint(_called_names(runtime_step)))

    def test_kernel_modules_do_not_import_or_call_ce_pricing_or_quantity_layers(self) -> None:
        forbidden_names = {
            "ce_retrieval_layer_v2_1",
            "retrieve",
            "pricing_engine_v3_4",
            "pricing_logic_v2_1",
            "quantity_logic_v2_1",
            "set_quantity",
            "clear_quantity",
            "apply_quantities",
            "price_line_item",
            "price_estimate_snapshot",
            "price_estimate_for_runner",
        }

        for relative_path in (
            "engine/modules/router_v2_1.py",
            "engine/modules/architect_v2_1.py",
            "engine/modules/validator_v2_1.py",
        ):
            with self.subTest(relative_path=relative_path):
                tree = _module_ast(relative_path)
                names = _imported_module_roots(tree) | _called_names(tree)
                self.assertTrue(forbidden_names.isdisjoint(names))

    def test_mvp_pricing_only_runs_from_explicit_price_command_after_snapshot_check(self) -> None:
        tree = _module_ast("engine/scripts/mvp_runner_v2_2.py")
        run_single_item = _function_node(tree, "_run_single_item")
        run_programmatic = _function_node(tree, "run_mvp_case_programmatic")
        print_pricing = _function_node(tree, "_print_pricing")
        main = _function_node(tree, "main")

        pricing_calls = {"_print_pricing", "apply_quantities", "estimator_runtime_price_snapshot"}

        self.assertTrue(pricing_calls.isdisjoint(_called_names(run_single_item)))
        self.assertTrue(pricing_calls.isdisjoint(_called_names(run_programmatic)))

        print_pricing_calls = _called_names(print_pricing)
        self.assertIn("get_estimate_snapshot", print_pricing_calls)
        self.assertIn("apply_quantities", print_pricing_calls)
        self.assertIn("estimator_runtime_price_snapshot", print_pricing_calls)

        price_command_calls = 0
        for node in ast.walk(main):
            if not isinstance(node, ast.If):
                continue
            comparison = ast.unparse(node.test)
            branch_calls = set()
            for statement in node.body:
                branch_calls |= _called_names(statement)
            if comparison == "lower == 'price'" and "_print_pricing" in branch_calls:
                price_command_calls += 1

        self.assertEqual(price_command_calls, 1)


if __name__ == "__main__":
    unittest.main()
