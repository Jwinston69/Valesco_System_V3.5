VALESCO_v1.7_BASELINE.md
System Baseline & Immutable Reference Snapshot

(For use in all development, migration, and system integrity checks)

1. Baseline Overview

This document defines the official frozen state of Valesco v1.7 prior to the v1.8 hardening and roadmap transition.
It exists to provide:

A stable recovery point

A fixed version anchor for the Dev Kit

A known-good configuration for schema, docs, and governance

A reference point for migration audits

This file must never change.

2. Baseline Version Metadata
Field	Value
Baseline Version	Valesco v1.7 (Stable)
Baseline Date	2025-11-18
Dev Kit Baseline	v1.7.DevKit-Release-A
Next Planned Version	v1.8 (Hardening / Consolidation)
Build Source	Local Google Drive Workspace
Execution Platform	Windows 11 / Batch + Portable Python
Cloud Behaviour	Not yet cloud-executed; local-only
3. Baseline File Set (“The Big Six”)

All files below are considered core governance for v1.7 and form the basis of strict architectural control.

File	Purpose	Version Status
VALESCO_SYSTEM_MANIFEST_v1.7.txt	System folder map & structural registry	v1.7
VALESCO_DEPENDENCY_MAP.md	Dependency blast-radius & cross-component rules	v1.7
VALESCO_TRUTH_HIERARCHY.md	Hierarchy of authority for all system layers	v1.7
VALESCO_DEVELOPER_CHECKLIST.md	Developer behaviour rules	v1.7 + Rule 14.x applied
valesco_instructions.txt	Execution behaviour, validation rules, lifecycle	v1.7
roadmap_strategy.txt	Legacy roadmap (historical reference)	v1.7

These files define the complete v1.7 governance matrix.

4. Additional Authoritative Documents (Added in 1.8)

Although not part of the v1.7 baseline, two documents are carried forward in the Dev Kit:

File	Purpose
valesco_future_roadmap.md	Authoritative roadmap: v1.7.x → v2.x
_AI_START_PROMPT.txt	AI development session governing prompt

These documents belong to v1.8 and above, but depend on this baseline.

5. Baseline Behavioural Rules

v1.7 systems must follow the exact behavioural definitions in:

valesco_instructions.txt — system logic & rules

VALESCO_TRUTH_HIERARCHY.md — override order

VALESCO_DEVELOPER_CHECKLIST.md — developer constraints

VALESCO_DEPENDENCY_MAP.md — cross-dependency limits

This includes:

5.1 Valid Units

Defined by the whitelist explicitly inside valesco_instructions.txt.

5.2 No AI-driven invention of schema fields

All schema fields must be defined upstream.

5.3 Packs do not include “materials”

Materials are external and must be linked via materials_allocator.

5.4 Extensions are additive only

They cannot override upstream truths.

5.5 Proposals are non-authoritative

They do not write back to core files.

5.6 Strict Error and Validation Rules

Validation behaviour must follow valesco_instructions.txt as written.

5.7 No circular dependencies

Dependency Map defines the blast radius and prohibits reverse direction flows.

6. Baseline System Boundaries

Valesco v1.7 operates entirely:

on a local Windows 11 environment

via Batch + Portable Python

with no cloud execution

and no API-level orchestration

These constraints define the “pre-cloud” system boundary.

7. Baseline Development Constraints

These constraints govern all modifications applied to v1.7 files:

7.1 No schema drift

All schema changes must begin in v1.8, never in v1.7.

7.2 No folder restructuring

Folder paths and file placement in v1.7 must remain intact.

7.3 No behavioural rewrites

valesco_instructions.txt must not be modified retroactively.

7.4 No changes to governance files

Truth Hierarchy → Manifest → Dependency Map must remain frozen.

7.5 No changes to Developer Checklist baseline rules

Only v1.8+ may append sections.

8. Migration Notes

When upgrading to:

v1.8
Hardening, safety rails, Dev Kit improvements

v1.9
Structure consolidation, pack workflow improvements

v2.0
Cloud execution migration

v2.1
Enterprise/runtime standardisation

All decisions must reference this baseline to prevent drift.

9. Sign-Off Summary

This baseline confirms the exact state of:

Folder structure

Governance documents

Behaviour definitions

Legacy roadmap

Developer rules

Cross-component dependencies

Execution boundaries

This document is the canonical “zero point” for all future development.

END OF BASELINE
File Status: Immutable