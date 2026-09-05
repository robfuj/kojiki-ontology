"""
NEURAXIS Escalation Engine - Vertical axis for recursive problem redefinition.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict


class ErrorClass(Enum):
    INFORMATION_ERROR = "Information error"
    EXECUTION_ERROR = "Execution error"
    REASONING_ERROR = "Reasoning error"
    ASSUMPTION_ERROR = "Assumption error"
    MODEL_REPRESENTATION_ERROR = "Model/representation error"
    META_ERROR = "Meta error"


class Layer(Enum):
    L0_EXECUTION = "L0_execution"
    L1_REASONING = "L1_reasoning"
    L2_PROBLEM_REPRESENTATION = "L2_problem_representation"
    L3_ONTOLOGY = "L3_ontology"
    L4_META_STRATEGY = "L4_meta_strategy"


ESCALATION_MAP = {
    ErrorClass.INFORMATION_ERROR: Layer.L0_EXECUTION,
    ErrorClass.EXECUTION_ERROR: Layer.L0_EXECUTION,
    ErrorClass.REASONING_ERROR: Layer.L1_REASONING,
    ErrorClass.ASSUMPTION_ERROR: Layer.L2_PROBLEM_REPRESENTATION,
    ErrorClass.MODEL_REPRESENTATION_ERROR: Layer.L3_ONTOLOGY,
    ErrorClass.META_ERROR: Layer.L4_META_STRATEGY,
}

# Layers that can revise autonomously vs require governance
AUTONOMOUS_LAYERS = {Layer.L0_EXECUTION, Layer.L1_REASONING, Layer.L2_PROBLEM_REPRESENTATION}
GOVERNANCE_LAYERS = {Layer.L3_ONTOLOGY, Layer.L4_META_STRATEGY}


@dataclass
class Experience:
    """An experience record - causal trace from hypothesis to diagnosis."""
    id: str
    problem_id: str
    hypothesis: str
    agents: List[str]
    action: str
    expected: str
    observed: str
    error_classification: str
    escalation: Dict[str, str]
    redefinition: Optional[Dict[str, str]] = None
    learning_ref: Optional[str] = None
    propagation_targets: List[str] = []


@dataclass
class Problem:
    """A versioned, mutable problem representation with lineage."""
    id: str
    supersedes: str
    reason: str
    goal: str
    constraints: List[str]
    assumptions: List[str]
    unknowns: List[str]


@dataclass
class GateRequest:
    """Governance gate request for L3/L4 changes."""
    id: str
    layer: str
    proposed_change: str
    evidence: Dict[str, Any]
    recommend: str
    consult: List[str]
    approve_role: str
    sla_deadline: str
    status: str = "PENDING"
    decision_reason: Optional[str] = None
    applied_at: Optional[str] = None


class EscalationEngine:
    """Core NEURAXIS engine for classifying failures and managing escalation."""
    
    def __init__(self, 
                 experience_log_path: str,
                 problem_store_path: str,
                 gate_request_path: str,
                 mycelium_propagator=None):
        self.experience_log_path = Path(experience_log_path)
        self.problem_store_path = Path(problem_store_path)
        self.gate_request_path = Path(gate_request_path)
        self.mycelium_propagator = mycelium_propagator
        
        self.experiences: List[Experience] = []
        self.problems: Dict[str, Problem] = {}
        self.gate_requests: Dict[str, GateRequest] = {}
        
        self._ensure_files()
        self.load()
    
    def _ensure_files(self) -> None:
        for path in [self.experience_log_path, self.problem_store_path, self.gate_request_path]:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text('[]')
    
    def load(self) -> None:
        """Load all stores."""
        for path, attr in [
            (self.experience_log_path, 'experiences'),
            (self.problem_store_path, 'problems'),
            (self.gate_request_path, 'gate_requests')
        ]:
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                    if attr == 'experiences':
                        self.experiences = [Experience(**e) for e in data]
                    elif attr == 'problems':
                        self.problems = {p['id']: Problem(**p) for p in data}
                    elif attr == 'gate_requests':
                        self.gate_requests = {g['id']: GateRequest(**g) for g in data}
    
    def save_experiences(self) -> None:
        with open(self.experience_log_path, 'w') as f:
            json.dump([asdict(e) for e in self.experiences], f, indent=2)
    
    def save_problems(self) -> None:
        with open(self.problem_store_path, 'w') as f:
            json.dump([asdict(p) for p in self.problems.values()], f, indent=2)
    
    def save_gate_requests(self) -> None:
        with open(self.gate_request_path, 'w') as f:
            json.dump([asdict(g) for g in self.gate_requests.values()], f, indent=2)
    
    def classify_error(self, expected: str, observed: str, context: Dict[str, Any]) -> ErrorClass:
        """
        Classify the error based on expected vs observed and context.
        
        This is a simplified classifier - in practice this would use more sophisticated
        analysis of the failure mode.
        """
        # Check for missing/incorrect data
        if 'missing_data' in context or 'incorrect_data' in context:
            return ErrorClass.INFORMATION_ERROR
        
        # Check for implementation failure
        if context.get('reasoning_valid', True) and not context.get('implementation_correct', True):
            return ErrorClass.EXECUTION_ERROR
        
        # Check for invalid inference
        if not context.get('reasoning_valid', True):
            return ErrorClass.REASONING_ERROR
        
        # Check for assumption failure
        if context.get('assumption_invalid', False):
            return ErrorClass.ASSUMPTION_ERROR
        
        # Check for repeated contradictions (model/representation error)
        similar_failures = self._count_similar_failures(context.get('problem_id', ''))
        if similar_failures >= 3:
            return ErrorClass.MODEL_REPRESENTATION_ERROR
        
        # Check for meta error (repeated inappropriate representations)
        if context.get('repeated_representation_issues', 0) >= 2:
            return ErrorClass.META_ERROR
        
        # Default to reasoning error
        return ErrorClass.REASONING_ERROR
    
    def _count_similar_failures(self, problem_id: str) -> int:
        """Count experiences with same problem_id and same error classification."""
        count = 0
        for exp in self.experiences:
            if exp.problem_id == problem_id and exp.error_classification == ErrorClass.MODEL_REPRESENTATION_ERROR.value:
                count += 1
        return count
    
    def escalate(self, experience: Experience) -> Dict[str, Any]:
        """
        Process an experience through the escalation ladder.
        
        Returns escalation result with actions taken.
        """
        error_class = ErrorClass(experience.error_classification)
        target_layer = ESCALATION_MAP[error_class]
        
        result = {
            "experience_id": experience.id,
            "error_class": error_class.value,
            "target_layer": target_layer.value,
            "actions": [],
            "gate_request_id": None
        }
        
        # Log the experience
        self.experiences.append(experience)
        self.save_experiences()
        
        if target_layer in AUTONOMOUS_LAYERS:
            # Autonomous revision
            result["actions"].append(f"Autonomous revision at {target_layer.value}")
            if target_layer == Layer.L2_PROBLEM_REPRESENTATION:
                # Create new problem version
                new_problem = self._create_superseding_problem(experience)
                result["new_problem_id"] = new_problem.id
                result["actions"].append(f"Created superseding problem: {new_problem.id}")
        else:
            # Requires governance gate
            gate_request = self._create_gate_request(experience, target_layer)
            self.gate_requests[gate_request.id] = gate_request
            self.save_gate_requests()
            result["gate_request_id"] = gate_request.id
            result["actions"].append(f"Gate request created for {target_layer.value}: {gate_request.id}")
        
        return result
    
    def _create_superseding_problem(self, experience: Experience) -> Problem:
        """Create a new problem version superseding the old one."""
        old_problem = self.problems.get(experience.problem_id)
        if not old_problem:
            # Create base problem
            new_problem = Problem(
                id=experience.redefinition['new_problem'] if experience.redefinition else f"P-{len(self.problems)+1:04d}",
                supersedes=experience.problem_id,
                reason=experience.redefinition.get('reason', f"Invalidated by {experience.id}") if experience.redefinition else f"Invalidated by {experience.id}",
                goal=context.get('goal', '') if (context := {}) else '',
                constraints=[],
                assumptions=[],
                unknowns=[]
            )
        else:
            # Build on old problem with revised assumptions
            new_problem = Problem(
                id=experience.redefinition['new_problem'] if experience.redefinition else f"{old_problem.id}-v{len([p for p in self.problems if p.startswith(old_problem.id)])+1}",
                supersedes=experience.problem_id,
                reason=experience.redefinition.get('reason', f"Assumption invalidated by {experience.id}") if experience.redefinition else f"Assumption invalidated by {experience.id}",
                goal=old_problem.goal,
                constraints=old_problem.constraints,
                assumptions=[a for a in old_problem.assumptions if a != experience.hypothesis],  # Remove invalidated assumption
                unknowns=old_problem.unknowns + [experience.hypothesis]  # Add as unknown
            )
        
        self.problems[new_problem.id] = new_problem
        self.save_problems()
        return new_problem
    
    def _create_gate_request(self, experience: Experience, target_layer: Layer) -> GateRequest:
        """Create a governance gate request for L3/L4."""
        # Find structurally connected nodes via MYCELIUM
        consult_nodes = []
        if self.mycelium_propagator:
            # This would use the subgraph computation
            pass
        
        gate_id = f"gate-{len(self.gate_requests)+1:04d}"
        sla_deadline = (datetime.utcnow() + timedelta(days=14)).isoformat() + 'Z'  # 2 weeks default
        
        return GateRequest(
            id=gate_id,
            layer=target_layer.value,
            proposed_change=f"Revise {'ontology' if target_layer == Layer.L3_ONTOLOGY else 'meta-strategy'} based on {experience.id}",
            evidence={
                "repetition_count": self._count_similar_failures(experience.problem_id),
                "experience_refs": [experience.id]
            },
            recommend=f"NEURAXIS/{experience.agents[0] if experience.agents else 'unknown'}",
            consult=consult_nodes,
            approve_role="ontology-governance-board" if target_layer == Layer.L3_ONTOLOGY else "meta-strategy-board",
            sla_deadline=sla_deadline
        )
    
    def process_gate_request(self, gate_id: str, decision: str, reason: str, approver: str) -> Dict[str, Any]:
        """
        Process a governance gate decision.
        
        decision: APPROVED, REJECTED, MODIFIED, ESCALATED
        """
        gate = self.gate_requests.get(gate_id)
        if not gate:
            return {"success": False, "error": "Gate request not found"}
        
        if gate.status != "PENDING":
            return {"success": False, "error": f"Gate request already {gate.status}"}
        
        valid_decisions = ["APPROVED", "REJECTED", "MODIFIED", "ESCALATED"]
        if decision not in valid_decisions:
            return {"success": False, "error": f"Invalid decision: {decision}"}
        
        gate.status = decision
        gate.decision_reason = reason
        gate.applied_at = datetime.utcnow().isoformat() + 'Z' if decision in ["APPROVED", "MODIFIED"] else None
        self.save_gate_requests()
        
        # If approved, apply the change and propagate via MYCELIUM
        if decision in ["APPROVED", "MODIFIED"]:
            # Log as learning case
            self._log_governance_decision(gate)
            
            # Propagate through MYCELIUM if available
            if self.mycelium_propagator:
                signal = {
                    "id": f"sig-{gate_id}",
                    "origin_kr": "GOVERNANCE",
                    "event": "ontology_change" if gate.layer == "L3" else "meta_strategy_change",
                    "new_status": "changed",
                    "diagnosed_cause": f"Governance {decision.lower()}: {gate.proposed_change}",
                    "diagnosed_cause_category": "Rule",
                    "status": "ROUTED",
                    "subgraph": gate.consult,
                    "fired_at": datetime.utcnow().isoformat() + 'Z'
                }
                self.mycelium_propagator.propagate(signal)
        
        # Handle SLA expiry (fail-closed)
        elif decision == "EXPIRED" or (datetime.fromisoformat(gate.sla_deadline.replace('Z', '+00:00')) < datetime.utcnow()):
            gate.status = "EXPIRED"
            self.save_gate_requests()
        
        return {"success": True, "gate_id": gate_id, "status": gate.status}
    
    def _log_governance_decision(self, gate: GateRequest) -> None:
        """Log governance decision as a learning case."""
        # This would integrate with the learning ledger
        pass
    
    def check_sla_expiry(self) -> List[str]:
        """Check for expired gate requests (fail-closed default)."""
        expired = []
        now = datetime.utcnow()
        for gate in self.gate_requests.values():
            if gate.status == "PENDING":
                deadline = datetime.fromisoformat(gate.sla_deadline.replace('Z', '+00:00'))
                if deadline < now:
                    gate.status = "EXPIRED"
                    expired.append(gate.id)
        if expired:
            self.save_gate_requests()
        return expired
    
    def should_stop_escalation(self, experience_chain: List[Experience], 
                               info_gain_threshold: float = 0.1) -> bool:
        """
        Termination condition: stop escalating when expected information gain < cost.
        
        Simplified: check if last N experiences at current layer produced no new info.
        """
        if len(experience_chain) < 3:
            return False
        
        # Check if last 3 experiences at same layer had diminishing returns
        last_three = experience_chain[-3:]
        layers = [ESCALATION_MAP[ErrorClass(e.error_classification)] for e in last_three]
        
        # If all at same layer and not escalating further
        if len(set(layers)) == 1 and layers[0] in AUTONOMOUS_LAYERS:
            return True
        
        return False


def main():
    """CLI for NEURAXIS operations."""
    import sys
    
    engine = EscalationEngine(
        "mycelium/neuraxis/log/experiences.jsonl",
        "mycelium/neuraxis/log/problems.json",
        "mycelium/neuraxis/log/gate_requests.json"
    )
    
    if len(sys.argv) < 2:
        print("Usage: python escalation.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "classify":
        if len(sys.argv) < 4:
            print("Usage: python escalation.py classify <expected> <observed> <context_json>")
            return
        expected = sys.argv[2]
        observed = sys.argv[3]
        context = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        error_class = engine.classify_error(expected, observed, context)
        print(f"Error class: {error_class.value}")
        print(f"Target layer: {ESCALATION_MAP[error_class].value}")
    
    elif cmd == "escalate":
        if len(sys.argv) < 3:
            print("Usage: python escalation.py escalate <experience_json>")
            return
        exp_data = json.loads(sys.argv[2])
        experience = Experience(**exp_data)
        result = engine.escalate(experience)
        print(json.dumps(result, indent=2))
    
    elif cmd == "gate-decide":
        if len(sys.argv) < 5:
            print("Usage: python escalation.py gate-decide <gate_id> <decision> <reason> <approver>")
            return
        gate_id = sys.argv[2]
        decision = sys.argv[3]
        reason = sys.argv[4]
        approver = sys.argv[5] if len(sys.argv) > 5 else "unknown"
        result = engine.process_gate_request(gate_id, decision, reason, approver)
        print(json.dumps(result, indent=2))
    
    elif cmd == "check-sla":
        expired = engine.check_sla_expiry()
        print(f"Expired gate requests: {expired}")
    
    elif cmd == "list-gates":
        for gate in engine.gate_requests.values():
            print(f"{gate.id}: {gate.layer} - {gate.status}")


if __name__ == "__main__":
    main()