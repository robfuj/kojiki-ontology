#!/usr/bin/env python3
"""
Deck DNA Cache - Cross-department deck template reuse.

Caches generated deck structures (slides, layouts, data bindings) by 
department + mode + structural hash. Subsequent runs with same context 
reuse cached template, only swapping dynamic data.

Expected token savings: ~60-70% on DECK stage.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import sys
from pathlib import Path as P
sys.path.insert(0, str(P(__file__).parent))
from postgres_registry import PostgresNodeRegistry
from postgres_persistence import get_cursor


@dataclass
class DeckDNAEntry:
    """Cached deck template structure."""
    cache_key: str
    department: str
    mode: str
    template_structure_hash: str
    template_data: Dict[str, Any]  # Full deck template (slides, layouts, placeholders)
    slides: List[Dict[str, Any]]   # Slide-level structure for granular reuse
    hit_count: int = 0
    created_at: str = ""
    expires_at: str = ""
    last_accessed: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeckDNACache:
    """Manages deck template caching with PostgreSQL backend."""
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl = timedelta(hours=ttl_hours)
        self.registry = PostgresNodeRegistry()
    
    def _compute_cache_key(self, department: str, mode: str, template_structure: Dict) -> str:
        """Generate deterministic cache key from department, mode, and template structure."""
        # Simplified: cache by department + mode only
        # Template structure is extracted from generated deck, not input content
        key_parts = f"{department}:{mode}"
        return hashlib.sha256(key_parts.encode()).hexdigest()[:32]
    
    def _extract_template_structure(self, deck_result: Dict) -> Dict:
        """Extract structural template from deck-builder result."""
        # deck_result contains the generated deck with full content
        # We extract the template structure (layouts, placeholders, bindings)
        slides = deck_result.get("slides", [])
        if not slides and "template_used" in deck_result:
            # Fallback: use template metadata
            return deck_result.get("template_structure", {})
        
        structure = {
            "slides": [],
            "theme": deck_result.get("theme", "default"),
            "master_layouts": deck_result.get("master_layouts", [])
        }
        
        for slide in slides:
            structure["slides"].append({
                "layout": slide.get("layout", "default"),
                "placeholders": slide.get("placeholders", []),
                "data_bindings": slide.get("data_bindings", {}),
                "content_type": slide.get("content_type", "text")
            })
        
        return structure
    
    def get(self, department: str, mode: str, template_structure: Dict) -> Optional[DeckDNAEntry]:
        """Retrieve cached deck template if valid."""
        cache_key = self._compute_cache_key(department, mode, template_structure)
        
        with get_cursor() as cur:
            # First update hit count and last_accessed atomically, then return new values
            cur.execute("""
                UPDATE deck_dna_cache
                SET hit_count = hit_count + 1, last_accessed = NOW()
                WHERE cache_key = %s AND expires_at > NOW()
                RETURNING cache_key, department, mode, template_structure_hash,
                       template_data, slides, hit_count, created_at, expires_at, last_accessed
            """, (cache_key,))
            row = cur.fetchone()
            
            if row:
                return DeckDNAEntry(
                    cache_key=row['cache_key'],
                    department=row['department'],
                    mode=row['mode'],
                    template_structure_hash=row['template_structure_hash'],
                    template_data=row['template_data'],
                    slides=row['slides'],
                    hit_count=row['hit_count'],
                    created_at=row['created_at'].isoformat() if row['created_at'] else "",
                    expires_at=row['expires_at'].isoformat() if row['expires_at'] else "",
                    last_accessed=row['last_accessed'].isoformat() if row['last_accessed'] else ""
                )
        return None
    
    def set(self, department: str, mode: str, template_structure: Dict, 
            deck_result: Dict) -> DeckDNAEntry:
        """Cache a new deck template."""
        cache_key = self._compute_cache_key(department, mode, template_structure)
        template_hash = hashlib.sha256(json.dumps(template_structure, sort_keys=True).encode()).hexdigest()[:16]
        
        now = datetime.utcnow()
        expires_at = now + self.ttl
        
        entry = DeckDNAEntry(
            cache_key=cache_key,
            department=department,
            mode=mode,
            template_structure_hash=template_hash,
            template_data=template_structure,
            slides=deck_result.get("slides", []),
            hit_count=0,
            created_at=now.isoformat() + "Z",
            expires_at=expires_at.isoformat() + "Z",
            last_accessed=now.isoformat() + "Z"
        )
        
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO deck_dna_cache 
                (cache_key, department, mode, template_structure_hash, template_data, slides,
                 hit_count, created_at, expires_at, last_accessed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cache_key) DO UPDATE SET
                    template_data = EXCLUDED.template_data,
                    slides = EXCLUDED.slides,
                    hit_count = EXCLUDED.hit_count,
                    expires_at = EXCLUDED.expires_at,
                    last_accessed = EXCLUDED.last_accessed
            """, (
                entry.cache_key, entry.department, entry.mode,
                entry.template_structure_hash,
                json.dumps(entry.template_data),
                json.dumps(entry.slides),
                entry.hit_count,
                entry.created_at,
                entry.expires_at,
                entry.last_accessed
            ))
        
        return entry
    
    def get_or_generate(self, department: str, mode: str, 
                        template_structure: Dict,
                        generator_func,
                        current_data: Optional[Dict] = None) -> Dict:
        """
        Get cached template or generate new one.
        
        Args:
            department: Department name (e.g., "marketing")
            mode: Deck mode ("native", "pdf", etc.)
            template_structure: Structural template definition
            generator_func: Function to generate deck if cache miss
            current_data: Current data to merge with cached template
            
        Returns:
            Deck result with cache metadata
        """
        cached = self.get(department, mode, template_structure)
        
        if cached:
            # Rehydrate deck from cached template + current data
            rehydrated = self._rehydrate_from_cache(cached, current_data or {})
            rehydrated["_cache"] = {"hit": True, "cache_key": cached.cache_key, "hits": cached.hit_count}
            return rehydrated
        
        # Cache miss - generate new
        deck_result = generator_func()
        
        # Cache the new template
        self.set(department, mode, template_structure, deck_result)
        deck_result["_cache"] = {"hit": False, "cache_key": self._compute_cache_key(department, mode, template_structure)}
        
        return deck_result
    
    def _rehydrate_from_cache(self, cached: DeckDNAEntry, current_data: Dict) -> Dict:
        """Rehydrate deck from cached template with current data."""
        # This merges the cached template structure with current data
        # The actual implementation depends on deck-builder's rehydration logic
        return {
            "slides": cached.slides,
            "template_data": cached.template_data,
            "data": current_data,
            "cached": True,
            "cache_key": cached.cache_key
        }
    
    def invalidate(self, department: str = None, mode: str = None) -> int:
        """Invalidate cache entries. Returns count of invalidated entries."""
        with get_cursor() as cur:
            if department and mode:
                cur.execute("""
                    DELETE FROM deck_dna_cache WHERE department = %s AND mode = %s
                """, (department, mode))
            elif department:
                cur.execute("DELETE FROM deck_dna_cache WHERE department = %s", (department,))
            else:
                cur.execute("DELETE FROM deck_dna_cache")
            return cur.rowcount
    
    def stats(self) -> Dict:
        """Get cache statistics."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    SUM(hit_count) as total_hits,
                    AVG(hit_count) as avg_hits,
                    department,
                    mode
                FROM deck_dna_cache
                WHERE expires_at > NOW()
                GROUP BY department, mode
            """)
            rows = cur.fetchall()
            return {
                "by_dept_mode": [dict(r) for r in rows],
                "total_entries": sum(r['total_entries'] for r in rows) if rows else 0,
                "total_hits": sum(r['total_hits'] for r in rows) if rows else 0
            }


def main():
    """CLI for cache operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deck DNA Cache")
    parser.add_argument("command", choices=["stats", "invalidate", "clear"])
    parser.add_argument("--department", help="Department filter")
    parser.add_argument("--mode", help="Mode filter")
    parser.add_argument("--ttl", type=int, default=24, help="TTL hours")
    args = parser.parse_args()
    
    cache = DeckDNACache(ttl_hours=args.ttl)
    
    if args.command == "stats":
        print(json.dumps(cache.stats(), indent=2))
    elif args.command == "invalidate":
        count = cache.invalidate(args.department, args.mode)
        print(f"Invalidated {count} entries")
    elif args.command == "clear":
        count = cache.invalidate()
        print(f"Cleared all {count} entries")


if __name__ == "__main__":
    main()