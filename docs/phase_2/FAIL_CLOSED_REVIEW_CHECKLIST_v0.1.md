# Fail-Closed Review Checklist v0.1

## 1. Purpose

This document defines a planning-only Phase 2.5 review checklist for validating fail-closed behaviour in the planned BOQ validation workflow.

It does not implement functionality. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, existing governance snapshots, the North Star document or existing planning documents.

Client-provided Excel BOQ import remains the first Phase 2 priority. VALESCO-generated BOQs from tender documents remain a later priority and are not implemented or approved by this document.

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

Any conflict with current authority must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Fail-closed review checklist | Planned | Defined by this document |
| Client-provided Excel BOQ import validation | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Requires separate controls before implementation |
| Checklist automation | Not implemented | No automated checklist is created |
| Runtime validation implementation | Not implemented | No validation engine is created |
| Tests | Not implemented | No tests are created or changed |
| Existing review behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived review behaviour | Archived only where separately recorded | Not reactivated by this document |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| AI authority | Inactive | Must not approve validation, pricing or readiness |

Implemented, tested, planned, archived and unknown states must remain distinct.

## 4. Review Principle

The review must confirm that validation fails closed when evidence is missing, invalid, unknown, blank, not checked or failed.

The review must also confirm that blocked conditions remain visible to estimators and are not hidden by summary statuses, workbook layout, export output, client return preparation or handover notes.

A checklist pass under this planning document does not mean functionality is implemented, tested or approved for production use.

## 5. Checklist Statuses

Planned checklist statuses:

| Status | Meaning | Treatment |
| --- | --- | --- |
| `pass` | Review point is satisfied under planned controls | May support review conclusion only |
| `warning` | Review point needs attention and remains visible | Does not equal pass |
| `fail` | Review point is not satisfied | Must fail closed for affected scope |
| `not_applicable` | Review point does not apply and reason is recorded | May proceed only where explicit |
| `not_checked` | Review point has not been checked | Must not pass |
| `unknown` | Review point is not evidenced | Must not pass |
| blank / empty | Review status is missing | Must not pass |
| `archived` | Historical review state only | Must not be active unless re-approved |

`not_checked`, `unknown` and blank statuses must not pass.

## 6. Review Checklist Summary

| Review area | Required outcome |
| --- | --- |
| Authority and scope | Planning-only status is explicit and current authority is preserved |
| Client BOQ priority | Client-provided Excel BOQ import remains first priority |
| Generated BOQ boundary | VALESCO-generated BOQs remain later priority |
| Status model | `not_checked`, `unknown` and blank statuses cannot pass |
| Source traceability | Source workbook, worksheet and row traceability are required |
| Validation gates | Required gates fail closed when evidence is missing or invalid |
| Visible review | Failures, warnings, exclusions and unresolved items remain visible |
| Estimator review | Commercial reliance requires estimator review |
| Data controls | No sensitive client or commercial data is introduced |
| Status classification | Implemented, tested, planned, archived and unknown remain distinct |

## 7. Authority And Scope Checks

The reviewer should confirm:

* the document or artifact identifies current authority where applicable
* the artifact does not claim to implement runtime functionality
* the artifact does not claim tests have been created or passed unless evidenced
* the artifact does not change architecture, engine, library, bin or workspace scope
* existing governance snapshots are not changed
* the North Star document is not changed
* existing planning documents are not changed unless separately approved
* AI authority is not treated as active for approval
* unknown capability is not treated as implemented
* archived behaviour is not treated as active without current re-approval

Fail if planned, unknown, archived, implemented or tested states are conflated.

## 8. Client BOQ Priority Checks

The reviewer should confirm:

* client-provided Excel BOQ import is stated as the first Phase 2 priority
* the original client workbook is treated as source evidence
* the original client workbook is not overwritten by VALESCO working data
* imported rows preserve source worksheet and row references where required
* source client rates or amounts are not treated as VALESCO pricing authority without governed validation and review
* validation status is recorded against imported source, mappings and rows in future implementation planning

Fail if the workflow starts from generated BOQ assumptions while a client Excel BOQ is the intended first-priority input.

## 9. Generated BOQ Boundary Checks

The reviewer should confirm:

* VALESCO-generated BOQ from tender documents is described as a later priority
* generated BOQ functionality is not claimed as implemented
* generated rows are not mixed into the v0.1 client BOQ import workflow without separate approval
* generated BOQ planning recognises document traceability, measurement assumptions, uncertainty and estimator review requirements
* generated BOQ status cannot bypass client BOQ validation rules

Fail if generated BOQ wording weakens the client-provided Excel BOQ priority or implies implementation.

## 10. Status Model Checks

