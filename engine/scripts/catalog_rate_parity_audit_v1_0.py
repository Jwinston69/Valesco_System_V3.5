#!/usr/bin/env python3
"""
Catalog / Rate Parity Audit v1.0 (offline, fixture-driven)

Validates identifier alignment between:
  - internal catalog IDs (dict keys)
  - CE backend catalog IDs (list of dicts with "id")
  - rate library IDs (dict keys)

Exit codes:
  0 = parity satisfied
  2 = parity violations detected
  1 = usage, argument, or I/O error
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, List, Set


def _read_json(path: str) -> object:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc.msg}") from exc
    except OSError as exc:
        raise ValueError(f"I/O error reading {path}: {exc}") from exc


def _collect_internal_ids(data: object) -> Set[str]:
    if not isinstance(data, dict):
        raise ValueError("Internal catalog must be a JSON object mapping ids to records.")
    ids: Set[str] = set()
    for key in data.keys():
        if not isinstance(key, str) or not key:
            raise ValueError("Internal catalog id keys must be non-empty strings.")
        ids.add(key)
    return ids


def _collect_ce_ids(data: object) -> Set[str]:
    if not isinstance(data, list):
        raise ValueError("CE catalog must be a JSON list of items.")
    ids: List[str] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"CE catalog item at index {idx} must be an object.")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"CE catalog item at index {idx} missing valid 'id'.")
        ids.append(item_id)
    duplicates = _find_duplicates(ids)
    if duplicates:
        raise ValueError(f"CE catalog contains duplicate ids: {', '.join(duplicates)}")
    return set(ids)


def _collect_rate_ids(data: object) -> Set[str]:
    if not isinstance(data, dict):
        raise ValueError("Rate library must be a JSON object mapping ids to records.")
    ids: Set[str] = set()
    for key in data.keys():
        if not isinstance(key, str) or not key:
            raise ValueError("Rate library id keys must be non-empty strings.")
        ids.add(key)
    return ids


def _find_duplicates(values: Iterable[str]) -> List[str]:
    seen = set()
    duplicates = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _format_id_list(values: Iterable[str]) -> str:
    return json.dumps(sorted(values))


def _print_summary(internal_ids: Set[str], ce_ids: Set[str], rate_ids: Set[str]) -> None:
    print(f"internal_count={len(internal_ids)}")
    print(f"ce_count={len(ce_ids)}")
    print(f"rate_count={len(rate_ids)}")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Audit parity between internal catalog, CE catalog, and rate library IDs.",
    )
    parser.add_argument("--internal-catalog", required=True, help="Path to internal catalog JSON.")
    parser.add_argument("--ce-catalog", required=True, help="Path to CE backend catalog JSON.")
    parser.add_argument("--rate-library", required=True, help="Path to rate library JSON.")
    parser.add_argument(
        "--no-orphan-rates",
        action="store_true",
        help="Treat extra rate IDs as parity failures.",
    )

    try:
        args = parser.parse_args(argv)
        internal_data = _read_json(args.internal_catalog)
        ce_data = _read_json(args.ce_catalog)
        rate_data = _read_json(args.rate_library)

        internal_ids = _collect_internal_ids(internal_data)
        ce_ids = _collect_ce_ids(ce_data)
        rate_ids = _collect_rate_ids(rate_data)
    except ValueError as exc:
        print(f"PARITY_ERROR: {exc}")
        return 1

    missing_in_ce = sorted(internal_ids - ce_ids)
    missing_in_internal = sorted(ce_ids - internal_ids)
    missing_in_rates = sorted(internal_ids - rate_ids)
    orphan_rate_ids = sorted(rate_ids - internal_ids)

    violations = bool(missing_in_ce or missing_in_internal or missing_in_rates)
    if args.no_orphan_rates and orphan_rate_ids:
        violations = True

    if violations:
        print("PARITY_VIOLATIONS")
        print(f"missing_in_ce: {_format_id_list(missing_in_ce)}")
        print(f"missing_in_internal: {_format_id_list(missing_in_internal)}")
        print(f"missing_in_rates: {_format_id_list(missing_in_rates)}")
        print(f"orphan_rate_ids: {_format_id_list(orphan_rate_ids)}")
        _print_summary(internal_ids, ce_ids, rate_ids)
        return 2

    print("PARITY_OK")
    _print_summary(internal_ids, ce_ids, rate_ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
