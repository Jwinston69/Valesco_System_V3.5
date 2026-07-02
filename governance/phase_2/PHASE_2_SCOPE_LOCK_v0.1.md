# Phase 2 Scope Lock v0.1

## 1. Purpose

This document locks the planned Phase 2 delivery boundary for the VALESCO BOQ / Excel workflow.

Phase 2.0 is a governance alignment and scope lock step only. It does not implement functionality, change runtime behaviour, change architecture or alter existing v3.7.11 governance controls.

## 2. Current Authority

Current authority:

* `governance/SNAPSHOT v3.7.11.txt`
* tag `v3.7.11-runtime-reconciled`
* `docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx`
* `docs/planning/usable_boq_workflow_v0_1.md`
* `docs/planning/phase_2_delivery_plan_v0_1.md`

This document must be read under that authority. Any conflict with the current authority must be flagged and resolved through governance before implementation.

## 3. Status Classification

| Area                                        | Status                   | Notes                                                                               |
| ------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------- |
| Stable governed MVP foundation              | Current baseline         | As stated in current handover, subject to repository evidence and v3.7.11 authority |
| Phase 2 planning documents                  | Implemented as documents | Planning documents adopted into main                                                |
| Phase 2 BOQ import workflow                 | Planned                  | No functionality implemented by this document                                       |
| Client-provided Excel BOQ import            | Planned                  | First Phase 2 priority                                                              |
| VALESCO-generated BOQ from tender documents | Planned later            | Later priority, not v0.1 delivery                                                   |
| AI authority                                | Inactive                 | Must not be treated as active for Phase 2 pricing or approval                       |
| Live production CE backend integration      | Unknown / not proven     | Must not be relied upon without evidence                                            |
| Phase 2 runtime behaviour                   | Not implemented          | No runtime change is made or implied                                                |
| Phase 2 tests                               | Not implemented          | No tests are created or changed by this document                                    |
| Existing v3.7.11 controls                   | Current authority        | Phase 2 does not override them                                                      |

## 4. Scope Lock

Phase 2 v0.1 is locked to a planning-first BOQ / Excel workflow for estimators.

The first priority is:

* client-provided Excel BOQ import
* controlled mapping
* validation
* traceability
* deterministic pricing readiness
* estimator review
* controlled export workbook planning

The later priority is:

* VALESCO-generated BOQ from tender documents

Scenario 2 must not be mixed into the v0.1 client BOQ import workflow unless separately approved through governance.

## 5. Phase 2.0 In Scope

Phase 2.0 includes planning and governance alignment only:

* confirm Phase 2 delivery boundary
* confirm client Excel BOQ import as first priority
* confirm generated BOQ from tender documents as later priority
* confirm Phase 2 does not override Phase 1 or v3.7.11 controls
* define v0.1 exclusions
* record assumptions, risks and unresolved governance points
* create Phase 2 governance documents under `governance/phase_2/`

## 6. Phase 2.0 Out of Scope

Phase 2.0 excludes:

* code changes
* test changes
* runtime behaviour changes
* architecture changes
* engine changes
* library changes
* bin changes
* workspace changes
* edits to existing governance snapshots
* real client BOQ examples
* production CE backend assumptions
* activation of AI authority
* implementation of BOQ import
* implementation of workbook export
* implementation of pricing logic
* implementation of generated BOQs from tender documents

## 7. Phase 2 v0.1 Exclusions

The following are excluded from v0.1 unless separately approved:

* automatic BOQ generation from tender documents
* AI-approved pricing
* AI-approved resource allocation
* unreviewed tender document measurement
* production CE backend reliance without proof
* automatic acceptance of workbook formulas as pricing authority
* committing real client BOQs to the repository
* importing sensitive client rates, quantities, supplier quotations or tender returns as examples
* replacing existing v3.7.11 governance controls
* loosening fail-closed behaviour
* assuming implementation from filenames or planning documents

## 8. Required Control Position

Phase 2 planning must preserve:

* deterministic pricing
* controlled data
* source traceability
* fail-closed behaviour
* governed AI assistance
* estimator review before commercial reliance
* explicit assumptions
* visible exclusions
* no silent conflict resolution

No BOQ row, pricing build-up, rate, resource allocation or export workbook should be treated as commercially reliable unless required validation and review controls are satisfied in future approved implementation.

## 9. Client BOQ Priority Rule

Client-provided Excel BOQ import is the first Phase 2 delivery priority.

The workflow must start from the client's BOQ where one is provided. The original client workbook must be treated as source evidence and must not be overwritten.

Real client BOQs must not be committed to the repository unless sanitised, approved and cleared for use.

## 10. Generated BOQ Later-Priority Rule

VALESCO-generated BOQs from tender documents are a later Phase 2 priority.

Generated BOQs require stronger controls for:

* document source traceability
* measurement assumptions
* uncertainty status
* estimator review
* scope gaps
* exclusions
* design responsibility
* commercial reliance

No generated BOQ functionality is implemented or approved by this document.

## 11. Conflict Handling

If this document conflicts with current authority, the conflict must be recorded and escalated through governance.

The conflict must not be resolved silently by:

* assuming newer planning overrides the snapshot
* weakening fail-closed controls
* activating AI authority
* treating planned scope as implemented
* relying on unproven integration
* using real client data without approval

## 12. Acceptance Criteria

This scope lock is acceptable when:

* client-provided Excel BOQ import is confirmed as first priority
* VALESCO-generated BOQ is confirmed as later priority
* Phase 2 does not override Phase 1 or v3.7.11 controls
* v0.1 exclusions are recorded
* implementation, testing and runtime status are not overstated
* risks and unresolved points are captured separately
* no code, tests, runtime behaviour, architecture or snapshot changes are proposed
* no real client BOQ examples are introduced
* no functionality is claimed as implemented by this document
