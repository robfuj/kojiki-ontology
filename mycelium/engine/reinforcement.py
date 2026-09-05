"""
MYCELIUM Reinforcement - Tero-style conductivity update for edge weights.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import math


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def reinforce(edge: Dict[str, Any], flow_signal: float, 
              gamma: float = 1.15, decay_rate: float = 0.08, 
              reinforcement_rate: float = 0.35) -> Dict[str, Any]:
    """
    Reinforce or decay an edge based on flow signal.
    
    Formula: dD/dt = f(|Q|) - D, where f(Q) = |Q|^gamma
    Discrete approximation: weight = weight * (1 - decay_rate) + reinforcement_rate * (flow_signal ** gamma)
    
    Args:
        edge: Edge dictionary with 'weight', 'reciprocal_exchanges', 'one_directional_exchanges'
        flow_signal: 1.0 if dependency delivered/used (reciprocal), 0.0 if declared but not delivered,
                     fractional for partial delivery
        gamma: Efficiency vs redundancy tradeoff (higher = sparser, lower = more redundant)
        decay_rate: Per-cycle decay rate
        reinforcement_rate: Per-cycle reinforcement rate
    
    Returns:
        Updated edge dictionary
    """
    # Apply decay and reinforcement
    new_weight = edge['weight'] * (1 - decay_rate) + reinforcement_rate * (flow_signal ** gamma)
    new_weight = clamp(new_weight, 0.0, 1.0)
    
    updated_edge = edge.copy()
    updated_edge['weight'] = new_weight
    updated_edge['last_reinforced'] = datetime.utcnow().isoformat() + 'Z'
    
    return updated_edge


def compute_flow_signal(edge: Dict[str, Any], delivery_confirmed: bool, 
                        partial_delivery: float = 0.0) -> float:
    """
    Compute flow signal based on delivery confirmation.
    
    Args:
        edge: Edge dictionary
        delivery_confirmed: Whether the dependency was actually delivered/used
        partial_delivery: Fractional delivery amount (0.0 to 1.0)
    
    Returns:
        Flow signal value (0.0 to 1.0)
    """
    if delivery_confirmed:
        if partial_delivery > 0:
            return partial_delivery
        return 1.0
    return 0.0


def compute_reciprocity(edge: Dict[str, Any]) -> float:
    """Compute reciprocity ratio for an edge."""
    reciprocal = edge.get('reciprocal_exchanges', 0)
    one_directional = edge.get('one_directional_exchanges', 0)
    total = reciprocal + one_directional
    if total == 0:
        return 0.0
    return reciprocal / total


class ReinforcementEngine:
    """Engine for managing edge reinforcement across the graph."""
    
    def __init__(self, store_path: str, gamma: float = 1.15, 
                 decay_rate: float = 0.08, reinforcement_rate: float = 0.35):
        self.store_path = Path(store_path)
        self.gamma = gamma
        self.decay_rate = decay_rate
        self.reinforcement_rate = reinforcement_rate
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.load()
    
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
    
    def edge_key(self, from_kr: str, to_kr: str) -> str:
        return f"{from_kr}->{to_kr}"
    
    def reinforce_edge(self, from_kr: str, to_kr: str, flow_signal: float) -> Optional[Dict[str, Any]]:
        """Reinforce a specific edge."""
        key = self.edge_key(from_kr, to_kr)
        if key not in self.edges:
            return None
        
        self.edges[key] = reinforce(
            self.edges[key], flow_signal, 
            self.gamma, self.decay_rate, self.reinforcement_rate
        )
        self.save()
        return self.edges[key]
    
    def reinforce_all(self, flow_signals: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Reinforce all edges with their flow signals.
        
        Args:
            flow_signals: Dict mapping edge_key to flow_signal value
        
        Returns:
            Dict of updated edges
        """
        updated = {}
        for key, edge in self.edges.items():
            flow_signal = flow_signals.get(key, 0.0)
            self.edges[key] = reinforce(
                edge, flow_signal,
                self.gamma, self.decay_rate, self.reinforcement_rate
            )
            updated[key] = self.edges[key]
        self.save()
        return updated
    
    def get_edge(self, from_kr: str, to_kr: str) -> Optional[Dict[str, Any]]:
        return self.edges.get(self.edge_key(from_kr, to_kr))
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        return list(self.edges.values())


def main():
    """CLI for reinforcement operations."""
    import sys
    engine = ReinforcementEngine("mycelium/engine/reinforcement.json")
    
    if len(sys.argv) < 2:
        print("Usage: python reinforcement.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "reinforce":
        if len(sys.argv) < 5:
            print("Usage: python reinforcement.py reinforce <from_kr> <to_kr> <flow_signal>")
            return
        from_kr = sys.argv[2]
        to_kr = sys.argv[3]
        flow_signal = float(sys.argv[4])
        result = engine.reinforce_edge(from_kr, to_kr, flow_signal)
        if result:
            print(f"Reinforced: {from_kr} -> {to_kr} (weight={result['weight']:.4f})")
        else:
            print("Edge not found")
    
    elif cmd == "config":
        print(f"gamma={engine.gamma}, decay_rate={engine.decay_rate}, reinforcement_rate={engine.reinforcement_rate}")
    
    elif cmd == "edges":
        for edge in engine.get_all_edges():
            recip = compute_reciprocity(edge)
            print(f"{edge['from']} -> {edge['to']}: w={edge['weight']:.4f}, recip={recip:.2f}")


if __name__ == "__main__":
    main()