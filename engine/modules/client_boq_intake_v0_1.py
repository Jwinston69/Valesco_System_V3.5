"""Phase 2 client BOQ workbook intake and validation foundation.

This module is intentionally standalone. It reads artificial .xlsx fixtures,
records source traceability, validates the minimum client BOQ fields, and does
not call pricing, export, CE backend, router, architect, validator, merge, or
runtime pipeline modules.
"""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


REQUIRED_FIELDS = ("client_item_ref", "description", "unit", "quantity")

HEADER_ALIASES = {
    "client_item_ref": {
        "item",
        "item no",
        "item no.",
        "item ref",
        "item reference",
        "client item ref",
        "client item reference",
        "boq item",
        "boq ref",
    },
    "description": {
        "description",
        "item description",
        "scope description",
        "work description",
        "boq description",
    },
    "unit": {
        "unit",
        "uom",
        "unit of measure",
        "units",
    },
    "quantity": {
        "quantity",
        "qty",
        "quantities",
        "client quantity",
    },
}

EXCLUSION_HEADERS = {
    "exclude",
    "excluded",
    "row state",
    "row status",
    "include",
}

EXCLUSION_MARKERS = {"exclude", "excluded", "no", "n", "skip", "omit"}


def import_client_boq_workbook(path: str, worksheet_name: Optional[str] = None) -> Dict[str, Any]:
    """Read a client BOQ fixture workbook and return validation evidence."""
    source_file_ref = os.path.basename(os.fspath(path))
    result = _empty_result(source_file_ref)

    try:
        workbook = load_workbook(path, data_only=False, read_only=False)
    except Exception as exc:
        result["workbook_readable"] = False
        result["workbook_status"] = "fail"
        result["workbook_messages"].append(f"Workbook is not readable: {type(exc).__name__}.")
        return result

    result["workbook_readable"] = True
    result["workbook_status"] = "pass"
    result["sheets"] = [
        {"worksheet_name": sheet.title, "worksheet_index": index}
        for index, sheet in enumerate(workbook.worksheets, start=1)
    ]

    worksheet, selection_message = _select_worksheet(workbook, worksheet_name)
    if worksheet is None:
        result["workbook_status"] = "fail"
        result["workbook_messages"].append(selection_message)
        return result

    result["selected_worksheet"] = {
        "worksheet_name": worksheet.title,
        "worksheet_index": workbook.worksheets.index(worksheet) + 1,
    }

    structural_messages = _worksheet_structure_messages(worksheet)
    result["workbook_messages"].extend(structural_messages)

    header_row_number, headers = _find_header_row(worksheet)
    result["header_row_number"] = header_row_number
    if header_row_number is None:
        result["column_mapping_status"] = "fail"
        result["workbook_status"] = "fail"
        result["workbook_messages"].append("No header row found.")
        return result

    mapping, mapping_messages, mapping_status, exclusion_column = _map_columns(headers)
    result["column_mapping"] = mapping
    result["column_mapping_status"] = mapping_status
    result["column_mapping_messages"] = mapping_messages

    if mapping_status != "pass":
        result["workbook_status"] = "fail" if mapping_status == "fail" else "warning"
        result["workbook_messages"].append("Column mapping requires review before pricing readiness.")

    data_start = header_row_number + 1
    for row_number in range(data_start, worksheet.max_row + 1):
        row = _build_row_result(
            worksheet=worksheet,
            row_number=row_number,
            mapping=mapping,
            exclusion_column=exclusion_column,
            source_file_ref=source_file_ref,
        )
        if row is not None:
            result["rows"].append(row)

    if not result["rows"]:
        result["workbook_messages"].append("No BOQ data rows found.")
        result["workbook_status"] = "fail"

    if structural_messages and result["workbook_status"] == "pass":
        result["workbook_status"] = "warning"

    if any(row["validation_status"] == "fail" for row in result["rows"]):
        result["workbook_status"] = "fail"
    elif any(row["validation_status"] in {"warning", "excluded"} for row in result["rows"]):
        if result["workbook_status"] == "pass":
            result["workbook_status"] = "warning"

    return result


