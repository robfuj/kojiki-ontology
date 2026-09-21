#!/usr/bin/env python3
"""
Abstract base class for MYCELIUM Registry implementations.

Defines the common interface that both JSON-based (NodeRegistry) and
PostgreSQL-based (PostgresNodeRegistry) registries must implement.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class RegistryBase(ABC):
    """Abstract base class for MYCELIUM registry implementations."""

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        pass

    @abstractmethod
    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all direct children of a node."""
        pass

    @abstractmethod
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes."""
        pass

    @abstractmethod
    def register_node(self, node_data: Dict[str, Any], signer: str, signature: str) -> bool:
        """Register a new node with validation."""
        pass

    @abstractmethod
    def issue_key_if_missing(self, node_id: str, actor: str) -> bool:
        """Admin repair: issue a key for a node that has no key."""
        pass

    @abstractmethod
    def rotate_key(self, node_id: str, authorized_by: str) -> tuple:
        """Admin rotation: generate a new keypair for an active node."""
        pass

    @abstractmethod
    def update_decision_rights(self, node_id: str, decision_rights: Dict[str, Any],
                               signer: Optional[str] = None, signature: Optional[str] = None) -> bool:
        """Update Decision Rights for a node from STRATEGY output."""
        pass

    @abstractmethod
    def get_decision_rights(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get full Decision Rights object for a node."""
        pass

    @abstractmethod
    def get_decision_right(self, node_id: str) -> Optional[str]:
        """Get primary Decision Right (own) for a node."""
        pass

    @abstractmethod
    def register_node_governance(self, node_id: str, domain: str, node_type: str,
                                 parent_id: Optional[str]) -> bool:
        """Governance-initiated node registration."""
        pass

    @abstractmethod
    def validate_all(self) -> List[str]:
        """Validate entire registry, return list of errors."""
        pass

    @abstractmethod
    def _validate_lineage(self, node_id: str, parent_id: Optional[str]) -> bool:
        """Validate that node_id follows lineage naming convention."""
        pass

    @abstractmethod
    def _verify_signer_authority(self, signer: str, node_id: str) -> bool:
        """Verify that signer has authority over node_id."""
        pass

    @abstractmethod
    def _audit(self, event_type: str, node_id: str, actor: str, detail: Any) -> None:
        """Emit a lifecycle audit event to SENTINEL."""
        pass