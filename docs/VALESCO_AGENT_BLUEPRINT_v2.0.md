\# Valesco v2.0 — Agent Blueprint

Version: 1.0  

Status: Planning / Pre-Implementation  

Scope: Defines the multi-agent architecture for the Valesco v2.0 Cloud Engine.



This document is non-governance but authoritative for development planning.  

It must remain consistent with:

\- VALESCO\_TRUTH\_HIERARCHY.md  

\- VALESCO\_DEVELOPER\_CHECKLIST.md  

\- valesco\_instructions.txt  

\- VALESCO\_ROADMAP\_v2.0  

\- The Context Engineering Addendum  



---



\# 1. Purpose of the Agent Blueprint



Valesco v2.0 moves from a static prompt-driven architecture to a multi-agent,

retrieval-powered orchestration model.  

This Blueprint defines:

\- The agents that exist in v2.0

\- Their responsibilities

\- Their interaction boundaries

\- Their allowed tools

\- How retrieval and memory integrate

\- How the Truth Hierarchy is protected



Agents do NOT override upstream truth, modify libraries directly, or bypass tool workflows.



---



\# 2. Agent Overview (v2.0)



The v2.0 system uses the following core agents:



1\. \*\*Supervisor Agent (NEW)\*\*

2\. \*\*Architect Agent (EXISTING ROLE, UNCHANGED PURPOSE)\*\*

3\. \*\*Estimator Agent\*\*

4\. \*\*Validator Agent\*\*

5\. \*\*Materials Agent\*\*

6\. \*\*Merge Agent\*\*



Optional / Future:

\- \*\*Retrieval Agent\*\*

\- \*\*Memory Agent\*\*

\- \*\*Snapshot/History Agent\*\*



Each agent is described in detail below.



---



\# 3. Supervisor Agent (New in v2.0)



\## 3.1 Purpose  

Primary orchestrator.  

Receives user intent and decides which specialist agent should handle the task.



\## 3.2 Responsibilities  

\- Interpret user intent.  

\- Route request to Estimator, Validator, Architect, Materials, or Merge Agent.  

\- Decide whether retrieval is required.  

\- Manage multi-step workflows (e.g., pricing multiple BoQ lines).  

\- Maintain working memory for in-progress tasks.  

\- Apply query rewriting or query decomposition before delegation.  



\## 3.3 Forbidden  

\- Cannot bypass Architect Agent.  

\- Cannot call tools that modify the filesystem without Architect approval.  

\- Cannot generate or modify YAML or pack files directly.  



---



\# 4. Architect Agent (Governance Enforcer)



\## 4.1 Purpose  

Enforces Valesco Truth Hierarchy and developer constraints.



\## 4.2 Responsibilities  

\- Approve or reject Supervisor routing and tool calls.  

\- Reject any action that violates:

&nbsp; - Instructions  

&nbsp; - Schema rules  

&nbsp; - Allocator  

&nbsp; - File boundaries  

&nbsp; - Library constraints  

\- Ensure retrieval results do not override authoritative truth.  

\- Maintain Air Gap safety logic.  



\## 4.3 Forbidden  

\- Cannot perform pricing or material management.  

\- Cannot alter data or files.  

\- Cannot execute tool logic itself.  



---



\# 5. Estimator Agent



\## 5.1 Purpose  

Performs First Principles rate build-up with retrieval assistance.



\## 5.2 Responsibilities  

\- Apply the deterministic mapping rules (§3a in instructions).  

\- Use retrieval to find materials, tasks, and pack entries.  

\- Use query decomposition for complex BoQ lines:

&nbsp; - labour

&nbsp; - plant

&nbsp; - materials

&nbsp; - productivity  

\- Build rates only from authoritative pack + library data.  

\- Raise assumptions when data is missing.  

\- Produce full provenance.  



\## 5.3 Forbidden  

\- Cannot invent material codes.  

\- Cannot override pack or library values.  

\- Cannot skip productivity rules.  

\- Cannot call merge or materials tools.  



---



\# 6. Validator Agent



\## 6.1 Purpose  

Enforce structural correctness and cross-file validation.



\## 6.2 Responsibilities  

\- Run schema validation (via tool API).  

\- Run cross-file checks:

&nbsp; - Task → Material links  

&nbsp; - Pack → Materials  

&nbsp; - Unit whitelist  

&nbsp; - Productivity keys  

\- Detect rule conflicts.  

\- Validate retrieval outputs for coherence.  



\## 6.3 Forbidden  

\- Cannot change files or fix data automatically.  

\- Cannot invent missing fields.  



---



\# 7. Materials Agent



\## 7.1 Purpose  

Assist with new material suggestions, comparisons, and classification.



\## 7.2 Responsibilities  

\- Retrieve relevant materials.  

\- Detect near-duplicates.  

\- Suggest new materials (BES codes).  

\- Provide mapping to allocator categories.  



\## 7.3 Forbidden  

\- Cannot write to core library.  

\- Cannot promote materials.  

\- Cannot bypass merge or material\_manager tools.



---



\# 8. Merge Agent



\## 8.1 Purpose  

Handle merge of proposals into extension files.



\## 8.2 Responsibilities  

\- Validate proposal items.  

\- Identify conflicts.  

\- Use merge tool to safely append new BES items.  

\- Add provenance notes.  



\## 8.3 Forbidden  

\- Cannot edit core materials.  

\- Cannot override or replace standard items.  



---



\# 9. Retrieval Integration (v2.0)



\## 9.1 How Agents Use Retrieval  

All agents may request retrieval but do not perform embedding or database interaction.  

Retrieval results flow into their working context.



Primary uses:

\- Estimator: materials/tasks/productivity lookups  

\- Validator: cross-file alignment  

\- Materials Agent: similarity matching  

\- Supervisor: task routing  



\## 9.2 Retrieval Rules  

\- Retrieval is \*\*downstream\*\* of Truth Hierarchy.  

\- Retrieval cannot contradict authoritative YAML.  

\- Retrieval cannot silently replace missing values.  



---



\# 10. Tool API Usage (v2.0)



\## 10.1 Allowed Tools for Agents  

\- Estimator: retrieve\_x(), calculate\_x()  

\- Validator: validate\_project(), check\_schema()  

\- Materials: classify\_material(), compare\_materials()  

\- Merge: merge\_proposals(), write\_ext()  

\- Supervisor: high-level orchestration only  

\- Architect: approve\_tool\_call()  



\## 10.2 Tool Access Rules  

\- All tools require Architect approval.  

\- Tools implement the Air Gap.  

\- Agents interact through APIs, not directly with filesystem.  



---



\# 11. Memory Integration (v2.0)



\## 11.1 Memory Layers  

\- Short-term: per-request context  

\- Working memory: multi-step workflows (Supervisor-owned)  

\- Semantic memory: materials/tasks/pack chunks  

\- Episodic retrieval: snapshots (read-only, non-authoritative)  



\## 11.2 Memory Restrictions  

\- No persistent learning that conflicts with YAML truths.  

\- No task/productivity caching beyond session unless explicitly validated.  



---



\# 12. Interaction Diagram (Text Form)



User → Supervisor Agent

Supervisor → Architect (approval)

Supervisor → Retrieval (if needed)

Supervisor → \[Estimator | Validator | Materials | Merge]

Specialist Agent → Tools (via Architect approval)

Tools → Return results

Supervisor → Format final response




---



\# 13. Next Steps (Post-Blueprint)



1\. Create Tool API Spec (v2.0).  

2\. Implement retrieval simulator.  

3\. Build schema-aware chunkers.  

4\. Begin v2.0 engine extraction.  



---



End of Document.

