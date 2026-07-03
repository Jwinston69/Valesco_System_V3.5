# Validation Status Model v0.1

## 1. Purpose

This document defines a planning-only Phase 2.5 validation status model for BOQ import, validation, pricing readiness, export readiness, client return review and handover review.

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

Any conflict with current authority must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Validation status model | Planned | Defined by this document |
| Client-provided Excel BOQ import validation | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Requires separate controls before implementation |
| Runtime status implementation | Not implemented | No status engine or schema is created |
| Tests | Not implemented | No tests are created or changed |
| Existing status behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived status behaviour | Archived only where separately recorded | Not reactivated by this document |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| AI authority | Inactive | Must not approve or promote statuses |

Implemented, tested, planned, archived and unknown states must remain distinct.

## 4. Status Model Principle

Every governed validation result should have an explicit status, a scope, a message where needed, a source trace where applicable and a review state where commercial reliance may follow.

The status model must preserve fail-closed behaviour. It must not allow missing, unknown, blank, archived or not-checked evidence to become approval.

## 5. Core Validation Statuses

| Status | Meaning | Pass treatment |
| --- | --- | --- |
| `pass` | Required control is satisfied with evidence | May proceed only to the next governed gate |
| `warning` | Issue requires visible review or controlled acceptance | Does not equal pass; may proceed only where governance allows |
| `fail` | Required control is not satisfied | Must fail closed for affected scope |
| `not_applicable` | Rule does not apply to the affected scope | May proceed only where the reason is explicit |
| `not_checked` | Required rule has not run or has no result | Must not pass |
| `unknown` | Status is not evidenced or cannot be determined | Must not pass |
| blank / empty | Status is missing or not populated | Must not pass |
| `archived` | Historical state only | Must not be active unless re-approved under current governance |
| `excluded` | Scope is intentionally excluded | Requires visible reason and review where relevant |

`not_checked`, `unknown` and blank statuses must not pass.

## 6. Review Statuses

Estimator review should use explicit statuses separate from validation status.

| Review status | Meaning | Treatment |
| --- | --- | --- |
| `not_started` | Review has not begun | Must not support commercial reliance |
| `in_review` | Review is underway | Must not support final readiness |
| `review_required` | Review is required before reliance | Must remain visible |
| `reviewed_pass` | Reviewer accepts the item under governed controls | May support next gate where validation also permits |
| `reviewed_warning` | Reviewer accepts visible warning for continued review path | Must remain visible and may still block final readiness |
| `reviewed_fail` | Reviewer confirms blocked condition | Must fail closed for affected scope |
| `not_applicable` | Review does not apply and reason is recorded | May proceed only where explicit |
| `not_checked` | Review has not been performed | Must not pass |
| `unknown` | Review status is not evidenced | Must not pass |
| blank / empty | Review status is missing | Must not pass |

Review status must not override validation failure unless future governance explicitly defines an auditable correction path.

## 7. Readiness Statuses

Readiness statuses should be separate from validation and review statuses.

| Readiness status | Meaning | Treatment |
| --- | --- | --- |
| `blocked` | Fail-closed condition prevents progression | Must remain visible |
| `review_only` | Artifact may be used for review but not commercial reliance | Must not be final |
| `draft_ready` | Draft may proceed for controlled review | Requires validation and review evidence |
| `pricing_review_ready` | Pricing review may proceed | Does not mean pricing is approved |
| `export_review_ready` | Export review may proceed | Does not mean export is final |
| `client_return_review_ready` | Client return may be reviewed | Does not mean client return is approved |
| `handover_review_ready` | Handover may be reviewed | Does not mean handover is complete |
| `final_ready` | Future governed implementation only | Not created by this document |
| `not_checked` | Readiness has not been assessed | Must not pass |
| `unknown` | Readiness is not evidenced | Must not pass |
| blank / empty | Readiness status is missing | Must not pass |

This document does not approve any final-ready state.

## 8. Status Scope

Each status should be scoped so that a failure is not lost or overgeneralised.

Planned status scopes include:

* file
* worksheet
* column mapping
* source row
* normalised BOQ row
* unit mapping
* quantity validation
* pricing build-up line
* resource source
* assumption
* exclusion
* validation summary
* estimator review
* export readiness
* client return readiness
* handover readiness

A status without an affected scope should be treated as incomplete and must not pass where scope is required.

## 9. Status Evidence

A status should be supported by evidence appropriate to the gate.

Evidence may include:

* source workbook reference
* source worksheet name
* source row number
* column mapping decision
* validation rule reference
* validation message
* estimator review note
* assumption reference
* exclusion reason
* resource source reference
* generated artifact identifier in future implementation

A `pass` without required evidence must be treated as invalid and fail closed for the affected scope.

## 10. Allowed Progression

Future implementation should allow progression only where the previous required gate has an evidenced acceptable status.

| Current condition | Allowed progression |
| --- | --- |
| `pass` with required evidence | May proceed to next governed gate |
| `warning` with visible message | May proceed only where governance allows and review remains visible |
| `not_applicable` with reason | May proceed where the rule truly does not apply |
| `excluded` with reason | May proceed only in an excluded/review path, not final pricing for that scope |
| `fail` | Must not proceed for affected scope |
| `not_checked` | Must not proceed for affected scope |
| `unknown` | Must not proceed for affected scope |
| blank / empty | Must not proceed for affected scope |
| `archived` | Must not proceed unless re-approved under current governance |

No automatic promotion from `warning`, `not_checked`, `unknown`, blank, `excluded` or `archived` to `pass` is permitted.

## 11. Client BOQ Priority Rule

The status model is planned first for client-provided Excel BOQ import.

Where a client-provided Excel BOQ exists, the workflow should preserve the source workbook as evidence and record validation statuses against the imported source, mappings, rows and review path.

VALESCO-generated BOQs from tender documents are later priority and require separate status treatment for tender document traceability, measurement assumptions, generated rows, uncertainty and estimator review.

## 12. Visible Status Rules

Statuses must remain visible where they affect commercial reliance.

Future implementation must not hide:

* failed statuses
* warning statuses
* not-checked statuses
* unknown statuses
* blank statuses
* archived statuses being presented as inactive
* excluded statuses and exclusion reasons
* estimator review status
* readiness status

A summary status must not conceal lower-level failures or unresolved warnings.

## 13. Sensitive Data Controls

This document contains no real client BOQs, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future examples, fixtures or workbook extracts must be artificial, sanitised or approved before being committed.

## 14. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Final status enumeration and naming | Yes |
| OD-002 | Whether `excluded` is a validation status, row state or both | Yes |
| OD-003 | Whether warnings can support draft export review | Yes |
| OD-004 | Status aggregation rules from row to workbook summary | Yes |
| OD-005 | Review override permissions and audit requirements | Yes |
| OD-006 | Status message catalogue | Yes |
| OD-007 | Future schema fields for status evidence | Yes |

## 15. Acceptance Criteria

This status model is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* validation, review and readiness statuses are separate
* `not_checked`, `unknown` and blank statuses cannot pass
* source traceability and status evidence are required
* estimator review remains visible
* fail-closed behaviour is preserved
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
