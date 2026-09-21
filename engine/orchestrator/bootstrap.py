#!/usr/bin/env python3
"""
Bootstrap module for Orchestrator — registry initialization and decision rights wiring.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from engine.mycelium.decision_rights import DecisionRight, DecisionRightsGate
from engine.mycelium.registry import NodeRegistry
from engine.sentinel import KeyManager
from engine.kojiki_core.utils import is_test_mode


def bootstrap_registry(registry: NodeRegistry, key_manager: KeyManager, orchestrator_node_id: Optional[str] = None):
    """Register 8 root departments, their head nodes, and the Orchestrator node."""
    root_departments = [
        "Finance", "Marketing", "Sales", "Engineering",
        "Operations", "Legal", "People & Comms", "Technology Platform"
    ]

    for dept in root_departments:
        if dept not in registry.nodes:
            # Register root department node
            _, pub_key = key_manager.generate_keypair(dept)
            registry.nodes[dept] = {
                "id": dept,
                "domain": dept.lower().replace(' ', '/'),
                "type": "agent",
                "status": "active",
                "pipeline_manifest_ref": f"bots/{dept.lower().replace(' ', '-')}/manifest.json#transformation_pipeline",
                "pipeline_validated": False,
                "public_key": pub_key,
                "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                "key_status": "active",
                "key_revoked_at": None,
                "parent": None,
                "decision_rights": {
                    "own": "OWN",
                    "consult": [],
                    "inform": []
                },
                "decision_right": "OWN"
            }
            # Register department head node
            head_id = f"{dept}.Head"
            _, head_pub_key = key_manager.generate_keypair(head_id)
            registry.nodes[head_id] = {
                "id": head_id,
                "domain": head_id.lower().replace('.', '/'),
                "type": "agent",
                "status": "active",
                "pipeline_manifest_ref": f"bots/{head_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                "pipeline_validated": False,
                "public_key": head_pub_key,
                "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                "key_status": "active",
                "key_revoked_at": None,
                "parent": dept,
                "decision_rights": {
                    "own": "OWN",
                    "consult": [dept],
                    "inform": []
                },
                "decision_right": "OWN"
            }

    # Register Orchestrator node
    orchestrator_id = "Orchestrator"
    if orchestrator_id not in registry.nodes:
        _, orchestrator_pub_key = key_manager.generate_keypair(orchestrator_id)
        registry.nodes[orchestrator_id] = {
            "id": orchestrator_id,
            "domain": "orchestrator",
            "type": "agent",
            "status": "active",
            "pipeline_manifest_ref": "bots/orchestrator/manifest.json#transformation_pipeline",
            "pipeline_validated": False,
            "public_key": orchestrator_pub_key,
            "key_issued_at": datetime.utcnow().isoformat() + 'Z',
            "key_status": "active",
            "key_revoked_at": None,
            "parent": None,
            "decision_rights": {
                "own": "OWN",
                "consult": [],
                "inform": []
            },
            "decision_right": "OWN"
        }

    registry.save()


def wire_decision_rights(registry: NodeRegistry, conversation_layer):
    """Wire decision rights for consultation layer from registry nodes."""
    conversation_layer.gate = DecisionRightsGate()
    for node_id, node in registry.nodes.items():
        dr = node.get("decision_rights")
        if dr:
            primary = node.get("decision_right") or dr.get("own")
            if primary:
                conversation_layer.gate.set_node_right(node_id, DecisionRight(primary))


def resolve_data_dir(data_dir: Optional[str] = None) -> Path:
    """Resolve data directory from env or parameter (NOT /tmp)."""
    if data_dir is None:
        data_dir = os.environ.get("KOJIKI_DATA_DIR", str(Path.home() / ".kojiki" / "data"))
    path = Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_orchestrator_node_id(orchestrator_node_id: Optional[str] = None) -> Optional[str]:
    """Handle Orchestrator node ID - prompt user if not provided."""
    if orchestrator_node_id is None and not is_test_mode():
        # In production, this would prompt the user or read from config
        pass
    return orchestrator_node_id