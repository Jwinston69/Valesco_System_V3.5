# C:/Valesco_System/engine/modules/eli.py
# ELI v1.0 — Extraction & Interpretation Layer
#
# Purpose:
#   - Parse BOQ / scope text inputs.
#   - Detect missing or ambiguous information.
#   - Emit provisional gap records only.
#
# Constraints:
#   - No pricing, validation, or cross-subsystem calls.
#   - No fabrication of materials or SKUs.
#   - Deterministic, idempotent, side-effect free.

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import re

_GAP_ORDER = (
    "missing_quantity",
    "missing_unit",
    "ambiguous_description",
    "undefined_specification",
)

_NUMBER_RE = re.compile(r"(?<![a-zA-Z])\d+(?:\.\d+)?")
_UNIT_RE = re.compile(
    r"\b(m2|m3|sqm|sq\.?m|sqft|ft2|ft|m|mm|cm|km|lm|ea|each|pcs|pc|unit|units|"
    r"kg|g|tonne|tonnes|t|hr|hour|hours|day|days|week|weeks|month|months|ls|"
    r"lump\s*sum)\b",
    re.IGNORECASE,
)
_NUMBER_UNIT_RE = re.compile(
    r"\d+(?:\.\d+)?\s*(m2|m3|sqm|sq\.?m|sqft|ft2|ft|m|mm|cm|km|lm|ea|each|pcs|"
    r"pc|unit|units|kg|g|tonne|tonnes|t|hr|hour|hours|day|days|week|weeks|month|"
    r"months|ls|lump\s*sum)\b",
    re.IGNORECASE,
)
_QTY_RE = re.compile(r"\b(qty|quantity|quantities)\b", re.IGNORECASE)

_AMBIGUOUS_MARKERS = (
    "tbd",
    "tbc",
    "to be determined",
    "to be confirmed",
    "unknown",
    "approx",
    "approximate",
    "as required",
    "as needed",
    "as per",
    "various",
    "misc",
    "miscellaneous",
    "allowance",
    "typical",
    "standard",
    "etc",
    "or equivalent",
    "confirm",
    "pending",
    "by others",
    "subject to",
)

_ALTERNATIVE_MARKERS = (
    "or equivalent",
    "equivalent",
    "alternative",
    "alternatives",
    "alt",
    "compatible",
    "substitute",
    "similar",
)

_VAGUE_TOKENS = {
    "misc",
    "miscellaneous",
    "various",
    "tbd",
    "tbc",
    "unknown",
    "allowance",
    "etc",
}

_OPTION_SEPARATOR_RE = re.compile(r"\b(or|either|and/or)\b", re.IGNORECASE)
_SLASH_OPTION_RE = re.compile(r"[a-zA-Z]+/[a-zA-Z]+")

_SPEC_UNDEFINED_RE = re.compile(
    r"\b(spec|specification|finish|grade|type|model|size|thickness|rating|class|"
    r"color|material)\b\s*(tbd|tbc|unknown|n/?a|to be confirmed|pending|"
    r"not specified|as per|per|$)",
    re.IGNORECASE,
)

_SPEC_KEYWORDS = {
    "spec",
    "specification",
    "finish",
    "grade",
    "type",
    "model",
    "size",
    "thickness",
    "rating",
    "class",
    "color",
    "material",
}

_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "per",
    "the",
    "to",
    "with",
}


def analyze_boq(
    raw_text: Union[str, Sequence[str]],
    metadata: Optional[Union[Dict[str, Any], Sequence[Optional[Dict[str, Any]]]]] = None,
) -> List[Dict[str, Any]]:
    """
    Parse BOQ / scope text and emit provisional gap records.

    Inputs:
        raw_text: string or list of strings
        metadata: dict or list of dicts (source, section, line_ref)
    """
    segments = _normalize_inputs(raw_text, metadata)
    outputs: List[Dict[str, Any]] = []

    for segment_text, meta, line_index, segment_index in segments:
        if not segment_text:
            continue

        gaps, context, tokens = _analyze_segment(segment_text)
        for gap_type in _GAP_ORDER:
            if not gaps.get(gap_type, False):
                continue
            outputs.append(
                _build_output(
                    gap_type=gap_type,
                    text=segment_text,
                    tokens=tokens,
                    meta=meta,
                    line_index=line_index,
                    segment_index=segment_index,
                    context=context,
                )
            )

    return outputs


