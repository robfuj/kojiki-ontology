"""
MYCELIUM Demo - Marketing and Sales dependency example.
"""

import json
import os
from datetime import datetime
from mycelium.engine.registry import NodeRegistry
from mycelium.engine.graph import EdgeStore
from mycelium.engine.reinforcement import ReinforcementEngine
from mycelium.engine.propagate import SignalPropagator
from mycelium.engine.prune import PruningEngine


def setup_demo():
    """Set up the worked example from the thesis."""
    
    # Initialize components with absolute paths
    base_path = "/Users/Fujita/Documents/AI Filing System/decision-systems/00-kojiki-ontology/mycelium"
    registry = NodeRegistry(os.path.join(base_path, "registry/nodes.json"))
    edge_store = EdgeStore(os.path.join(base_path, "graph/edges.json"))
    
    # Nodes (already in registry as root departments)
    # Marketing.Head, Marketing.Head.SEO, Sales.Head, Finance.Head
    
    # Spawn Marketing.Head.SEO as child
    registry.register_node({
        "id": "Marketing.Head.SEO",
        "parent": "Marketing.Head",
        "domain": "marketing/seo",
        "type": "sub-agent",
        "spawn_reason": "keyword strategy needed dedicated capacity"
    })
    
    # Add edges for dependencies
    # Marketing.Head.SEO KR depends on Marketing.Head KR (lineage-internal, high weight)
    edge_store.add_edge({
        "from": "kr-2026Q4-marketing-seo-01",
        "to": "kr-2026Q4-marketing-01",
        "weight": 0.85,
        "reciprocal_exchanges": 5,
        "one_directional_exchanges": 0,
        "trigger": "Marketing.Head KR-01 status change",
        "required_data": "keyword strategy direction",
        "acceptance_criteria": "SEO can act on strategy without clarification",
        "sla": "within 1 review cycle",
        "exception_path": "REQUEST escalates to Marketing.Head"
    })
    
    # Marketing.Head KR depends on Sales.Head KR (declared dependency, moderate weight)
    # Edge direction: from dependency (Sales) to dependent (Marketing) for propagation
    edge_store.add_edge({
        "from": "kr-2026Q4-sales-03",
        "to": "kr-2026Q4-marketing-01",
        "weight": 0.62,
        "reciprocal_exchanges": 3,
        "one_directional_exchanges": 0,
        "trigger": "Sales.Head KR-03 status change",
        "required_data": "qualified lead volume by segment",
        "acceptance_criteria": "Marketing can act on the figure without further clarification",
        "sla": "within 1 review cycle",
        "exception_path": "REQUEST escalates to Sales.Head"
    })
    
    # Initialize propagator AFTER edges are added
    propagator = SignalPropagator(os.path.join(base_path, "graph/edges.json"), os.path.join(base_path, "log/signals.jsonl"))
    pruner = PruningEngine(os.path.join(base_path, "graph/edges.json"), os.path.join(base_path, "log/edges_history.jsonl"))
    reinforcement = ReinforcementEngine(os.path.join(base_path, "engine/reinforcement.json"))
    
    # Sync reinforcement engine
    for edge in edge_store.get_all_edges():
        key = f"{edge['from']}->{edge['to']}"
        reinforcement.edges[key] = edge
    reinforcement.save()
    
    print("Demo setup complete:")
    print("  Nodes:", [n['id'] for n in registry.get_all_nodes()])
    print("  Edges:", len(edge_store.get_all_edges()))
    
    return registry, edge_store, reinforcement, propagator, pruner


def run_scenario():
    """Run the worked scenario: Sales.Head KR goes off_track."""
    
    registry, edge_store, reinforcement, propagator, pruner = setup_demo()
    
    print("\n=== SCENARIO: Sales.Head KR goes off_track ===")
    
    # Fire signal: Sales.Head KR-03 goes off_track
    signal = {
        "id": "sig-0001",
        "origin_kr": "kr-2026Q4-sales-03",
        "event": "status_change",
        "new_status": "off_track",
        "diagnosed_cause": "lead scoring model shipped 3 weeks late",
        "diagnosed_cause_category": "Cause",
        "status": "ROUTED",
        "subgraph": [],  # Will be computed
        "fired_at": datetime.utcnow().isoformat() + 'Z'
    }
    
    # Propagate
    result = propagator.propagate(signal)
    print(f"Propagation result: {json.dumps(result, indent=2)}")
    
    # Show what Finance.Head receives (should be nothing)
    finance_subgraph = propagator.compute_subgraph("kr-2026Q4-finance-01")
    print(f"\nFinance.Head subgraph (should be isolated): {finance_subgraph}")
    
    # Update edge exchanges - the Sales->Marketing edge was used but not delivered
    edge_store.update_exchange_counts("kr-2026Q4-sales-03", "kr-2026Q4-marketing-01", reciprocal=False)
    
    # Reinforce edges based on this cycle
    flow_signals = {
        "kr-2026Q4-marketing-seo-01->kr-2026Q4-marketing-01": 1.0,  # Delivered
        "kr-2026Q4-sales-03->kr-2026Q4-marketing-01": 0.0,  # Not delivered (Sales didn't deliver)
    }
    reinforcement.reinforce_all(flow_signals)
    
    print("\n=== AFTER REINFORCEMENT ===")
    for edge in edge_store.get_all_edges():
        recip = edge['reciprocal_exchanges'] / max(1, edge['reciprocal_exchanges'] + edge['one_directional_exchanges'])
        print(f"  {edge['from']} -> {edge['to']}: weight={edge['weight']:.4f}, recip={recip:.2f}, recip_ex={edge['reciprocal_exchanges']}, one_dir_ex={edge['one_directional_exchanges']}")
    
    # Run pruning
    print("\n=== PRUNING CHECK ===")
    for edge in edge_store.get_all_edges():
        status = pruner.get_edge_status(edge['from'], edge['to'])
        if status:
            print(f"  {status['from']} -> {status['to']}: w={status['weight']:.4f}, recip={status['reciprocity']:.2f}, prune={status['prune_decision']}")
    
    pruned = pruner.prune_edges()
    print(f"\nPruned {len(pruned)} edges")
    
    # Show signal log
    print("\n=== SIGNAL LOG ===")
    signals = propagator.get_signals()
    for s in signals:
        print(f"  {s['id']}: {s['origin_kr']} -> {s['new_status']} ({s['diagnosed_cause_category']})")


if __name__ == "__main__":
    run_scenario()