# BOQ Workflow Principles v0.1

## 1. Purpose

This document defines the planning principles for the Phase 2 BOQ / Excel workflow.

It is a governance planning document only. It does not implement BOQ import, pricing, validation, export or AI functionality.

## 2. Current Authority

Current authority:

* `governance/SNAPSHOT v3.7.11.txt`
* tag `v3.7.11-runtime-reconciled`
* `docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx`
* `docs/planning/usable_boq_workflow_v0_1.md`
* `docs/planning/phase_2_delivery_plan_v0_1.md`

These principles must remain subordinate to current v3.7.11 governance authority.

## 3. Status Classification

| Principle Area                   | Status                                   | Notes                           |
| -------------------------------- | ---------------------------------------- | ------------------------------- |
| BOQ workflow principles          | Planned                                  | Defined by this document        |
| Client Excel BOQ import workflow | Planned                                  | First delivery priority         |
| VALESCO-generated BOQ workflow   | Planned later                            | Not v0.1 delivery               |
| Deterministic pricing            | Existing principle / planned application | Must be preserved in Phase 2    |
| Controlled data                  | Existing principle / planned application | Must be preserved in Phase 2    |
| Source traceability              | Existing principle / planned application | Must be preserved in Phase 2    |
| Fail-closed behaviour            | Existing principle / planned application | Must be preserved in Phase 2    |
| Governed AI assistance           | Existing principle / planned application | AI authority remains inactive   |
| Runtime implementation           | Not implemented by this document         | No functionality is created     |
| Tests                            | Not implemented by this document         | No tests are created or changed |

## 4. Priority Principles

### 4.1 First Priority: Client-Provided Excel BOQ

Where a client-provided Excel BOQ exists, Phase 2 must prioritise that workflow.

The intended workflow is:

1. preserve the client workbook as source evidence
2. identify relevant worksheet structure
3. map client BOQ columns to controlled VALESCO fields
4. validate required fields
5. normalise validated rows
6. prepare controlled pricing build-up
7. support estimator review
8. support governed export planning

The workflow must not assume that workbook formatting, formulas, hidden content or structure are reliable without validation.

### 4.2 Later Priority: VALESCO-Generated BOQ

VALESCO-generated BOQs from tender documents are later priority.

They must not be treated as part of the v0.1 client BOQ import workflow. Future generated BOQ work must include stronger controls for measurement assumptions, source references, uncertainty and estimator review.

## 5. Core Governance Principles

### 5.1 Deterministic Pricing

Pricing logic must be deterministic when implemented.

Planning must avoid:

* hidden pricing assumptions
* uncontrolled AI pricing decisions
* untraceable uplifts
* unapproved rate sources
* unexplained differences between internal pricing and client return values

### 5.2 Controlled Data

Controlled fields, statuses, resources and rates must be defined before implementation.

Planning must distinguish between:

* client-provided data
* VALESCO-normalised data
* estimator-entered data
* controlled resource data
* calculated pricing data
* assumptions
* exclusions

### 5.3 Source Traceability

Each imported BOQ item intended for pricing should retain source traceability where available, including:

* source file reference
* source worksheet
* source row
* client item reference where provided
* original description
* original quantity
* original unit

Rows without required source trace must not be treated as pricing-ready in future implementation.

### 5.4 Fail-Closed Behaviour

The workflow must fail closed where required control information is missing, invalid or not checked.

`not_checked` must not be treated as `pass`.

Future implementation must not silently continue where required validation has failed.

### 5.5 Governed AI Assistance

AI authority remains inactive.

AI assistance must not:

* approve BOQ rows
* approve pricing
* approve resource allocations
* approve assumptions
* replace estimator review
* override fail-closed controls
* create commercially relied-upon outputs without governed review

### 5.6 Estimator Review

Estimator review is required before commercial reliance.

The workflow must make visible:

* failed rows
* excluded rows
* warning rows
* assumptions
* provisional allowances
* missing source information
* unmapped units
* resource gaps
* unresolved pricing items

## 6. Data Handling Principles

Real client BOQs must not be committed unless sanitised and approved.

Repository data must not include unapproved:

* client names
* project names
* tender returns
* supplier quotations
* commercial rates
* quantities
* scope gaps
* contract-specific pricing
* commercially sensitive metadata

Sample data must be artificial, sanitised or approved.

## 7. Workbook Principles

The planned export workbook must:

* preserve the source workbook separately
* act as a controlled derivative
* separate client BOQ, normalised BOQ, pricing build-up, validation and handover
* keep failed and excluded rows visible
* identify estimator input areas
* identify controlled formula areas
* include validation status
* support review, settlement and handover

No workbook functionality is implemented by this document.

## 8. Exclusions for v0.1

The v0.1 workflow principles exclude:

* automatic BOQ creation from tender documents
* automatic pricing approval
* automatic resource approval
* reliance on unproven CE backend integration
* use of real client BOQs without approval
* silent formula trust
* silent column mapping
* silent unit conversion
* silent assumption creation
* changes to existing governance snapshots
* changes to runtime behaviour

## 9. Acceptance Criteria

These principles are acceptable when:

* client BOQ import is clearly first priority
* generated BOQ is clearly later priority
* deterministic pricing, controlled data, traceability and fail-closed behaviour are preserved
* AI authority remains inactive
* estimator review is required before commercial reliance
* real client data controls are explicit
* no functionality is claimed as implemented
* conflicts with current authority must be flagged, not resolved silently
