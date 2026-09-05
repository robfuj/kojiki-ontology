"""
Tests for MYCELIUM Propagate.
"""

import json
import tempfile
import os
from mycelium.engine.propagate import SignalPropagator, SUBGRAPH_THRESHOLD


def test_propagator_initialization():
    """Test propagator initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "signals.jsonl")
        
        # Create edge store with test data
        edge_data = {
            "edges": {
                "kr-01->kr-02": {
                    "from": "kr-01", "to": "kr-02", "weight": 0.5,
                    "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
                    "trigger": "", "required_data": "", "acceptance_criteria": "",
                    "sla": "", "exception_path": ""
                },
                "kr-02->kr-03": {
                    "from": "kr-02", "to": "kr-03", "weight": 0.8,
                    "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
                    "trigger": "", "required_data": "", "acceptance_criteria": "",
                    "sla": "", "exception_path": ""
                }
            }
        }
        with open(edge_store_path, 'w') as f:
            json.dump(edge_data, f)
        
        propagator = SignalPropagator(edge_store_path, log_path, threshold=0.15)
        
        # Test subgraph computation
        subgraph = propagator.compute_subgraph("kr-01")
        assert "kr-01" in subgraph
        assert "kr-02" in subgraph  # weight 0.5 > 0.15
        assert "kr-03" in subgraph  # reachable via kr-02 (weight 0.8 > 0.15)


def test_subgraph_threshold():
    """Test subgraph threshold limits reach."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "signals.jsonl")
        
        # Edge below threshold
        edge_data = {
            "edges": {
                "kr-01->kr-02": {
                    "from": "kr-01", "to": "kr-02", "weight": 0.1,  # Below 0.15
                    "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
                    "trigger": "", "required_data": "", "acceptance_criteria": "",
                    "sla": "", "exception_path": ""
                }
            }
        }
        with open(edge_store_path, 'w') as f:
            json.dump(edge_data, f)
        
        propagator = SignalPropagator(edge_store_path, log_path, threshold=0.15)
        subgraph = propagator.compute_subgraph("kr-01")
        
        assert "kr-01" in subgraph
        assert "kr-02" not in subgraph  # Weight below threshold


def test_signal_validation():
    """Test signal validation rejects empty diagnosed_cause."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "signals.jsonl")
        
        with open(edge_store_path, 'w') as f:
            json.dump({"edges": {}}, f)
        
        propagator = SignalPropagator(edge_store_path, log_path)
        
        # Signal with empty diagnosed_cause should be rejected
        signal = {
            "id": "sig-001",
            "origin_kr": "kr-01",
            "event": "status_change",
            "new_status": "off_track",
            "diagnosed_cause": "",  # Empty!
            "diagnosed_cause_category": "Cause",
            "status": "ROUTED",
            "subgraph": [],
            "fired_at": "2026-01-01T00:00:00Z"
        }
        
        result = propagator.propagate(signal)
        assert not result['success']
        assert "empty diagnosed_cause" in result['error']
        
        # Signal with invalid category should be rejected
        signal['diagnosed_cause'] = "test cause"
        signal['diagnosed_cause_category'] = "InvalidCategory"
        result = propagator.propagate(signal)
        assert not result['success']


def test_signal_propagation():
    """Test successful signal propagation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "signals.jsonl")
        
        edge_data = {
            "edges": {
                "kr-01->kr-02": {
                    "from": "kr-01", "to": "kr-02", "weight": 0.5,
                    "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
                    "trigger": "", "required_data": "", "acceptance_criteria": "",
                    "sla": "", "exception_path": ""
                }
            }
        }
        with open(edge_store_path, 'w') as f:
            json.dump(edge_data, f)
        
        propagator = SignalPropagator(edge_store_path, log_path)
        
        signal = {
            "id": "sig-001",
            "origin_kr": "kr-01",
            "event": "status_change",
            "new_status": "off_track",
            "diagnosed_cause": "test cause",
            "diagnosed_cause_category": "Cause",
            "status": "ROUTED",
            "subgraph": [],
            "fired_at": "2026-01-01T00:00:00Z"
        }
        
        result = propagator.propagate(signal)
        assert result['success']
        assert "kr-01" in result['subgraph']
        assert "kr-02" in result['subgraph']
        
        # Check signal was logged
        signals = propagator.get_signals()
        assert len(signals) == 1
        assert signals[0]['id'] == "sig-001"


def test_signal_log_append_only():
    """Test signal log is append-only."""
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "signals.jsonl")
        
        with open(edge_store_path, 'w') as f:
            json.dump({"edges": {}}, f)
        
        propagator = SignalPropagator(edge_store_path, log_path)
        
        # Fire multiple signals
        for i in range(3):
            signal = {
                "id": f"sig-{i:03d}",
                "origin_kr": "kr-01",
                "event": "status_change",
                "new_status": "off_track",
                "diagnosed_cause": f"cause {i}",
                "diagnosed_cause_category": "Cause",
                "status": "ROUTED",
                "subgraph": [],
                "fired_at": "2026-01-01T00:00:00Z"
            }
            propagator.propagate(signal)
        
        # Check all signals in log
        signals = propagator.get_signals()
        assert len(signals) == 3


if __name__ == "__main__":
    test_propagator_initialization()
    test_subgraph_threshold()
    test_signal_validation()
    test_signal_propagation()
    test_signal_log_append_only()
    print("All propagate tests passed!")