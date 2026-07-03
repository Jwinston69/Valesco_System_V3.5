# Resource Allocation Schema v0.1

## 1. Purpose

This document defines the planned Phase 2.3 internal resource allocation schema for the VALESCO BOQ / Excel workflow.

It is a planning document only. It does not implement resource allocation, pricing, validation, import, export, runtime behaviour, tests, architecture, engine changes, library changes, bin changes or workspace changes.

The first Phase 2 priority remains client-provided Excel BOQ import. VALESCO-generated BOQs from tender documents remain later priority and are not implemented or approved by this document.

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

This document must remain subordinate to current authority. Any conflict must be flagged and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Client-provided Excel BOQ import | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Not part of this v0.1 schema delivery |
| BOQ item layer | Planned | Defined at planning level only |
| Resource allocation layer | Planned | Defined at planning level only |
| Pricing build-up layer | Planned | Defined at planning level only |
| Resource source controls | Planned | Defined separately in source control rules |
| Runtime implementation | Not implemented | No functionality is created by this document |
| Tests | Not implemented | No tests are created or changed by this document |
| Existing v3.7.11 controls | Current authority | Not replaced by this document |
| Archived behaviour | Archived only where separately recorded | Must not be inferred from this document |
| Unknown integration or data state | Unknown unless evidenced | Must not be treated as implemented or tested |

## 4. Layer Model

The planned internal model separates BOQ information from resource allocation and pricing build-up.

The planned layers are:

1. BOQ item layer
2. resource allocation layer
3. pricing build-up layer
4. resource source control layer
5. review and validation layer

No layer is implemented by this document.

## 5. BOQ Item Layer

The BOQ item layer represents validated and normalised BOQ rows derived from the client-provided Excel BOQ.

A planned BOQ item should retain source traceability where available:

* source workbook reference
* source worksheet name
* source row number
* client item reference
* client section or trade grouping
* original client description
* original client unit
* original client quantity
* normalised VALESCO description
* normalised VALESCO unit
* normalised VALESCO quantity
* import validation status
* exclusion or rejection reason where applicable

The original client workbook remains source evidence and must not be overwritten.

A BOQ item must not be treated as pricing-ready where required source traceability, quantity, unit or validation information is missing, failed or not checked.

## 6. Resource Allocation Layer

The resource allocation layer records the planned resources required to price a BOQ item.

Resource allocations must be separate from imported client BOQ data. Client BOQ rows do not become priced resources automatically.

Resource allocation categories are:

* labour
* plant
* materials
* subcontract
* preliminaries
* risk
* allowances

Future implementation may define additional governed subcategories, but must not hide risk, allowances or preliminaries inside another cost category.

Each planned resource allocation should include:

* allocation identifier
* linked BOQ item identifier
* resource category
* resource description
* resource unit
* resource quantity basis
* resource quantity
* productivity basis where applicable
* waste basis where applicable
* assumption reference where applicable
* exclusion reference where applicable
* rate source reference
* validation status
* estimator review status

## 7. Pricing Build-Up Layer

The pricing build-up layer is the planned deterministic calculation view over validated BOQ items and validated resource allocations.

A pricing build-up must remain traceable from priced value back to:

* BOQ item
* resource allocation
* rate source
* assumption or allowance where applicable
* estimator review record where applicable

Pricing readiness requires controlled rate source evidence before any resource can contribute to a priced total.

A resource allocation with no controlled rate source must remain not pricing-ready.

## 8. Resource Source Control Layer

The resource source control layer governs whether a labour, plant, material, subcontract, preliminaries, risk or allowance entry is controlled enough to support pricing.

Controlled source evidence may include future approved sources such as:

* governed internal resource library
* approved estimator-entered rate source
* approved supplier quotation reference
* approved subcontract quotation reference
* approved tender-specific assumption register
* approved preliminaries basis
* approved risk or allowance basis

This document does not approve any specific rate, supplier, quote, client BOQ, tender return or commercial value.

## 9. Pricing Readiness Statuses

Planned pricing readiness statuses:

| Status | Meaning |
| --- | --- |
| `not_started` | Resource allocation has not been prepared |
| `draft` | Allocation exists but required controls are incomplete |
| `source_required` | A controlled rate source or basis is missing |
| `review_required` | Estimator review is required before reliance |
| `pricing_ready` | Required controls are satisfied at planning status, subject to future implementation |
| `blocked` | Allocation cannot proceed until a fail condition is resolved |
| `excluded` | Allocation is excluded with a recorded reason |
| `not_checked` | Required checks have not been completed and cannot be treated as pass |

`not_checked` must not be treated as `pricing_ready`.

## 10. Fail-Closed Rules

Future implementation must fail closed where any required control is missing, invalid, failed or not checked.

Pricing readiness must be blocked where:

* BOQ item validation has failed
* BOQ source traceability is missing where required
* resource category is unknown
* resource quantity or unit is missing where required
* rate source is missing or uncontrolled
* estimator review is required but incomplete
* assumptions are unrecorded
* risk or allowance is hidden or unexplained
* resource allocation is generated by AI assistance without governed review

No silent fallback to default rates, default productivity, hidden allowances or unverified workbook formulas is permitted.

## 11. AI Assistance Position

AI authority remains inactive under current v3.7.11 authority.

AI assistance must not approve BOQ items, resource allocations, pricing build-ups, rate sources, assumptions, preliminaries, risk or allowances.

Any future AI-assisted suggestion must remain unapproved until governed estimator review and validation are complete.

## 12. Sensitive Data Controls

This document contains no real client BOQs, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future examples must be artificial, sanitised or approved before being committed.

## 13. Acceptance Criteria

This planning schema is acceptable when:

* client-provided Excel BOQ import remains the first priority
* VALESCO-generated BOQ from tender documents remains later priority
* BOQ item, resource allocation, pricing build-up and resource source control layers are separated
* labour, plant, materials, subcontract, preliminaries, risk and allowances are separate
* controlled rate source is required before pricing readiness
* source traceability is preserved
* fail-closed behaviour is explicit
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
