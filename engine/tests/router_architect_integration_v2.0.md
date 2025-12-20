ROUTER–ARCHITECT INTEGRATION TEST SUITE  

Version: 2.0.0  

Status: final  

Scope: Step 27 — Integration Validation for Valesco v2.0



============================================================

0\. PURPOSE

============================================================



This suite verifies that the Router and Architect interact correctly under all governance and intent-routing rules defined in:



\- Truth Hierarchy v2.0  

\- Safety Invariants  

\- Canonical Intent Set v2.0  

\- Router System Prompt v2.0  

\- Architect System Prompt v2.0  



It confirms deterministic routing, correct subtype refinement, and the absence of role drift.



============================================================

1\. TEST BLOCK A — FILE\_GENERATION PATHWAYS

============================================================



A1 — Request for a system specification  

User: “Produce a specification for how the estimator handles grounded CE items.”  

Expected Router Intent: FILE\_GENERATION  

Expected Architect Subtype: FILE\_GENERATION.spec  



A2 — Request for a new estimator system prompt  

User: “Write the full Estimator v2.0 system prompt.”  

Expected Router Intent: FILE\_GENERATION  

Expected Architect Subtype: FILE\_GENERATION.estimator\_prompt  



A3 — Governance document request  

User: “Create a governance document describing CE chunk safety rules.”  

Expected Router Intent: FILE\_GENERATION  

Expected Architect Subtype: FILE\_GENERATION.governance\_doc  



A4 — Script request  

User: “Generate a script that loads the CE bundle and prints chunk counts.”  

Expected Router Intent: FILE\_GENERATION  

Expected Architect Subtype: FILE\_GENERATION.script  



A5 — Library-update artifact  

User: “Produce a material library update describing the new aggregates pack.”  

Expected Router Intent: FILE\_GENERATION  

Expected Architect Subtype: FILE\_GENERATION.library\_update  



A6 — Proposal export  

User: “Export this estimate as a client-facing proposal document.”  

Expected Router Intent: FILE\_GENERATION  

Expected Architect Subtype: FILE\_GENERATION.proposal\_export  



============================================================

2\. TEST BLOCK B — AMBIGUITY RESOLUTION

============================================================



B1 — Underspecified intent  

User: “Can you create something that explains how the system works?”  

Expected Router Intent: AMBIGUOUS  

Architect Resolution:  

\- Request clarification OR  

\- Choose FILE\_GENERATION.governance\_doc if context indicates documentation is intended.



B2 — Hybrid request  

User: “Explain the architecture and give me the file.”  

Expected Router Intent: AMBIGUOUS  

Architect Resolution:  

\- Split interpretation → likely FILE\_GENERATION.spec after clarifying required artifact.



============================================================

3\. TEST BLOCK C — SYSTEM DESIGN vs FILE GENERATION

============================================================



C1 — System design modification  

User: “Change how CE sparse retrieval rules work.”  

Expected Router Intent: SYSTEM\_DESIGN  

Architect Output: A structured proposal for updated CE rules (not a file unless user requests one).



C2 — System design + artifact  

User: “Update the task schema and produce the new schema file.”  

Expected Router Intent: SYSTEM\_DESIGN  

Architect Behavior:  

\- Perform design reasoning  

\- Wait for explicit FILE\_GENERATION request before producing the schema file



============================================================

4\. TEST BLOCK D — GOVERNANCE \& STATUS REQUESTS

============================================================



D1 — Governance query  

User: “List all safety invariants and explain how they apply.”  

Expected Router Intent: GOVERNANCE\_QUERY  

Architect Output: Authoritative description (no file output).



D2 — System status  

User: “What chunk counts are loaded?”  

Expected Router Intent: SYSTEM\_STATUS  

Architect Output: Report based only on session-visible state.



============================================================

5\. TEST BLOCK E — NEGATIVE ROLE DRIFT CASES

============================================================



E1 — Estimating request misrouted  

User: “Give me a rate for 120mm drainage trench.”  

Expected Router Intent: ESTIMATE\_REQUEST  

Architect MUST NOT handle. Router must correctly assign to ESTIMATOR.



E2 — Merge request misrouted  

User: “Combine these two proposals.”  

Expected Router Intent: MERGE\_REQUEST  

Architect MUST NOT handle.



E3 — Material update misrouted  

User: “Add a new topsoil material.”  

Expected Router Intent: MATERIAL\_MANAGEMENT  

Architect MUST NOT handle.



============================================================

6\. PASS/FAIL CRITERIA

============================================================



PASS when:

\- Router selects the correct canonical intent for all test cases.  

\- Architect correctly refines FILE\_GENERATION subtypes.  

\- Architect respects role boundaries.  

\- No prohibited inference, hallucination, or hidden state occurs.



FAIL when:

\- Router misclassifies an intent.  

\- Architect produces a file without explicit FILE\_GENERATION routing.  

\- Architect violates governance rules or assumes unprovided library data.



============================================================

7\. VERSIONING

============================================================



Version: 2.0.0  

Updates require explicit Architect-level SYSTEM\_DESIGN approval.



This concludes Step 27 — Router–Architect Integration Test Suite.



