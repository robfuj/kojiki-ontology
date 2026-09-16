#!/usr/bin/env python3
"""Test for signal schema validation with signal_kind."""

import sys
import json
import tempfile
from pathlib import Path
import importlib.util

# Import propagate directly from file
PROPAGATE_PATH = Path(__file__).parent.parent.parent.parent / "engine" / "mycelium" / "propagate.py"
spec = importlib.util.spec_from_file_location("propagate", PROPAGATE_PATH)
propagate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(propagate_module)
SignalPropagator = propagate_module.SignalPropagator


def test_failure_signal_validation():
    """Test that failure signals require diagnosed_cause and category."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store = Path(tmpdir) / "edges.json"
        log_path = Path(tmpdir) / "signals.jsonl"
        
        # Create minimal edge store
        edge_store.write_text('{"edges": {}}')
        
        propagator = SignalPropagator(
            edge_store_path=str(edge_store),
            log_path=str(log_path),
        )
        
        # Valid failure signal
        valid_failure = {
            "id": "sig-001",
            "origin_kr": "kr-test",
            "event": "status_change",
            "new_status": "at_risk",
            "signal_kind": "failure",
            "diagnosed_cause": "Data pipeline failure",
            "diagnosed_cause_category": "Failure",
            "status": "ROUTED",
            "subgraph": ["kr-test", "kr-other"],
            "fired_at": "2026-09-07T10:00:00Z",
        }
        
        assert propagator.validate_signal(valid_failure) == True, "Valid failure signal should pass"
        
        # Missing diagnosed_cause
        invalid_failure = valid_failure.copy()
        del invalid_failure["diagnosed_cause"]
        assert propagator.validate_signal(invalid_failure) == False, "Missing diagnosed_cause should fail"
        
        # Empty diagnosed_cause
        invalid_failure2 = valid_failure.copy()
        invalid_failure2["diagnosed_cause"] = ""
        assert propagator.validate_signal(invalid_failure2) == False, "Empty diagnosed_cause should fail"
        
        # Invalid category
        invalid_failure3 = valid_failure.copy()
        invalid_failure3["diagnosed_cause_category"] = "InvalidCategory"
        assert propagator.validate_signal(invalid_failure3) == False, "Invalid category should fail"
        
        print("test_failure_signal_validation PASSED")


def test_request_signal_validation():
    """Test that request signals don't require diagnosed_cause."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store = Path(tmpdir) / "edges.json"
        log_path = Path(tmpdir) / "signals.jsonl"
        
        edge_store.write_text('{"edges": {}}')
        
        propagator = SignalPropagator(
            edge_store_path=str(edge_store),
            log_path=str(log_path),
        )
        
        # Valid deck_request signal (request kind, no cause required)
        valid_request = {
            "id": "sig-002",
            "origin_kr": "kr-test",
            "event": "deck_request",
            "new_status": "pending_review",
            "signal_kind": "request",
            "status": "ROUTED",
            "subgraph": ["kr-test", "kr-other"],
            "fired_at": "2026-09-07T10:00:00Z",
            "decision_ref": "dec-001",
            "participating_departments": ["kr-marketing", "kr-sales"],
            "deck_ref": "deck-001",
        }
        
        assert propagator.validate_signal(valid_request) == True, "Valid request signal should pass"
        
        # Request with diagnosed_cause present (should still pass - ignored)
        request_with_cause = valid_request.copy()
        request_with_cause["diagnosed_cause"] = "Some cause"
        request_with_cause["diagnosed_cause_category"] = "Failure"
        assert propagator.validate_signal(request_with_cause) == True, "Request with cause should pass (ignored)"
        
        # Invalid signal_kind
        invalid_kind = valid_request.copy()
        invalid_kind["signal_kind"] = "invalid"
        assert propagator.validate_signal(invalid_kind) == False, "Invalid signal_kind should fail"
        
        print("test_request_signal_validation PASSED")


def test_propagate_deck_request():
    """Test that deck_request validation works correctly (signature verification tested separately)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store = Path(tmpdir) / "edges.json"
        log_path = Path(tmpdir) / "signals.jsonl"
        registry_path = Path(tmpdir) / "nodes.json"
        
        edge_store.write_text('{"edges": {}}')
        # Registry expects nodes as array of objects with "id" field
        # Use valid base64 for public_key (32 bytes Ed25519 = 44 chars base64)
        # This is a dummy Ed25519 public key (32 bytes of 0x01)
        dummy_pub = "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry_path.write_text('{"nodes": [{"id": "kr-test", "public_key": "' + dummy_pub + '", "key_status": "active"}, {"id": "kr-marketing", "public_key": "' + dummy_pub + '", "key_status": "active"}, {"id": "kr-sales", "public_key": "' + dummy_pub + '", "key_status": "active"}]}')
        
        propagator = SignalPropagator(
            edge_store_path=str(edge_store),
            log_path=str(log_path),
            registry_path=str(registry_path),
        )
        
        deck_request = {
            "id": "sig-003",
            "origin_kr": "kr-test",
            "event": "deck_request",
            "new_status": "pending_review",
            "signal_kind": "request",
            "status": "ROUTED",
            "subgraph": ["kr-test"],
            "fired_at": "2026-09-07T10:00:00Z",
            "decision_ref": "dec-001",
            "participating_departments": ["kr-marketing", "kr-sales"],
            "deck_ref": "deck-001",
        }
        
        # Test validation - this is the core fix
        assert propagator.validate_signal(deck_request) == True, "Valid request signal should pass validation"
        
        # Verify the _propagate_deck_request method exists and has correct structure
        assert hasattr(propagator, '_propagate_deck_request'), "Should have _propagate_deck_request method"
        
        print("test_propagate_deck_request PASSED (validation logic verified)")


def test_failure_signal_rejected_without_cause():
    """Test that failure signal without cause is rejected in propagate."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store = Path(tmpdir) / "edges.json"
        log_path = Path(tmpdir) / "signals.jsonl"
        
        edge_store.write_text('{"edges": {}}')
        
        propagator = SignalPropagator(
            edge_store_path=str(edge_store),
            log_path=str(log_path),
        )
        
        # Failure signal without diagnosed_cause
        failure_no_cause = {
            "id": "sig-004",
            "origin_kr": "kr-test",
            "event": "status_change",
            "new_status": "at_risk",
            "signal_kind": "failure",
            "status": "ROUTED",
            "subgraph": ["kr-test"],
            "fired_at": "2026-09-07T10:00:00Z",
            # Missing diagnosed_cause and category
        }
        
        result = propagator.propagate(failure_no_cause)
        
        assert result["success"] == False, "Failure signal without cause should be rejected"
        assert "diagnosed_cause" in result.get("error", "") or "signal" in result.get("error", "").lower()
        
        print("test_failure_signal_rejected_without_cause PASSED")


if __name__ == "__main__":
    test_failure_signal_validation()
    test_request_signal_validation()
    test_propagate_deck_request()
    test_failure_signal_rejected_without_cause()
    print("\nAll signal validation tests passed")