\# Valesco Full System Handover Document v2.0  

Version: 2.0.0  

Status: final  

Compatibility: All v2.0 components (Bootstrap, Router, Agents, CE Layer, Roadmap, EIL Phase 2.5)



============================================================

0\. PURPOSE OF THIS HANDOVER

============================================================



This document provides a complete architectural and operational handover of the  

Valesco v2.0 multi-agent estimating system.



It consolidates:



\- Governance and Truth Hierarchy  

\- Safety Invariants  

\- CE Layer architecture  

\- External Intelligence Layer (EIL) specification  

\- Canonical Intent Set  

\- Router System Prompt summary  

\- Agent System Prompts summary  

\- Bootstrap Prompt v2.0  

\- Simulation and validation frameworks  

\- Phase roadmap and evolution path  



This is the authoritative artifact for onboarding engineers, architects, and maintainers.



============================================================

1\. GLOBAL GOVERNANCE FOUNDATION

============================================================



1.1 Truth Hierarchy v2.0 (Top → Bottom)



1\. Global Instructions \& Safety Invariants  

2\. Truth Hierarchy ordering rules  

3\. System Manifest \& Architecture Rules  

4\. CE Layer (chunking, retrieval, context discipline)  

5\. Agent Behavior Specifications  

6\. Development Policies  

7\. File System (read-only during AI operation)  

8\. Conversational suggestions  



Lower layers must not override higher layers.



------------------------------------------------------------

1.2 Safety Invariants (Mandatory)

------------------------------------------------------------



1\. No hallucination of system structure  

2\. No invention of YAML keys, schema fields, library codes, or agent capabilities  

3\. Immutable truth hierarchy  

4\. No creation or deletion of real files  

5\. CE Chunk Rule — no raw YAML reading  

6\. Sparse retrieval discipline  

7\. No autonomous architecture changes  

8\. Deterministic behavior  

9\. Strict multi-agent separation  

10\. No undocumented mechanisms  

11\. No hidden state  

12\. Governance > convenience always  



============================================================

2\. CONTEXT ENGINEERING LAYER (CE LAYER)

============================================================



The CE Layer is the only valid mechanism for reasoning about:



\- Materials  

\- Tasks  

\- Pack  

\- Subcontractors  



Rules:



\- CE chunks are authoritative.  

\- Retrieval must be minimal and intent-aligned.  

\- No vector database assumed.  

\- No inferred or invented library content.  

\- No access to raw YAML unless provided in-session.  



Outputs:



\- 909 material chunks  

\- 37 task chunks  

\- 121 pack chunks  

\- 111 subcontractor chunks  



============================================================

3\. EXTERNAL INTELLIGENCE LAYER (EIL) — PHASE 2.5

============================================================



Purpose:  

Provvisional, advisory-only external intelligence to support estimating and design discussions when the library has no match.



Position in Truth Hierarchy:  

EIL sits \*\*below all Valesco truths\*\* and cannot override CE, schemas, allocator, or internal data.



Capabilities:



\- Suggest comparable external products  

\- Provide indicative industry ranges  

\- Surface supplier/manufacturer examples  

\- Offer conceptual alternatives  

\- Act as a “thinking partner”  



Strict Limitations:



\- Always PROVISIONAL  

\- Never writes to Materials/Tasks/Pack/Subcontractors  

\- Never replaces CE truths  

\- Never integrates external data  

\- Never bypasses Architect, Estimator, or Validator  



Implementation:  

Fully defined later; advisory layer only.



============================================================

4\. CANONICAL INTENT SET v2.0

============================================================



INTENT.FILE\_GENERATION  

INTENT.ESTIMATE\_REQUEST  

INTENT.ESTIMATING\_DISCUSSION  

INTENT.DATA\_QUERY  

INTENT.VALIDATION\_CHECK  

INTENT.MERGE\_REQUEST  

INTENT.MATERIAL\_MANAGEMENT  

INTENT.SYSTEM\_DESIGN  

INTENT.ROUTER\_QUERY  

INTENT.GOVERNANCE\_QUERY  

INTENT.SYSTEM\_STATUS  

INTENT.AMBIGUOUS  



FILE\_GENERATION subtypes (Architect-refined):



\- spec  

\- estimator\_prompt  

\- governance\_doc  

\- script  

\- library\_update  

\- proposal\_export  



============================================================

5\. ROUTER SYSTEM (SUMMARY)

============================================================



\- Pure classifier.  

\- Must output: {intent, target\_agent, ce\_profile}.  

\- Must never perform estimating or design work.  

\- Applies deterministic intent mapping and CE-profile rules.  

\- Ambiguity → INTENT.AMBIGUOUS → Architect.



CE Profile fields:



\- use\_ce  

