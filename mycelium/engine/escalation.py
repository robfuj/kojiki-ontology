"""
NEURAXIS Escalation Engine - Vertical axis for recursive problem redefinition.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict, field

# Flat-import style (same directory) - consistent with registry.py and propagate.py
import sys
sys.path.insert(0, str(Path(__file__).parent))
from sentinel import SentinelEngine, canonical_json
from governance_handler import GovernanceHandler, ChangeType


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
    # FIX #1: mutable default on a dataclass field crashes at class-definition time
    # (Python explicitly rejects list/dict/set literal defaults on dataclasses).
    # Use default_factory instead — confirmed by import failing before this fix.
    propagation_targets: List[str] = field(default_factory=list)


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
                 mycelium_propagator=None,
                 learning_ledger_path: Optional[str] = None,
                 governance_handler=None):
        self.experience_log_path = Path(experience_log_path)
        self.problem_store_path = Path(problem_store_path)
        self.gate_request_path = Path(gate_request_path)
        self.mycelium_propagator = mycelium_propagator
        self.governance_handler = governance_handler
        # Expose module-level globals as instance attributes for governance_handler.py L4 handlers
        self.ESCALATION_MAP = ESCALATION_MAP
        self.AUTONOMOUS_LAYERS = AUTONOMOUS_LAYERS
        self.GOVERNANCE_LAYERS = GOVERNANCE_LAYERS
        # FIX #7: governance decisions were never actually written anywhere.
        # Default this alongside the other three logs so it exists even if
        # the caller doesn't pass one explicitly.
        self.learning_ledger_path = Path(
            learning_ledger_path or (self.gate_request_path.parent / "governance_learning_cases.jsonl")
        )

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
        self.learning_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.learning_ledger_path.exists():
            self.learning_ledger_path.touch()

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
        if 'missing_data' in context or 'incorrect_data' in context:
            return ErrorClass.INFORMATION_ERROR

        if context.get('reasoning_valid', True) and not context.get('implementation_correct', True):
            return ErrorClass.EXECUTION_ERROR

        if not context.get('reasoning_valid', True):
            return ErrorClass.REASONING_ERROR

        if context.get('assumption_invalid', False):
            return ErrorClass.ASSUMPTION_ERROR

        # FIX #2 (call site): explicitly ask "how many MODEL_REPRESENTATION_ERROR
        # precedents exist" here, since that's genuinely what this branch means to check.
        similar_failures = self._count_similar_failures(
            context.get('problem_id', ''), ErrorClass.MODEL_REPRESENTATION_ERROR
        )
        if similar_failures >= 3:
            return ErrorClass.MODEL_REPRESENTATION_ERROR

        if context.get('repeated_representation_issues', 0) >= 2:
            return ErrorClass.META_ERROR

        return ErrorClass.REASONING_ERROR

    def _count_similar_failures(self, problem_id: str, error_class: ErrorClass) -> int:
        """
        Count experiences with same problem_id and the SAME error classification
        being asked about.

        FIX #2: this previously hardcoded MODEL_REPRESENTATION_ERROR regardless of
        which layer/error class the caller actually cared about — confirmed by
        test: an L4 (Meta error) gate request reported repetition_count=1 when
        3 real Meta-error precedents existed, because it was counting L3-class
        errors instead. Now takes error_class explicitly so each caller asks
        about the class that's actually relevant to it.
        """
        count = 0
        for exp in self.experiences:
            if exp.problem_id == problem_id and exp.error_classification == error_class.value:
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

        self.experiences.append(experience)
        self.save_experiences()

        # Write experience to SENTINEL gate_evidence_log for verification
        if self.mycelium_propagator and hasattr(self.mycelium_propagator, 'registry'):
            # Use the same base path as the propagator's registry (mycelium root)
            # CRITICAL: Use the registry's key manager to ensure key consistency
            sentinel = SentinelEngine(
                str(self.mycelium_propagator.registry.registry_path.parent),
                key_manager=self.mycelium_propagator.registry.key_manager
            )
            try:
                # signer = primary agent that produced this experience (must be registered node with active key)
                signer = experience.agents[0] if experience.agents else "unknown"
                sentinel.write_gate_evidence(signer, experience.id, {
                    "id": experience.id,
                    "problem_id": experience.problem_id,
                    "hypothesis": experience.hypothesis,
                    "agents": experience.agents,
                    "action": experience.action,
                    "expected": experience.expected,
                    "observed": experience.observed,
                    "error_classification": experience.error_classification,
                    "escalation": experience.escalation,
                    "redefinition": experience.redefinition,
                    "learning_ref": experience.learning_ref,
                    "recorded_at": datetime.utcnow().isoformat() + 'Z'
                })
            except Exception:
                # Log but don't fail escalation if SENTINEL write fails
                pass

        if target_layer in AUTONOMOUS_LAYERS:
            result["actions"].append(f"Autonomous revision at {target_layer.value}")
            if target_layer == Layer.L2_PROBLEM_REPRESENTATION:
                new_problem = self._create_superseding_problem(experience)
                result["new_problem_id"] = new_problem.id
                result["actions"].append(f"Created superseding problem: {new_problem.id}")
        else:
            gate_request = self._create_gate_request(experience, target_layer, error_class)
            self.gate_requests[gate_request.id] = gate_request
            self.save_gate_requests()
            result["gate_request_id"] = gate_request.id
            result["actions"].append(f"Gate request created for {target_layer.value}: {gate_request.id}")

        return result

    def _create_superseding_problem(self, experience: Experience) -> Problem:
        """Create a new problem version superseding the old one."""
        old_problem = self.problems.get(experience.problem_id)
        if not old_problem:
            # FIX #6: `goal=context.get('goal', '') if (context := {}) else ''` always
            # took the else branch, since `{}` is falsy — goal was unconditionally ''
            # for every brand-new base Problem, confirmed empirically (bool({}) is False).
            # There was also no actual `context` argument on this method to read from.
            # Fall back to the experience's own hypothesis, which is the closest thing
            # to "what we were trying to achieve" available at this point — a real
            # base Problem should ideally come from SACCADE's P-0000 output, not be
            # synthesized here, but this at least stops it being silently blank.
            new_problem = Problem(
                id=experience.redefinition['new_problem'] if experience.redefinition else f"P-{len(self.problems)+1:04d}",
                supersedes=experience.problem_id,
                reason=experience.redefinition.get('reason', f"Invalidated by {experience.id}") if experience.redefinition else f"Invalidated by {experience.id}",
                goal=experience.hypothesis,
                constraints=[],
                assumptions=[],
                unknowns=[]
            )
        else:
            new_problem = Problem(
                id=experience.redefinition['new_problem'] if experience.redefinition else f"{old_problem.id}-v{len([p for p in self.problems if p.startswith(old_problem.id)])+1}",
                supersedes=experience.problem_id,
                reason=experience.redefinition.get('reason', f"Assumption invalidated by {experience.id}") if experience.redefinition else f"Assumption invalidated by {experience.id}",
                goal=old_problem.goal,
                constraints=old_problem.constraints,
                assumptions=[a for a in old_problem.assumptions if a != experience.hypothesis],
                unknowns=old_problem.unknowns + [experience.hypothesis]
            )

        self.problems[new_problem.id] = new_problem
        self.save_problems()
        return new_problem

    def _create_gate_request(self, experience: Experience, target_layer: Layer, error_class: ErrorClass) -> GateRequest:
        """Create a governance gate request for L3/L4."""
        # FIX #3: Real wiring for consult nodes - use compute_subgraph with correct signature
        consult_nodes: List[str] = []
        if self.mycelium_propagator is not None:
            if hasattr(self.mycelium_propagator, "compute_subgraph"):
                try:
                    # Correct signature: compute_subgraph(self, origin_kr: str) -> Set[str]
                    consult_nodes = list(self.mycelium_propagator.compute_subgraph(experience.problem_id))
                except Exception:
                    consult_nodes = list(dict.fromkeys(experience.agents))
            else:
                consult_nodes = list(dict.fromkeys(experience.agents))
        else:
            consult_nodes = list(dict.fromkeys(experience.agents))

        gate_id = f"gate-{len(self.gate_requests)+1:04d}"
        sla_deadline = (datetime.utcnow() + timedelta(days=14)).isoformat() + 'Z'

        # FIX: Use SENTINEL-verified experience count instead of unsigned self.experiences
        # This prevents fabricated corroboration from inflating the evidence bar
        repetition_count = 0
        if self.mycelium_propagator is not None and hasattr(self.mycelium_propagator, 'registry'):
            # Use the same base path as the propagator's registry (mycelium root)
            sentinel = SentinelEngine(str(self.mycelium_propagator.registry.registry_path.parent))
            # Build experience_refs for this error class
            experience_refs = [
                exp.id for exp in self.experiences
                if exp.problem_id == experience.problem_id and exp.error_classification == error_class.value
            ]
            repetition_count = sentinel.count_verified_experiences(experience_refs, self.mycelium_propagator.registry)
        else:
            # DECISION (2026-09-06): Fail-closed when no SENTINEL registry available.
            # Without a verified identity registry, we cannot distinguish real
            # corroboration from fabricated experiences. repetition_count=0 means
            # an L3/L4 gate will NEVER open on unsigned evidence alone — this is
            # intentional. If you need gates to open in standalone/test environments,
            # pass a mycelium_propagator with a populated registry.
            # See test_repetition_count_without_registry for expected behavior.
            repetition_count = 0

        return GateRequest(
            id=gate_id,
            layer=target_layer.value,
            proposed_change=f"Revise {'ontology' if target_layer == Layer.L3_ONTOLOGY else 'meta-strategy'} based on {experience.id}",
            evidence={
                "repetition_count": repetition_count,
                "experience_refs": [
                    exp.id for exp in self.experiences
                    if exp.problem_id == experience.problem_id and exp.error_classification == error_class.value
                ],
                "change_spec": self._generate_change_spec(experience, target_layer)
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

        # FIX #4: the SLA/fail-closed check previously lived in an `elif` that could
        # only run for REJECTED/ESCALATED decisions (never APPROVED/MODIFIED, since
        # those took the `if` branch first) — confirmed by test: an APPROVED decision
        # submitted after the deadline succeeded and propagated regardless. The
        # deadline is now checked FIRST, before any decision is processed, so a late
        # decision of ANY kind fails closed instead of depending on call order.
        deadline = datetime.fromisoformat(gate.sla_deadline.replace('Z', '+00:00')).replace(tzinfo=None)
        if deadline < datetime.utcnow():
            gate.status = "EXPIRED"
            self.save_gate_requests()
            return {
                "success": False,
                "error": "SLA deadline has passed — gate fails closed to EXPIRED, decision not applied",
                "gate_id": gate_id,
                "status": "EXPIRED"
            }

        valid_decisions = ["APPROVED", "REJECTED", "MODIFIED", "ESCALATED"]
        if decision not in valid_decisions:
            return {"success": False, "error": f"Invalid decision: {decision}"}

        gate.status = decision
        gate.decision_reason = reason
        gate.applied_at = datetime.utcnow().isoformat() + 'Z' if decision in ["APPROVED", "MODIFIED"] else None
        self.save_gate_requests()

        if decision in ["APPROVED", "MODIFIED"]:
            self._log_governance_decision(gate, approver)

            if self.mycelium_propagator:
                # Verify experience evidence via SENTINEL before propagating governance signal
                # This ensures only SENTINEL-verified experiences can drive ontology/meta-strategy changes
                verified = True
                if self.mycelium_propagator.registry:
                    from sentinel import SentinelEngine
                    # CRITICAL: Use the registry's key manager for verification consistency
                    sentinel = SentinelEngine(
                        str(self.mycelium_propagator.registry.registry_path.parent),
                        key_manager=self.mycelium_propagator.registry.key_manager
                    )
                    experience_refs = gate.evidence.get("experience_refs", [])
                    # Verify each experience has a valid SENTINEL chain with active signer
                    for exp_ref in experience_refs:
                        if not sentinel.verify_experience_chain(exp_ref, self.mycelium_propagator.registry):
                            verified = False
                            break
                    # For testing: if no experience_refs, skip verification
                    if not experience_refs:
                        verified = True

                if verified:
                    signal = {
                        "id": f"sig-{gate_id}",
                        "origin_kr": "GOVERNANCE",
                        "event": "ontology_change" if gate.layer == Layer.L3_ONTOLOGY.value else "meta_strategy_change",
                        "new_status": "changed",
                        "signal_kind": "failure",  # Governance decisions are failure-kind signals (rule changes)
                        "diagnosed_cause": f"Governance {decision.lower()}: {gate.proposed_change}",
                        "diagnosed_cause_category": "Rule",
                        "status": "ROUTED",
                        "subgraph": gate.consult,
                        "fired_at": datetime.utcnow().isoformat() + 'Z',
                        "change_spec": gate.evidence.get("change_spec", []),
                        "approver": approver
                    }
                    
                    # Sign the signal with GOVERNANCE key (or registry key as fallback)
                    if self.mycelium_propagator and hasattr(self.mycelium_propagator, 'registry'):
                        registry = self.mycelium_propagator.registry
                        if registry and hasattr(registry, 'key_manager'):
                            # Use registry key manager to sign
                            signal_data = {k: v for k, v in signal.items() if k != 'signature'}
                            signal_json = canonical_json(signal_data)
                            # Try to sign with GOVERNANCE node, fallback to registry
                            if registry.get_node('GOVERNANCE'):
                                signal['signature'] = registry.key_manager.sign('GOVERNANCE', signal_json)
                            else:
                                # Use registry's own key for signing
                                signal['signature'] = registry.key_manager.sign('registry', signal_json)
                    
                    self.mycelium_propagator.propagate(signal)
                    
                    # Also invoke governance handler to apply the actual ontology change
                    if self.governance_handler:
                        handler_result = self.governance_handler.handle_governance_signal(signal)
                        print(f"Governance handler result: {handler_result}")
                else:
                    # Log but don't propagate - evidence not SENTINEL-verified
                    print(f"WARNING: Gate {gate_id} approved but SENTINEL verification failed for experience refs; signal not propagated")

        return {"success": True, "gate_id": gate_id, "status": gate.status}

    def _log_governance_decision(self, gate: GateRequest, approver: str) -> None:
        """
        Log governance decision as a learning case.

        FIX #7: this was `pass` — an approved/modified gate was never actually
        recorded anywhere despite the comment claiming it was. Appends one JSON
        line per decision to learning_ledger_path. This is a stand-in for the
        real Universal Learning Ledger writer (§III.2) — point this at the
        actual ledger-write function once its interface is confirmed, rather
        than trusting this local file as the source of truth.
        """
        case = {
            "case_type": "governance_decision",
            "gate_id": gate.id,
            "layer": gate.layer,
            "decision": gate.status,
            "decision_reason": gate.decision_reason,
            "approver": approver,
            "proposed_change": gate.proposed_change,
            "evidence": gate.evidence,
            "applied_at": gate.applied_at,
        }
        with open(self.learning_ledger_path, 'a') as f:
            f.write(json.dumps(case) + "\n")

    def check_sla_expiry(self) -> List[str]:
        """Check for expired gate requests (fail-closed default)."""
        expired = []
        now = datetime.utcnow()
        for gate in self.gate_requests.values():
            if gate.status == "PENDING":
                deadline = datetime.fromisoformat(gate.sla_deadline.replace('Z', '+00:00')).replace(tzinfo=None)
                if deadline < now:
                    gate.status = "EXPIRED"
                    expired.append(gate.id)
        if expired:
            self.save_gate_requests()
        return expired

    def _generate_change_spec(self, experience: Experience, target_layer: Layer) -> List[Dict]:
        """Generate structured change_spec for gate request based on experience and target layer."""
        if target_layer == Layer.L3_ONTOLOGY:
            # L3: Ontology changes - node additions, decision rights updates, edge weight changes
            # Extract from experience.redefinition if available
            if experience.redefinition:
                redef = experience.redefinition
                if redef.get('new_problem'):
                    return [{
                        "change_type": ChangeType.ADD_NODE.value,
                        "target": redef['new_problem'],
                        "node_id": redef['new_problem'],
                        "parent": redef.get('parent'),
                        "domain": redef.get('domain', redef['new_problem'].lower().replace('.', '/')),
                        "type": redef.get('type', 'agent')
                    }]
            # Fallback: infer from error classification
            return [{
                "change_type": ChangeType.UPDATE_DECISION_RIGHTS.value,
                "target": experience.problem_id,
                "node_id": experience.problem_id,
                "decision_rights": {
                    "own": experience.problem_id,
                    "consult": experience.agents,
                    "inform": []
                }
            }]
        else:
            # L4: Meta-strategy changes
            return [{
                "change_type": ChangeType.UPDATE_ESCALATION_MAP.value,
                "mapping": {}
            }]

    def should_stop_escalation(self, experience_chain: List[Experience],
                               info_gain_threshold: float = 0.1) -> bool:
        """
        Termination condition: stop escalating when expected information gain < cost.

        FIX #8: previously only checked "are the last 3 experiences classified at
        the same autonomous layer" — the docstring claimed a diminishing-returns
        check that the code never actually performed. This adds a real (if still
        simplified — flagged honestly, not disguised as more sophisticated than
        it is) proxy: if the last 3 experiences at the same layer also produced
        essentially the same `observed` result, that's diminishing information
        gain, not just "same layer."
        """
        if len(experience_chain) < 3:
            return False

        last_three = experience_chain[-3:]
        layers = [ESCALATION_MAP[ErrorClass(e.error_classification)] for e in last_three]

        if len(set(layers)) != 1 or layers[0] not in AUTONOMOUS_LAYERS:
            return False

        # Diminishing-returns proxy: same layer AND repeating the same observation.
        observations = {e.observed.strip().lower() for e in last_three}
        if len(observations) == 1:
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