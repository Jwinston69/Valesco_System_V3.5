# Phase 2 Risk and Exclusion Register v0.1

## 1. Purpose

This register records Phase 2 planning risks, assumptions, exclusions and unresolved governance points for the VALESCO BOQ / Excel workflow.

It is a planning document only. It does not implement functionality, change runtime behaviour, change architecture or alter existing governance controls.

## 2. Current Authority

Current authority:

* `governance/SNAPSHOT v3.7.11.txt`
* tag `v3.7.11-runtime-reconciled`
* `docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx`
* `docs/planning/usable_boq_workflow_v0_1.md`
* `docs/planning/phase_2_delivery_plan_v0_1.md`

Any conflict with these authority documents must be flagged for governance review.

## 3. Status Classification

| Area                              | Status               | Notes                            |
| --------------------------------- | -------------------- | -------------------------------- |
| Risk register                     | Planned document     | Created for Phase 2.0 planning   |
| Exclusion register                | Planned document     | Created for Phase 2.0 planning   |
| Risk controls                     | Planned              | Not implemented by this document |
| Validation controls               | Planned              | Not implemented by this document |
| BOQ import functionality          | Not implemented      | Future Phase 2 work              |
| Pricing/export functionality      | Not implemented      | Future Phase 2 work              |
| Generated BOQ functionality       | Later priority       | Not v0.1 scope                   |
| AI authority                      | Inactive             | Must not be relied upon          |
| Production CE backend integration | Unknown / not proven | Must not be assumed              |

## 4. Key Assumptions

| Ref   | Assumption                                                     | Status                     | Required Treatment                             |
| ----- | -------------------------------------------------------------- | -------------------------- | ---------------------------------------------- |
| A-001 | Client-provided Excel BOQ import is the first Phase 2 priority | Planned authority          | Preserve throughout v0.1 planning              |
| A-002 | VALESCO-generated BOQ from tender documents is later priority  | Planned authority          | Keep separate from v0.1 import workflow        |
| A-003 | Phase 2 does not override Phase 1 or v3.7.11 controls          | Governance assumption      | Flag conflicts before implementation           |
| A-004 | AI authority remains inactive                                  | Current status             | Do not rely on AI approval                     |
| A-005 | Live production CE backend integration is not proven           | Unknown                    | Do not depend on it                            |
| A-006 | Real client BOQs are commercially sensitive                    | Controlled data assumption | Do not commit unless sanitised and approved    |
| A-007 | Planning documents do not prove implementation                 | Governance assumption      | Do not claim runtime capability from documents |

## 5. v0.1 Exclusions

| Ref   | Exclusion                                               | Reason                                          |
| ----- | ------------------------------------------------------- | ----------------------------------------------- |
| E-001 | Code changes                                            | Phase 2.0 is planning only                      |
| E-002 | Test changes                                            | Phase 2.0 is planning only                      |
| E-003 | Runtime behaviour changes                               | No functionality is implemented                 |
| E-004 | Architecture changes                                    | Scope lock only                                 |
| E-005 | Engine, library, bin or workspace edits                 | Explicitly excluded                             |
| E-006 | Existing governance snapshot edits                      | Current snapshots remain authority              |
| E-007 | Real client BOQ examples                                | Sensitive data risk                             |
| E-008 | VALESCO-generated BOQ implementation                    | Later priority                                  |
| E-009 | AI-approved pricing                                     | AI authority inactive                           |
| E-010 | AI-approved resource allocation                         | AI authority inactive                           |
| E-011 | Production CE backend reliance                          | Not proven                                      |
| E-012 | Automatic trust in workbook formulas                    | Validation required                             |
| E-013 | Silent column mapping                                   | Estimator confirmation required where uncertain |
| E-014 | Silent unit conversion                                  | Controlled unit rules required                  |
| E-015 | Treating planned documents as implemented functionality | Governance risk                                 |

## 6. Risks

