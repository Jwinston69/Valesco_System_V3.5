# Cortex v1.0 — Pure Interface Subsystem (Schemas Only)
#
# Cortex is intentionally inert.
# It defines contract I/O schemas (Pydantic models) and a thin facade that
# supports structural round-trips without any decision logic.

from __future__ import annotations

import math
from typing import Any, Dict, List, Type, TypeVar

from pydantic import BaseModel, Field

ACTIVE_AI_GUIDANCE_CONTRACT_VERSIONS = {
    "option_selection_contract": "v2",
    "missing_item_routing_contract": "v2",
    "variant_generation_contract": "v2",
}

LEARNING_MEMORY_ENABLED = False


class CortexContractViolation(ValueError):
    """Raised when Phase 2 contract enforcement rejects an illegal state."""


class DecisionMetadata(BaseModel):
    """Canonical decision metadata shared across Cortex contracts."""

    functional_intent_id: str
    declared_confidence: float
    evidence_count: int
    effective_confidence: float | None
    learning_memory_used: bool
    memory_context_hash: str | None


class Evidence(BaseModel):
    """Minimal, non-weighted evidence container."""

    reference_id: str
    source_type: str
    description: str | None


class CortexContractInput(BaseModel):
    """Base input envelope shared by all Cortex contracts."""

    contract_name: str
    contract_version: str
    decision_metadata: DecisionMetadata
    evidence: List[Evidence]


class CortexContractOutput(BaseModel):
    """Base output envelope shared by all Cortex contracts."""

    decision_metadata: DecisionMetadata
    evidence: List[Evidence]


# ---------------------------------------------------------------------------
# Contract: AI Guidance Contracts (schemas only)
# ---------------------------------------------------------------------------


class AIGuidanceContractInput(CortexContractInput):
    request: Dict[str, Any]


class AIGuidanceContractOutput(CortexContractOutput):
    echoed_input: AIGuidanceContractInput


# ---------------------------------------------------------------------------
# Contract: Option Selection (schemas only)
# ---------------------------------------------------------------------------


class OptionCandidate(BaseModel):
    option_id: str
    option_payload: Dict[str, Any]


class OptionSelectionInput(CortexContractInput):
    selection_context: Dict[str, Any]
    options: List[OptionCandidate]


class OptionSelectionOutput(CortexContractOutput):
    echoed_input: OptionSelectionInput
    ranked_option_ids: List[str] = Field(default_factory=list)
    selected_option_id: str | None = None
    rationale: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Contract: Missing-Item Routing (schemas only)
# ---------------------------------------------------------------------------


class MissingItemRoutingInput(CortexContractInput):
    routing_context: Dict[str, Any]
    missing_item: Dict[str, Any]


class MissingItemRoutingOutput(CortexContractOutput):
    echoed_input: MissingItemRoutingInput
    selected_state: str = ""
    rationale: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Contract: Variant Generation (schemas only)
# ---------------------------------------------------------------------------


class VariantGenerationInput(CortexContractInput):
    variant_context: Dict[str, Any]
    base_item: Dict[str, Any]


class VariantGenerationOutput(CortexContractOutput):
    echoed_input: VariantGenerationInput
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)


TContractInput = TypeVar("TContractInput", bound=CortexContractInput)
TContractOutput = TypeVar("TContractOutput", bound=CortexContractOutput)


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


