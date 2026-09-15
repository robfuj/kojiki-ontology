#!/usr/bin/env python3
"""
Governance → Ontology Loop Closure

Receives approved L3/L4 governance signals from NEURAXIS and applies
the actual ontology/meta-strategy changes to MYCELIUM registry and engine configs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass

# Import engine components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from registry import NodeRegistry
from sentinel import SentinelEngine, KeyManager, canonical_json, verify_signature


class ChangeType(Enum):
    ADD_NODE = "add_node"
    UPDATE_DECISION_RIGHTS = "update_decision_rights"
    UPDATE_EDGE_WEIGHT = "update_edge_weight"
    REMOVE_NODE = "remove_node"
    UPDATE_ESCALATION_MAP = "update_escalation_map"
    UPDATE_THRESHOLD = "update_threshold"
    UPDATE_AUTONOMOUS_LAYERS = "update_autonomous_layers"
    UPDATE_GOVERNANCE_LAYERS = "update_governance_layers"


@dataclass
class OntologyChange:
    """Structured representation of an ontology/meta-strategy change."""
    change_type: ChangeType
    target: str  # node_id, edge_key, or config key
    payload: Dict[str, Any]
    reason: str
    gate_id: str
    approver: str
    timestamp: str


class GovernanceHandler:
    """
    Handles APPROVED governance signals and applies the actual changes.
    
    This closes the loop: Governance decision → Signal → Ontology Mutation.
    """
    
    def __init__(
        self,
        registry: NodeRegistry,
        edge_store_path: str,
        escalation_engine=None,
        sentinel: Optional[SentinelEngine] = None
    ):
        self.registry = registry
        self.edge_store_path = Path(edge_store_path)
        self.escalation_engine = escalation_engine
        self.sentinel = sentinel or SentinelEngine(str(registry.registry_path.parent))
        self.key_manager = registry.key_manager
        
        # Load edge store
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.load_edges()
        
        # Track applied changes for audit
        self.changes_log_path = self.registry.registry_path.parent / "governance_changes.jsonl"
        self.changes_log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.changes_log_path.exists():
            self.changes_log_path.touch()
    
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
    
    def edge_key(self, from_kr: str, to_kr: str) -> str:
        return f"{from_kr}->{to_kr}"
    
    def handle_governance_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an approved governance signal and apply the change.
        
        Expected signal fields:
        - event: "ontology_change" or "meta_strategy_change"
        - diagnosed_cause: "Governance approved: <proposed_change>"
        - subgraph: list of affected nodes
        - signal_kind: "failure" (governance decisions are failure-kind signals)
        - origin_kr: "GOVERNANCE"
        """
        event = signal.get('event')
        if event not in ('ontology_change', 'meta_strategy_change'):
            return {"success": False, "error": f"Unknown governance event: {event}"}
        
        # Verify signal signature (GOVERNANCE origin)
        if not self._verify_governance_signal(signal):
            return {"success": False, "error": "Governance signal signature verification failed"}
        
        # Extract change details from signal
        cause = signal.get('diagnosed_cause', '')
        if not cause.startswith('Governance '):
            return {"success": False, "error": "Invalid governance signal format"}
        
        # Parse the proposed change from the cause string
        # Format: "Governance approved: Revise ontology based on EXP-..."
        change_desc = cause.split(':', 1)[1].strip() if ':' in cause else cause
        
        # Determine change type from subgraph and signal
        subgraph = signal.get('subgraph', [])
        
        if event == 'ontology_change':
            return self._apply_ontology_change(signal, change_desc, subgraph)
        else:
            return self._apply_meta_strategy_change(signal, change_desc, subgraph)
    
    def _verify_governance_signal(self, signal: Dict[str, Any]) -> bool:
        """Verify the GOVERNANCE signal signature using SENTINEL."""
        if 'signature' not in signal:
            # Fail closed - no signature means invalid
            return False
        
        origin = signal.get('origin_kr')
        if origin != 'GOVERNANCE':
            return False
        
        # Verify signature using GOVERNANCE node's public key
        # The signed data is the signal without the signature field
        signal_data = {k: v for k, v in signal.items() if k != 'signature'}
        data_str = canonical_json(signal_data)
        
        # Get GOVERNANCE public key from registry
        governance_node = self.registry.get_node('GOVERNANCE')
        if not governance_node:
            # In production, GOVERNANCE node must exist
            return False
        
        public_key = governance_node.get('public_key')
        if not public_key:
            return False
        
        signature = signal.get('signature')
        if not signature:
            return False
        return verify_signature(signature, data_str, public_key)
    
    def _apply_ontology_change(self, signal: Dict[str, Any], change_desc: str, subgraph: List[str]) -> Dict[str, Any]:
        """Apply an L3 ontology change."""
        
        # Parse the change description to extract structured intent
        # For now, support a structured format embedded in the signal
        # In production, the gate request should include structured change_spec
        
        change_spec = signal.get('change_spec')
        if not change_spec:
            # Fallback: infer from subgraph and signal
            change_spec = self._infer_ontology_change(change_desc, subgraph)
        
        results = []
        for change in change_spec:
            # Use "change_type" field for the ChangeType enum
            # (to avoid conflict with node "type" field in change_spec)
            change_type_val = change.get('change_type')
            if change_type_val is None:
                return {"success": False, "error": "change_type field required in change_spec"}
            change_type = ChangeType(change_type_val)
            
            if change_type == ChangeType.ADD_NODE:
                result = self._add_node(change)
            elif change_type == ChangeType.UPDATE_DECISION_RIGHTS:
                result = self._update_decision_rights(change)
            elif change_type == ChangeType.UPDATE_EDGE_WEIGHT:
                result = self._update_edge_weight(change)
            elif change_type == ChangeType.REMOVE_NODE:
                result = self._remove_node(change)
            else:
                result = {"success": False, "error": f"Unknown change type: {change_type}"}
            
            results.append(result)
            
            # Log the change
            self._log_change(OntologyChange(
                change_type=change_type,
                target=change.get('target', ''),
                payload=change,
                reason=signal.get('diagnosed_cause', ''),
                gate_id=signal.get('id', ''),
                approver=signal.get('approver', 'GOVERNANCE'),
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        return {
            "success": all(r.get('success', False) for r in results),
            "changes_applied": len([r for r in results if r.get('success')]),
            "results": results
        }
    
    def _apply_meta_strategy_change(self, signal: Dict[str, Any], change_desc: str, subgraph: List[str]) -> Dict[str, Any]:
        """Apply an L4 meta-strategy change."""
        
        if not self.escalation_engine:
            return {"success": False, "error": "No escalation engine available for meta-strategy changes"}
        
        change_spec = signal.get('change_spec')
        if not change_spec:
            change_spec = self._infer_meta_strategy_change(change_desc, subgraph)
        
        results = []
        for change in change_spec:
            # Use "change_type" field for the ChangeType enum
            # (to avoid conflict with node "type" field in change_spec)
            change_type_val = change.get('change_type')
            if change_type_val is None:
                return {"success": False, "error": "change_type field required in change_spec"}
            change_type = ChangeType(change_type_val)
            
            if change_type == ChangeType.UPDATE_ESCALATION_MAP:
                result = self._update_escalation_map(change)
            elif change_type == ChangeType.UPDATE_THRESHOLD:
                result = self._update_threshold(change)
            elif change_type == ChangeType.UPDATE_AUTONOMOUS_LAYERS:
                result = self._update_autonomous_layers(change)
            elif change_type == ChangeType.UPDATE_GOVERNANCE_LAYERS:
                result = self._update_governance_layers(change)
            else:
                result = {"success": False, "error": f"Unknown meta-strategy change type: {change_type}"}
            
            results.append(result)
            
            self._log_change(OntologyChange(
                change_type=change_type,
                target=change.get('target', ''),
                payload=change,
                reason=signal.get('diagnosed_cause', ''),
                gate_id=signal.get('id', ''),
                approver=signal.get('approver', 'GOVERNANCE'),
                timestamp=datetime.utcnow().isoformat() + 'Z'
            ))
        
        return {
            "success": all(r.get('success', False) for r in results),
            "changes_applied": len([r for r in results if r.get('success')]),
            "results": results
        }
    
    def _infer_ontology_change(self, change_desc: str, subgraph: List[str]) -> List[Dict]:
        """Infer ontology change from description (fallback for unstructured gates)."""
        # Heuristic: if subgraph has new nodes not in registry, they're being added
        new_nodes = [n for n in subgraph if n not in self.registry.nodes]
        changes = []
        
        for node_id in new_nodes:
            parts = node_id.split('.')
            parent_id = '.'.join(parts[:-1]) if len(parts) > 1 else None
            changes.append({
                "change_type": ChangeType.ADD_NODE.value,
                "target": node_id,
                "node_id": node_id,
                "parent": parent_id,
                "domain": node_id.lower().replace('.', '/'),
                "node_type": "agent"  # Use node_type to match _add_node expectation
            })
        
        # If no new nodes, assume decision rights update
        if not changes and subgraph:
            for node_id in subgraph:
                if node_id in self.registry.nodes:
                    changes.append({
                        "change_type": ChangeType.UPDATE_DECISION_RIGHTS.value,
                        "target": node_id,
                        "node_id": node_id,
                        "decision_rights": {
                            "own": node_id,
                            "consult": [],
                            "inform": []
                        }
                    })
        
        return changes
    
    def _infer_meta_strategy_change(self, change_desc: str, subgraph: List[str]) -> List[Dict]:
        """Infer meta-strategy change from description."""
        # Default: no-op for unstructured
        return []
    
    def _add_node(self, change: Dict) -> Dict[str, Any]:
        """Add a new node to the registry via registry.register_node_governance()."""
        node_id = change.get('node_id') or change.get('target')
        parent_id = change.get('parent')
        domain = change.get('domain', node_id.lower().replace('.', '/'))
        node_type = change.get('node_type', 'agent')
        
        if not node_id:
            return {"success": False, "error": "node_id required"}
        
        # Governance uses register_node_governance which bypasses parent signature
        # but still validates lineage and reject-not-overwrite
        try:
            success = self.registry.register_node_governance(
                node_id=node_id,
                domain=domain,
                node_type=node_type,
                parent_id=parent_id
            )
            
            if not success:
                return {"success": False, "error": f"Failed to register node {node_id}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        # Emit SENTINEL event
        self.sentinel.write_node_lifecycle_event(
            'registration_approved', node_id, 'GOVERNANCE', 
            {"governance_initiated": True, "parent": parent_id}
        )
        
        return {"success": True, "node_id": node_id, "action": "added"}
    
    def _update_decision_rights(self, change: Dict) -> Dict[str, Any]:
        """Update Decision Rights for a node."""
        node_id = change.get('node_id') or change.get('target')
        decision_rights = change.get('decision_rights')
        
        if not node_id or not decision_rights:
            return {"success": False, "error": "node_id and decision_rights required"}
        
        success = self.registry.update_decision_rights(node_id, decision_rights)
        
        return {"success": success, "node_id": node_id, "action": "decision_rights_updated"}
    
    def _update_edge_weight(self, change: Dict) -> Dict[str, Any]:
        """Update edge weight in the edge store."""
        from_kr = change.get('from')
        to_kr = change.get('to')
        weight = change.get('weight')
        
        if not from_kr or not to_kr or weight is None:
            return {"success": False, "error": "from, to, and weight required"}
        
        key = self.edge_key(from_kr, to_kr)
        
        if key not in self.edges:
            self.edges[key] = {
                "from": from_kr,
                "to": to_kr,
                "weight": weight,
                "reciprocal_exchanges": 0,
                "one_directional_exchanges": 0,
                "last_reinforced": datetime.utcnow().isoformat() + 'Z'
            }
        else:
            self.edges[key]["weight"] = weight
            self.edges[key]["last_reinforced"] = datetime.utcnow().isoformat() + 'Z'
        
        self.save_edges()
        
        return {"success": True, "edge": key, "weight": weight, "action": "edge_updated"}
    
    def _remove_node(self, change: Dict) -> Dict[str, Any]:
        """Remove a node (mark as deprecated)."""
        node_id = change.get('node_id') or change.get('target')
        
        if not node_id or node_id not in self.registry.nodes:
            return {"success": False, "error": "node_id not found"}
        
        # Don't actually delete - mark as deprecated
        self.registry.nodes[node_id]["status"] = "deprecated"
        self.registry.nodes[node_id]["key_status"] = "revoked"
        self.registry.nodes[node_id]["key_revoked_at"] = datetime.utcnow().isoformat() + 'Z'
        self.registry.save()
        
        self.sentinel.write_node_lifecycle_event(
            'node_deprecated', node_id, 'GOVERNANCE', {}
        )
        
        return {"success": True, "node_id": node_id, "action": "deprecated"}
    
    def _update_escalation_map(self, change: Dict) -> Dict[str, Any]:
        """Update the ESCALATION_MAP in escalation engine."""
        if not self.escalation_engine:
            return {"success": False, "error": "No escalation engine"}
        
        mapping = change.get('mapping')  # {error_class: layer}
        if not mapping:
            return {"success": False, "error": "mapping required"}
        
        # Validate and apply the mapping
        try:
            from escalation import ErrorClass, Layer, ESCALATION_MAP
            new_map = {}
            for error_class_str, layer_str in mapping.items():
                error_class = ErrorClass(error_class_str)
                layer = Layer(layer_str)
                new_map[error_class] = layer
            
            # Update the engine's ESCALATION_MAP in place
            self.escalation_engine.ESCALATION_MAP.clear()
            self.escalation_engine.ESCALATION_MAP.update(new_map)
            
            # Also update the global ESCALATION_MAP for any new instances
            ESCALATION_MAP.clear()
            ESCALATION_MAP.update(new_map)
            
            # Persist to a config file
            config_path = self.edge_store_path.parent / "escalation_config.json"
            with open(config_path, 'w') as f:
                json.dump({
                    "escalation_map": {k.value: v.value for k, v in new_map.items()},
                    "autonomous_layers": [l.value for l in self.escalation_engine.AUTONOMOUS_LAYERS],
                    "governance_layers": [l.value for l in self.escalation_engine.GOVERNANCE_LAYERS]
                }, f, indent=2)
            
            return {"success": True, "action": "escalation_map_updated", "mapping": {k.value: v.value for k, v in new_map.items()}}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_threshold(self, change: Dict) -> Dict[str, Any]:
        """Update the subgraph threshold."""
        threshold = change.get('threshold')
        if threshold is None:
            return {"success": False, "error": "threshold required"}
        
        # Update in propagation engine
        try:
            # The threshold is used by SignalPropagator
            # We need to update it in the propagator if available
            if self.escalation_engine and hasattr(self.escalation_engine, 'mycelium_propagator') and self.escalation_engine.mycelium_propagator:
                propagator = self.escalation_engine.mycelium_propagator
                if hasattr(propagator, 'threshold'):
                    old_threshold = propagator.threshold
                    propagator.threshold = float(threshold)
                    
                    # Persist to config
                    config_path = self.edge_store_path.parent / "propagator_config.json"
                    with open(config_path, 'w') as f:
                        json.dump({
                            "threshold": propagator.threshold
                        }, f, indent=2)
                    
                    return {"success": True, "action": "threshold_updated", "old_threshold": old_threshold, "new_threshold": propagator.threshold}
            
            # If no propagator, just persist the config
            config_path = self.edge_store_path.parent / "propagator_config.json"
            with open(config_path, 'w') as f:
                json.dump({"threshold": float(threshold)}, f, indent=2)
            
            return {"success": True, "action": "threshold_config_saved", "threshold": threshold}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_autonomous_layers(self, change: Dict) -> Dict[str, Any]:
        """Update autonomous layers set."""
        layers = change.get('layers')  # list of layer names
        if not layers:
            return {"success": False, "error": "layers required"}
        
        try:
            from escalation import Layer, AUTONOMOUS_LAYERS
            new_layers = {Layer(l) for l in layers}
            
            # Update the engine's AUTONOMOUS_LAYERS in place
            if self.escalation_engine:
                self.escalation_engine.AUTONOMOUS_LAYERS.clear()
                self.escalation_engine.AUTONOMOUS_LAYERS.update(new_layers)
            
            # Also update the global for new instances
            AUTONOMOUS_LAYERS.clear()
            AUTONOMOUS_LAYERS.update(new_layers)
            
            # Persist to config
            config_path = self.edge_store_path.parent / "escalation_config.json"
            with open(config_path, 'w') as f:
                json.dump({
                    "autonomous_layers": [l.value for l in new_layers],
                    "governance_layers": [l.value for l in (self.escalation_engine.GOVERNANCE_LAYERS if self.escalation_engine else set())],
                    "escalation_map": {k.value: v.value for k, v in (self.escalation_engine.ESCALATION_MAP if self.escalation_engine else {}).items()}
                }, f, indent=2)
            
            return {"success": True, "action": "autonomous_layers_updated", "layers": [l.value for l in new_layers]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_governance_layers(self, change: Dict) -> Dict[str, Any]:
        """Update governance layers set."""
        layers = change.get('layers')
        if not layers:
            return {"success": False, "error": "layers required"}
        
        try:
            from escalation import Layer, GOVERNANCE_LAYERS
            new_layers = {Layer(l) for l in layers}
            
            # Update the engine's GOVERNANCE_LAYERS in place
            if self.escalation_engine:
                self.escalation_engine.GOVERNANCE_LAYERS.clear()
                self.escalation_engine.GOVERNANCE_LAYERS.update(new_layers)
            
            # Also update the global for new instances
            GOVERNANCE_LAYERS.clear()
            GOVERNANCE_LAYERS.update(new_layers)
            
            # Persist to config
            config_path = self.edge_store_path.parent / "escalation_config.json"
            with open(config_path, 'w') as f:
                json.dump({
                    "autonomous_layers": [l.value for l in (self.escalation_engine.AUTONOMOUS_LAYERS if self.escalation_engine else set())],
                    "governance_layers": [l.value for l in new_layers],
                    "escalation_map": {k.value: v.value for k, v in (self.escalation_engine.ESCALATION_MAP if self.escalation_engine else {}).items()}
                }, f, indent=2)
            
            return {"success": True, "action": "governance_layers_updated", "layers": [l.value for l in new_layers]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_change(self, change: OntologyChange) -> None:
        """Log the applied change for audit."""
        with open(self.changes_log_path, 'a') as f:
            f.write(json.dumps({
                "change_type": change.change_type.value,
                "target": change.target,
                "payload": change.payload,
                "reason": change.reason,
                "gate_id": change.gate_id,
                "approver": change.approver,
                "timestamp": change.timestamp
            }) + "\n")


def main():
    """CLI for testing governance handler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Governance Handler")
    parser.add_argument("--registry", default="mycelium/registry/nodes.json")
    parser.add_argument("--edges", default="mycelium/engine/edges.json")
    parser.add_argument("--signal", help="Signal JSON file")
    args = parser.parse_args()
    
    registry = NodeRegistry(args.registry)
    handler = GovernanceHandler(registry, args.edges)
    
    if args.signal:
        with open(args.signal) as f:
            signal = json.load(f)
        result = handler.handle_governance_signal(signal)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python governance_handler.py --signal <signal.json>")


if __name__ == "__main__":
    main()