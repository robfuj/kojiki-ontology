#!/usr/bin/env python3
"""
Test the Governance → Ontology Loop Closure end-to-end.
"""

import json
import tempfile
import os
import sys
from datetime import datetime

sys.path.insert(0, '/Users/Fujita/Documents/AI Filing System/decision-systems/00-kojiki-ontology/mycelium/engine')

from escalation import EscalationEngine, Experience, ErrorClass, Layer
from registry import NodeRegistry
from governance_handler import GovernanceHandler
from sentinel import SentinelEngine

def test_governance_loop():
    """Test the full governance → ontology loop."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize components
        registry_path = os.path.join(tmpdir, "nodes.json")
        edges_path = os.path.join(tmpdir, "edges.json")
        exp_log = os.path.join(tmpdir, "experiences.jsonl")
        prob_store = os.path.join(tmpdir, "problems.json")
        gate_req = os.path.join(tmpdir, "gates.json")
        learning = os.path.join(tmpdir, "governance_learning.jsonl")
        
        # Create registry with genesis key
        registry = NodeRegistry(registry_path, genesis_public_key="genesis_key_placeholder")
        
        # Bootstrap root departments
        for dept in ["Finance", "Marketing", "Sales", "Engineering", "Operations",
            "Legal", "People & Comms", "Technology Platform"]:
            _, pub_key = registry.key_manager.generate_keypair(dept)
            registry.nodes[dept] = {
                "id": dept,
                "domain": dept.lower().replace('.', '/'),
                "type": "agent",
                "status": "active",
                "pipeline_manifest_ref": f"bots/{dept.lower().replace('.', '-').replace(' ', '-')}/manifest.json#transformation_pipeline",
                "pipeline_validated": False,
                "public_key": pub_key,
                "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                "key_status": "active",
                "key_revoked_at": None,
                "parent": None
            }
        
        # Add GOVERNANCE node for governance signal verification
        _, pub_key = registry.key_manager.generate_keypair("GOVERNANCE")
        registry.nodes["GOVERNANCE"] = {
            "id": "GOVERNANCE",
            "domain": "governance",
            "type": "agent",
            "status": "active",
            "pipeline_manifest_ref": "bots/governance/manifest.json#transformation_pipeline",
            "pipeline_validated": False,
            "public_key": pub_key,
            "key_issued_at": datetime.utcnow().isoformat() + 'Z',
            "key_status": "active",
            "key_revoked_at": None,
            "parent": None
        }
        registry.save()
        
        # Create propagator
        from propagate import SignalPropagator
        propagator = SignalPropagator(
            edge_store_path=edges_path,
            log_path=os.path.join(tmpdir, "signals.jsonl"),
            registry=registry
        )
        
        # Create governance handler
        sentinel = SentinelEngine(str(registry.registry_path.parent))
        governance_handler = GovernanceHandler(
            registry=registry,
            edge_store_path=edges_path,
            escalation_engine=None,
            sentinel=sentinel
        )
        
        # Create escalation engine with governance handler
        escalation = EscalationEngine(
            experience_log_path=exp_log,
            problem_store_path=prob_store,
            gate_request_path=gate_req,
            mycelium_propagator=propagator,
            learning_ledger_path=learning,
            governance_handler=governance_handler
        )
        
        # Create a test experience that triggers L3 ontology escalation
        experience = Experience(
            id="EXP-TEST-001",
            problem_id="P-TEST-001",
            hypothesis="New team needed: AI Safety",
            agents=["Technology Platform"],
            action="Propose AI Safety team under Technology Platform",
            expected="Team created",
            observed="Team does not exist in registry",
            error_classification=ErrorClass.MODEL_REPRESENTATION_ERROR.value,  # Triggers L3
            escalation={"layer": "L3_ontology", "action": "governance_review"},
            redefinition={"new_problem": "P-TEST-002", "reason": "Add AI Safety team to handle AI safety decisions"},
            learning_ref="KL-TEST-001",
            propagation_targets=[]
        )
        
        print("=== Step 1: Escalate experience ===")
        result = escalation.escalate(experience)
        print(f"Escalation result: {json.dumps(result, indent=2)}")
        
        gate_id = result.get("gate_request_id")
        if not gate_id:
            print("ERROR: No gate request created")
            return False
        
        # Add a change_spec to the gate evidence for structured change
        gate = escalation.gate_requests[gate_id]
        gate.evidence["change_spec"] = [
            {
                "change_type": "add_node",
                "target": "Technology Platform.AI.Safety",
                "node_id": "Technology Platform.AI.Safety",
                "parent": "Technology Platform",
                "domain": "technology/platform/ai/safety",
                "node_type": "agent"
            }
        ]
        gate.evidence["experience_refs"] = [experience.id]
        escalation.save_gate_requests()
        
        print(f"\n=== Step 2: Process gate decision (APPROVED) ===")
        decision_result = escalation.process_gate_request(
            gate_id=gate_id,
            decision="APPROVED",
            reason="AI Safety team required for compliance",
            approver="ontology-governance-board"
        )
        print(f"Gate decision result: {json.dumps(decision_result, indent=2)}")
        
        # Check if node was added to registry
        print(f"\n=== Step 3: Verify ontology change ===")
        node = registry.get_node("Technology Platform.AI.Safety")
        if node:
            print(f"SUCCESS: Node Technology Platform.AI.Safety added to registry: {node['id']}")
            print(f"  Domain: {node['domain']}")
            print(f"  Type: {node['type']}")
            print(f"  Key status: {node['key_status']}")
        else:
            print("FAILURE: Node Technology Platform.AI.Safety NOT found in registry")
            # Debug: list all nodes
            print("All nodes in registry:")
            for n in registry.get_all_nodes():
                print(f"  {n['id']}")
            return False
        
        # Check governance changes log
        changes_log = governance_handler.changes_log_path
        if changes_log.exists():
            with open(changes_log) as f:
                lines = f.readlines()
                print(f"\nGovernance changes log ({len(lines)} entries):")
                for line in lines:
                    change = json.loads(line)
                    print(f"  - {change['change_type']}: {change['target']} (gate: {change['gate_id']})")
        
        return True

if __name__ == "__main__":
    success = test_governance_loop()
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")
    sys.exit(0 if success else 1)