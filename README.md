# Valesco System v3.5

Valesco System is a deterministic estimating engine MVP with a governed,
modular pipeline for processing scope descriptions and producing consistent,
auditable outputs. It is designed to run locally with strict separation of
concerns and no learning side effects.

## What this repository contains

- Deterministic engine modules for CE retrieval routing, validation, estimator
  runtime, merge, pricing, and resource grouping.
- Runner scripts for interactive and programmatic flows under `engine/scripts/`
  and portable launchers under `bin/`.
- Test suites that enforce determinism and schema compliance under
  `engine/tests/`.
- Governance snapshots and DIBs that declare system state and allowed changes
  under `governance/`.
- Static library data, packs, and catalog inputs under `library/`.

## Runtime modes

The repository currently exposes two runtime modes that share the same kernel
boundary model but differ in how they are invoked.

- `run_valesco.py` and `bin/run_valesco_portable.bat` provide the deterministic
  interface REPL. This path uses the mock/static CE retrieval layer in
  `engine/modules/ce_retrieval_layer_v2_1.py` before entering the kernel.
- `engine/scripts/mvp_runner_v2_2.py` provides the MVP execution path for
  quantity and pricing commands. This path can invoke a CE backend command harness
  before entering the kernel.

## Runtime phase model

The stable execution order is:

```text
CE retrieval
-> Router
-> Architect
-> Validator
-> Estimator Runtime decision adapter
-> Merge Agent
-> post-merge quantity/pricing
```

CE retrieval is pre-kernel. Router, Architect, Validator, and Merge Agent form
the shared kernel pipeline. Estimator Runtime compatibility logic acts as the
decision adapter at the kernel boundary. Quantity and pricing operations are
explicit post-merge steps; the interface REPL may not exercise them, while the
MVP runner does through explicit commands.

## CE backend configuration

`engine/scripts/mvp_runner_v2_2.py` can invoke a CE backend through environment
variables:

- `VALESCO_CE_BACKEND_CMD`: full command to execute
- `VALESCO_CE_BACKEND_SCRIPT`: Python script path, invoked with the runner's
  interpreter

The backend reads JSON from stdin:

```json
{"description": "<scope text>"}
```

and returns JSON:

```json
{
  "hit_count": 0,
  "top_score": null,
  "score_gap_to_next": null,
  "coverage_flags": {},
  "retrieved_items": []
}
```

The CE backend harness is covered by tests with controlled stubs. Live
production CE backend integration is not proven by the current repository
validation.

## Running tests

Use the portable test runner:

```bat
engine\python_runtime\python.exe engine\scripts\run_tests_portable.py
```

By default, the portable runner executes the configured default integration
suite rather than full repository discovery. Targeted suites can be selected
with `VALESCO_TEST_PATTERN`:

```bat
set VALESCO_TEST_PATTERN=integration_test_suite_v2_1.py
engine\python_runtime\python.exe engine\scripts\run_tests_portable.py
```

## System state

The latest verified system status is tracked in:

- `governance/SNAPSHOT v3.7.10.txt`
