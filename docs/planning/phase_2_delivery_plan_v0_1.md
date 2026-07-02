# Phase 2 Delivery Plan v0.1

## 1. Purpose and Authority

This document defines the planned Phase 2 delivery sequence for the VALESCO BOQ / Excel workflow.

The objective is to create a usable BOQ workflow for estimators while preserving VALESCO governance principles:

- deterministic pricing
- controlled data
- traceability
- fail-closed behaviour
- governed AI assistance
- estimator review before commercial reliance

Current authority:

- `governance/SNAPSHOT v3.7.11.txt`
- tag `v3.7.11-runtime-reconciled`
- `docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx`
- `docs/planning/usable_boq_workflow_v0_1.md`

Status of this document:

- **planned only**
- no code proposed
- no architecture change proposed
- no new functionality created
- no implementation claimed
- no tests claimed

Client-provided Excel BOQs are the first delivery priority. VALESCO-generated BOQs from tender documents are later priority and must not be treated as part of the v0.1 client BOQ workflow.

Real client BOQs must not be committed to the repository unless they are sanitised, approved and cleared for use as test or example data.

---

## 2. Relationship to Existing Documents

### 2.1 North Star Document

`docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx` remains the higher-level strategic direction for Phase 2.

This delivery plan does not replace or duplicate the North Star document. It converts the Phase 2 intent into a practical delivery sequence, document register, branch structure and acceptance criteria.

### 2.2 Usable BOQ Workflow Plan

`docs/planning/usable_boq_workflow_v0_1.md` already exists as the first high-level BOQ workflow plan.

This delivery plan sits above that document and defines the wider Phase 2 sequence. Future detailed documents should follow the sequence defined here.

### 2.3 Governance Snapshot

`governance/SNAPSHOT v3.7.11.txt` remains the current governance baseline.

No Phase 2 planning document should weaken or bypass controls defined in the governance snapshot. Any conflict must be flagged and resolved through governance before implementation.

---

## 3. Phase 2 Delivery Sequence

## Phase 2.0 Governance Alignment and Scope Lock

### Status

Planned only.

### Purpose

Confirm the Phase 2 delivery boundary before detailed planning or implementation begins.

### Scope

- Confirm current authority documents.
- Confirm that Phase 2 does not override Phase 1 controls.
- Confirm client-provided Excel BOQ import as first priority.
- Confirm VALESCO-generated BOQ from tender documents as later priority.
- Define exclusions for v0.1.
- Confirm fail-closed planning principles.
- Record risks, assumptions and unresolved governance points.

### Output Documents

- `governance/phase_2/PHASE_2_SCOPE_LOCK_v0.1.md`
- `governance/phase_2/BOQ_WORKFLOW_PRINCIPLES_v0.1.md`
- `governance/phase_2/PHASE_2_RISK_EXCLUSION_REGISTER_v0.1.md`

### Branch Name

`phase2/planning-scope-lock`

### Acceptance Criteria

- Phase 2 scope is documented.
- Client-provided Excel BOQ import is confirmed as first priority.
- VALESCO-generated BOQ is explicitly deferred.
- No code changes are proposed.
- No implementation is claimed.
- Governance principles remain aligned with `governance/SNAPSHOT v3.7.11.txt`.
- Known exclusions and unresolved points are recorded.
- Any conflict with current governance is flagged rather than resolved silently.

---

## Phase 2.1 Usable BOQ Workflow v0.1

### Status

Planned only.

### Purpose

Define the estimator-facing workflow from client BOQ receipt through pricing review and export.

### Scope

- Receive client Excel BOQ.
- Preserve original workbook as source evidence.
- Identify workbook and worksheet structure.
- Map client BOQ columns to VALESCO-controlled fields.
- Validate required fields.
- Normalise client BOQ rows into internal BOQ rows.
- Allocate pricing resources.
- Apply deterministic pricing where controls are satisfied.
- Review risks, exclusions and unresolved rows.
- Export a pricing workbook suitable for estimator review.
- Preserve traceability back to original workbook, worksheet, row and source reference where available.

