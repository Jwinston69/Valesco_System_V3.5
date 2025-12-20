\# Valesco v2.0 — Tool API Specification

Version: 1.0

Status: Planning Draft

Scope: Defines the tool interface for the v2.0 Cloud Engine, providing a secure Air Gap layer between AI reasoning and system operations.



---------------------------------------------------------------------



1\. Purpose

This document describes the standardised API-based tool interface for the Valesco v2.0 Cloud Engine. Tools represent the approved mechanisms through which agents may request validation, merging, retrieval, or context processing.



Tools replace the local batch scripts used in v1.9.1 but preserve all governance and safety rules. No tool may violate the Truth Hierarchy or modify authoritative data without Architect approval.



---------------------------------------------------------------------



2\. Tool Architecture Overview

Each tool is implemented as a stateless HTTP endpoint (FastAPI or equivalent).



All tools:

\- Must validate all inputs

\- Must enforce schema and type checks

\- Must reject unsafe operations

\- Must log all calls

\- Must require Architect Agent approval

\- Must preserve existing Air Gap behaviour



Tool types:

\- Validation tools

\- Retrieval tools

\- Materials tools

\- Merge tools

\- Snapshot tools

\- Context tools (future)



---------------------------------------------------------------------



3\. Tool Set (v2.0 Minimum)



3.1 validate\_project

Purpose: Perform full schema validation on pack, materials, tasks, subcontractors and cross-file checks.

Method: POST

Endpoint: /validate/project

Input:

&nbsp; { "project\_id": "<id>" }

Output:

&nbsp; { "status": "PASS"|"FAIL", "errors": \[...], "warnings": \[...] }



3.2 validate\_schemas

Purpose: Run schema-only validation on YAML inputs.

Endpoint: /validate/schemas

Input:

&nbsp; { "files": \["valesco\_materials.yaml", ...] }

Output:

&nbsp; { "status": "PASS"|"FAIL", "details": \[...] }



3.3 retrieve\_chunks

Purpose: Retrieve semantic chunks from the vector database.

Endpoint: /retrieve/chunks

Input:

&nbsp; { "query": "concrete", "top\_k": 10 }

Output:

&nbsp; { "results": \[ { "id": "...", "score": 0.87, "text": "...", "meta": {...} } ] }



3.4 retrieve\_by\_id

Purpose: Direct lookup of a single chunk by ID.

Endpoint: /retrieve/by-id

Input:

&nbsp; { "id": "<chunk\_id>" }

Output:

&nbsp; { "chunk": { ... } }



3.5 propose\_material

Purpose: Accept a new BES-level material proposal.

Endpoint: /materials/propose

Input:

&nbsp; { "description": "...", "unit": "...", "rate": ..., "notes": "...", "supplier": "..." }

Output:

&nbsp; { "provisional\_id": "MAT.BES.XX.XX.XXX", "status": "accepted" }



3.6 classify\_material

Purpose: Categorise a material proposal according to allocator rules.

Endpoint: /materials/classify

Input:

&nbsp; { "description": "...", "unit": "m2" }

Output:

&nbsp; { "category": "01", "group": "03" }



3.7 merge\_proposals

Purpose: Safely append proposal items to extensions/materials\_ext.yaml.

Endpoint: /merge/proposals

Input:

&nbsp; { "project\_id": "<id>" }

Output:

&nbsp; { "merged": \[...], "rejected": \[...] }



3.8 snapshot\_create

Purpose: Create an immutable snapshot of all authoritative files.

Endpoint: /snapshot/create

Input:

&nbsp; { "label": "string" }

Output:

&nbsp; { "snapshot\_path": "..." }



3.9 snapshot\_get

Purpose: Return metadata about a snapshot.

Endpoint: /snapshot/get

Input:

&nbsp; { "snapshot\_id": "..." }

Output:

&nbsp; { "meta": {...}, "paths": \[...] }



3.10 prepare\_context

Purpose: Generate a context bundle for external agents.

Endpoint: /context/prepare

Input:

&nbsp; { "project\_id": "<id>" }

Output:

&nbsp; { "bundle": "<base64 or url>" }



---------------------------------------------------------------------



4\. Tool Access Control

4.1 All tools require explicit Architect Agent approval.

4.2 Tools cannot modify authoritative data unless:

&nbsp;    - The request originates from an approved command

&nbsp;    - Architect Agent approves the call

&nbsp;    - The operation follows the Truth Hierarchy

4.3 Tools must log:

&nbsp;    - Caller agent

&nbsp;    - Timestamp

&nbsp;    - Input payload

&nbsp;    - Output status

&nbsp;    - Validation results



---------------------------------------------------------------------



5\. Error Handling

Standardised error format:

{

&nbsp; "error": true,

&nbsp; "code": "VALIDATION\_FAIL" | "BAD\_REQUEST" | "UNAUTHORISED" | "NOT\_FOUND" | "INTERNAL",

&nbsp; "message": "text description",

&nbsp; "details": { optional }

}



---------------------------------------------------------------------



6\. Future Tools (v2.1+)

\- pack\_dev\_kit: deeper pack authoring engine

\- task\_editor: safe modification environment for tasks

\- rule\_analyser: computes rule impacts

\- retrieval\_explain: explain why retrieval selected particular chunks

\- semantic\_diff: compare differences between snapshots, materials, pack, tasks



---------------------------------------------------------------------



7\. Conclusion

This specification defines the foundational tool interface for the v2.0 Cloud Engine. It ensures:

\- Deterministic operations

\- Full compliance with Truth Hierarchy

\- Secure agent interactions

\- Cloud-native orchestration

\- Compatibility with retrieval and memory systems



End of Document.



