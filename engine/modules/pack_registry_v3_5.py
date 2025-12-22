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

from typing import Any, Dict, Optional
from pathlib import Path
import copy

import yaml


_PACK_ORDER = [
    ("pack", "library/packs/valesco_pack.yaml", "pricing-authority"),
    ("materials", "library/core/valesco_materials.yaml", "pricing-authority"),
    ("subcontractors", "library/core/valesco_subcontractors.yaml", "pricing-authority"),
    ("tasks", "library/core/valesco_tasks.yaml", "productivity-only"),
]

_REGISTRY: Optional[Dict[str, Any]] = None
_REGISTRY_ROOT: Optional[Path] = None
_LOGGED: bool = False


def _repo_root(root_dir: Optional[str]) -> Path:
    if root_dir:
        return Path(root_dir).resolve()
    return Path(__file__).resolve().parents[2]


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
    """
    global _REGISTRY, _REGISTRY_ROOT
    if _REGISTRY is None:
        root = _repo_root(root_dir)
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

