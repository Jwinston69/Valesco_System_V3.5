\# Router–Architect CE Missing Item State Transitions v2.1



\## Purpose \& Scope

\- This specification governs how the \*\*Router\*\* converts CE Retrieval Layer signals into behaviour states \*\*A–E\*\* and how the \*\*Architect\*\* converts those states into structured, estimator-facing outputs.  

\- It does not redefine state semantics; `ce\_missing\_item\_behaviour\_v2.1.md` is the single source of truth for state definitions.  

\- This document provides a deterministic transition and response pattern layer, directly implementable in code and tests and aligned with the integration test plan.



---



\## Inputs and Outputs



\### Router Inputs (from CE Retrieval Layer)

The Router may consume \*\*only\*\*:

\- `hit\_count` — integer ≥ 0  

\- `top\_score` — normalized similarity score for the top result (may be null if `hit\_count=0`)  

\- `score\_gap\_to\_next` — numeric difference between top and second result (may be null if `hit\_count<2`)  

\- `coverage\_flags` — structured category-level indicators, including at most:

&nbsp; - membership in `STRONG\_CATEGORY\_COVERAGE\_SET`

&nbsp; - membership in `WEAK\_OR\_CONFLICTING\_COVERAGE\_SET`

&nbsp; - membership in `CATEGORY\_COMPATIBLE\_SET`

&nbsp; - presence/absence of `COMPATIBILITY\_RULES\_AVAILABLE`



No additional signals, embeddings, vectors, or similarity internals are permitted.



\### Router Output

\- A single, explicit state identifier `state\_id ∈ {A, B, C, D, E}`.  

\- A minimal `rationale\_token` for logging/validation only (e.g. `"HIT0"`, `"CLEAN\_MATCH"`, `"INSUFFICIENT\_CONTEXT"`); this token is \*\*not\*\* exposed to the estimator.



\### Architect Input

\- `state\_id` chosen by the Router.  

\- `retrieved\_items` — ordered list of items and associated \*\*raw\*\* library metadata as supplied via CE and library layers.  

\- `compatibility\_metadata` — optional, strictly from predefined library compatibility rules (for State E).  

\- Context necessary to construct estimator messaging: state explanation templates and required action templates.



\### Architect Output

A structured response containing at least:

\- `state\_id` — the Router-selected state, unchanged.  

\- `estimator\_message` — concise, state-specific message explaining the situation and required estimator action.  

\- `items\_presented` — ordered list of zero or more items (depending on state).  

\- `required\_estimator\_action` — enumerated action (e.g. `CONFIRM\_MATCH`, `CHOOSE\_ITEM`, `PROVIDE\_CLARIFICATION`, `REVISE\_DESCRIPTION`).  



No additional inferred attributes, quantities, or items may be introduced by the Architect.



---



\## Deterministic Router Transition Rules



\### Symbolic Thresholds and Predicates

The following constants and predicates are defined symbolically; their \*\*values\*\* live in configuration, but \*\*logic and precedence are fixed here\*\*:



\- `CLEAN\_MATCH\_SCORE\_MIN` — minimum `top\_score` for a clean match.  

\- `CLEAN\_MATCH\_GAP\_MIN` — minimum `score\_gap\_to\_next` to treat the top result as clearly dominant.  

\- `AMBIGUITY\_GAP\_MAX` — maximum `score\_gap\_to\_next` that still indicates ambiguity.  

\- `ITEM\_CONFIDENCE\_LOW(top\_score)` — predicate indicating insufficient item-level confidence.  

\- `HAS\_STRONG\_CATEGORY\_COVERAGE(coverage\_flags)` — true if flags ∈ `STRONG\_CATEGORY\_COVERAGE\_SET`.  

\- `HAS\_WEAK\_OR\_CONFLICTING\_COVERAGE(coverage\_flags)` — true if flags ∈ `WEAK\_OR\_CONFLICTING\_COVERAGE\_SET`.  

\- `HAS\_CATEGORY\_COMPATIBILITY(coverage\_flags)` — true if flags ∈ `CATEGORY\_COMPATIBLE\_SET`.  

