"""
MYCELIUM Propagate - Signal propagation across decision subgraphs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import deque


SUBGRAPH_THRESHOLD = 0.15  # Default threshold for subgraph computation


class SignalPropagator:
    """Propagate signals through the decision subgraph."""
    
    def __init__(self, edge_store_path: str, log_path: str, threshold: float = SUBGRAPH_THRESHOLD):
        self.edge_store_path = Path(edge_store_path)
        self.log_path = Path(log_path)
        self.threshold = threshold
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.load_edges()
        self.ensure_log_file()
    
    def load_edges(self) -> None:
        """Load edges from edge store."""
        if self.edge_store_path.exists():
            with open(self.edge_store_path, 'r') as f:
                data = json.load(f)
                self.edges = data.get('edges', {})
    
    def ensure_log_file(self) -> None:
        """Ensure signal log file exists."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, 'w') as f:
                pass  # Create empty file
    
    def edge_key(self, from_kr: str, to_kr: str) -> str:
        return f"{from_kr}->{to_kr}"
    
    def build_adjacency(self) -> Dict[str, List[str]]:
        """Build adjacency list for edges above threshold."""
        adj = {}
        for key, edge in self.edges.items():
            if edge['weight'] >= self.threshold:
                from_kr = edge['from']
                to_kr = edge['to']
                if from_kr not in adj:
                    adj[from_kr] = []
                adj[from_kr].append(to_kr)
        return adj
    
    def compute_subgraph(self, origin_kr: str) -> Set[str]:
        """
        Compute decision subgraph from origin KR.
        
        Includes origin, all nodes connected at weight > threshold,
        and recursively one hop further if that edge is also above threshold.
        """
        adj = self.build_adjacency()
        subgraph = set()
        queue = deque([origin_kr])
        visited = set()
        hop = 0
        
        while queue and hop < 3:  # Max 3 levels (origin + 1 recursive hop = 2 hops from origin)
            level_size = len(queue)
            for _ in range(level_size):
                kr = queue.popleft()
                if kr in visited:
                    continue
                visited.add(kr)
                subgraph.add(kr)
                
                # Add neighbors
                for neighbor in adj.get(kr, []):
                    if neighbor not in visited:
                        queue.append(neighbor)
            hop += 1
        
        return subgraph
    
    def validate_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate signal has required fields."""
        required = ['id', 'origin_kr', 'event', 'new_status', 
                    'diagnosed_cause', 'diagnosed_cause_category', 'status', 'subgraph', 'fired_at']
        for field in required:
            if field not in signal:
                return False
        # diagnosed_cause must not be empty
        if not signal.get('diagnosed_cause', '').strip():
            return False
        # diagnosed_cause_category must be valid
        valid_categories = [
            "Signal", "Pattern", "Cause", "Assumption", "Decision", "Action",
            "Exception", "Failure", "Success", "Rule", "Threshold", "Automation",
            "Escalation", "Memory"
        ]
        if signal.get('diagnosed_cause_category') not in valid_categories:
            return False
        # status must be valid
        valid_statuses = ["ROUTED", "APPLIED_UNVERIFIED", "CLOSED_VERIFIED", "WITHDRAWN"]
        if signal.get('status') not in valid_statuses:
            return False
        return True
    
    def propagate(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propagate a signal to its decision subgraph.
        
        Returns dict with propagation results.
        """
        # Validate signal
        if not self.validate_signal(signal):
            return {
                "success": False,
                "error": "Invalid signal: missing required fields or empty diagnosed_cause"
            }
        
        # Compute subgraph
        subgraph = self.compute_subgraph(signal['origin_kr'])
        
        # Update signal with computed subgraph
        signal['subgraph'] = list(subgraph)
        
        # Log signal (append-only)
        self.log_signal(signal)
        
        # Update edge exchange counts for edges in subgraph
        self.update_edge_exchanges(signal['origin_kr'], subgraph)
        
        return {
            "success": True,
            "subgraph": list(subgraph),
            "signal_id": signal['id'],
            "nodes_notified": len(subgraph)
        }
    
    def log_signal(self, signal: Dict[str, Any]) -> None:
        """Append signal to log file."""
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(signal) + '\n')
    
    def update_edge_exchanges(self, origin_kr: str, subgraph: Set[str]) -> None:
        """Update exchange counts for edges involved in signal propagation."""
        # For edges from origin to subgraph nodes, mark as reciprocal if both directions exist
        # For edges within subgraph that were traversed, mark appropriately
        adj = self.build_adjacency()
        
        for kr in subgraph:
            if kr == origin_kr:
                continue
            # Check if edge exists from origin to this node
            for edge_key, edge in self.edges.items():
                if edge['from'] == origin_kr and edge['to'] == kr:
                    # This edge was used for propagation - check if reciprocal
                    reverse_key = self.edge_key(kr, origin_kr)
                    if reverse_key in self.edges and self.edges[reverse_key]['weight'] >= self.threshold:
                        edge['reciprocal_exchanges'] += 1
                    else:
                        edge['one_directional_exchanges'] += 1
                    edge['last_reinforced'] = datetime.utcnow().isoformat() + 'Z'
    
    def get_signals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent signals from log."""
        signals = []
        if self.log_path.exists():
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        signals.append(json.loads(line))
        return signals[-limit:]


def main():
    """CLI for propagation operations."""
    import sys
    propagator = SignalPropagator(
        "mycelium/engine/graph/edges.json",
        "mycelium/log/signals.jsonl"
    )
    
    if len(sys.argv) < 2:
        print("Usage: python propagate.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "propagate":
        if len(sys.argv) < 3:
            print("Usage: python propagate.py propagate <signal_json>")
            return
        signal = json.loads(sys.argv[2])
        result = propagator.propagate(signal)
        print(json.dumps(result, indent=2))
    
    elif cmd == "subgraph":
        if len(sys.argv) < 3:
            print("Usage: python propagate.py subgraph <origin_kr>")
            return
        origin_kr = sys.argv[2]
        subgraph = propagator.compute_subgraph(origin_kr)
        print(f"Subgraph for {origin_kr}: {sorted(subgraph)}")
    
    elif cmd == "signals":
        signals = propagator.get_signals()
        for s in signals:
            print(f"{s['id']}: {s['origin_kr']} -> {s['new_status']} ({s['diagnosed_cause_category']})")
    
    elif cmd == "threshold":
        print(f"Current threshold: {propagator.threshold}")


if __name__ == "__main__":
    main()