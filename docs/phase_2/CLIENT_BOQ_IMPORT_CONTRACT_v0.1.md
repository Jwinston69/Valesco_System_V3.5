# Client BOQ Import Contract v0.1

## 1. Purpose

This document defines the planning-only import contract for client-provided Excel BOQs in Phase 2.2.

It is a planning document only. No functionality is implemented by this document. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, governance snapshots, the North Star document or existing planning documents.

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

Any conflict with current authority must be flagged for governance review before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Client BOQ import contract | Planned | Defined by this document |
| Client-provided Excel BOQ import | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Not part of this v0.1 import contract |
| Runtime implementation | Not implemented | No importer is created by this document |
| Tests | Not tested / not implemented | No tests are created or changed by this document |
| Archived behaviour | Not applicable | No archived behaviour is restored or changed |
| Production CE backend integration | Unknown / not proven | Must not be relied upon |
| AI authority | Inactive | Must not approve rows, mappings, pricing or export |

## 4. Scope

This contract covers the planned import boundary for client-provided Excel BOQs.

In scope:

* accepted input assumptions
* source workbook preservation
* source traceability requirements
* required and optional BOQ fields
* worksheet and row handling assumptions
* validation statuses
* fail-closed rules
* estimator review requirements
* data handling restrictions

Out of scope:

* code changes
* test changes
* runtime implementation
* automatic BOQ generation from tender documents
* pricing implementation
* workbook export implementation
* real client BOQ examples
* production CE backend reliance
* AI-approved mappings, pricing or resource allocation

## 5. Priority Position

Client-provided Excel BOQ import is the first Phase 2 delivery priority.

Where a client-provided Excel BOQ exists, future Phase 2 implementation should start from that workbook as source evidence. The original client workbook must not be overwritten.

VALESCO-generated BOQ from tender documents is a later priority. It must not be mixed into this v0.1 import contract unless separately approved through governance.

## 6. Accepted Input Assumptions

The planned v0.1 import contract assumes the source file is a client-provided Excel workbook.

Accepted planning assumptions:

* `.xlsx` is the default expected workbook format.
* `.xlsm` handling is unresolved and must be governed before implementation.
* legacy `.xls` handling is unresolved and must be governed before implementation.
* password-protected, corrupted or unreadable workbooks must fail closed.
* the original workbook must be preserved separately from any controlled derivative.
* workbook formulas are source content only and must not be treated as pricing authority.
* hidden rows, hidden columns, filters, merged cells and blank sections require validation treatment.
* multiple candidate BOQ worksheets require estimator confirmation unless deterministic worksheet selection rules are approved.
* workbook metadata may assist traceability but must not replace source row evidence.

## 7. Required Source Traceability

Every imported row intended for pricing readiness should retain traceability where available.

Minimum planned trace fields:

| Field | Requirement | Treatment if missing |
| --- | --- | --- |
| Source file reference | Required | Fail closed for pricing readiness |
| Source workbook checksum or controlled file id | Planned | Open decision before implementation |
| Source worksheet name | Required | Fail closed for pricing readiness |
| Source worksheet index | Optional planned support | Warning if unavailable |
| Source row number | Required | Fail closed for pricing readiness |
| Original client item reference | Required where provided | Warning if expected but missing |
| Original description | Required | Fail closed for import row |
| Original quantity | Required for priced rows | Fail closed for pricing readiness |
| Original unit | Required for priced rows | Fail closed for pricing readiness |

Traceability must remain visible through normalisation, validation, pricing readiness and any future export planning.

## 8. Required BOQ Fields

The planned normalised BOQ row should distinguish required, optional and derived fields.

