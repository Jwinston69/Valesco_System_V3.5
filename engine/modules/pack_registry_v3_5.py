# C:/Valesco_System/engine/modules/pack_registry_v3_5.py
# Pack Registry v3.5 - Runtime Pack Registration Gate
#
# Purpose:
#   - Register pricing-authoritative packs at runtime
#   - Provide deterministic, read-only access to registered data
#   - Fail closed if required packs are missing or invalid
#
# Behaviour:
#   - Deterministic load order
#   - One-time initialization (immutable after init)
#   - Logging limited to one line per pack on request

from typing import Any, Dict, List, Optional
from pathlib import Path
import copy

import yaml


_PACK_ORDER = [
    ("pack", "library/packs/valesco_pack.yaml", "pricing-authority"),
    ("materials", "library/core/valesco_materials.yaml", "pricing-authority"),
    ("subcontractors", "library/core/valesco_subcontractors.yaml", "pricing-authority"),
    ("tasks", "library/core/valesco_tasks.yaml", "productivity-only"),
]

_REQUIRED_AUTHORITY_PACKS = [
    "library/packs/valesco_pack.yaml",
    "library/core/valesco_materials.yaml",
    "library/core/valesco_subcontractors.yaml",
]

_TASKS_PACK_PATH = "library/core/valesco_tasks.yaml"

_REGISTRY: Optional[Dict[str, Any]] = None
_REGISTRY_ROOT: Optional[Path] = None
_LOGGED: bool = False


def _repo_root(root_dir: Optional[str]) -> Path:
    if root_dir:
        return Path(root_dir).resolve()
    return Path(__file__).resolve().parents[2]


def _find_duplicates(values: List[str]) -> List[str]:
    seen = set()
    duplicates = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _assert_pack_order_valid() -> None:
    keys = [key for key, _, _ in _PACK_ORDER]
    paths = [rel_path for _, rel_path, _ in _PACK_ORDER]
    dup_keys = _find_duplicates(keys)
    dup_paths = _find_duplicates(paths)
    if dup_keys or dup_paths:
        details = []
        if dup_keys:
            details.append(f"keys={', '.join(dup_keys)}")
        if dup_paths:
            details.append(f"paths={', '.join(dup_paths)}")
        detail_text = "; ".join(details)
        raise RuntimeError(f"Pack registry duplicate entries detected: {detail_text}")

    missing_required = []
    for required in _REQUIRED_AUTHORITY_PACKS:
        matches = [role for _, rel_path, role in _PACK_ORDER if rel_path == required]
        if not matches:
            missing_required.append(required)
            continue
        if any(role != "pricing-authority" for role in matches):
            raise RuntimeError(f"Pack registry invalid authority role for: {required}")
    if missing_required:
        missing_text = ", ".join(missing_required)
        raise RuntimeError(f"Pack registry missing required authority packs: {missing_text}")

    for _, rel_path, role in _PACK_ORDER:
        if rel_path == _TASKS_PACK_PATH and role != "productivity-only":
            raise RuntimeError(f"Pack registry tasks pack must be productivity-only: {rel_path}")


def _assert_required_authority_files(root: Path) -> None:
    missing = []
    for rel_path in _REQUIRED_AUTHORITY_PACKS:
        if not (root / rel_path).exists():
            missing.append(rel_path)
    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(f"Pack registry missing required authority packs: {missing_text}")


def _load_yaml(root: Path, rel_path: str) -> Dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise RuntimeError(f"Pack registry missing required file: {rel_path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"Pack registry expected mapping in {rel_path}")
    return data


def _emit_registry_logs() -> None:
    global _LOGGED
    if _LOGGED:
        return
    for _, rel_path, role in _PACK_ORDER:
        suffix = " (productivity-only)" if role == "productivity-only" else ""
        print(f"PACK_REGISTERED | {rel_path}{suffix}")
    _LOGGED = True


def initialize_registry(root_dir: Optional[str] = None, log: bool = True) -> None:
    """
    Initialize the pack registry once, loading all packs in deterministic order.
    Subsequent calls are idempotent unless a different root_dir is provided.
    """
    global _REGISTRY, _REGISTRY_ROOT
    if _REGISTRY is not None:
        if root_dir is not None and _REGISTRY_ROOT is not None:
            root = _repo_root(root_dir)
            if root != _REGISTRY_ROOT:
                raise RuntimeError("Pack registry already initialized for a different root.")
        if log:
            _emit_registry_logs()
        return

    _assert_pack_order_valid()
    root = _repo_root(root_dir)
    _assert_required_authority_files(root)

    loaded: Dict[str, Any] = {}
    for key, rel_path, _ in _PACK_ORDER:
        loaded[key] = _load_yaml(root, rel_path)
    _REGISTRY = {key: copy.deepcopy(value) for key, value in loaded.items()}
    _REGISTRY_ROOT = root
    if log:
        _emit_registry_logs()


def is_initialized() -> bool:
    return _REGISTRY is not None


def require_registry() -> None:
    """
    Ensure the registry is initialized; fail closed on missing packs.
    """
    initialize_registry(log=False)
    if _REGISTRY is None:
        raise RuntimeError("Pack registry not initialized.")


def get_pack() -> Dict[str, Any]:
    require_registry()
    return copy.deepcopy(_REGISTRY["pack"])


def get_materials() -> Dict[str, Any]:
    require_registry()
    return copy.deepcopy(_REGISTRY["materials"])


def get_subcontractors() -> Dict[str, Any]:
    require_registry()
    return copy.deepcopy(_REGISTRY["subcontractors"])


def get_tasks() -> Dict[str, Any]:
    require_registry()
    return copy.deepcopy(_REGISTRY["tasks"])


def get_registry_root() -> Optional[Path]:
    return _REGISTRY_ROOT
