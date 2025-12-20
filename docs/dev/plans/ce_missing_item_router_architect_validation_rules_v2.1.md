\# CE Missing Item — Router/Architect Validation Rules v2.1



\## Purpose \& Scope

\- This document defines the \*\*Validator’s runtime checks\*\* over Router outputs and Architect responses for CE missing-item flows.  

\- It does \*\*not\*\* change state definitions or transition logic; it \*\*enforces\*\* the behaviour in:

&nbsp; - `ce\_missing\_item\_behaviour\_v2.1.md` (state semantics A–E),  

&nbsp; - `ce\_missing\_item\_behaviour\_integration\_v2.1.md` (scenarios/flows),  

&nbsp; - `router\_architect\_ce\_missing\_item\_state\_transitions\_v2.1.md` (transition logic \& patterns).  

\- Any violation detected here is blocked \*\*before\*\* estimator-facing output.



---



\## Validation Inputs \& Outputs



\### Inputs

The Validator receives, per request:



\- \*\*Router outputs\*\*

&nbsp; - `router\_state\_id ∈ {A, B, C, D, E}`  

&nbsp; - `router\_rationale\_token` (opaque, for logging only)



\- \*\*CE signals\*\*

&nbsp; - `hit\_count`  

&nbsp; - `top\_score` (nullable where defined)  

&nbsp; - `score\_gap\_to\_next` (nullable where defined)  

&nbsp; - `coverage\_flags`  



\- \*\*Architect structured response\*\*

&nbsp; - `architect\_state\_id` (must equal `router\_state\_id`)  

&nbsp; - `estimator\_message`  

&nbsp; - `items\_presented` (ordered list of item objects)  

&nbsp; - `required\_estimator\_action ∈ {CONFIRM\_MATCH, CHOOSE\_ITEM, PROVIDE\_CLARIFICATION, REVISE\_DESCRIPTION}`  

&nbsp; - `item\_metadata` for each item (raw library metadata only, including any compatibility metadata identifiers)



\### Outputs

\- A \*\*deterministic\*\* decision:

&nbsp; - `VALID`  

&nbsp; - `INVALID` with:

&nbsp;   - `violation\_code` (enumerated string)  

&nbsp;   - `violation\_description` (short, implementation-focused text)  

\- On `INVALID`, the estimator must receive:

&nbsp; - \*\*no item list\*\*, and  

&nbsp; - a generic safe error message: `SAFE\_ERROR\_TEMPLATE`  

&nbsp;   - Example semantic: “Internal retrieval validation failure; no items can be shown. Please revise your description or retry.”



The Validator \*\*never\*\* mutates Router or Architect outputs; it only passes or blocks.



---



\## Signal-Level Validation Rules



1\. \*\*Allowed signals only\*\*  

&nbsp;  - If any CE input field is present \*\*outside\*\*:

&nbsp;    - `hit\_count`, `top\_score`, `score\_gap\_to\_next`, `coverage\_flags`  

&nbsp;  - Then:  

&nbsp;    - Decision: `INVALID`  

&nbsp;    - `violation\_code = "ILLEGAL\_SIGNAL"`  



2\. \*\*Structural consistency\*\*  

&nbsp;  - If `hit\_count = 0` and:

&nbsp;    - any item is attached from CE, or  

&nbsp;    - `top\_score` or `score\_gap\_to\_next` is used where implementation requires them,  

&nbsp;  - Then:

&nbsp;    - `INVALID`, `violation\_code = "SIGNAL\_STRUCTURE\_ERROR"`  



3\. \*\*Missing or malformed signals vs. transition spec\*\*  

&nbsp;  - If signals are missing/malformed in a way that should have forced a \*\*fallback to State C or D\*\* (per transition spec) but Router did not choose C or D:

&nbsp;    - `INVALID`, `violation\_code = "MISSING\_SIGNAL\_FALLBACK"`  



4\. \*\*Coverage flag sanity\*\*  

&nbsp;  - If `coverage\_flags` simultaneously indicate strong and conflicting coverage (or otherwise impossible combinations) and Router did not route to C:

&nbsp;    - `INVALID`, `violation\_code = "COVERAGE\_CONFLICT\_NOT\_ROUTED\_C"`  



---



\## Router-State Consistency Rules



Validator enforces that Router decisions follow the \*\*ordered\*\* transition logic (D → C → A → E → B). For each state:



\### State D — No Internal Match

\- If `hit\_count = 0` and `router\_state\_id != D`:

&nbsp; - `INVALID`, `violation\_code = "STATE\_MISMATCH\_D"`  



\- If `hit\_count > 0` and `router\_state\_id = D`:

&nbsp; - `INVALID`, `violation\_code = "STATE\_D\_WITH\_HITS"`  



\### State C — Insufficient Retrieval Context

\- If `router\_state\_id != C` and:

&nbsp; - `hit\_count > 0` and `coverage\_flags` are weak/contradictory or structurally invalid \*\*as defined in the transition spec\*\*,  

\- Then:

&nbsp; - `INVALID`, `violation\_code = "STATE\_MISMATCH\_C"`  



\### State A — Clean Match

\- If `router\_state\_id = A` and \*\*any\*\* of the clean-match predicates fail:

&nbsp; - `hit\_count < 1`, or  

&nbsp; - coverage not in strong coverage set, or  

&nbsp; - `top\_score` below `CLEAN\_MATCH\_SCORE\_MIN`, or  

&nbsp; - `score\_gap\_to\_next` indicates ambiguity where required,  

\- Then:

&nbsp; - `INVALID`, `violation\_code = "STATE\_MISMATCH\_A"`  



\### State E — Compatible Alternatives

\- If `router\_state\_id = E` and:

&nbsp; - strong/compatible category coverage is \*\*not\*\* indicated, or  

&nbsp; - compatibility rules are unavailable, or  

&nbsp; - compatible alternative count < `MIN\_COMPATIBLE\_ALTERNATIVES`,  

\- Then:

&nbsp; - `INVALID`, `violation\_code = "STATE\_MISMATCH\_E"`  



\### State B — Closest Internal Matches (Top 3)

\- If `router\_state\_id = B` and \*\*any preceding rule\*\* should have applied:

&nbsp; - hit\_count=0 (D), or  

&nbsp; - insufficient/weak/contradictory coverage (C), or  

&nbsp; - clean-match predicates satisfied (A), or  

&nbsp; - compatibility conditions satisfied (E),  

\- Then:

&nbsp; - `INVALID`, `violation\_code = "STATE\_MISMATCH\_B"`  



\### State Identity \& Transition Ordering

\- If `router\_state\_id ∉ {A, B, C, D, E}`:

&nbsp; - `INVALID`, `violation\_code = "UNKNOWN\_STATE\_ID"`  



\- If `architect\_state\_id != router\_state\_id`:

&nbsp; - `INVALID`, `violation\_code = "ARCHITECT\_STATE\_OVERRIDE"`  



---



\## Architect-Structure Validation Rules per State



For all states, Validator checks that:

\- `items\_presented` items are \*\*subset\*\* of retrieved or compatibility-derived library items.  

\- `required\_estimator\_action` matches allowed actions.  

\- Item metadata is raw library metadata (no invented fields).



\### State A — Clean Match

\- Conditions:

&nbsp; - `router\_state\_id = A`  

&nbsp; - Must hold:

&nbsp;   - `items\_presented.length == 1`  

&nbsp;   - `required\_estimator\_action == "CONFIRM\_MATCH"`  

\- Violations:

&nbsp; - `items\_presented.length == 0` → `INVALID`, `"MISSING\_ITEM\_STATE\_A"`  

&nbsp; - `items\_presented.length > 1` → `INVALID`, `"TOO\_MANY\_ITEMS\_A"`  

&nbsp; - `required\_estimator\_action != "CONFIRM\_MATCH"` → `INVALID`, `"WRONG\_ACTION\_STATE\_A"`  



\### State B — Closest Internal Matches (Top 3)

\- Conditions:

&nbsp; - `router\_state\_id = B`  

&nbsp; - Must hold:

&nbsp;   - `1 ≤ items\_presented.length ≤ 3`  

&nbsp;   - All items ∈ top-k retrieved items (per CE order).  

&nbsp;   - `required\_estimator\_action == "CHOOSE\_ITEM"`  

\- Violations:

&nbsp; - `items\_presented.length == 0` → `INVALID`, `"TOO\_FEW\_ITEMS\_B"`  

&nbsp; - `items\_presented.length > 3` → `INVALID`, `"TOO\_MANY\_ITEMS\_B"`  

&nbsp; - Items not in top-k set → `INVALID`, `"ITEM\_NOT\_IN\_TOPK\_B"`  

&nbsp; - `required\_estimator\_action != "CHOOSE\_ITEM"` → `INVALID`, `"WRONG\_ACTION\_STATE\_B"`  



\### State C — Insufficient Retrieval Context

\- Conditions:

&nbsp; - `router\_state\_id = C`  

&nbsp; - Must hold:

&nbsp;   - `items\_presented.length == 0`  

&nbsp;   - `required\_estimator\_action == "PROVIDE\_CLARIFICATION"`  

\- Violations:

&nbsp; - `items\_presented.length > 0` → `INVALID`, `"ITEMS\_IN\_STATE\_C"`  

&nbsp; - `required\_estimator\_action != "PROVIDE\_CLARIFICATION"` → `INVALID`, `"WRONG\_ACTION\_STATE\_C"`  



\### State D — No Internal Match

\- Conditions:

&nbsp; - `router\_state\_id = D`  

&nbsp; - Must hold:

&nbsp;   - `items\_presented.length == 0`  

&nbsp;   - `required\_estimator\_action == "REVISE\_DESCRIPTION"`  

\- Violations:

&nbsp; - `items\_presented.length > 0` → `INVALID`, `"ITEMS\_IN\_STATE\_D"`  

