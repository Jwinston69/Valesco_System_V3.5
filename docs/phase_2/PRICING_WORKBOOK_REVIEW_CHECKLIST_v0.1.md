# Pricing Workbook Review Checklist v0.1

## 1. Purpose

This document defines the planned Phase 2.4 estimator review checklist for pricing/export workbooks.

It is a planning document only. It does not implement checklist automation, workbook export, formulas, import, validation, pricing logic, tests, runtime behaviour, architecture, engine changes, library changes, bin changes or workspace changes.

Client-provided Excel BOQ import remains the first Phase 2 priority. VALESCO-generated BOQs from tender documents remain later priority and are not implemented or approved by this document.

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

This document must remain subordinate to current authority. Any conflict must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Pricing workbook review checklist | Planned | Defined by this document |
| Client-provided Excel BOQ workflow | Planned | First Phase 2 priority |
| VALESCO-generated BOQ workflow | Planned later | Not part of this v0.1 workflow |
| Checklist automation | Not implemented | No functionality is created |
| Workbook export implementation | Not implemented | No functionality is created |
| Runtime validation | Not implemented | No validation logic is created |
| Tests | Not implemented | No tests are created or changed |
| Existing review workflow | Current / unknown only as evidenced | Not changed by this document |
| Archived review workflow | Archived only where separately recorded | Not reactivated here |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented |

## 4. Review Principle

The estimator review must confirm that the workbook preserves source evidence, keeps internal and client-facing views separate, exposes validation status, and fails closed where evidence or pricing basis is incomplete.

A checked workbook may still remain blocked, draft or review-only. Review does not convert planned functionality into implemented functionality.

## 5. Review Statuses

Planned review statuses:

| Status | Meaning |
| --- | --- |
| `not_started` | Review has not begun |
| `in_review` | Review is in progress |
| `pass` | Check is satisfied under future governed workflow |
| `warning` | Review point requires attention but may be carried forward visibly |
| `fail` | Affected scope must not proceed as final |
| `not_applicable` | Check does not apply and the reason is recorded |
| `not_checked` | Check has not been performed and cannot be treated as pass |
| `unknown` | Status is not evidenced and cannot be treated as pass |
| `archived` | Historical status only and not active without re-approval |

`not_checked` and `unknown` must not support final pricing, client return or handover readiness.

## 6. Checklist Summary

| Review area | Required outcome |
| --- | --- |
| Authority and workbook status | Workbook identifies governing authority and does not claim implementation |
| Source client BOQ | Client evidence is preserved and traceable |
| Normalised BOQ | VALESCO working rows are separate and validated |
| Pricing build-up | Cost categories and controlled sources are visible |
| Resources and rates | Source status and approval state are explicit |
| Risks and assumptions | Unresolved items remain visible |
| Validation | Failures, warnings, unknown and not-checked statuses are visible |
| Client return | Client-facing output is separated from internal pricing |
| Handover | Outstanding issues and commercial notes are visible |
| Sensitive data | No prohibited client or commercial data is introduced into repository examples |

## 7. Authority And Workbook Status Checks

The reviewer should confirm:

* workbook identifies `governance/SNAPSHOT v3.7.11.txt` and tag `v3.7.11-runtime-reconciled` where applicable
* workbook status is draft, review, blocked or ready under future governed controls
* workbook does not claim functionality beyond repository evidence
* no planning document is treated as implemented runtime behaviour
* no AI authority is treated as active for pricing approval
* VALESCO-generated BOQ from tender documents is not mixed into the v0.1 client BOQ workflow
* unresolved governance conflicts are visible

Fail if the workbook implies implementation, testing, approval or commercial readiness without evidence.

## 8. Source Client BOQ Checks

The reviewer should confirm:

* original client workbook reference is recorded
* source worksheet name is recorded for each imported row where applicable
* source row number is recorded for each imported row where applicable
* client item number or reference is preserved where supplied
* client description, unit and quantity are preserved as source values
* client rates and amounts, where supplied, remain client-originated values
* hidden rows, merged cells, formulas or structural issues are flagged where known
* excluded or rejected rows have reasons
* source client values are not overwritten by VALESCO working values

Fail if source traceability is missing for rows that require it.

## 9. Normalised BOQ Checks

The reviewer should confirm:

* normalised BOQ rows are separate from source client BOQ rows
* each normalised row links back to source evidence or approved future VALESCO-created item record
* normalised description, unit and quantity are visible
* quantity basis and unit basis are reviewed where required
* mapping assumptions are visible
* provisional items are marked
* missing required fields are blocked
* rejected, excluded or failed rows remain visible in review outputs

Fail if normalised rows cannot be traced, validated or reviewed.

## 10. Pricing Build-Up Checks

The reviewer should confirm:

* pricing build-up is separate from source BOQ and client return sheets
* labour is separately visible
* plant is separately visible
* materials are separately visible
* subcontract is separately visible
* preliminaries are separately visible
* risk is separately visible
* allowances are separately visible
* assumptions and exclusions are linked to priced items where applicable
* proposed rates and amounts are not treated as approved where checks are incomplete
* category subtotals and totals are reviewable in future implementation

Fail if hidden risk, hidden allowances, missing resource allocation or missing rate source supports pricing readiness.

## 11. Resource And Rate Source Checks

The reviewer should confirm:

* every priced resource has a source identifier or remains blocked
* source type is recorded
* source approval status is recorded
* source validation status is recorded
* archived, expired, rejected, unknown and not-checked sources are not treated as active
* supplier or subcontract quotation references are controlled and reviewed where applicable
* assumptions and exclusions are recorded
* no uncontrolled rates, quotations or tender return values are treated as authority

Fail if a priced resource relies on a missing, unknown, archived, expired, rejected or not-checked source.

## 12. Risk, Assumption And Exclusion Checks

The reviewer should confirm:

* assumptions are recorded and linked where applicable
* exclusions are visible and linked where applicable
* provisional items remain marked
* unresolved clarification questions remain visible
* risk allowances are separately visible where future governance permits them
* preliminaries, risk and allowances are not hidden in base rates
* decisions required before client return or handover are identified

Fail if unresolved commercial issues are hidden or represented as resolved.

## 13. Validation Checks

The reviewer should confirm:

* validation statuses are present for import, mapping, pricing and export areas
* `pass`, `warning`, `fail`, `not_applicable`, `not_checked` and `unknown` remain distinct
* failed checks block final readiness for the affected scope
* not-checked checks do not pass
* unknown statuses do not pass
* warnings are either resolved or carried forward visibly
* validation failures remain visible in client return and handover context where relevant

Fail if the workbook hides failed, unknown or not-checked statuses.

## 14. Client Return Checks

The reviewer should confirm:

* client return is separated from internal pricing build-up
* client-facing fields are appropriate for future governed output
* internal resource build-up is not exposed by default
* source traceability is retained where applicable
* exclusions, qualifications and provisional markers are visible where required
* client return status is blocked, draft or ready according to validation evidence
* client return values are not used as internal pricing authority

Fail if client return output bypasses validation or merges internal build-up into client-facing output without approval.

## 15. Handover Checks

The reviewer should confirm:

* handover sheet summarises unresolved warnings
* handover sheet summarises unresolved failures
* handover sheet summarises clarifications
* provisional items are listed
* exclusions and assumptions are listed
* pricing review status is visible
* client return status is visible
* outstanding actions and owners are visible where future implementation permits
* handover does not imply completion where evidence is incomplete

Fail if handover hides blocked, unresolved or provisional items.

## 16. Sensitive Data Checks

The reviewer should confirm:

* no real client BOQ is committed to the repository
* no client-identifying data is included in examples
* no tender returns are included
* no commercial rates are included
* no supplier quotations are included
* no project-specific sensitive quantities or scope details are included
* any future examples are artificial, sanitised or approved before commit

Fail if prohibited client or commercial data is present.

## 17. Review Outcomes

Planned review outcomes:

| Outcome | Meaning |
| --- | --- |
| `review_only` | Workbook can be used for review but not final pricing, client return or handover |
| `blocked` | Fail-closed condition prevents continuation for affected scope |
| `pricing_review_ready` | Pricing review may proceed under future governed controls |
| `client_return_review_ready` | Client return may be reviewed under future governed controls |
| `handover_review_ready` | Handover may be reviewed under future governed controls |
| `final_ready` | Future governed implementation only; not created by this document |

This document does not approve any final-ready state.

## 18. Acceptance Criteria

This checklist is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* source client BOQ, normalised BOQ, pricing build-up, resources, risks, validation, client return and handover are separately reviewed
* source traceability is required before pricing or export readiness
* failed, unknown and not-checked statuses remain visible and fail closed
* estimator review is required before commercial reliance
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
