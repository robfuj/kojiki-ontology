#!/usr/bin/env python3
"""
Chief of Staff Coordinator — Fanout-based Goal Decomposition & Dispatch.

Follows oh-my-hermes FANOUT pattern:
1. SACCADE: Frame the raw goal into a structured Problem (a priori)
2. PROPOSE: Decompose into department-level units with boundaries, owners, dependencies
3. FREEZE: Validate and freeze the fanout contract (deterministic checks)
4. DISPATCH: Route each unit to its department specialist for full SYNAPSIS execution
5. SYNTHESIZE: Merge results via Mycelium conversation layer

Departments run their own SYNAPSIS pipeline (SACCADE→EVIDENCE→INTERPRETATION→STRATEGY)
and use agency-agents skills for specialized work within their domain.
"""

import json
import asyncio
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict, field

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from kojiki.core import (
    Specialist, ScopedContext, load_specialist, call_model, StageName
)
from kojiki.core.runner import PipelineRunner, run_pipeline
from kojiki.core.stages import run_saccade_stage, run_evidence_stage, run_interpretation_stage, run_strategy_stage

# Import OKR engine for goal tracking
MYCELIUM_ENGINE = Path(__file__).parent.parent.parent / "mycelium" / "engine"
if MYCELIUM_ENGINE.exists():
    sys.path.insert(0, str(MYCELIUM_ENGINE))
    from okr_engine import OKREngine, Objective, KeyResult, OKRLevel, OKRStatus
    from registry import NodeRegistry
    from propagate import SignalPropagator
    from sentinel import SentinelEngine
    from conversation import MyceliumConversationLayer, ConversationType, SignalPriority, ChiefOfStaffMyceliumIntegration, MyceliumSignal


@dataclass
class FanoutUnit:
    """A unit of work dispatched to a department (mirrors fanout unit structure)."""
    unit_id: str
    title: str
    description: str
    owner_node: str              # MYCELIUM department head node (e.g., "Marketing")
    specialist_name: str         # Specialist to execute (e.g., "marketing-brand")
    file_scope: List[str]        # Boundaries - what this unit owns (department scope)
    depends_on: List[str] = field(default_factory=list)  # Other unit_ids this depends on
    success_criteria: List[Dict] = field(default_factory=list)  # Measurable KRs
    priority: int = 1
    status: str = "pending"      # pending, running, completed, failed
    result: Optional[Dict] = None


@dataclass
class FanoutContract:
    """Frozen coordination contract (mirrors fanout_contract/v2)."""
    contract_id: str
    original_goal: str
    problem_id: str
    units: List[FanoutUnit]
    spawn_plan: Optional[Dict[str, Any]] = None  # Required if >4 units
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: str = "frozen"  # proposed, frozen, dispatched, completed, failed
    sha256: str = ""  # Deterministic hash for idempotency


@dataclass
class CoordinationPlan:
    """Execution plan derived from frozen contract."""
    plan_id: str
    contract: FanoutContract
    execution_order: List[List[str]]  # Batches of unit_ids that can run in parallel
    created_at: str
    status: str = "planned"


