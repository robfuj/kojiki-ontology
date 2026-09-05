"""
SENTINEL - Provenance verification and non-fungible ledger wrapper.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import base64

# Try to import cryptography for Ed25519, fall back to mock for testing
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    # Mock for testing without cryptography
    class Ed25519PrivateKey:
        @staticmethod
        def generate():
            return MockPrivateKey()
        def sign(self, data):
            return b"mock_signature"
        def public_key(self):
            return MockPublicKey()
    
    class Ed25519PublicKey:
        @staticmethod
        def from_public_bytes(data):
            return MockPublicKey()
        def verify(self, signature, data):
            pass
    
    class MockPrivateKey:
        def sign(self, data):
            return b"mock_signature"
        def public_key(self):
            return MockPublicKey()
    
    class MockPublicKey:
        def verify(self, signature, data):
            pass


def sha256_hex(data: str) -> str:
    """Return SHA256 hash as hex string with prefix."""
    return "sha256:" + hashlib.sha256(data.encode('utf-8')).hexdigest()


def canonical_json(obj: Any) -> str:
    """Produce deterministic JSON for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


@dataclass
class ProvenanceToken:
    """SENTINEL provenance token wrapping a log entry."""
    entry_id: str
    prev_entry_id: str
    signer: str
    signature: str
    payload_ref: str
    payload_hash: str
    entry_type: str  # "signal", "edge_history", "gate_evidence"
    recorded_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvenanceToken':
        return cls(**data)


