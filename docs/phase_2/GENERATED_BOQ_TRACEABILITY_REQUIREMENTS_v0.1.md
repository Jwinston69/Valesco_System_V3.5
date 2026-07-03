# Generated BOQ Traceability Requirements v0.1

## 1. Purpose

This document defines planning-only traceability requirements for any future VALESCO-generated BOQ workflow from tender documents.

It does not implement functionality. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, existing governance snapshots, the North Star document or existing planning documents.

Client-provided Excel BOQ import remains the first Phase 2 priority. VALESCO-generated BOQs from tender documents remain a later priority and future scope only.

No generated BOQ, document ingestion, OCR, extraction, measurement, AI assistance, pricing, export or runtime functionality is implemented or approved by this document.

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

Any conflict with current authority must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Generated BOQ traceability requirements | Planned later | Defined for future Scenario 2 only |
| Client-provided Excel BOQ import traceability | Planned | First Phase 2 priority |
| Tender document source register | Planned later | Not implemented |
| Document ingestion | Not implemented | No ingestion runtime is created |
| OCR | Not implemented | No OCR capability is created |
| Extraction | Not implemented | No extraction capability is created |
| Measurement | Not implemented | No measurement capability is created |
| Generated BOQ row creation | Not implemented | No generated row workflow is created |
| Pricing/export | Not implemented | No pricing or export change is made |
| Tests | Not implemented | No tests are created or changed |
| AI authority | Inactive | Must not approve traceability, rows or pricing |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| Archived evidence | Archived only where separately recorded | Must not be active unless re-approved |

Implemented, tested, planned, archived and unknown states must remain distinct.

## 4. Priority Rule

The first Phase 2 priority remains client-provided Excel BOQ import.

These generated BOQ traceability requirements are for later Scenario 2 planning only. They must not be treated as a dependency for v0.1 client BOQ import unless governance explicitly changes the delivery sequence.

## 5. Traceability Principle

A future generated BOQ row must remain traceable to the tender source evidence that caused it to exist.

Traceability must be strong enough for an estimator to answer:

* which source document created or supported the BOQ row
* which revision of the source document was used
* whether the source document has been superseded
* which drawing, specification, schedule, clause or scope item supports the row
* what extraction or measurement assumption was applied
* what uncertainty remains
* who reviewed the row before commercial reliance
* why any exclusion, allowance or provisional treatment exists

A generated row without required traceability must fail closed and must not be pricing-ready, export-ready, client-return-ready or handover-ready.

## 6. Minimum Future Source Document Fields

Future generated BOQ planning should define a controlled source document register before implementation.

Minimum planned source document fields include:

| Field | Requirement | Fail-closed treatment |
| --- | --- | --- |
| `source_document_id` | Required | Missing id must fail closed |
| `source_document_title` | Required | Missing title must fail closed for reliance |
| `source_document_type` | Required | Unknown type must fail closed until reviewed |
| `source_document_revision` | Required | Missing or unknown revision must fail closed |
| `source_document_status` | Required | Superseded, unknown, blank or not-checked status must not pass |
| `source_document_date` | Planned | Missing date requires visible review |
| `source_document_originator` | Planned | Missing originator requires visible review where relevant |
| `source_location_reference` | Required where applicable | Missing location must fail closed for generated row reliance |
| `source_page_sheet_clause` | Required where applicable | Missing reference must fail closed for generated row reliance |
| `source_register_status` | Required | `not_checked`, `unknown`, blank and superseded must not pass |

## 7. Minimum Future Generated Row Fields

Future generated BOQ rows should have controlled traceability fields separate from pricing fields.

Minimum planned generated row fields include:

| Field | Requirement | Treatment if missing |
| --- | --- | --- |
| `generated_boq_row_id` | Required | Fail closed |
| `source_document_id` | Required | Fail closed |
| `source_document_revision` | Required | Fail closed |
| `source_reference_detail` | Required | Fail closed |
| `source_excerpt_or_summary` | Planned | Review required where absent |
| `measurement_basis` | Required before pricing readiness | Fail closed |
| `quantity_basis` | Required before pricing readiness | Fail closed |
| `unit_basis` | Required before pricing readiness | Fail closed |
| `assumption_ref` | Required where assumption exists | Fail closed if assumption is unreviewed |
| `uncertainty_status` | Required | `not_checked`, `unknown` or blank must not pass |
| `estimator_review_status` | Required before reliance | `not_checked`, `unknown` or blank must not pass |
| `exclusion_reason` | Required if excluded | Exclusion must remain visible |
| `ai_assistance_flag` | Required if AI assisted | AI output cannot approve the row |

