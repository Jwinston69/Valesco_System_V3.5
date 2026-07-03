# BOQ Export Rules v0.1

## 1. Purpose

This document defines planned Phase 2.4 rules for exporting a BOQ pricing workbook and preparing a controlled client return and handover view.

It is a planning document only. It does not implement export logic, workbook generation, formulas, import, validation, pricing logic, tests, runtime behaviour, architecture, engine changes, library changes, bin changes or workspace changes.

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

This document must remain subordinate to current authority. Any conflict must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| BOQ export rules | Planned | Defined by this document |
| Client-provided Excel BOQ export workflow | Planned | First Phase 2 priority |
| VALESCO-generated BOQ export workflow | Planned later | Not part of this v0.1 workflow |
| Workbook export implementation | Not implemented | No functionality is created |
| Client return generation | Planned | Requirements only |
| Handover export | Planned | Requirements only |
| Runtime validation | Not implemented | No validation logic is created |
| Tests | Not implemented | No tests are created or changed |
| Existing export behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived export behaviour | Archived only where separately recorded | Not reactivated here |
| Unknown export capability | Unknown unless evidenced | Must not be treated as implemented |

## 4. Export Principle

Export must preserve source traceability, keep internal and client-facing views separate, and fail closed where controlled validation is incomplete.

An export may create a review artifact for estimator use, but it must not mark a workbook, item, rate, resource, client return or handover as final where required checks are failed, unknown or not checked.

## 5. Planned Export Outputs

Planned export outputs are separated as follows:

| Output | Purpose | Planning rule |
| --- | --- | --- |
| Pricing review workbook | Estimator review of source BOQ, normalised BOQ, build-up, resources, risks and validation | May include internal sheets and must show validation status |
| Client return sheet | Client-facing return values where suitable | Must be separated from internal pricing build-up |
| Handover sheet | Summary of status, unresolved risks, exclusions and next actions | Must preserve unresolved issue visibility |
| Validation summary | Evidence of import, pricing and export checks | Must include failed, warning, unknown and not-checked statuses |

Future implementation may package these into one workbook only if the worksheet separation remains clear.

## 6. Export Readiness Inputs

Before export readiness can be claimed, future implementation should have evidence for:

* source workbook reference
* source worksheet and row traceability for imported items
* normalised BOQ item identifiers
* item description, unit and quantity validation
* pricing build-up references for priced items
* controlled rate and resource source references
* risk, allowance and assumption references
* validation statuses
* estimator review status
* client return status where applicable
* handover status where applicable

Missing, failed, unknown or not-checked evidence must prevent final export readiness.

## 7. Source Client BOQ Export Rules

The exported workbook must not overwrite, reorder or suppress client source evidence without traceability.

Rules:

* preserve source workbook, worksheet and row references
* preserve client item references where available
* preserve client descriptions, units, quantities, rates and amounts as source values where captured
* keep VALESCO working values separate from client-originated values
* retain excluded or rejected rows with reasons where they affect review
* show hidden, merged, formula-derived or structurally uncertain source issues where known
* do not treat client workbook formulas as approved pricing authority without validation

Source evidence remains evidence, not final VALESCO pricing.

## 8. Normalised BOQ Export Rules

Normalised BOQ export must show controlled VALESCO working rows separately from source client rows.

Rules:

* every normalised row must link to a source row or approved future VALESCO-created item record
* normalised description, unit and quantity must show validation status
* manual mapping or estimator review requirements must remain visible
* rejected or blocked rows must remain visible in review exports
* generated BOQ rows from tender documents must not be mixed into the v0.1 client BOQ workflow unless separately approved

If a normalised row cannot be traced or validated, it must not be export-ready.

## 9. Pricing Build-Up Export Rules

Pricing build-up export must show internal pricing logic separately from client return values.

Rules:

