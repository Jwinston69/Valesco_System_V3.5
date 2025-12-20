# C:/Valesco_System/engine/modules/resource_builder.py
# Resource Builder v1.0 — Provisional resource grouping (no pricing).
#
# Purpose:
#   - Convert ELI v1.0 provisional outputs into provisional resource groupings.
#   - Preserve traceability back to ELI sources.
#
# Constraints:
#   - No pricing, validation, or cross-subsystem calls.
#   - Deterministic, idempotent, side-effect free.

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Dict, List, Optional
import copy
import re

_QUOTED_EXCERPT_RE = re.compile(r"'([^']+)'")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_UNIT_RE = re.compile(
    r"\b(m2|m3|sqm|sq\.?m|sqft|ft2|ft|m|mm|cm|km|lm|ea|each|pcs|pc|unit|units|"
    r"kg|g|tonne|tonnes|t|hr|hour|hours|day|days|week|weeks|month|months|ls|"
    r"lump\s*sum)\b",
    re.IGNORECASE,
)

_PLANT_KEYWORDS = (
    "crane",
    "excavator",
    "lift",
    "hoist",
    "scaffold",
    "scaffolding",
    "forklift",
    "generator",
    "compressor",
    "plant",
    "equipment",
    "machine",
    "machinery",
)

_MATERIAL_KEYWORDS = (
    "tile",
    "tiles",
    "concrete",
    "cement",
    "brick",
    "block",
    "steel",
    "rebar",
    "timber",
    "wood",
    "pipe",
    "duct",
    "cable",
    "primer",
    "adhesive",
    "glass",
    "gypsum",
    "plasterboard",
    "board",
    "aggregate",
    "insulation",
    "membrane",
    "sealant",
    "fixing",
    "screw",
    "bolt",
)

_LABOUR_KEYWORDS = (
    "install",
    "installation",
    "fit",
    "fitting",
    "fix",
    "fixing",
    "paint",
    "painting",
    "plaster",
    "plastering",
    "demolition",
    "remove",
    "removal",
    "strip",
    "apply",
    "application",
    "labour",
    "labor",
    "wiring",
    "cabling",
    "survey",
    "test",
    "testing",
    "commission",
    "commissioning",
    "setup",
    "set-up",
    "erect",
    "construct",
    "build",
    "assemble",
    "assembly",
    "lay",
    "laying",
)

_CATEGORY_LABELS = {
    "labour": "general labour",
    "plant": "general plant",
    "materials": "general materials",
}


def build_resources(eli_output: Any, ce_output: Optional[Any] = None) -> Dict[str, Any]:
    """
    Build provisional resource groupings from ELI v1.0 outputs.

    Inputs:
        eli_output: list of ELI gap records (read-only)
        ce_output: optional CE context (read-only, not used for pricing)
    Output:
        {
            "labour": [...],
            "plant": [...],
            "materials": [...],
            "assumptions": [...],
            "all_provisional": True
        }
    """
    records = _normalize_eli_output(eli_output)

    labour: List[Dict[str, Any]] = []
    plant: List[Dict[str, Any]] = []
    materials: List[Dict[str, Any]] = []
    assumptions: List[Dict[str, Any]] = []

    for index, record in enumerate(records, start=1):
        traceability = _build_traceability(record, index)
        assumptions.append(
            {
                "assumption": _assumption_text(record),
                "traceability": copy.deepcopy(traceability),
                "provisional": True,
            }
        )

        excerpt = _extract_excerpt(record)
        category = _classify_excerpt(excerpt)
        if category is None:
            continue

        entry = {
            "category": _CATEGORY_LABELS[category],
            "description": _resource_description(excerpt, category),
            "indicative_range": "unspecified",
            "traceability": copy.deepcopy(traceability),
            "provisional": True,
        }

        if category == "labour":
            labour.append(entry)
        elif category == "plant":
            plant.append(entry)
        elif category == "materials":
            materials.append(entry)

    if ce_output is not None:
        assumptions.append(
            {
                "assumption": "CE context supplied for reference only; no pricing or validation applied.",
                "traceability": {"source": "ce_output"},
                "provisional": True,
            }
        )

    return {
        "labour": labour,
        "plant": plant,
        "materials": materials,
        "assumptions": assumptions,
        "all_provisional": True,
    }


def _normalize_eli_output(eli_output: Any) -> List[Dict[str, Any]]:
    if eli_output is None:
        return []
    if isinstance(eli_output, dict):
        if "eli_output" in eli_output and isinstance(eli_output["eli_output"], Sequence):
            return list(eli_output["eli_output"])
        if "items" in eli_output and isinstance(eli_output["items"], Sequence):
            return list(eli_output["items"])
        if "detected_gap_type" in eli_output:
            return [eli_output]
        return []
    if isinstance(eli_output, Sequence) and not isinstance(eli_output, (str, bytes, bytearray)):
        return list(eli_output)
    raise TypeError("eli_output must be a list of records or a compatible container.")


def _build_traceability(record: Dict[str, Any], index: int) -> Dict[str, Any]:
    source_ref = record.get("source_ref")
    source_ref_copy = dict(source_ref) if isinstance(source_ref, dict) else {}
    return {
        "eli_index": index,
        "eli_source_ref": source_ref_copy,
        "eli_gap_type": record.get("detected_gap_type"),
        "eli_missing_item_state": record.get("missing_item_state"),
        "eli_confidence": record.get("confidence_flag"),
    }


def _extract_excerpt(record: Dict[str, Any]) -> str:
    for key in ("provisional_resource_hint", "traceability_note"):
        value = record.get(key)
        if not isinstance(value, str):
            continue
        match = _QUOTED_EXCERPT_RE.search(value)
        if match:
            return match.group(1)
        if value:
            return value
    return str(record.get("detected_gap_type") or "unspecified")


def _classify_excerpt(excerpt: str) -> Optional[str]:
    text = excerpt.lower()
    if any(keyword in text for keyword in _PLANT_KEYWORDS):
        return "plant"
    if any(keyword in text for keyword in _LABOUR_KEYWORDS):
        return "labour"
    if any(keyword in text for keyword in _MATERIAL_KEYWORDS):
        return "materials"
    return None


def _resource_description(excerpt: str, category: str) -> str:
    cleaned = _sanitize_excerpt(excerpt)
    if cleaned:
        return cleaned
    return f"{_CATEGORY_LABELS[category]} scope"


def _sanitize_excerpt(excerpt: str) -> str:
    no_numbers = _NUMBER_RE.sub("", excerpt)
    no_units = _UNIT_RE.sub("", no_numbers)
    cleaned = " ".join(no_units.split())
    return cleaned.strip(" -,:;")


def _assumption_text(record: Dict[str, Any]) -> str:
    gap_type = record.get("detected_gap_type") or "unspecified gap"
    state = record.get("missing_item_state")
    confidence = record.get("confidence_flag")
    parts = [f"Provisional resource grouping based on {gap_type}."]
    if state:
        parts.append(f"Missing item state {state}.")
    if confidence:
        parts.append(f"Confidence {confidence}.")
    return " ".join(parts)
