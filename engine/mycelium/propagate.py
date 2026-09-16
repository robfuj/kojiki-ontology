"""
MYCELIUM Propagate - Signal propagation across decision subgraphs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import deque

# Import SENTINEL for signature verification
import sys
from pathlib import Path

from engine.sentinel import canonical_json, verify_signature

# Import registry to check node key status
import sys

from engine.mycelium.registry import NodeRegistry

# Import Decision Rights gating

from engine.mycelium.decision_rights import DecisionRightsGate, SignalType, DecisionRight

# Import reinforcement for proper flow signal computation
from engine.mycelium.reinforcement import compute_flow_signal, reinforce


SUBGRAPH_THRESHOLD = 0.15  # Default threshold for subgraph computation


class SignalPropagator:
    """Propagate signals through the decision subgraph."""
    
    def __init__(self, edge_store_path: str, log_path: str, threshold: float = SUBGRAPH_THRESHOLD,
                 registry: Optional[NodeRegistry] = None, registry_path: Optional[str] = None):
        self.edge_store_path = Path(edge_store_path)
        self.log_path = Path(log_path)
        self.threshold = threshold
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.registry = registry or (NodeRegistry(registry_path) if registry_path else None)
        self.load_edges()
        self.ensure_log_file()
    
    def load_edges(self) -> None:
        """Load edges from edge store."""
        if self.edge_store_path.exists():
            with open(self.edge_store_path, 'r') as f:
                data = json.load(f)
                self.edges = data.get('edges', {})
    
    def save_edges(self) -> None:
        """Save edges to edge store."""
        self.edge_store_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"edges": self.edges}
        with open(self.edge_store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
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
        """Validate signal has required fields (excluding subgraph - computed before validation)."""
        # Base required fields for all signals
        required = ['id', 'origin_kr', 'event', 'new_status', 'signal_kind', 'subgraph', 'fired_at']
        for field in required:
            if field not in signal:
                return False
        
        signal_kind = signal.get('signal_kind')
        
        # signal_kind must be valid
        if signal_kind not in ('failure', 'request'):
            return False
        
        # For failure signals: diagnosed_cause and diagnosed_cause_category required
        if signal_kind == 'failure':
            if not signal.get('diagnosed_cause', '').strip():
                return False
            valid_categories = [
                "Signal", "Pattern", "Cause", "Assumption", "Decision", "Action",
                "Exception", "Failure", "Success", "Rule", "Threshold", "Automation",
                "Escalation", "Memory"
            ]
            if signal.get('diagnosed_cause_category') not in valid_categories:
                return False
        # For request signals: diagnosed_cause and category are ignored if present
        
        # status must be valid
        valid_statuses = ["ROUTED", "APPLIED_UNVERIFIED", "CLOSED_VERIFIED", "WITHDRAWN"]
        if signal.get('status') not in valid_statuses:
            return False
        
        # subgraph must be present and non-empty (computed before validation)
        if 'subgraph' not in signal or not signal['subgraph']:
            return False
        
        return True
    
    def validate_signal_signature(self, signal: Dict[str, Any]) -> bool:
        """
        Verify the signal's signature against the origin node's public key.
        
        Expects signal to contain:
        - 'signature': Ed25519 signature over canonical_json(signal_without_signature_and_subgraph)
        - 'origin_kr': the node ID that signed the signal
        
        Returns True if signature is valid and origin node has key_status='active'.
        """
        if 'signature' not in signal or 'origin_kr' not in signal:
            return False
        
        origin_kr = signal['origin_kr']
        
        # Check registry if available
        if self.registry:
            node = self.registry.get_node(origin_kr)
            if not node:
                return False
            if node.get('key_status') != 'active':
                return False
            public_key = node.get('public_key')
            if not public_key:
                return False
        else:
            # No registry available - can't verify
            return False
        
        # Create a copy of signal without the signature AND subgraph fields for verification
        # The subgraph is computed by the receiver, not signed by the sender
        signal_to_verify = {k: v for k, v in signal.items() if k not in ('signature', 'subgraph')}
        data = canonical_json(signal_to_verify)
        
        return verify_signature(signal['signature'], data, public_key)
    
    def propagate(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propagate a signal to its decision subgraph.
        
        Returns dict with propagation results.
        """
        # Handle deck_request signal type
        if signal.get('event') == 'deck_request':
            return self._propagate_deck_request(signal)
        
        # Compute subgraph FIRST (before validation, so it's covered by signature)
        subgraph = self.compute_subgraph(signal['origin_kr'])
        
        # Apply Decision Rights gating
        signal_type = SignalType(signal.get('signal_kind', 'failure'))
        if self.registry:
            gate = DecisionRightsGate()
            # Load rights from registry
            for node_id in subgraph:
                node = self.registry.get_node(node_id)
                if node and node.get("decision_rights"):
                    # decision_rights can be a string (primary right) or dict with 'own', 'consult', 'inform' keys
                    # The primary right is in 'decision_right' field or 'own' in decision_rights
                    dr = node['decision_rights']
                    if isinstance(dr, str):
                        primary_right = dr
                    elif isinstance(dr, dict):
                        primary_right = node.get('decision_right') or dr.get('own')
                    else:
                        primary_right = None
                    
                    if primary_right:
                        gate.set_node_right(node_id, DecisionRight(primary_right))
            
            # Validate origin has rights to send this signal
            if not gate.validate_origin_right(signal_type, signal['origin_kr']):
                return {
                    "success": False,
                    "error": f"Origin {signal['origin_kr']} lacks Decision Rights to send {signal_type.value}"
                }
            
            # Filter subgraph by target rights
            subgraph = gate.filter_recipients(signal_type, signal['origin_kr'], subgraph, role="target")
        
        # Add computed (and gated) subgraph to signal
        signal['subgraph'] = list(subgraph)
        
        # Validate signal shape (now includes subgraph)
        if not self.validate_signal(signal):
            return {
                "success": False,
                "error": "Invalid signal: missing required fields, empty diagnosed_cause, or empty subgraph"
            }
        
        # Verify signature and origin node key status (covers subgraph now)
        if not self.validate_signal_signature(signal):
            return {
                "success": False,
                "error": "Signal signature verification failed or origin node not active"
            }
        
        # Log signal (append-only)
        self.log_signal(signal)
        
        # Update edge exchange counts for edges in subgraph
        self.update_edge_exchanges(signal['origin_kr'], subgraph, signal)
        
        return {
            "success": True,
            "subgraph": list(subgraph),
            "signal_id": signal['id'],
            "nodes_notified": len(subgraph)
        }
    
    def _propagate_deck_request(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propagate a deck_request signal.
        
        Expects signal to contain:
        - 'event': 'deck_request'
        - 'origin_kr': the KR that triggered the deck request
        - 'decision_ref': reference to the joint decision
        - 'participating_departments': list of department node IDs
        - 'deck_ref': deck identifier
        """
        # Validate required fields
        required = ['id', 'origin_kr', 'event', 'decision_ref', 'participating_departments', 'deck_ref', 'fired_at']
        for field in required:
            if field not in signal:
                return {
                    "success": False,
                    "error": f"deck_request missing required field: {field}"
                }
        
        if signal['event'] != 'deck_request':
            return {
                "success": False,
                "error": "Invalid event type for deck_request"
            }
        
        # Verify signature
        if not self.validate_signal_signature(signal):
            return {
                "success": False,
                "error": "Signal signature verification failed or origin node not active"
            }
        
        # Compute subgraph for each participating department
        all_subgraphs = {}
        for dept in signal['participating_departments']:
            all_subgraphs[dept] = list(self.compute_subgraph(dept))
        
        # Log signal
        self.log_signal(signal)
        
        return {
            "success": True,
            "signal_type": "deck_request",
            "signal_id": signal['id'],
            "decision_ref": signal['decision_ref'],
            "deck_ref": signal['deck_ref'],
            "participating_departments": signal['participating_departments'],
            "subgraphs": all_subgraphs,
            "nodes_notified": sum(len(sg) for sg in all_subgraphs.values())
        }
    
    def log_signal(self, signal: Dict[str, Any]) -> None:
        """Append signal to log file."""
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(signal) + '\n')
    
    def update_edge_exchanges(self, origin_kr: str, subgraph: Set[str], signal: Optional[Dict[str, Any]] = None) -> None:
        """Update exchange counts for edges involved in signal propagation using real flow signals.
        
        Args:
            origin_kr: The origin KR of the signal
            subgraph: The set of KRs in the propagation subgraph
            signal: The signal that was propagated (used to determine delivery_confirmed)
        """
        # For edges from origin to subgraph nodes, mark as reciprocal if both directions exist
        # For edges within subgraph that were traversed, mark appropriately
        adj = self.build_adjacency()
        
        # Derive delivery_confirmed from signal kind
        # failure signals mean the edge failed - should NOT reinforce
        delivery_confirmed = True
        if signal and signal.get('signal_kind') == 'failure':
            delivery_confirmed = False
        
        for kr in subgraph:
            if kr == origin_kr:
                continue
            # Check if edge exists from origin to this node
            for edge_key, edge in self.edges.items():
                if edge['from'] == origin_kr and edge['to'] == kr:
                    # This edge was used for propagation - compute REAL flow signal
                    # based on whether the dependency was actually delivered/confirmed
                    flow_signal = compute_flow_signal(
                        edge, 
                        delivery_confirmed=delivery_confirmed,
                        partial_delivery=0.0
                    )
                    
                    # Apply reinforcement with real flow signal
                    updated_edge = reinforce(edge, flow_signal)
                    self.edges[edge_key] = updated_edge
        
        # Persist the edge updates
        self.save_edges()
    
    def get_signals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent signals from log."""
        signals = []
        if self.log_path.exists():
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        signals.append(json.loads(line))
        return signals[-limit:]
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all edges."""
        return list(self.edges.values())
    
    def get_edge(self, from_kr: str, to_kr: str) -> Optional[Dict[str, Any]]:
        """Get edge by from/to KR."""
        return self.edges.get(self.edge_key(from_kr, to_kr))


def main():
    """CLI for propagation operations."""
    import sys
    propagator = SignalPropagator(
        "mycelium/graph/edges.json",
        "mycelium/log/signals.jsonl",
        registry_path="mycelium/registry/nodes.json"
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