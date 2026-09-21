#!/usr/bin/env python3
"""
PostgreSQL Data Access Layer for MYCELIUM Registry.

Full drop-in replacement for the JSON-based NodeRegistry with identical interface
but backed by PostgreSQL. Includes all NodeRegistry methods plus Postgres-specific features.
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from psycopg2.extras import Json

# Import KeyManager for real key generation
import sys
from pathlib import Path

from engine.mycelium.postgres_persistence import get_pool, get_cursor, get_conn, init_pool
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))
from engine.sentinel import KeyManager, canonical_json, verify_signature, SentinelEngine

from .registry_base import RegistryBase


class PostgresNodeRegistry(RegistryBase):
    """PostgreSQL-backed Node Registry with full API compatibility with JSON NodeRegistry."""

    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.environ.get("KOJIKI_DSN", "postgresql://localhost/kojiki")
        # Ensure pool is initialized
        init_pool(self.dsn)

        self.root_departments = {
            "Finance", "Marketing", "Sales", "Engineering", "Operations",
            "Legal", "People & Comms", "Technology Platform"
        }

        # Initialize KeyManager for real key generation
        self.key_manager = KeyManager("mycelium/sentinel/keys")

        # Initialize shared SentinelEngine for audit logging
        self.sentinel_engine = SentinelEngine("mycelium", self.key_manager)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, type, status, pipeline_manifest_ref, pipeline_validated,
                       public_key, key_status, key_issued_at, key_revoked_at, parent_id,
                       decision_rights, decision_right
                FROM mycelium_nodes WHERE id = %s
            """, (node_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            return None

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all direct children of a node."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, type, status, pipeline_manifest_ref, pipeline_validated,
                       public_key, key_status, key_issued_at, key_revoked_at, parent_id,
                       decision_rights, decision_right
                FROM mycelium_nodes
                WHERE parent_id = %s
            """, (parent_id,))
            return [dict(row) for row in cur.fetchall()]

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, type, status, pipeline_manifest_ref, pipeline_validated,
                       public_key, key_status, key_issued_at, key_revoked_at, parent_id,
                       decision_rights, decision_right
                FROM mycelium_nodes ORDER BY id
            """)
            return [dict(row) for row in cur.fetchall()]

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

        # Validate lineage
        if not self._validate_lineage(node_id, parent_id):
            self._audit('registration_rejected', node_id, signer, 'lineage validation failed')
            return False

        # Reject-not-overwrite gate: already active node_id cannot be re-registered
        existing = self.get_node(node_id)
        if existing and existing.get('key_status') == 'active':
            self._audit('registration_rejected', node_id, signer, 'already active')
            return False

        # Parent must sign its own child's registration — never a central authority.
        # Exception: the root departments, signed by the one-time genesis key.
        if parent_id is not None:
            parent = self.get_node(parent_id)
            if not parent or parent.get('key_status') != 'active':
                self._audit('registration_rejected', node_id, signer, 'parent not active')
                return False
            if not verify_signature(signature, canonical_json(node_data), parent['public_key']):
                self._audit('registration_rejected', node_id, signer, 'signature invalid')
                return False
        else:
            # Root department: must be signed by genesis key
            genesis_key = os.environ.get("KOJIKI_GENESIS_KEY")
            if not genesis_key:
                self._audit('registration_rejected', node_id, signer, 'genesis key not configured')
                return False
            if not verify_signature(signature, canonical_json(node_data), genesis_key):
                self._audit('registration_rejected', node_id, signer, 'genesis signature invalid')
                return False

        # Issue keypair for the new node
        _, pub_key = self.key_manager.generate_keypair(node_id)
        
        # Prepare node data with generated fields
        node_record = {
            "id": node_data.get('id'),
            "domain": node_data.get('domain', node_id.lower().replace('.', '/')),
            "type": node_data.get('type', 'agent'),
            "status": node_data.get('status', 'active'),
            "pipeline_manifest_ref": node_data.get('pipeline_manifest_ref', 
                f"bots/{node_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline"),
            "pipeline_validated": node_data.get('pipeline_validated', False),
            "public_key": pub_key,
            "key_issued_at": datetime.utcnow().isoformat() + 'Z',
            "key_status": "active",
            "key_revoked_at": None,
            "parent_id": parent_id,
            "decision_rights": Json(node_data.get('decision_rights', {
                "own": "OWN", "consult": [], "inform": []
            })),
            "decision_right": node_data.get('decision_right', "OWN")
        }

        # Insert into database
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO mycelium_nodes (id, domain, type, status, pipeline_manifest_ref,
                                            pipeline_validated, public_key, key_status,
                                            key_issued_at, parent_id, decision_rights,
                                            decision_right)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    domain = EXCLUDED.domain,
                    type = EXCLUDED.type,
                    status = EXCLUDED.status,
                    pipeline_manifest_ref = EXCLUDED.pipeline_manifest_ref,
                    pipeline_validated = EXCLUDED.pipeline_validated,
                    public_key = EXCLUDED.public_key,
                    key_status = EXCLUDED.key_status,
                    key_issued_at = EXCLUDED.key_issued_at,
                    parent_id = EXCLUDED.parent_id,
                    decision_rights = EXCLUDED.decision_rights,
                    decision_right = EXCLUDED.decision_right
                WHERE mycelium_nodes.key_status != 'active'
            """, (node_id, 
                  node_record["domain"], 
                  node_record["type"],
                  node_record["status"],
                  node_record["pipeline_manifest_ref"],
                  node_record["pipeline_validated"],
                  node_record["public_key"],
                  "active",
                  node_record["key_issued_at"],
                  parent_id,
                  node_record["decision_rights"],
                  node_record["decision_right"]))

        self._audit('registration_approved', node_id, signer, None)
        return True

    def _validate_lineage(self, node_id: str, parent_id: Optional[str]) -> bool:
        """Validate that node_id follows lineage naming convention."""
        if node_id in self.root_departments:
            return parent_id is None

        if parent_id is None:
            return False

        if parent_id not in [n['id'] for n in self.get_all_nodes()]:
            # Check in database directly for performance
            with get_cursor() as cur:
                cur.execute("SELECT 1 FROM mycelium_nodes WHERE id = %s", (parent_id,))
                if not cur.fetchone():
                    return False

        expected_prefix = parent_id + "."
        return node_id.startswith(expected_prefix) and node_id != parent_id

    def issue_key_if_missing(self, node_id: str, actor: str) -> bool:
        """
        Admin repair: issue a key for a node that has no key (unissued -> active).
        Never touches an already-active key.
        """
        node = self.get_node(node_id)
        if not node or node.get('key_status') == 'active':
            return False
        _, pub_key = self.key_manager.generate_keypair(node_id)
        
        with get_cursor() as cur:
            cur.execute("""
                UPDATE mycelium_nodes
                SET public_key = %s,
                    key_status = 'active',
                    key_issued_at = %s,
                    key_revoked_at = NULL
                WHERE id = %s
            """, (pub_key, datetime.utcnow().isoformat() + 'Z', node_id))
        
        self._audit('key_repaired', node_id, actor, None)
        return True

    def rotate_key(self, node_id: str, authorized_by: str) -> tuple:
        """
        Admin rotation: generate a new keypair for an active node.
        Requires explicit authorized_by. Returns (old_key, new_key).
        """
        if not authorized_by:
            raise ValueError("rotation requires an explicit authorized_by")
        node = self.get_node(node_id)
        if not node:
            raise KeyError(f"Node {node_id} not found")
        if node.get('key_status') != 'active':
            raise ValueError(f"Node {node_id} is not active (status: {node.get('key_status')})")
        old_key = node['public_key']
        _, new_pub_key = self.key_manager.generate_keypair(node_id)
        
        with get_cursor() as cur:
            cur.execute("""
                UPDATE mycelium_nodes
                SET public_key = %s,
                    key_issued_at = %s
                WHERE id = %s
            """, (new_pub_key, datetime.utcnow().isoformat() + 'Z', node_id))
        
        self._audit('key_rotated', node_id, authorized_by, {"old": old_key, "new": new_pub_key})
        return old_key, new_pub_key

    def _audit(self, event_type: str, node_id: str, actor: str, detail: Any) -> None:
        """Emit a lifecycle audit event to SENTINEL."""
        self.sentinel_engine.write_node_lifecycle_event(event_type, node_id, actor, detail)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, type, status, pipeline_manifest_ref, pipeline_validated,
                       public_key, key_status, key_issued_at, key_revoked_at, parent_id,
                       decision_rights, decision_right
                FROM mycelium_nodes WHERE id = %s
            """, (node_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            return None

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all direct children of a node."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, type, status, pipeline_manifest_ref, pipeline_validated,
                       public_key, key_status, key_issued_at, key_revoked_at, parent_id,
                       decision_rights, decision_right
                FROM mycelium_nodes
                WHERE parent_id = %s
            """, (parent_id,))
            return [dict(row) for row in cur.fetchall()]

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, domain, type, status, pipeline_manifest_ref, pipeline_validated,
                       public_key, key_status, key_issued_at, key_revoked_at, parent_id,
                       decision_rights, decision_right
                FROM mycelium_nodes ORDER BY id
            """)
            return [dict(row) for row in cur.fetchall()]

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

    def update_decision_rights(self, node_id: str, decision_rights: Dict[str, Any], 
                               signer: Optional[str] = None, signature: Optional[str] = None) -> bool:
        """Update Decision Rights for a node from STRATEGY output."""
        node = self.get_node(node_id)
        if not node:
            # Auto-create node if it doesn't exist (child of root department)
            parts = node_id.split('.')
            if len(parts) >= 2:
                parent_id = '.'.join(parts[:-1])
                if self.get_node(parent_id):
                    # Validate lineage
                    if not self._validate_lineage(node_id, parent_id):
                        return False  # Invalid lineage

                    # If auto-creating, require signer + signature authorization
                    if signer is not None and signature is not None:
                        # Verify signature against parent's public key
                        parent = self.get_node(parent_id)
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
                            "public_key": "",
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
                    
                    node_data = {
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
                    
                    with get_cursor() as cur:
                        cur.execute("""
                            INSERT INTO mycelium_nodes (id, domain, type, status, pipeline_manifest_ref,
                                                        pipeline_validated, public_key, key_status,
                                                        key_issued_at, parent_id, decision_rights,
                                                        decision_right)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (node_id, 
                              node_id.lower().replace('.', '/'), "agent", "active",
                              f"bots/{node_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                              False, pub_key, "active",
                              datetime.utcnow().isoformat() + 'Z', parent_id,
                              Json({"own": "OWN", "consult": [], "inform": []}), "OWN"))
                    node = self.get_node(node_id)
                else:
                    return False
            else:
                # Node exists - require authorization to update decision rights
                if signer is None or signature is None:
                    return False  # Authorization required for updates

                # Verify signer has authority over this node
                if not self._verify_signer_authority(signer, node_id):
                    return False

                # Verify signature
                node_data = {"id": node_id, "decision_rights": decision_rights}
                if not verify_signature(signature, canonical_json(node_data), self.get_node(signer).get('public_key', '')):
                    return False  # Invalid signature

        if not node:
            return False

        # Validate structure
        required = {"own", "consult", "inform"}
        if not all(k in decision_rights for k in required):
            return False

        # Store the full decision rights object
        with get_cursor() as cur:
            cur.execute("""
                UPDATE mycelium_nodes
                SET decision_rights = %s, decision_right = %s
                WHERE id = %s
            """, (Json(decision_rights), decision_rights.get("own"), node_id))

        self._audit("decision_rights_updated", node_id, "system", decision_rights)
        return True

    def get_decision_rights(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get full Decision Rights object for a node."""
        node = self.get_node(node_id)
        if not node:
            return None
        return node.get("decision_rights")

    def get_decision_right(self, node_id: str) -> Optional[str]:
        """Get primary Decision Right (own) for a node."""
        node = self.get_node(node_id)
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

            if not self._validate_lineage(node_id, parent_id):
                self._audit('registration_rejected', node_id, 'GOVERNANCE', 'lineage validation failed')
                return False

            # Reject-not-overwrite gate: already active node_id cannot be re-registered
            existing = self.get_node(node_id)
            if existing and existing.get('key_status') == 'active':
                self._audit('registration_rejected', node_id, 'GOVERNANCE', 'already active')
                return False

            # Issue keypair for the new node
            _, pub_key = self.key_manager.generate_keypair(node_id)

            with get_cursor() as cur:
                cur.execute("""
                    INSERT INTO mycelium_nodes (id, domain, type, status, pipeline_manifest_ref,
                                                pipeline_validated, public_key, key_status,
                                                key_issued_at, parent_id, decision_rights,
                                                decision_right)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        domain = EXCLUDED.domain,
                        type = EXCLUDED.type,
                        status = EXCLUDED.status,
                        pipeline_manifest_ref = EXCLUDED.pipeline_manifest_ref,
                        pipeline_validated = EXCLUDED.pipeline_validated,
                        public_key = EXCLUDED.public_key,
                        key_status = EXCLUDED.key_status,
                        key_issued_at = EXCLUDED.key_issued_at,
                        parent_id = EXCLUDED.parent_id,
                        decision_rights = EXCLUDED.decision_rights,
                        decision_right = EXCLUDED.decision_right
                    WHERE mycelium_nodes.key_status != 'active'
                """, (node_id, domain, node_type, "active", 
                      f"bots/{node_id.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                      False, pub_key, "active",
                      datetime.utcnow().isoformat() + 'Z', parent_id,
                      Json({"own": "OWN", "consult": [], "inform": []}), "OWN"))

            self._audit('registration_approved', node_id, 'GOVERNANCE', None)
            return True

    def validate_all(self) -> List[str]:
            """Validate entire registry, return list of errors."""
            errors = []
            for node in self.get_all_nodes():
                node_id = node['id']
                parent_id = node.get('parent')
                if not self._validate_lineage(node_id, parent_id):
                    errors.append(f"Invalid lineage: {node_id} (parent: {parent_id})")
            return errors


# Backward compatibility alias
PostgresNodeRegistryWrapper = PostgresNodeRegistry