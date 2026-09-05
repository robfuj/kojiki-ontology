"""
Tests for MYCELIUM Reinforcement.
"""

import json
import tempfile
import os
from mycelium.engine.reinforcement import ReinforcementEngine, reinforce, clamp


def test_clamp():
    """Test clamp function."""
    assert clamp(0.5, 0.0, 1.0) == 0.5
    assert clamp(-0.5, 0.0, 1.0) == 0.0
    assert clamp(1.5, 0.0, 1.0) == 1.0


def test_reinforce_formula():
    """Test the reinforcement formula matches Tero et al."""
    edge = {
        'weight': 0.5,
        'reciprocal_exchanges': 0,
        'one_directional_exchanges': 0
    }
    
    # Full delivery (flow_signal=1.0)
    updated = reinforce(edge, flow_signal=1.0, gamma=1.15, decay_rate=0.08, reinforcement_rate=0.35)
    
    # weight = 0.5 * (1 - 0.08) + 0.35 * (1.0 ** 1.15)
    # weight = 0.5 * 0.92 + 0.35 * 1.0
    # weight = 0.46 + 0.35 = 0.81
    expected = 0.5 * 0.92 + 0.35 * 1.0
    assert abs(updated['weight'] - expected) < 0.001
    assert updated['weight'] <= 1.0
    
    # No delivery (flow_signal=0.0)
    updated = reinforce(edge, flow_signal=0.0, gamma=1.15, decay_rate=0.08, reinforcement_rate=0.35)
    # weight = 0.5 * 0.92 + 0.35 * 0 = 0.46
    expected = 0.5 * 0.92
    assert abs(updated['weight'] - expected) < 0.001


def test_reinforcement_engine():
    """Test reinforcement engine operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "reinforcement.json")
        engine = ReinforcementEngine(store_path, gamma=1.15, decay_rate=0.08, reinforcement_rate=0.35)
        
        # Add edge
        engine.edges["kr-01->kr-02"] = {
            'from': 'kr-01',
            'to': 'kr-02',
            'weight': 0.5,
            'reciprocal_exchanges': 0,
            'one_directional_exchanges': 0,
            'last_reinforced': '2026-01-01T00:00:00Z'
        }
        engine.save()
        
        # Reinforce with full delivery
        result = engine.reinforce_edge("kr-01", "kr-02", 1.0)
        assert result is not None
        assert result['weight'] > 0.5
        
        # Reinforce with no delivery (decay)
        result = engine.reinforce_edge("kr-01", "kr-02", 0.0)
        assert result is not None
        assert result['weight'] < 0.81  # Should decay from previous


def test_gamma_efficiency_vs_redundancy():
    """Test that gamma controls efficiency vs redundancy tradeoff."""
    edge = {'weight': 0.5, 'reciprocal_exchanges': 0, 'one_directional_exchanges': 0}
    
    # High gamma (efficiency) - sparser networks
    high_gamma = reinforce(edge.copy(), flow_signal=0.5, gamma=2.0, decay_rate=0.0, reinforcement_rate=1.0)
    
    # Low gamma (redundancy) - more redundant networks
    low_gamma = reinforce(edge.copy(), flow_signal=0.5, gamma=0.5, decay_rate=0.0, reinforcement_rate=1.0)
    
    # With flow_signal < 1, higher gamma should produce lower reinforcement
    # (since 0.5^2.0 = 0.25 vs 0.5^0.5 = 0.707)
    assert high_gamma['weight'] < low_gamma['weight']


if __name__ == "__main__":
    test_clamp()
    test_reinforce_formula()
    test_reinforcement_engine()
    test_gamma_efficiency_vs_redundancy()
    print("All reinforcement tests passed!")