# Scenario 2 Generated BOQ Future Scope v0.1

## 1. Purpose

This document defines planning-only future scope for Scenario 2: VALESCO-generated BOQs from tender documents.

It exists to keep generated BOQ work visible as a later priority while protecting the first Phase 2 priority: client-provided Excel BOQ import.

This document does not implement functionality. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, existing governance snapshots, the North Star document or existing planning documents.

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
| Scenario 2 generated BOQ scope | Planned later | Future scope only |
| Client-provided Excel BOQ import | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Not part of client BOQ import v0.1 |
| Tender document ingestion | Not implemented | No document loader, parser or pipeline is created |
| OCR | Not implemented | No OCR capability is created or approved |
| Extraction | Not implemented | No tender document extraction is created |
| Measurement | Not implemented | No measurement rules or engine are created |
| AI assistance | Inactive / not implemented | AI authority remains inactive |
| Pricing | Not implemented | No pricing capability is created by this document |
| Export | Not implemented | No workbook or client return export is created |
| Tests | Not implemented | No tests are created or changed |
| Existing runtime behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived behaviour | Archived only where separately recorded | Not reactivated by this document |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |

Implemented, tested, planned, archived and unknown states must remain distinct.

## 4. Priority Position

Client-provided Excel BOQ import is the first Phase 2 priority.

Where a client-provided Excel BOQ exists, future work must start from that workbook as source evidence. Scenario 2 must not delay, dilute or silently expand the v0.1 client BOQ import workflow.

VALESCO-generated BOQs from tender documents are a later priority. Scenario 2 may be planned, but it must remain separate from client Excel BOQ import unless governance separately approves a controlled change in scope.

## 5. Future Scenario 2 Boundary

Scenario 2 may cover a future workflow where VALESCO prepares a BOQ from tender documents such as drawings, specifications, schedules, employer requirements, addenda and clarification records.

Future planning must address:

* tender document source register
* document revision and superseded-document control
* drawing, specification, schedule and employer requirement references
* extraction basis and extraction limitations
* measurement basis and measurement assumptions
* generated BOQ row structure
* source document traceability
* estimator review and approval gates
* visible uncertainty and confidence treatment
* exclusions and scope gaps
* fail-closed behaviour for unknown, blank, superseded and not-checked evidence
* separation from pricing and export approval

Scenario 2 must not produce commercially relied-upon BOQ rows without governed source traceability, estimator review and visible uncertainty treatment.

## 6. Future Source Inputs

Future source inputs may include tender document types such as:

* drawings
* specifications
* schedules
* employer requirements
* scope documents
* addenda
* clarification responses
* tender bulletins
* revision registers

This document does not introduce real tender documents, client-identifying data, tender returns, rates, supplier quotations or project-specific sensitive information.

Future examples or fixtures must be artificial, sanitised or formally approved before repository use.

## 7. Required Future Controls

Any future Scenario 2 implementation must require stronger controls than client BOQ import because VALESCO would be creating the BOQ structure rather than preserving a client-supplied one.

Minimum future controls include:

* every generated BOQ row has source document traceability
* every source document has revision status and superseded status treatment
* measurement basis is explicit
* assumptions are recorded and visible
* uncertainty is visible to estimators
* exclusions are explicit and reviewable
* estimator review is mandatory before pricing reliance
* AI output, if ever permitted, remains assistance only and cannot approve rows
* generated rows cannot become pricing-ready while required checks are `not_checked`, `unknown`, blank or superseded
* generated rows cannot become export-ready without governed validation and review

## 8. AI Authority

AI authority remains inactive.

AI assistance must not:

* ingest tender documents as approved evidence
* extract scope as approved BOQ content
* measure quantities as approved quantities
* approve generated BOQ rows
* approve assumptions or exclusions
* approve pricing
* approve export readiness
* replace estimator review
* override fail-closed controls

Any future AI-assisted workflow requires separate governance, review controls, status evidence and acceptance criteria before implementation.

## 9. Fail-Closed Position

Future Scenario 2 planning must fail closed wherever required evidence, status, source traceability, revision control, measurement basis, estimator review or approval is missing, unknown, blank, superseded or not checked.

The following conditions must not pass:

* `not_checked` status
* `unknown` status
* blank or empty status
* missing status field
* superseded source document status
* unverified source document revision
* missing source document reference
* missing generated row source reference
* unreviewed measurement assumption
* unresolved scope gap
* unreviewed exclusion
* unapproved AI suggestion

A generated BOQ may produce a future review artifact only where blocked and uncertain items remain visible. It must not produce final pricing or export readiness unless governed controls are satisfied.

## 10. Exclusions

This document excludes:

* code changes
* test changes
* runtime behaviour changes
* architecture changes
* engine changes
* library changes
* bin changes
* workspace changes
* existing governance snapshot edits
* North Star edits
* existing planning document edits
* document ingestion implementation
* OCR implementation
* tender document extraction implementation
* measurement implementation
* AI-assisted BOQ generation implementation
* generated BOQ pricing implementation
* generated BOQ export implementation
* real client BOQs
* real tender documents
* client-identifying data
* tender returns
* commercial rates
* supplier quotations
* project-specific sensitive information

## 11. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Future document source register structure | Yes |
| OD-002 | Accepted tender document formats | Yes |
| OD-003 | Revision and superseded-document rules | Yes |
| OD-004 | Measurement basis rules by trade or scope type | Yes |
| OD-005 | Minimum source trace fields for generated BOQ rows | Yes |
| OD-006 | Uncertainty and confidence status model | Yes |
| OD-007 | Estimator review and approval workflow | Yes |
| OD-008 | AI assistance governance, if ever proposed | Yes |
| OD-009 | Generated BOQ handoff into pricing workflow | Yes |
| OD-010 | Synthetic fixture policy for tender-document examples | Yes |

## 12. Acceptance Criteria

This future scope document is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* Scenario 2 is future scope only
* no generated BOQ, document ingestion, OCR, extraction, measurement, AI assistance, pricing, export or runtime functionality is claimed or implemented
* source document traceability is required for any future generated BOQ workflow
* estimator review is mandatory before commercial reliance
* uncertainty and exclusions must remain visible
* AI authority remains inactive
* `not_checked`, `unknown`, blank and superseded statuses must not pass
* implemented, tested, planned, archived and unknown states remain distinct
* no sensitive client or tender data is introduced