\- `COMPATIBILITY\_RULES\_AVAILABLE(coverage\_flags)` — true if compatibility rules are defined for this category.  

\- `COMPATIBLE\_ALTERNATIVE\_COUNT` — count of alternatives available under compatibility rules.  

\- `MIN\_COMPATIBLE\_ALTERNATIVES` — minimum count required to surface alternatives safely.  



If any required signal (`hit\_count`, `coverage\_flags`) is missing or structurally invalid, this is handled under \*\*Safety \& Error Handling\*\* (fail closed).



\### Ordered Transition Logic

The Router evaluates rules in the following \*\*strict order\*\*; the first matching rule determines the state. Rules are non-overlapping by definition and must be implemented as a single, ordered decision tree.



1\. \*\*Rule D — No Internal Match\*\*  

&nbsp;  - Condition: `hit\_count = 0`.  

&nbsp;  - Result: `state\_id = D` (No Internal Match), `rationale\_token = "HIT0"`.



2\. \*\*Rule C — Insufficient Retrieval Context\*\*  

&nbsp;  - Condition: `hit\_count > 0` \*\*and\*\* `HAS\_WEAK\_OR\_CONFLICTING\_COVERAGE(coverage\_flags)` is true  

&nbsp;    \*\*or\*\* any of the following safety conditions hold:

&nbsp;    - `coverage\_flags` missing or unusable;  

&nbsp;    - `top\_score` or `score\_gap\_to\_next` required downstream but missing/inconsistent;  

&nbsp;    - signals are structurally self-contradictory (e.g. simultaneous strong and conflicting coverage).  

&nbsp;  - Result: `state\_id = C`, `rationale\_token = "INSUFFICIENT\_CONTEXT"`.



3\. \*\*Rule A — Clean Match\*\*  

&nbsp;  - Condition:  

&nbsp;    - `hit\_count ≥ 1`,  

&nbsp;    - `HAS\_STRONG\_CATEGORY\_COVERAGE(coverage\_flags)` is true,  

&nbsp;    - `top\_score ≥ CLEAN\_MATCH\_SCORE\_MIN`,  

&nbsp;    - `score\_gap\_to\_next` is either null (no second result) or `score\_gap\_to\_next ≥ CLEAN\_MATCH\_GAP\_MIN`.  

&nbsp;  - Result: `state\_id = A`, `rationale\_token = "CLEAN\_MATCH"`.



4\. \*\*Rule E — Compatible Alternatives\*\*  

&nbsp;  - Condition:  

&nbsp;    - `hit\_count ≥ 1`,  

&nbsp;    - `HAS\_STRONG\_CATEGORY\_COVERAGE(coverage\_flags)` or `HAS\_CATEGORY\_COMPATIBILITY(coverage\_flags)` is true,  

&nbsp;    - `ITEM\_CONFIDENCE\_LOW(top\_score)` is true (i.e. not clean enough for A),  

&nbsp;    - `COMPATIBILITY\_RULES\_AVAILABLE(coverage\_flags)` is true,  

&nbsp;    - `COMPATIBLE\_ALTERNATIVE\_COUNT ≥ MIN\_COMPATIBLE\_ALTERNATIVES`.  

&nbsp;  - Result: `state\_id = E`, `rationale\_token = "COMPATIBLE\_ALTERNATIVES"`.



5\. \*\*Rule B — Closest Internal Matches (Top 3)\*\*  

&nbsp;  - Condition: all above rules (D, C, A, E) did \*\*not\*\* fire and `hit\_count ≥ 1`.  

&nbsp;  - Result: `state\_id = B`, `rationale\_token = "TOP3\_AMBIGUOUS"`.



\### Conflict and Missing Signal Handling

\- When signals are incomplete or conflicting and not caught by Rule D, the Router must prefer \*\*Rule C (Insufficient Retrieval Context)\*\* over any attempt to route to A, B, or E.  

\- If configuration thresholds (e.g. `CLEAN\_MATCH\_SCORE\_MIN`) are misconfigured or unavailable, the Router must \*\*not\*\* approximate or guess and must fall back to \*\*State C\*\* (if `hit\_count > 0`) or \*\*State D\*\* (if `hit\_count = 0`).  



