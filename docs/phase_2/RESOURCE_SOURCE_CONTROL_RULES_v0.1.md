# Resource Source Control Rules v0.1

## 1. Purpose

This document defines planned Phase 2.3 source control rules for resources, rates, preliminaries, risk and allowances used by the internal BOQ pricing build-up.

It is a planning document only. It does not implement source control, resource libraries, pricing logic, import, export, validation, tests, runtime behaviour, architecture, engine changes, library changes, bin changes or workspace changes.

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

This document must remain subordinate to current authority. Conflicts must be flagged and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Resource source control rules | Planned | Defined by this document |
| Controlled rate source requirement | Planned | Required before pricing readiness |
| Client-provided Excel BOQ workflow | Planned | First Phase 2 priority |
| VALESCO-generated BOQ workflow | Planned later | Not part of this v0.1 workflow |
| Resource library implementation | Not implemented | No library or data source is created |
| Runtime source validation | Not implemented | No functionality is created |
| Tests | Not implemented | No tests are created or changed |
| Existing governed controls | Current authority | Not replaced by this document |
| Archived source data | Archived only where separately recorded | Must not be reused without approval |
| Unknown source status | Unknown unless evidenced | Must not be treated as controlled |

## 4. Source Control Principle

Every priced labour, plant, material, subcontract, preliminaries, risk or allowance entry requires a controlled source before pricing readiness.

A source is controlled only when it has an approved provenance, review status and traceable reference suitable for the future governed workflow.

Unknown, missing, draft, archived, unapproved or not-checked sources must fail closed and must not support pricing readiness.

## 5. Resource Categories Under Control

The following categories must remain separately controlled:

* labour
* plant
* materials
* subcontract
* preliminaries
* risk
* allowances

Preliminaries, risk and allowances must be visible as separate source-controlled items and must not be hidden inside another category.

## 6. Planned Source Record Fields

A planned resource source record should include:

* source identifier
* source category
* source name or description
* applicable resource category
* unit
* rate or basis reference, where permitted by future governance
* provenance type
* provenance reference
* effective date or tender-specific applicability where applicable
* approval status
* reviewer or approval reference where applicable
* assumptions
* exclusions
* limitations
* archive status
* validation status
* linked resource allocation identifiers where used

This document does not define or approve any actual commercial rate.

## 7. Planned Provenance Types

Future implementation may define approved provenance types such as:

| Provenance type | Planning rule |
| --- | --- |
| Governed internal resource library | Must be approved, versioned and applicable to the priced scope |
| Estimator-entered basis | Must be reviewed, traceable and explicitly approved for the item or tender |
| Supplier quotation reference | Must be approved for use, traceable and checked for scope, date and exclusions |
| Subcontract quotation reference | Must be approved for use, traceable and checked for scope, date and exclusions |
| Preliminaries basis | Must be visible, reviewed and linked to the tender or project basis |
| Risk basis | Must be visible, justified and reviewed |
| Allowance basis | Must be visible, provisional where applicable, and linked to an assumption or unresolved item |
| Historic or archived source | Must not be used unless explicitly re-approved under current governance |

No real supplier quotation, tender return, client BOQ, commercial rate or project-specific sensitive information is introduced by this document.

## 8. Source Approval Statuses

Planned source approval statuses:

| Status | Meaning |
| --- | --- |
| `unknown` | Source status is not evidenced and cannot be used for pricing readiness |
| `not_started` | Source control has not started |
| `draft` | Source exists but is not approved |
| `not_checked` | Required checks have not run and cannot be treated as pass |
| `review_required` | Estimator or governance review is required |
| `approved` | Source is approved under future governed controls |
| `rejected` | Source cannot be used |
| `archived` | Source is retained for record only and is not active |
| `expired` | Source is no longer valid for pricing readiness |
| `superseded` | Source has been replaced and cannot be used unless re-approved |

Only an approved source, under future governed implementation, may support pricing readiness.

## 9. Required Checks Before Pricing Readiness

A source must not support pricing readiness unless future implementation can verify:

* source category is known
* resource category is known
* unit is compatible with the resource allocation
* provenance type is permitted
* provenance reference is present
* approval status is approved
* source is not archived, expired, superseded or rejected
* assumptions and exclusions are recorded where applicable
* subcontract or supplier quotation scope is reviewed where applicable
* preliminaries, risk and allowances are visible and separately reviewed
* validation status is pass or governed equivalent

`not_checked` must not be treated as pass.

## 10. Fail-Closed Source Rules

Future implementation must fail closed where:

* source is missing
* source is unknown
* source is draft, rejected, archived, expired or superseded
* source provenance is missing
* source approval is missing
* source unit is incompatible
* source assumptions are missing or ambiguous
* supplier or subcontract quotation scope is unclear
* preliminaries are hidden or unbased
* risk is hidden or unjustified
* allowances are hidden or unexplained
* source was generated or selected by AI assistance without governed review
* source contains unapproved sensitive client or supplier information

No silent substitution of default rates, historic rates, workbook formulas, AI suggestions or client return values is permitted.

## 11. Traceability Requirements

Every controlled source used for pricing should remain traceable to:

* resource allocation
* BOQ item
* pricing build-up line
* approval status
* provenance reference
* assumptions and exclusions
* review record where applicable

If traceability is lost, affected pricing must be blocked until resolved.

## 12. AI Assistance Position

AI authority remains inactive under current v3.7.11 authority.

AI assistance must not approve or select controlled sources for commercial reliance. AI-suggested sources, categories, rates, assumptions, risk or allowances must remain unapproved until governed estimator review and validation are complete.

## 13. Sensitive Data Controls

This document contains no real client BOQs, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future source examples must be artificial, sanitised or approved before being committed.

## 14. Acceptance Criteria

These source control rules are acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* labour, plant, materials, subcontract, preliminaries, risk and allowances are separately controlled
* controlled source evidence is required before pricing readiness
* unknown, archived, expired, rejected and not-checked sources fail closed
* source traceability is required from rate source to resource allocation and BOQ item
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
