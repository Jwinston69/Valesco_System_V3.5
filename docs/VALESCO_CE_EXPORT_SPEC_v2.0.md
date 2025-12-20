\# Valesco v2.0 — CE Export Specification

Version: 1.0

Status: Planning / Architectural

Scope: Defines the format, structure, and validation rules for the v2.0 Context Engineering (CE) export bundle.



-------------------------------------------------------------------------------

1\. PURPOSE

-------------------------------------------------------------------------------

The CE Export Bundle is the input payload consumed by v2.0 multi-agent orchestration.

It contains:



\- Governance (instructions + truth hierarchy + manifest metadata)

\- Allocator configuration

\- Core libraries (materials, tasks, subcontractors)

\- Pack

\- Chunk datasets (materials/tasks/pack/subs)

\- Provenance metadata

\- Version fingerprints

\- Integrity hashes



The bundle is read-only and must not alter authoritative files. It is a deterministic,

replayable representation of the entire Valesco domain for a given version state.



-------------------------------------------------------------------------------

2\. BUNDLE COMPOSITION

-------------------------------------------------------------------------------



The CE Bundle contains the following files:



2.1 Governance

\- valesco\_instructions.txt

\- VALESCO\_TRUTH\_HIERARCHY.md

\- VALESCO\_DEVELOPER\_CHECKLIST.md

\- VALESCO\_SYSTEM\_MANIFEST\_vX.Y.Z.md



2.2 Configuration

\- materials\_allocator.yaml



2.3 Core Library (Authoritative Truth)

\- valesco\_materials.yaml

\- valesco\_tasks.yaml

\- valesco\_subcontractors.yaml



2.4 Pack (Consumption Layer)

\- valesco\_pack.yaml



2.5 Chunk Dataset (Semantic Layer)

\- materials.jsonl

\- tasks.jsonl

\- pack.jsonl

\- subs.jsonl



2.6 Snapshot Metadata (Optional)

\- snapshot\_meta.json (if called from snapshot mode)



2.7 Version \& Integrity Block

\- version\_info.json

\- sha256\_all.txt



-------------------------------------------------------------------------------

3\. FOLDER STRUCTURE WITHIN THE BUNDLE

-------------------------------------------------------------------------------



The CE bundle is archived as a deterministic ZIP:



VALESCO\_CE\_BUNDLE\_<version>\_<timestamp>.zip

│

├── governance/

│     ├── valesco\_instructions.txt

│     ├── VALESCO\_TRUTH\_HIERARCHY.md

│     ├── VALESCO\_DEVELOPER\_CHECKLIST.md

│     └── manifest.md

│

├── allocator/

│     └── materials\_allocator.yaml

│

├── library/

│     ├── valesco\_materials.yaml

│     ├── valesco\_tasks.yaml

│     └── valesco\_subcontractors.yaml

│

├── pack/

│     └── valesco\_pack.yaml

│

├── chunks/

│     ├── materials.jsonl

│     ├── tasks.jsonl

│     ├── pack.jsonl

│     └── subs.jsonl

│

└── meta/

&nbsp;     ├── version\_info.json

&nbsp;     ├── sha256\_all.txt

&nbsp;     └── snapshot\_meta.json (optional)



-------------------------------------------------------------------------------

4\. BUNDLE GENERATION RULES

-------------------------------------------------------------------------------



4.1 Determinism

The bundle must be identical for identical input YAML+TXT files.

No timestamps may appear inside content — only in the filename and bundle-level metadata.



4.2 Read-only

The bundler must never modify:

\- YAML library files

\- Pack

\- Governance documents



4.3 Hashing Rules

The bundler must compute:



\- SHA256 over each individual file

\- SHA256 over concatenated governance text

\- SHA256 over chunk datasets

\- Overall bundle hash (sha256\_all.txt)



4.4 version\_info.json

Must include:



{

&nbsp; "bundle\_version": "v2.0",

&nbsp; "created\_utc": "...",

&nbsp; "materials\_version": "...",

&nbsp; "tasks\_version": "...",

&nbsp; "subcontractors\_version": "...",

&nbsp; "pack\_version": "...",

&nbsp; "allocator\_version": "...",

&nbsp; "sha256": { "file": "hash", ... }

}



4.5 Validation Gate

The bundler must run:



\- Schema validation (materials, tasks, subs, pack)

\- Cross-file validation

\- Pack/labour/plant rate checks

\- Unit whitelist conformity

\- Zero-productivity check

\- No missing material codes in tasks



\*\*If any validation fails → bundle is not produced.\*\*



-------------------------------------------------------------------------------

5\. AGENT CONSUMPTION MODEL

-------------------------------------------------------------------------------



5.1 Supervisor Agent

\- Loads bundle manifest

\- Routes queries based on included domain keys

\- Performs query decomposition using chunk datasets



5.2 Architect Agent

\- Verifies no bundle violates Truth Hierarchy

\- Confirms provenance correctness

\- Approves or rejects agent tool calls



5.3 Estimator Agent

\- Retrieves:

&nbsp; - materials from materials.jsonl

&nbsp; - tasks from tasks.jsonl

&nbsp; - labour/plant/waste/prelims from pack.jsonl

&nbsp; - subcontractors from subs.jsonl

\- Builds First Principles rates

\- Produces provenance from bundle version\_info.json



5.4 Validator Agent

\- Confirms pack/material/task/subs integrity via bundle metadata

\- Re-runs hash checks

\- Ensures authoritative truth has not been modified



-------------------------------------------------------------------------------

6\. CHUNK INDEX FORMAT (IN FUTURE v2.1)

-------------------------------------------------------------------------------



A chunk index may be added:



chunks\_index.json

{

&nbsp; "materials": 909,

&nbsp; "tasks": 37,

&nbsp; "pack": 121,

&nbsp; "subs": 111,

&nbsp; "by\_type": { ... },

&nbsp; "by\_category": { ... },

&nbsp; "sha256": { ... }

}



-------------------------------------------------------------------------------

7\. EXPORT COMMAND TARGET (v2.0)

-------------------------------------------------------------------------------



export ce-bundle



Arguments:

\- --snapshot <id> (optional)

\- --include-chunks (default: true)

\- --format zip (default: zip)



Output:

VALESCO\_CE\_BUNDLE\_<version>\_<timestamp>.zip



-------------------------------------------------------------------------------

8\. SECURITY REQUIREMENTS

-------------------------------------------------------------------------------



8.1 Air Gap Required  

Agent reasoning cannot write to library/core or pack.  

Bundle must be produced by trusted local tool.



8.2 No Agent-Side Modifications  

Agents may read-only.



8.3 Full Structural Validation Required  

Same rules as validate.bat.



-------------------------------------------------------------------------------

END OF DOCUMENT



