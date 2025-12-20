# C:/Valesco_System/engine/modules/error_handling_v4.0.py
# Operational Error-Handling Framework v4.0
#
# Purpose:
#   - Provide a uniform, deterministic, production-safe error-handling layer
#     for runtime modules (Runner, Pricing Engine, Assembly Resolver,
#     Catalog/Rate Sync pipelines, etc.).
#   - Wrap operations safely and convert low-level exceptions into structured
#     error objects.
#
# Behaviour:
#   - No changes to CE or estimator behaviour.
#   - No enrichment or inference of information.
#   - Purely operational; no new rules or semantics.
#
# Public API:
#   - wrap(operation: callable, *, context: dict | None = None) -> Any | dict
#   - safe_call(operation: callable, *args, **kwargs) -> Any | dict
#   - log_error(err_obj: dict) -> None
#
# Error object format:
#   {
#       "error": True,
#       "type": str,       # exception class name, e.g. "ValueError"
#       "message": str,    # stringified exception message
#       "context": dict | None  # optional, only from caller
#   }

from typing import Any, Callable, Dict, Optional
from json import JSONDecodeError
import copy


__all__ = [
    "wrap",
    "safe_call",
    "log_error",
]


# ---------------------------------------------------------------------------
# Internal helper – construct error payload
# ---------------------------------------------------------------------------

def _build_error_object(exc: Exception, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Construct a deterministic error object:

        {
            "error": True,
            "type": "<ExceptionClassName>",
            "message": "<stringified exception>",
            "context": <deep copy of context or None>
        }

    Rules:
        - 'type' must match exc.__class__.__name__.
        - 'message' = str(exc).
        - 'context' is a deep copy of caller-provided context or None.
        - No inferred or synthesized fields.
    """
    ctx_copy = copy.deepcopy(context) if context is not None else None

    return {
        "error": True,
        "type": exc.__class__.__name__,
        "message": str(exc),
        "context": ctx_copy,
    }


# ---------------------------------------------------------------------------
# API Function 2 – wrap
# ---------------------------------------------------------------------------

def wrap(operation: Callable[[], Any], *, context: Optional[Dict[str, Any]] = None) -> Any:
    """
    Execute an operation and return either the normal result or a structured
    error object.

    Signature:
        wrap(operation: callable, *, context: dict | None = None) -> Any | dict

    Behaviour:
        - On success: return operation()'s result.
        - On failure with expected operational exceptions:
              ValueError, KeyError, TypeError, IOError,
              FileNotFoundError, JSONDecodeError
          => return deterministic error object.

        - On unexpected exceptions: re-raise.

    Constraints:
        - Must not mutate the context dict.
        - Must not infer or construct context automatically.
        - Must not alter CE, estimator, or pricing behaviour.
    """
    try:
        return operation()
    except (ValueError, KeyError, TypeError, IOError, FileNotFoundError, JSONDecodeError) as exc:
        return _build_error_object(exc, context)
    # Any other exceptions must propagate to allow upstream handling and
    # to avoid masking unexpected failures.


# ---------------------------------------------------------------------------
# API Function 3 – safe_call
# ---------------------------------------------------------------------------

def safe_call(
    operation: Callable[..., Any],
    *args: Any,
    context: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    """
    Helper that wraps a callable with positional and keyword arguments.

    Usage examples:
        result = safe_call(build_internal_catalog, normalized_list)

        result = safe_call(
            sync_catalog,
            raw_catalog_list,
            "/path/to/output.json",
            context={"stage": "live_sync_catalog"}
        )

    Returns:
        - operation(*args, **kwargs) on success
        - structured error object on handled failure (see wrap)
    """

    def _op() -> Any:
        return operation(*args, **kwargs)

    return wrap(_op, context=context)


# ---------------------------------------------------------------------------
# API Function 4 – logging hook (stub)
# ---------------------------------------------------------------------------

def log_error(err_obj: Dict[str, Any]) -> None:
    """
    Logging hook for error objects.

    Current behaviour:
        - Accepts error object.
        - Does not modify it.
        - Does not emit external logs yet (Phase 4.2 will implement logging).

    This function is intentionally a no-op to maintain pure operational
    behaviour in v4.0.
    """
    # Placeholder for future logging integration.
    # Intentionally no side effects in v4.0.
    return None


# ---------------------------------------------------------------------------
# Optional local smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Simple deterministic smoke checks
    def _ok():
        return 42

    def _fail():
        raise ValueError("example failure")

    print("Success call:", safe_call(_ok))
    print("Failure call:", safe_call(_fail, context={"module": "smoke_test"}))
