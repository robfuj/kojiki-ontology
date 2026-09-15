#!/usr/bin/env python3
"""
MYCELIUM Registry - Node lineage registry with naming validation and SENTINEL key lifecycle.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import SENTINEL KeyManager for key issuance
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from sentinel import KeyManager, canonical_json, verify_signature, SentinelEngine


class NodeRegistry:
    """Registry for MYCELIUM nodes with lineage validation and cryptographic key lifecycle."""

    def __init__(self, registry_path: str, genesis_public_key: Optional[str] = None,
                 key_manager: Optional[KeyManager] = None):
        self.registry_path = Path(registry_path)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.root_departments = {
            "Finance", "Marketing", "Sales", "Engineering", "Operations",
            "Legal", "People & Comms", "Technology Platform"
        }
        # Initialize KeyManager for SENTINEL key issuance
        self.key_manager = key_manager or KeyManager()
        # Initialize shared SentinelEngine for audit logging
        self.sentinel_engine = SentinelEngine(str(self.registry_path.parent))
        # Genesis public key (set once at init, no private key retained)
        self.genesis_public_key = genesis_public_key
        self.load()

    def load(self) -> None:
        """Load registry from file."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                self.nodes = {node['id']: node for node in data.get('nodes', [])}
        else:
            # Initialize with root departments ONLY if genesis_public_key provided
            # Otherwise start with empty registry (bootstrap via CLI command)
            if self.genesis_public_key:
                for dept in self.root_departments:
                    # Root departments are pre-issued active keys (genesis-signed offline)
                    # We only store the public key; key_status='active' reflects they're already issued
                    _, pub_key = self.key_manager.generate_keypair(dept)
                    self.nodes[dept] = {
                        "id": dept,
                        "domain": dept.lower().replace('.', '/'),
                        "type": "agent",
                        "status": "active",
                        "pipeline_manifest_ref": f"bots/{dept.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                        "pipeline_validated": False,
                        "public_key": pub_key,
                        "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                        "key_status": "active",
                        "key_revoked_at": None,
                        "parent": None
                    }
                self.save()
            # else: empty registry - will be bootstrapped via CLI command

    def save(self) -> None:
        """Save registry to file."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"nodes": list(self.nodes.values())}
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def validate_lineage(self, node_id: str, parent_id: Optional[str]) -> bool:
        """Validate that node_id follows lineage naming convention."""
        if node_id in self.root_departments:
            return parent_id is None

        if parent_id is None:
            return False

        if parent_id not in self.nodes:
            return False

        expected_prefix = parent_id + "."
        return node_id.startswith(expected_prefix) and node_id != parent_id

    def register_node(self, node_data: Dict[str, Any], signer: str, signature: str) -> bool:
        """
        Register a new node with validation, parent-signs-child enforcement, and reject-not-overwrite gate.

        Args:
            node_data: Node data including 'id' and 'parent' (None for root departments)
            signer: Node ID of the signer (parent for children, 'genesis' for root departments)
            signature: Ed25519 signature over canonical_json(node_data) by the signer's private key

        Returns:
            True if registration approved, False if rejected
        """
        node_id = node_data.get('id')
        parent_id = node_data.get('parent')

        if not node_id:
            return False

        if not self.validate_lineage(node_id, parent_id):
            self._audit('registration_rejected', node_id, signer, 'lineage validation failed')
            return False

        # Reject-not-overwrite gate: already active node_id cannot be re-registered
        if node_id in self.nodes and self.nodes[node_id].get('key_status') == 'active':
            self._audit('registration_rejected', node_id, signer, 'already active')
            return False

        # Parent must sign its own child's registration — never a central authority.
        # Exception: the 20 root departments, signed by the one-time genesis key.
        if parent_id is not None:
            parent = self.nodes.get(parent_id)
            if not parent or parent.get('key_status') != 'active':
                self._audit('registration_rejected', node_id, signer, 'parent not active')
                return False
            if not verify_signature(signature, canonical_json(node_data), parent['public_key']):
                self._audit('registration_rejected', node_id, signer, 'signature invalid')
                return False
        else:
            # Root department: must be signed by genesis key
            if not self.genesis_public_key:
                self._audit('registration_rejected', node_id, signer, 'genesis key not configured')
                return False
            if not verify_signature(signature, canonical_json(node_data), self.genesis_public_key):
                self._audit('registration_rejected', node_id, signer, 'genesis signature invalid')
                return False

        # Issue keypair for the new node
        _, pub_key = self.key_manager.generate_keypair(node_id)
        node_data.update(
            public_key=pub_key,
            key_status='active',
            key_issued_at=datetime.utcnow().isoformat() + 'Z',
            key_revoked_at=None
        )

        self.nodes[node_id] = node_data
        self.save()
        self._audit('registration_approved', node_id, signer, None)
        return True

    def issue_key_if_missing(self, node_id: str, actor: str) -> bool:
        """
        Admin repair: issue a key for a node that has no key (unissued -> active).
        Never touches an already-active key.
        """
        node = self.nodes.get(node_id)
        if not node or node.get('key_status') == 'active':
            return False
        _, pub_key = self.key_manager.generate_keypair(node_id)
        node.update(
            public_key=pub_key,
            key_status='active',
            key_issued_at=datetime.utcnow().isoformat() + 'Z',
            key_revoked_at=None
        )
        self.save()
        self._audit('key_repaired', node_id, actor, None)
        return True

    def rotate_key(self, node_id: str, authorized_by: str) -> tuple:
        """
        Admin rotation: generate a new keypair for an active node.
        Requires explicit authorized_by. Returns (old_key, new_key).
        """
        if not authorized_by:
            raise ValueError("rotation requires an explicit authorized_by")
        node = self.nodes.get(node_id)
        if not node:
            raise KeyError(f"Node {node_id} not found")
        if node.get('key_status') != 'active':
            raise ValueError(f"Node {node_id} is not active (status: {node.get('key_status')})")
        old_key = node['public_key']
        _, new_pub_key = self.key_manager.generate_keypair(node_id)
        node.update(
            public_key=new_pub_key,
            key_issued_at=datetime.utcnow().isoformat() + 'Z',
            # key_status remains 'active'
        )
        self.save()
        self._audit('key_rotated', node_id, authorized_by, {"old": old_key, "new": new_pub_key})
        return old_key, new_pub_key

    def _audit(self, event_type: str, node_id: str, actor: str, detail: Any) -> None:
        """Emit a lifecycle audit event to SENTINEL."""
        # Use shared SentinelEngine instance
        self.sentinel_engine.write_node_lifecycle_event(event_type, node_id, actor, detail)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all direct children of a node."""
        prefix = parent_id + "."
        return [node for node in self.nodes.values()
                if node['id'].startswith(prefix) and node['id'] != parent_id
                and node['id'].count('.') == parent_id.count('.') + 1]

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes."""
        return list(self.nodes.values())

    def _verify_signer_authority(self, signer: str, node_id: str) -> bool:
        """Verify that signer has authority over node_id (signer is ancestor or same node)."""
        if signer == node_id:
            return True
        # Check if signer is an ancestor
        current = node_id
        while '.' in current:
            current = '.'.join(current.split('.')[:-1])
            if current == signer:
                return True
        return False

    def update_decision_rights(self, node_id: str, decision_rights: Dict[str, Any], signer: Optional[str] = None, signature: Optional[str] = None) -> bool:
        """Update Decision Rights for a node from STRATEGY output.

        Args:
            node_id: Node ID to update
            decision_rights: Dict with 'own', 'consult', 'inform' keys
            signer: Optional signer node ID for authorization (required for auto-creating or updating)
            signature: Optional signature for authorization (required for auto-creating or updating)

        Returns:
            True if updated, False if node not found or authorization failed
        """
        node = self.nodes.get(node_id)
        if not node:
            # Auto-create node if it doesn't exist (child of root department)
            # Find parent from node_id
            parts = node_id.split('.')
            if len(parts) >= 2:
                parent_id = '.'.join(parts[:-1])
                if parent_id in self.nodes:
                    # Validate lineage
                    if not self.validate_lineage(node_id, parent_id):
                        return False  # Invalid lineage

                    # If auto-creating, require signer + signature authorization
                    if signer is not None and signature is not None:
                        # Verify signature against parent's public key
                        parent = self.nodes.get(parent_id)
                        if not parent:
                            return False
                        parent_pub_key = parent.get('public_key')
                        if not parent_pub_key:
                            return False

                        node_data = {
                            "id": node_id,
                            "domain": node_id.lower().replace('.', '/'),
                            "type": "agent",
                            "status": "active",
                            "pipeline_manifest_ref": f"bots/{node_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                            "pipeline_validated": False,
                            "public_key": "",  # Will be filled after keypair generation
                            "key_status": "active",
                            "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                            "key_revoked_at": None,
                            "parent": parent_id
                        }

                        if not verify_signature(signature, canonical_json(node_data), parent.get('public_key', '')):
                            return False  # Invalid signature
                    elif signer is None and signature is None:
                        # No authorization provided - reject auto-create for safety
                        return False

                    # Generate real keypair for the new node
                    _, pub_key = self.key_manager.generate_keypair(node_id)
                    self.nodes[node_id] = {
                        "id": node_id,
                        "domain": node_id.lower().replace('.', '/'),
                        "type": "agent",
                        "status": "active",
                        "pipeline_manifest_ref": f"bots/{node_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                        "pipeline_validated": False,
                        "public_key": pub_key,
                        "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                        "key_status": "active",
                        "key_revoked_at": None,
                        "parent": parent_id
                    }
                    node = self.nodes[node_id]
            else:
                # Node exists - require authorization to update decision rights
                if signer is None or signature is None:
                    return False  # Authorization required for updates

                # Verify signer has authority over this node
                if not self._verify_signer_authority(signer, node_id):
                    return False

                # Verify signature
                node_data = {"id": node_id, "decision_rights": decision_rights}
                if not verify_signature(signature, canonical_json(node_data), self.nodes[signer].get('public_key', '')):
                    return False  # Invalid signature

        if not node:
            return False

        # Validate structure
        required = {"own", "consult", "inform"}
        if not all(k in decision_rights for k in required):
            return False

        # Store the full decision rights object
        node["decision_rights"] = decision_rights
        # Also store primary right for quick filtering (the 'own' field)
        node["decision_right"] = decision_rights.get("own")

        self.save()
        self._audit("decision_rights_updated", node_id, "system", decision_rights)
        return True

    def get_decision_rights(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get full Decision Rights object for a node."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        return node.get("decision_rights")

    def get_decision_right(self, node_id: str) -> Optional[str]:
        """Get primary Decision Right (own) for a node."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        return node.get("decision_right")

    def register_node_governance(self, node_id: str, domain: str, node_type: str, parent_id: Optional[str]) -> bool:
        """
        Governance-initiated node registration - bypasses parent signature requirement.

        Used by GovernanceHandler for approved ontology changes.
        Still validates lineage and reject-not-overwrite.
        """
        if not node_id:
            return False

        if not self.validate_lineage(node_id, parent_id):
            self._audit('registration_rejected', node_id, 'GOVERNANCE', 'lineage validation failed')
            return False

        # Reject-not-overwrite gate: already active node_id cannot be re-registered
        if node_id in self.nodes and self.nodes[node_id].get('key_status') == 'active':
            self._audit('registration_rejected', node_id, 'GOVERNANCE', 'already active')
            return False

        # Issue keypair for the new node
        _, pub_key = self.key_manager.generate_keypair(node_id)

        node_data = {
            "id": node_id,
            "domain": domain,
            "type": node_type,
            "status": "active",
            "pipeline_manifest_ref": f"bots/{node_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
            "pipeline_validated": False,
            "public_key": pub_key,
            "key_issued_at": datetime.utcnow().isoformat() + 'Z',
            "key_status": "active",
            "key_revoked_at": None,
            "parent": parent_id
        }

        self.nodes[node_id] = node_data
        self.save()
        self._audit('registration_approved', node_id, 'GOVERNANCE', None)
        return True

    def validate_all(self) -> List[str]:
        """Validate entire registry, return list of errors."""
        errors = []
        for node_id, node in self.nodes.items():
            parent_id = node.get('parent')
            if not self.validate_lineage(node_id, parent_id):
                errors.append(f"Invalid lineage: {node_id} (parent: {parent_id})")
        return errors


