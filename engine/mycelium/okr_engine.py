#!/usr/bin/env python3
"""
OKR Engine — BCG-style OKR management for the Orchestrator.
Simple implementation for goal decomposition with JSON file persistence.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pathlib import Path
import uuid


class OKRLevel(Enum):
    CORPORATE = "corporate"
    DEPARTMENT = "department"
    TEAM = "team"
    INDIVIDUAL = "individual"


class KRType(Enum):
    METRIC = "metric"
    MILESTONE = "milestone"
    TASK = "task"


@dataclass
class KeyResult:
    id: str
    name: str
    type: KRType
    target: float
    unit: str
    weight: float = 1.0
    current: float = 0.0
    confidence: float = 0.5
    depends_on: List[str] = field(default_factory=list)

    def progress(self) -> float:
        if self.target == 0:
            return 0.0
        return min(self.current / self.target, 1.0)


@dataclass
class Objective:
    id: str
    name: str
    description: str
    level: OKRLevel
    owner: str
    parent_id: Optional[str] = None
    key_results: List[KeyResult] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def weighted_progress(self) -> float:
        if not self.key_results:
            return 0.0
        total_weight = sum(kr.weight for kr in self.key_results)
        if total_weight == 0:
            return 0.0
        return sum(kr.progress() * kr.weight for kr in self.key_results) / total_weight


class OKREngine:
    """Simple OKR engine for goal decomposition with JSON persistence."""

    def __init__(self, store_path: Optional[str] = None):
        self.store_path = Path(store_path or (Path.home() / ".kojiki" / "data" / "okrs.json"))
        self.objectives: Dict[str, Objective] = {}
        self.key_results: Dict[str, KeyResult] = {}
        self._load()

    def _load(self):
        """Load OKRs from JSON file."""
        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text())
                for o in data.get("objectives", []):
                    kr_list = [
                        KeyResult(**{**kr, "type": KRType(kr["type"])}) 
                        for kr in o.pop("key_results", [])
                    ]
                    obj = Objective(**{**o, "level": OKRLevel(o["level"])})
                    obj.key_results = kr_list
                    self.objectives[obj.id] = obj
                    for kr in kr_list:
                        self.key_results[kr.id] = kr
            except Exception:
                pass  # Corrupted file, start fresh

    def _save(self):
        """Save OKRs to JSON file."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"objectives": [
            {**asdict(o), "level": o.level.value,
             "key_results": [{**asdict(kr), "type": kr.type.value} for kr in o.key_results]}
            for o in self.objectives.values()
        ]}
        self.store_path.write_text(json.dumps(data, indent=2))

    def create_objective(
        self, 
        name: str, 
        description: str, 
        level: OKRLevel, 
        owner: str, 
        parent_id: Optional[str] = None,
        registry=None
    ) -> Objective:
        # Validate owner against registry if provided
        if registry and not registry.get_node(owner):
            raise ValueError(f"Objective owner '{owner}' is not a registered node")
        
        obj = Objective(
            id=f"OKR-{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            level=level,
            owner=owner,
            parent_id=parent_id
        )
        self.objectives[obj.id] = obj
        self._save()
        return obj

    def add_key_result(
        self, 
        objective_id: str, 
        name: str, 
        type: KRType, 
        target: float, 
        unit: str,
        weight: float = 1.0
    ) -> KeyResult:
        kr = KeyResult(
            id=f"KR-{uuid.uuid4().hex[:8]}",
            name=name,
            type=type,
            target=target,
            unit=unit,
            weight=weight
        )
        self.key_results[kr.id] = kr

        if objective_id in self.objectives:
            self.objectives[objective_id].key_results.append(kr)
        
        self._save()
        return kr

    def get_key_results(self, objective_id: str) -> List[KeyResult]:
        if objective_id in self.objectives:
            return self.objectives[objective_id].key_results
        return []

    def get_objective(self, objective_id: str) -> Optional[Objective]:
        return self.objectives.get(objective_id)

    def rollup_progress(self, objective_id: str) -> float:
        """Roll up progress from children to parent."""
        obj = self.objectives.get(objective_id)
        if not obj:
            return 0.0

        # Own progress
        own_progress = obj.weighted_progress()

        # Children progress
        children = [o for o in self.objectives.values() if o.parent_id == objective_id]
        if not children:
            return own_progress

        child_progress = sum(self.rollup_progress(c.id) for c in children) / len(children)

        # Weighted combination: 60% own, 40% children
        return 0.6 * own_progress + 0.4 * child_progress

    def decompose_okrs(
        self,
        problem: Dict[str, Any],
        dept_choices,
        registry=None
    ) -> Dict[str, Any]:
        """Phase 4: OKR Decomposition — corporate OKR → dept OKRs → team OKRs."""
        print("\n--- PHASE 4: OKR DECOMPOSITION ---")

        # Create corporate objective with Orchestrator owner (now registered)
        corporate_obj = self.create_objective(
            name=f"Corporate: {problem.get('goal', 'Strategic Goal')}",
            description=problem.get('goal', ''),
            level=OKRLevel.CORPORATE,
            owner="Orchestrator",
            registry=registry
        )

        dept_okrs = {}
        for choice in dept_choices:
            # Map specialist_name to registry node ID format
            # e.g., "finance-accounting" -> "Finance.Head", "marketing-brand" -> "Marketing.Head"
            dept_mapping = {
                "marketing-brand": "Marketing.Head",
                "sales-outbound": "Sales.Head",
                "finance-accounting": "Finance.Head",
                "engineering-platform": "Engineering.Head",
                "operations-ops": "Operations.Head",
                "legal-compliance": "Legal.Head",
                "people-hr": "People & Comms.Head",
                "ai-intelligence": "Technology Platform.Head"
            }
            owner_node = dept_mapping.get(choice.specialist_name, f"{choice.department}.Head")
            display_name = choice.department

            # Create department objective under corporate
            dept_obj = self.create_objective(
                name=f"Dept: {display_name}",
                description=f"Support corporate goal: {problem.get('goal', '')}",
                level=OKRLevel.DEPARTMENT,
                owner=owner_node,
                parent_id=corporate_obj.id,
                registry=registry
            )

            # Add default KRs based on department
            if choice.specialist_name == "marketing-brand":
                self.add_key_result(dept_obj.id, "Referral pipeline QoQ growth", KRType.METRIC, 0.15, "%")
                self.add_key_result(dept_obj.id, "Paid CAC reduction", KRType.METRIC, -0.20, "%")
            elif choice.specialist_name == "sales-outbound":
                self.add_key_result(dept_obj.id, "Qualified pipeline growth", KRType.METRIC, 0.25, "%")
                self.add_key_result(dept_obj.id, "Win rate improvement", KRType.METRIC, 0.10, "%")
            elif choice.specialist_name == "finance-accounting":
                self.add_key_result(dept_obj.id, "Budget variance", KRType.METRIC, -0.05, "%")
                self.add_key_result(dept_obj.id, "CAC/LTV ratio", KRType.METRIC, 3.0, "x")

            dept_okrs[choice.specialist_name] = {
                "objective_id": dept_obj.id,
                "name": dept_obj.name,
                "owner": dept_obj.owner,
                "key_results": [{"name": kr.name, "target": kr.target, "unit": kr.unit, "weight": kr.weight} for kr in self.get_key_results(dept_obj.id)]
            }

            print(f"  📊 {display_name}: {len(dept_okrs[choice.specialist_name]['key_results'])} KRs")

        return {
            "corporate_objective": {"id": corporate_obj.id, "name": corporate_obj.name, "owner": corporate_obj.owner},
            "department_okrs": dept_okrs
        }