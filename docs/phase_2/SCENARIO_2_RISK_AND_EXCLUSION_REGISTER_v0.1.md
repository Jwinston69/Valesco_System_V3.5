# Scenario 2 Risk and Exclusion Register v0.1

## 1. Purpose

This register records planning-only risks, exclusions, assumptions and open decisions for Scenario 2: VALESCO-generated BOQs from tender documents.

It keeps Scenario 2 visible as later priority without changing the Phase 2 first priority of client-provided Excel BOQ import.

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
| Scenario 2 risk register | Planned later | Future scope planning only |
| Scenario 2 exclusion register | Planned later | Future scope planning only |
| Client-provided Excel BOQ import | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Not part of client BOQ import v0.1 |
| Scenario 2 controls | Planned later | Not implemented |
| Document ingestion | Not implemented | No runtime pipeline is created |
| OCR | Not implemented | No OCR capability is created |
| Extraction | Not implemented | No extraction capability is created |
| Measurement | Not implemented | No measurement capability is created |
| AI assistance | Inactive / not implemented | AI authority remains inactive |
| Pricing/export | Not implemented | No pricing or export change is made |
| Tests | Not implemented | No tests are created or changed |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| Archived behaviour | Archived only where separately recorded | Must not be reactivated by assumption |

Implemented, tested, planned, archived and unknown states must remain distinct.

## 4. Key Assumptions

| Ref | Assumption | Status | Required treatment |
| --- | --- | --- | --- |
| A-001 | Client-provided Excel BOQ import is the first Phase 2 priority | Planned authority | Preserve throughout Scenario 2 planning |
| A-002 | VALESCO-generated BOQ from tender documents is later priority | Planned later | Keep separate from client BOQ import v0.1 |
| A-003 | Scenario 2 requires stronger controls than client BOQ import | Planning assumption | Require source document traceability and estimator review |
| A-004 | AI authority remains inactive | Current status | Do not rely on AI approval |
| A-005 | Source document revision status may be incomplete or superseded | Risk assumption | Treat unknown, blank, not-checked and superseded statuses as non-pass |
| A-006 | Tender documents and extracts may be commercially sensitive | Controlled data assumption | Do not commit unless artificial, sanitised or approved |
| A-007 | Planning documents do not prove implementation | Governance assumption | Do not claim runtime capability from documents |
| A-008 | Existing implementation capability is unknown unless evidenced | Unknown | Do not assume document ingestion, OCR, extraction or measurement exists |

## 5. Scenario 2 Exclusions

| Ref | Exclusion | Reason |
| --- | --- | --- |
| E-001 | Code changes | Planning documents only |
| E-002 | Test changes | Planning documents only |
| E-003 | Runtime behaviour changes | No functionality is implemented |
| E-004 | Architecture changes | Future scope only |
| E-005 | Engine, library, bin or workspace edits | Explicitly excluded |
| E-006 | Existing governance snapshot edits | Current snapshots remain authority |
| E-007 | North Star edits | Existing North Star remains authority |
| E-008 | Existing planning document edits | Not approved in this change |
| E-009 | Generated BOQ implementation | Later priority only |
| E-010 | Document ingestion implementation | Later priority only |
| E-011 | OCR implementation | Later priority only |
| E-012 | Tender document extraction implementation | Later priority only |
| E-013 | Measurement implementation | Later priority only |
| E-014 | AI-assisted BOQ approval | AI authority inactive |
| E-015 | Generated BOQ pricing implementation | Not part of Scenario 2 future scope planning |
| E-016 | Generated BOQ export implementation | Not implemented |
| E-017 | Real client BOQs | Sensitive data risk |
| E-018 | Real tender documents | Sensitive data risk |
| E-019 | Client-identifying data | Sensitive data risk |
| E-020 | Tender returns | Commercial confidentiality risk |
| E-021 | Commercial rates | Commercial confidentiality risk |
| E-022 | Supplier quotations | Commercial confidentiality risk |
| E-023 | Project-specific sensitive information | Commercial and data protection risk |
| E-024 | Treating planned, archived or unknown states as implemented | Governance risk |
| E-025 | Allowing `not_checked`, `unknown`, blank or superseded statuses to pass | Fail-closed breach |

## 6. Risks

