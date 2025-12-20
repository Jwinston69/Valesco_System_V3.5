\# Valesco Chunk Structure Map — v2.0 (Context Engineering Layer)



Version: 1.0  

Status: Planning/Design (Non-Governance)  

Purpose: Describe the structure and expected usage of the CE chunk dataset created in v1.9.1–v2.0 transition.



---



\## 1. Overview



The following chunk files were generated as part of CE Step 6:



\- `materials.jsonl` — 909 chunks

\- `tasks.jsonl` — 2 generic chunks (placeholder)

\- `pack.jsonl` — 7 chunks (top-level groups)

\- `subs.jsonl` — 3 chunks (top-level groups)



These files are stored under:

workspace/vector\_input/

Each file contains one JSON object per line (JSONL/NDJSON).  

Each object represents a retrieval unit (“atomic chunk”) for future v2.0 agents.



---



\## 2. Chunk File: materials.jsonl



\### 2.1 Summary

\- 909 chunks generated.

\- Each chunk represents \*\*one material node\*\* under `materials\[]`.

\- These are the most retrieval-ready chunks in this dataset.



\### 2.2 Fields Present

\- `id`: deterministic identifier including source file + material code.

\- `type`: `material`

\- `source\_file`: `library/core/valesco\_materials.yaml`

\- `path`: `materials\[N]`

\- `text`: condensed description (code, description, unit, rate)

\- `meta`: full YAML node



\### 2.3 Intended Usage

\- Material lookup for Estimator Agent.

\- Price reconstruction.

\- Cross-file reference validation.

\- Historical comparison and RAG provenance.



---



\## 3. Chunk File: tasks.jsonl (Generic Pass)



\### 3.1 Summary

\- 2 chunks created.

\- These represent \*\*top-level YAML groups\*\*, not individual tasks.



\### 3.2 Notes

This is a temporary structure and will be replaced with a \*\*schema-aware task chunker\*\* that produces:

\- One chunk per task key

\- Includes outputs, gangs, materials links

\- Includes productivity information



\### 3.3 Intended Usage (for now)

\- Structural validation only.

\- Retrieval simulator testing.



---



\## 4. Chunk File: pack.jsonl



\### 4.1 Summary

\- 7 chunks representing:

&nbsp; - meta

&nbsp; - labour

&nbsp; - plant

&nbsp; - prelims

&nbsp; - waste

&nbsp; - productivity

&nbsp; - rules



\### 4.2 Intended Usage

\- Retrieval of pack-level information for Estimator/Validator Agents.

\- Semantic access to labour/plant roles and prelim rules.



---



\## 5. Chunk File: subs.jsonl



\### 5.1 Summary

\- 3 chunks representing the subcontractor YAML layout.



\### 5.2 Intended Usage

\- Retrieval of subcontractor groups.

\- Later versions will produce one chunk per subcontractor item.



---



\## 6. Retrieval Integration Plan (Preview for v2.0)



The chunk dataset will be used for:



1\. \*\*Query Augmentation\*\*

&nbsp;  - Identify the most relevant material/task entries given a BoQ line.

2\. \*\*Semantic Retrieval\*\*

&nbsp;  - Vector-based top-N search over all chunks.

3\. \*\*Task Decomposition\*\*

&nbsp;  - Break complex BoQ lines into subproblems and retrieve chunks for each.

4\. \*\*Agent Tooling\*\*

&nbsp;  - Estimator Agent uses chunks as evidence for rate build-up.

5\. \*\*Memory Architecture\*\*

&nbsp;  - Materials and tasks feed into semantic memory.

&nbsp;  - Snapshots feed into episodic retrieval (not priority truth).



---



\## 7. Next Steps



1\. Implement schema-aware chunkers for:

&nbsp;  - tasks

&nbsp;  - pack

&nbsp;  - subcontractors

2\. Build retrieval simulator.

3\. Define v2.0 Agent Blueprint.

4\. Define Tool API specification.

5\. Integrate retrieval into Estimator/Validator agents in v2.0 cloud.



---



End of Document.

