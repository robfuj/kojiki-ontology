#!/usr/bin/env python3
"""Test for repetition_count behavior without SENTINEL registry."""

import sys
import json
import tempfile
from pathlib import Path
import importlib.util

# Import escalation engine directly from file
ESCALATION_PATH = Path(__file__).parent.parent / "engine" / "escalation.py"
spec = importlib.util.spec_from_file_location("escalation", ESCALATION_PATH)
escalation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(escalation_module)
EscalationEngine = escalation_module.EscalationEngine
Experience = escalation_module.Experience
ErrorClass = escalation_module.ErrorClass


def test_repetition_count_without_registry():
    """
    Test that repetition_count returns 0 when no SENTINEL registry is available.
    
    This is the fail-closed behavior: without a verified identity registry,
    we cannot distinguish real corroboration from fabricated experiences.
    An L3/L4 gate will NEVER open on unsigned evidence alone.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        exp_log = Path(tmpdir) / "experiences.jsonl"
        prob_store = Path(tmpdir) / "problems.json"
        gate_req = Path(tmpdir) / "gate_requests.json"
        
        engine = EscalationEngine(
            experience_log_path=str(exp_log),
            problem_store_path=str(prob_store),
            gate_request_path=str(gate_req),
            mycelium_propagator=None,  # No propagator = no registry
        )
        
        # Add some experiences manually (unsigned)
        for i in range(5):
            exp = Experience(
                id=f"exp-{i:03d}",
                problem_id="P-0001",
                hypothesis="Test hypothesis",
                agents=["test-agent"],
                action="Test action",
                expected="Expected result",
                observed="Observed result",
                error_classification=ErrorClass.MODEL_REPRESENTATION_ERROR.value,
                escalation={},
            )
            engine.experiences.append(exp)
        
        engine.save_experiences()
        
        # Create a gate request - this should have repetition_count = 0
        # because there's no registry to verify experiences
        new_exp = Experience(
            id="exp-new",
            problem_id="P-0001",
            hypothesis="New hypothesis",
            agents=["test-agent"],
            action="New action",
            expected="Expected",
            observed="Observed",
            error_classification=ErrorClass.MODEL_REPRESENTATION_ERROR.value,
            escalation={},
        )
        
        result = engine.escalate(new_exp)
        
        # Verify gate request was created
        assert result["gate_request_id"] is not None, "Gate request should be created"
        
        gate = engine.gate_requests[result["gate_request_id"]]
        
        # CRITICAL ASSERTION: repetition_count must be 0 without registry
        assert gate.evidence["repetition_count"] == 0, \
            f"Expected repetition_count=0 without registry, got {gate.evidence['repetition_count']}"
        
        # Experience refs should include the new experience too (escalate adds it first)
        assert len(gate.evidence["experience_refs"]) == 6, \
            f"Expected 6 experience refs (5 original + 1 new), got {len(gate.evidence['experience_refs'])}"
        
        print("✅ test_repetition_count_without_registry PASSED")
        print(f"   Gate ID: {gate.id}")
        print(f"   Repetition count: {gate.evidence['repetition_count']}")
        print(f"   Experience refs: {gate.evidence['experience_refs']}")
        
        return True


if __name__ == "__main__":
    test_repetition_count_without_registry()
    # Skip mock test for now - core behavior verified
    print("\n✅ Core test passed (fail-closed behavior verified)")