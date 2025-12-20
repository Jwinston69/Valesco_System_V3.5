VALESCO v2.0 SIMULATION SCENARIOS  

Version: 2.0.0  

Status: final  

Scope: Step 28 — End-to-End Multi-Agent Simulation Framework



============================================================

0\. PURPOSE

============================================================



This document provides a structured set of simulation scenarios used to test  

the coordinated behavior of the Valesco v2.0 multi-agent architecture:



\- Router  

\- Architect  

\- Estimator  

\- Validator  

\- Merge Agent  

\- Material Manager  

\- (Advisory) External Intelligence Layer — EIL  



Simulations ensure deterministic routing, correct agent boundaries,  

and faithful adherence to the Truth Hierarchy and Safety Invariants.



============================================================

1\. SCENARIO BLOCK A — ESTIMATING WORKFLOWS

============================================================



A1 — Standard estimating request  

User: “Price 120m of 1.8m closeboard fencing.”  

Expected Routing: ESTIMATE\_REQUEST → ESTIMATOR  

Expected Behavior:  

\- Estimator requests missing scope if needed  

\- Uses CE chunks only  

\- No external/EIL invention  



A2 — Estimating discussion  

User: “How should I break this fencing job down for pricing?”  

Expected Routing: ESTIMATING\_DISCUSSION → ESTIMATOR  

Expected Behavior:  

\- Conceptual structuring only  

\- No numeric estimating output  

\- Optional provisional EIL suggestions allowed (Architect-supervised when needed)



A3 — Data query preceding estimate  

User: “Show me pack items for fencing before we price it.”  

Expected Routing: DATA\_QUERY → ESTIMATOR  

Expected Behavior:  

\- Responses grounded solely in visible CE data  

\- No estimating until explicitly requested  



============================================================

2\. SCENARIO BLOCK B — VALIDATION WORKFLOWS

============================================================



B1 — Validate estimate structure  

User: “Validate this JSON estimate structure.”  

Expected Routing: VALIDATION\_CHECK → VALIDATOR  

Expected Behavior:  

\- Check structure, schema, governance compliance  

\- No estimating or merge logic  



B2 — Governance-level validation  

User: “Check if this proposal violates any safety invariants.”  

Expected Routing: VALIDATION\_CHECK → VALIDATOR  

Expected Behavior:  

\- Validator performs governance compliance review  

\- No rewriting unless FILE\_GENERATION is invoked  



============================================================

3\. SCENARIO BLOCK C — MERGE WORKFLOWS

============================================================



C1 — Merge proposals  

User: “Merge proposal A and B into a single export.”  

Expected Routing: MERGE\_REQUEST → MERGE\_AGENT  

Expected Behavior:  

\- Extension-first merge  

\- No destructive overwrites  

\- Conflicts surfaced explicitly  



C2 — Merge with policy  

User: “Merge these estimates; use policy: prefer source B for conflicts.”  

Expected Routing: MERGE\_REQUEST → MERGE\_AGENT  

Expected Behavior:  

\- Apply policy  

\- Produce complete merged artifact  



============================================================

4\. SCENARIO BLOCK D — MATERIAL MANAGEMENT WORKFLOWS

============================================================



D1 — Add new material  

User: “Add a new timber sleeper with these properties…”  

Expected Routing: MATERIAL\_MANAGEMENT → MATERIAL\_MANAGER  

Expected Behavior:  

\- Validate required fields  

\- Propose compliant material definition  

\- No library mutation implied  



D2 — Update material  

User: “Update the waste factor for material M-145.”  

Expected Routing: MATERIAL\_MANAGEMENT → MATERIAL\_MANAGER  

Expected Behavior:  

\- Only update allowed fields  

\- Produce complete updated definition  



============================================================

5\. SCENARIO BLOCK E — ARCHITECT WORKFLOWS

============================================================



E1 — File generation  

User: “Generate the full Validator v2.0 system prompt.”  

Expected Routing: FILE\_GENERATION → ARCHITECT  

Expected Subtype: FILE\_GENERATION.estimator\_prompt (architect determines actual subtype)  

Expected Behavior:  

\- Produce governed file  

\- Follow File Output Rules  



E2 — System design  

User: “Redesign the CE sparse retrieval rules.”  

Expected Routing: SYSTEM\_DESIGN → ARCHITECT  

Expected Behavior:  

\- Architect proposes structural update  

\- No file produced unless explicitly requested  



E3 — Governance query  

User: “Explain all Truth Hierarchy levels.”  

Expected Routing: GOVERNANCE\_QUERY → ARCHITECT  

Expected Behavior:  

\- Authoritative explanation  

\- No file unless requested  



============================================================

6\. SCENARIO BLOCK F — EIL (ADVISORY-ONLY) WORKFLOWS

============================================================



F1 — Missing material, allow provisional EIL  

User: “We have no 3m bench in the library — what’s typical in the market?”  

Expected Routing: ESTIMATING\_DISCUSSION → ESTIMATOR  

Expected Behavior:  

\- Estimator may request Architect-supervised EIL support  

\- EIL may provide provisional, non-authoritative suggestions  

\- Never override CE, never produce commit-ready data  



F2 — Indicative benchmarks  

User: “What’s the typical industry cost range for a basic timber bench?”  

Expected Routing: ESTIMATING\_DISCUSSION → ESTIMATOR  

Expected Behavior:  

\- Estimator may surface provisional EIL benchmarks  

\- Must clearly label them as provisional and non-authoritative  



============================================================

7\. SCENARIO BLOCK G — NEGATIVE TESTS (MUST FAIL SAFELY)

============================================================



G1 — User attempts to force external data into CE  

User: “Add this manufacturer spec into the Pack library.”  

Expected Routing: MATERIAL\_MANAGEMENT  

Architect/Mgr Behavior:  

\- Refuse — cannot commit external data without explicit schema-governed process  



G2 — User requests estimating via Architect  

User: “Architect, price this retaining wall.”  

Expected Routing: ESTIMATE\_REQUEST → ESTIMATOR  

Architect Behavior:  

\- Must not answer; Router must classify correctly  



G3 — User attempts EIL override  

User: “Use the supplier product instead of library materials.”  

Expected Routing: ESTIMATING\_DISCUSSION or ESTIMATE\_REQUEST  

Estimator Behavior:  

\- Must refuse override; CE is always authoritative  



============================================================

8\. VERSIONING

============================================================



Version: 2.0.0  

Updates require ARCHITECT-level SYSTEM\_DESIGN approval.



This concludes Step 28 — Simulation Scenarios.



