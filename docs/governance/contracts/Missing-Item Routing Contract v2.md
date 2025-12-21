Missing-Item Routing Contract v2

AI-Led State Selection with System-Enforced Evidence and Validator Veto

0. Purpose

Enable AI to select the appropriate missing-item state (A–E) for incomplete information, while ensuring:

no silent assumption filling

no bypass of validation

full replayable audit trail

safe escalation instead of false certainty

1. Scope

This contract applies when:

required information is missing, ambiguous, or insufficient for:

pricing,

validation,

or downstream commitment.

It does not apply to:

resolving the missing item,

inventing substitute values,

altering truth or extensions,

final pricing decisions.

Routing ≠ resolution.

2. Missing-Item State Model (Authoritative)

The system recognises the following exclusive states:

State	Meaning
A	Clarification required (hard block)
B	Assumption required (explicit, user-approved)
C	Provisional placeholder allowed (clearly flagged)
D	External dependency required (survey, third-party)
E	Escalation / out-of-scope (cannot proceed safely)

AI may select one state only per missing-item instance.

3. Preconditions (Hard Gates)

AI may route a missing item only if:

The missing element is explicitly identified
(field, reference, or dependency name)

The missing item is material to downstream behaviour
(pricing, validation, scope, or risk)

No authoritative value exists in:

CE context

core library

approved extensions

If an authoritative value exists → missing-item routing is forbidden.

4. Allowed Inputs

AI may consider:

CE context

User instructions and constraints

Option metadata

Learning Memory (pattern + outcome domains only)

AI may not:

invent values

infer hidden truth

resolve the missing item

5. Routing Authority Model
What AI Is Allowed to Do

AI must:

identify the missing item explicitly

select one missing-item state (A–E)

justify the routing declaratively

mark the item as unresolved

AI may:

recommend follow-up actions

propose clarification questions

suggest provisional structures (if state allows)

What AI Is NOT Allowed to Do

AI must never:

fill missing data implicitly

downgrade a hard block to proceed

route multiple states simultaneously

suppress the missing-item flag

allow pricing to proceed without permission

6. Justification Structure (Declarative Only)

For each routed missing item, AI must output:

missing_item_id (stable identifier)

missing_field_or_dependency

selected_state (A–E)

routing_criteria (short list)

evidence_refs (CE / library refs if any)

declared_confidence (low|medium|high)

reversibility: true

assumptions_made: none (must be explicit if non-none)

No narrative reasoning.
No inferred values.

7. System-Derived Routing Confidence

As with Option Selection, confidence is not trusted directly.

System computes:

evidence_count = count(valid evidence_refs)

effective_confidence (system-derived)

Minimum rules:

If evidence_count == 0 → effective_confidence = low

If declared_confidence == high and evidence_count < 2 → downgrade to low

States B and C require effective_confidence ≥ medium
Otherwise AI must escalate to A or E

This prevents unsafe “proceed anyway” routing.

8. Learning Memory Influence (Bounded)

Learning Memory may influence:

likelihood of selecting B vs C vs D

prioritisation of clarification questions

Learning Memory may not:

justify skipping A

permit pricing

override hard dependencies

If used, snapshot must record:

influence domains

memory_context_hash

9. Validator Role

Validator may:

ACCEPT routing

REJECT routing (AI must re-route)

UPGRADE routing severity (e.g., C → A or E)

Validator may not downgrade severity without explicit justification.

10. Snapshot Requirements

Each missing-item routing must be snapshotted with:

missing_item_id

selected_state

routing_criteria

declared_confidence

effective_confidence

learning_memory_enabled

learning_influence_domains

memory_context_hash (if enabled)

validator_outcome

timestamp / run_id

This ensures full auditability and transferability.

11. Fail-Safe Behaviour

AI must halt downstream progression if:

state A, D, or E is selected

Validator rejects routing

multiple critical missing items compound risk

In these cases:

AI may summarise blockers

AI must request clarification

AI must not select defaults or price

12. Declared System Class

With this contract:

Missing-item handling becomes AI-guided but system-controlled.

AI leads routing,
the system controls resolution and authority.