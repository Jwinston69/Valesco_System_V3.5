\# Valesco v2.0 — Context Engineering Addendum



Version: 0.1 (Draft)

Status: Planning Document

Scope: Bridge from v1.9.1 (Portable Runtime) to v2.0 (Cloud Engine) using context engineering principles.



This document refines the existing `VALESCO\_ROADMAP\_v2.0.md` by specifying how

retrieval, agents, tools, and memory will work in the v2.0 architecture.



It does NOT change any governance files, instructions, schemas, or libraries.

It is a planning aid for development only.



---



\## CE-0 — Constraints and Invariants



1\. Truth Hierarchy remains unchanged:

&nbsp;  - Instructions > Schemas > Allocator > Libraries > Packs > Extensions > Proposals > Runtime.

2\. Context engineering components (retrieval, memory, agents, tools) must:

&nbsp;  - Never override upstream truths.

&nbsp;  - Never write directly to core libraries (`library/core`).

&nbsp;  - Interact via existing tools (`material\_manager`, `merge`, `validate`) or v2.0 API equivalents.

3\. Snapshots remain immutable. They may be used as retrieval sources but not as a higher-priority truth than core libraries.



---



\## CE-1 — Conceptual Model



Goal: Replace the v1.9.1 “static bundle” model with a v2.0 “dynamic retrieval + agents” model.



\### 1.1 Context Layers



\- \*\*Semantic Memory (Authoritative Data)\*\*

&nbsp; - `library/core/valesco\_materials.yaml`

&nbsp; - `library/core/valesco\_tasks.yaml`

&nbsp; - `library/core/valesco\_subcontractors.yaml`

&nbsp; - `library/packs/valesco\_pack.yaml`

&nbsp; - Allocator and schemas.

\- \*\*Episodic Retrieval Sources (Historical Data)\*\*

&nbsp; - `workspace/snapshots/` content.

&nbsp; - Selected historical exports or project summaries.

\- \*\*Short-Term Working Context\*\*

&nbsp; - Per-request context window built from retrieved chunks, current BoQ lines, and active project docs.



All retrieval and memory systems are strictly downstream of the Truth Hierarchy.



---



\## CE-2 — YAML-Aware Chunking \& Retrieval



Objective: Prepare the v2.0 engine to use vector-based retrieval without corrupting YAML semantics.



\### 2.1 Atomic Chunk Definition



For the purpose of retrieval:



\- \*\*Materials:\*\*

&nbsp; - One atomic chunk per material item (e.g. one `MAT.STD.\*` or `MAT.BES.\*` node).

\- \*\*Tasks:\*\*

&nbsp; - One atomic chunk per task (including its outputs, materials links, and metadata).

\- \*\*Pack Content:\*\*

&nbsp; - One atomic chunk per labour/plant/prelim/waste “unit of meaning” (e.g. a single labour role, one plant item, one prelim line).

\- \*\*Subcontractors:\*\*

&nbsp; - One atomic chunk per subcontract item.



Each chunk must include:



\- Source file (e.g. `library/core/valesco\_materials.yaml`).

\- YAML path or logical identifier.

\- Human-readable text expansion for the LLM (description, unit, rate, code, group, etc.).

\- Version metadata when available.



\### 2.2 Chunking Rules



1\. Chunking must respect YAML boundaries (no splitting inside a material or task).

2\. Chunking is a pre-processing step only; it never writes back to YAML.

3\. Chunk output format (initial proposal):

&nbsp;  - NDJSON/JSONL: one JSON object per chunk.

&nbsp;  - Top-level keys: `id`, `source\_file`, `path`, `type`, `text`, `meta`.



\### 2.3 Retrieval Engine (v2.0 Target)



\- A v2.0 microservice ingests chunks into a vector database.

\- At query time, the Estimator / Validator agents request specific retrieval:

&nbsp; - “Find materials related to X”

&nbsp; - “Find tasks with unit m2 involving paving”

\- Retrieve N best chunks and pass them into the LLM context window.



No retrieval component has the authority to change any YAML or pack data.



---



\## CE-3 — Agent Roles and Orchestration



Objective: Clarify how agents will operate in a retrieval-based v2.0 world.



\### 3.1 Core Agents



