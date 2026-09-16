#!/usr/bin/env python3
"""Tests for NEURAXIS Escalation Engine - repetition_count behavior without SENTINEL registry."""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add mycelium to path
sys.path.insert(0, "/Users/Fujita/Documents/AI Filing System/decision-systems/00-kojiki-ontology/mycelium")

from engine.neuraxis import EscalationEngine, Experience, ErrorClass, Layer


def test_repetition_count_without_registry():
    """
    DECISION (2026-09-06): Fail-closed when no SENTINEL registry available.
    Without a verified identity registry, we cannot distinguish real
    corroboration from fabricated experiences. repetition_count=0 means
    an L3/L4 gate will NEVER open on unsigned evidence alone — this is
    intentional.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        engine = EscalationEngine(
            experience_log_path=str(tmp / "experiences.jsonl"),
            problem_store_path=str(tmp / "problems.json"),
            gate_request_path=str(tmp / "gate_requests.json"),
            mycelium_propagator=None,  # No propagator = no registry
        )
        
        # Create 3 experiences with same problem_id and error class
        # (would normally trigger MODEL_REPRESENTATION_ERROR escalation to L3)
        exp1 = Experience(
            id="exp-001",
            problem_id="P-001",
            hypothesis="H1",
            agents=["agent-1"],
            action="A1",
            expected="success",
            observed="failure",
            error_classification="Model/representation error",
            escalation={"target_layer": "L3_ontology"},
        )
        exp2 = Experience(
            id="exp-002",
            problem_id="P-001",
            hypothesis="H2",
            agents=["agent-1"],
            action="A2",
            expected="success",
            observed="failure",
            error_classification="Model/representation error",
            escalation={"target_layer": "L3_ontology"},
        )
        exp3 = Experience(
            id="exp-003",
            problem_id="P-001",
            hypothesis="H3",
            agents=["agent-1"],
            action="A3",
            expected="success",
            observed="failure",
            error_classification="Model/representation error",
            escalation={"target_layer": "L3_ontology"},
        )
        
        # Add to engine's experiences (simulating loaded history)
        engine.experiences = [exp1, exp2, exp3]
        
        # Create a new experience that would escalate to L3
        new_exp = Experience(
            id="exp-004",
            problem_id="P-001",
            hypothesis="H4",
            agents=["agent-1"],
            action="A4",
            expected="success",
            observed="failure",
            error_classification="Model/representation error",
            escalation={"target_layer": "L3_ontology"},
        )
        
        result = engine.escalate(new_exp)
        
        # Verify: gate request created but repetition_count = 0 (fail-closed)
        assert "gate_request_id" in result, "Gate request should be created for L3"
        gate_id = result["gate_request_id"]
        assert gate_id is not None, "Gate ID should not be None"
        
        gate = engine.gate_requests[gate_id]
        assert gate.evidence["repetition_count"] == 0, \
            f"Expected repetition_count=0 without registry, got {gate.evidence['repetition_count']}"
        
        print("✅ test_repetition_count_without_registry PASSED")
        print(f"   Gate created: {gate_id}")
        print(f"   repetition_count: {gate.evidence['repetition_count']} (fail-closed)")
        return True


def test_repetition_count_with_registry():
    """Test that with a registry, repetition_count would be >0 (mock test)."""
    # This is a placeholder - real test would need a mock registry
    # The key point: the fail-closed behavior is explicit and tested above
    print("ℹ️  test_repetition_count_with_registry: SKIPPED (requires SENTINEL registry mock)")
    return True


def main():
    print("=" * 60)
    print("NEURAXIS Escalation Engine - repetition_count tests")
    print("=" * 60)
    
    test_repetition_count_without_registry()
    test_repetition_count_with_registry()
    
    print("=" * 60)
    print("All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())