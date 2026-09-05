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
        registry = NodeRegistry(registry_path)
        
        nodes = registry.get_all_nodes()
        assert len(nodes) == 20  # 20 root departments
        
        # Check all root departments present
        node_ids = {n['id'] for n in nodes}
        expected = {
            "Executive.Strategy", "Finance", "Marketing", "Sales", "Business.Development",
            "Customer.Success", "Product", "Engineering.Technology", "Operations",
            "Supply.Chain.Procurement", "Data.Analytics", "AI.Intelligence", "IT",
            "Security", "Legal", "Compliance.Risk", "People.HR", "Corporate.Development",
            "Communications.Public.Affairs", "Executive.Office.Chief.of.Staff"
        }
        assert node_ids == expected


def test_register_child_node():
    """Test registering a child node with valid lineage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        registry = NodeRegistry(registry_path)
        
        success = registry.register_node({
            "id": "Marketing.Head.SEO",
            "parent": "Marketing",
            "domain": "marketing/seo",
            "type": "sub-agent",
            "spawn_reason": "keyword strategy needed dedicated capacity"
        })
        
        assert success
        node = registry.get_node("Marketing.Head.SEO")
        assert node is not None
        assert node['parent'] == "Marketing"
        assert node['type'] == "sub-agent"


def test_reject_orphan_node():
    """Test that orphan nodes (no valid parent) are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        registry = NodeRegistry(registry_path)
        
        success = registry.register_node({
            "id": "Invalid.Node",
            "parent": "NonExistent.Parent",
            "domain": "invalid",
            "type": "sub-agent"
        })
        
        assert not success
        assert registry.get_node("Invalid.Node") is None


def test_reject_wrong_lineage():
    """Test that nodes with wrong lineage naming are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        registry = NodeRegistry(registry_path)
        
        # Node ID doesn't start with parent + "."
        success = registry.register_node({
            "id": "Wrong.Lineage",
            "parent": "Marketing",
            "domain": "marketing/wrong",
            "type": "sub-agent"
        })
        
        assert not success


def test_validate_all():
    """Test registry validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = os.path.join(tmpdir, "nodes.json")
        registry = NodeRegistry(registry_path)
        
        # Add valid child
        registry.register_node({
            "id": "Marketing.Head.SEO",
            "parent": "Marketing",
            "domain": "marketing/seo",
            "type": "sub-agent"
        })
        
        errors = registry.validate_all()
        assert len(errors) == 0


if __name__ == "__main__":
    test_registry_initialization()
    test_register_child_node()
    test_reject_orphan_node()
    test_reject_wrong_lineage()
    test_validate_all()
    print("All registry tests passed!")