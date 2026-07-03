# Pricing Export Workbook Shape v0.1

## 1. Purpose

This document defines the planned Phase 2.4 estimator-facing Excel workbook shape for BOQ pricing review, settlement support, client return preparation and tender handover.

It is a planning document only. It does not implement workbook export, formulas, import, validation, pricing logic, tests, runtime behaviour, architecture, engine changes, library changes, bin changes or workspace changes.

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

This document must remain subordinate to current authority. Any conflict must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Pricing/export workbook shape | Planned | Defined by this document |
| Client-provided Excel BOQ workflow | Planned | First Phase 2 priority |
| VALESCO-generated BOQ workflow | Planned later | Not part of this v0.1 workflow |
| Workbook export implementation | Not implemented | No functionality is created |
| Workbook formulas | Planned | Requirements only, not executable formulas |
| Runtime validation | Not implemented | No validation logic is created |
| Tests | Not implemented | No tests are created or changed |
| Existing workbook/export behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived workbook behaviour | Archived only where separately recorded | Not reactivated here |
| Unknown capability | Unknown unless evidenced | Must not be treated as implemented |

## 4. Workbook Shape Principle

The planned workbook must separate source evidence, VALESCO working data, pricing build-up, controlled resources, risk, validation, client return and handover.

The workbook must be usable by an estimator without hiding unresolved warnings, replacing client evidence, or treating planned calculations as approved commercial output.

The source client BOQ must remain preserved as evidence. VALESCO working fields and pricing outputs must be separately visible and traceable.

## 5. Planned Worksheet Register

| Worksheet | Purpose | Primary audience |
| --- | --- | --- |
| `00_Control` | Workbook metadata, authority reference, export timestamp, source workbook reference and overall validation status | Estimator / reviewer |
| `01_Client_BOQ` | Imported client BOQ rows with source workbook, sheet, row and original client values | Estimator / reviewer |
| `02_Normalised_BOQ` | VALESCO-normalised BOQ rows, mapped fields, review statuses and controlled identifiers | Estimator / pricing reviewer |
| `03_Pricing_Buildup` | Labour, plant, materials, subcontract, preliminaries, risk and allowance build-up by BOQ item | Estimator |
| `04_Rates_Resources` | Controlled resource and rate source references used by the pricing build-up | Estimator / governance reviewer |
| `05_Risks_Assumptions` | Assumptions, exclusions, provisional items, risk allowances and unresolved commercial notes | Estimator / commercial reviewer |
| `06_Validation` | Import, mapping, pricing and export validation statuses, warnings and fail-closed conditions | Estimator / reviewer |
| `07_Client_Return` | Client-facing return sheet where suitable, separated from internal pricing build-up | Estimator / commercial lead |
| `08_Handover` | Tender handover notes, unresolved issues, exclusions and next-action summary | Handover recipient |

Future implementation may add supporting sheets only if source traceability, validation visibility and client/internal separation are preserved.

## 6. Worksheet Content Requirements

### 6.1 `00_Control`

The control sheet should include:

* workbook purpose and status
* governing snapshot and tag
* export timestamp
* source workbook filename or controlled source reference
* source workbook hash or identifier where future governance permits
* generated workbook identifier
* validation summary
* warning count
* fail count
* not-checked count
* estimator review status
* client return readiness status
* handover readiness status

The control sheet must state that the workbook is not final where validation, pricing review or handover checks are incomplete.

### 6.2 `01_Client_BOQ`

The client BOQ sheet should preserve imported source evidence fields, including:

* source workbook reference
* source worksheet name
* source row number
* client section or heading
* client item number or reference
* client description
* client unit
* client quantity
* client rate where supplied
* client amount where supplied
* client notes, qualifications or comments where captured
* import status
* row exclusion reason where applicable

Client-originated values must remain distinguishable from VALESCO working values. Pricing outputs must not overwrite this sheet.

### 6.3 `02_Normalised_BOQ`

The normalised BOQ sheet should include controlled VALESCO working fields, including:

