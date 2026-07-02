# Usable BOQ Workflow v0.1

## Purpose

This document defines the Phase 2 planning shape for a usable BOQ workflow in VALESCO. The workflow is intended to let VALESCO receive, preserve, validate, price and export Bills of Quantities while keeping client workbook evidence intact and ensuring that ambiguous or incomplete items fail closed until reviewed.

This is a planning document only. It does not change runtime behaviour, code, tests, architecture, engine modules, library data, workspace outputs or governance snapshots.

## Current Authority

- `governance/SNAPSHOT v3.7.11.txt`
- tag `v3.7.11-runtime-reconciled`

## Workflow Scenarios

### Scenario 1: Client-Provided BOQ

The client provides an Excel BOQ workbook. VALESCO imports the workbook into a controlled working structure, preserves the source workbook evidence, maps minimum pricing fields, records warnings and clarification needs, allocates resource categories, prices ready items and exports a workbook that can be reviewed before use.

Scenario 1 is the first implementation priority because it reflects the lowest-friction commercial workflow: the tenderer already has a structured BOQ, client intent and item numbering are externally defined, and VALESCO can focus on preservation, validation, pricing support and export without first solving document measurement or BOQ authoring.

### Scenario 2: VALESCO-Created BOQ From Tender Documents

VALESCO creates a BOQ from tender documents such as drawings, specifications, schedules and employer requirements. The workflow identifies measurable items, builds a BOQ structure, records assumptions, links evidence, flags gaps and produces a pricing-ready workbook after human review.

Scenario 2 is a later priority because it requires additional document interpretation, measurement rules, evidence linking and human approval gates before BOQ items can be treated as ready to price.

## Minimum Imported BOQ Fields

The import workflow should capture these fields where present or derivable from the client workbook:

- Source workbook filename.
- Source worksheet name.
- Source row number.
- Section or trade heading.
- Item reference or item number.
- Item description.
- Unit.
- Quantity.
- Client rate, where supplied.
- Client amount, where supplied.
- Notes, qualifications or appendices referenced by the item.

Items missing item description, unit or quantity are not ready to price until reviewed.

## Fields Preserved From The Client Workbook

The workflow must preserve client-originated workbook evidence without overwriting it:

- Original workbook file.
- Worksheet names and tab order.
- Row order.
- Section headings and hierarchy.
- Item numbers and references.
- Descriptions exactly as supplied.
- Units exactly as supplied.
- Quantities exactly as supplied.
- Client-supplied rates and amounts.
- Formula results visible in the workbook.
- Client notes, exclusions, qualifications and comments.
- Any cells, rows or sheets not mapped into pricing fields.

Client-authored values remain distinguishable from VALESCO working values.

## Internal VALESCO Working Fields

VALESCO working fields should be stored separately from preserved client fields:

- VALESCO item status.
- Normalised section.
- Normalised unit.
- Quantity review status.
- Resource allocation category.
- Labour allowance.
- Plant allowance.
- Materials allowance.
- Subcontract allowance.
- Preliminaries allowance.
- Proposed rate.
- Proposed amount.
- Confidence level.
- Warning flags.
- Clarification questions.
- Provisional item flag.
- Review owner.
- Review notes.
- Ready-to-price flag.
- Ready-to-export flag.

## Resource Allocation Categories

Each priced item should be allocated across one or more of these categories:

- Labour.
- Plant.
- Materials.
- Subcontract.
- Preliminaries.

The workflow should allow a single BOQ item to carry multiple resource allocations where the commercial build-up requires it.

## Pricing And Export Workbook Shape

The exported workbook should be reviewable by a human estimator and should keep source evidence visible. The expected workbook shape is:

- Cover sheet with project name, source workbook reference, export timestamp, authority reference and warning count.
- Import summary sheet showing source worksheets, rows imported, rows skipped and validation results.
- BOQ pricing sheet containing client item references, descriptions, units, quantities, VALESCO working fields, proposed rates and proposed amounts.
- Resource build-up sheet showing labour, plant, materials, subcontract and preliminaries allocations by item.
- Warnings and clarifications sheet listing every unresolved warning, clarification question and provisional item.
- Export readiness sheet showing ready-to-price and ready-to-export checks.

The export must not silently remove client rows, reorder source items without traceability, or hide unresolved warnings.

