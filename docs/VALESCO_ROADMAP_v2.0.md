# Valesco Future Roadmap (v1.7 → v2.x)

## Execution Priorities (Mandatory Phase Order)

1. **Phase 1 must be completed before any v1.8 development.**
2. **Phase 2 must be completed before any v1.9 development.**
3. **Phase 3 must be completed before any v2.0 cloud migration.**
4. **Phase 4 must be completed before any v2.1 enterprise features.**

These priorities ensure stable evolution, avoid rework, and maintain system integrity throughout the transition from local v1.x architecture to cloud‑based v2.x.

This roadmap defines the complete evolution of the Valesco Estimating Engine from the current stable local version (v1.7) to a fully cloud-hosted, multi-user architecture (v2.x). It is broken into phases, each with clear objectives, required technical work, and measurable completion criteria.

---

## Phase 0 — Establish v1.7 as the Golden Baseline

**Objective:** Create a fixed, known-good v1.7 reference that can always be restored.

### Actions

* Create `VALESCO_v1.7_BASELINE.md` in `_DEV_KIT` containing:

  * Version tag (e.g., v1.7.3)
  * Known behaviours, limitations, and dependencies
* Snapshot: `engine/`, `library/`, `packs/`, `docs/governance/`, `_START_VALESCO.bat`, `bin/`
* Document current workflows for materials, tasks, validation, and merge

### Done When

* v1.7 can be restored from a zip
* Behaviour is clearly defined and stable

---

## Phase 1 — v1.7.x Hardening + Regression Harness

**Objective:** Make the local system stable, predictable, and fully testable.

### 1.1 Batch Hardening

* Apply `EnableDelayedExpansion` where input is processed
* Sanitize all user-input paths (trim, strip quotes)
* Detect wrong working directory
* Validate Python runtime
* Add clear exit codes and error pauses
* Improve visibility checks for `engine/`

### 1.2 Regression Suite

* Test all `_START_VALESCO.bat` menu options
* Test Material Manager template, import, promote
* Test validator on all packs and schemas
* Test merge workflow
* Optional automation via `regression.bat`

### Done When

* Every update passes a predictable regression checklist

---

## Phase 2 — v1.8 “Intelligence Update”

**Objective:** Add AI-friendly behaviour and stronger validation while retaining local architecture.

### 2.1 Prompt Library

Create `engine/prompts/` containing dedicated role prompts for:

* Estimator Agent
* Material Manager Agent
* Validator Agent
* Merge Agent
* System Architect Agent

### 2.2 Validator Expansion

* Enforce unit whitelist and coherence
* Check cross-file integrity (task↔material↔pack)
* Improve JSON/YAML error output

### 2.3 Smarter Material Manager

* Support multiple extension files
* Add dry-run mode
* More structured CLI output

### 2.4 Documentation Update

* Update system manifest, dependency map
* Add v1.8 behaviour descriptions

### Done When

* AI agents interact consistently using prompts
* Validation is more robust
* Material Manager experience is upgraded

---
## Phase 2.5 — External Intelligence Layer (EIL) — Phase 2 Component

**Objective:** Introduce a governed, strictly non-authoritative External Intelligence Layer for advisory-only supplementary information during estimating and design discussions.

### Purpose

The EIL provides optional, provisional external intelligence to support reasoning when the Valesco internal library does not contain a direct match.  
It may surface:

- Market-typical products  
- External supplier/manufacturer examples  
- Conceptual alternatives  
- Indicative industry benchmarks  
- Advisory background information for estimating discussions  

The EIL acts as a *thinking partner*, not a truth source.

### Position in the Truth Hierarchy

EIL sits **below all Valesco truth layers**, including:

1. Instructions  
2. Schemas  
3. Allocator  
4. Materials  
5. Tasks  
6. Pack  
7. Subcontractors  

EIL **must never override or conflict with any internal Valesco data**.

### Capabilities (Advisory Only)

EIL may:

- Suggest comparable external products when no library match exists  
- Provide typical industry ranges or provisional benchmark costs  
- Surface supplier/manufacturer examples or indicative specs  
- Offer conceptual alternatives or approaches during estimating discussions  
- Support estimator reasoning by filling conversational gaps with non-authoritative context  

### Strict Limitations

EIL must:

- Always return **PROVISIONAL** suggestions  
- Never commit or write data into Materials, Tasks, Pack, or Subcontractors  
- Never replace CE-derived truth  
- Never be treated as authoritative  
- Never bypass the Architect, Estimator, or Validator  
- Never automatically integrate external data into the Valesco system  

### Conceptual Examples (Not behavior rules)

- “No 3m bench found in the library. Typical market products include A, B, C.”  
- “Suppliers X and Y publish indicative specifications; here is a summary.”  
- “Industry cost range for a timber bench is approximately £X–£Y.”  

### Implementation Deferred

The EIL’s **operational rules, routing logic, and integration behavior**  
will be defined in:

**Step 26 — Architect System Prompt v2.0**

This phase only adds the component to the roadmap; it does not authorize active use.

---

## Phase 3 — v1.9 “Data Update”

**Objective:** Raise commercial accuracy and add reporting capabilities.

### 3.1 Supplier Data Ingestion

* Bulk-import key supplier rates
* Enforce naming, coding, and unit standards

### 3.2 Task Calibration

* Use real project history to tune productivity outputs
* Optionally version tasks

### 3.3 Reporting Uplift

* Improve human export template
* Add CSV/JSON structured reporting
* Highlight assumptions, warnings, and provisional items

### 3.4 Spon External Works Benchmarking (Optional Intelligence Module)

A post-rate benchmarking module using Spon External Works & Landscape 2025 as an industry reference.

* Provides variance checks against Valesco-constructed rates.
* Flags outliers above/below benchmark ranges.
* Advisory-only: does **not** alter Valesco rate logic or build-up outputs.
* Helps validate commercial fit, VE justification, and TRP framework alignment.
* Implemented as a simple `spon_2025.yaml` reference pack.

### Done When

* Data feels commercially strong
* Outputs are client-ready
* Optional Spon benchmarks provide additional confidence

---

## Phase 4 — v2.0 Web-Hosted Architecture

**Objective:** Transform Valesco from a local toolkit to a web-hosted platform accessible from any device.

### 4.1 Extract Engine as a Python Package

* Convert scripts into modules under `engine/valesco_engine/`
* Remove hardcoded paths

### 4.2 Storage Abstraction Layer

Define a storage interface that supports:

* Local filesystem (dev mode)
* S3 (cloud mode)

### 4.3 FastAPI Service Layer

Expose engine functions through API endpoints:

* `/materials/template`
* `/materials/import`
* `/validate`
* `/merge`
* `/snapshot`

### 4.4 Web UI

Start with Streamlit or lightweight React:

* Buttons for template, import, validate, merge
* Status/warnings panel
* Project workspace browser

### 4.5 Authentication & Multi-Device Support

* Basic auth/API key initially
* Later: Cognito, Supabase, or enterprise IAM

### Done When

* The full engine is accessible via browser with no installs
* Cloud storage and API actions work reliably

---

## Phase 5 — v2.1+ Enterprise Enhancements

**Objective:** Enable multi-user, audited, collaborative estimating.

### 5.1 Multi-User Projects

* Project table with roles and permissions
* Workspace isolation

### 5.2 Audit / Version History

* Track all changes to packs, materials, tasks
* Provide diffing and rollback

### 5.3 Team Workflows

* Framework-specific templates (TRP, EA, LLDC)
* Risk registers, VE options, scope reviews

### 5.4 Advanced AI Integration

* AI agents read/write directly to S3
* Provide VE suggestions, risk flags, scope maps
* Generate structured change proposals

### Done When

* The system supports teams, history, and collaborative workflows

---

## Recommended Execution Timeline

1. **Now** – Finish v1.7.x hardening + regression suite
2. **Next 1–2 months** – Deliver v1.8 (Prompts + Validator + Manager enhancements)
3. **Next 3–6 months** – Build v1.9 (Data + Reporting + Spon benchmarking)
4. **After 1.x stabilises** – Extract engine for v2.0 cloud architecture
5. **Post-hosting** – Add enterprise features in v2.1+

---

## Summary

Valesco evolves through three chapters:

* **v1.x:** Local Engine (Stable, Intelligent, Reliable)
* **v2.0:** Cloud Engine (API-Based, Device-Agnostic)
* **v2.1+:** Enterprise Engine (Multi-User, Audited, Collaborative)

This roadmap provides a clear, structured path from the current local system to a scalable, cloud-based, AI-integrated future architecture.