| Ref   | Risk                                                       | Exposure                                                | Control / Required Response                                 |
| ----- | ---------------------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------- |
| R-001 | Phase 2 planning is mistaken for implemented functionality | Incorrect handover or implementation assumptions        | State clearly that documents do not implement functionality |
| R-002 | Client BOQ import scope expands into generated BOQ scope   | Loss of delivery focus                                  | Keep Scenario 2 as later priority                           |
| R-003 | Existing v3.7.11 controls are weakened                     | Governance breach                                       | Flag conflicts and require governance review                |
| R-004 | Real client BOQs are committed                             | Commercial confidentiality and data protection exposure | Use only artificial, sanitised or approved examples         |
| R-005 | Workbook formulas are trusted without validation           | Pricing error                                           | Treat formulas as source content, not pricing authority     |
| R-006 | Hidden rows or columns affect BOQ totals                   | Scope or pricing omission                               | Require future validation and visibility rules              |
| R-007 | Merged cells or irregular headers cause incorrect mapping  | Incorrect BOQ normalisation                             | Require controlled mapping and estimator confirmation       |
| R-008 | Missing source trace is ignored                            | Loss of auditability                                    | Missing trace must prevent pricing readiness                |
| R-009 | Invalid units are silently converted                       | Quantity or pricing error                               | Require controlled unit mapping                             |
| R-010 | Missing rate source is overlooked                          | Uncontrolled pricing                                    | Future pricing must require rate source                     |
| R-011 | AI suggestions are treated as approved                     | Governance breach                                       | AI authority remains inactive                               |
| R-012 | CE backend integration is assumed                          | Delivery and integration risk                           | Treat as unknown until proven                               |
| R-013 | Planning documents duplicate or conflict with North Star   | Governance inconsistency                                | Keep delivery plan subordinate and concise                  |
| R-014 | Existing snapshots are edited                              | Loss of baseline authority                              | Do not edit existing governance snapshots                   |
| R-015 | Future implementation starts before planning acceptance    | Rework and governance risk                              | Complete Phase 2.0 planning approval first                  |

## 7. Unresolved Governance Points

| Ref   | Point                                                         | Status     | Required Decision                                |
| ----- | ------------------------------------------------------------- | ---------- | ------------------------------------------------ |
| G-001 | Exact approval route for sanitised BOQ examples               | Unresolved | Define who can approve example data              |
| G-002 | Minimum metadata required for source workbook traceability    | Unresolved | Define in import contract                        |
| G-003 | Whether `.xlsm` files are accepted and how macros are handled | Unresolved | Define in import contract                        |
| G-004 | Whether legacy `.xls` files are accepted                      | Unresolved | Define in import contract                        |
| G-005 | Required controlled unit list                                 | Unresolved | Define before implementation                     |
| G-006 | Rate source hierarchy                                         | Unresolved | Define before resource allocation implementation |
| G-007 | Estimator override model for warnings or failures             | Unresolved | Define through governance before implementation  |
| G-008 | Export conditions where warnings remain open                  | Unresolved | Define in validation and export rules            |
| G-009 | CE backend integration dependency                             | Unknown    | Prove before relying on it                       |
| G-010 | Test fixture policy for BOQ workbooks                         | Unresolved | Define before committing sample workbooks        |

## 8. Conflict Handling

Any conflict between this register and current authority must be recorded and escalated.

The following must not happen silently:

* planned status treated as implemented
* AI authority treated as active
* generated BOQ scope pulled into v0.1
* v3.7.11 controls bypassed
* real client data committed without approval
* unproven integration treated as available
* fail-closed rules relaxed

## 9. Acceptance Criteria

This register is acceptable when:

* assumptions are explicit
* v0.1 exclusions are recorded
* risks are visible
* unresolved governance points are listed
* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ remains later priority
* Phase 2 does not override Phase 1 or v3.7.11 controls
* no functionality is claimed as implemented
* no code, tests, runtime, architecture or snapshot changes are proposed
