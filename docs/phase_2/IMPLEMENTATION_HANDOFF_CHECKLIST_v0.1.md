# Implementation Handoff Checklist v0.1

## 1. Purpose

This checklist defines what must be confirmed before Phase 2 implementation work starts.

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
* `docs/phase_2/FIRST_IMPLEMENTATION_SLICE_PLAN_v0.1.md`

Any conflict with current authority must be recorded and resolved through governance before coding.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Implementation handoff checklist | Planned | Defined by this document |
| Handoff evidence | Planned | To be completed before coding |
| First implementation slice | Planned | Deterministic client BOQ workbook intake and validation foundations |
| Client-provided Excel BOQ import | Planned | First implementation priority |
| Scenario 2 generated BOQ | Planned later | Future scope only |
| Runtime implementation | Not implemented | No code is created by this document |
| Tests | Not implemented | No tests or fixtures are created by this document |
| Existing runtime behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived behaviour | Archived only where separately recorded | Not active unless re-approved |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| AI authority | Inactive | Must not approve import, validation, pricing or export |
| Production CE backend reliance | Unknown / not proven | Must not be required for first slice |

Implemented, tested, planned, archived and unknown states must remain distinct in handoff notes, implementation plans, test evidence and review summaries.

## 4. Handoff Priority Confirmation

Before coding, confirm:

| Check | Required answer |
| --- | --- |
| First implementation priority is client-provided Excel BOQ import | Yes |
| Recommended first slice is deterministic workbook intake and validation foundations | Yes |
| Artificial `.xlsx` fixtures will be used | Yes |
| Scenario 2 generated BOQ remains later priority and future scope only | Yes |
| Pricing is excluded from the first slice | Yes |
| Export is excluded from the first slice | Yes |
| Client return is excluded from the first slice | Yes |
| OCR and tender document extraction are excluded from the first slice | Yes |
| AI authority remains inactive | Yes |
| Production CE backend reliance is excluded from the first slice | Yes |
| No real client or tender data will be committed | Yes |

If any required answer is not yes, the handoff is not ready.

## 5. Repository and Branch Checklist

Record before coding:

| Item | Required evidence |
| --- | --- |
| Repository | `Jwinston69/Valesco_System_V3.5` |
| Base branch | `main` |
| Working branch | Implementation branch name recorded |
| Latest `origin/main` commit | Commit hash recorded |
| Branch divergence | Planned implementation branch compared with `origin/main` |
| Unrelated changes | Identified and excluded from scope |
| PR state | No PR opened unless explicitly approved |
| Merge state | No merge performed |

## 6. Scope Checklist

Confirm the future implementation scope includes only:

* artificial `.xlsx` workbook intake
* workbook readability checks
* worksheet identification for fixture workbooks
* deterministic fixture column mapping
* source workbook, worksheet and row traceability
* required description, unit and quantity validation
* validation status and message capture
* visible warning, fail, excluded and review-required outcomes
* fail-closed behaviour for missing, invalid, unknown, blank and not-checked evidence
* tests using artificial fixtures only

Confirm the future implementation scope excludes:

* pricing
* pricing build-up calculations
* workbook export
* client return
* generated BOQ from tender documents
* document ingestion
* OCR
* tender document extraction
* measurement
* AI authority
* production CE backend reliance
* real client BOQs
* real tender documents
* client-identifying data
* tender returns
* commercial rates
* supplier quotations
* project-specific sensitive information

## 7. Affected Modules Checklist

Before coding, identify:

| Item | Required before coding |
| --- | --- |
| Existing modules likely to be touched | Yes |
| New modules proposed | Yes |
| Existing runtime entry points that must remain untouched | Yes |
| Engine, library, bin or workspace paths affected | Must be none unless separately approved |
| Architecture boundary touched | Must be recorded and approved if any |
| Any existing behaviour relied upon | Must be evidenced, not assumed |
| Any unknown or archived behaviour | Must remain classified as unknown or archived |

No code should be edited until the affected-module list is recorded.

## 8. Dependency Checklist

Before coding, identify:

| Item | Required before coding |
| --- | --- |
| `.xlsx` parsing library or existing project dependency | Yes |
| Dependency already present or new | Yes |
| Lockfile impact | Yes, if applicable |
| Security or license concern | Yes, if applicable |
| Offline or deterministic test behaviour | Yes |
| Production CE backend dependency | Must be no for first slice |
| AI service dependency | Must be no for first slice |

