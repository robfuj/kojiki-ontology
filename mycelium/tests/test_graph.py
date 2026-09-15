"""
Tests for MYCELIUM Graph.
"""

import json
import tempfile
import os
from mycelium.engine.graph import EdgeStore, CentralityComputer


def test_edge_store():
    """Test edge store basic operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "edges.json")
        edge_store = EdgeStore(store_path)
        
        # Add edges
        edge_store.add_edge({
            "from": "kr-01",
            "to": "kr-02",
            "weight": 0.5,
            "reciprocal_exchanges": 2,
            "one_directional_exchanges": 1,
            "trigger": "test",
            "required_data": "test",
            "acceptance_criteria": "test",
            "sla": "test",
            "exception_path": "test"
        })
        
        edge_store.add_edge({
            "from": "kr-02",
            "to": "kr-03",
            "weight": 0.8,
            "reciprocal_exchanges": 3,
            "one_directional_exchanges": 0,
            "trigger": "test",
            "required_data": "test",
            "acceptance_criteria": "test",
            "sla": "test",
            "exception_path": "test"
        })
        
        # Test retrieval
        edge = edge_store.get_edge("kr-01", "kr-02")
        assert edge is not None
        assert edge['weight'] == 0.5
        
        outgoing = edge_store.get_outgoing("kr-01")
        assert len(outgoing) == 1
        
        incoming = edge_store.get_incoming("kr-02")
        assert len(incoming) == 1
        
        all_edges = edge_store.get_all_edges()
        assert len(all_edges) == 2


def test_update_exchange_counts():
    """Test exchange count updates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "edges.json")
        edge_store = EdgeStore(store_path)
        
        edge_store.add_edge({
            "from": "kr-01",
            "to": "kr-02",
            "weight": 0.5,
            "reciprocal_exchanges": 0,
            "one_directional_exchanges": 0,
            "trigger": "test",
            "required_data": "test",
            "acceptance_criteria": "test",
            "sla": "test",
            "exception_path": "test"
        })
        
        # Update with reciprocal exchange
        edge_store.update_exchange_counts("kr-01", "kr-02", reciprocal=True)
        edge = edge_store.get_edge("kr-01", "kr-02")
        assert edge is not None
        assert edge['reciprocal_exchanges'] == 1
        
        # Update with one-directional exchange
        edge_store.update_exchange_counts("kr-01", "kr-02", reciprocal=False)
        edge = edge_store.get_edge("kr-01", "kr-02")
        assert edge is not None
        assert edge['one_directional_exchanges'] == 1


def test_centrality_computation():
    """Test centrality metrics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "edges.json")
        edge_store = EdgeStore(store_path)
        centrality = CentralityComputer(edge_store)
        
        # Create a small graph: kr-01 -> kr-02 -> kr-03, kr-01 -> kr-03
        edge_store.add_edge({
            "from": "kr-01", "to": "kr-02", "weight": 0.5,
            "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
            "trigger": "", "required_data": "", "acceptance_criteria": "",
            "sla": "", "exception_path": ""
        })
        edge_store.add_edge({
            "from": "kr-02", "to": "kr-03", "weight": 0.8,
            "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
            "trigger": "", "required_data": "", "acceptance_criteria": "",
            "sla": "", "exception_path": ""
        })
        edge_store.add_edge({
            "from": "kr-01", "to": "kr-03", "weight": 0.3,
            "reciprocal_exchanges": 0, "one_directional_exchanges": 0,
            "trigger": "", "required_data": "", "acceptance_criteria": "",
            "sla": "", "exception_path": ""
        })
        
        degree = centrality.compute_weighted_degree()
        assert "kr-01" in degree
        assert degree["kr-01"]["out_degree"] == 0.8  # 0.5 + 0.3
        assert degree["kr-03"]["in_degree"] == 1.1  # 0.8 + 0.3
        
        betweenness = centrality.compute_betweenness()
        # kr-02 should have some betweenness as it's on the path kr-01 -> kr-02 -> kr-03
        assert "kr-02" in betweenness


if __name__ == "__main__":
    test_edge_store()
    test_update_exchange_counts()
    test_centrality_computation()
    print("All graph tests passed!")