---



\## Architect Response Patterns per State



\### Common Structural Requirements

For every state A–E, the Architect must produce:

\- `state\_id` — exactly the Router-provided identifier.  

\- `estimator\_message` — concise explanation and explicit instruction, using state-specific templates only.  

\- `items\_presented` — list of items; size and content constrained per state.  

\- `required\_estimator\_action` — one of:

&nbsp; - `CONFIRM\_MATCH`  

&nbsp; - `CHOOSE\_ITEM`  

&nbsp; - `PROVIDE\_CLARIFICATION`  

&nbsp; - `REVISE\_DESCRIPTION`  



All item content must use \*\*raw library metadata only\*\* (name, code, catalog attributes) as provided; no new properties may be inferred.



\### State A — Clean Match

\- \*\*Estimator Message\*\*: explains that a single, high-confidence internal match has been found and invites confirmation or explicit override.  

\- \*\*Items Presented\*\*:  

&nbsp; - Maximum: \*\*1\*\* item (the top item only).  

&nbsp; - If Router indicates State A, Architect must present that single item and \*\*no alternatives\*\*.  

\- \*\*Required Estimator Action\*\*: `CONFIRM\_MATCH`.  

\- \*\*Prohibitions\*\*:  

&nbsp; - No additional attributes beyond raw metadata.  

&nbsp; - No secondary suggestions, “similar items”, or compatibility advice.



\### State B — Closest Internal Matches (Top 3)

\- \*\*Estimator Message\*\*: states that multiple plausible internal matches exist and estimator selection is required.  

\- \*\*Items Presented\*\*:  

&nbsp; - Maximum: \*\*3\*\* items.  

&nbsp; - If `hit\_count ≥ 3`, present exactly the top 3 retrieved items.  

&nbsp; - If `1 ≤ hit\_count < 3`, present all available items.  

\- \*\*Required Estimator Action\*\*: `CHOOSE\_ITEM` (or request clarification via separate estimator tooling).  

\- \*\*Prohibitions\*\*:  

&nbsp; - No merging or hybrid items.  

&nbsp; - No items outside the retrieved top-k set.  

&nbsp; - No inferred attributes or ranking beyond CE order.



\### State C — Insufficient Retrieval Context

\- \*\*Estimator Message\*\*: states that retrieval context is insufficient or contradictory and requests specific clarifying information (e.g. dimensions, category details).  

\- \*\*Items Presented\*\*:  

&nbsp; - \*\*Must be empty\*\* (`items\_presented = \[]`).  

&nbsp; - Optional minimal textual examples may appear only inside `estimator\_message` if sourced directly from library phrasing templates, not from `retrieved\_items`.  

\- \*\*Required Estimator Action\*\*: `PROVIDE\_CLARIFICATION`.  

\- \*\*Prohibitions\*\*:  

&nbsp; - No candidate items or alternatives surfaced.  

&nbsp; - No implied “best guess” material.



\### State D — No Internal Match

\- \*\*Estimator Message\*\*: explicitly states that no internal match exists and requests a revised or alternative description.  

\- \*\*Items Presented\*\*:  

&nbsp; - \*\*Must be empty\*\* (`items\_presented = \[]`).  

\- \*\*Required Estimator Action\*\*: `REVISE\_DESCRIPTION`.  

\- \*\*Prohibitions\*\*:  

&nbsp; - No suggestion of external substitutes.  

&nbsp; - No fabricated or inferred materials.



\### State E — Compatible Alternatives

\- \*\*Estimator Message\*\*: explains that category-compatible alternatives are available but item-level certainty is insufficient; estimator must choose or reject.  

\- \*\*Items Presented\*\*:  

&nbsp; - One or more items derived \*\*only\*\* from `compatibility\_metadata` and library-defined compatibility rules.  

&nbsp; - Maximum set: all compatible items deemed safe by rules; no truncation by model discretion beyond deterministic ordering.  

\- \*\*Required Estimator Action\*\*: `CHOOSE\_ITEM` (or explicitly reject all options).  

\- \*\*Prohibitions\*\*:  

&nbsp; - No new compatibility rules inferred at runtime.  

