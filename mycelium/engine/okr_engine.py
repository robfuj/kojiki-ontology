"""
OKR Engine - Objectives and Key Results management integrated with MYCELIUM.

Based on BCG's "Unleashing the Power of OKRs" methodology:
- Objectives: qualitative, ambitious, time-bound, customer/outcome-focused
- Key Results: quantitative, measurable, 3-5 per objective, leading indicators
- Integration: OKRs cascade from corporate → department → team → individual
- Maturity: standardized checklist, continuous assessment
- Accountability: owners own outcomes, not just outputs
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from psycopg2.extras import Json
import sys
from pathlib import Path
POSTGRES_EXT = Path(__file__).parent.parent / "extensions" / "postgres"
if POSTGRES_EXT.exists():
    sys.path.insert(0, str(POSTGRES_EXT))
from postgres_persistence import get_cursor


class OKRLevel(Enum):
    """Hierarchical level of OKR."""
    CORPORATE = "corporate"
    DEPARTMENT = "department"
    TEAM = "team"
    INDIVIDUAL = "individual"


class OKRStatus(Enum):
    """OKR status."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class KRType(Enum):
    """Key Result type."""
    METRIC = "metric"           # Quantitative metric (revenue, users, %)
    MILESTONE = "milestone"     # Binary milestone (launch, hire, complete)
    TASK = "task"              # Task completion


@dataclass
class KeyResult:
    """Single Key Result."""
    kr_id: str
    objective_id: str
    description: str
    kr_type: str  # KRType value as string
    target: float
    current: float = 0.0
    unit: str = ""  # "%", "$", "count", "score"
    weight: float = 1.0
    source: str = ""  # Data source for measurement
    frequency: str = "weekly"  # daily, weekly, monthly, quarterly
    confidence: float = 0.5  # 0-1 confidence in achievability
    is_leading: bool = True  # Leading vs lagging indicator


@dataclass
class Objective:
    """Objective with Key Results."""
    objective_id: str
    title: str
    description: str
    level: OKRLevel
    owner_node: str  # MYCELIUM node ID (e.g., "Marketing.Growth")
    parent_objective_id: Optional[str] = None
    key_results: List[KeyResult] = field(default_factory=list)
    status: OKRStatus = OKRStatus.DRAFT
    start_date: str = ""
    end_date: str = ""  # Usually quarter-end
    created_at: str = ""
    updated_at: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class OKRChecklistItem:
    """BCG-style OKR maturity checklist item."""
    category: str
    criterion: str
    score: float = 0.0  # 0-1
    notes: str = ""