class KeyManager:
    """Manage Ed25519 keys for nodes."""
    
    def __init__(self, keys_dir: str = "mycelium/sentinel/keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.private_keys: Dict[str, Ed25519PrivateKey] = {}
        self.public_keys: Dict[str, Ed25519PublicKey] = {}
    
    def generate_keypair(self, node_id: str) -> Tuple[str, str]:
        """Generate and store keypair for a node. Returns (public_key, private_key_pem)."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Store private key (node runtime only - never shared)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Store public key (in registry)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        public_key_b64 = base64.b64encode(public_pem).decode('ascii')
        
        self.private_keys[node_id] = private_key
        self.public_keys[node_id] = public_key
        
        # Save private key to file (node runtime)
        key_file = self.keys_dir / f"{node_id.replace('.', '_')}_private.pem"
        key_file.write_bytes(private_pem)
        
        return f"ed25519:{public_key_b64}", private_pem.decode('ascii')
    
    def load_private_key(self, node_id: str) -> Optional[Ed25519PrivateKey]:
        """Load private key for node (only available to node's own runtime)."""
        key_file = self.keys_dir / f"{node_id.replace('.', '_')}_private.pem"
        if key_file.exists():
            private_pem = key_file.read_bytes()
            private_key = serialization.load_pem_private_key(private_pem, password=None)
            self.private_keys[node_id] = private_key
            return private_key
        return None
    
    def get_public_key(self, node_id: str) -> Optional[str]:
        """Get public key in registry format."""
        # In production, this reads from registry.node.public_key
        # For now, load from stored key
        key_file = self.keys_dir / f"{node_id.replace('.', '_')}_private.pem"
        if key_file.exists():
            private_pem = key_file.read_bytes()
            private_key = serialization.load_pem_private_key(private_pem, password=None)
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return f"ed25519:{base64.b64encode(public_pem).decode('ascii')}"
        return None
    
    def sign(self, node_id: str, data: str) -> str:
        """Sign data with node's private key."""
        if node_id not in self.private_keys:
            self.load_private_key(node_id)
        
        private_key = self.private_keys.get(node_id)
        if not private_key:
            raise ValueError(f"No private key for node {node_id}")
        
        signature = private_key.sign(data.encode('utf-8'))
        return "ed25519:" + base64.b64encode(signature).decode('ascii')
    
    def verify(self, node_id: str, data: str, signature: str) -> bool:
        """Verify signature using node's public key."""
        public_key_str = self.get_public_key(node_id)
        if not public_key_str:
            return False
        
        # Extract PEM from registry format
        pub_b64 = public_key_str.replace("ed25519:", "")
        public_pem = base64.b64decode(pub_b64)
        
        # Parse PEM to get Ed25519 public key
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        public_key = serialization.load_pem_public_key(public_pem)
        if not isinstance(public_key, Ed25519PublicKey):
            return False
        
        # Extract signature
        sig_b64 = signature.replace("ed25519:", "")
        signature_bytes = base64.b64decode(sig_b64)
        
        try:
            public_key.verify(signature_bytes, data.encode('utf-8'))
            return True
        except Exception:
            return False


class SentinelLog:
    """SENTINEL-wrapped append-only log with hash-chained provenance tokens."""
    
    def __init__(self, log_path: str, entry_type: str, key_manager: KeyManager):
        self.log_path = Path(log_path)
        self.entry_type = entry_type  # "signal", "edge_history", "gate_evidence"
        self.key_manager = key_manager
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_genesis()
    
    def _ensure_genesis(self) -> None:
        """Ensure log file exists."""
        if not self.log_path.exists():
            self.log_path.write_text("")
    
    def get_last_entry_id(self) -> str:
        """Get entry_id of last entry in log, or GENESIS."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return "GENESIS"
        
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return "GENESIS"
        
        last_token = json.loads(lines[-1])
        return last_token['entry_id']
    
    def compute_payload_hash(self, payload: Any) -> str:
        """Compute canonical hash of payload."""
        return sha256_hex(canonical_json(payload))
    
    def write(self, signer: str, payload_ref: str, payload: Any) -> ProvenanceToken:
        """
        Write a payload to the log with provenance token.
        
        Returns the provenance token (not the payload - payload goes to original log).
        """
        prev_entry_id = self.get_last_entry_id()
        payload_hash = self.compute_payload_hash(payload)
        recorded_at = datetime.utcnow().isoformat() + 'Z'
        
        # Data to sign: payload_hash + prev_entry_id
        sign_data = payload_hash + prev_entry_id
        signature = self.key_manager.sign(signer, sign_data)
        
        # Compute entry_id = hash(payload_hash + signer + prev_entry_id)
        entry_id_data = payload_hash + signer + prev_entry_id
        entry_id = sha256_hex(entry_id_data)
        
        token = ProvenanceToken(
            entry_id=entry_id,
            prev_entry_id=prev_entry_id,
            signer=signer,
            signature=signature,
            payload_ref=payload_ref,
            payload_hash=payload_hash,
            entry_type=self.entry_type,
            recorded_at=recorded_at
        )
        
        # Append token to sentinel log
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(token.to_dict()) + '\n')
        
        return token
    
    def verify_token(self, token: ProvenanceToken) -> bool:
        """Verify a provenance token."""
        # Check entry_id matches computed
        expected_id = sha256_hex(token.payload_hash + token.signer + token.prev_entry_id)
        if token.entry_id != expected_id:
            return False
        
        # Check signature
        sign_data = token.payload_hash + token.prev_entry_id
        if not self.key_manager.verify(token.signer, sign_data, token.signature):
            return False
        
        return True
    
    def verify_chain(self) -> Tuple[bool, List[str]]:
        """Verify entire chain integrity."""
        errors = []
        if not self.log_path.exists():
            return True, errors
        
        prev_id = "GENESIS"
        with open(self.log_path, 'r') as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                token = ProvenanceToken.from_dict(json.loads(line))
                
                # Check chain link
                if token.prev_entry_id != prev_id:
                    errors.append(f"Line {i}: chain broken - prev_entry_id {token.prev_entry_id} != expected {prev_id}")
                
                # Verify token
                if not self.verify_token(token):
                    errors.append(f"Line {i}: token verification failed for {token.entry_id}")
                
                prev_id = token.entry_id
        
        return len(errors) == 0, errors
    
    def get_tokens(self) -> List[ProvenanceToken]:
        """Get all tokens in log."""
        tokens = []
        if not self.log_path.exists():
            return tokens
        
        with open(self.log_path, 'r') as f:
            for line in f:
                if line.strip():
                    tokens.append(ProvenanceToken.from_dict(json.loads(line)))
        return tokens


class SentinelEngine:
    """Top-level SENTINEL engine coordinating all wrapped logs."""
    
    def __init__(self, base_path: str = "mycelium"):
        self.base_path = Path(base_path)
        self.key_manager = KeyManager(str(self.base_path / "sentinel/keys"))
        
        # Three wrapped logs
        self.signal_log = SentinelLog(
            str(self.base_path / "log/signals.jsonl"),
            "signal",
            self.key_manager
        )
        self.edge_history_log = SentinelLog(
            str(self.base_path / "log/edges_history.jsonl"),
            "edge_history",
            self.key_manager
        )
        self.gate_evidence_log = SentinelLog(
            str(self.base_path / "log/gate_evidence.jsonl"),
            "gate_evidence",
            self.key_manager
        )
    
    def write_signal(self, signer: str, signal_id: str, signal: Dict[str, Any]) -> ProvenanceToken:
        """Write a signal with provenance."""
        return self.signal_log.write(signer, signal_id, signal)
    
    def write_edge_history(self, signer: str, edge_ref: str, edge_data: Dict[str, Any]) -> ProvenanceToken:
        """Write an edge history entry with provenance."""
        return self.edge_history_log.write(signer, edge_ref, edge_data)
    
    def write_gate_evidence(self, signer: str, exp_ref: str, experience: Dict[str, Any]) -> ProvenanceToken:
        """Write gate evidence (Experience) with provenance."""
        return self.gate_evidence_log.write(signer, exp_ref, experience)
    
    def verify_experience_for_gate(self, exp_ref: str, experience: Dict[str, Any], signer: str) -> bool:
        """Verify an Experience reference for GateRequest repetition count."""
        # Check if there's a valid provenance token for this experience
        tokens = self.gate_evidence_log.get_tokens()
        for token in tokens:
            if token.payload_ref == exp_ref and token.signer == signer:
                return self.gate_evidence_log.verify_token(token)
        return False
    
    def count_verified_experiences(self, experience_refs: List[str], registry) -> int:
        """
        Count distinct, verified experiences for GateRequest.
        
        Only counts experiences that pass verify_entry - this is the fix for
        fabricated corroboration.
        """
        count = 0
        seen_signers = set()
        
        for exp_ref in experience_refs:
            tokens = self.gate_evidence_log.get_tokens()
            for token in tokens:
                if token.payload_ref == exp_ref:
                    node = registry.get_node(token.signer)
                    if not node:
                        continue
                    
                    # Check key status
                    if node.get('key_status') == 'revoked':
                        revoked_at = node.get('key_revoked_at')
                        if revoked_at and token.recorded_at > revoked_at:
                            continue  # Signed after revocation
                    
                    if self.gate_evidence_log.verify_token(token):
                        if token.signer not in seen_signers:
                            seen_signers.add(token.signer)
                            count += 1
                        break
        
        return count
    
    def verify_all_chains(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Verify all three log chains."""
        return {
            "signal": self.signal_log.verify_chain(),
            "edge_history": self.edge_history_log.verify_chain(),
            "gate_evidence": self.gate_evidence_log.verify_chain()
        }


def main():
    """CLI for SENTINEL operations."""
    import sys
    
    engine = SentinelEngine()
    
    if len(sys.argv) < 2:
        print("Usage: python sentinel.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "gen-key":
        if len(sys.argv) < 3:
            print("Usage: python sentinel.py gen-key <node_id>")
            return
        node_id = sys.argv[2]
        pub_key, priv_key = engine.key_manager.generate_keypair(node_id)
        print(f"Public key: {pub_key}")
        print(f"Private key saved to mycelium/sentinel/keys/{node_id.replace('.', '_')}_private.pem")
    
    elif cmd == "verify-chains":
        results = engine.verify_all_chains()
        for log_name, (ok, errors) in results.items():
            print(f"{log_name}: {'OK' if ok else 'FAILED'}")
            for err in errors:
                print(f"  - {err}")
    
    elif cmd == "sign":
        if len(sys.argv) < 5:
            print("Usage: python sentinel.py sign <node_id> <log_type> <payload_ref> <payload_json>")
            return
        node_id = sys.argv[2]
        log_type = sys.argv[3]
        payload_ref = sys.argv[4]
        payload = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        
        if log_type == "signal":
            token = engine.write_signal(node_id, payload_ref, payload)
        elif log_type == "edge":
            token = engine.write_edge_history(node_id, payload_ref, payload)
        elif log_type == "gate":
            token = engine.write_gate_evidence(node_id, payload_ref, payload)
        else:
            print(f"Unknown log type: {log_type}")
            return
        
        print(f"Token written: {token.entry_id}")


if __name__ == "__main__":
    main()