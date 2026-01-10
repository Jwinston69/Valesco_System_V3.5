\# VALESCO\_REGRESSION\_SUITE\_v1.9.md

Full Regression Test Specification (Architecture v1.9)



1\. Purpose

This file defines the regression standard for Valesco v1.9 (Intelligent-Tools).

It ensures that the "Self-Activating" context and "Open Box" file delivery work correctly.



2\. System-Wide Invariants

2.1 Folder Structure

The following must exist:

\- bin\\

\- docs\\

\- engine\\prompts\\

\- library\\packs\\

\- workspace\\



2.2 Governance Files (The Integrity Core)

These files must exist:

\- VALESCO\_SYSTEM\_MANIFEST\_v1.9.txt

\- VALESCO\_DEPENDENCY\_MAP.md

\- VALESCO\_TRUTH\_HIERARCHY.md

\- VALESCO\_DEVELOPER\_CHECKLIST.md

\- valesco\_instructions.txt

\- VALESCO\_ROADMAP\_v2.0.md



3\. Batch Script Tests



3.1 prepare\_context.bat (The Engine)

Test: Run script.

Expected Result:

1\. Creates folder `\_UPLOAD\_ME`.

2\. Generates `VALESCO\_FULL\_CONTEXT.txt` with `### VALESCO SYSTEM ACTIVATION HEADER` on Line 1.

3\. Generates `\_ACTIVATION\_KEY.txt` containing the command string.

4\. Copies physical YAML files (pack, materials, tasks) into the folder.

5\. Opens the folder automatically.



3.2 pack\_dev\_kit.bat (The Architect)

Test: Run script.

Expected Result:

1\. Creates `\_DEV\_KIT` folder.

2\. Generates `\_AI\_START\_PROMPT.txt`.

3\. Prompt contains text from `VALESCO\_ROADMAP\_v2.0.md` (not the old future\_roadmap).



4\. Python Runtime Tests

Test: Run `bin\\validate.bat`

Expected: System acknowledges v1.9 architecture and passes schema validation.



5\. Migration Assurance

Test: `VALESCO\_v1.7\_BASELINE.md` exists and is unchanged (Historical Record).