&nbsp; - No expansion to items outside the compatibility rule-set.  

&nbsp; - No additional property inference.



---



\## Safety \& Error Handling Rules



\- If the Router receives any signal \*\*outside\*\* the allowed set (`hit\_count`, `top\_score`, `score\_gap\_to\_next`, `coverage\_flags`) or any attempt is made to access embeddings, vectors, or undefined metrics:

&nbsp; - The transition must \*\*fail closed\*\*.  

&nbsp; - No `state\_id` from `{A, B, C, D, E}` may be surfaced to the estimator.  

&nbsp; - No items are presented.  

&nbsp; - A violation is raised to the Validator for handling.  



\- Under uncertainty (e.g. missing thresholds, inconsistent signals):

&nbsp; - If `hit\_count = 0` → treat as \*\*State D\*\*.  

&nbsp; - If `hit\_count > 0` but category or scoring signals are incomplete or inconsistent → treat as \*\*State C\*\*.  

&nbsp; - Router must never approximate or use probabilistic “best guess” logic.



\- The Architect \*\*must not override\*\* the Router’s chosen `state\_id`.  

&nbsp; - If the Architect output is inconsistent with the state (e.g. items presented in C or D, more than 3 items in B), the Validator must treat this as a failure and block estimator-facing output.



---



\## Alignment with Test Plan



\- \*\*State A Scenarios (A1–A3)\*\*  

&nbsp; - Derive from \*\*Rule A — Clean Match\*\* where `hit\_count ≥ 1`, strong coverage, and clean thresholds satisfied.  

&nbsp; - Integration tests verify that Architect uses the State A response pattern (single item, high-confidence messaging).



\- \*\*State B Scenarios (B1–B3)\*\*  

&nbsp; - Derive from \*\*Rule B — Closest Internal Matches (Top 3)\*\* where no prior rule (D, C, A, E) fires and `hit\_count ≥ 1`.  

&nbsp; - Tests confirm exactly top 3 (or fewer if `hit\_count<3`), explicit ambiguity messaging, and no hybrids.



\- \*\*State C Scenarios (C1–C3)\*\*  

&nbsp; - Derive from \*\*Rule C — Insufficient Retrieval Context\*\*, including weak/contradictory coverage and unstable scores.  

&nbsp; - Tests confirm empty `items\_presented` and clarifying prompts only.



\- \*\*State D Scenarios (D1–D3)\*\*  

&nbsp; - Derive directly from \*\*Rule D — No Internal Match\*\* (`hit\_count = 0`).  

&nbsp; - Tests confirm explicit “no internal match” messaging and absence of alternatives.



\- \*\*State E Scenarios (E1–E3)\*\*  

&nbsp; - Derive from \*\*Rule E — Compatible Alternatives\*\* with strong category/compatibility, low item confidence, and available compatibility rules.  

&nbsp; - Tests confirm compatible alternatives only, with Architect following the State E pattern.



Any change to Router or Architect logic that would alter state outcomes for these scenarios must first update this \*\*transition specification\*\*, and then update the integration test plan.



---



\## Acceptance Criteria

\- Every valid CE signal combination (within allowed signals and structural assumptions) yields exactly \*\*one\*\* well-defined state via the ordered transition rules.  

\- The Router uses only `hit\_count`, `top\_score`, `score\_gap\_to\_next`, and `coverage\_flags`; no probabilistic or heuristic “best guess” branching is permitted.  

\- Architect outputs are fully determined by `(state\_id, retrieved\_items, compatibility\_metadata)` and fixed templates, and never introduce hallucinated items, quantities, attributes, or rules.  

\- The specification contains no YAML, no new governance frameworks, and no meta-policies, and is directly implementable in code and tests.



---



\## Non-Acceptable / Negative Conditions

\- No vague language such as “generally prefers”, “usually routes”, or “model can decide”; all behaviour must be rule-driven.  

\- No transitions conditioned on LLM introspection, embeddings, vector-space properties, or any signals beyond the permitted CE signals.  

\- No dynamic rule synthesis, runtime policy rewriting, or self-modifying logic; transition rules are static, versioned by this document only.

