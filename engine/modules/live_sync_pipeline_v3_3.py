# C:/Valesco_System/engine/modules/live_sync_pipeline_v3.3.py
# Live Catalog / Rate Sync Pipeline v3.3
#
# Purpose:
#   Deterministic synchronization pipeline for:
#     - Pulling real catalog data and rate library data (as raw lists)
#     - Passing them through ingestion pipelines
#     - Building internal catalogs and rate libraries
#     - Exporting CE-ready payloads via CE backend adapter
#
# Behaviour:
#   - No CE calls
#   - No inference or enrichment
#   - Pure sync → ingest → normalize → export
#   - Deterministic, no stateful caches
#
# Public API:
#   sync_catalog(raw_catalog_list: list, output_path: str) -> dict
#   sync_rate_library(raw_rate_list: list, output_path: str) -> dict
#   sync_all(raw_catalog_list, raw_rate_list, base_output_path: str) -> dict

from typing import Any, Dict, List

import os

from engine.modules.catalog_ingestion_v3_0 import (
    load_raw_catalog,
    build_internal_catalog,
    save_internal_catalog,
)
from engine.modules.rate_library_ingestion_v3_1 import (
    load_raw_rate_library,
    build_internal_rate_library,
    save_internal_rate_library,
)
from engine.modules.ce_backend_adapter_v3_2 import (
    to_ce_backend_catalog,
    export_ce_backend_payload,
)

InternalCatalog = Dict[str, Dict[str, Any]]
InternalRateLibrary = Dict[str, Dict[str, Any]]


# ---------------------------------------------------------------------------
# API Function 1 — Catalog sync
# ---------------------------------------------------------------------------

def sync_catalog(raw_catalog_list: List[Dict[str, Any]], output_path: str) -> InternalCatalog:
    """
    Synchronize catalog data:

        1. Validate raw list type.
        2. Ingest via load_raw_catalog (schema validation).
        3. Build internal catalog via build_internal_catalog.
        4. Save internal catalog to disk at `output_path`.
        5. Convert internal catalog to CE backend format via adapter.
        6. Save CE payload to disk at `output_path + "_ce.json"`.
        7. Return internal catalog dict.

    Deterministic rules:
        - No enrichment or inference.
        - Fail fast on malformed data (ValueError from ingestion/adapter).
        - No dynamic metadata injection.
    """
    if not isinstance(raw_catalog_list, list):
        raise ValueError("raw_catalog_list must be a list of catalog item dicts.")

    # Step 2: ingestion (validates structure and normalizes)
    normalized_list = load_raw_catalog(raw_catalog_list)

    # Step 3: build internal catalog dict
    internal_catalog: InternalCatalog = build_internal_catalog(normalized_list)

    # Step 4: save internal catalog
    save_internal_catalog(internal_catalog, output_path)

    # Step 5: convert to CE backend format
    ce_catalog_list = to_ce_backend_catalog(internal_catalog)

    # Step 6: save CE-ready payload
    ce_output_path = f"{output_path}_ce.json"
    export_ce_backend_payload(ce_catalog_list, ce_output_path)

    # Step 7: return internal catalog
    return internal_catalog


# ---------------------------------------------------------------------------
# API Function 2 — Rate library sync
# ---------------------------------------------------------------------------

def sync_rate_library(raw_rate_list: List[Dict[str, Any]], output_path: str) -> InternalRateLibrary:
    """
    Synchronize rate library data:

        1. Validate raw list type.
        2. Ingest via load_raw_rate_library.
        3. Build internal rate library via build_internal_rate_library.
        4. Save internal rate library to disk at `output_path`.
        5. Return internal rate library dict.

    Notes:
        - Rates are not exported to CE (pricing-only concern).
        - All schema checks and validation are delegated to ingestion layer.
    """
    if not isinstance(raw_rate_list, list):
        raise ValueError("raw_rate_list must be a list of rate record dicts.")

    normalized_rates = load_raw_rate_library(raw_rate_list)
    internal_rates: InternalRateLibrary = build_internal_rate_library(normalized_rates)

    save_internal_rate_library(internal_rates, output_path)

    return internal_rates


# ---------------------------------------------------------------------------
# API Function 3 — Combined sync
# ---------------------------------------------------------------------------

def sync_all(
    raw_catalog_list: List[Dict[str, Any]],
    raw_rate_list: List[Dict[str, Any]],
    base_output_path: str,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Synchronize both catalog and rate library in one deterministic operation.

    Steps:
        - Derive separate output paths from base_output_path:
            catalog_path = base_output_path + "_catalog.json"
            rates_path   = base_output_path + "_rates.json"
        - Call sync_catalog(raw_catalog_list, catalog_path)
        - Call sync_rate_library(raw_rate_list, rates_path)
        - Return:
            {
              "catalog": internal_catalog,
              "rates": internal_rate_library
            }

    Deterministic requirements:
        - No cross-dependency between catalog and rate sync.
        - No ordering side-effects beyond the explicit call order.
        - No cache or hidden state retention.
    """
    if not isinstance(base_output_path, str) or not base_output_path:
        raise ValueError("base_output_path must be a non-empty string.")

    directory = os.path.dirname(base_output_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    catalog_output_path = f"{base_output_path}_catalog.json"
    rates_output_path = f"{base_output_path}_rates.json"

    internal_catalog = sync_catalog(raw_catalog_list, catalog_output_path)
    internal_rates = sync_rate_library(raw_rate_list, rates_output_path)

    return {
        "catalog": internal_catalog,
        "rates": internal_rates,
    }


# ---------------------------------------------------------------------------
# Optional deterministic smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example raw catalog and rate data for local verification only.
    example_catalog_raw = [
        {
            "id": "A001",
            "name": "Example Product 1",
            "category": "wall",
            "attributes": {"thickness": "100mm"},
        },
        {
            "id": "A002",
            "name": "Example Product 2",
            "category": "wall",
            "attributes": {"finish": "galvanised"},
        },
    ]

    example_rates_raw = [
        {
            "id": "R001",
            "description": "Rate for A001",
            "components": {
                "material": {"rate": 4.2, "unit": "m2"},
                "labour": {"rate": 6.5, "unit": "m2"},
                "plant": {"rate": 0.0, "unit": "m2"},
            },
        }
    ]

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "live_sync")
        result = sync_all(example_catalog_raw, example_rates_raw, base_path)
        print("Sync result (internal structures):", result)
