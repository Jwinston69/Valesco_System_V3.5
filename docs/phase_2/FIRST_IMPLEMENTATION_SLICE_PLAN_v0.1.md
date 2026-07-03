# First Implementation Slice Plan v0.1

## 1. Purpose

This document defines the recommended first implementation slice for Phase 2 after implementation readiness is accepted.

It is a planning document only. No functionality is implemented by this document. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, existing governance snapshots, the North Star document or existing planning documents.

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
* `docs/phase_2/PHASE_2_IMPLEMENTATION_READINESS_v0.1.md`

Any conflict with current authority must be recorded and resolved through governance before coding.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| First implementation slice | Planned | Defined by this document |
| Client-provided Excel BOQ workbook intake | Planned | First implementation priority |
| Workbook validation foundations | Planned | First slice focus |
| Artificial `.xlsx` fixtures | Planned | Required for tests, not created by this document |
| Pricing | Not implemented / excluded | Not part of first slice |
| Export | Not implemented / excluded | Not part of first slice |
| Client return | Not implemented / excluded | Not part of first slice |
| VALESCO-generated BOQ from tender documents | Planned later / excluded | Future scope only |
| OCR and tender document extraction | Not implemented / excluded | Not part of first slice |
| Tests | Not implemented | No tests are created or changed by this document |
| Runtime behaviour | Not implemented | No runtime path changes are made |
| AI authority | Inactive | Must not approve import, validation or review |
| Production CE backend reliance | Unknown / not proven | Must not be required |
| Archived or unknown behaviour | Not active | Must not be treated as implemented or tested |

Implemented, tested, planned, archived and unknown states must remain distinct.

## 4. Priority Position

The first implementation priority is client-provided Excel BOQ import.

The recommended first slice is deterministic client BOQ workbook intake and validation foundations using artificial `.xlsx` fixtures. This slice should prove the lowest-risk foundation: a workbook can be read, controlled source traceability can be recorded, required fields can be validated and blocked rows remain visible.

Scenario 2 generated BOQ remains later priority and future scope only.

## 5. Recommended Slice Name

Recommended slice name:

`phase2/client-boq-intake-validation-foundation`

The requested working branch for this planning step is:

`phase2/implementation-readiness`

A future implementation branch may use the recommended slice name if approved.

## 6. Slice Objective

Create a deterministic foundation for importing an artificial client BOQ workbook into a controlled internal representation and producing visible validation outcomes.

The slice should answer these implementation questions:

* can the system read an artificial `.xlsx` workbook without relying on production CE backend services
* can the system identify workbook, worksheet and row evidence
* can required BOQ columns be selected deterministically for known artificial fixtures
* can required row fields be validated
* can failed, warning, excluded and review-required rows remain visible
* can missing, invalid, unknown, blank and not-checked statuses fail closed
* can tests prove this behaviour without real client or tender data

## 7. In Scope

The first implementation slice may include future code and tests for:

* reading artificial `.xlsx` fixture workbooks
* rejecting unreadable, unsupported or structurally invalid fixture workbooks
* identifying workbook-level metadata needed for source traceability
* identifying worksheet name and worksheet index where available
* selecting a known fixture worksheet deterministically
* mapping required fixture columns for item reference, description, unit and quantity
* preserving original description, unit and quantity values separately from any normalised values
* recording source file reference, source worksheet name and source row number
* validating required description, unit and quantity fields
* detecting blank, missing, invalid and non-numeric quantity values
* recording explicit validation status and validation messages
* recording rows blocked from pricing readiness
* recording warning rows and excluded rows with reasons
* exposing review-required outcomes for estimator review
* proving fail-closed outcomes through tests

## 8. Out of Scope

The first implementation slice excludes:

* pricing implementation
* pricing build-up rules execution
* resource allocation implementation beyond any placeholder status needed for validation boundaries
* workbook export implementation
* pricing workbook shape generation
* client return generation
* client-facing tender return output
* generated BOQ from tender documents
* tender document ingestion
* OCR
* document extraction
* measurement from drawings, specifications or schedules
* AI authority or AI-approved mappings, validation, pricing or review
* production CE backend reliance
* real client BOQs
* real tender documents
* client-identifying data
* tender returns
* commercial rates
* supplier quotations
* project-specific sensitive information
* changes to existing governance snapshots
* North Star edits
* existing planning document edits

## 9. Expected Artificial Fixture Types

Future implementation should use artificial `.xlsx` fixtures only.

Recommended fixture categories:

