\# Assembly \& Pack Integration Plan v3.0  

\*\*Purpose:\*\* Developer-facing operational plan for introducing deterministic assemblies and packs into the Valesco Phase-3 production system.  

\*\*Not governance.\*\* No estimator behaviour, CE behaviour, or pricing rules are defined or modified here.



---



\# 1. Purpose of Assemblies \& Packs



Assemblies and packs enable Valesco to represent multi-component construction systems as \*single selectable units\* that expand into explicit catalog items during pricing.



Key goals:



\- Allow estimators to choose one system (e.g., \*100mm Timber Stud Wall\*) instead of selecting multiple catalog items individually.  

\- Ensure every assembly is \*\*deterministic and explicit\*\* — no inference, no conditional logic.  

\- Maintain full CE-safety, catalog integrity, and non-hallucination guarantees.  

\- Provide a clean foundation for future system expansion without changing estimator UX.



Assemblies/packs never introduce free-text rules, behaviour, or decision logic.



---



\# 2. Assembly Data Model (External → Internal)



Assemblies use a minimal, explicit schema:



```json

{

&nbsp; "id": "ASM001",

&nbsp; "name": "100mm Timber Stud Wall",

&nbsp; "components": \[

&nbsp;   {"catalog\_id": "A001", "multiplier": 1.0},

&nbsp;   {"catalog\_id": "A002", "multiplier": 0.4},

&nbsp;   {"catalog\_id": "A010", "multiplier": 8.0}

&nbsp; ]

}