### Output Documents

- `docs/planning/usable_boq_workflow_v0_1.md`
- `docs/phase_2/BOQ_PROCESS_MAP_v0.1.md`
- `docs/phase_2/ESTIMATOR_BOQ_REVIEW_CHECKLIST_v0.1.md`

### Branch Name

`phase2/boq-workflow-v0.1-planning`

### Acceptance Criteria

- Workflow starts with client-provided Excel BOQ import.
- Workflow is usable by estimators without requiring tender document BOQ generation.
- Estimator decision points are identified.
- System validation points are identified.
- Fail-closed gates are identified.
- Source traceability requirements are defined.
- No automatic AI pricing approval is implied.
- VALESCO-generated BOQ remains future scope only.

---

## Phase 2.2 Client BOQ Import Contract

### Status

Planned only.

### Purpose

Define the controlled import contract for client-provided Excel BOQs.

### Scope

- Accepted input file assumptions.
- Required and optional BOQ fields.
- Manual and controlled column mapping.
- Worksheet and header identification.
- Source file, sheet and row traceability.
- Treatment of hidden rows, hidden columns, merged cells, blank rows and formulas.
- Validation status model.
- Rejection and exclusion rules.
- Estimator confirmation where mapping is uncertain.

### Output Documents

- `docs/phase_2/CLIENT_BOQ_IMPORT_CONTRACT_v0.1.md`
- `docs/phase_2/BOQ_COLUMN_MAPPING_RULES_v0.1.md`
- `docs/phase_2/BOQ_IMPORT_VALIDATION_MATRIX_v0.1.md`

### Branch Name

`phase2/client-boq-import-contract`

### Acceptance Criteria

- Required and optional fields are defined.
- Client source workbook remains primary evidence.
- Workbook formulas are not trusted as deterministic pricing without validation.
- Hidden rows, merged cells, blank descriptions, invalid units and non-numeric quantities are controlled.
- Import cannot proceed silently where required fields are missing.
- Manual estimator mapping is required where automatic mapping is uncertain.
- Every imported priced row must retain source traceability.
- Every rejected or excluded row must have a reason.
- Real client BOQs are not committed unless sanitised and approved.

---

## Phase 2.3 Internal Resource Allocation Schema

### Status

Planned only.

### Purpose

Define the planned internal structure used to build deterministic pricing from validated BOQ rows.

### Scope

Resource allocation must separate:

- labour
- plant
- materials
- subcontract
- preliminaries
- risk / allowance
- waste
- productivity
- uplift / margin, only where governed elsewhere

The schema must distinguish between:

- imported client BOQ data
- normalised VALESCO BOQ rows
- resource allocations
- pricing build-ups
- assumptions
- rate sources
- estimator review requirements

### Output Documents

- `docs/phase_2/RESOURCE_ALLOCATION_SCHEMA_v0.1.md`
- `docs/phase_2/BOQ_PRICING_BUILDUP_RULES_v0.1.md`
- `docs/phase_2/RESOURCE_SOURCE_CONTROL_RULES_v0.1.md`

### Branch Name

`phase2/resource-allocation-schema`

### Acceptance Criteria

- Resource allocation is separated from imported client BOQ data.
- Labour, plant, materials, subcontract and preliminaries are separate cost categories.
- Pricing is traceable from resource allocation back to BOQ item.
- Rate source is required for every priced resource.
- Assumptions are explicit.
- AI assistance cannot create approved resources without governed review.
- Preliminaries and risk are visible, not hidden.
- Deterministic pricing calculation requirements are defined at planning level.

---

## Phase 2.4 Pricing / Export Workbook Shape

### Status

Planned only.

### Purpose

Define the planned estimator-facing Excel workbook output for pricing review, settlement and handover.