| Fixture | Purpose | Sensitive data rule |
| --- | --- | --- |
| `valid_minimal_client_boq.xlsx` | Proves required fields pass where present | Artificial values only |
| `missing_required_fields_client_boq.xlsx` | Proves blank description, unit or quantity fails closed | Artificial values only |
| `invalid_quantity_client_boq.xlsx` | Proves invalid quantity status and message | Artificial values only |
| `ambiguous_mapping_client_boq.xlsx` | Proves uncertain mapping requires review | Artificial values only |
| `hidden_or_merged_structure_client_boq.xlsx` | Proves structural warnings or failures are visible | Artificial values only |

Fixture filenames and contents must be approved before coding. No real client names, project names, quantities, rates, supplier quotations or tender details may be used.

## 10. Minimum Data Outputs

The first slice should produce or assert a controlled internal result containing at least:

| Field | Requirement |
| --- | --- |
| `source_file_ref` | Required for every imported row |
| `source_sheet_name` | Required for every imported row |
| `source_row_number` | Required for every imported row |
| `client_item_ref` | Required where provided by fixture |
| `description_original` | Required for pricing readiness |
| `unit_original` | Required for pricing readiness |
| `quantity_original` | Required for pricing readiness |
| `validation_status` | Required for every row |
| `validation_messages` | Required where warning, fail, excluded or review-required |
| `readiness_status` | Required to distinguish blocked and review-only outcomes |
| `estimator_review_required` | Required where human review is needed |
| `exclusion_reason` | Required where a row is excluded |

A row without required traceability, status or message evidence must not pass.

## 11. Validation Expectations

Future tests should prove:

* valid artificial rows can receive evidenced `pass` statuses for the checked gate
* blank descriptions fail closed
* blank or invalid units fail closed or require review according to the approved rule
* missing, blank, invalid or non-numeric quantities fail closed for pricing readiness
* `not_checked`, `unknown` and blank statuses cannot pass
* ambiguous column mappings require visible review
* excluded rows require exclusion reasons
* source workbook, worksheet and row traceability is retained
* validation failures remain visible in the result
* no pricing or export readiness is implied by import validation alone

## 12. Required Pre-Coding Identification

Before implementation begins, the implementer must record:

* affected modules and files
* proposed new files, if any
* dependencies for `.xlsx` reading
* whether dependency installation or lockfile changes are required
* test files to create or update
* fixture directory and fixture naming
* exact artificial fixture scenarios
* governance documents used as acceptance authority
* any architecture boundary that would be touched
* any existing runtime entry point that must not be changed

Coding must not begin until these are identified and reviewed.

## 13. Definition of Done For Future Implementation

A future implementation of this first slice should be done only when:

* artificial `.xlsx` fixtures are used exclusively
* source traceability is captured for imported rows
* visible validation statuses and messages are produced
* estimator review-required outcomes are visible
* fail-closed behaviour is covered by tests
* pricing, export, client return, generated BOQ, OCR, extraction, AI authority and production CE backend reliance remain excluded
* no real client or tender data is committed
* implemented, tested, planned, archived and unknown status is recorded accurately
* no documentation claims a broader capability than the implemented and tested slice proves

## 14. Open Decisions

| Ref | Decision | Required before coding |
| --- | --- | --- |
| OD-001 | Exact workbook parsing dependency | Yes |
| OD-002 | Fixture directory and naming convention | Yes |
| OD-003 | Internal imported row structure | Yes |
| OD-004 | Validation status enum and message schema | Yes |
| OD-005 | Column mapping method for first fixtures | Yes |
| OD-006 | Hidden rows, hidden columns and merged cells treatment in first slice | Yes |
| OD-007 | Test runner and test file placement | Yes |
| OD-008 | Whether importer returns a pure data object, writes an artifact or both | Yes |
| OD-009 | How source file references avoid leaking local user paths | Yes |
| OD-010 | Whether any existing CLI or runtime entry point is included later | Yes |

## 15. Acceptance Criteria

This first slice plan is acceptable when:

* client-provided Excel BOQ import is confirmed as first implementation priority
* Scenario 2 generated BOQ remains later priority and future scope only
* deterministic client BOQ workbook intake and validation foundations are recommended
* artificial `.xlsx` fixtures are required
* source traceability, visible validation, estimator review and fail-closed behaviour are required
* affected modules, dependencies, governance documents and tests must be identified before coding
* pricing, export, client return, generated BOQ, OCR, extraction, AI authority and production CE backend reliance are excluded
* implemented, tested, planned, archived and unknown states remain distinct
* no functionality is claimed as implemented
* no sensitive client or tender data is introduced
