\# CE Missing Item — End-to-End Safety Envelope v2.1



\## Purpose \& Constraints

\- This safety envelope describes the \*\*operational boundaries\*\* governing missing-item flows across all relevant agents: \*\*Router → Architect → Validator → Estimator → Merge Agent → Material Manager\*\*.  

\- It introduces \*\*no new rules, signals, thresholds, or agent behaviours\*\*.  

\- It restates, at the operational level, only what is already defined in:  

&nbsp; - `ce\_missing\_item\_behaviour\_v2.1.md` (state semantics A–E),  

&nbsp; - `ce\_missing\_item\_behaviour\_integration\_v2.1.md` (scenarios and flows),  

&nbsp; - `router\_architect\_ce\_missing\_item\_state\_transitions\_v2.1.md` (routing and Architect patterns),  

&nbsp; - `ce\_missing\_item\_router\_architect\_validation\_rules\_v2.1.md` (Validator constraints).  

\- All extensions beyond these documents are explicitly forbidden.



---



\## End-to-End Operational Flow Overview



\### 1. CE Retrieval Layer → Router

\- CE Retrieval Layer produces only the \*\*permitted signals\*\*: `hit\_count`, `top\_score`, `score\_gap\_to\_next`, `coverage\_flags`.  

\- No embeddings, vectors, similarity internals, or additional metrics may flow downstream.



\### 2. Router → Architect

\- Router evaluates CE signals using the \*\*ordered transition rules\*\* and emits \*\*exactly one\*\* state from {A, B, C, D, E} with a rationale token (logging only).  

\- Router sends the state plus retrieved items (and any compatibility metadata) to the Architect.



\### 3. Architect → Validator

\- Architect constructs the \*\*state-constrained output structure\*\*:

&nbsp; - `state\_id`,  

&nbsp; - `estimator\_message`,  

&nbsp; - `items\_presented` (allowed per state only),  

&nbsp; - `required\_estimator\_action`.  

\- Architect must not introduce new items, metadata, or inferred attributes.



\### 4. Validator → Estimator

\- Validator applies the \*\*signal consistency\*\*, \*\*Router-state consistency\*\*, \*\*Architect-structure\*\* and \*\*safety\*\* checks.  

\- If VALID → estimator receives the Architect’s structured response.  

\- If INVALID → estimator receives \*\*no items\*\* and only a generic safe error message.



\### 5. Estimator → Merge Agent

\- Estimator acts exclusively on validated outputs:

&nbsp; - Confirms the match (A),  

&nbsp; - Chooses among top-3 (B),  

&nbsp; - Provides clarification (C),  

&nbsp; - Revises description (D),  

&nbsp; - Chooses among compatibility alternatives (E).  



\### 6. Merge Agent → Material Manager

\- Merge Agent merges \*\*only\*\* items confirmed by the Estimator and validated by the Validator.  

\- Material Manager then supplies \*\*raw library metadata\*\* for these validated items only.



No other operational pathways are allowed.



---



\## Cross-Agent Boundary Conditions



\### CE Retrieval → Router

\- Router may read only the permitted CE signals; any other fields are invalid.  

\- Router cannot route based on missing, contradictory, or illegal signals except as defined (fallback to C or D).



\### Router → Architect

\- Router must output a \*\*recognised\*\* state (A–E); no additional or custom states.  

\- Architect must not override `state\_id`.



\### Architect → Validator

\- Architect must supply outputs consistent with the Router state and behavioural patterns.  

\- Validator does not modify Architect output; it only passes or blocks.



\### Validator → Estimator

\- Estimator receives \*\*no signal-level data\*\* and no CE internals.  

\- For INVALID outputs, only the generic safe error is surfaced.



\### Estimator → Merge Agent

\- Merge Agent acts only on estimator-confirmed choices validated upstream.  

\- It may not assume or infer compatibility, substitutes, or new attributes.



\### Merge Agent → Material Manager

\- Material Manager may not introduce metadata not present in the library.  

\- Only validated items may be processed.



These boundaries restate—without extending—the constraints already defined in existing specifications.



---



\## Allowed \& Disallowed Information Flows



\### Allowed Flows (Operational Restatement)

\- CE signals → Router  

\- Router state + retrieved items → Architect  

\- Architect structured output → Validator  

\- Validator VALID output → Estimator  

\- Estimator decisions → Merge Agent  

\- Merge Agent validated items → Material Manager  



\### Disallowed Flows (Already Defined in Prior Specs)

\- Any access to embeddings, vectors, or similarity internals by any agent.  

\- Architect modifying or reinterpreting Router’s chosen state.  

\- Estimator receiving item lists in \*\*States C or D\*\*.  

\- Merge Agent or Material Manager using unvalidated, inferred, or external data.  

\- Introduction of new technical attributes not present in raw library metadata.



---



\## State-Specific Safety Paths (Operational Restatement Only)



\### State A — Clean Match

\- Exactly one item presented; no alternatives; estimator confirms.  

\- Architect shows raw metadata only; downstream agents propagate validated item.



\### State B — Closest Internal Matches (Top 3)

\- Up to three retrieved items shown; estimator must choose; no hybrids or inferred items.  



\### State C — Insufficient Retrieval Context

\- No items allowed; estimator must provide clarification.  



\### State D — No Internal Match

\- No items allowed; estimator must revise description.  



\### State E — Compatible Alternatives

\- Items presented are strictly from compatibility rules; estimator must choose.  

\- No new compatibility logic is introduced.



These flows mirror the behavioural spec and transition spec exactly.



---



\## Failure Modes \& Blocking Points (No New Rules)



The Validator blocks outputs at any of the following conditions (all defined in validation\_rules\_v2.1):



\- \*\*Illegal signals\*\* (unsupported fields, embeddings, vector metrics).  

&nbsp; - ⇒ `INVALID`, estimator receives generic safe error.  

\- \*\*Signal–state mismatch\*\* (e.g., `hit\_count=0` but Router chose A/B/C/E).  

\- \*\*Architect pattern mismatch\*\* (items shown in C/D, too many items in A/B, wrong action types).  

\- \*\*Unsafe attributes\*\* (inferred metadata, external substitutes, free-text technical additions).  

\- \*\*Non-library or non-compatible items\*\* in any state.  



Any invalid output must be blocked; Validator does not correct or rewrite.



---



\## Acceptance Criteria

\- This safety envelope adds \*\*no new rules\*\* or behaviours; it restates operational boundaries only.  

\- Fully consistent with all CE missing-item documents: behaviour spec, integration plan, transition spec, and validation rules.  

\- Describes only the allowed flows and existing blocking points.  

\- Contains no YAML, governance extensions, or new abstractions.



---



\## Non-Acceptable Conditions

\- Introducing new agent behaviours, thresholds, decision logic, or signals.  

\- Creating governance structures or meta-rules.  

\- Adding constraints not already present in existing CE missing-item specifications.  

\- Suggesting alternative or extended pathways beyond the established flow.

