Variant & Sensitivity Generation Contract v2

AI-Led Exploration with Zero Authority over Commitment

0. Purpose

Enable AI to generate and rank estimate variants and sensitivities in order to:

expose risk,

surface cost drivers,

inform senior estimator judgement,

without:

altering the baseline,

committing prices,

or mutating truth.

1. Scope

This contract applies when:

a baseline option has been selected or proposed, and

uncertainty, assumptions, or cost drivers exist that materially affect outcomes.

It does not apply to:

baseline commitment,

pricing approval,

library updates,

missing-item resolution,

validation outcomes.

Variants inform decisions; they do not make them.

2. Preconditions (Hard Gates)

AI may generate variants only if:

A baseline artefact exists

baseline option ID is known

baseline assumptions are explicit

Variants are reversible

no truth mutation

no pricing commit

no downstream locking

Missing-item routing allows exploration

no unresolved A / D / E blocks

If these conditions fail → variant generation is forbidden.

3. Variant Types (Authoritative Enumeration)

AI may generate variants of the following types only:

Type	Description
Assumption Variant	Change in a declared assumption
Quantity Variant	Bounded range adjustment
Productivity Variant	Output rate sensitivity
Method Variant	Alternative method within same functional intent
Risk Allowance Variant	Explicit risk contingency toggle

AI may not generate:

new scopes,

alternative intents,

speculative “optimisations” not grounded in baseline intent.

4. Allowed Inputs

AI may consider:

Baseline artefact

Declared assumptions

CE context

Learning Memory (outcome + pattern domains only)

AI may not:

introduce new data

invent prices

reinterpret validation outcomes

5. Authority Model
What AI Is Allowed to Do

AI must:

enumerate variants explicitly

bind each variant to:
Structured changes only

identify the primary driver affected

rank variants by impact magnitude, not preference

AI may:

recommend which sensitivities matter most

flag fragile assumptions

suggest data that would collapse uncertainty

What AI Is NOT Allowed to Do

AI must never:

select a “better” baseline

mark a variant as preferred

collapse variants into a single number

hide the baseline

override missing-item blocks

6. Variant Structure (Declarative Only)

Each variant must include:

variant_id

variant_type (from §3)

baseline_option_id

changed_inputs (explicit fields only)

unchanged_inputs (optional, encouraged)

impact_dimension

cost | time | risk | scope

impact_direction

increase | decrease | mixed

impact_band

low | medium | high

assumptions

reversibility: true

No narrative reasoning.
No hidden deltas.

7. System-Derived Confidence & Impact Calibration

AI may declare:

declared_confidence (low|medium|high)

System must compute:

evidence_count

effective_confidence (same downgrade rules as v2 contracts)

Additionally:

Variants with effective_confidence == low must be flagged as illustrative only

Variants may not influence defaults or routing when confidence is low

8. Learning Memory Influence (Strictly Limited)

Learning Memory may influence:

which variant types are generated first

which drivers are highlighted as fragile

Learning Memory may not:

suppress variants

inflate impact bands

prioritise variants based on historical acceptance

All influence must be recorded with:

memory_context_hash

influence domains used

9. Validator Role

Validator may:

ACCEPT variant set

REJECT specific variants

REQUEST_REFINEMENT (narrow scope, clearer deltas)

Validator may not:

pick a preferred variant

convert a variant into a baseline

10. Snapshot Requirements

Each variant event must be snapshotted with:

baseline option ID

full variant list

variant types

impact bands

declared & effective confidence

learning_memory_enabled

learning_influence_domains

memory_context_hash (if enabled)

validator outcome

timestamp / run ID

This guarantees replayability and transfer.

11. Fail-Safe Behaviour

AI must halt variant generation if:

baseline is unstable

missing-item routing escalates

Validator rejects repeatedly

variants would imply scope change

In these cases AI must:

summarise uncertainty

recommend clarification

stop exploration

12. Declared System Class

With this contract:

Variants become a diagnostic instrument, not an optimisation engine.

AI leads exploration,
humans control decisions,
the system preserves truth and trust.