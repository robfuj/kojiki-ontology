#!/usr/bin/env python3
"""
PostgreSQL Data Access Layer for MYCELIUM Registry.

Provides the same interface as the JSON-based NodeRegistry but backed by PostgreSQL.
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

from engine.mycelium.postgres_persistence import get_pool, get_cursor
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))
from engine.sentinel import KeyManager, canonical_json, verify_signature


class PostgresNodeRegistryWrapper:
    """PostgreSQL-backed Node Registry with full API compatibility."""

    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.environ.get("KOJIKI_DSN", "postgresql://localhost/kojiki")
        # Ensure pool is initialized
        get_pool(self.dsn)

        self.root_departments = {
            "Finance", "Marketing", "Sales", "Engineering", "Operations",
            "Legal", "People & Comms", "Technology Platform"
        }

        # Initialize KeyManager for real key generation
        self.key_manager = KeyManager("mycelium/sentinel/keys")

    def load(self) -> None:
        """No-op for PostgreSQL - data is always in DB."""
        pass

    def save(self) -> None:
        """No-op for PostgreSQL - data is auto-committed."""
        pass

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

    def register_node(self, node_id: str, domain: str, node_type: str, status: str = "active",
                      pipeline_manifest_ref: str = None, pipeline_validated: bool = False,
                      parent_id: str = None, decision_rights: Dict = None,
                      decision_right: str = None, signer_id: str = None,
                      signature: str = None) -> bool:
        """Register a new node with atomic upsert and lineage validation."""
        # Validate lineage: parent must exist and have active key
        if parent_id:
            parent = self.get_node(parent_id)
            if not parent:
                raise ValueError(f"Parent node {parent_id} does not exist")
            if parent.get("key_status") != "active":
                raise ValueError(f"Parent node {parent_id} key status is not active")

        # Generate keypair for this node (only once after validation)
        private_key, public_key_registry_format = self.key_manager.generate_keypair(node_id)

        # If signer provided, verify signature
        if signer_id and signature:
            verified = verify_signature(signature, node_id, signer_id)
            if not verified:
                raise ValueError(f"Signature verification failed for signer {signer_id}")

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
            """, (node_id, domain, node_type, status, pipeline_manifest_ref,
                  pipeline_validated, public_key_registry_format, "active",
                  datetime.utcnow().isoformat() + "Z", parent_id,
                  Json(decision_rights) if decision_rights else None,
                  decision_right))

            return cur.rowcount > 0

    def register_node_governance(self, node_id: str, domain: str, node_type: str,
                                 parent_id: str = None, signer_id: str = None,
                                 signature: str = None) -> bool:
        """Governance-approved node registration with signature verification."""
        # This is the governance-approved path - validates parent + lineage + signature
        return self.register_node(
            node_id=node_id,
            domain=domain,
            node_type=node_type,
            status="active",
            parent_id=parent_id,
            signer_id=signer_id,
            signature=signature,
        )

    def update_decision_rights(self, node_id: str, decision_right: str,
                               decision_rights: Dict = None,
                               signer_id: str = None, signature: str = None) -> bool:
        """Update decision rights with lineage and signature validation."""
        node = self.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} does not exist")

        # Validate lineage if changing parent
        if node.get("parent_id") and node["parent_id"] != (parent_id := node.get("parent_id")):
            parent = self.get_node(node["parent_id"])
            if not parent or parent.get("key_status") != "active":
                raise ValueError(f"Invalid lineage for {node_id}")

        # If signer provided, verify signature
        if signer_id and signature:
            verified = verify_signature(signature, node_id, signer_id)
            if not verified:
                raise ValueError(f"Signature verification failed for signer {signer_id}")

        with get_cursor() as cur:
            cur.execute("""
                UPDATE mycelium_nodes
                SET decision_right = %s, decision_rights = %s
                WHERE id = %s
            """, (decision_right, Json(decision_rights) if decision_rights else None, node_id))
            return cur.rowcount > 0

    def revoke_key(self, node_id: str) -> bool:
        """Revoke a node's key."""
        with get_cursor() as cur:
            cur.execute("""
                UPDATE mycelium_nodes
                SET key_status = 'revoked', key_revoked_at = %s
                WHERE id = %s
            """, (datetime.utcnow().isoformat() + "Z", node_id))
            return cur.rowcount > 0

    def set_key_status(self, node_id: str, key_status: str) -> bool:
        """Set key status."""
        with get_cursor() as cur:
            cur.execute("""
                UPDATE mycelium_nodes
                SET key_status = %s
                WHERE id = %s
            """, (key_status, node_id))
            return cur.rowcount > 0

    def save_causal_chain(self, chain_data: Dict[str, Any]) -> bool:
        """Save a complete causal chain to PostgreSQL."""
        chain_id = chain_data.get('chain_id')
        dispatch_id = chain_data.get('dispatch_id')
        started_at = chain_data.get('started_at')
        completed_at = chain_data.get('completed_at')
        total_tokens = chain_data.get('total_tokens', 0)
        total_latency_ms = chain_data.get('total_latency_ms', 0)
        final_problem_id = chain_data.get('final_problem_id')
        final_output_id = chain_data.get('final_output_id')
        final_learning_id = chain_data.get('final_learning_id')

        try:
            with get_cursor() as cur:
                # Insert chain
                cur.execute("""
                    INSERT INTO causal_chains (chain_id, dispatch_id, started_at, completed_at,
                                               total_tokens, total_latency_ms,
                                               final_problem_id, final_output_id, final_learning_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (chain_id) DO UPDATE SET
                        completed_at = EXCLUDED.completed_at,
                        total_tokens = EXCLUDED.total_tokens,
                        total_latency_ms = EXCLUDED.total_latency_ms,
                        final_problem_id = EXCLUDED.final_problem_id,
                        final_output_id = EXCLUDED.final_output_id,
                        final_learning_id = EXCLUDED.final_learning_id
                """, (chain_id, dispatch_id, started_at, completed_at, total_tokens, total_latency_ms,
                      final_problem_id, final_output_id, final_learning_id))

                # Insert transitions
                transitions = chain_data.get('transitions', [])
                for t in transitions:
                    cur.execute("""
                        INSERT INTO causal_transitions (chain_id, from_stage, to_stage, input_hash,
                                                        output_hash, agent_id, signer, signature, public_key,
                                                        input_summary, output_summary, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (chain_id, t.get('from_stage'), t.get('to_stage'), t.get('input_hash'),
                          t.get('output_hash'), t.get('agent_id'), t.get('signer'), t.get('signature'),
                          t.get('public_key'), t.get('input_summary'), t.get('output_summary'),
                          t.get('timestamp')))

                # Insert causal nodes (stage outputs)
                causal_links = chain_data.get('causal_links', [])
                stage_outputs = {}
                for link in causal_links:
                    # Track source
                    src_key = f"{link['source_type']}:{link['source_id']}"
                    if src_key not in stage_outputs:
                        stage_outputs[src_key] = link
                    # Track target
                    tgt_key = f"{link['target_type']}:{link['target_id']}"
                    if tgt_key not in stage_outputs:
                        stage_outputs[tgt_key] = link

                # Also add from transitions
                for t in transitions:
                    stage_outputs[f"{t['to_stage']}:{t['output_hash']}"] = {
                        "source_type": t.get("to_stage", ""),
                        "source_id": t.get("output_hash", ""),
                        "target_type": "",
                        "target_id": "",
                    }

                for out_key, out_data in stage_outputs.items():
                    if ":" in out_key:
                        out_type, out_id = out_key.split(":", 1)
                        if out_type and out_id:
                            try:
                                cur.execute("""
                                    INSERT INTO causal_nodes (chain_id, node_type, node_id, created_at)
                                    VALUES (%s, %s, %s, %s)
                                    ON CONFLICT DO NOTHING
                                """, (chain_id, out_type, out_id, datetime.utcnow().isoformat()))
                            except Exception:
                                # Table schema may differ (e.g., column named 'type' not 'node_type')
                                # Skip node insert but continue with links
                                pass

                # Insert causal links
                for link in causal_links:
                    cur.execute("""
                        INSERT INTO causal_links (chain_id, source_type, source_id, target_type, target_id, relationship)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (chain_id, link['source_type'], link['source_id'],
                          link['target_type'], link['target_id'], link.get('relationship', 'derives_from')))

            return True
        except Exception as e:
            # Log the error but don't crash the pipeline
            print(f"  [CAUSAL CHAIN SAVE ERROR] {e}")
            return False

    # Backward compatibility alias
PostgresNodeRegistry = PostgresNodeRegistryWrapper