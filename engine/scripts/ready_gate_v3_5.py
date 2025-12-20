"""READY v3.5 — canonical fail-closed governance gate.

This module is intentionally standalone (stdlib-only at import time) so entrypoints
can always import it. Third-party dependencies (PyYAML + jsonschema) are imported
inside evaluation and reported as READY failures if missing.

Public API:
- evaluate_ready(root_dir: str) -> tuple[bool, list[str], str]
- assert_ready_or_exit(root_dir: str) -> None

Reporting format:
  timestamp | severity | system | file | path | code | rule | message

Sorting:
  severity (ERROR, then WARN, then INFO), then (file, path, rule).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


READY_SUMMARY_LINE = "Valesco Pack ✅ / Materials ✅ / Tasks ✅ / Subcontractors ✅ — Ready to proceed."
SYSTEM_NAME = "validator"

# Governance whitelist (docs/governance/valesco_instructions.txt)
UNIT_WHITELIST_RAW = {
    "m",
    "m2",
    "m3",
    "lm",
    "hr",
    "nr",
    "day",
    "week",
    "item",
    "t",
    "l",
    "kg",
    "each",
}


def _utc_timestamp_seconds() -> str:
    dt = datetime.now(timezone.utc).replace(microsecond=0)
    # isoformat() produces +00:00; governance requires Z suffix.
    return dt.isoformat().replace("+00:00", "Z")


def _canonical_unit(raw: Any) -> str:
    """Normalize units for internal checks.

    - lower-case
    - treat 'each' as synonym of 'nr' (in-memory only)
    """
    if not isinstance(raw, str):
        return ""
    u = raw.strip().lower()
    return "nr" if u == "each" else u


CANONICAL_UNIT_WHITELIST = {_canonical_unit(u) for u in UNIT_WHITELIST_RAW}


_SEVERITY_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


@dataclass(frozen=True)
class _Finding:
    severity: str
    file: str
    path: str
    code: str
    rule: str
    message: str

    def sort_key(self) -> tuple[Any, ...]:
        return (
            _SEVERITY_ORDER.get(self.severity, 99),
            self.file,
            self.path,
            self.rule,
        )


def _is_simple_identifier(s: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", s))


def _json_path(parts: Iterable[Any]) -> str:
    """Best-effort JSONPath-ish string."""
    out = "$"
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
            continue
        key = str(part)
        if _is_simple_identifier(key):
            out += f".{key}"
        else:
            escaped = key.replace("\\", "\\\\").replace("'", "\\'")
            out += f"['{escaped}']"
    return out


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _load_json(path: Path) -> Any:
    return json.loads(_load_text(path))


def _safe_load_yaml(path: Path) -> Any:
    # Import here to keep module import stdlib-only.
    import yaml  # type: ignore

    return yaml.safe_load(_load_text(path))


def _validate_schema(
    *,
    root: Path,
    yaml_rel: str,
    schema_rel: str,
    findings: list[_Finding],
) -> Any:
    """Load YAML + schema and append schema findings. Returns parsed YAML (or None)."""

    yaml_path = root / Path(yaml_rel)
    schema_path = root / Path(schema_rel)

    if not yaml_path.exists():
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="FILE-EXISTS",
                message="Required YAML file not found.",
            )
        )
        return None

    if not schema_path.exists():
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="FILE-EXISTS",
                message=f"Required schema file not found: {schema_rel}.",
            )
        )
        return None

    try:
        data = _safe_load_yaml(yaml_path)
    except ImportError as e:
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="DEPENDENCY-MISSING",
                message=f"Missing dependency for YAML loading: {e}",
            )
        )
        return None
    except Exception as e:
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="YAML-PARSE",
                message=f"YAML parse failed: {type(e).__name__}: {e}",
            )
        )
        return None

    try:
        schema = _load_json(schema_path)
    except Exception as e:
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="SCHEMA-LOAD",
                message=f"Schema load failed ({schema_rel}): {type(e).__name__}: {e}",
            )
        )
        return data

    try:
        import jsonschema  # type: ignore

        ValidatorCls = jsonschema.validators.validator_for(schema)
        ValidatorCls.check_schema(schema)
        validator = ValidatorCls(schema)

        errors = list(validator.iter_errors(data))
        errors_sorted = sorted(
            errors,
            key=lambda err: (
                _json_path(getattr(err, "absolute_path", [])),
                str(getattr(err, "message", "")),
                str(getattr(err, "validator", "")),
            ),
        )

        for err in errors_sorted:
            findings.append(
                _Finding(
                    severity="ERROR",
                    file=yaml_rel,
                    path=_json_path(getattr(err, "absolute_path", [])),
                    code="READY_SCHEMA_FAIL",
                    rule="SCHEMA-VALIDATION",
                    message=f"Schema violation ({schema_rel}): {err.message}",
                )
            )

    except ImportError as e:
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="DEPENDENCY-MISSING",
                message=f"Missing dependency for schema validation: {e}",
            )
        )
    except Exception as e:
        findings.append(
            _Finding(
                severity="ERROR",
                file=yaml_rel,
                path="$",
                code="READY_SCHEMA_FAIL",
                rule="SCHEMA-VALIDATION",
                message=f"Schema validation failed unexpectedly: {type(e).__name__}: {e}",
            )
        )

    return data


def evaluate_ready(root_dir: str) -> tuple[bool, list[str], str]:
    """Evaluate READY v3.5 governance predicates.

    Returns:
      (ok, report_lines, ready_summary_line)
    """

    ts = _utc_timestamp_seconds()
    root = Path(root_dir).resolve()

    findings: list[_Finding] = []

    # ------------------------------------------------------------------
    # Schema execution (fail-closed)
    # ------------------------------------------------------------------
    _validate_schema(
        root=root,
        yaml_rel="library/packs/valesco_pack.yaml",
        schema_rel="engine/schemas/valesco_pack.schema.json",
        findings=findings,
    )
    materials = _validate_schema(
        root=root,
        yaml_rel="library/core/valesco_materials.yaml",
        schema_rel="engine/schemas/valesco_materials.schema.json",
        findings=findings,
    )
    tasks = _validate_schema(
        root=root,
        yaml_rel="library/core/valesco_tasks.yaml",
        schema_rel="engine/schemas/valesco_tasks.schema.json",
        findings=findings,
    )
    subs = _validate_schema(
        root=root,
        yaml_rel="library/core/valesco_subcontractors.yaml",
        schema_rel="engine/schemas/valesco_subcontractors.schema.json",
        findings=findings,
    )

    # ------------------------------------------------------------------
    # Cross-file checks (fail-closed with ERROR lines)
    # ------------------------------------------------------------------
    materials_codes: set[str] = set()
    if isinstance(materials, dict):
        for idx, m in enumerate(materials.get("materials", []) or []):
            if isinstance(m, dict) and isinstance(m.get("code"), str):
                materials_codes.add(m["code"])
            else:
                findings.append(
                    _Finding(
                        severity="ERROR",
                        file="library/core/valesco_materials.yaml",
                        path=f"$.materials[{idx}]",
                        code="READY_CROSSFILE_FAIL",
                        rule="MATERIALS-CODE",
                        message="Material missing string 'code'.",
                    )
                )

    declared_units_canon: set[str] = set()
    if isinstance(tasks, dict):
        meta = tasks.get("meta") if isinstance(tasks.get("meta"), dict) else {}
        units = meta.get("units") if isinstance(meta, dict) else None
        if isinstance(units, list):
            for i, u in enumerate(units):
                cu = _canonical_unit(u)
                if not cu or cu not in CANONICAL_UNIT_WHITELIST:
                    findings.append(
                        _Finding(
                            severity="ERROR",
                            file="library/core/valesco_tasks.yaml",
                            path=f"$.meta.units[{i}]",
                            code="READY_CROSSFILE_FAIL",
                            rule="TASKS-META-UNITS",
                            message=f"Unit not allowed by whitelist: {u!r}.",
                        )
                    )
                else:
                    declared_units_canon.add(cu)
        else:
            findings.append(
                _Finding(
                    severity="ERROR",
                    file="library/core/valesco_tasks.yaml",
                    path="$.meta.units",
                    code="READY_CROSSFILE_FAIL",
                    rule="TASKS-META-UNITS",
                    message="meta.units must be a list.",
                )
            )

        tasks_list = tasks.get("tasks")
        if isinstance(tasks_list, list):
            for ti, task in enumerate(tasks_list):
                if not isinstance(task, dict):
                    findings.append(
                        _Finding(
                            severity="ERROR",
                            file="library/core/valesco_tasks.yaml",
                            path=f"$.tasks[{ti}]",
                            code="READY_CROSSFILE_FAIL",
                            rule="TASKS-STRUCT",
                            message="Task must be an object.",
                        )
                    )
                    continue

                # derived_unit_rate_<unit> keys must be in declared meta.units
                rates = task.get("rates")
                if isinstance(rates, dict):
                    for k in sorted(rates.keys(), key=lambda x: str(x)):
                        if not isinstance(k, str):
                            continue
                        m = re.match(r"^derived_unit_rate_(.+)$", k)
                        if not m:
                            continue
                        unit_part = m.group(1)
                        cu = _canonical_unit(unit_part)
                        if cu not in declared_units_canon:
                            findings.append(
                                _Finding(
                                    severity="ERROR",
                                    file="library/core/valesco_tasks.yaml",
                                    path=f"$.tasks[{ti}].rates.{k}",
                                    code="READY_CROSSFILE_FAIL",
                                    rule="TASKS-DERIVED-RATE-KEY",
                                    message=(
                                        f"Derived rate key unit '{unit_part}' not declared in meta.units (canonical='{cu}')."
                                    ),
                                )
                            )

                # task.materials[].code must exist in materials codes
                mats = task.get("materials")
                if isinstance(mats, list):
                    for mi, ref in enumerate(mats):
                        if not isinstance(ref, dict):
                            continue
                        code = ref.get("code")
                        if code is None:
                            continue
                        if not isinstance(code, str) or not code:
                            findings.append(
                                _Finding(
                                    severity="ERROR",
                                    file="library/core/valesco_tasks.yaml",
                                    path=f"$.tasks[{ti}].materials[{mi}].code",
                                    code="READY_CROSSFILE_FAIL",
                                    rule="TASK-MATERIAL-REF",
                                    message="Material reference 'code' must be a non-empty string.",
                                )
                            )
                            continue
                        if code not in materials_codes:
                            findings.append(
                                _Finding(
                                    severity="ERROR",
                                    file="library/core/valesco_tasks.yaml",
                                    path=f"$.tasks[{ti}].materials[{mi}].code",
                                    code="READY_CROSSFILE_FAIL",
                                    rule="TASK-MATERIAL-REF",
                                    message=f"Task references unknown material code: {code}",
                                )
                            )

    if isinstance(subs, dict):
        groups = subs.get("groups")
        if isinstance(groups, dict):
            seen: dict[tuple[str, str, str], tuple[str, str]] = {}
            for group_name in sorted(groups.keys(), key=lambda x: str(x)):
                group = groups.get(group_name)
                if not isinstance(group, dict):
                    continue
                items = group.get("items")
                if not isinstance(items, list):
                    continue
                for idx, item in enumerate(items):
                    if not isinstance(item, dict):
                        continue
                    unit_raw = item.get("unit")
                    unit_canon = _canonical_unit(unit_raw)
                    if not unit_canon or unit_canon not in CANONICAL_UNIT_WHITELIST:
                        findings.append(
                            _Finding(
                                severity="ERROR",
                                file="library/core/valesco_subcontractors.yaml",
                                path=f"$.groups.{group_name}.items[{idx}].unit",
                                code="READY_CROSSFILE_FAIL",
                                rule="SUBS-UNIT-WHITELIST",
                                message=f"Subcontractor unit not allowed by whitelist: {unit_raw!r}.",
                            )
                        )

                    t = item.get("type")
                    t_str = t if isinstance(t, str) else ""
                    tup = (str(group_name), t_str, unit_canon)
                    path_here = f"$.groups.{group_name}.items[{idx}]"
                    if tup in seen:
                        first_id, first_path = seen[tup]
                        this_id = item.get("id")
                        this_id_str = this_id if isinstance(this_id, str) else ""
                        findings.append(
                            _Finding(
                                severity="ERROR",
                                file="library/core/valesco_subcontractors.yaml",
                                path=path_here,
                                code="READY_CROSSFILE_FAIL",
                                rule="SUBS-DUP-TUPLE",
                                message=(
                                    "Duplicate subcontractor (group,type,unit) tuple: "
                                    f"group={group_name!r}, type={t_str!r}, unit={unit_raw!r} (canonical={unit_canon!r}); "
                                    f"first_id={first_id!r} at {first_path}, this_id={this_id_str!r}."
                                ),
                            )
                        )
                    else:
                        first_id = item.get("id")
                        first_id_str = first_id if isinstance(first_id, str) else ""
                        seen[tup] = (first_id_str, path_here)

    # ------------------------------------------------------------------
    # BoQ unit coherence (skipped without BoQ context)
    # ------------------------------------------------------------------
    findings.append(
        _Finding(
            severity="INFO",
            file="workspace/inputs",
            path="$",
            code="READY_INFO",
            rule="UNIT-COHERENCE-FAIL",
            message="UNIT-COHERENCE-FAIL check skipped (no BoQ context).",
        )
    )

    # ------------------------------------------------------------------
    # Project docs conflict gate (optional convention)
    # ------------------------------------------------------------------
    active_docs_rel = "workspace/inputs/_ACTIVE_DOCS.yaml"
    active_docs_path = root / Path(active_docs_rel)
    if not active_docs_path.exists():
        findings.append(
            _Finding(
                severity="INFO",
                file=active_docs_rel,
                path="$",
                code="READY_INFO",
                rule="DOCS-REGISTRY",
                message="_ACTIVE_DOCS.yaml not found; treating as no project doc conflicts.",
            )
        )
    else:
        try:
            docs_obj = _safe_load_yaml(active_docs_path)
        except Exception as e:
            findings.append(
                _Finding(
                    severity="ERROR",
                    file=active_docs_rel,
                    path="$",
                    code="READY_DOCS_CONFLICT",
                    rule="DOCS-CONFLICT",
                    message=f"Failed to parse _ACTIVE_DOCS.yaml: {type(e).__name__}: {e}",
                )
            )
        else:
            # Accept a few shapes:
            # - list[dict]
            # - dict with a 'docs' list
            # - dict mapping names -> dict
            entries: list[tuple[str, Any]] = []
            if isinstance(docs_obj, list):
                entries = [(str(i), v) for i, v in enumerate(docs_obj)]
            elif isinstance(docs_obj, dict):
                if isinstance(docs_obj.get("docs"), list):
                    entries = [(f"docs[{i}]", v) for i, v in enumerate(docs_obj.get("docs") or [])]
                else:
                    entries = [(str(k), v) for k, v in sorted(docs_obj.items(), key=lambda kv: str(kv[0]))]

            if not entries:
                findings.append(
                    _Finding(
                        severity="ERROR",
                        file=active_docs_rel,
                        path="$",
                        code="READY_DOCS_CONFLICT",
                        rule="DOCS-CONFLICT",
                        message="_ACTIVE_DOCS.yaml has unsupported or empty structure; cannot determine conflicts.",
                    )
                )
            else:
                for key, entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    conflict = entry.get("conflict")
                    if conflict is True:
                        name = entry.get("name")
                        name_str = name if isinstance(name, str) else key
                        findings.append(
                            _Finding(
                                severity="ERROR",
                                file=active_docs_rel,
                                path=f"$.{key}",
                                code="READY_DOCS_CONFLICT",
                                rule="DOCS-CONFLICT",
                                message=f"Project doc marked conflict=true: {name_str}",
                            )
                        )

    # ------------------------------------------------------------------
    # Finalize
    # ------------------------------------------------------------------
    findings_sorted = sorted(findings, key=lambda f: f.sort_key())

    report_lines = [
        f"{ts} | {f.severity} | {SYSTEM_NAME} | {f.file} | {f.path} | {f.code} | {f.rule} | {f.message}"
        for f in findings_sorted
    ]

    ok = not any(f.severity == "ERROR" for f in findings_sorted)
    return ok, report_lines, READY_SUMMARY_LINE


def assert_ready_or_exit(root_dir: str) -> None:
    ok, report_lines, ready_line = evaluate_ready(root_dir)

    for line in report_lines:
        print(line)

    if not ok:
        raise SystemExit(1)

    print(ready_line)


def _main(argv: list[str]) -> int:
    # Minimal CLI helper: python engine/scripts/ready_gate_v3_5.py [root_dir]
    root_dir = argv[1] if len(argv) > 1 else str(Path(__file__).resolve().parents[2])
    try:
        assert_ready_or_exit(root_dir)
        return 0
    except SystemExit as e:
        return int(getattr(e, "code", 1) or 1)


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
