\# CE Missing Item Behaviour — Integration Test Plan v2.1



\## Test Objectives

\- Verify that Router, Architect, Estimator, Validator, Merge Agent, Material Manager, and CE Retrieval Layer conform precisely to the behaviour states defined in `ce\_missing\_item\_behaviour\_v2.1.md`.  

\- Ensure no hallucinated materials, quantities, compatible alternatives, or inferred attributes are ever surfaced.  

\- Confirm strict use of permitted CE signals only: \*\*hit\_count\*\*, \*\*top\_score\*\*, \*\*score\_gap\_to\_next\*\*, \*\*coverage\_flags\*\*.



---



\## Test Environment \& Assumptions

\- CE Retrieval Layer is replaced by a controlled mock emitting only the allowed signals; embeddings, vectors, or similarity internals are inaccessible.  

\- All surfaced items, metadata, and compatibility alternatives originate from a predefined, fixed test library subset.  

\- Tests evaluate agents strictly as black-box components; no reliance on LLM internals or model reasoning paths.  

\- All expectations are deterministic and bounded by the reference specification.



---



\## State-Based Scenario Matrix (A–E)



\### State A — Clean Match

\*\*Scenario A1\*\*  

\- \*\*Signals\*\*: hit\_count=1; top\_score above high-confidence threshold; coverage\_flags=strong.  

\- \*\*Expected\*\*: Router selects State A; Architect outputs exactly one item; Estimator receives “high confidence” message; no alternatives or extra attributes.  



\*\*Scenario A2\*\*  

\- \*\*Signals\*\*: hit\_count=2 but score\_gap\_to\_next is large and top\_score meets clean threshold; coverage\_flags=strong.  

\- \*\*Expected\*\*: Only the top item shown; second item suppressed; deterministic clean-match messaging.



\*\*Scenario A3\*\*  

\- \*\*Signals\*\*: hit\_count≥1 with extremely strong category coverage and dominant top\_score.  

\- \*\*Expected\*\*: Same as above; no ambiguity messaging; no inferred metadata.



---



\### State B — Closest Internal Matches (Top 3)

\*\*Scenario B1\*\*  

\- \*\*Signals\*\*: hit\_count≥3; top\_score below clean threshold; score\_gap\_to\_next < ambiguity boundary.  

\- \*\*Expected\*\*: Exactly top 3 items presented; clear ambiguity label; no merged/hybrid hints.



\*\*Scenario B2\*\*  

\- \*\*Signals\*\*: hit\_count=5; modest top\_score; narrow dispersion among first three results.  

\- \*\*Expected\*\*: Only top 3 results surfaced; Estimator instructed to choose; no fourth or fifth item included.



\*\*Scenario B3\*\*  

\- \*\*Signals\*\*: hit\_count≥1 with mid-level coverage\_flags indicating moderate category alignment but not sufficient for clean match.  

\- \*\*Expected\*\*: Ambiguous set of top 3; no artificial narrowing; no suggested attributes.



---



\### State C — Insufficient Retrieval Context

\*\*Scenario C1\*\*  

\- \*\*Signals\*\*: hit\_count≥1; coverage\_flags=weak or partial; ambiguous category signal.  

\- \*\*Expected\*\*: Clarification request; minimal retrieved context allowed; no item selection.



\*\*Scenario C2\*\*  

\- \*\*Signals\*\*: hit\_count=2; coverage\_flags indicate conflicting category evidence.  

\- \*\*Expected\*\*: Estimator prompted for missing information; no alternatives and no inferred guesses.



\*\*Scenario C3\*\*  

\- \*\*Signals\*\*: hit\_count≥1 but top\_score and score\_gap\_to\_next indicate unstable retrieval.  

\- \*\*Expected\*\*: Architect outputs clarification form only; no item surfaced.



---



\### State D — No Internal Match

\*\*Scenario D1\*\*  

\- \*\*Signals\*\*: hit\_count=0.  

\- \*\*Expected\*\*: “No internal match” message; Estimator asked to revise description; zero alternatives.