def _normalize_inputs(
    raw_text: Union[str, Sequence[str]],
    metadata: Optional[Union[Dict[str, Any], Sequence[Optional[Dict[str, Any]]]]],
) -> List[Tuple[str, Dict[str, Any], int, int]]:
    lines = _coerce_lines(raw_text)
    segments: List[Tuple[str, Dict[str, Any], int, int]] = []

    for line_index, line in enumerate(lines, start=1):
        if line is None:
            continue
        line_str = str(line)
        line_meta = _line_metadata(metadata, line_index - 1)
        segment_index = 0
        for segment in _segment_line(line_str):
            segment_index += 1
            segments.append((segment, line_meta, line_index, segment_index))

    return segments


def _coerce_lines(raw_text: Union[str, Sequence[str]]) -> List[str]:
    if raw_text is None:
        return []
    if isinstance(raw_text, str):
        return raw_text.splitlines()
    if isinstance(raw_text, Sequence):
        return [str(item) for item in raw_text]
    raise TypeError("raw_text must be a string or a sequence of strings.")


def _line_metadata(
    metadata: Optional[Union[Dict[str, Any], Sequence[Optional[Dict[str, Any]]]]],
    index: int,
) -> Dict[str, Any]:
    if metadata is None:
        return {}
    if isinstance(metadata, dict):
        return dict(metadata)
    if isinstance(metadata, Sequence) and not isinstance(metadata, (str, bytes)):
        if 0 <= index < len(metadata):
            item = metadata[index]
            if isinstance(item, dict):
                return dict(item)
    return {}


def _segment_line(line: str) -> List[str]:
    return [segment.strip() for segment in line.split(";") if segment.strip()]


def _analyze_segment(text: str) -> Tuple[Dict[str, bool], Dict[str, Any], List[str]]:
    lowered = text.lower()
    tokens = _tokenize(lowered)

    has_number = bool(_NUMBER_RE.search(lowered))
    has_unit = bool(_UNIT_RE.search(lowered) or _NUMBER_UNIT_RE.search(lowered))
    has_qty_token = bool(_QTY_RE.search(lowered))

    ambiguous_marker = _find_marker(lowered, _AMBIGUOUS_MARKERS)
    alternative_marker = _find_marker(lowered, _ALTERNATIVE_MARKERS)
    has_option_separator = bool(_OPTION_SEPARATOR_RE.search(lowered) or _SLASH_OPTION_RE.search(text))
    vague_token = _find_vague_token(tokens)
    spec_undefined = bool(_SPEC_UNDEFINED_RE.search(lowered))

    missing_quantity = (not has_number) and (has_unit or has_qty_token)
    missing_unit = has_number and (not has_unit)
    ambiguous_description = bool(
        ambiguous_marker or alternative_marker or vague_token or has_option_separator
    )
    undefined_specification = bool(spec_undefined)

    gaps = {
        "missing_quantity": missing_quantity,
        "missing_unit": missing_unit,
        "ambiguous_description": ambiguous_description,
        "undefined_specification": undefined_specification,
    }

    context = {
        "ambiguous_marker": ambiguous_marker,
        "alternative_marker": alternative_marker,
        "has_option_separator": has_option_separator,
        "vague_token": vague_token,
        "has_number": has_number,
        "has_unit": has_unit,
        "has_qty_token": has_qty_token,
        "spec_undefined": spec_undefined,
    }

    return gaps, context, tokens


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _find_marker(text: str, markers: Sequence[str]) -> Optional[str]:
    for marker in markers:
        if marker in text:
            return marker
    return None


def _find_vague_token(tokens: Sequence[str]) -> Optional[str]:
    for token in tokens:
        if token in _VAGUE_TOKENS:
            return token
    return None


