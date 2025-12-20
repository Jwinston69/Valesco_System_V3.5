\# Pricing Engine Expansion Plan v3.0 (Phase 3B — Operational Roadmap)



\*\*Purpose:\*\* Define the build-oriented plan for evolving the MVP pricing subsystem into a full production pricing engine.  

\*\*Scope:\*\* Operational roadmap only — no new pricing rules, no behavioural specification.



---



\## 1. Objectives of the Production Pricing Engine



The production pricing engine will:



\- \*\*Replace static mock unit rates\*\* used in the MVP with a structured, external, and maintainable rate library.  

\- \*\*Integrate multiple cost components\*\* (material, labour, plant, overhead, and other chargeable elements) in a controlled, auditable way.  

\- \*\*Support packs/assemblies\*\* in later 3.x phases, allowing grouped items to be priced as composed structures rather than isolated lines.  

\- \*\*Maintain strict determinism and CE-safety\*\*, ensuring identical inputs always produce identical pricing outputs, with no CE signal usage.  

\- \*\*Avoid inference of missing data\*\*, ensuring that missing rates or quantities block pricing instead of being guessed.  

\- \*\*Prevent hallucinated rates or productivity\*\*, so that every cost is traceable to a defined, explicit rate record and quantity.



---



\## 2. Required Inputs for Real Pricing



The production pricing engine will only work with data coming from upstream modules in structured form. Required inputs:



\- \*\*Confirmed catalog item metadata\*\*  

&nbsp; - Item ID, name, category, and raw attributes from the internal catalog/Material Manager.  

&nbsp; - No CE signals, embeddings, or similarity metrics.



\- \*\*User-supplied quantity\*\*  

&nbsp; - Numeric quantity attached via the Quantity Logic layer.  

&nbsp; - No geometric interpretation, takeoff, or inferred quantities.



\- \*\*Structured rate library (future component)\*\*  

&nbsp; - Deterministic records for material, labour, plant, overhead, and assembly/packs.  

&nbsp; - Versioned and auditable, with explicit IDs and fields for each cost component.



\- \*\*Optional allowance overrides\*\*  

&nbsp; - Explicit, user-supplied allowance values (e.g., lump sums or per-line adjustments).  

&nbsp; - Stored and applied as overrides, not as inferred or derived rates.



The production pricing engine must \*\*not\*\* accept:



\- CE signals or routing information.  

\- Estimator “guesses” or heuristic rates.  

\- Any implicit or inferred productivity factors.



---



\## 3. Pricing Engine Architecture (High-Level)



The production engine will be structured into three core layers:



\### 3.1 Rate Retrieval Layer



Responsibilities:



\- \*\*Read the structured rate library\*\* (future Phase 3B module) using deterministic lookups by rate ID or item-to-rate mapping.  

\- Provide \*\*pure retrieval\*\* of rate records: material, labour, plant, overhead, and assembly definitions.  

\- Ensure \*\*deterministic behaviour\*\*: same item and context → same rate set, with no probabilistic or heuristic variation.  

\- Perform no CE logic, no enrichment, and no interpretation of catalog attributes.



\### 3.2 Rate Build-Up Layer



Responsibilities:



\- \*\*Combine cost components\*\* into composed unit rates and extended costs:

&nbsp; - Material cost

&nbsp; - Labour cost

&nbsp; - Plant cost

&nbsp; - Overhead and margin components (where applicable)

\- Use \*\*strict deterministic formulas\*\* defined in the rate library or configuration (e.g., sum of components, fixed markups).  

\- Allow build-up \*\*only when all required components\*\* for a given rate are present and valid.  

\- If any component is missing, mark the item as “incomplete pricing” rather than approximating.  

\- Avoid:

&nbsp; - Any assumptions about missing pieces.

&nbsp; - Productivity models or derived productivity.

&nbsp; - Statistical or regression-based costing.



\### 3.3 Estimate Assembly Layer



Responsibilities:



\- \*\*Apply quantities\*\* from the Quantity Logic layer to built-up unit rates to compute:

&nbsp; - Per-line extended totals.

&nbsp; - Subtotals and rolled-up totals (e.g., by category, by work section, or full estimate total).

\- Maintain clear handling of \*\*provisional lines\*\*:

&nbsp; - Flagged as “user-supplied only” with no internal rate calculation.

\- Provide \*\*deterministic rollups\*\* that sum known costs without introducing assumptions or smoothing.



---



\## 4. Integration Plan (MVP → Production)



Migration from MVP pricing to the production pricing engine will proceed in discrete, backward-compatible steps:



1\. \*\*Introduce Rate Library Ingestion Pipeline\*\*

&nbsp;  - Implement a dedicated ingestion module for rate records (material, labour, plant, overhead, assemblies).

&nbsp;  - Use a similar pattern to the catalog ingestion pipeline (v3.x) with deterministic normalization and validation.



2\. \*\*Replace Mock Pricing Table with Library-Backed Lookups\*\*

&nbsp;  - Swap the current `MOCK\_PRICING` structure with the Rate Retrieval Layer.

&nbsp;  - Maintain the same external pricing API surface (for MVP callers) initially, to avoid breaking Estimator Runtime and Runner.



3\. \*\*Introduce Rate Build-Up Logic (v3.x)\*\*

&nbsp;  - Implement the Rate Build-Up Layer that reads atomic rate records and composes full unit rates.

&nbsp;  - Start with simple additive models, ensuring full traceability from item to each cost component.



4\. \*\*Introduce Assembly-Level Rollups\*\*

&nbsp;  - Extend the engine to support assemblies/packs as grouped items referencing multiple underlying catalog items and rate records.

&nbsp;  - Ensure per-assembly costs are deterministic and traceable.



5\. \*\*Maintain Backward Compatibility with MVP Runner\*\*

&nbsp;  - Keep the MVP Runner’s interfaces stable (quantities, line items, pricing outputs).

&nbsp;  - Internally route existing calls to the new pricing engine, preserving behaviour for existing tests.



6\. \*\*Enhance Test Suites\*\*

&nbsp;  - Add test suites for:

&nbsp;    - Rate library ingestion.

&nbsp;    - Component-level rate build-up.

&nbsp;    - Assembly/pack pricing.

&nbsp;    - Cross-checks against known reference estimates.

&nbsp;  - Ensure all new tests respect non-inference and CE-safety constraints.



7\. \*\*Keep Non-Inference Alignment\*\*

&nbsp;  - Explicitly verify that missing data in rate library or quantities results in blocked pricing (e.g., “rate\_required” or “quantity\_required”), not approximated values.



---



\## 5. Determinism \& Safety Rules



The production pricing engine must preserve and extend the MVP’s determinism and safety guarantees:



\- \*\*No inferred material → labour mappings\*\*

&nbsp; - No automatic assumptions such as “this material always requires X labour hours per unit” unless explicitly encoded in the rate library.



\- \*\*No dynamic productivity models\*\*

&nbsp; - No runtime learning, regression fits, or statistical adjustments of rates based on historical data.



\- \*\*No statistical costing\*\*

&nbsp; - No averages, trend predictions, or probabilistic cost ranges as substitutes for missing rate records.



\- \*\*No substitution logic\*\*

&nbsp; - No automatic replacement of missing items with similar catalog items or rates.



\- \*\*No estimator heuristics inside the engine\*\*

&nbsp; - Estimator decisions remain separate and user-driven; the pricing engine only applies explicit rates and quantities.



\- \*\*Missing data must block pricing\*\*

&nbsp; - When required rate components or quantities are absent, the engine must surface explicit “pricing incomplete” states instead of interpolating or guessing.



These constraints are operational guardrails for implementation and testing, not a new pricing specification.



---



\## 6. Acceptance Criteria for Phase 3B Pricing Engine



The Phase 3B production pricing engine will be considered ready when all of the following conditions are met:



\- \*\*Deterministic, library-sourced rates\*\*

&nbsp; - Catalog items are priced using rate records from the structured rate library, with no fallback to hardcoded mocks.



\- \*\*Correct rate build-ups\*\*

&nbsp; - Material, labour, plant, and overhead components are combined using documented deterministic formulas.

&nbsp; - Assembly/packs (where implemented) correctly aggregate underlying components.



\- \*\*Provisional item handling\*\*

&nbsp; - Provisional lines are handled with explicit “user-supplied only” pricing, with no internal rate assumptions.



\- \*\*Deterministic test coverage\*\*

&nbsp; - All pricing-related unit tests, integration tests, and end-to-end tests pass repeatedly with identical outputs.



\- \*\*No estimator behavioural changes\*\*

&nbsp; - Estimator Runtime behaviour, messaging patterns, and interaction flows remain unchanged; only underlying pricing mechanics evolve.



\- \*\*CE safety \& non-inference preserved\*\*

&nbsp; - No CE signals are consumed by the pricing engine.

&nbsp; - No new inference or hallucinated productivity/rates are introduced during the pricing process.



When these conditions are satisfied, the system will be ready to support production-level pricing while staying aligned with Phase 3 CE and catalog integrations.



