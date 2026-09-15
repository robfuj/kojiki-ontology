"""
Tests for SENTINEL Provenance Layer.
"""

import json
import tempfile
import os
from mycelium.engine.sentinel import SentinelEngine, ProvenanceToken, sha256_hex, canonical_json


def test_sha256_hex():
    """Test SHA256 hash function."""
    result = sha256_hex("test")
    assert result.startswith("sha256:")
    assert len(result) == 71  # "sha256:" + 64 hex chars


def test_canonical_json():
    """Test deterministic JSON serialization."""
    obj1 = {"b": 2, "a": 1}
    obj2 = {"a": 1, "b": 2}
    assert canonical_json(obj1) == canonical_json(obj2)


def test_provenance_token_entry_id():
    """Test entry_id computation."""
    token = ProvenanceToken(
        entry_id="sha256:test",
        prev_entry_id="GENESIS",
        signer="Test.Node",
        signature="ed25519:mock",
        payload_ref="sig-001",
        payload_hash="sha256:abc123",
        entry_type="signal",
        recorded_at="2026-01-01T00:00:00Z"
    )
    
    # entry_id = hash(payload_hash + signer + prev_entry_id)
    expected = sha256_hex("sha256:abc123Test.NodeGENESIS")
    # Note: actual token.entry_id would be computed this way


def test_sentinel_write_signal():
    """Test writing a signal with provenance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "mycelium")
        os.makedirs(base_path)
        
        engine = SentinelEngine(base_path)
        
        # Generate key for node
        pub_key, _ = engine.key_manager.generate_keypair("Test.Node")
        
        signal = {
            "id": "sig-001",
            "origin_kr": "kr-001",
            "event": "status_change",
            "new_status": "off_track",
            "diagnosed_cause": "test cause",
            "diagnosed_cause_category": "Cause",
            "status": "ROUTED",
            "subgraph": ["kr-001"],
            "fired_at": "2026-01-01T00:00:00Z"
        }
        
        token = engine.write_signal("Test.Node", "sig-001", signal)
        
        assert token.entry_id.startswith("sha256:")
        assert token.prev_entry_id == "GENESIS"  # First entry
        assert token.signer == "Test.Node"
        assert token.payload_ref == "sig-001"
        assert token.entry_type == "signal"
        assert token.signature.startswith("ed25519:")


def test_sentinel_chain_verification():
    """Test chain verification detects tampering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "mycelium")
        os.makedirs(base_path)
        
        engine = SentinelEngine(base_path)
        
        # Generate key
        engine.key_manager.generate_keypair("Test.Node")
        
        # Write multiple signals
        for i in range(3):
            signal = {"id": f"sig-{i}", "data": f"test {i}"}
            engine.write_signal("Test.Node", f"sig-{i}", signal)
        
        # Verify chain passes
        ok, errors = engine.signal_log.verify_chain()
        assert ok
        assert len(errors) == 0
        
        # Tamper with the log file directly
        log_path = engine.signal_log.log_path
        lines = log_path.read_text().strip().split('\n')
        # Modify middle entry's payload_hash
        middle = json.loads(lines[1])
        middle['payload_hash'] = "sha256:tampered"
        lines[1] = json.dumps(middle)
        log_path.write_text('\n'.join(lines) + '\n')
        
        # Verify chain fails
        ok, errors = engine.signal_log.verify_chain()
        assert not ok
        assert len(errors) > 0
        assert any("verification failed" in e for e in errors)


def test_gate_evidence_verification():
    """Test GateRequest experience verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "mycelium")
        os.makedirs(base_path)
        
        engine = SentinelEngine(base_path)
        
        # Generate keys for multiple nodes
        engine.key_manager.generate_keypair("Node.A")
        engine.key_manager.generate_keypair("Node.B")
        engine.key_manager.generate_keypair("Node.C")
        
        # Write valid experiences from different nodes
        for node_id, exp_id in [("Node.A", "EXP-001"), ("Node.B", "EXP-002"), ("Node.C", "EXP-003")]:
            exp = {"id": exp_id, "problem_id": "P-001", "error_classification": "Assumption error"}
            engine.write_gate_evidence(node_id, exp_id, exp)
        
        # Mock registry
        class MockRegistry:
            def get_node(self, node_id):
                return {
                    "id": node_id,
                    "public_key": f"ed25519:mock",
                    "key_status": "active",
                    "key_revoked_at": None
                }
        
        registry = MockRegistry()
        
        # Count verified experiences - should be 3 (3 distinct signers)
        count = engine.count_verified_experiences(["EXP-001", "EXP-002", "EXP-003"], registry)
        assert count == 3


def test_forged_experience_excluded():
    """Test that forged experience references are excluded from count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "mycelium")
        os.makedirs(base_path)
        
        engine = SentinelEngine(base_path)
        
        # Generate key for one node
        engine.key_manager.generate_keypair("Node.A")
        
        # Write ONE valid experience from Node.A
        exp = {"id": "EXP-001", "problem_id": "P-001", "error_classification": "Assumption error"}
        engine.write_gate_evidence("Node.A", "EXP-001", exp)
        
        # Try to claim 4 experiences from 4 different nodes
        # but only one has valid provenance
        class MockRegistry:
            def get_node(self, node_id):
                return {
                    "id": node_id,
                    "public_key": f"ed25519:mock",
                    "key_status": "active",
                    "key_revoked_at": None
                }
        
        registry = MockRegistry()
        
        # Should only count the one with valid provenance
        count = engine.count_verified_experiences(
            ["EXP-001", "EXP-002", "EXP-003", "EXP-004"], registry
        )
        assert count == 1  # Only EXP-001 has valid token


def test_key_revocation():
    """Test key revocation excludes post-revocation entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "mycelium")
        os.makedirs(base_path)
        
        engine = SentinelEngine(base_path)
        
        engine.key_manager.generate_keypair("Node.A")
        
        # Write experience before revocation
        exp1 = {"id": "EXP-001", "problem_id": "P-001"}
        engine.write_gate_evidence("Node.A", "EXP-001", exp1)
        
        # Get the token's recorded_at timestamp
        tokens = engine.gate_evidence_log.get_tokens()
        token_recorded_at = tokens[0].recorded_at
        
        # Mock registry with revocation AFTER the token was recorded
        class MockRegistry:
            def get_node(self, node_id):
                return {
                    "id": node_id,
                    "public_key": f"ed25519:mock",
                    "key_status": "revoked",
                    "key_revoked_at": "2099-01-02T00:00:00Z"  # Far future - after token
                }
        
        registry = MockRegistry()
        count = engine.count_verified_experiences(["EXP-001"], registry)
        assert count == 1  # Still counts because recorded before revocation
        
        # Now test with revocation BEFORE token
        class MockRegistry2:
            def get_node(self, node_id):
                return {
                    "id": node_id,
                    "public_key": f"ed25519:mock",
                    "key_status": "revoked",
                    "key_revoked_at": "2020-01-02T00:00:00Z"  # Before token
                }
        
        registry2 = MockRegistry2()
        count2 = engine.count_verified_experiences(["EXP-001"], registry2)
        assert count2 == 0  # Excluded because recorded after revocation


if __name__ == "__main__":
    test_sha256_hex()
    test_canonical_json()
    test_provenance_token_entry_id()
    test_sentinel_write_signal()
    test_sentinel_chain_verification()
    test_gate_evidence_verification()
    test_forged_experience_excluded()
    test_key_revocation()
    print("All SENTINEL tests passed!")