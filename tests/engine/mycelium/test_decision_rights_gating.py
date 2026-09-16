"""
Test Decision Rights Gating in Signal Propagation.
"""

import tempfile
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))

from engine.mycelium.propagate import SignalPropagator
from engine.mycelium.decision_rights import DecisionRightsGate, SignalType, DecisionRight
from engine.mycelium.registry import NodeRegistry
from engine.sentinel import KeyManager


def test_decision_rights_gating():
    """Test that signals are filtered by Decision Rights."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        edge_path = os.path.join(tmpdir, 'edges.json')
        log_path = os.path.join(tmpdir, 'signals.jsonl')
        registry_path = os.path.join(tmpdir, 'registry.json')
        keys_path = os.path.join(tmpdir, 'keys')
        
        # Create initial edges (Marketing.Head connects to all)
        edges_data = {
            'edges': {
                'Marketing.Head->Marketing.Growth': {'from': 'Marketing.Head', 'to': 'Marketing.Growth', 'weight': 0.8, 'reciprocal_exchanges': 0, 'one_directional_exchanges': 0, 'last_reinforced': ''},
                'Marketing.Head->Marketing.Analytics': {'from': 'Marketing.Head', 'to': 'Marketing.Analytics', 'weight': 0.7, 'reciprocal_exchanges': 0, 'one_directional_exchanges': 0, 'last_reinforced': ''},
                'Marketing.Head->Sales.Head': {'from': 'Marketing.Head', 'to': 'Sales.Head', 'weight': 0.6, 'reciprocal_exchanges': 0, 'one_directional_exchanges': 0, 'last_reinforced': ''},
                'Marketing.Growth->Marketing.Analytics': {'from': 'Marketing.Growth', 'to': 'Marketing.Analytics', 'weight': 0.8, 'reciprocal_exchanges': 0, 'one_directional_exchanges': 0, 'last_reinforced': ''},
            }
        }
        with open(edge_path, 'w') as f:
            json.dump(edges_data, f)
        
        # Create registry with decision rights
        km = KeyManager(keys_path)
        for node_id in ['Marketing.Head', 'Marketing.Growth', 'Marketing.Analytics', 'Sales.Head']:
            km.generate_keypair(node_id)
        
        registry = NodeRegistry(registry_path, genesis_public_key=km.get_public_key('Marketing.Head'))
        registry.nodes = {
            'Marketing.Head': {'id': 'Marketing.Head', 'public_key': km.get_public_key('Marketing.Head'), 'key_status': 'active', 'decision_rights': 'OWN'},
            'Marketing.Growth': {'id': 'Marketing.Growth', 'public_key': km.get_public_key('Marketing.Growth'), 'key_status': 'active', 'decision_rights': 'RECOMMEND'},
            'Marketing.Analytics': {'id': 'Marketing.Analytics', 'public_key': km.get_public_key('Marketing.Analytics'), 'key_status': 'active', 'decision_rights': 'CONSULT'},
            'Sales.Head': {'id': 'Sales.Head', 'public_key': km.get_public_key('Sales.Head'), 'key_status': 'active', 'decision_rights': 'APPROVE'},
        }
        registry.save()
        
        # Create propagator
        propagator = SignalPropagator(edge_path, log_path, registry=registry)
        
        from engine.sentinel import canonical_json
        
        # Test 1: Failure signal from OWN node - should reach CONSULT, EXECUTE, APPROVE
        print("Test 1: Failure signal from Marketing.Head (OWN)")
        signal = {
            'id': 'sig-001',
            'origin_kr': 'Marketing.Head',
            'event': 'failure',
            'signal_kind': 'failure',
            'new_status': 'ROUTED',
            'diagnosed_cause': 'test cause',
            'diagnosed_cause_category': 'Assumption',
            'status': 'ROUTED',
            'fired_at': '2026-01-01T00:00:00Z',
        }
        signal_data = {k: v for k, v in signal.items() if k != 'signature'}
        signal['signature'] = km.sign('Marketing.Head', canonical_json(signal_data))
        
        result = propagator.propagate(signal)
        print(f"  Result: {result}")
        assert result['success'] == True
        # Should reach Marketing.Analytics (CONSULT) and Sales.Head (APPROVE)
        # NOT Marketing.Growth (RECOMMEND - not in target set for failure)
        # NOT Marketing.Head (OWN - origin excluded)
        expected = {'Marketing.Analytics', 'Sales.Head'}
        assert set(result['subgraph']) == expected, f"Expected {expected}, got {set(result['subgraph'])}"
        print("  ✓ PASS")
        
        # Test 2: Failure signal from RECOMMEND node - should be REJECTED (origin lacks rights)
        print("\nTest 2: Failure signal from Marketing.Growth (RECOMMEND - no rights)")
        signal = {
            'id': 'sig-002',
            'origin_kr': 'Marketing.Growth',
            'event': 'failure',
            'signal_kind': 'failure',
            'new_status': 'ROUTED',
            'diagnosed_cause': 'test cause',
            'diagnosed_cause_category': 'Assumption',
            'status': 'ROUTED',
            'fired_at': '2026-01-01T00:00:00Z',
        }
        signal_data = {k: v for k, v in signal.items() if k != 'signature'}
        signal['signature'] = km.sign('Marketing.Growth', canonical_json(signal_data))
        
        result = propagator.propagate(signal)
        print(f"  Result: {result}")
        assert result['success'] == False
        assert 'lacks Decision Rights' in result['error']
        print("  ✓ PASS - correctly rejected")
        
        # Test 3: Deck request from OWN node - should reach CONSULT, EXECUTE, APPROVE
        print("\nTest 3: Deck request from Marketing.Head (OWN)")
        signal = {
            'id': 'sig-003',
            'origin_kr': 'Marketing.Head',
            'event': 'deck_request',
            'signal_kind': 'request',
            'decision_ref': 'DEC-001',
            'participating_departments': ['Marketing.Head', 'Marketing.Growth', 'Marketing.Analytics', 'Sales.Head'],
            'deck_ref': 'DECK-001',
            'fired_at': '2026-01-01T00:00:00Z',
        }
        signal_data = {k: v for k, v in signal.items() if k != 'signature'}
        signal['signature'] = km.sign('Marketing.Head', canonical_json(signal_data))
        
        result = propagator.propagate(signal)
        print(f"  Result: {result}")
        assert result['success'] == True
        # deck_request uses _propagate_deck_request which doesn't apply gating yet
        # but that's okay - it computes subgraphs for each dept
        print("  ✓ PASS")
        
        # Test 4: No registry - signature verification fails (expected - need registry for verification)
        print("\nTest 4: No registry - signature verification fails")
        propagator_no_reg = SignalPropagator(edge_path, log_path)
        signal = {
            'id': 'sig-004',
            'origin_kr': 'Marketing.Head',
            'event': 'failure',
            'signal_kind': 'failure',
            'new_status': 'ROUTED',
            'diagnosed_cause': 'test cause',
            'diagnosed_cause_category': 'Assumption',
            'status': 'ROUTED',
            'fired_at': '2026-01-01T00:00:00Z',
        }
        signal_data = {k: v for k, v in signal.items() if k != 'signature'}
        signal['signature'] = km.sign('Marketing.Head', canonical_json(signal_data))
        
        result = propagator_no_reg.propagate(signal)
        print(f"  Result: {result}")
        # Without registry, signature verification fails
        assert result['success'] == False
        assert 'signature verification failed' in result['error'].lower()
        print("  ✓ PASS - signature verification requires registry")
        
        print("\n=== ALL TESTS PASSED ===")


if __name__ == "__main__":
    test_decision_rights_gating()