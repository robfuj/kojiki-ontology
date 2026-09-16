#!/usr/bin/env python3
"""
Regression test for write_gate_evidence signer fix.

Tests that count_verified_experiences() correctly counts distinct signers,
not just entries. This would have caught the bug where all entries were
signed by "registry" signer.
"""

import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engine.sentinel import SentinelEngine, KeyManager
from engine.mycelium.registry import NodeRegistry


def test_distinct_signer_count():
    """Test that count_verified_experiences counts distinct signers, not total entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup registry with multiple nodes
        registry_path = Path(tmpdir) / "nodes.json"
        genesis_pub = "ed25519:AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry = NodeRegistry(str(registry_path), genesis_public_key=genesis_pub)
        
        # Register 3 distinct nodes with active keys
        dummy_pub = "ed25519:AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry.nodes = {
            "kr-marketing-brand": {"id": "kr-marketing-brand", "public_key": dummy_pub, "key_status": "active", "key_issued_at": "2026-01-01T00:00:00Z", "key_revoked_at": None, "parent": None},
            "kr-sales-growth": {"id": "kr-sales-growth", "public_key": dummy_pub, "key_status": "active", "key_issued_at": "2026-01-01T00:00:00Z", "key_revoked_at": None, "parent": None},
            "kr-finance-fpa": {"id": "kr-finance-fpa", "public_key": dummy_pub, "key_status": "active", "key_issued_at": "2026-01-01T00:00:00Z", "key_revoked_at": None, "parent": None},
        }
        registry.save()
        
        # Create SentinelEngine with same base path
        sentinel_base = Path(tmpdir) / "mycelium"
        sentinel = SentinelEngine(str(sentinel_base))
        sentinel._ensure_registry_key()
        
        # Generate private keys for test signers
        for signer in ["kr-marketing-brand", "kr-sales-growth", "kr-finance-fpa"]:
            sentinel.key_manager.generate_keypair(signer)
        
        # Write experiences from 3 DIFFERENT signers
        for i, signer in enumerate(["kr-marketing-brand", "kr-sales-growth", "kr-finance-fpa"]):
            sentinel.write_gate_evidence(signer, f"exp-{i+1:03d}", {
                "id": f"exp-{i+1:03d}",
                "problem_id": "P-0001",
                "hypothesis": "Test hypothesis",
                "agents": [signer],
                "error_classification": "Model/representation error",
                "recorded_at": "2026-09-08T10:00:00Z"
            })
        
        # Count verified experiences for this problem
        count = sentinel.count_verified_experiences(["exp-001", "exp-002", "exp-003"], registry)
        
        assert count == 3, f"Expected 3 distinct signers, got {count}"
        print("✅ test_distinct_signer_count PASSED")


def test_same_signer_dedup():
    """Test that multiple entries from SAME signer count as 1 (dedup)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "nodes.json"
        genesis_pub = "ed25519:AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry = NodeRegistry(str(registry_path), genesis_public_key=genesis_pub)
        
        dummy_pub = "ed25519:AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry.nodes = {
            "kr-marketing-brand": {"id": "kr-marketing-brand", "public_key": dummy_pub, "key_status": "active", "key_issued_at": "2026-01-01T00:00:00Z", "key_revoked_at": None, "parent": None},
        }
        registry.save()
        
        sentinel_base = Path(tmpdir) / "mycelium"
        sentinel = SentinelEngine(str(sentinel_base))
        sentinel._ensure_registry_key()
        
        # Generate private key for test signer
        sentinel.key_manager.generate_keypair("kr-marketing-brand")
        
        # Write 5 experiences from SAME signer
        signer = "kr-marketing-brand"
        for i in range(5):
            sentinel.write_gate_evidence(signer, f"exp-{i+1:03d}", {
                "id": f"exp-{i+1:03d}",
                "problem_id": "P-0001",
                "hypothesis": "Test hypothesis",
                "agents": [signer],
                "error_classification": "Model/representation error",
                "recorded_at": "2026-09-08T10:00:00Z"
            })
        
        count = sentinel.count_verified_experiences(
            [f"exp-{i:03d}" for i in range(1, 6)], registry)
        
        assert count == 1, f"Expected 1 (dedup), got {count}"
        print("✅ test_same_signer_dedup PASSED")


def test_unknown_signer_rejected():
    """Test that experiences from unknown/unregistered signers are rejected at write time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "nodes.json"
        genesis_pub = "ed25519:AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry = NodeRegistry(str(registry_path), genesis_public_key=genesis_pub)
        
        dummy_pub = "ed25519:AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        registry.nodes = {
            "kr-marketing-brand": {"id": "kr-marketing-brand", "public_key": dummy_pub, "key_status": "active", "key_issued_at": "2026-01-01T00:00:00Z", "key_revoked_at": None, "parent": None},
        }
        registry.save()
        
        sentinel_base = Path(tmpdir) / "mycelium"
        sentinel = SentinelEngine(str(sentinel_base))
        sentinel._ensure_registry_key()
        
        # Generate private key for known signer
        sentinel.key_manager.generate_keypair("kr-marketing-brand")
        
        # Write from known signer - should succeed
        sentinel.write_gate_evidence("kr-marketing-brand", "exp-001", {
            "id": "exp-001", "problem_id": "P-0001", "agents": ["kr-marketing-brand"],
            "error_classification": "Model/representation error", "recorded_at": "2026-09-08T10:00:00Z"
        })
        
        # Write from UNKNOWN signer (not in registry, no key) - should fail
        try:
            sentinel.write_gate_evidence("unknown-node", "exp-002", {
                "id": "exp-002", "problem_id": "P-0001", "agents": ["unknown-node"],
                "error_classification": "Model/representation error", "recorded_at": "2026-09-08T10:00:00Z"
            })
            assert False, "Expected ValueError for unknown signer"
        except ValueError as e:
            assert "No private key for node unknown-node" in str(e)
        
        # Count should still be 1
        count = sentinel.count_verified_experiences(["exp-001", "exp-002"], registry)
        
        assert count == 1, f"Expected 1 (unknown signer rejected at write), got {count}"
        print("✅ test_unknown_signer_rejected PASSED")


if __name__ == "__main__":
    test_distinct_signer_count()
    test_same_signer_dedup()
    test_unknown_signer_rejected()
    print("\n✅ ALL REGRESSION TESTS PASSED")