class CortexFacade:
    """Thin facade for structural I/O handling.

    Phase 2 adds strict contract enforcement (no decision logic):
    - snapshot-bound contract name/version validation
    - evidence_count enforcement
    - illegal-state rejection
    - effective_confidence scaffolding (system-derived)
    """

    def _enforce_contract_binding(self, contract_name: str, contract_version: str) -> None:
        if not contract_name or not contract_name.strip():
            raise CortexContractViolation("contract_name must be a non-empty string")
        if not contract_version or not contract_version.strip():
            raise CortexContractViolation("contract_version must be a non-empty string")

        expected_version = ACTIVE_AI_GUIDANCE_CONTRACT_VERSIONS.get(contract_name)
        if expected_version is None:
            raise CortexContractViolation(
                f"illegal contract_name={contract_name!r}; allowed={sorted(ACTIVE_AI_GUIDANCE_CONTRACT_VERSIONS.keys())}"
            )
        if contract_version != expected_version:
            raise CortexContractViolation(
                f"illegal contract_version={contract_version!r} for contract_name={contract_name!r}; expected={expected_version!r}"
            )

    def _enforce_decision_metadata(self, meta: DecisionMetadata, evidence: List[Evidence]) -> DecisionMetadata:
        if not meta.functional_intent_id or not meta.functional_intent_id.strip():
            raise CortexContractViolation("functional_intent_id must be a non-empty string")

        if not math.isfinite(meta.declared_confidence) or not (0.0 <= meta.declared_confidence <= 1.0):
            raise CortexContractViolation("declared_confidence must be a finite float in [0.0, 1.0]")

        if meta.evidence_count < 0:
            raise CortexContractViolation("evidence_count must be >= 0")
        if meta.evidence_count != len(evidence):
            raise CortexContractViolation(
                f"evidence_count must equal len(evidence); evidence_count={meta.evidence_count} len(evidence)={len(evidence)}"
            )

        if not LEARNING_MEMORY_ENABLED:
            if meta.learning_memory_used:
                raise CortexContractViolation("learning_memory_used must be false when Learning Memory is disabled")
            if meta.memory_context_hash is not None:
                raise CortexContractViolation("memory_context_hash must be null when Learning Memory is disabled")
        else:
            if meta.learning_memory_used and (not meta.memory_context_hash or not meta.memory_context_hash.strip()):
                raise CortexContractViolation("memory_context_hash is required when learning_memory_used is true")
            if (not meta.learning_memory_used) and meta.memory_context_hash is not None:
                raise CortexContractViolation("memory_context_hash must be null when learning_memory_used is false")

        derived_effective = meta.declared_confidence
        if meta.effective_confidence is None:
            return meta.model_copy(update={"effective_confidence": derived_effective})

        if not math.isfinite(meta.effective_confidence) or not (0.0 <= meta.effective_confidence <= 1.0):
            raise CortexContractViolation("effective_confidence must be a finite float in [0.0, 1.0] or null")
        if meta.effective_confidence != derived_effective:
            raise CortexContractViolation(
                f"effective_confidence must match system-derived value; got={meta.effective_confidence} expected={derived_effective}"
            )
        return meta

    def enforce_contract_input(self, contract_input: TContractInput) -> TContractInput:
        """Return an enforced copy of the input (no mutation)."""

        self._enforce_contract_binding(contract_input.contract_name, contract_input.contract_version)
        enforced_meta = self._enforce_decision_metadata(contract_input.decision_metadata, contract_input.evidence)

        if enforced_meta == contract_input.decision_metadata:
            return contract_input
        return contract_input.model_copy(update={"decision_metadata": enforced_meta})

    def validate_contract_io(
        self,
        contract_input: TContractInput,
        contract_output: TContractOutput,
    ) -> tuple[TContractInput, TContractOutput]:
        enforced_input = self.enforce_contract_input(contract_input)

        if contract_output.decision_metadata != enforced_input.decision_metadata:
            raise CortexContractViolation("contract_output.decision_metadata must match enforced contract_input")
        if contract_output.evidence != enforced_input.evidence:
            raise CortexContractViolation("contract_output.evidence must match enforced contract_input")

        if hasattr(contract_output, "echoed_input") and contract_output.echoed_input != enforced_input:
            raise CortexContractViolation("contract_output.echoed_input must match enforced contract_input")

        return enforced_input, contract_output

    def round_trip(
        self,
        contract_input: TContractInput,
        output_model: Type[TContractOutput],
    ) -> TContractOutput:
        return output_model(
            decision_metadata=contract_input.decision_metadata,
            evidence=contract_input.evidence,
            echoed_input=contract_input,
        )

    def round_trip_enforced(
        self,
        contract_input: TContractInput,
        output_model: Type[TContractOutput],
    ) -> TContractOutput:
        enforced_input = self.enforce_contract_input(contract_input)
        enforced_output = self.round_trip(enforced_input, output_model)
        self.validate_contract_io(enforced_input, enforced_output)
        return enforced_output

    def deterministic_option_selection(self, contract_input: OptionSelectionInput) -> OptionSelectionOutput:
        enforced_input = self.enforce_contract_input(contract_input)

        rationale: List[str]
        ranked_option_ids: List[str]
        selected_option_id: str | None

        if not enforced_input.options:
            ranked_option_ids = []
            selected_option_id = None
            rationale = ["no options provided"]
        else:
            costs = [o.option_payload.get("estimated_total_cost") for o in enforced_input.options]
            if all(_is_finite_number(v) for v in costs):
                ranked = sorted(
                    enforced_input.options,
                    key=lambda o: (float(o.option_payload["estimated_total_cost"]), o.option_id),
                )
                ranked_option_ids = [o.option_id for o in ranked]
                selected_option_id = ranked_option_ids[0] if ranked_option_ids else None
                rationale = ["ranked by estimated_total_cost ascending"]
            else:
                durations = [o.option_payload.get("duration_days") for o in enforced_input.options]
                if all(_is_finite_number(v) for v in durations):
                    ranked = sorted(
                        enforced_input.options,
                        key=lambda o: (float(o.option_payload["duration_days"]), o.option_id),
                    )
                    ranked_option_ids = [o.option_id for o in ranked]
                    selected_option_id = ranked_option_ids[0] if ranked_option_ids else None
                    rationale = ["ranked by duration_days ascending"]
                else:
                    ranked = sorted(enforced_input.options, key=lambda o: o.option_id)
                    ranked_option_ids = [o.option_id for o in ranked]
                    selected_option_id = ranked_option_ids[0] if ranked_option_ids else None
                    rationale = ["ranked by option_id lexicographic fallback"]

        out = OptionSelectionOutput(
            decision_metadata=enforced_input.decision_metadata,
            evidence=enforced_input.evidence,
            echoed_input=enforced_input,
            ranked_option_ids=ranked_option_ids,
            selected_option_id=selected_option_id,
            rationale=rationale,
        )
        self.validate_contract_io(enforced_input, out)
        return out

    def deterministic_missing_item_routing(self, contract_input: MissingItemRoutingInput) -> MissingItemRoutingOutput:
        enforced_input = self.enforce_contract_input(contract_input)

        mi = enforced_input.missing_item

        state_hint = mi.get("state_hint")
        if isinstance(state_hint, str) and state_hint in {"A", "B", "C", "D", "E"}:
            selected_state = state_hint
            rationale = ["used state_hint"]
        else:
            severity = mi.get("severity")
            if severity in {"critical", "high"}:
                selected_state = "A"
                rationale = ["severity critical/high -> A"]
            elif severity in {"medium"}:
                selected_state = "C"
                rationale = ["severity medium -> C"]
            else:
                selected_state = "E"
                rationale = ["fallback -> E"]

        out = MissingItemRoutingOutput(
            decision_metadata=enforced_input.decision_metadata,
            evidence=enforced_input.evidence,
            echoed_input=enforced_input,
            selected_state=selected_state,
            rationale=rationale,
        )
        self.validate_contract_io(enforced_input, out)
        return out

    def deterministic_variant_generation(self, contract_input: VariantGenerationInput) -> VariantGenerationOutput:
        enforced_input = self.enforce_contract_input(contract_input)

        keys = enforced_input.variant_context.get("variant_keys")
        if isinstance(keys, list) and all(isinstance(k, str) for k in keys):
            variants = [{"variant_key": k, "base_item": enforced_input.base_item} for k in keys]
            rationale = ["enumerated variant_keys in order"]
        else:
            variants = [{"variant_key": "baseline", "base_item": enforced_input.base_item}]
            rationale = ["baseline variant only"]

        out = VariantGenerationOutput(
            decision_metadata=enforced_input.decision_metadata,
            evidence=enforced_input.evidence,
            echoed_input=enforced_input,
            variants=variants,
            rationale=rationale,
        )
        self.validate_contract_io(enforced_input, out)
        return out

    def execute_deterministic(
        self,
        contract_input: TContractInput,
        output_model: Type[TContractOutput],
    ) -> TContractOutput:
        if isinstance(contract_input, OptionSelectionInput):
            if output_model is not OptionSelectionOutput:
                raise CortexContractViolation("output_model mismatch for OptionSelectionInput")
            return self.deterministic_option_selection(contract_input)  # type: ignore[return-value]

        if isinstance(contract_input, MissingItemRoutingInput):
            if output_model is not MissingItemRoutingOutput:
                raise CortexContractViolation("output_model mismatch for MissingItemRoutingInput")
            return self.deterministic_missing_item_routing(contract_input)  # type: ignore[return-value]

        if isinstance(contract_input, VariantGenerationInput):
            if output_model is not VariantGenerationOutput:
                raise CortexContractViolation("output_model mismatch for VariantGenerationInput")
            return self.deterministic_variant_generation(contract_input)  # type: ignore[return-value]

        raise CortexContractViolation("unsupported contract_input for deterministic execution")
