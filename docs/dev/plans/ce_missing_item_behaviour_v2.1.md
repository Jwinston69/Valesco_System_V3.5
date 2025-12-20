\# CE Missing Item Behaviour v2.1



\## Purpose

\- Prevent dead-end flows and guarantee recoverable behaviour paths.  

\- Ensure consistent, predictable estimator-facing outputs across all agents.  

\- Eliminate hallucinations by mandating strict CE-driven responses only.  

\- Maintain accuracy through deterministic, library-bound retrieval logic.



---



\## Scope and Actors



\### Router

\- Determines initial retrieval route and selects the correct behaviour state based solely on CE signals.  

\- Enforces state transitions without generating content outside retrieved context.



\### Architect

\- Interprets Router-selected state and applies system-defined transformation rules.  

\- Ensures structural correctness while avoiding inference beyond CE-permitted information.



\### Estimator

\- Receives clear, deterministic messages indicating match quality and required user decisions.  

\- Never receives invented materials, quantities, or alternatives not grounded in CE retrieval.



\### Validator

\- Confirms the selected state is consistent with CE signals and blocking rules.  

\- Prevents leakage of unverified or non-retrieved information.



\### Merge Agent

\- Integrates estimator-confirmed items with internal structures while preserving CE-driven boundaries.  

\- Rejects any content not derived from permitted states and retrieval signals.



\### Material Manager

\- Supplies accurate catalogue metadata for retrieved items and compatible alternatives.  

\- Does not generate inferred or speculative materials.



\### CE Retrieval Layer

\- Produces strictly bounded retrieval signals: hit\_count, top\_score, score\_gap\_to\_next, coverage\_flags.  

\- Never exposes embeddings, vectors, similarity internals, or algorithmic details.



---



\## CE Retrieval Signals

Permitted signals:

\- \*\*hit\_count\*\* — number of viable matches returned.  

\- \*\*top\_score\*\* — normalized similarity score of the highest-ranked item.  

\- \*\*score\_gap\_to\_next\*\* — difference between top and second result for stability checks.  

\- \*\*coverage\_flags\*\* — category-level indicators describing retrieval confidence.



Agents may \*\*not\*\*:

\- Inspect embeddings, vector data, model internals, or similarity algorithm mechanics.  

\- Infer or compute any additional retrieval metrics not explicitly defined above.



---



\## Behaviour States (Deterministic)



\### State A — Clean Match

\*\*Entry Conditions\*\*

\- hit\_count ≥ 1  

\- top\_score exceeds state threshold and score\_gap\_to\_next satisfies confidence requirements  

\- coverage\_flags indicate high category certainty  



\*\*Required Estimator-Facing Action\*\*

\- Present the single matched item deterministically with no alternatives.  

\- Communicate that the system has high confidence and no estimator correction is required.



\*\*Disallowed Behaviour\*\*

\- Generating embellishments, inferred material properties, or speculative descriptions.



\*\*Handoff Guidance\*\*

\- Architect prepares clean match output; Estimator confirms or overrides explicitly.



---



\### State B — Closest Internal Matches (Top 3)

\*\*Entry Conditions\*\*

\- hit\_count ≥ 1  

\- top\_score is below clean-match threshold or score\_gap\_to\_next indicates ambiguity  



\*\*Required Estimator-Facing Action\*\*

\- Present top three candidates exactly as retrieved, with clear ambiguity messaging.  

\- Require the estimator to select the correct item or request further narrowing.



\*\*Disallowed Behaviour\*\*

\- Merging candidates, inferring hybrids, or suggesting items not present in the top three.



\*\*Handoff Guidance\*\*

\- Architect renders comparison structure; Router ensures no additional items are introduced.



---



\### State C — Insufficient Retrieval Context

\*\*Entry Conditions\*\*

\- hit\_count ≥ 1 but coverage\_flags indicate weak or incomplete category fit  

\- Retrieval content is too broad or vague for safe item selection  



\*\*Required Estimator-Facing Action\*\*

\- Ask the estimator for clarification needed to disambiguate the category or item attributes.  

\- Provide only the retrieved subset demonstrating ambiguity without fabricating details.



\*\*Disallowed Behaviour\*\*

\- Using incomplete signals to guess an item or propose unsourced technical attributes.



\*\*Handoff Guidance\*\*

\- Architect produces clarification-request template; Estimator provides missing information.



---



\### State D — No Internal Match

\*\*Entry Conditions\*\*

\- hit\_count = 0  

\- No safe match within library scope  



\*\*Required Estimator-Facing Action\*\*

\- Inform the estimator that no internal match exists and request a revised description.  

\- State explicitly that no alternative can be suggested without CE-validated retrieval.



\*\*Disallowed Behaviour\*\*

\- Inventing materials, inferring categories, proposing external-domain substitutes.



\*\*Handoff Guidance\*\*

\- Router declares retrieval failure; Estimator supplies new or corrected input.



---



\### State E — Compatible Alternatives

\*\*Entry Conditions\*\*

\- hit\_count ≥ 1  

\- coverage\_flags indicate category alignment but insufficient item-level confidence  

\- System identifies alternative items strictly within predefined compatibility rules  



\*\*Required Estimator-Facing Action\*\*

\- Present compatible alternatives validated by library metadata and compatibility rules.  

\- Explain that alternatives are category-compatible but require estimator selection.



\*\*Disallowed Behaviour\*\*

\- Generating alternatives that exceed library metadata or compatibility definitions.



\*\*Handoff Guidance\*\*

\- Architect outputs structured alternatives; Estimator selects or rejects.



---



\## Acceptance Criteria

\- Deterministic, role-contained behaviour with no agent-role leakage.  

\- No new governance models, meta-frameworks, or outside-scope rule systems.  

\- Directly reinforces estimator correctness and CE safety boundaries.  

\- Immediately usable by Architect, Router, and CE Retrieval Layer.  

\- Contains no YAML, dynamic policy generation, or probabilistic elements.



---



\## Negative Conditions

\- Reject any behaviour requiring access to vectors, embeddings, or model internals.  

\- Reject probabilistic or open-ended decision paths.  

\- Reject dynamic rule synthesis, meta-policies, or runtime policy rewriting.

