# BOQ Column Mapping Rules v0.1

## 1. Purpose

This document defines planning-only rules for mapping columns from client-provided Excel BOQs into controlled VALESCO BOQ fields.

No functionality is implemented by this document. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, governance snapshots, the North Star document or existing planning documents.

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

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Column mapping rules | Planned | Defined for future implementation |
| Client-provided Excel BOQ import | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Not part of this v0.1 mapping scope |
| Runtime mapping engine | Not implemented | No mapper is created by this document |
| Tests | Not tested / not implemented | No tests are created or changed |
| Archived mapping behaviour | Not applicable | No archived behaviour is restored |
| Production CE backend integration | Unknown / not proven | Must not be assumed |
| AI authority | Inactive | Must not approve mappings |

## 4. Mapping Principles

Column mapping must preserve source evidence and avoid silent assumptions.

Planning principles:

* map from the client workbook to controlled VALESCO fields
* keep original client values visible
* distinguish original values from normalised values
* require estimator confirmation for uncertain mappings
* fail closed where required fields cannot be mapped
* treat workbook formulas as source content, not pricing authority
* keep excluded and unmapped rows visible
* preserve source worksheet and row traceability

## 5. Candidate Source Columns

Future implementation may use header names, nearby labels, worksheet structure and estimator input to identify candidate columns.

Common candidate meanings include:

| Controlled meaning | Example source labels | Required status |
| --- | --- | --- |
| Item reference | Item, Ref, No, Item No, BOQ Ref | Required where provided |
| Description | Description, Works Description, Item Description | Required |
| Quantity | Qty, Quantity, QTY | Required for priced rows |
| Unit | Unit, UOM, Measure | Required for priced rows |
| Rate | Rate, Unit Rate | Source only, not pricing authority |
| Amount | Amount, Total, Value | Source only, not pricing authority |
| Section | Section, Trade, Heading | Optional |
| Location | Location, Zone, Area | Optional |
| Notes | Notes, Remarks, Comments | Optional |

Source labels are examples only. They are not approved implementation rules.

## 6. Controlled Target Fields

Planned target fields:

| Target field | Mapping requirement | Review requirement |
| --- | --- | --- |
| `client_item_ref` | Map where source provides item reference | Review if blank across priced rows |
| `description_original` | Required source column | Fail closed if missing |
| `quantity_original` | Required for priced rows | Fail closed if missing or invalid |
| `unit_original` | Required for priced rows | Fail closed if missing |
| `section_or_trade` | Optional source column | Review if used for grouping |
| `location_or_zone` | Optional source column | Review if used for pricing assumptions |
| `source_rate_original` | Optional source column | Must not become pricing authority |
| `source_amount_original` | Optional source column | Must not become pricing authority |
| `source_notes_original` | Optional source column | Preserve where relevant |

## 7. Mapping Confidence

Mapping confidence is planned as a review aid only.

| Confidence | Meaning | Treatment |
| --- | --- | --- |
| `confirmed` | Estimator or governed rule confirms mapping | May proceed to validation |
| `probable` | Strong candidate but not confirmed | Estimator review required |
| `ambiguous` | Multiple plausible candidates | Fail closed until resolved |
| `missing` | Required source column not found | Fail closed for affected scope |
| `not_checked` | Mapping check has not run | Must not be treated as pass |

AI assistance may suggest candidate mappings but must not approve them.

## 8. Header and Worksheet Rules

Future implementation should account for irregular workbook layouts.

Planned rules:

* multi-row headers require controlled interpretation
* merged cells must not silently determine mapping
* hidden rows or columns must be identified before reliance
* filtered rows must remain visible to validation
* blank header cells require review
* repeated headers within a worksheet require row range handling
* multiple BOQ-like worksheets require estimator confirmation unless governed selection rules exist
* summary tabs must not be imported as detailed BOQ rows without review

## 9. Formula and Derived Value Rules

Workbook formulas must not be treated as deterministic pricing authority.

Planned treatment:

* preserve formula-derived cells as source content where imported
* record whether a mapped value was formula-derived where detectable
* validate quantities and units independently of formula presence
* do not accept source rate or amount as VALESCO pricing without controlled pricing rules
* flag formula inconsistencies for estimator review

## 10. Fail-Closed Mapping Rules

Mapping must fail closed when:

* required description column is missing
* required quantity column for priced rows is missing
* required unit column for priced rows is missing
* multiple candidate columns cannot be resolved
* source worksheet cannot be confirmed
* source row traceability cannot be preserved
* required mapping status is `not_checked`
* required mapping status is `missing`
* required mapping status is `ambiguous` without estimator confirmation
* hidden or merged structure prevents reliable mapping

Fail-closed mapping must not delete source rows or hide review issues.

## 11. Estimator Review Rules

Estimator review is required for:

* worksheet selection
* ambiguous mappings
* missing required columns
* probable but unconfirmed mappings
* unusual units
* formula-derived source fields
* excluded rows
* manual mapping changes
* any override from warning or fail status

Estimator decisions should be traceable in future implementation.

## 12. Exclusions

This planning document excludes:

* implementation of automatic column mapping
* implementation of AI-approved mapping
* implementation of pricing logic
* reliance on production CE backend integration
* committing real client BOQs
* changing existing governance snapshots
* changing existing planning documents

## 13. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Approved synonym list for source headers | Yes |
| OD-002 | Handling rules for repeated headers and subtotals | Yes |
| OD-003 | Whether source rates and amounts are imported for comparison | Yes |
| OD-004 | How estimator confirmations are recorded | Yes |
| OD-005 | Whether mapping suggestions may use AI assistance | Yes |
| OD-006 | Minimum confidence required before validation | Yes |

## 14. Acceptance Criteria

These mapping rules are acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ remains later priority
* required mappings are explicit
* source traceability is preserved
* uncertain mapping requires estimator review
* `not_checked` is not treated as `pass`
* fail-closed behaviour is preserved
* no functionality is implemented by this document
* no sensitive client data is introduced