* VALESCO BOQ item identifier
* source traceability reference
* normalised section
* normalised item description
* normalised unit
* normalised quantity
* quantity review status
* item status
* pricing readiness status
* export readiness status
* clarification status
* provisional item flag
* estimator review notes

Normalisation must not remove source traceability or hide source differences.

### 6.4 `03_Pricing_Buildup`

The pricing build-up sheet should separate:

* labour
* plant
* materials
* subcontract
* preliminaries
* risk
* allowances
* waste where applicable
* productivity where applicable
* assumptions and exclusions
* category subtotals
* proposed rate
* proposed amount

Every priced line should trace back to a normalised BOQ item and every resource should trace to a controlled source record. Missing source, missing quantity, missing unit, unresolved fail status or not-checked validation must block pricing readiness.

### 6.5 `04_Rates_Resources`

The rates and resources sheet should show controlled source references, not uncontrolled commercial detail.

Planned fields include:

* resource identifier
* resource category
* resource description
* unit
* source identifier
* source type
* source approval status
* source validation status
* archive status
* assumptions
* exclusions
* linked pricing build-up references

Real commercial rates, supplier quotations or client-sensitive details must not be committed to the repository as examples.

### 6.6 `05_Risks_Assumptions`

The risks and assumptions sheet should include:

* assumption identifier
* linked BOQ item or pricing build-up line
* risk or assumption category
* description
* commercial effect where future governance permits
* provisional status
* owner
* review status
* decision required
* exclusion or qualification wording where applicable

Risk, preliminaries and allowances must be visible and must not be hidden inside another pricing category.

### 6.7 `06_Validation`

The validation sheet should include import, mapping, pricing and export checks.

Planned statuses include:

| Status | Meaning |
| --- | --- |
| `pass` | Planned check satisfied |
| `warning` | Estimator review required before reliance |
| `fail` | Workflow must stop for the affected scope |
| `not_applicable` | Check does not apply |
| `not_checked` | Check has not run and cannot be treated as pass |
| `unknown` | Status is not evidenced and cannot be treated as pass |

Failures, warnings and not-checked statuses must remain visible in the workbook.

### 6.8 `07_Client_Return`

The client return sheet should be separated from internal pricing build-up and controlled resources.

It may contain client-facing values only where future governance and estimator review permit. It must not expose internal build-up detail by default, and it must not become source authority for internal pricing.

### 6.9 `08_Handover`

The handover sheet should summarise:

* tender or workbook status
* unresolved warnings
* unresolved clarifications
* provisional items
* exclusions
* assumptions
* validation failures
* pricing review status
* client return status
* handover notes
* next actions

Handover must keep unresolved items commercially visible.

## 7. Source Traceability Requirements

Every imported, normalised, priced or exported BOQ item should retain traceability to:

* source workbook reference
* source worksheet name
* source row number
* client item reference where available
* normalised BOQ item identifier
* pricing build-up line identifier where priced
* resource source identifier where resources are used
* validation status
* estimator review status

Where traceability is missing, the affected item must fail closed and must not be marked pricing-ready or export-ready.

## 8. Fail-Closed Workbook Rules

Future implementation must fail closed where:

* source workbook evidence is missing
* source row traceability is missing for an imported item
* required client BOQ fields are missing or invalid
* normalised quantity or unit is missing, invalid or not reviewed
* controlled resource source is missing
* pricing build-up status is failed, unknown or not checked
* validation status is failed or not checked
* unresolved warnings are hidden from the workbook
* client return is generated without validation visibility
* internal pricing build-up is merged into source client BOQ evidence
* handover omits unresolved commercial risks

A review workbook may still be produced, but it must not claim final pricing, final export or final handover readiness.

## 9. Sensitive Data Controls

This document contains no real client BOQs, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future workbook examples must be artificial, sanitised or approved before being committed.

## 10. Acceptance Criteria

This workbook shape is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* source client BOQ, normalised BOQ, pricing build-up, resources, risks, validation, client return and handover are separated
* each worksheet has a clear purpose
* estimator manual input areas are visible
* controlled formula and validation areas are identifiable in future implementation
* source evidence is not overwritten
* source traceability is mandatory
* validation failures remain visible
* fail-closed behaviour is preserved
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