### Scope

The workbook shape should separate:

- control and metadata
- imported client BOQ
- normalised BOQ
- pricing build-up
- controlled rates and resources
- risks, assumptions and exclusions
- validation results
- client return
- handover notes

Indicative worksheet structure:

| Worksheet              | Purpose                                                                          |
| ---------------------- | -------------------------------------------------------------------------------- |
| `00_Control`           | File metadata, validation status, export timestamp and source workbook reference |
| `01_Client_BOQ`        | Imported client BOQ rows with source references                                  |
| `02_Normalised_BOQ`    | VALESCO-normalised BOQ structure                                                 |
| `03_Pricing_Buildup`   | Labour, plant, material, subcontract and preliminaries allocation                |
| `04_Rates_Resources`   | Controlled rates and resource references                                         |
| `05_Risks_Assumptions` | Assumptions, exclusions, risk allowances and review notes                        |
| `06_Validation`        | Import, pricing and export validation results                                    |
| `07_Client_Return`     | Client-facing return sheet where suitable                                        |
| `08_Handover`          | Tender handover summary, unresolved issues and commercial notes                  |

### Output Documents

- `docs/phase_2/PRICING_EXPORT_WORKBOOK_SHAPE_v0.1.md`
- `docs/phase_2/BOQ_EXPORT_RULES_v0.1.md`
- `docs/phase_2/PRICING_WORKBOOK_REVIEW_CHECKLIST_v0.1.md`

### Branch Name

`phase2/pricing-export-workbook-shape`

### Acceptance Criteria

- Workbook tabs are defined.
- Each tab has a clear purpose.
- Source BOQ, normalised BOQ, pricing build-up, validation and commercial review are separated.
- Estimator manual input areas are identified.
- Controlled formula areas are identified.
- Validation failures remain visible.
- Export does not overwrite source evidence.
- Workbook supports review, settlement and handover.
- Client return sheet is separated from internal pricing build-up.

---

## Phase 2.5 Validation and Fail-Closed Rules

### Status

Planned only.

### Purpose

Define the rules that prevent unsafe import, pricing and export.

### Scope

Validation must cover:

- file validation
- worksheet validation
- column mapping validation
- row validation
- unit validation
- quantity validation
- source traceability validation
- resource allocation validation
- pricing validation
- export validation

### Planned Validation Statuses

| Status           | Meaning                                                         |
| ---------------- | --------------------------------------------------------------- |
| `pass`           | Rule satisfied                                                  |
| `warning`        | Review required but workflow may continue if governance permits |
| `fail`           | Workflow must stop for the affected scope                       |
| `not_applicable` | Rule does not apply                                             |
| `not_checked`    | Rule has not run and cannot be treated as pass                  |

### Output Documents

- `governance/phase_2/BOQ_FAIL_CLOSED_RULES_v0.1.md`
- `docs/phase_2/BOQ_VALIDATION_CATALOGUE_v0.1.md`
- `docs/phase_2/BOQ_VALIDATION_ACCEPTANCE_RULES_v0.1.md`

### Branch Name

`phase2/boq-validation-fail-closed`

### Acceptance Criteria

- Fail-closed rules are explicit.
- `not_checked` cannot pass validation.
- Missing source trace prevents pricing.
- Missing required BOQ fields prevent normalisation or pricing.
- Missing rate source prevents resource pricing.
- Export cannot proceed where controlled validation is incomplete.
- Warnings and failures are separated.
- Estimator override, if allowed later, must be governed and traceable.

---

## Phase 2.6 Scenario 2 Future Scope

### Status

Planned only.

### Purpose

Define future scope for VALESCO-generated BOQs from tender documents without distracting from the client BOQ import workflow.

### Scope

Scenario 2 is later priority and is not part of v0.1 client BOQ import delivery unless separately approved.

Future planning must address:

- tender document source register
- drawing and specification extraction
- scope classification
- measurement basis
- estimator review
- uncertainty flags
- source references
- exclusions
- generated BOQ confidence status
- no automatic tender pricing without estimator review

### Output Documents

- `docs/phase_2/FUTURE_VALESCO_GENERATED_BOQ_SCOPE_v0.1.md`
- `governance/phase_2/GENERATED_BOQ_CONTROL_REQUIREMENTS_v0.1.md`

### Branch Name

`phase2/generated-boq-future-scope`

### Acceptance Criteria

- VALESCO-generated BOQ is clearly marked as later priority.
- No generated BOQ functionality is included in client BOQ import v0.1.
- Source traceability requirements are stronger than for client BOQ import.
- Estimator review is mandatory.
- AI extraction cannot create an approved BOQ without review.
- Measurement assumptions must be visible.
- Uncertainty remains commercially visible.

---

## Phase 2.7 90-Day Delivery Plan / Implementation Readiness

### Status

Planned only.

### Purpose

Consolidate the Phase 2 planning sequence and define readiness conditions before implementation work is proposed.

### Scope

- Consolidated planning document register.
- 90-day delivery sequence.
- Implementation readiness checklist.
- Affected module identification.
- Affected library identification.
- Affected governance document identification.
- Affected test category identification.
- Handover position for future implementation work.

### Output Documents

- `docs/planning/phase_2_delivery_plan_v0_1.md`
- `docs/phase_2/PHASE_2_IMPLEMENTATION_READINESS_CHECKLIST_v0.1.md`

### Branch Name

`phase2/90-day-delivery-plan`

### Acceptance Criteria

- Phase 2 planning documents are sequenced.
- Client BOQ import remains first priority.
- VALESCO-generated BOQ remains later priority.
- Implementation is not proposed until planning is accepted.
- Affected modules, libraries, governance documents and tests are identified before implementation.
- No functionality is claimed as implemented unless confirmed by repository evidence.
- No real client BOQs are committed unless sanitised and approved.

---

## 4. Consolidated Document Register

| Ref    | Document                                                          | Status                   |
| ------ | ----------------------------------------------------------------- | ------------------------ |
| P2-001 | `governance/phase_2/PHASE_2_SCOPE_LOCK_v0.1.md`                   | Planned                  |
| P2-002 | `governance/phase_2/BOQ_WORKFLOW_PRINCIPLES_v0.1.md`              | Planned                  |
| P2-003 | `governance/phase_2/PHASE_2_RISK_EXCLUSION_REGISTER_v0.1.md`      | Planned                  |
| P2-004 | `docs/planning/usable_boq_workflow_v0_1.md`                       | Existing high-level plan |
| P2-005 | `docs/phase_2/BOQ_PROCESS_MAP_v0.1.md`                            | Planned                  |
| P2-006 | `docs/phase_2/ESTIMATOR_BOQ_REVIEW_CHECKLIST_v0.1.md`             | Planned                  |
| P2-007 | `docs/phase_2/CLIENT_BOQ_IMPORT_CONTRACT_v0.1.md`                 | Planned                  |
| P2-008 | `docs/phase_2/BOQ_COLUMN_MAPPING_RULES_v0.1.md`                   | Planned                  |
| P2-009 | `docs/phase_2/BOQ_IMPORT_VALIDATION_MATRIX_v0.1.md`               | Planned                  |
| P2-010 | `docs/phase_2/RESOURCE_ALLOCATION_SCHEMA_v0.1.md`                 | Planned                  |
| P2-011 | `docs/phase_2/BOQ_PRICING_BUILDUP_RULES_v0.1.md`                  | Planned                  |
| P2-012 | `docs/phase_2/RESOURCE_SOURCE_CONTROL_RULES_v0.1.md`              | Planned                  |
| P2-013 | `docs/phase_2/PRICING_EXPORT_WORKBOOK_SHAPE_v0.1.md`              | Planned                  |
| P2-014 | `docs/phase_2/BOQ_EXPORT_RULES_v0.1.md`                           | Planned                  |
| P2-015 | `docs/phase_2/PRICING_WORKBOOK_REVIEW_CHECKLIST_v0.1.md`          | Planned                  |
| P2-016 | `governance/phase_2/BOQ_FAIL_CLOSED_RULES_v0.1.md`                | Planned                  |
| P2-017 | `docs/phase_2/BOQ_VALIDATION_CATALOGUE_v0.1.md`                   | Planned                  |
| P2-018 | `docs/phase_2/BOQ_VALIDATION_ACCEPTANCE_RULES_v0.1.md`            | Planned                  |
| P2-019 | `docs/phase_2/FUTURE_VALESCO_GENERATED_BOQ_SCOPE_v0.1.md`         | Planned                  |
| P2-020 | `governance/phase_2/GENERATED_BOQ_CONTROL_REQUIREMENTS_v0.1.md`   | Planned                  |
| P2-021 | `docs/phase_2/PHASE_2_IMPLEMENTATION_READINESS_CHECKLIST_v0.1.md` | Planned                  |
| P2-022 | `docs/planning/phase_2_delivery_plan_v0_1.md`                     | Planned delivery plan    |