&nbsp; - `required\_estimator\_action != "REVISE\_DESCRIPTION"` → `INVALID`, `"WRONG\_ACTION\_STATE\_D"`  



\### State E — Compatible Alternatives

\- Conditions:

&nbsp; - `router\_state\_id = E`  

&nbsp; - Must hold:

&nbsp;   - `items\_presented.length ≥ 1`  

&nbsp;   - Every item is in the \*\*compatibility rule-set\*\* for the category.  

&nbsp;   - `required\_estimator\_action == "CHOOSE\_ITEM"`  

\- Violations:

&nbsp; - `items\_presented.length == 0` → `INVALID`, `"MISSING\_ITEMS\_STATE\_E"`  

&nbsp; - Any item not in compatibility rule-set → `INVALID`, `"NON\_COMPATIBLE\_ITEM\_E"`  

&nbsp; - `required\_estimator\_action != "CHOOSE\_ITEM"` → `INVALID`, `"WRONG\_ACTION\_STATE\_E"`  



---



\## Attribute \& Alternative Safety Rules



1\. \*\*No inferred attributes\*\*

&nbsp;  - If any item metadata contains fields or values that cannot be traced to library metadata:

&nbsp;    - `INVALID`, `violation\_code = "INFERRED\_ATTRIBUTE"`  



2\. \*\*No external substitutes\*\*

&nbsp;  - If text or metadata indicates items outside the internal library (e.g., external brand references not present in library subset):

&nbsp;    - `INVALID`, `violation\_code = "EXTERNAL\_SUBSTITUTE"`  



3\. \*\*State E compatibility sourcing\*\*

&nbsp;  - If State E item set cannot be traced to compatibility metadata for the routed category:

&nbsp;    - `INVALID`, `violation\_code = "NON\_COMPATIBLE\_ITEM\_E"`  



4\. \*\*Free-text attribute expansion\*\*

&nbsp;  - If `estimator\_message` introduces \*\*new technical attributes\*\* (dimensions, performance, standards, etc.) not present in underlying library metadata:

&nbsp;    - `INVALID`, `violation\_code = "UNSAFE\_FREETEXT\_ATTRIBUTES"`  



5\. \*\*Top-k and library membership\*\*

&nbsp;  - For States A, B:

&nbsp;    - All items must be drawn from CE-retrieved set; otherwise `INVALID`, `violation\_code = "ITEM\_NOT\_FROM\_LIBRARY"`  



---



\## Validator Behaviour on Invalid Outputs



\- On `VALID`:

&nbsp; - Router and Architect outputs pass unchanged to the estimator.



\- On `INVALID`:

&nbsp; - No Router/Architect message or item list is passed to the estimator.  

&nbsp; - Validator returns a generic safe error message constructed from `SAFE\_ERROR\_TEMPLATE`.  

&nbsp; - `violation\_code` and `violation\_description` are logged for diagnostics only (not shown to estimator).  

&nbsp; - Validator performs \*\*no auto-correction\*\*; it does not alter state, items, or actions and does not re-run transitions.



\- All negative integration tests (illegal signals, speculative materials, external substitutes, dynamic rule attempts) must be mapped to explicit violation codes, including but not limited to:

&nbsp; - `"ILLEGAL\_SIGNAL"`  

&nbsp; - `"INFERRED\_ATTRIBUTE"`  

&nbsp; - `"EXTERNAL\_SUBSTITUTE"`  

&nbsp; - `"UNSAFE\_FREETEXT\_ATTRIBUTES"`  

&nbsp; - `"STATE\_MISMATCH\_\*"`  

&nbsp; - `"ITEMS\_IN\_STATE\_C"`, `"ITEMS\_IN\_STATE\_D"`  

&nbsp; - `"NON\_COMPATIBLE\_ITEM\_E"`  



---



\## Acceptance Criteria \& Non-Acceptable Conditions



\### Acceptance Criteria

\- Every Router–Architect combination for CE missing-item flows yields either:

&nbsp; - a deterministic `VALID` pass, or  

&nbsp; - a blocked output with explicit `violation\_code` and safe error message.  

\- No probabilistic or heuristic allowances: Validator decisions are rule-based only.  

\- No dynamic rule synthesis, meta-governance, or YAML; all rules are static and versioned in this document.  

\- Spec remains narrowly focused on \*\*runtime validation\*\* for CE missing-item safety and directly supports:

&nbsp; - `ce\_missing\_item\_behaviour\_v2.1.md`,  

&nbsp; - `ce\_missing\_item\_behaviour\_integration\_v2.1.md`,  

&nbsp; - `router\_architect\_ce\_missing\_item\_state\_transitions\_v2.1.md`.



\### Non-Acceptable Conditions

\- Any rule that depends on LLM introspection, embeddings, vector space operations, or signals beyond the allowed CE signals.  

\- Any language or behaviour allowing “best effort guessing”, “usually valid”, or similar probabilistic notions.  

\- Any Validator behaviour that modifies Router or Architect outputs instead of passing or blocking them deterministically.

