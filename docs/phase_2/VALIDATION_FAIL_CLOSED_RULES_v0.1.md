# Validation Fail-Closed Rules v0.1

## 1. Purpose

This document defines planning-only Phase 2.5 fail-closed rules for BOQ validation.

It does not implement functionality. It does not change code, tests, runtime behaviour, architecture, engine, library, bin, workspace, existing governance snapshots, the North Star document or existing planning documents.

Client-provided Excel BOQ import remains the first Phase 2 priority. VALESCO-generated BOQs from tender documents remain a later priority and are not implemented or approved by this document.

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

Any conflict with current authority must be recorded and resolved through governance before implementation.

## 3. Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Validation fail-closed rules | Planned | Defined by this document |
| Client-provided Excel BOQ import validation | Planned | First Phase 2 priority |
| VALESCO-generated BOQ from tender documents | Planned later | Requires separate controls before implementation |
| Runtime validation implementation | Not implemented | No validation engine is created |
| Tests | Not implemented | No tests are created or changed |
| Existing validation behaviour | Current / unknown only as evidenced | Not changed by this document |
| Archived validation behaviour | Archived only where separately recorded | Not reactivated by this document |
| Unknown validation capability | Unknown unless evidenced | Must not be treated as implemented or tested |
| AI authority | Inactive | Must not approve validation outcomes |

Implemented, tested, planned, archived and unknown states must remain distinct in future documents, review records and implementation evidence.

## 4. Fail-Closed Principle

The validation workflow must fail closed wherever required evidence, required review or required status is missing, failed, unknown, blank or not checked.

A fail-closed result may still allow a review artifact to be produced, but the affected file, worksheet, mapping, BOQ row, pricing readiness, export readiness, client return or handover must remain visibly blocked until governed resolution occurs.

No validation rule may silently convert uncertainty into approval.

## 5. Absolute Non-Pass Statuses

The following statuses must not pass validation and must not support pricing readiness, export readiness, client return readiness or handover readiness:

| Status | Required treatment |
| --- | --- |
| `not_checked` | Fail closed until the required check has run and produced an evidenced status |
| `unknown` | Fail closed until evidence resolves the status |
| blank / empty status | Fail closed until an explicit status is recorded |
| missing status field | Fail closed until the status field exists and is populated |
| `fail` | Fail closed for the affected scope |
| `archived` | Must not be active unless re-approved under current governance |

`not_checked`, `unknown` and blank statuses must not be treated as `pass`, `warning`, `not_applicable`, reviewed or accepted by default.

## 6. Validation Gates

Future implementation should use explicit gates. Each gate must record status, message, affected scope, source trace and reviewer state where applicable.

| Gate | Purpose | Fail-closed condition |
| --- | --- | --- |
| File gate | Confirm workbook readability and accepted file assumptions | Unreadable, unsupported, password-protected, corrupted, unknown or not checked |
| Source preservation gate | Confirm original client workbook is preserved as evidence | Source workbook missing, overwritten, uncontrolled or not checked |
| Worksheet gate | Confirm selected BOQ worksheet evidence | Worksheet unresolved, ambiguous without review, missing or not checked |
| Column mapping gate | Confirm required source columns and mappings | Required mapping missing, unknown, blank or not checked |
| Row identity gate | Confirm source row traceability | Missing source sheet, row number or controlled row reference |
| Required field gate | Confirm description, quantity and unit where required | Required field missing, invalid, unknown, blank or not checked |
| Unit gate | Confirm controlled unit interpretation | Unit unmapped, ambiguous, unknown, blank or not checked |
| Quantity gate | Confirm numeric and scoped quantity where required | Quantity invalid, ambiguous, unknown, blank or not checked |
| Formula and structure gate | Identify formulas, hidden rows, hidden columns and merged cells | Structural issue blocks scope or is not reviewed where required |
| Pricing readiness gate | Confirm row can move toward pricing | Any required import, mapping, traceability or field check failed or not checked |
| Export readiness gate | Confirm row can move toward workbook export | Any required validation, pricing or review status failed, unknown, blank or not checked |
| Estimator review gate | Confirm required estimator review | Review missing, incomplete, unknown, blank or not checked |

