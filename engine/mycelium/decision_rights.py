"""
Decision Rights Gating - Filters MYCELIUM signal propagation by Decision Rights.

Decision Rights (from STRATEGY stage output):
- OWN: Makes the final decision (only one per decision)
- RECOMMEND: Makes recommendation to owner
- CONSULT: Provides input before decision
- EXECUTE: Implements the decision
- APPROVE: Approves/rejects the decision
- ESCALATE: Can escalate the decision
- AUTOMATE: Automated decision (no human in loop)
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field


class DecisionRight(str, Enum):
    OWN = "OWN"
    RECOMMEND = "RECOMMEND"
    CONSULT = "CONSULT"
    EXECUTE = "EXECUTE"
    APPROVE = "APPROVE"
    ESCALATE = "ESCALATE"
    AUTOMATE = "AUTOMATE"


class SignalType(str, Enum):
    """Types of signals in MYCELIUM."""
    FAILURE = "failure"
    DECK_REQUEST = "deck_request"
    ONTOLOGY_CHANGE = "ontology_change"
    ESCALATION = "escalation"
    COORDINATION = "coordination"
    REQUEST = "request"


# Decision Rights required for each signal type
# Maps signal_type -> { node_role: required_decision_rights }
SIGNAL_DECISION_RIGHTS = {
    SignalType.FAILURE: {
        "origin": {DecisionRight.OWN, DecisionRight.ESCALATE},
        "target": {DecisionRight.CONSULT, DecisionRight.EXECUTE, DecisionRight.APPROVE},
    },
    SignalType.DECK_REQUEST: {
        "origin": {DecisionRight.OWN, DecisionRight.RECOMMEND},
        "target": {DecisionRight.CONSULT, DecisionRight.EXECUTE, DecisionRight.APPROVE},
    },
    SignalType.ONTOLOGY_CHANGE: {
        "origin": {DecisionRight.OWN, DecisionRight.APPROVE},
        "target": {DecisionRight.CONSULT, DecisionRight.APPROVE},
    },
    SignalType.ESCALATION: {
        "origin": {DecisionRight.OWN, DecisionRight.ESCALATE},
        "target": {DecisionRight.APPROVE, DecisionRight.ESCALATE},
    },
    SignalType.COORDINATION: {
        "origin": {DecisionRight.RECOMMEND, DecisionRight.CONSULT},
        "target": {DecisionRight.CONSULT, DecisionRight.EXECUTE},
    },
    SignalType.REQUEST: {
        "origin": {DecisionRight.OWN, DecisionRight.RECOMMEND},
        "target": {DecisionRight.CONSULT, DecisionRight.EXECUTE, DecisionRight.APPROVE},
    },
}


@dataclass
class DecisionRightsGate:
    """Gate that filters signal recipients by Decision Rights."""
    
    # node_id -> DecisionRight (from STRATEGY output)
    node_rights: Dict[str, DecisionRight] = field(default_factory=dict)
    
    def set_node_right(self, node_id: str, right: DecisionRight) -> None:
        """Record the Decision Right for a node (from STRATEGY output)."""
        self.node_rights[node_id] = right
    
    def get_node_right(self, node_id: str) -> Optional[DecisionRight]:
        """Get the Decision Right for a node."""
        return self.node_rights.get(node_id)
    
    def filter_recipients(
        self,
        signal_type: SignalType,
        origin_kr: str,
        candidate_recipients: Set[str],
        role: str = "target"
    ) -> Set[str]:
        """
        Filter candidate recipients based on Decision Rights.
        
        Args:
            signal_type: Type of signal being sent
            origin_kr: Origin KR ID
            candidate_recipients: Set of candidate recipient node IDs
            role: "origin" or "target" - which role to check
            
        Returns:
            Filtered set of recipients who have appropriate Decision Rights
        """
        required_rights = SIGNAL_DECISION_RIGHTS.get(signal_type, {}).get(role, set())
        
        if not required_rights:
            # No specific rights required - allow all
            return candidate_recipients
        
        filtered = set()
        for node_id in candidate_recipients:
            node_right = self.node_rights.get(node_id)
            if node_right in required_rights:
                filtered.add(node_id)
        
        return filtered
    
    def validate_origin_right(self, signal_type: SignalType, origin_kr: str) -> bool:
        """Validate that the origin node has appropriate Decision Rights."""
        required = SIGNAL_DECISION_RIGHTS.get(signal_type, {}).get("origin", set())
        if not required:
            return True
        
        origin_right = self.node_rights.get(origin_kr)
        return origin_right in required


# Convenience function for propagator integration
def gate_subgraph_by_decision_rights(
    propagator,
    signal_type: SignalType,
    origin_kr: str,
    subgraph: Set[str],
    node_registry: Any,
) -> Set[str]:
    """
    Filter a subgraph by Decision Rights.
    
    Reads Decision Rights from node registry (stored from STRATEGY output).
    """
    gate = DecisionRightsGate()
    
    # Load rights from registry
    for node_id in subgraph:
        node = node_registry.get_node(node_id) if node_registry else None
        if node and "decision_rights" in node:
            # decision_rights is a dict with 'own', 'consult', 'inform' keys
            # The primary right is in 'decision_right' field or 'own' in decision_rights
            primary_right = node.get('decision_right') or node['decision_rights'].get('own')
            if primary_right:
                gate.set_node_right(node_id, DecisionRight(primary_right))
    
    return gate.filter_recipients(signal_type, origin_kr, subgraph, role="target")


if __name__ == "__main__":
    # Quick test
    gate = DecisionRightsGate()
    
    # Set up some nodes with rights
    gate.set_node_right("Marketing.Head", DecisionRight.OWN)
    gate.set_node_right("Marketing.Growth", DecisionRight.RECOMMEND)
    gate.set_node_right("Marketing.Analytics", DecisionRight.CONSULT)
    gate.set_node_right("Sales.Head", DecisionRight.APPROVE)
    gate.set_node_right("Sales.Rep", DecisionRight.EXECUTE)
    
    candidates = {"Marketing.Head", "Marketing.Growth", "Marketing.Analytics", "Sales.Head", "Sales.Rep"}
    
    # Test deck_request - origin needs OWN/RECOMMEND, targets need CONSULT/EXECUTE/APPROVE
    filtered = gate.filter_recipients(SignalType.DECK_REQUEST, "Marketing.Head", candidates, "target")
    print(f"DECK_REQUEST targets: {filtered}")
    assert "Marketing.Analytics" in filtered  # CONSULT
    assert "Sales.Head" in filtered  # APPROVE
    assert "Sales.Rep" in filtered  # EXECUTE
    assert "Marketing.Growth" not in filtered  # RECOMMEND not in target set
    assert "Marketing.Head" not in filtered  # OWN not in target set
    
    # Test failure signal
    filtered = gate.filter_recipients(SignalType.FAILURE, "Marketing.Head", candidates, "target")
    print(f"FAILURE targets: {filtered}")
    
    # Test origin validation
    assert gate.validate_origin_right(SignalType.DECK_REQUEST, "Marketing.Head")  # OWN
    assert gate.validate_origin_right(SignalType.DECK_REQUEST, "Marketing.Growth")  # RECOMMEND
    assert not gate.validate_origin_right(SignalType.DECK_REQUEST, "Marketing.Analytics")  # CONSULT
    print("All tests passed!")