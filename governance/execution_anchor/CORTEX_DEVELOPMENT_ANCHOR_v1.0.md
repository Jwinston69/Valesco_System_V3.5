Cortex Development Anchor v1.0



(Layered, Non-Superseding, Phase-Scoped)



1\. Status and Authority of This Document



Document Type: Development Anchor

Version: v1.0

Scope: Snapshot v3.5.1 (“The Pivot”) → Cortex v1.x completion

Authority Level: Non-governing, non-superseding



This document:



Does not replace:



VALESCO\_ROADMAP\_v2.0.md



VALESCO\_SYSTEM\_MANIFEST\_v1.9.1.md



Context Engineering Addendum



Does not introduce new governance, authority, or truth rules



Does not redefine the long-term system trajectory



This document exists solely to:



Anchor near-term development execution following the Cortex pivot already authorised by Snapshot v3.5.1.



If any conflict is perceived between this document and an upstream roadmap or manifest, the upstream document prevails.



2\. Starting State (Explicit Anchor)



Development under this anchor begins from the following verified system state:



Snapshot: v3.5.1 — The Pivot



Estimator Runtime: Active



Cortex: Authorised but unimplemented



AI Guidance Contracts:



Option Selection v2 — Active



Missing-Item Routing v2 — Active



Variant Generation v2 — Active



Learning Memory: Disabled



ELI / Resource Builder: Suspended



No work under this anchor may assume:



existing Cortex logic,



AI reasoning,



Learning Memory availability.



3\. Intended End State (Local, Not Global)



The end state of this anchor is not “Valesco v2.0 complete”.



The end state is narrowly defined:



Cortex exists as a production-safe, contract-compliant subsystem capable of supporting AI-guided decision-making under existing governance.



Specifically:



Cortex interfaces are implemented and stable



Contracts are enforced structurally and at runtime



Deterministic (non-AI) behaviour exists as a baseline



AI reasoning may be enabled without altering interfaces or governance



ELI / Resource Builder can be reintegrated or formally retired under the same authority model



4\. Phased Development Path (Binding Locally)

Phase 1 — Cortex v1.0: Interface Materialisation



Objective: Make Cortex real without making it smart.



Implement cortex\_v1\_0.py



Pydantic models only



Encodes:



inputs/outputs for the three AI contracts



decision metadata



evidence structures



No logic



No learning



No heuristics



Exit Criteria:



Estimator Runtime can import Cortex



Contract I/O round-trips succeed



No behavioural change to estimates



Phase 2 — Contract Enforcement Layer



Objective: Move rules from prompts into system behaviour.



System-derived confidence



Evidence count enforcement



Illegal state rejection



Snapshot binding validation



Explicitly forbidden:



AI reasoning



scoring



ranking logic



Phase 3 — Deterministic Baseline Behaviour



Objective: Establish a non-AI reference implementation.



Rule-based option ranking



Deterministic missing-item routing



Enumerated variant generation



This phase exists to:



validate contracts end-to-end



provide a baseline for later AI benefit measurement



Phase 4 — AI Reasoning Injection



Objective: Replace deterministic internals with AI-generated candidates.



AI produces candidate outputs only



System enforces contracts and confidence



Validator retains veto



No Learning Memory yet



Phase 5 — Learning Memory Activation



Objective: Introduce adaptability without eroding trust.



Preference + pattern learning first



Outcome learning last



Memory always snapshotted



Memory never alters contracts



5\. Drift Guards (Non-Negotiable)



During all phases:



Primer authority must not be modified



Snapshot must be updated at phase completion



No phase may:



collapse uncertainty



introduce silent learning



bypass validator



alter truth hierarchy



If a future change violates these, this anchor must be paused and reviewed.



6\. Relationship to Existing Roadmaps (Explicit)



This Development Anchor:



Implements a subset of the Valesco Roadmap



Does not advance version numbering



Does not redefine milestones



Think of it as:



A zoomed-in execution slice within the already-declared trajectory.