---

## 5. 90-Day Delivery Plan

### Days 1 to 15: Planning and Governance Lock

Objective:

- Establish the controlled Phase 2 delivery boundary.

Deliverables:

- Phase 2 scope lock.
- BOQ workflow principles.
- Risk and exclusion register.
- Planning document structure.
- First issue of the 90-day plan.

Acceptance criteria:

- Scope is approved for client BOQ import first.
- Scenario 2 is deferred.
- No implementation work starts before import contract and workbook shape are agreed.
- Governance conflicts are logged.

---

### Days 16 to 30: Client BOQ Import Contract

Objective:

- Define how client-provided Excel BOQs enter VALESCO.

Deliverables:

- Client BOQ import contract.
- Column mapping rules.
- Import validation matrix.
- Required internal fields.
- Source traceability rules.

Acceptance criteria:

- Required fields are defined.
- Manual mapping process is defined.
- Invalid or uncertain imports fail closed.
- Source workbook is preserved.
- Hidden rows, hidden columns, merged cells, formulas and invalid units are addressed.
- Real client BOQs are not committed unless sanitised and approved.

---

### Days 31 to 45: Resource Allocation and Pricing Build-up

Objective:

- Define how validated BOQ rows become controlled pricing build-ups.

Deliverables:

- Resource allocation schema.
- Pricing build-up rules.
- Resource source control rules.
- Cost category separation.
- Assumption control rules.

Acceptance criteria:

- Labour, plant, materials, subcontract and preliminaries are separated.
- Rate source is mandatory.
- Pricing build-up remains deterministic.
- Assumptions are explicit.
- Missing resources prevent pricing for affected rows.

---

### Days 46 to 60: Pricing / Export Workbook Shape

Objective:

- Define the estimator-facing pricing workbook.

Deliverables:

- Pricing/export workbook shape.
- Export rules.
- Workbook review checklist.
- Client return sheet structure.
- Validation and handover tab requirements.

Acceptance criteria:

- Workbook is practical for estimator review.
- Source BOQ, normalised BOQ and pricing build-up are separated.
- Client return is separated from internal pricing.
- Validation status is visible.
- Export cannot hide failed rows.

---

### Days 61 to 75: Validation and Fail-Closed Framework

Objective:

- Complete the control framework for import, pricing and export.

Deliverables:

- BOQ fail-closed rules.
- Validation catalogue.
- Validation acceptance rules.
- Status model.
- Unresolved item handling rules.

Acceptance criteria:

- `not_checked` cannot pass.
- Missing source trace prevents pricing.
- Missing required data prevents normalisation or pricing.
- Export cannot proceed with incomplete controlled validation.
- Overrides, if later permitted, require governance and traceability.

