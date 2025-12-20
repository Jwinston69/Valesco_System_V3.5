# C:/Valesco_System/engine/modules/logging_telemetry_v4.1.py
# Logging & Telemetry Layer v4.1
#
# Purpose:
#   Deterministic, in-memory logging and telemetry for Valesco runtime
#   operations:
#       - error-handling v4.0
#       - pricing engine v3.x
#       - pack resolver v3.2
#       - sync pipeline v3.3
#       - future runner v4.x
#
# Behaviour:
#   - No estimator/CE behaviour changes.
#   - No inference or enrichment.
#   - No external logging side effects (stdout/files/system logs).
#
# Public API:
#   log_event(level: str, event: str, details: dict | None = None) -> dict
#   get_logs() -> list[dict]
#   clear_logs() -> None
#   log_error(err_obj: dict) -> None
#
# Log record format:
#   {
#       "timestamp": str,       # ISO8601 UTC, from datetime.datetime.utcnow()
#       "level": str,           # "INFO", "WARNING", "ERROR"
#       "event": str,           # short event tag
#       "details": dict | None  # JSON-serializable, deep-copied
#   }

from typing import Any, Dict, List, Optional
from datetime import datetime
import copy
import json

__all__ = [
    "log_event",
    "get_logs",
    "clear_logs",
    "log_error",
]

# In-memory log buffer (module-level, append-only until cleared)
_LOG_BUFFER: List[Dict[str, Any]] = []


def _ensure_json_serializable(obj: Any) -> None:
    """
    Ensure that 'obj' is JSON-serializable. Raises ValueError otherwise.
    """
    try:
        json.dumps(obj)
    except Exception as exc:  # pragma: no cover (defensive)
        raise ValueError("details must be JSON-serializable.") from exc


def log_event(level: str, event: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a structured log record and append it to the in-memory buffer.

    Args:
        level: "INFO", "WARNING", or "ERROR".
        event: short event tag.
        details: optional dict with JSON-serializable extra information.

    Behaviour:
        - Validates level against allowed set.
        - Validates details type (dict or None) and JSON-serializability.
        - Deep-copies details (if provided) into the log record.
        - Does not mutate caller's details dict.
        - Returns a deep copy of the created record.
    """
    allowed_levels = {"INFO", "WARNING", "ERROR"}
    if level not in allowed_levels:
        raise ValueError(f"Invalid log level '{level}'. Allowed: {allowed_levels}.")

    if details is not None:
        if not isinstance(details, dict):
            raise ValueError("details must be a dict or None.")
        _ensure_json_serializable(details)
        details_copy = copy.deepcopy(details)
    else:
        details_copy = None

    record: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "event": event,
        "details": details_copy,
    }

    _LOG_BUFFER.append(record)

    # Return a deep copy to avoid external mutation
    return copy.deepcopy(record)


def get_logs() -> List[Dict[str, Any]]:
    """
    Return a deep-copied list of all log entries in chronological order.
    """
    return copy.deepcopy(_LOG_BUFFER)


def clear_logs() -> None:
    """
    Clear the in-memory log buffer deterministically.
    """
    _LOG_BUFFER.clear()


def log_error(err_obj: Dict[str, Any]) -> None:
    """
    Integration hook for error-handling v4.0.

    Logs a runtime exception error object as a single ERROR-level event
    without modifying the input error object.

    Schema of err_obj is expected to match error_handling_v4.0:
        {
            "error": True,
            "type": str,
            "message": str,
            "context": dict | None
        }
    """
    # Do not modify err_obj; pass it through as details (deep-copied by log_event)
    log_event("ERROR", "runtime_exception", details=err_obj)


if __name__ == "__main__":
    # Simple local smoke test (no external side effects)
    clear_logs()
    r1 = log_event("INFO", "startup", {"module": "logging_telemetry_v4.1"})
    r2 = log_event("WARNING", "config_missing", {"key": "EXAMPLE_VAR"})
    log_error({"error": True, "type": "ValueError", "message": "x", "context": None})
    print("Sample logs:", get_logs())
