# Phase 2 Implementation Readiness v0.1

## 1. Purpose

This document defines Phase 2.7 implementation readiness for the VALESCO BOQ / Excel workflow.

It is a planning document only. No functionality is implemented by this document. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, existing governance snapshots, the North Star document or existing planning documents.

The purpose of Phase 2.7 is to define what must be true before the first implementation work begins.

## 2. Current Authority

Current authority:

* `governance/SNAPSHOT v3.7.11.txt`
* tag `v3.7.11-runtime-reconciled`
* `docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx`
* `docs/planning/usable_boq_workflow_v0_1.md`
* `docs/planning/phase_2_delivery_plan_v0_1.md`
* `governance/phase_2/PHASE_2_SCOPE_LOCK_v0.1.md`
* `governance/phase_2/BOQ_WORKFLOW_PRINCIPLES_v0.1.md`
* `governance/phase_2/PHASE_2_RISK_EXCLUSION_REGISTER_v0.1.md`
* `docs/phase_2/CLIENT_BOQ_IMPORT_CONTRACT_v0.1.md`
* `docs/phase_2/BOQ_COLUMN_MAPPING_RULES_v0.1.md`
* `docs/phase_2/BOQ_IMPORT_VALIDATION_MATRIX_v0.1.md`
* `docs/phase_2/RESOURCE_ALLOCATION_SCHEMA_v0.1.md`
* `docs/phase_2/BOQ_PRICING_BUILDUP_RULES_v0.1.md`
* `docs/phase_2/RESOURCE_SOURCE_CONTROL_RULES_v0.1.md`
* `docs/phase_2/PRICING_EXPORT_WORKBOOK_SHAPE_v0.1.md`
* `docs/phase_2/BOQ_EXPORT_RULES_v0.1.md`
* `docs/phase_2/PRICING_WORKBOOK_REVIEW_CHECKLIST_v0.1.md`
* `docs/phase_2/VALIDATION_FAIL_CLOSED_RULES_v0.1.md`
* `docs/phase_2/VALIDATION_STATUS_MODEL_v0.1.md`
* `docs/phase_2/FAIL_CLOSED_REVIEW_CHECKLIST_v0.1.md`
* `docs/phase_2/SCENARIO_2_GENERATED_BOQ_FUTURE_SCOPE_v0.1.md`
* `docs/phase_2/GENERATED_BOQ_TRACEABILITY_REQUIREMENTS_v0.1.md`
* `docs/phase_2/SCENARIO_2_RISK_AND_EXCLUSION_REGISTER_v0.1.md`

Any conflict with current authority must be recorded and resolved through governance before coding.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Phase 2.7 implementation readiness | Planned | Defined by this document |
| First implementation slice | Planned | Defined separately in `FIRST_IMPLEMENTATION_SLICE_PLAN_v0.1.md` |
| Implementation handoff checklist | Planned | Defined separately in `IMPLEMENTATION_HANDOFF_CHECKLIST_v0.1.md` |
| Client-provided Excel BOQ import | Planned | First implementation priority |
| VALESCO-generated BOQ from tender documents | Planned later | Future scope only |
| Runtime implementation | Not implemented | No importer, validator or workflow is created by this document |
| Tests | Not implemented | No tests or fixtures are created or changed by this document |
| Existing runtime behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived behaviour | Archived only where separately recorded | Not reactivated by this document |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| AI authority | Inactive | Must not approve mapping, validation, pricing or export |
| Production CE backend reliance | Unknown / not proven | Must not be required for the first slice |

Implemented, tested, planned, archived and unknown states must remain distinct before and during implementation.

## 4. Priority Position

Client-provided Excel BOQ import is the first implementation priority.

The first implementation work should start with deterministic client BOQ workbook intake and validation foundations using artificial `.xlsx` fixtures. The original client workbook concept must be treated as source evidence, and every imported or rejected row must retain source traceability where the row is in scope.

Scenario 2, where VALESCO generates a BOQ from tender documents, remains a later priority and future scope only. Scenario 2 must not be included in the first implementation slice.

## 5. Implementation Entry Criteria

Implementation may begin only after the following entry criteria are satisfied and recorded in the handoff material:

| Ref | Entry criterion | Required evidence before coding |
| --- | --- | --- |
| EC-001 | Branch and base are confirmed | Working branch and latest `origin/main` commit recorded |
| EC-002 | Governance authority is confirmed | Current authority documents listed and checked for conflicts |
| EC-003 | First slice boundary is approved | Scope, exclusions and acceptance criteria recorded |
| EC-004 | Affected modules are identified | Candidate files, packages and ownership boundaries listed before editing code |
| EC-005 | Dependencies are identified | Excel parsing, workbook fixture and validation dependencies listed before use |
| EC-006 | Test strategy is identified | Planned test files, fixture policy and expected assertions listed before coding |
| EC-007 | Artificial fixtures policy is confirmed | `.xlsx` fixtures are synthetic and contain no client or tender data |
| EC-008 | Source traceability model is selected | Minimum workbook, worksheet, row and field trace requirements recorded |
| EC-009 | Validation statuses are selected | `pass`, `warning`, `fail`, `not_applicable`, `not_checked`, `unknown` and `excluded` treatment confirmed |
| EC-010 | Fail-closed behaviour is defined | Missing, invalid, unknown, blank and not-checked controls cannot pass |
| EC-011 | Estimator review visibility is defined | Warnings, failures, exclusions and review-required rows remain visible |
| EC-012 | Out-of-scope items are confirmed | Pricing, export, client return, generated BOQ, OCR, extraction, AI authority and production CE backend reliance excluded |

If any entry criterion is unresolved, implementation should not proceed beyond investigation and branch preparation.

## 6. First Implementation Boundary

The recommended first slice is deterministic client BOQ workbook intake and validation foundations.

It may include planning for future code that:

* accepts artificial `.xlsx` workbook fixtures only
* identifies workbook readability
* identifies workbook sheets
* applies controlled worksheet selection assumptions
* maps required BOQ columns where deterministic or explicitly configured
* captures source file, worksheet and row traceability
* validates required description, unit and quantity fields
* records validation statuses and messages
* records blocked, warning, excluded and review-required rows visibly
* fails closed where required evidence is missing, invalid, unknown, blank or not checked

It must not include pricing, export, client return, generated BOQ, OCR, tender document extraction, AI authority, production CE backend reliance or real client/tender data.

## 7. Required Pre-Coding Identification

Before coding starts, the implementer must identify and record:

* affected modules and files
* any new modules proposed
* any existing modules that must remain untouched
* dependencies required for `.xlsx` parsing and fixture handling
* whether dependencies are already present or require approval
* governance documents that control the implementation
* tests to create or update
* artificial fixture filenames and contents at a non-sensitive level
* expected fail-closed behaviours and assertions
* any architectural risk or boundary question

This identification step is mandatory because the planning documents do not themselves authorize broad architecture, engine, library, bin, workspace or runtime changes.

## 8. Required Controls

Future implementation must preserve these controls:

* source traceability from workbook to worksheet to row
* visible validation statuses and messages
* visible estimator review requirements
* visible exclusions and blocked rows
* fail-closed treatment for missing, invalid, unknown, blank and not-checked evidence
* separation between client-originated source values and VALESCO working values
* artificial fixture-only repository data
* no AI approval or pricing authority
* no production CE backend dependency for the first slice
* no claim that planning means implementation or testing exists

## 9. First Slice Exclusions

The first implementation slice excludes:

* pricing implementation
* pricing build-up calculations
* workbook export implementation
* client return generation
* client-facing tender return output
* generated BOQ from tender documents
* document ingestion
* OCR
* tender document extraction
* measurement from drawings or specifications
* AI authority or AI-approved mappings
* production CE backend reliance
* real client BOQs
* real tender documents
* client-identifying data
* tender returns
* commercial rates
* supplier quotations
* project-specific sensitive information

## 10. Open Decisions

| Ref | Decision | Required before coding |
| --- | --- | --- |
| OD-001 | Exact code modules and ownership boundaries for workbook intake | Yes |
| OD-002 | Approved `.xlsx` parsing dependency or existing library path | Yes |
| OD-003 | Synthetic fixture directory and naming convention | Yes |
| OD-004 | Minimal internal row object or schema shape for imported rows | Yes |
| OD-005 | Whether column mapping is configuration-driven or hard-coded for fixtures | Yes |
| OD-006 | Exact validation status enum names and message format | Yes |
| OD-007 | Estimator review marker format for first slice outputs | Yes |
| OD-008 | Test runner and assertion pattern to use | Yes |
| OD-009 | Whether any existing runtime entry point is touched or avoided | Yes |
| OD-010 | Documentation evidence required before implementation starts | Yes |

## 11. Acceptance Criteria

This readiness document is acceptable when:

* client-provided Excel BOQ import is confirmed as first implementation priority
* Scenario 2 generated BOQ remains later priority and future scope only
* implementation entry criteria are defined
* affected modules, dependencies, governance documents and tests must be identified before coding
* source traceability, visible validation, estimator review and fail-closed behaviour are required
* the recommended first slice uses deterministic client BOQ workbook intake and validation foundations with artificial `.xlsx` fixtures
* pricing, export, client return, generated BOQ, OCR, extraction, AI authority and production CE backend reliance are excluded from the first slice
* implemented, tested, planned, archived and unknown states remain distinct
* no functionality is claimed as implemented
* no sensitive client or tender data is introduced
