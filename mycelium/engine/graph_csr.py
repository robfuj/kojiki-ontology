#!/usr/bin/env python3
"""
MYCELIUM Graph - Cache-friendly CSR Edge Store.

Optimized for CPU cache locality using Compressed Sparse Row (CSR) format.
Replaces Dict[str, Dict] with contiguous arrays to eliminate pointer chasing.

Per Algorithmica.org: pointer chasing through dict-of-dicts causes massive
latency penalties. CSR layout enables streaming access with hardware prefetcher.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Iterator
from collections import defaultdict
import math
import bisect


class NodeIndex:
    """Maps KR string IDs to contiguous integer indices."""
    
    def __init__(self):
        self.kr_to_idx: Dict[str, int] = {}
        self.idx_to_kr: List[str] = []
    
    def get_or_create(self, kr: str) -> int:
        """Get index for KR, creating if needed."""
        if kr not in self.kr_to_idx:
            idx = len(self.idx_to_kr)
            self.kr_to_idx[kr] = idx
            self.idx_to_kr.append(kr)
        return self.kr_to_idx[kr]
    
    def get(self, kr: str) -> Optional[int]:
        return self.kr_to_idx.get(kr)
    
    def kr(self, idx: int) -> str:
        return self.idx_to_kr[idx]
    
    def __len__(self) -> int:
        return len(self.idx_to_kr)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"kr_to_idx": self.kr_to_idx, "idx_to_kr": self.idx_to_kr}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeIndex':
        idx = cls()
        idx.kr_to_idx = data["kr_to_idx"]
        idx.idx_to_kr = data["idx_to_kr"]
        return idx


class CSREdgeStore:
    """
    Cache-friendly edge store using CSR (Compressed Sparse Row) format.
    
    Layout:
    - edges_from: List[int]         # source node indices
    - edges_to: List[int]           # target node indices  
    - edges_weight: List[float]     # edge weights
    - edges_reciprocal: List[int]   # reciprocal exchange counts
    - edges_one_dir: List[int]      # one-directional exchange counts
    - edges_last_reinforced: List[str]  # ISO timestamps
    - edges_trigger: List[str]      # trigger descriptions
    - edges_required_data: List[str]
    - edges_acceptance: List[str]
    - edges_sla: List[str]
    - edges_exception: List[str]
    
    CSR index:
    - row_ptr: List[int]  # row_ptr[i] = start index in edges_* for node i's outgoing edges
    - row_ptr[i+1] - row_ptr[i] = out-degree of node i
    
    For incoming edges, we maintain a separate CSR (transpose).
    """
    
    def __init__(self, store_path: str):
        self.store_path = Path(store_path)
        
        # Node index mapping
        self.node_index = NodeIndex()
        
        # CSR arrays for outgoing edges
        self.edges_from: List[int] = []
        self.edges_to: List[int] = []
        self.edges_weight: List[float] = []
        self.edges_reciprocal: List[int] = []
        self.edges_one_dir: List[int] = []
        self.edges_last_reinforced: List[str] = []
        self.edges_trigger: List[str] = []
        self.edges_required_data: List[str] = []
        self.edges_acceptance: List[str] = []
        self.edges_sla: List[str] = []
        self.edges_exception: List[str] = []
        
        # CSR row pointers (built on demand, cached)
        self._row_ptr: Optional[List[int]] = None
        self._row_ptr_in: Optional[List[int]] = None
        self._in_edges_to: Optional[List[int]] = None
        self._in_edges_from: Optional[List[int]] = None
        self._in_edges_weight: Optional[List[float]] = None
        
        # Dirty flags
        self._dirty = True
        
        self.load()
    
    def _invalidate_csr(self):
        """Mark CSR structures as needing rebuild."""
        self._dirty = True
        self._row_ptr = None
        self._row_ptr_in = None
        self._in_edges_to = None
        self._in_edges_from = None
        self._in_edges_weight = None
    
    def _build_csr(self):
        """Build CSR row pointers from edge arrays. O(E) time."""
        if not self._dirty and self._row_ptr is not None:
            return
        
        n_nodes = len(self.node_index)
        n_edges = len(self.edges_from)
        
        # Build outgoing CSR
        out_counts = [0] * n_nodes
        for from_idx in self.edges_from:
            out_counts[from_idx] += 1
        
        self._row_ptr = [0] * (n_nodes + 1)
        for i in range(n_nodes):
            self._row_ptr[i + 1] = self._row_ptr[i] + out_counts[i]
        
        # Build incoming CSR (transpose)
        in_counts = [0] * n_nodes
        for to_idx in self.edges_to:
            in_counts[to_idx] += 1
        
        self._row_ptr_in = [0] * (n_nodes + 1)
        for i in range(n_nodes):
            self._row_ptr_in[i + 1] = self._row_ptr_in[i] + in_counts[i]
        
        # Fill incoming arrays
        self._in_edges_to = [0] * n_edges
        self._in_edges_from = [0] * n_edges
        self._in_edges_weight = [0.0] * n_edges
        
        # Use counters to place edges in correct positions
        out_pos = self._row_ptr[:-1].copy()
        in_pos = self._row_ptr_in[:-1].copy()
        
        for e in range(n_edges):
            from_idx = self.edges_from[e]
            to_idx = self.edges_to[e]
            weight = self.edges_weight[e]
            
            # Outgoing already in correct order (edges are appended in order)
            # For incoming, place at next available position
            pos = in_pos[to_idx]
            self._in_edges_to[pos] = from_idx
            self._in_edges_from[pos] = to_idx
            self._in_edges_weight[pos] = weight
            in_pos[to_idx] += 1
        
        self._dirty = False
    
    def load(self) -> None:
        """Load edges from JSON file, rebuild CSR."""
        if self.store_path.exists():
            with open(self.store_path, 'r') as f:
                data = json.load(f)
            
            # Load node index
            if "node_index" in data:
                self.node_index = NodeIndex.from_dict(data["node_index"])
            else:
                # Legacy: rebuild from edges
                self.node_index = NodeIndex()
            
            # Load edge arrays
            edges_data = data.get("edges", {})
            if isinstance(edges_data, dict) and "edges_from" in edges_data:
                # New CSR format
                self.edges_from = edges_data["edges_from"]
                self.edges_to = edges_data["edges_to"]
                self.edges_weight = edges_data["edges_weight"]
                self.edges_reciprocal = edges_data["edges_reciprocal"]
                self.edges_one_dir = edges_data["edges_one_dir"]
                self.edges_last_reinforced = edges_data["edges_last_reinforced"]
                self.edges_trigger = edges_data["edges_trigger"]
                self.edges_required_data = edges_data["edges_required_data"]
                self.edges_acceptance = edges_data["edges_acceptance"]
                self.edges_sla = edges_data["edges_sla"]
                self.edges_exception = edges_data["edges_exception"]
            else:
                # Legacy dict format - convert
                self._convert_legacy_format(edges_data)
            
            self._invalidate_csr()
        else:
            self._invalidate_csr()
    
    def _convert_legacy_format(self, edges_dict: Dict[str, Dict[str, Any]]):
        """Convert legacy dict format to CSR arrays."""
        for key, edge in edges_dict.items():
            from_kr = edge['from']
            to_kr = edge['to']
            
            from_idx = self.node_index.get_or_create(from_kr)
            to_idx = self.node_index.get_or_create(to_kr)
            
            self.edges_from.append(from_idx)
            self.edges_to.append(to_idx)
            self.edges_weight.append(edge.get('weight', 1.0))
            self.edges_reciprocal.append(edge.get('reciprocal_exchanges', 0))
            self.edges_one_dir.append(edge.get('one_directional_exchanges', 0))
            self.edges_last_reinforced.append(edge.get('last_reinforced', datetime.utcnow().isoformat() + 'Z'))
            self.edges_trigger.append(edge.get('trigger', ''))
            self.edges_required_data.append(edge.get('required_data', ''))
            self.edges_acceptance.append(edge.get('acceptance_criteria', ''))
            self.edges_sla.append(edge.get('sla', ''))
            self.edges_exception.append(edge.get('exception_path', ''))
    
    def save(self) -> None:
        """Save edges to JSON file in CSR format."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "node_index": self.node_index.to_dict(),
            "edges": {
                "edges_from": self.edges_from,
                "edges_to": self.edges_to,
                "edges_weight": self.edges_weight,
                "edges_reciprocal": self.edges_reciprocal,
                "edges_one_dir": self.edges_one_dir,
                "edges_last_reinforced": self.edges_last_reinforced,
                "edges_trigger": self.edges_trigger,
                "edges_required_data": self.edges_required_data,
                "edges_acceptance": self.edges_acceptance,
                "edges_sla": self.edges_sla,
                "edges_exception": self.edges_exception,
            }
        }
        
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def edge_key(self, from_kr: str, to_kr: str) -> str:
        """Generate edge key (for compatibility)."""
        return f"{from_kr}->{to_kr}"
    
    def _find_edge_index(self, from_idx: int, to_idx: int) -> Optional[int]:
        """Find edge index in CSR arrays. O(out-degree) scan."""
        self._build_csr()
        start = self._row_ptr[from_idx]
        end = self._row_ptr[from_idx + 1]
        
        for i in range(start, end):
            if self.edges_to[i] == to_idx:
                return i
        return None
    
    def add_edge(self, edge_data: Dict[str, Any]) -> None:
        """Add or update an edge."""
        from_kr = edge_data['from']
        to_kr = edge_data['to']
        
        from_idx = self.node_index.get_or_create(from_kr)
        to_idx = self.node_index.get_or_create(to_kr)
        
        # Check if edge exists
        existing_idx = self._find_edge_index(from_idx, to_idx)
        
        now = datetime.utcnow().isoformat() + 'Z'
        
        if existing_idx is not None:
            # Update existing edge
            self.edges_weight[existing_idx] = edge_data.get('weight', self.edges_weight[existing_idx])
            self.edges_trigger[existing_idx] = edge_data.get('trigger', self.edges_trigger[existing_idx])
            self.edges_required_data[existing_idx] = edge_data.get('required_data', self.edges_required_data[existing_idx])
            self.edges_acceptance[existing_idx] = edge_data.get('acceptance_criteria', self.edges_acceptance[existing_idx])
            self.edges_sla[existing_idx] = edge_data.get('sla', self.edges_sla[existing_idx])
            self.edges_exception[existing_idx] = edge_data.get('exception_path', self.edges_exception[existing_idx])
            self.edges_last_reinforced[existing_idx] = now
        else:
            # Append new edge
            self.edges_from.append(from_idx)
            self.edges_to.append(to_idx)
            self.edges_weight.append(edge_data.get('weight', 1.0))
            self.edges_reciprocal.append(edge_data.get('reciprocal_exchanges', 0))
            self.edges_one_dir.append(edge_data.get('one_directional_exchanges', 0))
            self.edges_last_reinforced.append(now)
            self.edges_trigger.append(edge_data.get('trigger', ''))
            self.edges_required_data.append(edge_data.get('required_data', ''))
            self.edges_acceptance.append(edge_data.get('acceptance_criteria', ''))
            self.edges_sla.append(edge_data.get('sla', ''))
            self.edges_exception.append(edge_data.get('exception_path', ''))
        
        self._invalidate_csr()
        self.save()
    
    def get_edge(self, from_kr: str, to_kr: str) -> Optional[Dict[str, Any]]:
        """Get edge by from/to KR."""
        from_idx = self.node_index.get(from_kr)
        to_idx = self.node_index.get(to_kr)
        
        if from_idx is None or to_idx is None:
            return None
        
        edge_idx = self._find_edge_index(from_idx, to_idx)
        if edge_idx is None:
            return None
        
        return self._edge_to_dict(edge_idx)
    
    def _edge_to_dict(self, edge_idx: int) -> Dict[str, Any]:
        """Convert CSR edge entry to dict."""
        from_idx = self.edges_from[edge_idx]
        to_idx = self.edges_to[edge_idx]
        return {
            "from": self.node_index.kr(from_idx),
            "to": self.node_index.kr(to_idx),
            "weight": self.edges_weight[edge_idx],
            "reciprocal_exchanges": self.edges_reciprocal[edge_idx],
            "one_directional_exchanges": self.edges_one_dir[edge_idx],
            "last_reinforced": self.edges_last_reinforced[edge_idx],
            "trigger": self.edges_trigger[edge_idx],
            "required_data": self.edges_required_data[edge_idx],
            "acceptance_criteria": self.edges_acceptance[edge_idx],
            "sla": self.edges_sla[edge_idx],
            "exception_path": self.edges_exception[edge_idx],
        }
    
    def get_outgoing(self, from_kr: str) -> List[Dict[str, Any]]:
        """Get all outgoing edges from a KR. O(out-degree) - cache friendly!"""
        from_idx = self.node_index.get(from_kr)
        if from_idx is None:
            return []
        
        self._build_csr()
        start = self._row_ptr[from_idx]
        end = self._row_ptr[from_idx + 1]
        
        return [self._edge_to_dict(i) for i in range(start, end)]
    
    def get_incoming(self, to_kr: str) -> List[Dict[str, Any]]:
        """Get all incoming edges to a KR. Resolves through forward arrays for complete data."""
        to_idx = self.node_index.get(to_kr)
        if to_idx is None:
            return []
        
        self._build_csr()
        start = self._row_ptr_in[to_idx]
        end = self._row_ptr_in[to_idx + 1]
        
        edges = []
        for i in range(start, end):
            from_idx = self._in_edges_to[i]
            # Resolve through forward arrays to get complete edge data
            edge_idx = self._find_edge_index(from_idx, to_idx)
            if edge_idx is not None:
                edges.append(self._edge_to_dict(edge_idx))
            else:
                # Fallback (shouldn't happen if CSR is consistent)
                edges.append({
                    "from": self.node_index.kr(from_idx),
                    "to": self.node_index.kr(to_idx),
                    "weight": self._in_edges_weight[i],
                    "reciprocal_exchanges": self.edges_reciprocal[edge_idx] if edge_idx is not None else 0,
                    "one_directional_exchanges": self.edges_one_dir[edge_idx] if edge_idx is not None else 0,
                    "last_reinforced": "",
                    "trigger": "",
                    "required_data": "",
                    "acceptance_criteria": "",
                    "sla": "",
                    "exception_path": "",
                })
        return edges
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all edges as list of dicts."""
        return [self._edge_to_dict(i) for i in range(len(self.edges_from))]
    
    def get_edge_count(self) -> int:
        return len(self.edges_from)
    
    def get_node_count(self) -> int:
        return len(self.node_index)
    
    def iterate_outgoing(self, from_kr: str) -> Iterator[Tuple[int, int, float]]:
        """Iterate outgoing edges as (from_idx, to_idx, weight) tuples. Zero-allocation!"""
        from_idx = self.node_index.get(from_kr)
        if from_idx is None:
            return
        
        self._build_csr()
        start = self._row_ptr[from_idx]
        end = self._row_ptr[from_idx + 1]
        
        for i in range(start, end):
            yield (from_idx, self.edges_to[i], self.edges_weight[i])
    
    def iterate_all(self) -> Iterator[Tuple[int, int, float]]:
        """Iterate all edges as (from_idx, to_idx, weight) tuples. Zero-allocation!"""
        for i in range(len(self.edges_from)):
            yield (self.edges_from[i], self.edges_to[i], self.edges_weight[i])
    
    def update_exchange_counts(self, from_kr: str, to_kr: str, reciprocal: bool = True) -> None:
        """Update exchange counts after signal propagation."""
        from_idx = self.node_index.get(from_kr)
        to_idx = self.node_index.get(to_kr)
        
        if from_idx is None or to_idx is None:
            return
        
        edge_idx = self._find_edge_index(from_idx, to_idx)
        if edge_idx is not None:
            if reciprocal:
                self.edges_reciprocal[edge_idx] += 1
            else:
                self.edges_one_dir[edge_idx] += 1
            self.edges_last_reinforced[edge_idx] = datetime.utcnow().isoformat() + 'Z'
            self.save()


# Backward compatibility wrapper
class EdgeStore:
    """Legacy-compatible wrapper around CSREdgeStore."""
    
    def __init__(self, store_path: str):
        self.csr_store = CSREdgeStore(store_path)
        self.store_path = self.csr_store.store_path
        self.edges = {}  # Kept for API compatibility but not used
    
    def load(self) -> None:
        self.csr_store.load()
    
    def save(self) -> None:
        self.csr_store.save()
    
    def edge_key(self, from_kr: str, to_kr: str) -> str:
        return self.csr_store.edge_key(from_kr, to_kr)
    
    def add_edge(self, edge_data: Dict[str, Any]) -> None:
        self.csr_store.add_edge(edge_data)
    
    def get_edge(self, from_kr: str, to_kr: str) -> Optional[Dict[str, Any]]:
        return self.csr_store.get_edge(from_kr, to_kr)
    
    def get_outgoing(self, from_kr: str) -> List[Dict[str, Any]]:
        return self.csr_store.get_outgoing(from_kr)
    
    def get_incoming(self, to_kr: str) -> List[Dict[str, Any]]:
        return self.csr_store.get_incoming(to_kr)
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        return self.csr_store.get_all_edges()
    
    def update_exchange_counts(self, from_kr: str, to_kr: str, reciprocal: bool = True) -> None:
        self.csr_store.update_exchange_counts(from_kr, to_kr, reciprocal)


if __name__ == "__main__":
    # Quick benchmark
    import time
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        store = CSREdgeStore(f"{tmpdir}/edges.json")
        
        # Add 10000 edges
        n = 10000
        for i in range(n):
            store.add_edge({
                "from": f"KR-{i % 100}",
                "to": f"KR-{(i + 1) % 100}",
                "weight": 1.0,
            })
        
        print(f"Nodes: {store.get_node_count()}, Edges: {store.get_edge_count()}")
        
        # Benchmark get_outgoing (should be fast with CSR)
        start = time.perf_counter()
        for _ in range(100):
            _ = store.get_outgoing("KR-50")
        elapsed = time.perf_counter() - start
        print(f"get_outgoing x100: {elapsed*1000:.2f}ms")
        
        # Benchmark iterate_all
        start = time.perf_counter()
        total_weight = 0.0
        for _ in range(100):
            for _, _, w in store.iterate_all():
                total_weight += w
        elapsed = time.perf_counter() - start
        print(f"iterate_all x100: {elapsed*1000:.2f}ms (total weight: {total_weight})")
        
        # Compare with legacy
        legacy = store.csr_store  # Same object, but test dict access
        start = time.perf_counter()
        for _ in range(100):
            _ = legacy.get_all_edges()  # Creates list of dicts
        elapsed = time.perf_counter() - start
        print(f"get_all_edges (dict alloc) x100: {elapsed*1000:.2f}ms")