* labour, plant, materials, subcontract, preliminaries, risk and allowances must remain separate
* each resource allocation must link to a BOQ item
* each priced resource must link to a controlled source record
* assumptions and exclusions must be visible
* category subtotals must be reviewable in future implementation
* proposed rates and amounts must not be treated as approved where validation or review is incomplete
* hidden uplifts, hidden risk and hidden allowances are not permitted

A priced row with missing source, missing resource, failed validation, unknown validation or not-checked validation must not be final-export-ready.

## 10. Resource And Rate Export Rules

Resource and rate export must protect commercial and source-control boundaries.

Rules:

* show resource identifiers and source references needed for review
* show approval and validation status
* show assumptions, exclusions and archive status
* do not expose unnecessary internal commercial detail in client-facing sheets
* do not commit real rates, supplier quotations, tender returns or client-sensitive resource data as examples
* do not use archived, expired, rejected, unknown or not-checked sources for pricing readiness

Only approved future governed sources may support pricing readiness.

## 11. Risk, Assumption And Exclusion Export Rules

Risks, assumptions and exclusions must remain visible in review and handover outputs.

Rules:

* each risk or assumption should have an identifier
* each item-level risk should link to a BOQ item or pricing build-up line
* provisional items must remain marked
* unresolved clarifications must remain visible
* exclusions must not be hidden in notes outside the review path
* risk and allowance values, where future governance permits them, must remain separate from base build-up categories

Export must not present unresolved risks as resolved.

## 12. Validation Export Rules

Validation output must distinguish:

| Status | Export rule |
| --- | --- |
| `pass` | May support readiness where all other controls are satisfied |
| `warning` | Must remain visible and may require estimator review |
| `fail` | Must block final readiness for the affected scope |
| `not_applicable` | Must be justified by the rule context |
| `not_checked` | Must not be treated as pass |
| `unknown` | Must not be treated as pass |
| `archived` | Must not be active unless re-approved under current governance |

No failed, unknown or not-checked status may be hidden from the review workbook.

## 13. Client Return Rules

The client return sheet must be separated from internal pricing build-up.

Rules:

* include only client-facing fields approved by future governance and estimator review
* do not expose internal resource build-up detail by default
* do not use client return values as internal pricing authority
* show exclusions, qualifications or provisional markers where required
* block final client return readiness where validation is failed, unknown or not checked
* preserve traceability from client return rows back to normalised BOQ and source client BOQ rows where applicable

The client return is an output view, not the source of truth for internal pricing.

## 14. Handover Rules

The handover sheet must support transfer of tender status without hiding uncertainty.

Rules:

* summarise unresolved warnings, failures and clarifications
* list provisional items and commercial exclusions
* identify validation and review status
* identify outstanding actions and owners where future implementation permits
* preserve source traceability references
* state whether client return readiness is blocked, draft or ready under future controls

Handover must not imply completion where evidence is incomplete.

## 15. Fail-Closed Export Rules

Future implementation must fail closed where:

* source traceability is missing
* imported client BOQ evidence is not preserved
* normalised BOQ rows are unvalidated
* required item fields are missing or invalid
* pricing build-up is missing for priced rows
* controlled rate source is missing or not approved
* risks, assumptions or exclusions are unresolved but hidden
* validation status is `fail`, `unknown` or `not_checked`
* client return attempts to merge internal build-up into client-facing output without approval
* export totals do not reconcile in future implementation
* handover omits blocked or provisional items

A review workbook may still be produced, but it must carry the blocked status visibly.

## 16. Sensitive Data Controls

This document contains no real client BOQs, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future export examples must be artificial, sanitised or approved before being committed.

## 17. Acceptance Criteria

These export rules are acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* source client BOQ, normalised BOQ, pricing build-up, resources, risks, validation, client return and handover are separated
* source traceability is mandatory
* failed, unknown and not-checked validation cannot be hidden
* client return is separated from internal pricing build-up
* handover preserves unresolved commercial issues
* fail-closed behaviour is preserved
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
