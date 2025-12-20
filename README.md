\# Valesco System v3.5 (GitHub Context)



Valesco System is a deterministic estimating engine MVP with a governed, modular

pipeline for processing scope descriptions and producing consistent, auditable

outputs. It is designed to be run locally with strict separation of concerns

and no learning side effects.



\## What this repository contains



\- Deterministic engine modules for CE retrieval routing, validation, estimator

&nbsp; runtime, merge, pricing, and resource grouping.

\- Runner scripts for interactive and programmatic flows under `engine/scripts/`.

\- Test suites that enforce determinism and schema compliance under `engine/tests/`.

\- Governance snapshots and DIBs that declare system state and allowed changes

&nbsp; under `governance/`.

\- Static library data (packs, catalog) under `library/`.



\## Core pipeline (high level)



CE backend -> Router -> Architect -> Validator -> Estimator Runtime -> Merge Agent



Pricing and quantity operations are separate, explicit steps in the runner

scripts and test suites.



\## CE backend configuration (runner scripts)



Runner scripts (e.g., `engine/scripts/mvp\_runner\_v2\_2.py`) invoke a CE backend

via environment variables:



\- `VALESCO\_CE\_BACKEND\_CMD`: full command to execute

\- `VALESCO\_CE\_BACKEND\_SCRIPT`: Python script path (invoked with the runner's

&nbsp; interpreter)



The backend reads JSON from stdin with:



```

{"description": "<scope text>"}

```



and returns JSON with:



```

{

&nbsp; "hit\_count": int,

&nbsp; "top\_score": float | null,

&nbsp; "score\_gap\_to\_next": float | null,

&nbsp; "coverage\_flags": dict,

&nbsp; "retrieved\_items": list\[dict]

}

```



\## Running tests



Use the portable test runner:



```

engine/python\_runtime/python.exe engine/scripts/run\_tests\_portable.py

```



You can override the discovery pattern:



```

set VALESCO\_TEST\_PATTERN=integration\_test\_suite\_v2\_1.py

```



\## System state



The current system status (active/frozen/pending subsystems) is tracked in:



\- `governance/valesco\_snapshot\_v3.5.txt`



