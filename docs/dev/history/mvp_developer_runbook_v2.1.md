\# Valesco MVP Developer Runbook v2.1  

\*\*Purpose:\*\* Practical operational guide for developing, running, testing, and extending the Valesco MVP.  

\*\*Non-governance:\*\* This document does \*\*not\*\* define rules or behaviour. It describes \*\*how to execute\*\* the already-defined system.



---



\# 1. Overview of MVP Architecture



User

↓

CE Retrieval Layer (signals only)

↓

Router (deterministic state A–E selection)

↓

Architect (state-constrained structured output)

↓

Validator (pass/block — no corrections)

↓

Estimator Runtime (runtime user interaction)

↓

Merge Agent (confirmed/provisional item integration)

↓

Material Manager (raw catalog metadata only)



\*\*Key notes:\*\*

\- All components are \*\*deterministic\*\*.  

\- No module may cross boundaries or perform another module’s responsibility.  

\- No inference, no embeddings, no heuristics, no enrichment.



---



\# 2. How to Run the MVP Manually



Open a terminal in the project root and run:



```bash

python C:/Valesco\_System/engine/scripts/mvp\_runner\_v2.1.py


You will see:



Welcome to Valesco MVP Runner v2.1

Type an item description to start CE handling.

Commands: 'show', 'meta <id>', 'reset', 'exit'.

Manual Flow

Type an item description



Respond to Estimator prompts, e.g.



yes / no



1, 2, <item-id>



Clarification text



Revised descriptions or provisional



Use helper commands:



show — prints current estimate



meta <id> — prints catalog metadata



reset — clears the estimate



exit — quits



Example interaction:



> clean item description

Estimator: Single high-confidence match identified.

Confirm this item? (yes/no): yes

Item confirmed and added to estimate.

Current Estimate:

1\. A001 — Single Clean-Match Item

3\. How to Run Automated Tests

Execute:

python -m unittest C:/Valesco\_System/engine/tests/integration\_test\_suite\_v2.1.py

You should see output similar to:

----------------------------------------------------------------------

Ran 10 tests in 0.23s

OK

Pass/Fail Interpretation

OK → All pipeline components behave deterministically and consistently.



FAIL / ERROR → Investigate the specific module indicated.



Determinism failures indicate mock or logic drift.



State mismatch failures indicate Router or CE retrieval inconsistencies.



Metadata-related failures indicate Architect or Merge Agent violations.



4\. Module Summaries (Operational Only)

CE Retrieval Layer

Provides only four CE signals + retrieved\_items.



No vectors, no embeddings, no inference.



Static, deterministic keyword mapping.



Router

Implements strict, ordered A→E state logic.



No enrichment, no fallback guessing.



Outputs state\_id, rationale token, items, compatibility metadata.



Architect

Formats deterministic estimator payloads per state A–E.



No item modification or inference.



No alternative generation.



Validator

Pass/block only.



Checks signals, Router consistency, Architect structure, metadata safety.



On INVALID → blocks all content and returns safe error.



Estimator Runtime

Turns validated payloads into runtime UI instructions.



Determines meaning of user replies.



No CE access, no inference.



Merge Agent

Integrates confirmed catalog or provisional items.



Never modifies metadata.



Maintains deterministic estimate structure.



Material Manager

Returns raw catalog metadata.



No enrichment, no classification, no substitutes.



MVP Runner

Thin REPL orchestrator for manual operation.



No decision-making or CE logic.



5\. Adding New Test Cases (Developer Notes)

To extend automated tests:



Add new static mock catalog entries to the CE Retrieval Layer and Material Manager.



Extend deterministic keyword-profile mapping for CE retrieval.



Add new test methods to integration\_test\_suite\_v2.1.py following existing patterns.



Ensure all tests run twice to verify determinism: same inputs → same snapshots.



Avoid any non-deterministic behaviour (timestamps, randomness, ordering drift).



6\. Common Failure Modes (Troubleshooting)

Architect injecting attributes

Symptoms: Validator fails with METADATA\_SAFETY\_ERROR.

Cause: Architect enriched or altered item metadata.



Router selecting incorrect state

Symptoms: Validator fails with STATE\_MISMATCH\_\*.

Cause: Transition ordering violated or CE signals inconsistent.



Validator allowing illegal signals

Symptoms: CE Retrieval returns extra fields; tests detect ILLEGAL\_SIGNAL.

Cause: CE retrieval implementation drift.



Merge Agent modifying metadata

Symptoms: Catalog metadata in snapshot does not match Material Manager values.

Cause: Merge Agent injected attributes.



Estimator Runtime leaking CE internals

Symptoms: User-facing messages contain CE terms (score, state, coverage).

Cause: Estimator prompt or runtime modifications.



CE Retrieval non-determinism

Symptoms: Snapshots differ across identical test runs.

Cause: New code introduced randomness or unstable ordering.



7\. Extending Beyond MVP

This MVP is designed to be directly replaceable by production components:



Replace mock CE Retrieval Layer with real retrieval backend.



Replace static catalog with dynamic product database.



Add pricing logic and quantity modelling.



Integrate Estimator Runtime with UI frontend.



Extend test harness for multi-item estimating workflows.



Maintain strict determinism and separation of responsibilities.



8\. Acceptance Criteria

This runbook:



Adds no new rules, no behavioural changes, no governance.



Offers purely operational instructions for developers.



Uses corrected Markdown code-block formatting (bash and text).



Provides a clear guide for running, testing, debugging, and extending the MVP.



