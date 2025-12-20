# C:/Valesco_System/engine/build/system_packaging_v4.0_rc.py
# Valesco v4.0-RC System Packaging Script
#
# Purpose:
#   Assemble all validated modules and tests into a deterministic deployable bundle.
#
# Behaviour:
#   - Pure packaging and metadata reflection.
#   - No behaviour changes to CE, estimator, pricing, or any runtime logic.
#   - No test execution.
#   - No code modification — files are copied verbatim.
#
# Public API:
#   collect_modules(output_dir: str) -> dict
#   collect_tests(output_dir: str) -> dict
#   generate_manifest(output_dir: str) -> dict
#   run_packaging(output_dir: str) -> dict

import os
import shutil
import json
from datetime import datetime
from typing import Dict, List, Any

#"%REAL_ROOT%\engine\python_runtime\python.exe" system_packaging_v4.0_rc.py

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_engine_root() -> str:
    """
    Resolve the engine root directory from this script location.

    Assumes this file lives in:
        C:/Valesco_System/engine/build/system_packaging_v4.0_rc.py

    Returns:
        C:/Valesco_System/engine
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(this_dir, ".."))


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. collect_modules
# ---------------------------------------------------------------------------

def collect_modules(output_dir: str) -> Dict[str, List[str]]:
    """
    Copy all runtime modules into a clean build folder.

    Modules included:

        engine/modules/estimator_runtime_v2_1.py
        engine/modules/ce_retrieval_layer_v2_1.py
        engine/modules/router_v2_1.py
        engine/modules/architect_v2_1.py
        engine/modules/validator_v2_1.py
        engine/modules/merge_agent_v2_1.py
        engine/modules/material_manager_v2_1.py
        engine/modules/pricing_engine_v3_4.py
        engine/modules/rate_library_ingestion_v3_1.py
        engine/modules/rate_retrieval_v3_2.py
        engine/modules/rate_build_up_v3_3.py
        engine/modules/assembly_pack_resolver_v3_2.py
        engine/modules/pack_ingestion_v3_1.py
        engine/modules/catalog_ingestion_v3_0.py
        engine/modules/catalog_ce_adapter_v3_1.py
        engine/modules/ce_backend_adapter_v3_2.py
        engine/modules/live_sync_pipeline_v3_3.py
        engine/modules/error_handling_v4_0.py
        engine/modules/logging_telemetry_v4_1.py
        engine/modules/performance_optimisation_v4_2.py
        engine/scripts/mvp_runner_v2_2.py

    Rules:
        - Validate existence of each file.
        - Copy deterministically into output_dir/modules and output_dir/scripts.
        - Never modify files.
        - Return dict of copied destination paths.
    """
    engine_root = _get_engine_root()

    modules_src_dir = os.path.join(engine_root, "modules")
    scripts_src_dir = os.path.join(engine_root, "scripts")

    modules_dst_dir = os.path.join(output_dir, "modules")
    scripts_dst_dir = os.path.join(output_dir, "scripts")

    _ensure_dir(modules_dst_dir)
    _ensure_dir(scripts_dst_dir)

    module_files = [
    "estimator_runtime_v2_1.py",
    "ce_retrieval_layer_v2_1.py",
    "router_v2_1.py",
    "architect_v2_1.py",
    "validator_v2_1.py",
    "merge_agent_v2_1.py",
    "material_manager_v2_1.py",
    "pricing_engine_v3_4.py",
    "rate_library_ingestion_v3_1.py",
    "rate_retrieval_v3_2.py",
    "rate_build_up_v3_3.py",
    "assembly_pack_resolver_v3_2.py",
    "pack_ingestion_v3_1.py",
    "catalog_ingestion_v3_0.py",
    "catalog_ce_adapter_v3_1.py",
    "ce_backend_adapter_v3_2.py",
    "live_sync_pipeline_v3_3.py",
    "error_handling_v4_0.py",
    "logging_telemetry_v4_1.py",
    "performance_optimisation_v4_2.py",
]

    script_files = [
        "mvp_runner_v2_2.py",
    ]

    copied_paths: List[str] = []

    # Copy modules
    for name in module_files:
        src = os.path.join(modules_src_dir, name)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Required module not found: {src}")
        dst = os.path.join(modules_dst_dir, name)
        shutil.copy2(src, dst)
        copied_paths.append(os.path.abspath(dst))

    # Copy scripts
    for name in script_files:
        src = os.path.join(scripts_src_dir, name)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Required script not found: {src}")
        dst = os.path.join(scripts_dst_dir, name)
        shutil.copy2(src, dst)
        copied_paths.append(os.path.abspath(dst))

    return {"modules": copied_paths}


# ---------------------------------------------------------------------------
# 2. collect_tests
# ---------------------------------------------------------------------------

def collect_tests(output_dir: str) -> Dict[str, List[str]]:
    """
    Copy all test suites into a parallel folder.

    Behaviour:
        - Discover all *.py files in engine/tests (non-recursive).
        - Validate each exists (by nature of discovery).
        - Copy into output_dir/tests.
        - Preserve deterministic ordering by sorting filenames.
        - Do not modify any test file.

    Returns:
        {"tests": [<absolute destination paths>]}
    """
    engine_root = _get_engine_root()
    tests_src_dir = os.path.join(engine_root, "tests")
    tests_dst_dir = os.path.join(output_dir, "tests")

    _ensure_dir(tests_dst_dir)

    if not os.path.isdir(tests_src_dir):
        # If tests directory is missing entirely, treat as packaging failure.
        raise FileNotFoundError(f"Tests directory not found: {tests_src_dir}")

    test_files = sorted(
        f for f in os.listdir(tests_src_dir)
        if f.endswith(".py") and os.path.isfile(os.path.join(tests_src_dir, f))
    )

    copied_paths: List[str] = []

    for name in test_files:
        src = os.path.join(tests_src_dir, name)
        dst = os.path.join(tests_dst_dir, name)
        shutil.copy2(src, dst)
        copied_paths.append(os.path.abspath(dst))

    return {"tests": copied_paths}


# ---------------------------------------------------------------------------
# 3. generate_manifest
# ---------------------------------------------------------------------------

def generate_manifest(output_dir: str) -> Dict[str, Any]:
    """
    Generate a deterministic manifest describing the packaged system.

    Manifest schema:

        {
            "version": "4.0-rc",
            "modules": [...],        # sorted list of relative paths
            "tests":   [...],        # sorted list of relative paths
            "build_timestamp": "<UTC ISO8601>"
        }

    Behaviour:
        - Reflects only files present in output_dir/modules, output_dir/scripts,
          and output_dir/tests.
        - Deterministic ordering (sorted lexicographically).
        - No enrichment or inference beyond the required timestamp.
    """
    modules_entries: List[str] = []
    tests_entries: List[str] = []

    modules_root = os.path.join(output_dir, "modules")
    scripts_root = os.path.join(output_dir, "scripts")
    tests_root = os.path.join(output_dir, "tests")

    # Collect module + script paths relative to output_dir
    if os.path.isdir(modules_root):
        for name in sorted(os.listdir(modules_root)):
            full = os.path.join(modules_root, name)
            if os.path.isfile(full):
                rel = os.path.relpath(full, output_dir)
                modules_entries.append(rel)

    if os.path.isdir(scripts_root):
        for name in sorted(os.listdir(scripts_root)):
            full = os.path.join(scripts_root, name)
            if os.path.isfile(full):
                rel = os.path.relpath(full, output_dir)
                modules_entries.append(rel)

    # Collect test paths
    if os.path.isdir(tests_root):
        for name in sorted(os.listdir(tests_root)):
            full = os.path.join(tests_root, name)
            if os.path.isfile(full):
                rel = os.path.relpath(full, output_dir)
                tests_entries.append(rel)

    manifest = {
        "version": "4.0-rc",
        "modules": modules_entries,
        "tests": tests_entries,
        "build_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    return manifest


# ---------------------------------------------------------------------------
# 4. run_packaging
# ---------------------------------------------------------------------------

def run_packaging(output_dir: str) -> Dict[str, Any]:
    """
    Execute the full packaging routine.

    Steps:
        1. Create clean directory at output_dir (remove if exists).
        2. Call collect_modules(output_dir).
        3. Call collect_tests(output_dir).
        4. Call generate_manifest(output_dir).
        5. Save manifest.json into output_dir.
        6. Return a summary dict with version, modules, tests, and output_dir.

    Behaviour:
        - Does not execute modules or tests.
        - Does not modify any code files.
        - Only copies and describes artifacts.
    """
    abs_output_dir = os.path.abspath(output_dir)

    # Clean directory
    if os.path.isdir(abs_output_dir):
        shutil.rmtree(abs_output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)

    modules_info = collect_modules(abs_output_dir)
    tests_info = collect_tests(abs_output_dir)

    manifest = generate_manifest(abs_output_dir)

    manifest_path = os.path.join(abs_output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    summary = {
        "output_dir": abs_output_dir,
        "version": manifest["version"],
        "modules": manifest["modules"],
        "tests": manifest["tests"],
        "manifest_path": manifest_path,
    }

    return summary


# ---------------------------------------------------------------------------
# Optional CLI entrypoint for manual packaging
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Valesco v4.0-RC System Packaging")
    parser.add_argument(
        "output_dir",
        help="Output directory for the v4.0-RC packaged bundle.",
    )
    args = parser.parse_args()

    result = run_packaging(args.output_dir)
    print("Packaging complete.")
    print("Output directory:", result["output_dir"])
    print("Manifest:", result["manifest_path"])