\*\*Scenario D2\*\*  

\- \*\*Signals\*\*: hit\_count=0; coverage\_flags=none.  

\- \*\*Expected\*\*: Same as above; no fallback suggestions; strict enforcement of absence of match.



\*\*Scenario D3\*\*  

\- \*\*Signals\*\*: hit\_count=0 with deliberately ambiguous estimator input.  

\- \*\*Expected\*\*: Request for clearer description; no invented materials.



---



\### State E — Compatible Alternatives

\*\*Scenario E1\*\*  

\- \*\*Signals\*\*: hit\_count≥1; coverage\_flags indicate correct category but insufficient item-level confidence.  

\- \*\*Expected\*\*: Compatible alternatives surfaced strictly from library compatibility rules; estimator required to choose.



\*\*Scenario E2\*\*  

\- \*\*Signals\*\*: top\_score moderate; score\_gap\_to\_next wide; category certainty strong.  

\- \*\*Expected\*\*: Architect shows validated alternatives; no clean-match framing.



\*\*Scenario E3\*\*  

\- \*\*Signals\*\*: hit\_count≥1 with multiple category-compatible candidates but low certainty for any singular item.  

\- \*\*Expected\*\*: Clear alternatives list; no probability-driven ranking.



---



\## Cross-Agent Flow Tests



\### Flow A — Clean Match End-to-End

\- \*\*Input\*\* → CE mock outputs high-confidence signals.  

\- \*\*Router\*\* → selects State A.  

\- \*\*Architect\*\* → emits deterministic clean-match structure.  

\- \*\*Estimator\*\* → receives single item, confirms.  

\- \*\*Validator\*\* → checks consistency with signals.  

\- \*\*Merge Agent / Material Manager\*\* → attach only the approved item.



\### Flow B — Ambiguous Match (Top 3)

\- CE mock emits multi-hit ambiguous signals.  

\- Router selects State B.  

\- Architect formats three-item list.  

\- Estimator chooses one.  

\- Validator ensures match-to-signal fidelity.  

\- Merge Agent integrates chosen item; Material Manager provides metadata only from test library.



\### Flow C — Insufficient Context

\- CE mock provides partial coverage.  

\- Router enters State C.  

\- Architect generates clarification request.  

\- Estimator supplies required data.  

\- Validator confirms no disallowed content.  

\- Merge Agent performs no merge until re-run after clarification.



\### Flow D — No Match

\- CE mock returns hit\_count=0.  

\- Router selects State D.  

\- Architect outputs no-match message.  

\- Estimator revises input.  

\- Validator confirms no alternatives shown.  

\- Merge Agent remains idle.



\### Flow E — Compatible Alternatives

\- CE mock signals category certainty but low item certainty.  

\- Router selects State E.  

\- Architect lists compatibility-rule-derived alternatives only.  

\- Estimator chooses or rejects.  

\- Validator enforces rule compliance.  

\- Material Manager surfaces metadata for chosen alternative only.



---



\## Negative \& Safety Tests

\- \*\*Attempt to access embeddings/vectors\*\* → System blocks request; violation reported; no estimator-facing content.  

\- \*\*Speculative material generation\*\* → Blocked; zero items surfaced; violation flagged.  

\- \*\*External substitute suggestions\*\* → Rejected; no output beyond violation message.  

\- \*\*Dynamic policy rewriting or probabilistic branching\*\* → Rejected; strict adherence to fixed spec enforced.  



---



\## Acceptance Criteria

\- All states A–E validated with deterministic expected outcomes: entry criteria, required action, disallowed behaviours, and handoff paths.  

\- No scenario allows items or alternatives outside CE retrieval results or compatibility rules.  

\- Any agent deviation from the reference spec must cause at least one test to fail.  

\- No YAML, no governance modifications, no meta-rules.



---



\## Non-Acceptable Outcomes

\- Non-deterministic expectations or fuzzy “usually” behaviour.  

\- Tests relying on introspection of LLM internals or vector space operations.  

\- Scenarios that allow fallback guessing, inferred substitutes, or hallucinations.