## 8. Status Requirements

Future generated BOQ traceability must use explicit statuses.

The following statuses must not pass and must not support pricing readiness, export readiness, client return readiness or handover readiness:

* `not_checked`
* `unknown`
* blank or empty status
* missing status field
* superseded source status
* archived status unless re-approved under current governance
* AI-suggested status without estimator review

`pass` is only acceptable where the required evidence exists, the source document is current for the affected scope and the required estimator review path is satisfied.

`warning` does not equal pass. It may only support a future review path where governance permits and the warning remains visible.

`not_applicable` requires an explicit reason and must not hide missing evidence.

## 9. Estimator Review Requirements

Estimator review is mandatory before commercial reliance on any future generated BOQ row.

Estimator review must address:

* source document selection
* source document revision and superseded status
* generated row description
* measurement basis
* quantity basis
* unit basis
* assumptions
* exclusions
* uncertainty status
* AI assistance flags, if any
* unresolved source conflicts
* readiness for pricing, export, client return and handover

Estimator review must not be replaced by AI assistance, automated extraction, OCR confidence, document parsing confidence or default statuses.

## 10. Visible Uncertainty Rules

Future generated BOQ workflows must keep uncertainty visible.

Visible uncertainty should cover:

* missing source reference
* conflicting source documents
* superseded or unverified document revision
* ambiguous scope
* unclear measurement basis
* provisional quantity
* assumed unit
* missing specification clause
* drawing/specification mismatch
* unresolved addendum or clarification impact
* AI-suggested content awaiting review

Uncertainty must not be hidden in summary statuses, overwritten by later pricing fields or removed from review artifacts without a recorded resolution.

## 11. Fail-Closed Rules

Future generated BOQ traceability must fail closed where required evidence is missing, invalid, superseded, unknown, blank or not checked.

Fail-closed conditions include:

* missing source document id
* missing source revision
* source document status of superseded
* source document status of `unknown`, `not_checked` or blank
* missing source reference detail
* missing measurement basis
* missing quantity basis for priced rows
* missing unit basis for priced rows
* missing estimator review status
* estimator review status of `unknown`, `not_checked` or blank
* unresolved source conflict
* unreviewed assumption
* unreviewed exclusion
* AI-generated content treated as approval

A fail-closed result may allow a future review artifact but must not allow commercial reliance.

## 12. Sensitive Data Controls

This document contains no real client BOQs, real tender documents, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future source documents, extracts, fixtures or examples must be artificial, sanitised or approved before being committed.

## 13. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Final source document register schema | Yes |
| OD-002 | Required source reference granularity by document type | Yes |
| OD-003 | Revision and superseded-document status model | Yes |
| OD-004 | Measurement basis evidence fields | Yes |
| OD-005 | Quantity basis and unit basis evidence fields | Yes |
| OD-006 | Uncertainty status catalogue | Yes |
| OD-007 | Estimator review status catalogue for generated rows | Yes |
| OD-008 | Treatment of AI-assisted extraction evidence, if proposed | Yes |
| OD-009 | Conflict handling across drawings, specifications and addenda | Yes |
| OD-010 | Synthetic tender document fixture policy | Yes |

## 14. Acceptance Criteria

These traceability requirements are acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority and future scope only
* every future generated BOQ row requires source document traceability
* source revision and superseded status must be controlled
* estimator review is mandatory before commercial reliance
* visible uncertainty is required
* fail-closed behaviour is preserved
* AI authority remains inactive
* `not_checked`, `unknown`, blank and superseded statuses must not pass
* implemented, tested, planned, archived and unknown states remain distinct
* no functionality is claimed as implemented
* no sensitive client or tender data is introduced