The reviewer should confirm:

* validation statuses are explicit
* review statuses are explicit where review is required
* readiness statuses are separate from validation statuses
* `pass`, `warning`, `fail`, `not_applicable`, `not_checked`, `unknown`, blank, `archived` and `excluded` are not conflated
* `not_checked` does not pass
* `unknown` does not pass
* blank or missing statuses do not pass
* `archived` does not become active without current re-approval
* `warning` remains visible and does not silently become pass
* status aggregation does not hide row-level failures

Fail if a missing, unknown, blank or not-checked status can support pricing, export, client return or handover readiness.

## 11. Source Traceability Checks

The reviewer should confirm:

* source workbook reference is required where applicable
* source worksheet name is required where applicable
* source row number or controlled equivalent is required where applicable
* client item reference is preserved where supplied
* original description is preserved
* original quantity is preserved where required
* original unit is preserved where required
* normalised rows link to source evidence
* priced rows link to normalised BOQ items
* resource sources link to controlled source records where required
* traceability exceptions are visible

Fail if missing source traceability can pass or be hidden from estimator review.

## 12. Validation Gate Checks

The reviewer should confirm that planned gates fail closed for:

* unreadable workbooks
* unsupported or unresolved file types
* missing source workbook evidence
* ambiguous worksheet selection without review
* missing required column mapping
* unresolved or uncertain mapping without review
* missing source row reference
* missing description
* missing quantity where required
* invalid quantity where required
* missing unit where required
* unresolved unit mapping
* formula-derived source values used as authority
* hidden rows, hidden columns or merged cells where they affect scope
* missing validation status
* `fail`, `not_checked`, `unknown` or blank validation status

Fail if any required gate can be bypassed silently.

## 13. Visible Review Checks

The reviewer should confirm that future review outputs keep visible:

* failed rows
* warning rows
* excluded rows
* exclusion reasons
* unresolved mappings
* source traceability gaps
* unusual or unmapped units
* formula-derived values
* hidden-row, hidden-column and merged-cell concerns
* assumptions
* unresolved clarifications
* estimator review notes
* blocked readiness statuses

Fail if blocked or uncertain items can disappear from the review path.

## 14. Estimator Review Checks

The reviewer should confirm:

* estimator review is required before commercial reliance
* estimator review status is separate from validation status
* estimator review does not replace missing validation evidence
* AI assistance does not approve rows, mappings, pricing, assumptions or readiness
* reviewer decisions are visible where required
* unresolved warnings remain visible after review
* reviewed failures remain blocked
* override permissions remain an open decision unless separately governed

Fail if commercial reliance can occur without estimator review where required.

## 15. Pricing, Export And Handover Readiness Checks

The reviewer should confirm:

* pricing readiness is blocked by failed, unknown, blank or not-checked validation where required
* export readiness is blocked by failed, unknown, blank or not-checked validation where required
* client return readiness is blocked by failed, unknown, blank or not-checked validation where required
* handover readiness preserves unresolved warnings, failures, assumptions and exclusions
* review-only artifacts are not presented as final
* final-ready status is not created by this document

Fail if readiness can be inferred from incomplete evidence.

## 16. Sensitive Data Checks

The reviewer should confirm that no repository change introduces unapproved:

* real client BOQs
* client-identifying data
* tender returns
* commercial rates
* supplier quotations
* project-specific quantities
* project-specific sensitive information
* commercially sensitive metadata

Fail if prohibited client or commercial data is present.

## 17. Review Outcomes

Planned review outcomes:

| Outcome | Meaning |
| --- | --- |
| `accepted_as_planning` | Checklist is acceptable as planning only |
| `changes_required` | Wording or control changes are required before adoption |
| `blocked` | Fail-closed principle is weakened or prohibited data is present |
| `not_checked` | Review has not been performed and cannot pass |
| `unknown` | Evidence is insufficient and cannot pass |

No review outcome under this document implements functionality or approves commercial reliance.

## 18. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Final checklist ownership and sign-off role | Yes |
| OD-002 | Required evidence for estimator review completion | Yes |
| OD-003 | Whether warnings can support draft export review | Yes |
| OD-004 | Override permissions and audit requirements | Yes |
| OD-005 | Required review fields in future workbook output | Yes |
| OD-006 | Treatment of hidden rows, hidden columns and merged cells | Yes |
| OD-007 | Status aggregation from row checks to workbook summary | Yes |

## 19. Acceptance Criteria

This checklist is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* validation gates are reviewable
* `not_checked`, `unknown` and blank statuses cannot pass
* source traceability is required
* visible review is preserved
* estimator review is required before commercial reliance
* fail-closed behaviour is preserved
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
