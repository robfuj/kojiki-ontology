"""
Tests for MYCELIUM Prune.
"""

import json
import tempfile
import os
from mycelium.engine.prune import PruningEngine


def test_pruning_engine():
    """Test pruning engine operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "edges_history.jsonl")
        
        engine = PruningEngine(store_path, log_path, min_weight=0.05, reciprocity_floor=0.2)
        
        # Add test edges
        engine.edges["kr-01->kr-02"] = {
            "from": "kr-01", "to": "kr-02", "weight": 0.1,
            "reciprocal_exchanges": 5, "one_directional_exchanges": 0
        }
        engine.edges["kr-03->kr-04"] = {
            "from": "kr-03", "to": "kr-04", "weight": 0.8,
            "reciprocal_exchanges": 0, "one_directional_exchanges": 5  # No reciprocity
        }
        engine.edges["kr-05->kr-06"] = {
            "from": "kr-05", "to": "kr-06", "weight": 0.03,  # Below min_weight
            "reciprocal_exchanges": 3, "one_directional_exchanges": 1
        }
        engine.save()
        
        # Check statuses
        status1 = engine.get_edge_status("kr-01", "kr-02")
        assert status1['prune_decision'] == "keep"  # Good weight, good reciprocity
        
        status2 = engine.get_edge_status("kr-03", "kr-04")
        assert status2['prune_decision'] == "prune"  # Good weight, bad reciprocity
        
        status3 = engine.get_edge_status("kr-05", "kr-06")
        assert status3['prune_decision'] == "prune"  # Below min_weight
        
        # Prune
        pruned = engine.prune_edges()
        assert len(pruned) == 2  # kr-03->kr-04 and kr-05->kr-06
        
        # Check remaining
        remaining = engine.get_all_edges()
        assert len(remaining) == 1
        assert remaining[0]['from'] == "kr-01"
        assert remaining[0]['to'] == "kr-02"
        
        # Check log was written
        assert os.path.exists(log_path)
        with open(log_path, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 2  # Two pruned edges logged


def test_reciprocity_calculation():
    """Test reciprocity calculation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "edges.json")
        log_path = os.path.join(tmpdir, "edges_history.jsonl")
        
        engine = PruningEngine(store_path, log_path)
        
        edge = {
            "from": "kr-01", "to": "kr-02", "weight": 0.5,
            "reciprocal_exchanges": 3, "one_directional_exchanges": 1
        }
        
        reciprocity = engine.compute_reciprocity(edge)
        assert reciprocity == 0.75  # 3 / (3+1)


if __name__ == "__main__":
    test_pruning_engine()
    test_reciprocity_calculation()
    print("All prune tests passed!")