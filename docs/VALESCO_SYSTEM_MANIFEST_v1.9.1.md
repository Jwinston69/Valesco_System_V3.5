\# Valesco Estimating System — Definitive System Manifest

======================================================

Version: 1.9.1 (Intelligent-Tools)

Status:  ACTIVE

Updated: 2025-12-01

Architecture: Hybrid (Portable Runtime)



1\. SYSTEM OVERVIEW

------------------

Valesco v1.9.1 refines the "Self-Activating" architecture.

It introduces a "Portable Runtime" model, ensuring the system runs

identically on any machine without global Python installation.



2\. DIRECTORY STRUCTURE

------------------------------------------

C:\\Valesco\_System\\

├── \_START\_VALESCO.bat        \[MASTER CONSOLE + SINGLETON LOCK]

├── bin\\                      \[EXECUTABLES]

│   ├── install\_deps.bat      \[PORTABLE BOOTSTRAPPER]

│   ├── material\_manager.bat  \[INTERACTIVE TOOL]

│   ├── merge.bat             \[INTERACTIVE TOOL]

│   ├── pack\_dev\_kit.bat      \[ARCHITECT TOOL]

│   ├── prepare\_context.bat   \[CONTEXT ENGINE]

│   ├── snapshot\_archive.bat  \[BACKUP TOOL]

│   └── validate.bat          \[INTEGRITY CHECKER]

├── docs\\                     \[GOVERNANCE]

│   ├── VALESCO\_DEPENDENCY\_MAP.md

│   ├── VALESCO\_REGRESSION\_SUITE\_v1.9.md

│   ├── VALESCO\_ROADMAP\_v2.0.md

│   ├── VALESCO\_SYSTEM\_MANIFEST\_v1.9.1.md  <-- (YOU ARE HERE)

│   ├── VALESCO\_v1.7\_BASELINE.md

│   └── governance\\

│       ├── VALESCO\_DEVELOPER\_CHECKLIST.md

│       ├── VALESCO\_TRUTH\_HIERARCHY.md

│       └── valesco\_instructions.txt

├── engine\\                   \[THE MACHINERY]

│   ├── config\\

│   │   └── materials\_allocator.yaml

│   ├── prompts\\              \[INTELLIGENCE LAYER]

│   │   ├── agent\_architect.txt

│   │   ├── agent\_estimator.txt

│   │   ├── agent\_material\_manager.txt

│   │   ├── agent\_merge.txt

│   │   └── agent\_validator.txt

│   ├── python\_runtime\\       \[PORTABLE ENGINE - DO NOT COMMIT]

│   │   ├── python.exe

│   │   └── (Lib/Scripts)

│   ├── schemas\\              \[VALIDATORS]

│   │   ├── valesco\_materials.schema.json

│   │   ├── valesco\_pack.schema.json

│   │   └── (others)

│   └── scripts\\              \[LOGIC CORES]

│       ├── material\_manager.py

│       ├── merge.py

│       ├── prepare\_context.py

│       └── validate.py

├── library\\                  \[THE TRUTH - DATABASE]

│   ├── core\\

│   │   ├── valesco\_materials.yaml

│   │   ├── valesco\_subcontractors.yaml

│   │   └── valesco\_tasks.yaml

│   ├── extensions\\

│   │   └── materials\_ext.yaml

│   └── packs\\

│       └── valesco\_pack.yaml

└── workspace\\                \[THE CONTEXT - USER AREA]

&nbsp;   ├── inputs\\               (Client Docs / BoQ)

&nbsp;   ├── outputs\\              (Reports \& Excel Templates)

&nbsp;   ├── proposals\\            (AI Staging Area)

&nbsp;   └── snapshots\\            (Project History)



3\. ARCHITECTURAL RULES (v1.9.1)

-------------------------------

1\. \*\*The Portable Rule:\*\* All Batch scripts must check for `engine\\python\_runtime\\python.exe` before falling back to system python.

2\. \*\*The Singleton Rule:\*\* `\_START\_VALESCO.bat` enforces a lock file (`%TEMP%\\valesco\_v1.9.lock`) to prevent concurrent write access.

3\. \*\*The Hybrid Context:\*\* `prepare\_context.bat` bundles Governance (Text) + Tools (YAML) into `\_UPLOAD\_ME`.

4\. \*\*Path Safety:\*\* All Batch scripts use `pushd "%~dp0.."` to resolve absolute roots.



4\. DEPRECATED / REMOVED

-----------------------

\- bin/view\_manual.bat

\- engine/scripts/valesco\_dependency\_check.py

\- engine/scripts/valesco\_view\_manual.py

\- engine/scripts/valesco\_validate\_local.py (Renamed to validate.py)



End of Manifest.

