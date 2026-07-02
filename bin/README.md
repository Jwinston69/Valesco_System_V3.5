# Bin Scripts

## Canonical scripts

- install_deps.bat - Embedded Python runtime bootstrap
- run_valesco_portable.bat - Portable launcher for `run_valesco.py`
- validate.bat - Library/schema integrity validation

`run_valesco_portable.bat` starts the deterministic interface REPL. It does not
launch `engine/scripts/mvp_runner_v2_2.py`, which is the MVP quantity/pricing
execution path.

`validate.bat` is an operational, non-governing validation helper. The READY
gate remains the governing readiness gate.

## Legacy scripts

Legacy scripts are retained for provenance and recovery only and are not part
of the current execution path.

- start_valesco_v1.9.bat - Retired legacy launcher
  Replaced by:
  - install_deps.bat (Python bootstrap)
  - run_valesco_portable.bat (execution)
- build_development_authority_pack_v3.5.bat - Offline onboarding pack builder
- export_ai_context_bundle_portable.bat - Legacy AI context bundle exporter
- package_release_v4.0_rc.bat - Release packaging helper

## Legacy scripts still present in bin/

- backup_filesystem_state.bat - Emergency / recovery snapshot tooling
  Status: legacy; retained for provenance and fallback
