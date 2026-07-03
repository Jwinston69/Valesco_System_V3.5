# BOQ Import Validation Matrix v0.1

## 1. Purpose

This document defines a planning-only validation matrix for client-provided Excel BOQ import in Phase 2.2.

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
| Import validation matrix | Planned | Defined by this document |
| Client-provided Excel BOQ import | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Not part of this v0.1 matrix |
| Runtime validation engine | Not implemented | No validation code is created |
| Tests | Not tested / not implemented | No tests are created or changed |
| Archived validation behaviour | Not applicable | No archived behaviour is restored |
| Production CE backend integration | Unknown / not proven | Must not be relied upon |
| AI authority | Inactive | Must not approve validation outcomes |

## 4. Validation Statuses

Future implementation should use explicit validation statuses.

| Status | Meaning | Treatment |
| --- | --- | --- |
| `pass` | Rule satisfied | May proceed to next governed gate |
| `warning` | Issue requires review | Estimator review required |
| `fail` | Required control failed | Must fail closed |
| `not_applicable` | Rule does not apply | Must be explicit |
| `not_checked` | Rule has not run | Must not be treated as pass |
| `excluded` | Row or scope is excluded | Reason required |

## 5. Validation Gates

Validation should be planned as gated checks.

| Gate | Purpose | Fail-closed position |
| --- | --- | --- |
| File gate | Confirm readable workbook and accepted file assumptions | Fail closed if unreadable or unsupported |
| Worksheet gate | Confirm source worksheet selection | Fail closed if unresolved |
| Mapping gate | Confirm required columns | Fail closed for missing required mappings |
| Row gate | Confirm row-level required fields | Fail closed for affected rows |
| Unit gate | Confirm unit mapping readiness | Fail closed for pricing readiness |
| Quantity gate | Confirm numeric quantity where required | Fail closed for pricing readiness |
| Traceability gate | Confirm source file, sheet and row trace | Fail closed for pricing readiness |
| Review gate | Confirm estimator review where required | Fail closed for commercial reliance |
| Export readiness gate | Confirm validation status before future export | Fail closed if required checks are incomplete |

## 6. Validation Matrix

| Ref | Validation rule | Applies to | Planned status on failure | Required response |
| --- | --- | --- | --- | --- |
| V-001 | Workbook is readable | File | `fail` | Stop import for file |
| V-002 | File type is accepted or governed | File | `fail` | Stop import for file |
| V-003 | Source workbook is preserved | File | `fail` | Stop controlled derivative creation |
| V-004 | Worksheet selection is confirmed | Worksheet | `fail` | Estimator confirmation required |
| V-005 | Source worksheet name is recorded | Worksheet | `fail` | Stop affected rows |
| V-006 | Source row number is recorded | Row | `fail` | Stop affected row pricing readiness |
| V-007 | Description is present | Row | `fail` | Stop affected row import |
| V-008 | Quantity is present for priced row | Row | `fail` | Stop affected row pricing readiness |
| V-009 | Quantity is numeric where required | Row | `fail` | Stop affected row pricing readiness |
| V-010 | Unit is present for priced row | Row | `fail` | Stop affected row pricing readiness |
| V-011 | Unit has controlled mapping | Row | `fail` | Stop affected row pricing readiness |
| V-012 | Required column mapping is confirmed | Mapping | `fail` | Stop affected import scope |
| V-013 | Ambiguous mapping is resolved | Mapping | `fail` | Estimator confirmation required |
| V-014 | Hidden rows are identified | Worksheet | `warning` or `fail` | Review required; fail if scope unclear |
| V-015 | Hidden columns are identified | Worksheet | `warning` or `fail` | Review required; fail if mapping affected |
| V-016 | Merged cells are identified | Worksheet | `warning` or `fail` | Review required; fail if mapping affected |
| V-017 | Formula-derived source values are flagged | Row | `warning` | Estimator review required |
| V-018 | Source rate is not treated as VALESCO pricing authority | Row | `fail` | Stop pricing reliance |
| V-019 | Source amount is not treated as VALESCO pricing authority | Row | `fail` | Stop pricing reliance |
| V-020 | Excluded row has reason | Row | `fail` | Stop exclusion acceptance |
| V-021 | Warning row has visible message | Row | `fail` | Stop review readiness |
| V-022 | `not_checked` is not promoted to `pass` | All gates | `fail` | Stop affected scope |
| V-023 | Estimator review is complete where required | Review | `fail` | Stop commercial reliance |
| V-024 | Real client data is approved before repository use | Data | `fail` | Do not commit data |
| V-025 | AI output is not treated as approval | All gates | `fail` | Require governed review |

## 7. Fail-Closed Rules

The validation model must fail closed where a required rule is not satisfied.

Required fail-closed principles:

* `not_checked` must not pass validation.
* missing source trace must prevent pricing readiness.
* missing description must prevent row import.
* missing quantity or unit must prevent pricing readiness for priced rows.
* unresolved mapping must prevent affected import scope from proceeding.
* formula-derived source values must not become pricing authority.
* warnings must remain visible until reviewed.
* excluded rows must remain visible with reasons.
* estimator review must occur before commercial reliance.

## 8. Estimator Review Rules

Estimator review is required for validation outcomes that affect commercial reliance.

Review should cover:

* all warning rows
* all failed rows
* all excluded rows
* all unresolved mappings
* all unusual or unmapped units
* all formula-derived source values used for context
* all assumptions introduced during normalisation
* all cases where source trace is incomplete

Estimator review must not be replaced by AI assistance.

## 9. Data Handling Validation

Validation planning must protect sensitive data.

Repository commits must not include unapproved:

* real client BOQs
* client-identifying data
* tender returns
* commercial rates
* supplier quotations
* project-specific sensitive information

Sample fixtures must be artificial, sanitised or approved before any future implementation work.

## 10. Exclusions

This matrix excludes:

* validation engine implementation
* automated Excel import implementation
* test fixture creation
* real client BOQ examples
* pricing implementation
* export implementation
* production CE backend reliance
* changes to existing governance snapshots
* changes to existing planning documents

## 11. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Whether hidden rows should always fail or sometimes warn | Yes |
| OD-002 | Whether hidden columns should always fail or sometimes warn | Yes |
| OD-003 | Controlled unit list and normalisation rules | Yes |
| OD-004 | Quantity tolerance and numeric parsing rules | Yes |
| OD-005 | Estimator override permissions and audit requirements | Yes |
| OD-006 | Validation message catalogue | Yes |
| OD-007 | Export readiness conditions where warnings remain open | Yes |

## 12. Acceptance Criteria

This validation matrix is acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ remains later priority
* validation statuses are explicit
* fail-closed rules are defined
* source traceability is required
* estimator review is required before commercial reliance
* implemented, tested, planned, archived and unknown statuses are clearly distinguished
* no functionality is implemented by this document
* no sensitive client data is introduced
