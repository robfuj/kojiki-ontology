"""
MYCELIUM Registry - Node lineage registry with naming validation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class NodeRegistry:
    """Registry for MYCELIUM nodes with lineage validation."""
    
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.root_departments = {
            "Executive.Strategy", "Finance", "Marketing", "Sales", "Business.Development",
            "Customer.Success", "Product", "Engineering.Technology", "Operations",
            "Supply.Chain.Procurement", "Data.Analytics", "AI.Intelligence", "IT",
            "Security", "Legal", "Compliance.Risk", "People.HR", "Corporate.Development",
            "Communications.Public.Affairs", "Executive.Office.Chief.of.Staff"
        }
        self.load()
    
    def load(self) -> None:
        """Load registry from file."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                self.nodes = {node['id']: node for node in data.get('nodes', [])}
        else:
            # Initialize with root departments
            for dept in self.root_departments:
                self.nodes[dept] = {
                    "id": dept,
                    "domain": dept.lower().replace('.', '/'),
                    "type": "agent",
                    "status": "active",
                    "pipeline_manifest_ref": f"bots/{dept.lower().replace('.', '-')}/manifest.json#transformation_pipeline",
                    "pipeline_validated": False
                }
            self.save()
    
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
    
    def register_node(self, node_data: Dict[str, Any]) -> bool:
        """Register a new node with validation."""
        node_id = node_data.get('id')
        parent_id = node_data.get('parent')
        
        if not self.validate_lineage(node_id, parent_id):
            return False
        
        if node_id in self.nodes:
            return False
        
        # Set timestamps
        node_data['spawned_at'] = node_data.get('spawned_at', datetime.utcnow().isoformat() + 'Z')
        node_data['status'] = node_data.get('status', 'active')
        
        self.nodes[node_id] = node_data
        self.save()
        return True
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all direct children of a node."""
        prefix = parent_id + "."
        return [node for node in self.nodes.values() if node['id'].startswith(prefix) and node['id'] != parent_id]
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes."""
        return list(self.nodes.values())
    
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
    registry = NodeRegistry("mycelium/registry/nodes.json")
    
    if len(sys.argv) < 2:
        print("Usage: python registry.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
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
            print(f"{node['id']} ({node['status']})")
    
    elif cmd == "add":
        if len(sys.argv) < 4:
            print("Usage: python registry.py add <node_id> <parent_id>")
            return
        node_id = sys.argv[2]
        parent_id = sys.argv[3]
        success = registry.register_node({"id": node_id, "parent": parent_id})
        print(f"Registration {'successful' if success else 'failed'}")


if __name__ == "__main__":
    main()