Any new dependency must be approved before introduction.

## 9. Governance Checklist

Before coding, record which governance documents control:

* source workbook preservation
* source traceability
* column mapping
* validation status naming
* validation failure behaviour
* estimator review visibility
* sensitive data handling
* Scenario 2 exclusion
* AI authority inactivity
* production CE backend non-reliance

Any conflict must be recorded and resolved before implementation.

## 10. Test and Fixture Checklist

Before coding, identify:

| Item | Required before coding |
| --- | --- |
| Test files to create or update | Yes |
| Fixture directory | Yes |
| Artificial `.xlsx` fixture names | Yes |
| Fixture contents summary | Yes, non-sensitive only |
| Expected pass cases | Yes |
| Expected fail-closed cases | Yes |
| Expected warning or review-required cases | Yes |
| Assertions for source traceability | Yes |
| Assertions that pricing/export are not implied | Yes |
| Confirmation fixtures contain no sensitive data | Yes |

Artificial fixtures must not contain real client names, project names, tender details, quantities, rates, supplier quotations, tender returns or project-specific sensitive information.

## 11. Validation Checklist

The future implementation must prove or preserve:

* source file reference is captured
* source worksheet name is captured
* source row number is captured
* original description is preserved
* original unit is preserved
* original quantity is preserved
* required missing fields fail closed
* invalid quantities fail closed
* ambiguous mappings require visible review
* excluded rows have visible reasons
* validation statuses are explicit
* `not_checked`, `unknown` and blank statuses do not pass
* estimator review-required outcomes remain visible
* import validation does not imply pricing approval
* import validation does not imply export readiness

## 12. Sensitive Data Checklist

Confirm before coding and before commit:

| Prohibited material | Added? Required answer |
| --- | --- |
| Real client BOQs | No |
| Real tender documents | No |
| Client-identifying data | No |
| Tender returns | No |
| Commercial rates | No |
| Supplier quotations | No |
| Project-specific sensitive information | No |
| Extracted client workbook data | No |
| Real project quantities | No |
| Commercially sensitive metadata | No |

If any answer is not no, stop and remove the material before proceeding.

## 13. Handoff Completion Criteria

The implementation handoff is complete only when:

* repository, base branch, working branch and latest `origin/main` commit are recorded
* first implementation priority is confirmed as client-provided Excel BOQ import
* Scenario 2 generated BOQ is confirmed as later priority and future scope only
* first slice scope and exclusions are recorded
* affected modules are identified
* dependencies are identified
* governance documents are identified
* tests and artificial fixtures are identified
* source traceability requirements are recorded
* visible validation and estimator review expectations are recorded
* fail-closed behaviour is recorded
* sensitive data exclusion is confirmed
* no functionality is claimed as already implemented by planning documents

## 14. Open Decisions

| Ref | Decision | Required before coding |
| --- | --- | --- |
| OD-001 | Final implementation branch name | Yes |
| OD-002 | Exact modules and files to touch | Yes |
| OD-003 | `.xlsx` dependency and fixture generation method | Yes |
| OD-004 | Internal row schema or data object | Yes |
| OD-005 | Validation status enum and review status fields | Yes |
| OD-006 | Test file placement and fixture directory | Yes |
| OD-007 | Whether any CLI or runtime path is included later | Yes |
| OD-008 | Whether any documentation update accompanies future code | Yes |
| OD-009 | Review owner for estimator-facing validation outputs | Yes |
| OD-010 | Approval path for any dependency or architecture change | Yes |

## 15. Acceptance Criteria

This checklist is acceptable when:

* implementation readiness entry criteria are checklist-based
* client-provided Excel BOQ import is confirmed as first implementation priority
* Scenario 2 generated BOQ remains later priority and future scope only
* affected modules, dependencies, governance documents and tests must be identified before coding
* source traceability, visible validation, estimator review and fail-closed behaviour are required
* deterministic client BOQ workbook intake and validation foundations using artificial `.xlsx` fixtures are the recommended first slice
* pricing, export, client return, generated BOQ, OCR, extraction, AI authority and production CE backend reliance are excluded from the first slice
* implemented, tested, planned, archived and unknown states remain distinct
* no functionality is claimed as implemented
* no sensitive client or tender data is introduced