\- \*\*Supervisor Agent (new in v2.0)\*\*

&nbsp; - Interprets user requests.

&nbsp; - Decides which specialized agent to invoke (Estimator, Validator, Material Manager, Merge).

&nbsp; - Ensures each request obeys project scope and file status.



\- \*\*Architect Agent\*\*

&nbsp; - Enforces Truth Hierarchy and governance compliance.

&nbsp; - Rejects flows that would bypass instructions, schemas, or tools.

&nbsp; - Approves or rejects structural changes and tool orchestration plans.



\- \*\*Estimator Agent\*\*

&nbsp; - Performs first-principles rate build-up.

&nbsp; - Uses retrieval to locate relevant materials, tasks, and pack entries.

&nbsp; - Uses query decomposition for complex BoQ items (labour, plant, materials, productivity).



\- \*\*Validator Agent\*\*

&nbsp; - Coordinates schema validation, cross-file rules, and runtime checks.

&nbsp; - May call validate APIs/tools, but never edits core data.



\- \*\*Material Manager / Merge Agents\*\*

&nbsp; - Provide advisory and integration logic for new items and proposals.

&nbsp; - Operate only via extension and proposal workflows.



\### 3.2 Orchestration Pattern



All agents follow a Thought–Action–Observation loop:



1\. Thought: decide whether to retrieve, validate, or price.

2\. Action: call a retrieval endpoint or a v2.0 tool API.

3\. Observation: inspect results; either proceed, retry with rewritten query, or escalate to user for assumptions.



---



\## CE-4 — Memory Strategy



Objective: Introduce memory layers without violating governance.



\### 4.1 Memory Types



\- \*\*Short-Term (Context Window)\*\*

&nbsp; - Current BoQ lines, retrieved chunks, and active instructions.

&nbsp; - Reset per major task or request.



\- \*\*Working Memory\*\*

&nbsp; - Task-scoped state during multi-step operations (e.g., pricing all lines of a fence system).

&nbsp; - Stored in transient state (database or in-memory) and cleared when task completes.



\- \*\*Long-Term Retrieval Sources\*\*

&nbsp; - Semantic: library and pack chunks.

&nbsp; - Episodic: snapshots and selected historical exports (read-only).



\### 4.2 Rules



1\. No “learning” that alters upstream truth.

2\. Memory stores \*references\* to authoritative data, not parallel copies.

3\. Retrieval over snapshots is clearly tagged as historical and never silently overrides current pack/library.



---



\## CE-5 — Tool Integration (v2.0 API Level)



Objective: Move from manual batch scripts to structured v2.0 tools.



\### 5.1 Toolization Strategy



Existing scripts become v2.0 engine functions:



\- `validate\_project()` → wraps `validate.py`.

\- `manage\_materials()` → wraps `material\_manager.py`.

\- `merge\_proposals()` → wraps `merge.py`.

\- `prepare\_context()` → replaced by retrieval pre-processing and config endpoints.



All tool calls are:



\- Explicit, logged, and auditable.

\- Routed through the Supervisor + Architect agents.

\- Executed in a service context that maintains the Air Gap between AI reasoning and file system writes.



---



\## CE-6 — Execution Phases (Add-On to Existing Roadmap)



The existing v2.0 roadmap remains the primary plan. This addendum adds:



1\. \*\*CE-1 (Design) — NOW\*\*

&nbsp;  - Finalize this addendum.

&nbsp;  - Confirm chunking formats and retrieval surfaces.



2\. \*\*CE-2 (Chunking \& Export) — Pre-v2.0\*\*

&nbsp;  - Implement YAML-aware chunking tools and emit NDJSON chunks for materials/tasks/pack/subs.

&nbsp;  - Store outputs in `workspace/vector\_input/`.



3\. \*\*CE-3 (Retrieval Prototype) — v2.0 dev\*\*

&nbsp;  - Stand up a prototype vector DB.

&nbsp;  - Wire Estimator/Validator agents to query chunked data in a dev-only environment.



4\. \*\*CE-4 (Full v2.0 Integration)\*\*

&nbsp;  - Promote retrieval and agents into the production v2.0 API.

&nbsp;  - Deprecate `\_UPLOAD\_ME`-style static bundles for cloud