def _build_output(
    gap_type: str,
    text: str,
    tokens: Sequence[str],
    meta: Dict[str, Any],
    line_index: int,
    segment_index: int,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    source_ref = _build_source_ref(meta, line_index, segment_index)
    excerpt = _excerpt(text)
    missing_item_state = _missing_item_state(gap_type, tokens, context)
    confidence_flag = _confidence_flag(context)
    traceability_note = _traceability_note(gap_type, excerpt, context)
    provisional_hint = _provisional_hint(gap_type, excerpt)

    return {
        "source_ref": source_ref,
        "detected_gap_type": gap_type,
        "missing_item_state": missing_item_state,
        "provisional_resource_hint": provisional_hint,
        "confidence_flag": confidence_flag,
        "traceability_note": traceability_note,
        "provisional": True,
    }


def _build_source_ref(meta: Dict[str, Any], line_index: int, segment_index: int) -> Dict[str, Any]:
    return {
        "source": meta.get("source"),
        "section": meta.get("section"),
        "line_ref": meta.get("line_ref", f"line_{line_index}"),
        "line_index": line_index,
        "segment_index": segment_index,
    }


def _excerpt(text: str, limit: int = 80) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit]}..."


def _missing_item_state(gap_type: str, tokens: Sequence[str], context: Dict[str, Any]) -> str:
    if _is_unresolvable(tokens, context):
        return "D"
    if context.get("alternative_marker"):
        return "E"
    if context.get("has_option_separator"):
        return "B"
    if gap_type in ("missing_quantity", "missing_unit") and _is_specific(tokens, context):
        return "A"
    return "C"


def _is_unresolvable(tokens: Sequence[str], context: Dict[str, Any]) -> bool:
    if not tokens:
        return True
    content_tokens = [
        token
        for token in tokens
        if token not in _STOPWORDS
        and token not in _VAGUE_TOKENS
        and token not in _SPEC_KEYWORDS
        and not token.isdigit()
    ]
    if not content_tokens:
        return True
    if context.get("vague_token") and len(content_tokens) <= 1:
        return True
    return False


def _is_specific(tokens: Sequence[str], context: Dict[str, Any]) -> bool:
    if context.get("ambiguous_marker") or context.get("vague_token") or context.get("spec_undefined"):
        return False
    content_tokens = [
        token
        for token in tokens
        if token not in _STOPWORDS
        and token not in _VAGUE_TOKENS
        and token not in _SPEC_KEYWORDS
        and not token.isdigit()
    ]
    return len(content_tokens) >= 2


def _confidence_flag(context: Dict[str, Any]) -> str:
    if (
        context.get("ambiguous_marker")
        or context.get("alternative_marker")
        or context.get("has_option_separator")
        or context.get("vague_token")
        or context.get("has_qty_token")
        or context.get("has_number")
        or context.get("spec_undefined")
    ):
        return "medium"
    return "low"


def _traceability_note(gap_type: str, excerpt: str, context: Dict[str, Any]) -> str:
    if gap_type == "missing_quantity":
        return f"Missing quantity detected for '{excerpt}'."
    if gap_type == "missing_unit":
        return f"Missing unit detected for '{excerpt}'."
    if gap_type == "ambiguous_description":
        marker = (
            context.get("ambiguous_marker")
            or context.get("alternative_marker")
            or context.get("vague_token")
            or ("options" if context.get("has_option_separator") else None)
            or "ambiguous"
        )
        return f"Ambiguous description detected ({marker}) for '{excerpt}'."
    if gap_type == "undefined_specification":
        return f"Undefined specification detected for '{excerpt}'."
    return f"Gap detected for '{excerpt}'."


def _provisional_hint(gap_type: str, excerpt: str) -> Optional[str]:
    if gap_type == "missing_quantity":
        return f"HINT (provisional): clarify quantity for '{excerpt}'."
    if gap_type == "missing_unit":
        return f"HINT (provisional): clarify unit for '{excerpt}'."
    if gap_type == "ambiguous_description":
        return f"HINT (provisional): clarify description for '{excerpt}'."
    if gap_type == "undefined_specification":
        return f"HINT (provisional): clarify specification for '{excerpt}'."
    return None
