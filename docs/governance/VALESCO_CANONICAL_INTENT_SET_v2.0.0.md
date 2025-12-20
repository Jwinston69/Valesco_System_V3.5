\# Valesco v2.0 — Canonical Intent Set

\# Version: 2.0.0 (Final, Production-Ready)

\# Status: Frozen for Router Implementation

\# Location: docs/governance/VALESCO\_CANONICAL\_INTENT\_SET\_v2.0.0.md



============================================================

CANONICAL INTENT SET v2.0 — FINAL FORM

============================================================



Every user message must map to exactly one intent below.

All intents are mutually exclusive, deterministic, and exhaustive.

No new intents may be inferred or invented outside this set.



------------------------------------------------------------

A-SERIES — GOVERNANCE / SYSTEM

------------------------------------------------------------



\### A1 — System Governance Clarification

User requests explanation or interpretation of governance rules, invariants, truth hierarchy, or system boundaries WITHOUT requesting changes or modifications.

\*\*Routing Target:\*\* Architect



\### A2 — System Bootstrap / Reset / Handoff

User provides or requests session bootstrap, initialization, handoff loading, or controlled restart.

\*\*Routing Target:\*\* Architect



\### A3 — System Design / Architecture Modification

User requests creation, modification, or extension of governance rules, schema definitions, agent logic, or system architecture.  

Includes any change request to Valesco behavior.

\*\*Routing Target:\*\* Architect



------------------------------------------------------------

B-SERIES — COMMERCIAL ESTIMATING REQUESTS

------------------------------------------------------------



\### B1 — Quantity Interpretation

Interpret scope descriptions, quantities, or measurements.

\*\*Routing Target:\*\* Estimator



\### B2 — First-Principles Estimation

Structured estimating logic based on CE chunks (task → material → pack → subcontractor).

\*\*Routing Target:\*\* Estimator



\### B3 — Pack / Assembly Retrieval

Retrieval or interpretation of pack logic and CE pack relationships.

\*\*Routing Target:\*\* Estimator



\### B4 — Subcontractor Analysis

Requests involving subcontractor relationships, inclusions, or trade package logic.

\*\*Routing Target:\*\* Estimator



\### B5 — Estimate Refinement / Expansion

Refinement, extension, or development of existing estimate logic.

\*\*Routing Target:\*\* Estimator



------------------------------------------------------------

C-SERIES — STRUCTURAL / VALIDATION REQUESTS

------------------------------------------------------------



\### C1 — Schema Validation

Validation of structured objects (materials, tasks, packs, estimate objects).

\*\*Routing Target:\*\* Validator



\### C2 — Consistency Check

Logic coherence checking, rules compliance, invariant enforcement.

\*\*Routing Target:\*\* Validator



\### C3 — Schema Generation Request

Production of schemas (JSON, YAML patterns) for system components.

\*\*Routing Target:\*\* Validator



\### C4 — Output Integrity Verification

Verification of previously generated estimating outputs or artifacts.

\*\*Routing Target:\*\* Validator



------------------------------------------------------------

D-SERIES — MERGE / MATERIAL MANAGEMENT

------------------------------------------------------------



\### D1 — Merge Request

User provides an extension or additive estimate component requiring controlled, governed merging.

\*\*Routing Target:\*\* Merge Agent



\### D2 — Material Additive Request

Creation or modification of material entries under allocator rules.

\*\*Routing Target:\*\* Material Manager



------------------------------------------------------------

E-SERIES — OUT-OF-SCOPE

------------------------------------------------------------



\### E1 — Out-of-Scope / Non-Valesco Query

User request is unrelated to Valesco estimating, architecture, CE layer, system design, or domain.  

Handled only for safe redirection.

\*\*Routing Target:\*\* Architect



============================================================

DETERMINISTIC COVERAGE CONFIRMATION

============================================================



• A1 = clarification only  

• A3 = modification only  

• A2 = session bootstrap and resets  

• B-series = all commercial estimating operations  

• C-series = all structural and validation operations  

• D-series = additive and merge operations  

• E1 = strictly non-Valesco  

• No overlap exists  

• No ambiguous categories remain  

• CE retrieval is only used for B-series intents  



============================================================

VERSIONING RULES

============================================================



This document is versioned under:



\*\*VALESCO\_CANONICAL\_INTENT\_SET\_v2.0.0\*\*



Changes require:

• Minor version bump for additive categories  

• Major version bump for breaking changes  

• No agent may infer new intents outside this file  



============================================================

END OF SPEC

============================================================