---

### Days 76 to 90: Consolidation and Implementation Readiness

Objective:

- Prepare Phase 2 for controlled implementation after planning approval.

Deliverables:

- Consolidated Phase 2 delivery pack.
- Implementation readiness checklist.
- Test planning outline.
- Handover notes.
- Future scope note for VALESCO-generated BOQ.

Acceptance criteria:

- Planning documents are complete and internally consistent.
- Affected modules, libraries, governance documents and tests are identified before implementation.
- Implementation is not proposed until planning is accepted.
- Client BOQ workflow v0.1 is ready to be broken into implementation tickets.
- Scenario 2 remains future scope.

---

## 6. Implementation Readiness Checklist

Before implementation is proposed, the responsible agent must confirm the following from repository evidence.

### 6.1 Affected Modules

To be confirmed from repository evidence. Likely areas to inspect:

- file upload / ingestion modules
- Excel parsing or document ingestion modules
- validation engine
- pricing engine
- resource library / rate library
- export workbook generation
- audit / traceability logging
- governance checks
- test harnesses

No module should be treated as implemented or suitable for reuse based on filename alone.

### 6.2 Affected Libraries

To be confirmed from repository evidence. Do not assume libraries are available.

Potential library categories:

- Excel read/write
- tabular processing
- schema validation
- deterministic calculation
- audit logging
- test fixtures

### 6.3 Affected Governance Documents

At minimum:

- `governance/SNAPSHOT v3.7.11.txt`
- `docs/north_star/VALESCO_North_Star_and_Roadmap_v3_7_11_BOQ_Phase_2.docx`
- `docs/planning/usable_boq_workflow_v0_1.md`
- new Phase 2 governance documents under `governance/phase_2/`

### 6.4 Affected Tests

To be confirmed from repository evidence. Expected future test categories:

- client BOQ import tests
- workbook structure tests
- column mapping tests
- validation tests
- fail-closed tests
- resource allocation tests
- deterministic pricing tests
- export workbook tests
- traceability tests
- regression tests against existing governance controls

### 6.5 Data Handling

- Real client BOQs must not be committed unless sanitised and approved.
- Any sample BOQ used for tests or examples must be artificial, sanitised or formally approved.
- Source data provenance must be recorded.
- Sensitive commercial information must not be introduced into repository history.
- Test fixtures must not expose client names, project names, rates, quantities, tender returns or supplier quotations unless cleared.

---

## 7. Consolidated Phase 2 Acceptance Criteria

Phase 2 planning is acceptable when:

1. Client-provided Excel BOQ import is confirmed as the first usable workflow.
2. VALESCO-generated BOQ from tender documents is clearly deferred.
3. The import contract defines required, optional and rejected data conditions.
4. The internal resource allocation schema separates labour, plant, materials, subcontract and preliminaries.
5. The pricing/export workbook shape is practical for estimator use.
6. Source workbook traceability is mandatory.
7. Validation and fail-closed rules are explicit.
8. `not_checked` does not equal pass.
9. Missing source trace prevents pricing.
10. Missing required fields prevent normalisation or pricing.
11. Missing rate source prevents resource pricing.
12. Failed rows remain visible in review outputs.
13. Client return output is separated from internal pricing build-up.
14. No AI-generated pricing or BOQ item is treated as approved without estimator review.
15. Planning documents clearly separate implemented, tested, planned, archived and unknown.
16. No code is proposed before planning acceptance.
17. Affected modules, libraries, governance documents and tests are identified before implementation begins.
18. Real client BOQs are not committed unless sanitised and approved.

---

## 8. Reconciliation Note

`docs/planning/usable_boq_workflow_v0_1.md` already exists as the first high-level BOQ workflow plan.

This file, `docs/planning/phase_2_delivery_plan_v0_1.md`, is the formal Phase 2 delivery plan.

Future detailed documents should follow the sequence defined here.
