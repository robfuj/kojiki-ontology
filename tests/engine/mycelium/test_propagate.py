"""
Tests for MYCELIUM Propagate.
"""

import json
import tempfile
import os
from engine.mycelium.propagate import SignalPropagator, SUBGRAPH_THRESHOLD


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
        registry_path = os.path.join(tmpdir, "nodes.json")
        
        # Create edge store with test data
        edge_data = {
            "edges": {
                "Marketing->kr-02": {
                    "from": "Marketing", "to": "kr-02", "weight": 0.5,
                    "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
                    "trigger": "", "required_data": "", "acceptance_criteria": "",
                    "sla": "", "exception_path": ""
                }
            }
        }
        with open(edge_store_path, 'w') as f:
            json.dump(edge_data, f)
        
        # Create registry with genesis key
        from engine.sentinel import KeyManager, canonical_json
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        _, genesis_pub = key_manager.generate_keypair("genesis")
        
        from engine.mycelium.registry import NodeRegistry
        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        # Generate keypair for Marketing
        marketing_priv, marketing_pub = key_manager.generate_keypair("Marketing")
        kr2_priv, kr2_pub = key_manager.generate_keypair("kr-02")
        
        # Register Marketing with OWN decision right (required for failure signals)
        registry.nodes['Marketing'] = {
            'id': 'Marketing', 'public_key': marketing_pub, 'key_status': 'active',
            'key_issued_at': '2026-01-01T00:00:00Z', 'key_revoked_at': None, 'parent': None,
            'decision_rights': {'own': 'OWN', 'consult': [], 'inform': []}
        }
        registry.nodes['Marketing']['decision_right'] = 'OWN'
        # Also register kr-02 as a CONSULT node so it passes filter_recipients
        registry.nodes['kr-02'] = {
            'id': 'kr-02', 'public_key': kr2_pub, 'key_status': 'active',
            'key_issued_at': '2026-01-01T00:00:00Z', 'key_revoked_at': None, 'parent': 'Marketing',
            'decision_rights': {'own': 'CONSULT', 'consult': [], 'inform': []}
        }
        registry.nodes['kr-02']['decision_right'] = 'CONSULT'
        registry.save()
        
        # "Marketing" is a root department - already has keypair from registry init
        # Just use it directly
        
        # Pass the registry object directly (not just path) so it uses the same KeyManager
        propagator = SignalPropagator(edge_store_path, log_path, registry=registry)
        
        signal = {
            "id": "sig-001",
            "origin_kr": "Marketing",
            "event": "status_change",
            "new_status": "off_track",
            "diagnosed_cause": "test cause",
            "diagnosed_cause_category": "Cause",
            "status": "ROUTED",
            "fired_at": "2026-01-01T00:00:00Z",
            "signal_kind": "failure"
        }
        
        # Sign the signal using Marketing's private key
        signal_to_sign = {k: v for k, v in signal.items() if k not in ('signature', 'subgraph')}
        signal['signature'] = key_manager.sign("Marketing", canonical_json(signal_to_sign))
        
        result = propagator.propagate(signal)
        assert result['success']
        # Subgraph contains target nodes that pass Decision Rights filter
        # Marketing (origin, OWN) is filtered out by target filter for failure signals
        # kr-02 (target, CONSULT) passes the filter
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
        registry_path = os.path.join(tmpdir, "nodes.json")
        
        with open(edge_store_path, 'w') as f:
            json.dump({"edges": {
                "Marketing->kr-02": {
                    "from": "Marketing", "to": "kr-02", "weight": 0.5,
                    "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
                    "trigger": "", "required_data": "", "acceptance_criteria": "",
                    "sla": "", "exception_path": ""
                }
            }}, f)
        
        # Create registry with genesis key
        from engine.sentinel import KeyManager, canonical_json
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        _, genesis_pub = key_manager.generate_keypair("genesis")
        
        from engine.mycelium.registry import NodeRegistry

        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        # Generate keypair for Marketing
        marketing_priv, marketing_pub = key_manager.generate_keypair("Marketing")
        kr2_priv, kr2_pub = key_manager.generate_keypair("kr-02")
        
        # Register Marketing with OWN decision right (required for failure signals)
        registry.nodes['Marketing'] = {
            'id': 'Marketing', 'public_key': marketing_pub, 'key_status': 'active',
            'key_issued_at': '2026-01-01T00:00:00Z', 'key_revoked_at': None, 'parent': None,
            'decision_rights': {'own': 'OWN', 'consult': [], 'inform': []}
        }
        registry.nodes['Marketing']['decision_right'] = 'OWN'
        # Also register kr-02 as a CONSULT node so it passes filter_recipients
        registry.nodes['kr-02'] = {
            'id': 'kr-02', 'public_key': kr2_pub, 'key_status': 'active',
            'key_issued_at': '2026-01-01T00:00:00Z', 'key_revoked_at': None, 'parent': 'Marketing',
            'decision_rights': {'own': 'CONSULT', 'consult': [], 'inform': []}
        }
        registry.nodes['kr-02']['decision_right'] = 'CONSULT'
        
        # "Marketing" is a root department - already has keypair from registry init
        # Just use it directly
        
        # Pass the registry object directly (not just path) so it uses the same KeyManager
        propagator = SignalPropagator(edge_store_path, log_path, registry=registry)
        
        # Fire multiple signals
        for i in range(3):
            signal = {
                "id": f"sig-{i:03d}",
                "origin_kr": "Marketing",
                "event": "status_change",
                "new_status": "off_track",
                "diagnosed_cause": f"cause {i}",
                "diagnosed_cause_category": "Cause",
                "status": "ROUTED",
                "fired_at": "2026-01-01T00:00:00Z",
                "signal_kind": "failure"
            }
            signal_to_sign = {k: v for k, v in signal.items() if k not in ('signature', 'subgraph')}
            signal['signature'] = key_manager.sign("Marketing", canonical_json(signal_to_sign))
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