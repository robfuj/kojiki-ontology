"""
MYCELIUM Prune - Decay and reciprocity-aware pruning.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class PruningEngine:
    """Engine for pruning edges based on weight and reciprocity."""
    
    def __init__(self, store_path: str, log_path: str, 
                 min_weight: float = 0.05, reciprocity_floor: float = 0.2):
        self.store_path = Path(store_path)
        self.log_path = Path(log_path)
        self.min_weight = min_weight
        self.reciprocity_floor = reciprocity_floor
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.load()
        self.ensure_log_file()
    
    def load(self) -> None:
        """Load edges from file."""
        if self.store_path.exists():
            with open(self.store_path, 'r') as f:
                data = json.load(f)
                self.edges = data.get('edges', {})
    
    def save(self) -> None:
        """Save edges to file."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"edges": self.edges}
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def ensure_log_file(self) -> None:
        """Ensure edge history log file exists."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, 'w') as f:
                pass
    
    def edge_key(self, from_kr: str, to_kr: str) -> str:
        return f"{from_kr}->{to_kr}"
    
    def compute_reciprocity(self, edge: Dict[str, Any]) -> float:
        """Compute reciprocity ratio for an edge."""
        reciprocal = edge.get('reciprocal_exchanges', 0)
        one_directional = edge.get('one_directional_exchanges', 0)
        total = reciprocal + one_directional
        if total == 0:
            return 0.0
        return reciprocal / total
    
    def maybe_prune(self, edge: Dict[str, Any]) -> str:
        """
        Determine if an edge should be pruned.
        
        Returns: "prune" or "keep"
        
        An edge with high weight but poor reciprocity is pruned - the parasitism guard.
        """
        weight = edge.get('weight', 0.0)
        reciprocity = self.compute_reciprocity(edge)
        
        if weight < self.min_weight or reciprocity < self.reciprocity_floor:
            return "prune"
        return "keep"
    
    def prune_edges(self) -> List[Dict[str, Any]]:
        """
        Prune all edges that meet pruning criteria.
        
        Returns list of pruned edges.
        """
        pruned = []
        keys_to_remove = []
        
        for key, edge in self.edges.items():
            if self.maybe_prune(edge) == "prune":
                # Log before removal
                self.log_edge_change(key, edge, "PRUNED")
                pruned.append(edge.copy())
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.edges[key]
        
        if pruned:
            self.save()
        
        return pruned
    
    def log_edge_change(self, key: str, edge: Dict[str, Any], action: str) -> None:
        """Log edge weight change to history."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "edge_key": key,
            "from": edge['from'],
            "to": edge['to'],
            "weight": edge.get('weight', 0.0),
            "reciprocity": self.compute_reciprocity(edge),
            "reciprocal_exchanges": edge.get('reciprocal_exchanges', 0),
            "one_directional_exchanges": edge.get('one_directional_exchanges', 0),
            "action": action
        }
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_weight_change(self, from_kr: str, to_kr: str, old_weight: float, new_weight: float) -> None:
        """Log edge weight change."""
        edge = self.edges.get(self.edge_key(from_kr, to_kr))
        if edge:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "edge_key": self.edge_key(from_kr, to_kr),
                "from": from_kr,
                "to": to_kr,
                "old_weight": old_weight,
                "new_weight": new_weight,
                "reciprocity": self.compute_reciprocity(edge),
                "action": "WEIGHT_CHANGE"
            }
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def get_edge_status(self, from_kr: str, to_kr: str) -> Optional[Dict[str, Any]]:
        """Get edge status including pruning recommendation."""
        key = self.edge_key(from_kr, to_kr)
        edge = self.edges.get(key)
        if not edge:
            return None
        
        reciprocity = self.compute_reciprocity(edge)
        prune_decision = self.maybe_prune(edge)
        
        return {
            "edge_key": key,
            "from": from_kr,
            "to": to_kr,
            "weight": edge.get('weight', 0.0),
            "reciprocity": reciprocity,
            "reciprocal_exchanges": edge.get('reciprocal_exchanges', 0),
            "one_directional_exchanges": edge.get('one_directional_exchanges', 0),
            "prune_decision": prune_decision,
            "min_weight_threshold": self.min_weight,
            "reciprocity_floor_threshold": self.reciprocity_floor
        }
    
    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Get status for all edges."""
        statuses = []
        for e in self.edges.values():
            status = self.get_edge_status(e['from'], e['to'])
            if status:
                statuses.append(status)
        return statuses
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all edges."""
        return list(self.edges.values())


def main():
    """CLI for pruning operations."""
    import sys
    engine = PruningEngine(
        "mycelium/engine/graph/edges.json",
        "mycelium/log/edges_history.jsonl"
    )
    
    if len(sys.argv) < 2:
        print("Usage: python prune.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "prune":
        pruned = engine.prune_edges()
        print(f"Pruned {len(pruned)} edges:")
        for edge in pruned:
            print(f"  {edge['from']} -> {edge['to']}")
    
    elif cmd == "status":
        if len(sys.argv) < 4:
            print("Usage: python prune.py status <from_kr> <to_kr>")
            return
        from_kr = sys.argv[2]
        to_kr = sys.argv[3]
        status = engine.get_edge_status(from_kr, to_kr)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print("Edge not found")
    
    elif cmd == "all-status":
        statuses = engine.get_all_statuses()
        for s in statuses:
            if s:
                print(f"{s['from']} -> {s['to']}: w={s['weight']:.4f}, recip={s['reciprocity']:.2f}, prune={s['prune_decision']}")
    
    elif cmd == "config":
        print(f"min_weight={engine.min_weight}, reciprocity_floor={engine.reciprocity_floor}")


if __name__ == "__main__":
    main()