def main():
    """CLI for registry operations."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="MYCELIUM Registry CLI")
    parser.add_argument("--registry", default="mycelium/registry/nodes.json", help="Registry file path")
    parser.add_argument("--genesis-key", help="Genesis public key for bootstrap")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs="*", help="Command arguments")
    args = parser.parse_args()

    registry = NodeRegistry(args.registry, genesis_public_key=args.genesis_key)

    if not args.command:
        print("Usage: python registry.py <command> [args]")
        print("Commands: validate, list, add, repair-key, rotate-key, bootstrap")
        return

    cmd = args.command

    if cmd == "validate":
        errors = registry.validate_all()
        if errors:
            print("Validation errors:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("All nodes valid")

    elif cmd == "list":
        for node in registry.get_all_nodes():
            print(f"{node['id']} ({node['status']}) key_status={node.get('key_status')}")

    elif cmd == "add":
        if len(args.args) < 4:
            print("Usage: python registry.py add <node_id> <parent_id> <signer> <signature_b64>")
            return
        node_id = args.args[0]
        parent_id = args.args[1]
        signer = args.args[2]
        signature = args.args[3]
        success = registry.register_node({"id": node_id, "parent": parent_id}, signer, signature)
        print(f"Registration {'successful' if success else 'failed'}")

    elif cmd == "repair-key":
        if len(args.args) < 2:
            print("Usage: python registry.py repair-key <node_id> <actor>")
            return
        node_id = args.args[0]
        actor = args.args[1]
        success = registry.issue_key_if_missing(node_id, actor)
        print(f"Key repair {'successful' if success else 'failed or not needed'}")

    elif cmd == "rotate-key":
        if len(args.args) < 2:
            print("Usage: python registry.py rotate-key <node_id> <authorized_by>")
            return
        node_id = args.args[0]
        authorized_by = args.args[1]
        try:
            old, new = registry.rotate_key(node_id, authorized_by)
            print(f"Key rotated: old={old[:32]}... new={new[:32]}...")
        except Exception as e:
            print(f"Rotation failed: {e}")

    elif cmd == "bootstrap":
        if not registry.genesis_public_key:
            print("Error: --genesis-key required for bootstrap")
            return
        # Initialize root departments
        count = 0
        for dept in registry.root_departments:
            if dept not in registry.nodes:
                _, pub_key = registry.key_manager.generate_keypair(dept)
                registry.nodes[dept] = {
                    "id": dept,
                    "domain": dept.lower().replace('.', '/'),
                    "type": "agent",
                    "status": "active",
                    "pipeline_manifest_ref": f"bots/{dept.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                    "pipeline_validated": False,
                    "public_key": pub_key,
                    "key_issued_at": datetime.utcnow().isoformat() + 'Z',
                    "key_status": "active",
                    "key_revoked_at": None,
                    "parent": None
                }
                count += 1
        if count > 0:
            registry.save()
            print(f"Bootstrapped {count} root departments")
        else:
            print("Registry already has root departments")


if __name__ == "__main__":
    main()