## Warning, Clarification And Provisional Item Handling

Warnings should be raised for missing, inconsistent or risky source data. Clarification questions should be recorded when pricing depends on information not available in the client workbook. Provisional items should be explicitly flagged when quantity, scope, specification or pricing basis is uncertain.

Examples include:

- Missing unit.
- Missing quantity.
- Zero or negative quantity where not clearly intentional.
- Ambiguous item description.
- Unit mismatch against likely resource build-up.
- Formula-derived quantity that cannot be traced.
- Client rate supplied but inconsistent with amount.
- Provisional sum, prime cost, daywork or undefined allowance.
- Item requiring specification, drawing or scope clarification.

No warning, clarification or provisional marker may be discarded without a recorded review outcome.

## Ready-To-Price Rules

An item is ready to price only when:

- It has a preserved source reference.
- It has an item description.
- It has a unit.
- It has a quantity or an approved quantity basis.
- Its resource allocation category is selected.
- Any warning affecting price basis has been reviewed.
- Any clarification required before pricing has either been answered or explicitly deferred with approval.
- Any provisional status is visible to the estimator.

Items that do not meet these conditions must remain blocked from final pricing.

## Ready-To-Export Rules

An export is ready only when:

- Every exported item traces back to a source workbook, sheet and row or to an approved VALESCO-created item record.
- Every priced item has a proposed rate and amount or an approved no-price status.
- Every warning is either resolved or carried into the export warnings sheet.
- Every clarification is either answered or carried into the export clarifications sheet.
- Every provisional item remains visibly marked.
- Export totals reconcile with included item amounts.
- The export workbook identifies the governing snapshot and tag.
- No real client BOQ data is committed to the repository.

## Fail-Closed Rules

The workflow must fail closed when evidence or pricing basis is insufficient. It must not silently infer commercial values as final.

Fail-closed conditions include:

- Missing source workbook evidence.
- Missing item description.
- Missing or invalid unit.
- Missing, invalid or unapproved quantity.
- Unresolved warning affecting price, scope or quantity.
- Required clarification unanswered.
- Formula, merged-cell or workbook structure issue preventing reliable import.
- Export total mismatch.
- Attempt to export without warning and clarification sheets.
- Attempt to commit or package a real client BOQ example into the repository.

When a fail-closed condition is present, the workflow may produce a review artifact but must not mark the item or workbook as final.

## Data Protection Rule For Client BOQs

Real client BOQ files, extracted client workbook data and client-identifying examples must not be committed to the repository. Any test fixtures or examples must be synthetic, anonymised and clearly marked as non-client data. Client workbook evidence should be handled as project input or workspace output, not as source-controlled documentation.

## 90-Day Delivery Outline

### Days 1-30: Scenario 1 Import And Preservation

- Define the client BOQ import contract.
- Confirm minimum field mapping and preserved workbook evidence.
- Define synthetic test fixtures only.
- Draft warning, clarification and provisional item taxonomy.
- Define review states for item readiness.

### Days 31-60: Pricing Workspace And Validation

- Define resource allocation working fields.
- Define item-level pricing readiness checks.
- Define fail-closed validation outcomes.
- Define export workbook tabs and totals checks.
- Confirm data protection handling for client inputs.

### Days 61-90: Export And Scenario 2 Preparation

- Define export readiness checks.
- Define human review workflow before issue.
- Record open questions for Scenario 2 BOQ creation from tender documents.
- Identify document evidence requirements for future measurement workflows.
- Prepare implementation backlog without adding real client examples.

## Open Decisions Before Implementation

- Which Excel formats are supported first: `.xlsx` only, or `.xlsm` and legacy `.xls` as well.
- Whether client workbook formulas are preserved as formulas, cached values, or both in review exports.
- How merged cells, hidden rows, filters and multi-row descriptions should be normalised.
- Whether VALESCO item IDs should be generated on import or only after review.
- Which user role can approve deferred clarifications or provisional pricing.
- Whether resource allocations are entered manually first or proposed from a library in a later phase.
- How export workbook branding, protection and locked cells should be handled.
- Whether Scenario 2 requires a separate evidence model before any document-derived BOQ items are created.
- What retention policy applies to uploaded client BOQs and generated review artifacts.
- Whether pricing totals should support alternates, exclusions and optional sections in v0.1.