class ChiefOfStaff:
    """
    Chief of Staff Coordinator — Fanout-based architecture.

    The single coordinator that:
    1. SACCADE: Frames the raw goal into a Problem (a priori)
    2. PROPOSE: Decomposes into department-level FanoutUnits
    3. FREEZE: Validates boundaries, dependencies, spawn plan → frozen contract
    4. DISPATCH: Routes each unit to its department specialist for SYNAPSIS execution
    5. SYNTHESIZE: Merges results via Mycelium conversation layer

    Department specialists run full SYNAPSIS (SACCADE→EVIDENCE→INTERPRETATION→STRATEGY)
    and use agency-agents skills for specialized work.
    """

    def __init__(self):
        self.okr_engine = OKREngine() if 'OKREngine' in globals() else None
        self.execution_history: List[Dict] = []
        self.contracts: Dict[str, FanoutContract] = {}

        # Initialize Mycelium components for cross-department coordination
        if self.okr_engine:
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mycelium" / "engine"))
                from postgres_registry import PostgresNodeRegistry
                self.registry = PostgresNodeRegistry()
                self.propagator = SignalPropagator(
                    edge_store_path="mycelium/engine/edges.json",
                    log_path="mycelium/log/signals.jsonl",
                    registry=self.registry
                )
                self.sentinel = SentinelEngine("mycelium")

                # Initialize Mycelium Conversation Layer for cross-department sync
                self.conversation_layer = MyceliumConversationLayer(
                    conversation_store="mycelium/conversations/conversations.json",
                    signal_log="mycelium/conversations/signals.jsonl",
                    saccade_cache_path="mycelium/conversations/saccade_cache.json",
                    signal_propagator=self.propagator,
                    neuraxis_escalator=self.sentinel,
                    okr_engine=self.okr_engine
                )
                self.chief_myelium = ChiefOfStaffMyceliumIntegration(self.conversation_layer)

                # Bootstrap root departments if needed
                for dept in ["Finance", "Marketing", "Sales", "Engineering", "Operations",
                    "Legal", "People & Comms", "Technology Platform"]:
                    if not self.registry.get_node(dept):
                        _, pub_key = self.registry.key_manager.generate_keypair(dept)
                        self.registry.register_node(
                            node_data={
                                "id": dept, "domain": dept.lower().replace(".", "/").replace(" ", "/"), "type": "agent",
                                "status": "active", "parent": None
                            },
                            signer=dept,
                            signature="root_dept_bootstrap"
                        )
            except Exception as e:
                print(f"Warning: Could not initialize Mycelium for dept heads: {e}")
                import traceback
                traceback.print_exc()
                self.registry = None
                self.propagator = None
                self.sentinel = None
                self.conversation_layer = None
                self.chief_myelium = None

    # ============================================================
    # STAGE 1: SACCADE — A Priori Problem Framing
    # ============================================================
    def frame_problem(self, raw_record: str, context: Dict = None) -> Dict:
        """Stage 1: SACCADE — sharpen raw record into structured Problem."""
        print(f"\n=== CHIEF OF STAFF: SACCADE FRAMING ===")
        print(f"Raw record: {raw_record[:200]}...")

        # Check SACCADE cache first
        if self.chief_myelium:
            department = context.get('department', 'Marketing') if context else 'Marketing'
            constraints = context.get('constraints', []) if context else []
            assumptions = context.get('assumptions', []) if context else []
            unknowns = context.get('unknowns', []) if context else []

            cached = self.chief_myelium.check_saccade_cache(
                goal=raw_record, constraints=constraints, assumptions=assumptions,
                unknowns=unknowns, department=department
            )
            if cached:
                print(f"  🎯 Found cached SACCADE: {cached.problem_id} (used {cached.usage_count} times)")
                return {
                    "problem_id": cached.problem_id, "goal": cached.goal,
                    "constraints": cached.constraints, "assumptions": cached.assumptions,
                    "unknowns": cached.unknowns
                }

        # Run SACCADE using Chief of Staff's own prompt
        dispatch = {
            "task_id": f"cos-saccade-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "raw_record": raw_record,
            **(context or {})
        }

        specialist = load_specialist("chief-of-staff")
        specialist.stages["saccade"].prompt = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / "chief-of-staff" / "prompts" / "01-saccade-cos.md")
        runner = PipelineRunner(specialist, dispatch)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_saccade_stage(runner, dispatch, runner.context, "marketing"))
            problem = runner.context.stage_outputs.get("saccade", {})
        finally:
            loop.close()

        print(f"Problem framed: {problem.get('problem_id')} - {problem.get('goal')}")
        return problem

    # ============================================================
    # STAGE 2: PROPOSE — Decompose into Fanout Units
    # ============================================================
    def propose_units(self, problem: Dict, raw_record: str) -> List[FanoutUnit]:
        """
        Propose department-level units with boundaries, owners, dependencies.
        Uses Chief of Staff's own strategy prompt for decomposition.
        """
        print(f"\n=== CHIEF OF STAFF: PROPOSING FANOUT UNITS ===")

        problem_id = problem.get("problem_id", "UNKNOWN")
        goal = problem.get("goal", "")
        constraints = problem.get("constraints", [])
        assumptions = problem.get("assumptions", [])
        unknowns = problem.get("unknowns", [])

        # Dynamically discover available departments
        specialists_dir = Path(__file__).parent.parent.parent / "kojiki" / "specialists"
        dept_head_mapping = self._get_dept_head_mapping()

        dept_lines = []
        available_departments = {}
        for dept_name, spec_name in dept_head_mapping.items():
            spec_path = specialists_dir / spec_name
            if spec_path.exists():
                try:
                    spec = load_specialist(spec_name)
                    desc = self._get_dept_description(dept_name)
                    dept_lines.append(f"- {dept_name} ({spec_name}): {desc}")
                    available_departments[dept_name] = spec_name
                except:
                    dept_lines.append(f"- {dept_name} ({spec_name})")
                    available_departments[dept_name] = spec_name

        dept_list = "\n".join(dept_lines)

        # Build decomposition prompt
        decomp_prompt = f"""You are the Chief of Staff. Decompose this problem into DEPARTMENT-LEVEL units for fanout dispatch.

PROBLEM: {goal}
CONSTRAINTS: {constraints}
ASSUMPTIONS: {assumptions}
UNKNOWNS: {unknowns}

DEPARTMENT HEADS (delegate to these — they own SYNAPSIS execution within their domain):
{dept_list}

FOR EACH RELEVANT DEPARTMENT, specify a FanoutUnit:
1. unit_id: unique (e.g., "UNIT-001")
2. title: Clear, measurable department outcome
3. description: What this department must achieve (specific to THIS problem)
4. owner_node: EXACT department head name from list above
5. specialist_name: Specialist for department head (auto-mapped, leave blank)
6. file_scope: List of domain boundaries this unit owns (e.g., ["brand", "growth", "content"])
7. depends_on: Other unit_ids this depends on
8. success_criteria: [{{name, metric, target, operator, weight}}] - Department-level KRs
9. priority: 1 (high), 2 (medium), 3 (low)

Return JSON array of FanoutUnits (3-6 max). Each department head runs full SYNAPSIS.

IMPORTANT: owner_node MUST match exactly one department head name. Use exact names: Marketing, Legal, Finance, Engineering, Operations, Sales, People & Comms, Technology Platform."""

        dispatch = {
            "task_id": f"cos-propose-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "raw_record": decomp_prompt,
            "dept_head": "ChiefOfStaff"
        }

        specialist = load_specialist("chief-of-staff")
        specialist.stages["strategy"].prompt = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / "chief-of-staff" / "prompts" / "04-strategy-cos.md")
        specialist.stages["strategy"].schema = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / "chief-of-staff" / "schemas" / "strategy-cos.json")
        runner = PipelineRunner(specialist, dispatch)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_saccade_stage(runner, dispatch, runner.context, "marketing"))
            loop.run_until_complete(run_evidence_stage(runner, dispatch, runner.context, "marketing"))
            loop.run_until_complete(run_interpretation_stage(runner, dispatch, runner.context, "marketing"))
            loop.run_until_complete(run_strategy_stage(runner, dispatch, runner.context, "marketing"))
            strategy_output = runner.context.stage_outputs.get("strategy", {})
        finally:
            loop.close()

        # Parse FanoutUnits from strategy output
        units_data = strategy_output.get("actions", [])
        units = []
        for i, action in enumerate(units_data):
            owner = action.get("owner", "Marketing")
            owner = self._validate_owner_node(owner)

            unit = FanoutUnit(
                unit_id=action.get("unit_id", f"UNIT-{problem_id}-{i+1:03d}"),
                title=action.get("description", f"Department objective {i+1}"),
                description=action.get("description", ""),
                owner_node=owner,
                specialist_name=self._owner_to_specialist(owner),
                file_scope=action.get("file_scope", [owner.lower()]),
                depends_on=action.get("depends_on", []),
                success_criteria=action.get("success_criteria", []),
                priority=action.get("priority", 1)
            )
            units.append(unit)

        # Run each department's own SACCADE to refine their unit
        print(f"\n=== DEPARTMENT HEAD SACCADE REFINEMENT ===")
        for unit in units:
            dept_name = unit.owner_node
            if dept_name in available_departments:
                print(f"  📋 {dept_name} running their SACCADE...")
                spec_name = available_departments[dept_name]
                dept_specialist = load_specialist(spec_name)
                dept_dispatch = {
                    "task_id": f"dh-saccade-{unit.unit_id}",
                    "raw_record": unit.description,
                    "dept_objective": {"objective_id": unit.unit_id, "title": unit.title},
                    "department": dept_name
                }
                # Use department's own SACCADE prompt
                dept_specialist.stages["saccade"].prompt = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / spec_name / "prompts" / "01-saccade-dh.md")
                dept_runner = PipelineRunner(dept_specialist, dept_dispatch)

                dept_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(dept_loop)
                try:
                    dept_loop.run_until_complete(run_saccade_stage(dept_runner, dept_dispatch, dept_runner.context, dept_name))
                    dept_saccade = dept_runner.context.stage_outputs.get("saccade", {})
                    unit.description = f"DEPT SACCADE: {dept_saccade.get('goal', unit.description)}"
                    print(f"    ✅ {dept_name}: {dept_saccade.get('problem_id', 'N/A')} - {dept_saccade.get('goal', 'N/A')[:80]}")
                finally:
                    dept_loop.close()
            else:
                print(f"  ⚠️  {dept_name} specialist not found")

        return units

    # ============================================================
    # STAGE 3: FREEZE — Validate & Freeze Contract
    # ============================================================
    def freeze_contract(self, problem: Dict, raw_record: str, units: List[FanoutUnit]) -> FanoutContract:
        """
        Validate and freeze the fanout contract.
        Deterministic checks: boundary overlaps, dependency cycles, spawn plan.
        """
        print(f"\n=== CHIEF OF STAFF: FREEZING CONTRACT ===")

        problem_id = problem.get("problem_id", "UNKNOWN")
        goal = problem.get("goal", "")

        # Build contract
        contract = FanoutContract(
            contract_id=f"CONTRACT-{problem_id}",
            original_goal=goal,
            problem_id=problem_id,
            units=units,
            created_at=datetime.utcnow().isoformat() + "Z"
        )

        # Deterministic validation
        errors = self._validate_contract(contract)
        if errors:
            raise ValueError(f"Contract validation failed: {errors}")

        # Spawn plan required if >4 units
        if len(units) > 4:
            spawn_plan = self._generate_spawn_plan(units)
            contract.spawn_plan = spawn_plan
            print(f"  📋 Spawn plan required ({len(units)} units > 4): {spawn_plan['why_parallel']}")

        # Compute deterministic SHA256 for idempotency
        contract_bytes = json.dumps(asdict(contract), sort_keys=True, separators=(',', ':')).encode()
        contract.sha256 = hashlib.sha256(contract_bytes).hexdigest()[:16]

        # Store contract
        self.contracts[contract.contract_id] = contract

        print(f"  ✅ Contract frozen: {contract.contract_id} (sha256: {contract.sha256})")
        print(f"  Units: {len(units)} | Spawn plan: {'yes' if contract.spawn_plan else 'no'}")
        return contract

    def _validate_contract(self, contract: FanoutContract) -> List[str]:
        """Validate contract deterministically."""
        errors = []
        unit_ids = {u.unit_id for u in contract.units}

        # 1. Check boundary overlaps (file_scope) without depends_on edge
        for u in contract.units:
            for v in contract.units:
                if u.unit_id >= v.unit_id:
                    continue
                overlap = set(u.file_scope) & set(v.file_scope)
                if overlap and v.unit_id not in u.depends_on and u.unit_id not in v.depends_on:
                    errors.append(f"Boundary overlap without depends_on edge: {u.unit_id} <-> {v.unit_id} (overlap: {overlap})")

        # 2. Check dependency cycles
        if self._has_dependency_cycle(contract.units):
            errors.append("Dependency cycle detected in units")

        # 3. Check all depends_on reference valid unit_ids
        for u in contract.units:
            for dep in u.depends_on:
                if dep not in unit_ids:
                    errors.append(f"Unit {u.unit_id} depends on unknown unit: {dep}")

        # 4. Check owner_node validity
        valid_owners = set(self._get_dept_head_mapping().keys())
        for u in contract.units:
            if u.owner_node not in valid_owners:
                errors.append(f"Unit {u.unit_id} has invalid owner_node: {u.owner_node}")

        return errors

    def _has_dependency_cycle(self, units: List[FanoutUnit]) -> bool:
        """Detect cycles in dependency graph using DFS."""
        unit_map = {u.unit_id: u for u in units}
        visited = set()
        rec_stack = set()

        def dfs(unit_id):
            visited.add(unit_id)
            rec_stack.add(unit_id)
            unit = unit_map.get(unit_id)
            if unit:
                for dep in unit.depends_on:
                    if dep not in visited:
                        if dfs(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            rec_stack.remove(unit_id)
            return False

        for unit in units:
            if unit.unit_id not in visited:
                if dfs(unit.unit_id):
                    return True
        return False

    def _generate_spawn_plan(self, units: List[FanoutUnit]) -> Dict[str, str]:
        """Generate spawn plan justification (required for >4 units)."""
        return {
            "why_parallel": f"{len(units)} departments each own disjoint domain scope with independent SYNAPSIS execution",
            "why_not_single_unit": "Single executor would serialize unrelated department work, losing parallelism",
            "independence": "No unit reads/writes another unit's file_scope; cross-dept coordination via Mycelium conversation layer",
            "expected_evidence_shape": "Per-unit causal chain + department OKRs + Mycelium signals"
        }

    # ============================================================
    # STAGE 4: DISPATCH — Route to Department Specialists
    # ============================================================
    async def execute_contract(self, contract: FanoutContract) -> Dict[str, Any]:
        """Execute frozen contract: dispatch each unit to its department specialist."""
        print(f"\n=== CHIEF OF STAFF: DISPATCHING CONTRACT {contract.contract_id} ===")

        contract.status = "dispatched"
        plan = CoordinationPlan(
            plan_id=f"PLAN-{contract.contract_id}",
            contract=contract,
            execution_order=self._build_execution_order(contract.units),
            created_at=datetime.utcnow().isoformat() + "Z"
        )

        results = {}
        plan.status = "executing"

        for batch_idx, batch in enumerate(plan.execution_order):
            print(f"\n--- Execution Batch {batch_idx + 1}/{len(plan.execution_order)} ---")

            batch_tasks = []
            for unit_id in batch:
                unit = next(u for u in contract.units if u.unit_id == unit_id)
                unit.status = "running"
                print(f"  ▶️ Dispatching {unit_id} ({unit.specialist_name}) to {unit.owner_node}")
                batch_tasks.append((unit_id, self._execute_unit(unit, contract)))

            batch_results = await asyncio.gather(*[t[1] for t in batch_tasks], return_exceptions=True)

            for (unit_id, _), result in zip(batch_tasks, batch_results):
                unit = next(u for u in contract.units if u.unit_id == unit_id)
                if isinstance(result, Exception):
                    unit.status = "failed"
                    unit.result = {"error": str(result)}
                    print(f"  ❌ {unit_id} failed: {result}")
                else:
                    unit.status = "completed"
                    unit.result = result
                    results[unit_id] = result
                    print(f"  ✅ {unit_id} completed")

        plan.status = "completed"
        contract.status = "completed"

        # Cross-department coordination via Mycelium
        if self.chief_myelium and len(contract.units) > 1:
            departments = list(set(u.owner_node for u in contract.units))
            self.chief_myelium.coordinate_cross_department(
                goal=contract.original_goal,
                departments=departments,
                context={
                    "contract_id": contract.contract_id,
                    "problem_id": contract.problem_id,
                    "units": [{"unit_id": u.unit_id, "owner": u.owner_node, "title": u.title} for u in contract.units]
                }
            )

        # Synthesis
        synthesis = self._synthesize_results(plan, results)

        return {
            "contract_id": contract.contract_id,
            "plan_id": plan.plan_id,
            "status": plan.status,
            "unit_results": results,
            "synthesis": synthesis,
            "completed_at": datetime.utcnow().isoformat() + "Z"
        }

    async def _execute_unit(self, unit: FanoutUnit, contract: FanoutContract) -> Dict:
            """Execute a single unit through its department's full SYNAPSIS pipeline."""
            dispatch = {
                "task_id": unit.unit_id,
                "raw_record": unit.description,
                "parent_contract_id": contract.contract_id,
                "unit_id": unit.unit_id,
                "success_criteria": unit.success_criteria,
                "dept_head": True,
                "owner_node": unit.owner_node
            }

            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, run_pipeline, unit.specialist_name, dispatch
                )
                return result
            except Exception as e:
                return {"error": str(e), "unit_id": unit.unit_id}

    def _build_execution_order(self, units: List[FanoutUnit]) -> List[List[str]]:
        """Topological sort for execution order based on dependencies."""
        no_deps = [u.unit_id for u in units if not u.depends_on]
        has_deps = [u.unit_id for u in units if u.depends_on]

        order = []
        if no_deps:
            order.append(no_deps)
        if has_deps:
            order.append(has_deps)
        return order

    # ============================================================
    # STAGE 5: SYNTHESIZE — Merge Results
    # ============================================================
    def _synthesize_results(self, plan: CoordinationPlan, results: Dict) -> Dict:
        """Synthesize unit results into coherent outcome."""
        print(f"\n=== CHIEF OF STAFF: SYNTHESIS ===")

        all_insights = []
        all_actions = []
        all_risks = []

        for unit_id, result in results.items():
            if isinstance(result, dict) and "interpretation" in result:
                interp = result.get("interpretation", {})
                all_insights.extend(interp.get("key_insights", []))

            if isinstance(result, dict) and "strategy" in result:
                strategy = result.get("strategy", {})
                all_actions.extend([
                    {
                        "action_id": a.get("action_id"),
                        "description": a.get("description"),
                        "owner": a.get("owner"),
                        "due_date": a.get("due_date"),
                        "unit": unit_id
                    }
                    for a in strategy.get("actions", [])
                ])
                all_risks.extend(strategy.get("risks", []))

        # Create OKRs if engine available
        if self.okr_engine:
            self._create_okrs_from_contract(plan.contract)

        synthesis = {
            "plan_id": plan.plan_id,
            "contract_id": plan.contract.contract_id,
            "original_goal": plan.contract.original_goal,
            "total_units": len(plan.contract.units),
            "completed": len([u for u in plan.contract.units if u.status == "completed"]),
            "failed": len([u for u in plan.contract.units if u.status == "failed"]),
            "key_insights": list(set(all_insights)),
            "consolidated_actions": all_actions,
            "consolidated_risks": all_risks,
            "overall_status": "completed" if all(u.status == "completed" for u in plan.contract.units) else "partial"
        }

        print(f"Synthesis: {synthesis['completed']}/{synthesis['total_units']} units completed")
        print(f"Key insights: {len(synthesis['key_insights'])}")
        print(f"Consolidated actions: {len(synthesis['consolidated_actions'])}")

        return synthesis

    def _create_okrs_from_contract(self, contract: FanoutContract):
        """Create OKR objectives from the frozen contract."""
        if not self.okr_engine:
            return

        # Corporate objective
        corp_objective = Objective(
            objective_id=f"OKR-{contract.problem_id}",
            title=contract.original_goal,
            description=f"Fanout contract: {contract.contract_id}",
            level=OKRLevel.CORPORATE,
            owner_node="Finance",
            key_results=[
                KeyResult(
                    kr_id=f"KR-{contract.problem_id}-{i+1:03d}",
                    objective_id=f"OKR-{contract.problem_id}",
                    description=f"Unit: {u.title}",
                    kr_type="metric", target=100.0, current=0.0, unit="%",
                    weight=1.0, source="chief_of_staff_tracking", frequency="weekly",
                    confidence=0.7, is_leading=True
                )
                for i, u in enumerate(contract.units)
            ],
            status=OKRStatus.ACTIVE,
            start_date=datetime.utcnow().strftime("%Y-%m-%d"),
            end_date=(datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
            tags=["fanout", contract.contract_id]
        )
        self.okr_engine.create_objective(corp_objective)

        # Department objectives
        owner_nodes = set(u.owner_node for u in contract.units)
        for owner_node in owner_nodes:
            owner_units = [u for u in contract.units if u.owner_node == owner_node]
            if not owner_units:
                continue

            dept_head_mapping = self._get_dept_head_mapping()
            if owner_node not in dept_head_mapping:
                continue

            dept_objective = Objective(
                objective_id=f"OKR-{owner_node.replace('.', '-')}-{contract.problem_id}",
                title=f"{owner_node} contribution to {contract.original_goal}",
                description=f"Department objective for {owner_node}",
                level=OKRLevel.DEPARTMENT,
                owner_node=owner_node,
                parent_objective_id=f"OKR-{contract.problem_id}",
                key_results=[
                    KeyResult(
                        kr_id=f"KR-{owner_node.replace('.', '-')}-{contract.problem_id}-{i+1:03d}",
                        objective_id=f"OKR-{owner_node.replace('.', '-')}-{contract.problem_id}",
                        description=u.title,
                        kr_type="metric", target=100.0, current=0.0, unit="%",
                        weight=1.0, source="chief_of_staff_tracking", frequency="weekly",
                        confidence=0.8, is_leading=True
                    )
                    for i, u in enumerate(owner_units)
                ],
                status=OKRStatus.ACTIVE,
                start_date=datetime.utcnow().strftime("%Y-%m-%d"),
                end_date=(datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
                tags=["fanout", contract.contract_id, owner_node]
            )
            self.okr_engine.create_objective(dept_objective)

        print(f"  ✅ Created OKRs: 1 corporate + {len(owner_nodes)} department objectives")

    # ============================================================
    # MAIN ENTRY POINT
    # ============================================================
    def coordinate(self, raw_record: str, context: Dict = None) -> Dict[str, Any]:
        """
        Main entry: Coordinate a high-level goal end-to-end via fanout.

        1. SACCADE framing (with cache check)
        2. PROPOSE department-level units
        3. FREEZE contract (deterministic validation)
        4. DISPATCH units to department specialists (parallel, SYNAPSIS each)
        5. SYNTHESIZE via Mycelium
        6. Cache SACCADE for reuse
        """
        print(f"\n{'='*60}")
        print(f"CHIEF OF STAFF COORDINATION STARTED (Fanout)")
        print(f"{'='*60}")

        # Stage 1: SACCADE
        problem = self.frame_problem(raw_record, context)

        # Cache SACCADE
        if self.chief_myelium and problem.get('problem_id'):
            department = context.get('department', 'Marketing') if context else 'Marketing'
            self.chief_myelium.store_saccade(
                problem_id=problem['problem_id'],
                goal=problem['goal'],
                constraints=problem.get('constraints', []),
                assumptions=problem.get('assumptions', []),
                unknowns=problem.get('unknowns', []),
                department=department
            )

        # Stage 2: Propose units
        units = self.propose_units(problem, raw_record)

        # Stage 3: Freeze contract
        contract = self.freeze_contract(problem, raw_record, units)

        # Stage 4: Execute (dispatch)
        execution_result = asyncio.run(self.execute_contract(contract))

        # Final result
        final_result = {
            "coordination_id": f"COS-{problem.get('problem_id', 'UNKNOWN')}",
            "problem": problem,
            "contract": asdict(contract),
            "execution": execution_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.execution_history.append(final_result)

        print(f"\n{'='*60}")
        print(f"CHIEF OF STAFF COORDINATION COMPLETED")
        print(f"{'='*60}")

        return final_result

    # ============================================================
    # HELPER METHODS
    # ============================================================
    def _validate_owner_node(self, owner_node: str) -> str:
        corrections = {
            "Marketing.Growth": "Marketing", "Marketing.Head": "Marketing", "Marketing.Brand": "Marketing",
            "Engineering.Referral": "Engineering", "Engineering": "Engineering", "Engineering.Head": "Engineering",
            "Engineering.Platform": "Engineering", "Engineering.Technology": "Engineering",
            "Sales.Outbound": "Sales", "Sales.Head": "Sales",
            "Finance.Budget": "Finance", "Finance.CFO": "Finance",
            "Product.Head": "Engineering", "Customer.Success": "Engineering", "Customer.Success.Head": "Engineering",
            "Operations.Head": "Operations",
            "Data.Analytics": "Technology Platform", "Data.Analytics.Head": "Technology Platform",
            "Business.Development": "Sales", "Business.Development.Head": "Sales",
            "Corporate.Development": "Sales",
            "Supply.Chain.Procurement": "Operations", "Supply.Chain.Procurement.Head": "Operations",
            "AI.Intelligence": "Technology Platform", "AI.Intelligence.Head": "Technology Platform",
            "Security": "Technology Platform", "Security.Head": "Technology Platform",
            "IT": "Technology Platform", "IT.Head": "Technology Platform",
            "People.HR": "People & Comms", "People.HR.Head": "People & Comms",
            "Communications.Public.Affairs": "People & Comms", "Communications.Public.Affairs.Head": "People & Comms",
            "Compliance.Risk": "Legal", "Compliance.Risk.Head": "Legal", "Legal.Head": "Legal",
            "Executive.Strategy": "Finance", "Executive.Office.Chief.of.Staff": "Finance",
        }
        return corrections.get(owner_node, owner_node)

    def _get_dept_description(self, dept_name: str) -> str:
        descriptions = {
            "Finance": "Budget, CAC, ROI, financial planning, FP&A, treasury",
            "Marketing": "Brand, growth, GTM, demand generation, referral, paid media",
            "Sales": "Pipeline, quota, outbound, enablement, partnerships, M&A, strategic investments",
            "Engineering": "Platform, APIs, infrastructure, product strategy, roadmap, features, retention, expansion, NPS",
            "Operations": "Process, vendors, logistics, procurement, supply chain, fulfillment",
            "Legal": "Contracts, regulatory, compliance, audit, controls, risk, IP",
            "People & Comms": "Hiring, performance, culture, PR, internal comms, org design",
            "Technology Platform": "AI strategy, models, governance, systems, identity, tools, InfoSec, privacy, risk, measurement, attribution, dashboards",
        }
        return descriptions.get(dept_name, "")

    def _get_dept_head_mapping(self) -> Dict[str, str]:
        return {
            "Finance": "finance-accounting",
            "Marketing": "marketing-brand",
            "Sales": "sales-outbound",
            "Engineering": "engineering-platform",
            "Operations": "operations-ops",
            "Legal": "legal-compliance",
            "People & Comms": "people-hr",
            "Technology Platform": "ai-intelligence",
        }

    def _owner_to_specialist(self, owner_node: str) -> str:
        mapping = self._get_dept_head_mapping()
        return mapping.get(owner_node, "marketing-brand")


# Convenience function
def coordinate_goal(raw_record: str, context: Dict = None) -> Dict[str, Any]:
    """Convenience function for one-shot coordination."""
    cos = ChiefOfStaff()
    return cos.coordinate(raw_record, context)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m kojiki.core.chief_of_staff <raw_record> [context_json_file]")
        sys.exit(1)

    raw_record = sys.argv[1]
    context = {}
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            context = json.load(f)

    result = coordinate_goal(raw_record, context)
    print(json.dumps(result, indent=2))