class OKREngine:
    """Manages OKRs integrated with MYCELIUM registry and governance."""
    
    def __init__(self):
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure OKR tables exist."""
        with get_cursor() as cur:
            # OKR Objectives table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS okr_objectives (
                    objective_id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    level VARCHAR(50) NOT NULL,
                    owner_node VARCHAR(255) NOT NULL REFERENCES mycelium_nodes(id),
                    parent_objective_id VARCHAR(255) REFERENCES okr_objectives(objective_id),
                    key_results JSONB NOT NULL DEFAULT '[]',
                    status VARCHAR(50) NOT NULL DEFAULT 'draft',
                    start_date DATE,
                    end_date DATE,
                    tags JSONB DEFAULT '[]',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # OKR Progress tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS okr_progress (
                    id BIGSERIAL PRIMARY KEY,
                    objective_id VARCHAR(255) NOT NULL REFERENCES okr_objectives(objective_id),
                    kr_id VARCHAR(255) NOT NULL,
                    recorded_value FLOAT NOT NULL,
                    recorded_at TIMESTAMPTZ DEFAULT NOW(),
                    recorded_by VARCHAR(255),
                    source VARCHAR(255),
                    notes TEXT
                )
            """)
            
            # OKR Maturity assessments
            cur.execute("""
                CREATE TABLE IF NOT EXISTS okr_maturity (
                    id BIGSERIAL PRIMARY KEY,
                    objective_id VARCHAR(255) NOT NULL REFERENCES okr_objectives(objective_id),
                    assessment_date DATE DEFAULT CURRENT_DATE,
                    category VARCHAR(100) NOT NULL,
                    criterion VARCHAR(255) NOT NULL,
                    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 1),
                    notes TEXT,
                    assessed_by VARCHAR(255)
                )
            """)
            
            # OKR-KPI alignment
            cur.execute("""
                CREATE TABLE IF NOT EXISTS okr_kpi_links (
                    id BIGSERIAL PRIMARY KEY,
                    objective_id VARCHAR(255) NOT NULL REFERENCES okr_objectives(objective_id),
                    kpi_name VARCHAR(255) NOT NULL,
                    kpi_target FLOAT,
                    alignment_type VARCHAR(50),  -- 'direct', 'proxy', 'enabler'
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_okr_owner ON okr_objectives(owner_node)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_okr_parent ON okr_objectives(parent_objective_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_okr_status ON okr_objectives(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_okr_dates ON okr_objectives(start_date, end_date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_okr_progress_obj ON okr_progress(objective_id, kr_id)")
    
    def create_objective(self, objective: Objective) -> str:
        """Create a new OKR objective."""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO okr_objectives 
                (objective_id, title, description, level, owner_node, parent_objective_id,
                 key_results, status, start_date, end_date, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (objective_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    key_results = EXCLUDED.key_results,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """, (
                objective.objective_id,
                objective.title,
                objective.description,
                objective.level.value,
                objective.owner_node,
                objective.parent_objective_id,
                Json([asdict(kr) for kr in objective.key_results]),
                objective.status.value,
                objective.start_date or None,
                objective.end_date or None,
                Json(objective.tags)
            ))
        return objective.objective_id
    
    def get_objective(self, objective_id: str) -> Optional[Objective]:
        """Get objective by ID."""
        with get_cursor() as cur:
            cur.execute("SELECT * FROM okr_objectives WHERE objective_id = %s", (objective_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_objective(row)
    
    def get_objectives_by_owner(self, owner_node: str, status: Optional[OKRStatus] = None) -> List[Objective]:
        """Get all objectives for a MYCELIUM node."""
        with get_cursor() as cur:
            if status:
                cur.execute("""
                    SELECT * FROM okr_objectives 
                    WHERE owner_node = %s AND status = %s
                    ORDER BY start_date DESC
                """, (owner_node, status.value))
            else:
                cur.execute("""
                    SELECT * FROM okr_objectives 
                    WHERE owner_node = %s
                    ORDER BY start_date DESC
                """, (owner_node,))
            return [self._row_to_objective(row) for row in cur.fetchall()]
    
    def get_cascade(self, objective_id: str) -> List[Objective]:
        """Get full cascade tree from an objective down."""
        with get_cursor() as cur:
            cur.execute("""
                WITH RECURSIVE cascade AS (
                    SELECT * FROM okr_objectives WHERE objective_id = %s
                    UNION ALL
                    SELECT o.* FROM okr_objectives o
                    JOIN cascade c ON o.parent_objective_id = c.objective_id
                )
                SELECT * FROM cascade ORDER BY level, start_date
            """, (objective_id,))
            return [self._row_to_objective(row) for row in cur.fetchall()]
    
    def update_kr_progress(self, objective_id: str, kr_id: str, value: float, 
                           recorded_by: str = "", source: str = "", notes: str = "") -> Dict:
        """Update Key Result progress and return current status."""
        objective = self.get_objective(objective_id)
        if not objective:
            raise ValueError(f"Objective {objective_id} not found")
        
        kr = next((k for k in objective.key_results if k.kr_id == kr_id), None)
        if not kr:
            raise ValueError(f"Key Result {kr_id} not found in objective {objective_id}")
        
        old_value = kr.current
        kr.current = value
        
        # Record progress
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO okr_progress (objective_id, kr_id, recorded_value, recorded_by, source, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (objective_id, kr_id, value, recorded_by, source, notes))
            
            # Update the objective's key_results JSON
            cur.execute("""
                UPDATE okr_objectives 
                SET key_results = %s, updated_at = NOW()
                WHERE objective_id = %s
            """, (Json([asdict(k) for k in objective.key_results]), objective_id))
        
        return {
            "kr_id": kr_id,
            "old_value": old_value,
            "new_value": value,
            "progress_pct": (value / kr.target * 100) if kr.target != 0 else 0,
            "on_track": value >= kr.target * 0.7  # 70% threshold
        }
    
    def assess_maturity(self, objective_id: str, assessments: List[Dict], assessed_by: str) -> Dict:
        """Record BCG-style OKR maturity assessment."""
        results = []
        with get_cursor() as cur:
            for a in assessments:
                cur.execute("""
                    INSERT INTO okr_maturity (objective_id, category, criterion, score, notes, assessed_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (objective_id, a.get("category"), a.get("criterion"), 
                      a.get("score", 0), a.get("notes", ""), assessed_by))
                results.append({
                    "category": a.get("category"),
                    "criterion": a.get("criterion"),
                    "score": a.get("score")
                })
        
        # Calculate overall maturity
        total_score = sum(a.get("score", 0) for a in assessments)
        avg_score = total_score / len(assessments) if assessments else 0
        
        maturity_level = "nascent"
        if avg_score >= 0.8:
            maturity_level = "optimized"
        elif avg_score >= 0.6:
            maturity_level = "standardized"
        elif avg_score >= 0.4:
            maturity_level = "developing"
        
        return {
            "objective_id": objective_id,
            "overall_score": avg_score,
            "maturity_level": maturity_level,
            "assessments": results
        }
    
    def link_kpi(self, objective_id: str, kpi_name: str, kpi_target: float = None, 
                 alignment_type: str = "direct") -> bool:
        """Link OKR to KPI for integrated steering."""
        with get_cursor() as cur:
            cur.execute("""
                INSERT INTO okr_kpi_links (objective_id, kpi_name, kpi_target, alignment_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (objective_id, kpi_name, kpi_target, alignment_type))
        return True
    
    def get_dashboard(self, owner_node: str = None, level: OKRLevel = None) -> Dict:
        """Get OKR dashboard for owner or level."""
        with get_cursor() as cur:
            where_clauses = ["1=1"]
            params = []
            
            if owner_node:
                where_clauses.append("owner_node = %s")
                params.append(owner_node)
            if level:
                where_clauses.append("level = %s")
                params.append(level.value)
            
            where_sql = " AND ".join(where_clauses)
            
            cur.execute(f"""
                SELECT * FROM okr_objectives 
                WHERE {where_sql}
                ORDER BY level, start_date DESC
            """, params)
            objectives = [self._row_to_objective(row) for row in cur.fetchall()]
            
            # Calculate summary stats
            total = len(objectives)
            active = len([o for o in objectives if o.status == OKRStatus.ACTIVE])
            completed = len([o for o in objectives if o.status == OKRStatus.COMPLETED])
            
            # Average progress across all KRs
            all_krs = []
            for obj in objectives:
                for kr in obj.key_results:
                    all_krs.append(kr)
            
            avg_progress = 0
            if all_krs:
                avg_progress = sum(kr.current / kr.target * 100 if kr.target else 0 
                                   for kr in all_krs) / len(all_krs)
            
            return {
                "summary": {
                    "total_objectives": total,
                    "active": active,
                    "completed": completed,
                    "avg_kr_progress_pct": round(avg_progress, 1)
                },
                "objectives": objectives
            }
    
    def _row_to_objective(self, row) -> Objective:
        """Convert database row to Objective."""
        krs = []
        for kr_data in row.get('key_results', []):
            krs.append(KeyResult(
                kr_id=kr_data['kr_id'],
                objective_id=kr_data['objective_id'],
                description=kr_data['description'],
                kr_type=kr_data.get('kr_type', 'metric'),  # Already a string
                target=kr_data['target'],
                current=kr_data.get('current', 0.0),
                unit=kr_data.get('unit', ''),
                weight=kr_data.get('weight', 1.0),
                source=kr_data.get('source', ''),
                frequency=kr_data.get('frequency', 'weekly'),
                confidence=kr_data.get('confidence', 0.5),
                is_leading=kr_data.get('is_leading', True)
            ))
        
        return Objective(
            objective_id=row['objective_id'],
            title=row['title'],
            description=row['description'],
            level=OKRLevel(row['level']),
            owner_node=row['owner_node'],
            parent_objective_id=row.get('parent_objective_id'),
            key_results=krs,
            status=OKRStatus(row['status']),
            start_date=str(row['start_date']) if row.get('start_date') else "",
            end_date=str(row['end_date']) if row.get('end_date') else "",
            created_at=str(row['created_at']) if row.get('created_at') else "",
            updated_at=str(row['updated_at']) if row.get('updated_at') else "",
            tags=row.get('tags', [])
        )

    # ============================================================
    # UI-READY API ENDPOINTS (for eventual frontend)
    # ============================================================

    def get_objective_tree(self, root_objective_id: str = None, 
                           owner_node: str = None,
                           include_completed: bool = True) -> Dict:
        """
        Get full objective tree for UI rendering.
        Returns nested structure with computed progress at each level.
        """
        if root_objective_id:
            # Get specific cascade
            objectives = self.get_cascade(root_objective_id)
        elif owner_node:
            objectives = self.get_objectives_by_owner(owner_node)
            if not include_completed:
                objectives = [o for o in objectives if o.status != OKRStatus.COMPLETED]
        else:
            # All objectives - build forest
            all_objs = self.get_all_objectives()
            if not include_completed:
                all_objs = [o for o in all_objs if o.status != OKRStatus.COMPLETED]
            # Find roots (no parent or parent not in set)
            obj_map = {o.objective_id: o for o in all_objs}
            roots = [o for o in all_objs if not o.parent_objective_id or o.parent_objective_id not in obj_map]
            objectives = roots
        
        # Build tree with computed progress
        obj_map = {o.objective_id: o for o in self.get_all_objectives()}
        tree = []
        
        for obj in objectives:
            tree.append(self._build_objective_node(obj, obj_map))
        
        return {
            "tree": tree,
            "summary": self._compute_tree_summary(tree)
        }
    
    def get_all_objectives(self) -> List[Objective]:
        """Get all objectives from database."""
        with get_cursor() as cur:
            cur.execute("SELECT * FROM okr_objectives ORDER BY level, start_date DESC")
            return [self._row_to_objective(row) for row in cur.fetchall()]
    
    def _build_objective_node(self, obj: Objective, obj_map: Dict) -> Dict:
        """Build a tree node with computed progress."""
        # Calculate this objective's progress
        kr_progress = self._calculate_objective_progress(obj)
        
        # Find children
        children = [o for o in obj_map.values() if o.parent_objective_id == obj.objective_id]
        child_nodes = [self._build_objective_node(child, obj_map) for child in children]
        
        # Aggregate progress from children (if no KRs of its own)
        aggregated_progress = kr_progress
        if not obj.key_results and child_nodes:
            # Average of children's progress weighted by their KR counts
            total_krs = sum(n['kr_count'] for n in child_nodes)
            if total_krs > 0:
                aggregated_progress = sum(n['progress_pct'] * n['kr_count'] for n in child_nodes) / total_krs
        
        return {
            "objective_id": obj.objective_id,
            "title": obj.title,
            "description": obj.description,
            "level": obj.level.value,
            "owner_node": obj.owner_node,
            "parent_objective_id": obj.parent_objective_id,
            "status": obj.status.value,
            "start_date": obj.start_date,
            "end_date": obj.end_date,
            "tags": obj.tags,
            "progress_pct": round(aggregated_progress, 1),
            "kr_progress": kr_progress,
            "kr_count": len(obj.key_results),
            "key_results": [
                {
                    "kr_id": kr.kr_id,
                    "description": kr.description,
                    "target": kr.target,
                    "current": kr.current,
                    "unit": kr.unit,
                    "progress_pct": round((kr.current / kr.target * 100) if kr.target else 0, 1),
                    "weight": kr.weight,
                    "is_leading": kr.is_leading,
                    "source": kr.source,
                    "frequency": kr.frequency,
                    "confidence": kr.confidence
                }
                for kr in obj.key_results
            ],
            "children": child_nodes,
            "child_count": len(child_nodes),
            "maturity_score": self._get_latest_maturity(obj.objective_id)
        }
    
    def _calculate_objective_progress(self, obj: Objective) -> float:
        """Calculate weighted progress for an objective's own KRs."""
        if not obj.key_results:
            return 0.0
        
        total_weight = sum(kr.weight for kr in obj.key_results)
        if total_weight == 0:
            return 0.0
        
        weighted_progress = 0.0
        for kr in obj.key_results:
            if kr.target != 0:
                kr_pct = min(kr.current / kr.target * 100, 100)  # Cap at 100%
            else:
                kr_pct = 100.0 if kr.current >= kr.target else 0.0
            weighted_progress += kr_pct * kr.weight
        
        return weighted_progress / total_weight
    
    def _compute_tree_summary(self, tree: List[Dict]) -> Dict:
        """Compute summary stats for tree."""
        all_nodes = []
        
        def collect_nodes(nodes):
            for n in nodes:
                all_nodes.append(n)
                collect_nodes(n['children'])
        
        collect_nodes(tree)
        
        total_krs = sum(n['kr_count'] for n in all_nodes)
        completed_krs = sum(1 for n in all_nodes for kr in n['key_results'] if kr['current'] >= kr['target'])
        
        return {
            "total_objectives": len(all_nodes),
            "active_objectives": len([n for n in all_nodes if n['status'] == 'active']),
            "completed_objectives": len([n for n in all_nodes if n['status'] == 'completed']),
            "total_krs": total_krs,
            "completed_krs": completed_krs,
            "kr_completion_pct": round(completed_krs / total_krs * 100, 1) if total_krs > 0 else 0,
            "avg_progress_pct": round(sum(n['progress_pct'] for n in all_nodes) / len(all_nodes), 1) if all_nodes else 0
        }
    
    def _get_latest_maturity(self, objective_id: str) -> Optional[float]:
        """Get latest maturity assessment score."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT AVG(score) as avg_score FROM okr_maturity
                WHERE objective_id = %s
                AND assessment_date = (SELECT MAX(assessment_date) FROM okr_maturity WHERE objective_id = %s)
            """, (objective_id, objective_id))
            row = cur.fetchone()
            return round(row['avg_score'], 2) if row and row['avg_score'] is not None else None
    
    def get_progress_timeseries(self, objective_id: str, kr_id: str = None, 
                                days: int = 90) -> List[Dict]:
        """Get progress timeseries for charting."""
        with get_cursor() as cur:
            if kr_id:
                cur.execute("""
                    SELECT recorded_at, recorded_value, recorded_by, source
                    FROM okr_progress
                    WHERE objective_id = %s AND kr_id = %s
                    AND recorded_at >= NOW() - INTERVAL '%s days'
                    ORDER BY recorded_at
                """, (objective_id, kr_id, days))
            else:
                # Aggregate all KRs for objective
                cur.execute("""
                    SELECT recorded_at, kr_id, recorded_value
                    FROM okr_progress
                    WHERE objective_id = %s
                    AND recorded_at >= NOW() - INTERVAL '%s days'
                    ORDER BY recorded_at, kr_id
                """, (objective_id, days))
            return [dict(row) for row in cur.fetchall()]
    
    def get_department_progress(self, department: str) -> Dict:
        """Get aggregated progress for a department (by owner_node prefix, case-insensitive)."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT * FROM okr_objectives
                WHERE LOWER(owner_node) LIKE LOWER(%s)
                ORDER BY level, start_date DESC
            """, (f"{department}.%",))
            objectives = [self._row_to_objective(row) for row in cur.fetchall()]
        
        # Build tree and compute
        obj_map = {o.objective_id: o for o in objectives}
        roots = [o for o in objectives if not o.parent_objective_id or o.parent_objective_id not in obj_map]
        
        tree = [self._build_objective_node(root, obj_map) for root in roots]
        summary = self._compute_tree_summary(tree)
        
        return {
            "department": department,
            "tree": tree,
            "summary": summary
        }
    
    def get_global_heatmap(self) -> Dict:
        """Get cross-department heatmap data for executive view."""
        with get_cursor() as cur:
            cur.execute("""
                SELECT owner_node, level, COUNT(*) as objective_count,
                       AVG(CASE WHEN status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM okr_objectives
                GROUP BY owner_node, level
                ORDER BY level, owner_node
            """)
            dept_stats = [dict(row) for row in cur.fetchall()]
        
        # Calculate progress per department
        dept_progress = {}
        for stat in dept_stats:
            dept = stat['owner_node'].split('.')[0] if '.' in stat['owner_node'] else stat['owner_node']
            if dept not in dept_progress:
                dept_progress[dept] = {'objectives': 0, 'completion_sum': 0.0, 'levels': set()}
            dept_progress[dept]['objectives'] += stat['objective_count']
            dept_progress[dept]['completion_sum'] += float(stat['completion_rate']) * stat['objective_count']
            dept_progress[dept]['levels'].add(stat['level'])
        
        heatmap = []
        for dept, data in dept_progress.items():
            avg_completion = data['completion_sum'] / data['objectives'] if data['objectives'] > 0 else 0
            heatmap.append({
                "department": dept,
                "objectives": data['objectives'],
                "avg_completion_pct": round(avg_completion * 100, 1),
                "levels": list(data['levels'])
            })
        
        return {"heatmap": sorted(heatmap, key=lambda x: -x['avg_completion_pct'])}


# BCG Maturity Checklist (standardized)
BCG_OKR_CHECKLIST = [
    # 1. Specificity & Crispness
    {"category": "Specificity & Crispness", "criterion": "Objective is clear, concise, compelling (≤ few lines)"},
    {"category": "Specificity & Crispness", "criterion": "Each KR is a single measurable outcome, not a task list"},
    {"category": "Specificity & Crispness", "criterion": "KRs use concrete numbers with units (%, $, count)"},
    
    # 2. Ambition & Stretch
    {"category": "Ambition & Stretch", "criterion": "Objective represents a meaningful step-change, not business-as-usual"},
    {"category": "Ambition & Stretch", "criterion": "At least one KR is a 'moonshot' (~70% confidence achievable)"},
    {"category": "Ambition & Stretch", "criterion": "KRs are leading indicators, not just lagging KPIs"},
    
    # 3. Customer/Outcome Focus
    {"category": "Customer/Outcome Focus", "criterion": "Objective framed as customer/end-user outcome, not internal output"},
    {"category": "Customer/Outcome Focus", "criterion": "KRs measure value delivered, not activity completed"},
    
    # 4. Alignment & Cascade
    {"category": "Alignment & Cascade", "criterion": "Objective explicitly links to parent objective (if not corporate)"},
    {"category": "Alignment & Cascade", "criterion": "Department OKRs cascade from corporate priorities"},
    {"category": "Alignment & Cascade", "criterion": "No orphan OKRs - every objective has a clear owner node"},
    
    # 5. Measurability & Tracking
    {"category": "Measurability & Tracking", "criterion": "Every KR has a defined data source and measurement frequency"},
    {"category": "Measurability & Tracking", "criterion": "Progress is tracked weekly with automated/data-driven updates"},
    {"category": "Measurability & Tracking", "criterion": "Confidence scores are calibrated and reviewed weekly"},
    
    # 6. Accountability & Governance
    {"category": "Accountability & Governance", "criterion": "Owner node has decision rights (OWN) for this objective"},
    {"category": "Accountability & Governance", "criterion": "Escalation path defined for off-track KRs (NEURAXIS integration)"},
    {"category": "Accountability & Governance", "criterion": "Regular check-ins scheduled with consulting/informing nodes"},
    
    # 7. Learning & Adaptation
    {"category": "Learning & Adaptation", "criterion": "Failed/off-track KRs trigger Kaizen loop analysis"},
    {"category": "Learning & Adaptation", "criterion": "Insights from OKR cycle feed back into next quarter's objectives"},
]


def create_sample_corporate_okr() -> Objective:
    """Create a sample corporate OKR for Q4 2026."""
    return Objective(
        objective_id="OKR-CORP-Q4-2026-001",
        title="Customers experience our new data offerings as innovative and strongly value-enhancing",
        description="Shift from feature delivery to customer value realization across all data products",
        level=OKRLevel.CORPORATE,
        owner_node="Finance",
        key_results=[
            KeyResult(
                kr_id="KR-CORP-Q4-2026-001",
                objective_id="OKR-CORP-Q4-2026-001",
                description="65% of clients perceive innovation capabilities as better than competitors",
                kr_type="metric",
                target=65.0,
                current=0.0,
                unit="%",
                weight=1.0,
                source="quarterly_client_survey",
                frequency="quarterly",
                confidence=0.6,
                is_leading=True
            ),
            KeyResult(
                kr_id="KR-CORP-Q4-2026-002",
                objective_id="OKR-CORP-Q4-2026-001",
                description="Average customer service rating ≥ 4.0/5.0 across all touchpoints",
                kr_type="metric",
                target=4.0,
                current=0.0,
                unit="score",
                weight=1.0,
                source="post_interaction_survey",
                frequency="weekly",
                confidence=0.7,
                is_leading=False
            ),
            KeyResult(
                kr_id="KR-CORP-Q4-2026-003",
                objective_id="OKR-CORP-Q4-2026-001",
                description="Pilot implementations achieve 40% cost reduction vs previous implementations",
                kr_type="metric",
                target=40.0,
                current=0.0,
                unit="%",
                weight=0.8,
                source="financial_tracking",
                frequency="monthly",
                confidence=0.5,
                is_leading=True
            )
        ],
        status=OKRStatus.ACTIVE,
        start_date="2026-10-01",
        end_date="2026-12-31",
        tags=["corporate", "customer-value", "data-platform"]
    )


if __name__ == "__main__":
    # Test OKR Engine
    engine = OKREngine()
    
    # Create corporate OKR
    corp_okr = create_sample_corporate_okr()
    engine.create_objective(corp_okr)
    print(f"Created: {corp_okr.objective_id} - {corp_okr.title}")
    
    # Create department cascade
    dept_okr = Objective(
        objective_id="OKR-MKT-Q4-2026-001",
        title="Shift 30% paid budget to referral program activation to drive customer value",
        description="Marketing contribution to corporate customer-value objective via referral channel",
        level=OKRLevel.DEPARTMENT,
        owner_node="Marketing.Growth",
        parent_objective_id=corp_okr.objective_id,
        key_results=[
            KeyResult(
                kr_id="KR-MKT-Q4-2026-001",
                objective_id="OKR-MKT-Q4-2026-001",
                description="Referral pipeline QoQ growth ≥ 15%",
                kr_type="metric",
                target=15.0,
                current=0.0,
                unit="%",
                weight=1.0,
                source="crm_pipeline",
                frequency="weekly",
                confidence=0.7,
                is_leading=True
            ),
            KeyResult(
                kr_id="KR-MKT-Q4-2026-002",
                objective_id="OKR-MKT-Q4-2026-001",
                description="Paid CAC reduction ≥ 20%",
                kr_type="metric",
                target=-20.0,
                current=0.0,
                unit="%",
                weight=1.0,
                source="marketing_attribution",
                frequency="weekly",
                confidence=0.6,
                is_leading=True
            ),
            KeyResult(
                kr_id="KR-MKT-Q4-2026-003",
                objective_id="OKR-MKT-Q4-2026-001",
                description="Referral-to-opportunity conversion ≥ 20%",
                kr_type="metric",
                target=20.0,
                current=0.0,
                unit="%",
                weight=0.5,
                source="crm_conversion",
                frequency="weekly",
                confidence=0.8,
                is_leading=True
            )
        ],
        status=OKRStatus.ACTIVE,
        start_date="2026-10-01",
        end_date="2026-12-31",
        tags=["marketing", "referral", "budget-shift"]
    )
    engine.create_objective(dept_okr)
    print(f"Created: {dept_okr.objective_id} - {dept_okr.title}")
    
    # Test cascade
    cascade = engine.get_cascade(corp_okr.objective_id)
    print(f"\nCascade from {corp_okr.objective_id}:")
    for obj in cascade:
        print(f"  {obj.level.value}: {obj.title} (owner: {obj.owner_node})")
        for kr in obj.key_results:
            print(f"    KR: {kr.description} (target: {kr.target}{kr.unit})")
    
    # Test progress update
    result = engine.update_kr_progress(dept_okr.objective_id, "KR-MKT-Q4-2026-001", 8.0, 
                                        recorded_by="Marketing.Growth", source="crm_pipeline")
    print(f"\nProgress update: {result}")
    
    # Test maturity assessment
    assessments = [
        {"category": "Specificity & Crispness", "criterion": "Objective is clear, concise, compelling", "score": 0.9},
        {"category": "Ambition & Stretch", "criterion": "At least one KR is a moonshot", "score": 0.7},
        {"category": "Customer/Outcome Focus", "criterion": "Objective framed as customer outcome", "score": 0.85},
        {"category": "Alignment & Cascade", "criterion": "Objective links to parent", "score": 1.0},
        {"category": "Measurability & Tracking", "criterion": "Every KR has data source", "score": 0.95},
        {"category": "Accountability & Governance", "criterion": "Owner has decision rights", "score": 1.0},
    ]
    maturity = engine.assess_maturity(dept_okr.objective_id, assessments, "Marketing.Head")
    print(f"\nMaturity assessment: {maturity['maturity_level']} ({maturity['overall_score']:.1%})")
    
    # Dashboard
    dashboard = engine.get_dashboard(owner_node="Marketing.Growth")
    print(f"\nDashboard: {dashboard['summary']}")