Option Selection Contract v2

AI-Recommended Default Selection with System-Derived Confidence, Immutable Memory Context, and Intent-Bound Comparability

0. Purpose

Enable AI to lead option selection (choose a default) while ensuring:

No AI control over commitment or truth

Deterministic auditability

Transferability across agents and time

1. Scope

This contract applies only when:

There are 2+ candidate options addressing the same problem

An option is a structured artefact (e.g., build-up, approach, variant) that can be uniquely identified

This contract does not apply to:

Pricing finalisation

Library mutation (core or extension)

Schema changes

Merge/commit operations

Validation outcomes

2. Preconditions (Hard Gates)

AI may select a default only if all gates pass:

2.1 Validity Gate

Each option must:

be structurally complete for its type

contain no schema violations

contain no unresolved missing-item blocks that prevent evaluation

If any option fails → it may remain in the candidate set only if explicitly marked invalid_reason and excluded from selection.

2.2 Comparability Gate (Intent-Bound)

All selectable options must share the same:

functional_intent_id

Options may differ structurally (repair vs replace) only if they share the same intent.

If functional_intent_id is missing or inconsistent → AI must pause and request/obtain it (no default selection permitted).

2.3 Reversibility Gate

Selection must be reversible:

no writes to authoritative truth

no commits

no irreversible side effects

2.4 Veto Gate

Validator (or an equivalent gatekeeper) must be available to accept/reject the selection outcome.

3. Allowed Inputs

AI may use:

User instructions and constraints

CE context and references

Option metadata (completeness, provenance, assumptions)

Learning Memory (if enabled) for ranking only

AI may not use:

hidden knowledge

invented references

non-declared external sources

4. Learning Memory Rules (Advisory, Frozen-in-Snapshot)

Learning Memory may influence:

ordering of options

selection of default recommendation

confidence calibration (indirectly via evidence density rules)

Learning Memory may not:

determine validity

override missing-item rules

mutate pricing or truth

suppress disclosure of alternatives

If Learning Memory is enabled, the system must record an immutable context identity:

memory_context_hash (system-derived)

optionally memory_context_version

5. Outputs (What AI Must Produce)

AI must output the following structure:

5.1 Intent Binding

functional_intent_id

optional functional_intent_label

5.2 Ranked Options

ranked_option_ids: ordered list of valid selectable options

each option must include:

option_id

provenance_refs (CE/library refs if applicable)

assumptions (explicit)

5.3 Default Recommendation

ai_recommended_option_id (must exist in ranked_option_ids)

alternatives_presented: true (must always be true when 2+ options exist)

5.4 Justification (Declarative Only)

AI must provide:

selection_criteria (short list)

evidence_refs (enumerable references only)

declared_confidence (low|medium|high) — AI-reported

reversibility: true

risks (optional but encouraged)

questions (if any remain)

No narrative reasoning. No chain-of-thought.

6. System-Derived Confidence (Non-Negotiable)

AI confidence is not trusted directly.

The system must compute:

evidence_count = count(valid evidence_refs)

effective_confidence (low|medium|high) — system-derived

Minimum calibration rules:

If evidence_count == 0 → effective_confidence = low

If evidence_count < 2 and declared_confidence == high → effective_confidence = low

If evidence_count < 2 → effective_confidence cannot exceed medium

Optional strengthening: if no CE reference exists in evidence_refs → cap at medium

This ensures “confident but wrong” cannot bypass safety.

7. Validator Decision (Veto and Outcomes)

Validator may:

ACCEPT: selection can proceed as the default recommendation

REJECT: default selection invalid; AI must revert to advisory ranking only

REQUEST_REVISION: AI must re-rank or re-frame with additional questions

Validator does not:

invent new options

silently pick a different option without recording the reason

8. Snapshot Requirements (Full Replayability)

Every selection event must be snapshotted with:

functional_intent_id

ranked_option_ids

ai_recommended_option_id

declared_confidence

evidence_count

effective_confidence

learning_memory_enabled

learning_influence_domains (if any)

memory_context_hash (if enabled)

validator_outcome (accept/reject/revise)

timestamp and run_id (or equivalent)

This makes the decision auditable and transferable across time.

9. Fail-Safe Behaviour

AI must not select a default if:

functional_intent_id is missing or inconsistent

effective_confidence == low and options are materially divergent

unresolved questions materially affect scope

In these cases AI must:

output ranked options (if possible)

ask targeted questions

defer default selection

10. Declared System Class

With this contract:

The system remains a regulated pipeline,
augmented with AI-led default recommendation under:

system-derived calibration,

immutable memory context,

and validator veto.

AI leads the suggestion, not the commit.