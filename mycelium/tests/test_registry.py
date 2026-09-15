"""
Tests for MYCELIUM Registry.
"""

import json
import tempfile
import os
from mycelium.engine.registry import NodeRegistry


def test_registry_initialization():
    """Test registry initializes with root departments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        # Generate a genesis key for testing
        from mycelium.engine.sentinel import KeyManager
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        genesis_pub, _ = key_manager.generate_keypair("genesis")
        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        nodes = registry.get_all_nodes()
        assert len(nodes) == 8  # 8 consolidated root departments
        
        # Check all root departments present
        node_ids = {n['id'] for n in nodes}
        expected = {
            "Finance", "Marketing", "Sales", "Engineering", "Operations",
            "Legal", "People & Comms", "Technology Platform"
        }
        assert node_ids == expected


def test_register_child_node():
    """Test registering a child node with valid lineage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        from mycelium.engine.sentinel import KeyManager, canonical_json
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        genesis_pub, _ = key_manager.generate_keypair("genesis")
        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        # Load parent's private key to sign the registration
        key_manager.load_private_key("Marketing")
        signature = key_manager.sign("Marketing", canonical_json({
            "id": "Marketing.Head.SEO",
            "parent": "Marketing",
            "domain": "marketing/seo",
            "type": "sub-agent",
            "spawn_reason": "keyword strategy needed dedicated capacity"
        }))
        
        success = registry.register_node({
            "id": "Marketing.Head.SEO",
            "parent": "Marketing",
            "domain": "marketing/seo",
            "type": "sub-agent",
            "spawn_reason": "keyword strategy needed dedicated capacity"
        }, "Marketing", signature)
        
        assert success
        node = registry.get_node("Marketing.Head.SEO")
        assert node is not None
        assert node['parent'] == "Marketing"
        assert node['type'] == "sub-agent"


def test_reject_orphan_node():
    """Test that orphan nodes (no valid parent) are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        from mycelium.engine.sentinel import KeyManager, canonical_json
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        genesis_pub, _ = key_manager.generate_keypair("genesis")
        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        # Try to register without a valid parent signature
        success = registry.register_node({
            "id": "Invalid.Node",
            "parent": "NonExistent.Parent",
            "domain": "invalid",
            "type": "sub-agent"
        }, "NonExistent.Parent", "ed25519:invalid_signature")
        
        assert not success
        assert registry.get_node("Invalid.Node") is None


def test_reject_wrong_lineage():
    """Test that nodes with wrong lineage naming are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        from mycelium.engine.sentinel import KeyManager, canonical_json
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        genesis_pub, _ = key_manager.generate_keypair("genesis")
        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        # Node ID doesn't start with parent + "."
        key_manager.load_private_key("Marketing")
        signature = key_manager.sign("Marketing", canonical_json({
            "id": "Wrong.Lineage",
            "parent": "Marketing",
            "domain": "marketing/wrong",
            "type": "sub-agent"
        }))
        
        success = registry.register_node({
            "id": "Wrong.Lineage",
            "parent": "Marketing",
            "domain": "marketing/wrong",
            "type": "sub-agent"
        }, "Marketing", signature)
        
        assert not success


def test_validate_all():
    """Test registry validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        from mycelium.engine.sentinel import KeyManager, canonical_json
        key_manager = KeyManager(os.path.join(tmpdir, "keys"))
        genesis_pub, _ = key_manager.generate_keypair("genesis")
        registry = NodeRegistry(registry_path, genesis_public_key=genesis_pub, key_manager=key_manager)
        
        # Add valid child
        key_manager.load_private_key("Marketing")
        signature = key_manager.sign("Marketing", canonical_json({
            "id": "Marketing.Head.SEO",
            "parent": "Marketing",
            "domain": "marketing/seo",
            "type": "sub-agent"
        }))
        
        registry.register_node({
            "id": "Marketing.Head.SEO",
            "parent": "Marketing",
            "domain": "marketing/seo",
            "type": "sub-agent"
        }, "Marketing", signature)
        
        errors = registry.validate_all()
        assert len(errors) == 0


if __name__ == "__main__":
    test_registry_initialization()
    test_register_child_node()
    test_reject_orphan_node()
    test_reject_wrong_lineage()
    test_validate_all()
    print("All registry tests passed!")