def _empty_result(source_file_ref: str) -> Dict[str, Any]:
    return {
        "source_file_ref": source_file_ref,
        "workbook_readable": False,
        "workbook_status": "unknown",
        "workbook_messages": [],
        "sheets": [],
        "selected_worksheet": None,
        "header_row_number": None,
        "column_mapping_status": "unknown",
        "column_mapping": {},
        "column_mapping_messages": [],
        "rows": [],
        "pricing_approval": False,
        "export_ready": False,
    }


def _select_worksheet(workbook: Any, worksheet_name: Optional[str]) -> Tuple[Any, str]:
    if worksheet_name:
        if worksheet_name in workbook.sheetnames:
            return workbook[worksheet_name], "Worksheet selected by explicit name."
        return None, f"Worksheet not found: {worksheet_name}."

    visible_sheets = [sheet for sheet in workbook.worksheets if sheet.sheet_state == "visible"]
    if not visible_sheets:
        return None, "No visible worksheet found."
    return visible_sheets[0], "First visible worksheet selected."


def _worksheet_structure_messages(worksheet: Any) -> List[str]:
    messages: List[str] = []

    hidden_rows = [
        index
        for index, dimension in worksheet.row_dimensions.items()
        if dimension.hidden
    ]
    hidden_columns = [
        column
        for column, dimension in worksheet.column_dimensions.items()
        if dimension.hidden
    ]

    if hidden_rows:
        messages.append(f"Hidden rows visible for review: {hidden_rows}.")
    if hidden_columns:
        messages.append(f"Hidden columns visible for review: {hidden_columns}.")
    if worksheet.merged_cells.ranges:
        ranges = [str(cell_range) for cell_range in worksheet.merged_cells.ranges]
        messages.append(f"Merged cells visible for review: {ranges}.")

    return messages


def _find_header_row(worksheet: Any) -> Tuple[Optional[int], Dict[int, str]]:
    max_scan = min(worksheet.max_row, 10)
    for row_number in range(1, max_scan + 1):
        headers: Dict[int, str] = {}
        for cell in worksheet[row_number]:
            value = _clean_text(cell.value)
            if value:
                headers[cell.column] = value
        if headers:
            return row_number, headers
    return None, {}


def _map_columns(
    headers: Dict[int, str]
) -> Tuple[Dict[str, Dict[str, Any]], List[str], str, Optional[int]]:
    normalized = {column: _normalize_header(header) for column, header in headers.items()}
    mapping: Dict[str, Dict[str, Any]] = {}
    messages: List[str] = []
    status = "pass"

    for field in REQUIRED_FIELDS:
        matches = [
            column
            for column, header in normalized.items()
            if header in HEADER_ALIASES[field]
        ]
        if not matches:
            status = "fail"
            messages.append(f"Missing required column for {field}.")
            continue
        if len(matches) > 1:
            if status != "fail":
                status = "review_required"
            labels = [headers[column] for column in matches]
            messages.append(f"Ambiguous column mapping for {field}: {labels}.")
        selected = matches[0]
        mapping[field] = {
            "column_index": selected,
            "column_letter": get_column_letter(selected),
            "header": headers[selected],
        }

    exclusion_matches = [
        column
        for column, header in normalized.items()
        if header in EXCLUSION_HEADERS
    ]
    exclusion_column = exclusion_matches[0] if exclusion_matches else None

    if not messages:
        messages.append("Required fixture columns mapped deterministically.")
    return mapping, messages, status, exclusion_column


