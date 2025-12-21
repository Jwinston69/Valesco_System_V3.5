\# Governance Contracts



This directory contains \*\*normative governance contracts\*\* that define and constrain

AI authority within the Valesco system.



These documents are \*\*not executable\*\*, \*\*not optional\*\*, and \*\*not advisory\*\*.

They establish hard behavioural boundaries enforced by validators and snapshots.



---



\## What These Contracts Are



Governance Contracts:



\- Define \*\*what the AI is allowed to do\*\*

\- Define \*\*what the AI is explicitly forbidden from doing\*\*

\- Establish \*\*hard gates, veto points, and escalation rules\*\*

\- Ensure decisions are \*\*auditable, replayable, and reversible\*\*

\- Protect against silent assumption filling, false certainty, and truth mutation



They operate \*\*above all subsystems\*\*.



---



\## What These Contracts Are Not



These contracts do \*\*not\*\*:



\- Execute logic

\- Resolve missing information

\- Commit prices or scope

\- Modify libraries or schemas

\- Replace human authority



They constrain behaviour; they do not perform work.



---



\## Contract Index



\### 1. Missing-Item Routing Contract (v2)



\*\*File:\*\* `missing-item-routing.v2.md`



\*\*Purpose:\*\*  

Defines how the system handles missing, ambiguous, or insufficient information.



\*\*Key Controls:\*\*

\- Authoritative A–E missing-item state model

\- Explicit routing only (no resolution by AI)

\- Hard blocks on unsafe progression

\- System-derived confidence calibration

\- Mandatory validator oversight



\*\*Applies To:\*\*  

Router · Architect · CE · Validator · Estimator



---



\### 2. Option Selection Contract (v2)



\*\*File:\*\* `option-selection.v2.md`



\*\*Purpose:\*\*  

Allows AI to recommend a default option when multiple valid options exist,

without granting commitment authority.



\*\*Key Controls:\*\*

\- Functional intent binding

\- Comparability and reversibility gates

\- Evidence-based confidence calibration

\- Mandatory disclosure of alternatives

\- Validator veto on default recommendation



\*\*Applies To:\*\*  

Architect · CE · Option Router · Validator



---



\### 3. Variant \& Sensitivity Generation Contract (v2)



\*\*File:\*\* `variant-sensitivity-generation.v2.md`



\*\*Purpose:\*\*  

Enables AI-led exploration of uncertainty and risk around a baseline

without destabilising or replacing it.



\*\*Key Controls:\*\*

\- Authoritative variant type enumeration

\- Baseline binding (no new intents or scopes)

\- Explicit deltas and impact bands

\- No optimisation or preference selection

\- Exploration-only authority



\*\*Applies To:\*\*  

Estimator · CE · Risk Analysis · Validator



---



\## Authority Hierarchy



Governance Contracts sit \*\*above\*\*:



\- Engine modules

\- Schemas

\- Cost libraries

\- Extensions

\- Snapshots



They are referenced by snapshots but \*\*never embedded within them\*\*.



---



\## Versioning Rules



\- Contracts are versioned explicitly (`v2`, `v3`, etc.)

\- Changes require:

&nbsp; - Clear rationale

&nbsp; - Explicit version bump

&nbsp; - Snapshot compatibility review

\- Snapshots must reference:

&nbsp; - Contract name

&nbsp; - Version

&nbsp; - (Optional) content hash



---



\## Snapshot Interaction



Snapshots:

\- Reference governance contracts

\- Record outcomes constrained by them

\- Do \*\*not\*\* duplicate or override them



If a snapshot conflicts with a contract, \*\*the contract wins\*\*.



---



\## One Governing Principle



> \*\*AI may guide, rank, and explore.  

> The system enforces.  

> Humans decide.\*\*



These contracts exist to keep that principle true.