| Field | Status | Notes |
| --- | --- | --- |
| `source_file_ref` | Required | Controlled source reference |
| `source_sheet_name` | Required | Original worksheet name |
| `source_row_number` | Required | Original row number |
| `client_item_ref` | Required where provided | May be blank only if source row is otherwise traceable |
| `description_original` | Required | Original client description |
| `description_normalised` | Planned | Controlled derivative, not source replacement |
| `quantity_original` | Required for priced rows | Preserve client value |
| `quantity_normalised` | Planned | Derived only after validation |
| `unit_original` | Required for priced rows | Preserve client unit text |
| `unit_normalised` | Planned | Controlled mapping required |
| `section_or_trade` | Optional | Useful for estimator review |
| `location_or_zone` | Optional | Useful where provided |
| `validation_status` | Required | Planned status model below |
| `validation_messages` | Required where warning or fail | Must be visible |
| `mapping_confidence` | Planned | Must not replace estimator review |
| `estimator_review_status` | Required before commercial reliance | Planned status only |
| `exclusion_reason` | Required if excluded | Must remain visible |
| `assumption_ref` | Required if assumption used | Must link to controlled assumption |

## 9. Validation Status Model

Future implementation should use explicit validation statuses.

| Status | Meaning | Planned treatment |
| --- | --- | --- |
| `pass` | Required control satisfied | May proceed to next planned gate |
| `warning` | Review required | May proceed only where governance allows |
| `fail` | Required control not satisfied | Must fail closed for affected scope |
| `not_applicable` | Rule does not apply | Must be explicit |
| `not_checked` | Rule has not run | Must not be treated as pass |
| `excluded` | Row intentionally excluded | Reason required |

`not_checked` must not be treated as `pass`.

## 10. Fail-Closed Rules

The planned import workflow must fail closed where required controls are missing, invalid or unresolved.

Fail-closed conditions include:

* unreadable workbook
* unsupported or unresolved file type
* missing source worksheet evidence
* missing source row number
* missing required description
* missing required quantity for a priced row
* invalid quantity for a priced row
* missing original unit for a priced row
* unresolved unit mapping for pricing readiness
* missing validation status
* validation status of `fail`
* validation status of `not_checked` at a required gate
* uncertain column mapping without estimator confirmation
* row excluded without an exclusion reason
* reliance on workbook formulas as pricing authority
* any use of real client data without approval

Fail-closed behaviour must be visible to estimators and must not silently discard rows.

## 11. Estimator Review Rules

Estimator review is required before commercial reliance.

Estimator review should confirm:

* correct worksheet selection
* column mapping decisions where automatic mapping is uncertain
* excluded rows and exclusion reasons
* warning rows
* failed rows
* missing or unusual units
* provisional assumptions
* rows that cannot be priced
* source traceability exceptions
* workbook formula concerns
* any manual corrections or overrides

AI assistance must not approve mappings, BOQ rows, pricing, assumptions or export readiness.

## 12. Data Handling Restrictions

Real client BOQs must not be committed unless sanitised and approved.

Repository material must not include unapproved:

* client names
* project names
* tender returns
* supplier quotations
* commercial rates
* quantities
* contract-specific pricing
* commercially sensitive metadata
* project-specific sensitive information

Any future examples must be artificial, sanitised or approved.

## 13. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Whether `.xlsm` is accepted and how macros are handled | Yes |
| OD-002 | Whether legacy `.xls` is accepted | Yes |
| OD-003 | Minimum source workbook identifier or checksum model | Yes |
| OD-004 | Controlled unit list and unit mapping rules | Yes |
| OD-005 | Estimator override model for warnings and failures | Yes |
| OD-006 | Test fixture policy for artificial or sanitised workbooks | Yes |
| OD-007 | Required worksheet selection rules for multi-sheet workbooks | Yes |

## 14. Acceptance Criteria

This planning contract is acceptable when:

* client-provided Excel BOQ import is confirmed as first priority
* VALESCO-generated BOQ from tender documents is confirmed as later priority
* accepted input assumptions are explicit
* source traceability is required
* required BOQ fields are defined
* validation statuses are defined
* fail-closed rules are visible
* estimator review is required before commercial reliance
* no functionality is implemented by this document
* implemented, tested, planned, archived and unknown statuses are clearly distinguished
* no real client BOQ examples or sensitive client data are introduced