## 7. Source Traceability Rules

Source traceability is mandatory for any imported client BOQ row that may support pricing, export, client return or handover.

Minimum planned traceability should include:

* source workbook reference
* source worksheet name
* source row number or controlled equivalent
* client item reference where supplied
* original description
* original quantity where required
* original unit where required
* validation status and messages
* estimator review status where required

If source traceability is missing, incomplete, unknown, blank or not checked, the affected scope must fail closed.

## 8. Visible Review Rules

Fail-closed behaviour must remain visible to estimators.

Future implementation must not hide:

* failed rows
* warning rows
* excluded rows
* rows blocked by missing source traceability
* rows blocked by missing quantity or unit
* unresolved mappings
* formula-derived source values
* hidden-row, hidden-column or merged-cell concerns
* unknown, blank or not-checked statuses
* assumptions and exclusions
* reviewer decisions and unresolved review actions

A blocked row may be excluded from final client-facing output only where its exclusion reason remains visible in the review and handover path.

## 9. Estimator Review Rules

Estimator review is required before commercial reliance.

Estimator review must not be replaced by:

* AI assistance
* workbook formulas
* client-originated rates or amounts
* default mappings
* blank statuses
* unknown statuses
* not-checked statuses
* archived evidence without current re-approval

Estimator review should explicitly address warnings, failures, exclusions, unresolved mappings, unusual units, source trace exceptions, formula-derived values and assumptions.

## 10. Client BOQ Priority Rule

Client-provided Excel BOQ import is the first Phase 2 delivery priority.

Where a client workbook is provided, the validation model must start from that workbook as source evidence. The original workbook must not be overwritten or treated as VALESCO pricing authority without governed validation and review.

VALESCO-generated BOQs from tender documents are a later priority. They require separate controls for document traceability, measurement assumptions, uncertainty, estimator review, scope gaps, exclusions and commercial reliance.

## 11. Sensitive Data Controls

This document contains no real client BOQs, client-identifying data, tender returns, commercial rates, supplier quotations, project-specific quantities or project-specific sensitive information.

Future examples, fixtures or workbook extracts must be artificial, sanitised or approved before being committed.

## 12. Exclusions

This document excludes:

* validation engine implementation
* Excel import implementation
* test fixture creation
* workbook export implementation
* pricing implementation
* generated BOQ implementation
* real client BOQ examples
* production CE backend reliance
* changes to existing governance snapshots
* changes to the North Star document
* changes to existing planning documents

## 13. Open Decisions

| Ref | Decision | Required before implementation |
| --- | --- | --- |
| OD-001 | Exact validation status catalogue and allowed transitions | Yes |
| OD-002 | Whether hidden rows always fail or can warn under review | Yes |
| OD-003 | Whether hidden columns always fail or can warn under review | Yes |
| OD-004 | Rules for merged cells and repeated section headings | Yes |
| OD-005 | Quantity parsing and tolerance rules | Yes |
| OD-006 | Controlled unit list and normalisation rules | Yes |
| OD-007 | Estimator override permissions and audit evidence | Yes |
| OD-008 | Export readiness rules where warnings remain unresolved | Yes |

## 14. Acceptance Criteria

These fail-closed rules are acceptable when:

* client-provided Excel BOQ import remains first priority
* VALESCO-generated BOQ from tender documents remains later priority
* validation gates are explicit
* `not_checked`, `unknown` and blank statuses cannot pass
* source traceability is required
* visible review is preserved
* estimator review is required before commercial reliance
* implemented, tested, planned, archived and unknown states are distinguished
* no functionality is claimed as implemented
* no sensitive client data is introduced
