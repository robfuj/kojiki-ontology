"""
MYCELIUM Graph - Edge store and centrality computation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import math


class EdgeStore:
    """Store and manage edges between Key Results."""
    
    def __init__(self, store_path: str):
        self.store_path = Path(store_path)
        self.edges: Dict[str, Dict[str, Any]] = {}  # key = "from_kr->to_kr"
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
        """Generate edge key."""
        return f"{from_kr}->{to_kr}"
    
    def add_edge(self, edge_data: Dict[str, Any]) -> None:
        """Add or update an edge."""
        key = self.edge_key(edge_data['from'], edge_data['to'])
        edge_data['last_reinforced'] = edge_data.get('last_reinforced', datetime.utcnow().isoformat() + 'Z')
        self.edges[key] = edge_data
        self.save()
    
    def get_edge(self, from_kr: str, to_kr: str) -> Optional[Dict[str, Any]]:
        """Get edge by from/to KR."""
        return self.edges.get(self.edge_key(from_kr, to_kr))
    
    def get_outgoing(self, from_kr: str) -> List[Dict[str, Any]]:
        """Get all outgoing edges from a KR."""
        return [e for k, e in self.edges.items() if k.startswith(from_kr + "->")]
    
    def get_incoming(self, to_kr: str) -> List[Dict[str, Any]]:
        """Get all incoming edges to a KR."""
        return [e for k, e in self.edges.items() if k.endswith("->" + to_kr)]
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all edges."""
        return list(self.edges.values())
    
    def update_exchange_counts(self, from_kr: str, to_kr: str, reciprocal: bool = True) -> None:
        """Update exchange counts after a signal propagation."""
        key = self.edge_key(from_kr, to_kr)
        if key in self.edges:
            if reciprocal:
                self.edges[key]['reciprocal_exchanges'] += 1
            else:
                self.edges[key]['one_directional_exchanges'] += 1
            self.edges[key]['last_reinforced'] = datetime.utcnow().isoformat() + 'Z'
            self.save()


class CentralityComputer:
    """Compute centrality metrics for nodes in the KR graph."""
    
    def __init__(self, edge_store: EdgeStore):
        self.edge_store = edge_store
    
    def compute_weighted_degree(self) -> Dict[str, Dict[str, float]]:
        """Compute weighted in-degree and out-degree for each KR."""
        in_degree = defaultdict(float)
        out_degree = defaultdict(float)
        
        for edge in self.edge_store.get_all_edges():
            from_kr = edge['from']
            to_kr = edge['to']
            weight = edge['weight']
            out_degree[from_kr] += weight
            in_degree[to_kr] += weight
        
        all_krs = set(in_degree.keys()) | set(out_degree.keys())
        return {
            kr: {"in_degree": in_degree.get(kr, 0.0), "out_degree": out_degree.get(kr, 0.0)}
            for kr in all_krs
        }
    
    def compute_betweenness(self, max_nodes: int = 100) -> Dict[str, float]:
        """
        Compute approximate betweenness centrality using Brandes algorithm.
        Limited to max_nodes for performance.
        """
        # Build adjacency list
        adj = defaultdict(list)
        krs = set()
        
        for edge in self.edge_store.get_all_edges():
            from_kr = edge['from']
            to_kr = edge['to']
            weight = edge['weight']
            if weight > 0:
                adj[from_kr].append((to_kr, weight))
                krs.add(from_kr)
                krs.add(to_kr)
        
        krs = list(krs)[:max_nodes]
        betweenness = defaultdict(float)
        
        for s in krs:
            # Single-source shortest paths
            stack = []
            pred = defaultdict(list)
            sigma = defaultdict(float)
            dist = defaultdict(lambda: float('inf'))
            
            sigma[s] = 1.0
            dist[s] = 0.0
            
            # Dijkstra with weights
            import heapq
            pq = [(0.0, s)]
            visited = set()
            
            while pq:
                d, v = heapq.heappop(pq)
                if v in visited:
                    continue
                visited.add(v)
                stack.append(v)
                
                for w, weight in adj[v]:
                    # Use inverse weight as distance
                    vw_dist = d + (1.0 / weight if weight > 0 else float('inf'))
                    if vw_dist < dist[w]:
                        dist[w] = vw_dist
                        heapq.heappush(pq, (vw_dist, w))
                        sigma[w] = sigma[v]
                        pred[w] = [v]
                    elif abs(vw_dist - dist[w]) < 1e-10:
                        sigma[w] += sigma[v]
                        pred[w].append(v)
            
            # Accumulate dependencies
            delta = defaultdict(float)
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]
        
        # Normalize
        n = len(krs)
        if n > 2:
            scale = 1.0 / ((n - 1) * (n - 2))
            for k in betweenness:
                betweenness[k] *= scale
        
        return dict(betweenness)
    
    def compute_all(self) -> Dict[str, Any]:
        """Compute all centrality metrics."""
        degree = self.compute_weighted_degree()
        betweenness = self.compute_betweenness()
        
        all_krs = set(degree.keys()) | set(betweenness.keys())
        return {
            kr: {
                "in_degree": degree.get(kr, {}).get("in_degree", 0.0),
                "out_degree": degree.get(kr, {}).get("out_degree", 0.0),
                "betweenness": betweenness.get(kr, 0.0)
            }
            for kr in all_krs
        }


def main():
    """CLI for graph operations."""
    import sys
    edge_store = EdgeStore("mycelium/graph/edges.json")
    centrality = CentralityComputer(edge_store)
    
    if len(sys.argv) < 2:
        print("Usage: python graph.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "centrality":
        result = centrality.compute_all()
        print(json.dumps(result, indent=2))
    
    elif cmd == "edges":
        for edge in edge_store.get_all_edges():
            print(f"{edge['from']} -> {edge['to']} (w={edge['weight']:.2f})")
    
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: python graph.py add <from_kr> <to_kr> <weight>")
            return
        from_kr = sys.argv[2]
        to_kr = sys.argv[3]
        weight = float(sys.argv[4])
        edge_store.add_edge({
            "from": from_kr,
            "to": to_kr,
            "weight": weight,
            "reciprocal_exchanges": 0,
            "one_directional_exchanges": 0,
            "trigger": "",
            "required_data": "",
            "acceptance_criteria": "",
            "sla": "",
            "exception_path": ""
        })
        print(f"Edge added: {from_kr} -> {to_kr}")


if __name__ == "__main__":
    main()