import unittest

from engine.modules.cortex_v1_0 import (
    AIGuidanceContractInput,
    AIGuidanceContractOutput,
    CortexContractViolation,
    CortexFacade,
    DecisionMetadata,
    Evidence,
    MissingItemRoutingInput,
    MissingItemRoutingOutput,
    OptionCandidate,
    OptionSelectionInput,
    OptionSelectionOutput,
    VariantGenerationInput,
    VariantGenerationOutput,
)


class TestCortexV10(unittest.TestCase):
    def _meta_and_ev(self, *, declared_confidence: float = 0.0) -> tuple[DecisionMetadata, Evidence]:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=declared_confidence,
            evidence_count=1,
            effective_confidence=None,
            learning_memory_used=False,
            memory_context_hash=None,
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        return meta, ev

    def test_module_imports_cleanly(self) -> None:
        # Import is performed at module load; this test exists to satisfy the
        # explicit requirement and to remain explicit in the test report.
        self.assertTrue(True)

    def test_models_instantiate_and_round_trip(self) -> None:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=0.0,
            evidence_count=1,
            effective_confidence=None,
            learning_memory_used=False,
            memory_context_hash=None,
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        cortex = CortexFacade()

        ai_in = AIGuidanceContractInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            request={"k": "v"},
        )
        ai_out = cortex.round_trip(ai_in, AIGuidanceContractOutput)
        self.assertEqual(ai_out.echoed_input, ai_in)

        opt_in = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={"scope": "test"},
            options=[OptionCandidate(option_id="O1", option_payload={"id": 1})],
        )
        opt_out = cortex.round_trip(opt_in, OptionSelectionOutput)
        self.assertEqual(opt_out.echoed_input, opt_in)

        route_in = MissingItemRoutingInput(
            contract_name="missing_item_routing_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            routing_context={"scope": "test"},
            missing_item={"description": "missing"},
        )
        route_out = cortex.round_trip(route_in, MissingItemRoutingOutput)
        self.assertEqual(route_out.echoed_input, route_in)

        var_in = VariantGenerationInput(
            contract_name="variant_generation_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            variant_context={"scope": "test"},
            base_item={"id": "BASE"},
        )
        var_out = cortex.round_trip(var_in, VariantGenerationOutput)
        self.assertEqual(var_out.echoed_input, var_in)

        # Phase 1 stays inert: round-trip must not mutate inputs.
        before = ai_in.model_dump()
        _ = cortex.round_trip(ai_in, AIGuidanceContractOutput)
        after = ai_in.model_dump()
        self.assertEqual(before, after)

    def test_phase2_enforcement_round_trip_and_validate(self) -> None:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=0.25,
            evidence_count=1,
            effective_confidence=None,
            learning_memory_used=False,
            memory_context_hash=None,
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        cortex = CortexFacade()

        opt_in = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={"scope": "test"},
            options=[OptionCandidate(option_id="O1", option_payload={"id": 1})],
        )

        opt_out = cortex.round_trip_enforced(opt_in, OptionSelectionOutput)
        self.assertEqual(opt_out.echoed_input.decision_metadata.effective_confidence, 0.25)

        validated_in, validated_out = cortex.validate_contract_io(opt_out.echoed_input, opt_out)
        self.assertEqual(validated_in, opt_out.echoed_input)
        self.assertEqual(validated_out, opt_out)

        # No mutation / side effects: enforcement must not change original inputs.
        self.assertIsNone(opt_in.decision_metadata.effective_confidence)

    def test_phase2_rejects_unknown_contract(self) -> None:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=0.0,
            evidence_count=1,
            effective_confidence=None,
            learning_memory_used=False,
            memory_context_hash=None,
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        cortex = CortexFacade()

        bad_in = AIGuidanceContractInput(
            contract_name="unknown_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            request={},
        )
        bad_out = cortex.round_trip(bad_in, AIGuidanceContractOutput)

        with self.assertRaises(CortexContractViolation):
            cortex.validate_contract_io(bad_in, bad_out)

    def test_phase2_rejects_evidence_count_mismatch(self) -> None:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=0.0,
            evidence_count=2,
            effective_confidence=None,
            learning_memory_used=False,
            memory_context_hash=None,
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        cortex = CortexFacade()

        bad_in = AIGuidanceContractInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            request={},
        )
        bad_out = cortex.round_trip(bad_in, AIGuidanceContractOutput)

        with self.assertRaises(CortexContractViolation):
            cortex.validate_contract_io(bad_in, bad_out)

    def test_phase2_rejects_learning_memory_used_when_disabled(self) -> None:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=0.0,
            evidence_count=1,
            effective_confidence=None,
            learning_memory_used=True,
            memory_context_hash="HASH",
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        cortex = CortexFacade()

        bad_in = AIGuidanceContractInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            request={},
        )
        bad_out = cortex.round_trip(bad_in, AIGuidanceContractOutput)

        with self.assertRaises(CortexContractViolation):
            cortex.validate_contract_io(bad_in, bad_out)

    def test_phase2_rejects_effective_confidence_mismatch(self) -> None:
        meta = DecisionMetadata(
            functional_intent_id="TEST_INTENT",
            declared_confidence=0.5,
            evidence_count=1,
            effective_confidence=0.6,
            learning_memory_used=False,
            memory_context_hash=None,
        )

        ev = Evidence(
            reference_id="EVIDENCE_1",
            source_type="unit_test",
            description=None,
        )

        cortex = CortexFacade()

        bad_in = AIGuidanceContractInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            request={},
        )
        bad_out = cortex.round_trip(bad_in, AIGuidanceContractOutput)

        with self.assertRaises(CortexContractViolation):
            cortex.validate_contract_io(bad_in, bad_out)

    def test_phase3_option_selection_ranks_by_estimated_total_cost(self) -> None:
        meta, ev = self._meta_and_ev(declared_confidence=0.25)
        cortex = CortexFacade()

        inp = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={},
            options=[
                OptionCandidate(option_id="O1", option_payload={"estimated_total_cost": 10.0}),
                OptionCandidate(option_id="O2", option_payload={"estimated_total_cost": 5.0}),
            ],
        )

        out = cortex.deterministic_option_selection(inp)
        self.assertEqual(out.ranked_option_ids, ["O2", "O1"])
        self.assertEqual(out.selected_option_id, "O2")
        self.assertEqual(out.rationale, ["ranked by estimated_total_cost ascending"])

        # Deterministic + no mutation.
        self.assertIsNone(inp.decision_metadata.effective_confidence)

    def test_phase3_option_selection_falls_back_to_option_id_when_cost_not_uniform(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        inp = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={},
            options=[
                OptionCandidate(option_id="B", option_payload={"estimated_total_cost": 10.0}),
                OptionCandidate(option_id="A", option_payload={}),
            ],
        )

        out = cortex.deterministic_option_selection(inp)
        self.assertEqual(out.ranked_option_ids, ["A", "B"])
        self.assertEqual(out.selected_option_id, "A")
        self.assertEqual(out.rationale, ["ranked by option_id lexicographic fallback"])

    def test_phase3_option_selection_ranks_by_duration_days_when_available(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        inp = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={},
            options=[
                OptionCandidate(option_id="O1", option_payload={"duration_days": 5}),
                OptionCandidate(option_id="O2", option_payload={"duration_days": 2}),
            ],
        )

        out = cortex.deterministic_option_selection(inp)
        self.assertEqual(out.ranked_option_ids, ["O2", "O1"])
        self.assertEqual(out.selected_option_id, "O2")
        self.assertEqual(out.rationale, ["ranked by duration_days ascending"])

    def test_phase3_option_selection_empty_options(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        inp = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={},
            options=[],
        )

        out = cortex.deterministic_option_selection(inp)
        self.assertEqual(out.ranked_option_ids, [])
        self.assertIsNone(out.selected_option_id)
        self.assertEqual(out.rationale, ["no options provided"])

    def test_phase3_missing_item_routing_state_hint_respected(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        inp = MissingItemRoutingInput(
            contract_name="missing_item_routing_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            routing_context={},
            missing_item={"state_hint": "B"},
        )

        out = cortex.deterministic_missing_item_routing(inp)
        self.assertEqual(out.selected_state, "B")
        self.assertEqual(out.rationale, ["used state_hint"])

    def test_phase3_missing_item_routing_severity_mapping(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        inp = MissingItemRoutingInput(
            contract_name="missing_item_routing_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            routing_context={},
            missing_item={"severity": "high"},
        )

        out = cortex.deterministic_missing_item_routing(inp)
        self.assertEqual(out.selected_state, "A")
        self.assertEqual(out.rationale, ["severity critical/high -> A"])

    def test_phase3_missing_item_routing_medium_and_fallback(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        medium_in = MissingItemRoutingInput(
            contract_name="missing_item_routing_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            routing_context={},
            missing_item={"severity": "medium"},
        )
        medium_out = cortex.deterministic_missing_item_routing(medium_in)
        self.assertEqual(medium_out.selected_state, "C")
        self.assertEqual(medium_out.rationale, ["severity medium -> C"])

        fallback_in = MissingItemRoutingInput(
            contract_name="missing_item_routing_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            routing_context={},
            missing_item={"severity": "low"},
        )
        fallback_out = cortex.deterministic_missing_item_routing(fallback_in)
        self.assertEqual(fallback_out.selected_state, "E")
        self.assertEqual(fallback_out.rationale, ["fallback -> E"])

    def test_phase3_variant_generation_enumerates_variant_keys_in_order(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        base_item = {"id": "BASE"}
        inp = VariantGenerationInput(
            contract_name="variant_generation_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            variant_context={"variant_keys": ["k1", "k2"]},
            base_item=base_item,
        )

        out = cortex.deterministic_variant_generation(inp)
        self.assertEqual(
            out.variants,
            [
                {"variant_key": "k1", "base_item": base_item},
                {"variant_key": "k2", "base_item": base_item},
            ],
        )
        self.assertEqual(out.rationale, ["enumerated variant_keys in order"])

    def test_phase3_variant_generation_fallback_baseline(self) -> None:
        meta, ev = self._meta_and_ev()
        cortex = CortexFacade()

        base_item = {"id": "BASE"}
        inp = VariantGenerationInput(
            contract_name="variant_generation_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            variant_context={},
            base_item=base_item,
        )

        out = cortex.deterministic_variant_generation(inp)
        self.assertEqual(out.variants, [{"variant_key": "baseline", "base_item": base_item}])
        self.assertEqual(out.rationale, ["baseline variant only"])

    def test_phase3_determinism_same_input_same_output(self) -> None:
        meta, ev = self._meta_and_ev(declared_confidence=0.1)
        cortex = CortexFacade()

        inp = OptionSelectionInput(
            contract_name="option_selection_contract",
            contract_version="v2",
            decision_metadata=meta,
            evidence=[ev],
            selection_context={},
            options=[
                OptionCandidate(option_id="O2", option_payload={"estimated_total_cost": 2.0}),
                OptionCandidate(option_id="O1", option_payload={"estimated_total_cost": 1.0}),
            ],
        )

        out1 = cortex.deterministic_option_selection(inp)
        out2 = cortex.deterministic_option_selection(inp)
        self.assertEqual(out1.model_dump(), out2.model_dump())


if __name__ == "__main__":
    unittest.main()