\- materials  

\- tasks  

\- pack  

\- subcontractors  

\- governance  



============================================================

6\. MULTI-AGENT SYSTEM ARCHITECTURE

============================================================



------------------------------------------------------------

6.1 Architect  

------------------------------------------------------------

\- Enforces governance and truth hierarchy.  

\- Handles FILE\_GENERATION and SYSTEM\_DESIGN.  

\- Resolves ambiguity.  

\- Oversees EIL boundaries.  

\- Produces governed artifacts.



------------------------------------------------------------

6.2 Estimator  

------------------------------------------------------------

Handles:  

\- ESTIMATE\_REQUEST  

\- ESTIMATING\_DISCUSSION  

\- DATA\_QUERY  



Rules:  

\- CE-grounded estimating only.  

\- No invented materials or rates.  

\- No file generation.  



------------------------------------------------------------

6.3 Validator  

------------------------------------------------------------

Handles: VALIDATION\_CHECK  



Rules:  

\- Structural/schema correctness  

\- Governance compliance  

\- Diagnostic only  



------------------------------------------------------------

6.4 Merge Agent  

------------------------------------------------------------

Handles: MERGE\_REQUEST  



Rules:  

\- Extension-first merging  

\- Non-destructive  

\- No schema invention  



------------------------------------------------------------

6.5 Material Manager  

------------------------------------------------------------

Handles: MATERIAL\_MANAGEMENT  



Rules:  

\- Controlled additions/updates  

\- Schema + allocator-governed  

\- No task/pack alteration  



============================================================

7\. BOOTSTRAP PROMPT v2.0 (SUMMARY)

============================================================



\- Activates all governance layers.  

\- Enforces truth hierarchy, CE rules, agent boundaries, safety invariants.  

\- Integrates EIL as non-authoritative.  

\- Defines output discipline and routing contract.  

\- Requires session handoff snapshot for resumption.



============================================================

8\. SYSTEM TESTING \& VALIDATION SUITES

============================================================



------------------------------------------------------------

8.1 Router–Architect Integration Tests  

------------------------------------------------------------

Ensures:



\- Accurate routing  

\- FILE\_GENERATION subtype refinement  

\- Correct ambiguity handling  

\- No role drift  



------------------------------------------------------------

8.2 Simulation Scenarios v2.0  

------------------------------------------------------------

Covers:



\- Estimating workflows  

\- Validation workflows  

\- Merge workflows  

\- Material management workflows  

\- Architect workflows  

\- EIL advisory scenarios  

\- Negative tests for invariants and roles  



------------------------------------------------------------

8.3 Bootstrap Integration Validation  

------------------------------------------------------------

Confirms:



\- Cross-agent harmony  

\- CE discipline  

\- Deterministic routing  

\- EIL compliance  

\- Governance enforcement  



============================================================

9\. DEVELOPMENT POLICIES (NON-NEGOTIABLE)

============================================================



\- No agent may add new capabilities without SYSTEM\_DESIGN.  

\- All artifacts must be single-block, complete, versioned, with file paths.  

\- No speculative or partial implementations.  

\- All changes must preserve Truth Hierarchy compliance.  

\- Governance always supersedes convenience.  



============================================================

10\. ROADMAP ALIGNMENT (Phase 0 → Phase 5)

============================================================



Phase 0 — Baseline v1.7  

Phase 1 — Hardening \& Regression  

Phase 2 — Intelligence Update  

Phase 2.5 — External Intelligence Layer (EIL)  

Phase 3 — Data Update  

Phase 4 — v2.0 Cloud Architecture  

Phase 5 — v2.1 Enterprise Features  



============================================================

11\. COMPLETE AGENT PROMPT BUNDLE (REFERENCES)

============================================================



\- architect\_system\_prompt\_v2.0.md  

\- router\_system\_prompt\_v2.0.md  

\- estimator\_system\_prompt\_v2.0.md  

\- validator\_system\_prompt\_v2.0.md  

\- merge\_agent\_system\_prompt\_v2.0.md  

\- material\_manager\_system\_prompt\_v2.0.md  

\- bootstrap\_prompt\_v2.0.md  



All files are governed, versioned, and aligned with this handover.



============================================================

12\. SYSTEM GUARANTEES UNDER v2.0

============================================================



\- Deterministic multi-agent behavior  

\- Strict CE-bounded estimating  

\- Zero hallucinated structure  

\- Role purity and cross-agent discipline  

\- EIL strictly advisory  

\- Governance invariants always in force  



============================================================

13\. HANDOVER COMPLETION

============================================================



This document completes the full Valesco v2.0 system handover.  

It is the authoritative reference for maintenance, evolution, and architectural integrity.



Version: 2.0.0 — Final.



