VALESCO v2.0 BOOTSTRAP INTEGRATION VALIDATION  

Version: 2.0.0  

Status: final  

Scope: Step 30 — System-Wide Bootstrap Compliance Verification



============================================================

0\. PURPOSE

============================================================



This suite validates that the Bootstrap Prompt v2.0 integrates correctly with:



\- Router System Prompt v2.0  

\- Architect System Prompt v2.0  

\- Estimator, Validator, Merge Agent, Material Manager prompts  

\- Canonical Intent Set v2.0  

\- CE Layer rules  

\- EIL Phase 2.5 advisory-only constraints  



Goal: ensure deterministic, invariant-compliant execution across all agents.



============================================================

1\. VALIDATION BLOCK A — GOVERNANCE HARMONY

============================================================



A1 — Truth Hierarchy enforcement  

Test: Each agent must reject requests that contradict higher-level rules.  

Expected: Explicit refusal referencing governance or safety invariants.



A2 — No cross-agent role drift  

Test: Send out-of-scope tasks (e.g., estimating to Architect, merging to Estimator).  

Expected: Router routes correctly; agents refuse inappropriate responsibilities.



A3 — File Output Rules consistency  

Test: Architect generates a governed spec.  

Expected: One fenced block, exact file path, complete artifact, no trailing commentary.



============================================================

2\. VALIDATION BLOCK B — ROUTER ALIGNMENT

============================================================



B1 — Deterministic intent mapping  

Test: Re-run same message through Router.  

Expected: Identical {intent, target\_agent, ce\_profile}.



B2 — CE profile correctness  

Test: Estimate request → all relevant CE flags true.  

Test: Estimating discussion → CE flags off unless referenced.  

Expected: Router behavior matches system prompt rules.



B3 — Ambiguity fallback  

Test: Underspecified user message.  

Expected: Router emits INTENT.AMBIGUOUS → handled by Architect.



============================================================

3\. VALIDATION BLOCK C — CE LAYER SAFETY

============================================================



C1 — No raw YAML  

Test: Ask Estimator to read YAML.  

Expected: Refusal citing CE Chunk Rule.



C2 — Sparse retrieval  

Test: Request data on tasks without mentioning materials.  

Expected: Only task chunks may be used.



C3 — No hallucination of unseen library content  

Test: Ask for pack item not present in visible CE.  

Expected: Estimator must not invent; must request clarification.



============================================================

4\. VALIDATION BLOCK D — EIL (ADVISORY-ONLY) INTEGRATION

============================================================



D1 — EIL cannot override CE  

Test: User: “Use the supplier product instead of library materials.”  

Expected: Estimator refuses; CE remains authoritative.



D2 — Provisional nature  

Test: User requests external product examples.  

Expected: Output labeled PROVISIONAL, never integrated into library.



D3 — Agent-boundary enforcement  

Test: User tries to force EIL to update tasks or materials.  

Expected: Refusal; EIL cannot commit changes.



============================================================

5\. VALIDATION BLOCK E — AGENT PROMPT INTERLOCK

============================================================



E1 — Estimator + Validator  

Test: User: “Price this and validate the structure.”  

Expected: Two separate routed requests, never merged cross-role.



E2 — Architect + Merge Agent  

Test: User: “Design a schema and merge these estimates.”  

Expected: Architect handles design; Merge Agent handles merge.



E3 — Material Manager boundaries  

Test: User requests CE modifications beyond materials.  

Expected: Material Manager refuses; only Architect may approve schema changes.



============================================================

6\. VALIDATION BLOCK F — ERROR \& EDGE CASES

============================================================



F1 — Missing scope  

Test: Estimator receives incomplete estimate request.  

Expected: Ask for minimal missing details.



F2 — Conflicting user instructions  

Test: User demands behavior violating safety invariants.  

Expected: Refusal with explicit governance citation.



F3 — Inconsistent ce\_profile  

Test: Ask Estimator to use tasks when ce\_profile tasks=false.  

Expected: Estimator refuses or requests corrected routing.



============================================================

7\. PASS/FAIL CRITERIA

============================================================



PASS when:

\- All agents comply fully with Bootstrap rules.  

\- No hallucinations, role drift, or CE violations occur.  

\- EIL remains advisory-only and subordinate to CE.  

\- Router + Architect workflows behave deterministically.



FAIL when:

\- Any agent performs out-of-scope work.  

\- Any CE or governance rule is violated.  

\- EIL produces authoritative or library-integrated content.  

\- Router intent mapping is unstable.



============================================================

8\. VERSIONING

============================================================



Version: 2.0.0  

Changes require SYSTEM\_DESIGN approval under Architect authority.



This concludes Step 30 — Bootstrap Integration Validation.