def _build_row_result(
    worksheet: Any,
    row_number: int,
    mapping: Dict[str, Dict[str, Any]],
    exclusion_column: Optional[int],
    source_file_ref: str,
) -> Optional[Dict[str, Any]]:
    row_values = {
        field: _cell_value(worksheet, row_number, spec.get("column_index"))
        for field, spec in mapping.items()
    }
    if not any(_clean_text(value) for value in row_values.values()):
        return None

    messages: List[str] = []
    status = "pass"
    estimator_review_required = False
    exclusion_reason = None

    hidden_or_merged_messages = _row_structure_messages(worksheet, row_number, mapping)
    if hidden_or_merged_messages:
        status = "warning"
        estimator_review_required = True
        messages.extend(hidden_or_merged_messages)

    exclusion_value = _cell_value(worksheet, row_number, exclusion_column)
    if _is_excluded(exclusion_value):
        status = "excluded"
        exclusion_reason = "Fixture row marked as excluded."
        messages.append(exclusion_reason)

    description = row_values.get("description")
    unit = row_values.get("unit")
    quantity = row_values.get("quantity")

    if not _clean_text(description):
        status = "fail"
        estimator_review_required = True
        messages.append("Description is required and is blank or missing.")
    if not _clean_text(unit):
        status = "fail"
        estimator_review_required = True
        messages.append("Unit is required and is blank or missing.")

    quantity_status, quantity_message = _validate_quantity(quantity)
    if quantity_status != "pass":
        status = "fail"
        estimator_review_required = True
        messages.append(quantity_message)

    if not messages:
        messages.append("Required row fields passed import validation.")

    return {
        "source_file_ref": source_file_ref,
        "source_sheet_name": worksheet.title,
        "source_row_number": row_number,
        "client_item_ref": row_values.get("client_item_ref"),
        "description_original": description,
        "unit_original": unit,
        "quantity_original": quantity,
        "quantity_normalized": _normalize_quantity(quantity) if quantity_status == "pass" else None,
        "validation_status": status,
        "validation_messages": messages,
        "readiness_status": _readiness_status(status),
        "pricing_ready": False,
        "export_ready": False,
        "estimator_review_required": estimator_review_required,
        "exclusion_reason": exclusion_reason,
    }


def _row_structure_messages(
    worksheet: Any,
    row_number: int,
    mapping: Dict[str, Dict[str, Any]],
) -> List[str]:
    messages: List[str] = []
    row_dimension = worksheet.row_dimensions[row_number]
    if row_dimension.hidden:
        messages.append(f"Source row {row_number} is hidden and requires review.")

    for field, spec in mapping.items():
        column_index = spec["column_index"]
        column_letter = get_column_letter(column_index)
        if worksheet.column_dimensions[column_letter].hidden:
            messages.append(f"Mapped {field} column {column_letter} is hidden and requires review.")

        cell_ref = f"{column_letter}{row_number}"
        if _cell_is_merged(worksheet, cell_ref):
            messages.append(f"Mapped {field} cell {cell_ref} is merged and requires review.")

    return messages


def _cell_is_merged(worksheet: Any, cell_ref: str) -> bool:
    for merged_range in worksheet.merged_cells.ranges:
        if cell_ref in merged_range:
            return True
    return False


def _cell_value(worksheet: Any, row_number: int, column_index: Optional[int]) -> Any:
    if column_index is None:
        return None
    return worksheet.cell(row=row_number, column=column_index).value


def _validate_quantity(value: Any) -> Tuple[str, str]:
    if value is None:
        return "fail", "Quantity is required and is blank or missing."
    text = _clean_text(value)
    if not text:
        return "fail", "Quantity is required and is blank or missing."
    try:
        quantity = Decimal(text)
    except InvalidOperation:
        return "fail", f"Quantity is not numeric: {text}."
    if quantity < 0:
        return "fail", f"Quantity must not be negative: {text}."
    return "pass", "Quantity passed import validation."


def _normalize_quantity(value: Any) -> Optional[float]:
    try:
        return float(Decimal(_clean_text(value)))
    except (InvalidOperation, ValueError):
        return None


def _readiness_status(validation_status: str) -> str:
    if validation_status == "pass":
        return "import_valid_pricing_blocked"
    if validation_status == "excluded":
        return "excluded"
    if validation_status == "warning":
        return "review_required_pricing_blocked"
    return "blocked"


def _is_excluded(value: Any) -> bool:
    return _normalize_header(_clean_text(value)) in EXCLUSION_MARKERS


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_header(value: str) -> str:
    return " ".join(_clean_text(value).lower().replace("_", " ").split())