| Ref | Risk | Exposure | Control / required response |
| --- | --- | --- | --- |
| R-001 | Scenario 2 distracts from client BOQ import | Delivery focus is diluted | Keep client-provided Excel BOQ import as first priority |
| R-002 | Future scope is mistaken for implemented capability | Incorrect handover or commercial reliance | State no functionality is implemented |
| R-003 | Generated rows lack source document traceability | Audit failure and scope uncertainty | Require source document, revision and location reference |
| R-004 | Superseded source documents are used | Incorrect scope or quantities | Superseded status must not pass |
| R-005 | Unknown or blank document status is accepted | Uncontrolled evidence | `unknown`, blank and `not_checked` must fail closed |
| R-006 | Measurement assumptions are hidden | Pricing or scope error | Require visible measurement basis and assumptions |
| R-007 | AI suggestions are treated as approved BOQ rows | Governance breach | AI authority remains inactive and estimator review is mandatory |
| R-008 | OCR or extraction confidence is treated as approval | Incorrect BOQ content | Require estimator review and source evidence |
| R-009 | Tender document conflicts are unresolved | Duplicated, omitted or incorrect scope | Require conflict status and review path |
| R-010 | Scope gaps are converted into silent allowances | Commercial risk | Require visible exclusions, assumptions and uncertainty |
| R-011 | Generated BOQ moves directly into pricing | Pricing unsupported by review | Require fail-closed pricing readiness gates |
| R-012 | Generated BOQ export hides uncertainty | Client return may overstate confidence | Uncertainty must remain visible in review artifacts |
| R-013 | Real tender documents are committed | Confidentiality and data protection exposure | Use only artificial, sanitised or approved examples |
| R-014 | Existing v3.7.11 controls are weakened | Governance breach | Flag conflicts and require governance review |
| R-015 | Archived or unknown behaviour is reactivated by assumption | Unsupported implementation reliance | Treat archived and unknown states separately from implemented/tested |
| R-016 | Scenario 2 relies on production CE backend assumptions | Integration risk | Treat integration as unknown until proven |

## 7. Future Fail-Closed Controls

Future Scenario 2 workflows must fail closed when required evidence, review or status is missing, invalid, superseded, unknown, blank or not checked.

The following must not pass:

* `not_checked` status
* `unknown` status
* blank or empty status
* missing status field
* superseded source document status
* archived status unless re-approved under current governance
* missing source document reference
* missing source document revision
* missing source location reference where required
* missing measurement basis
* missing quantity or unit basis for priced rows
* unreviewed assumption
* unreviewed exclusion
* unapproved AI suggestion

Fail-closed outcomes must remain visible to estimators and must not be hidden in generated summaries, pricing build-ups, export workbooks or handover material.

## 8. AI Authority

AI authority remains inactive.

AI assistance must not:

* approve source documents
* approve document extraction
* approve OCR output
* approve measurement
* approve generated BOQ rows
* approve assumptions or exclusions
* approve pricing
* approve export readiness
* replace estimator review
* override fail-closed controls

Any future AI-assisted Scenario 2 workflow requires separate governance approval before implementation.

## 9. Sensitive Data Controls

This document contains no real client BOQs, real tender documents, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future Scenario 2 examples, fixtures, source extracts and review artifacts must be artificial, sanitised or formally approved before being committed.

## 10. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Whether Scenario 2 requires a separate governance phase before implementation | Yes |
| OD-002 | Source document register schema and ownership | Yes |
| OD-003 | Tender document formats and ingestion assumptions | Yes |
| OD-004 | OCR, extraction and parsing governance, if proposed | Yes |
| OD-005 | Measurement basis rules and estimator responsibility | Yes |
| OD-006 | Source conflict resolution model | Yes |
| OD-007 | Uncertainty and confidence status catalogue | Yes |
| OD-008 | Generated row review and approval workflow | Yes |
| OD-009 | Generated BOQ handoff into pricing and export workflows | Yes |
| OD-010 | Synthetic tender document fixture policy | Yes |
| OD-011 | Retention and handling policy for tender source evidence | Yes |

## 11. Acceptance Criteria

This register is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* Scenario 2 remains future scope only
* exclusions are explicit
* risks are visible
* source document traceability is required for future generated BOQs
* estimator review is mandatory before commercial reliance
* uncertainty and exclusions must remain visible
* AI authority remains inactive
* `not_checked`, `unknown`, blank and superseded statuses must not pass
* implemented, tested, planned, archived and unknown states remain distinct
* no generated BOQ, document ingestion, OCR, extraction, measurement, AI assistance, pricing, export or runtime functionality is claimed or implemented
* no sensitive client or tender data is introduced
