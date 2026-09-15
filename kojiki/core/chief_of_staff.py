#!/usr/bin/env python3
"""
Chief of Staff Coordinator - Goal Decomposition & Specialist Orchestration.

The single entry point that:
1. Takes a raw goal/record
2. Runs SACCADE to frame the problem (a priori)
3. Decomposes into sub-goals with owner nodes
4. Routes to specialists in parallel
5. Synthesizes results
"""

import json
import asyncio
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
from kojiki.core.stages import run_saccade_stage

# Import OKR engine for goal tracking
MYCELIUM_ENGINE = Path(__file__).parent.parent.parent / "mycelium" / "engine"
if MYCELIUM_ENGINE.exists():
    sys.path.insert(0, str(MYCELIUM_ENGINE))
    from okr_engine import OKREngine, Objective, KeyResult, OKRLevel, OKRStatus
    from registry import NodeRegistry
    from propagate import SignalPropagator
    from sentinel import SentinelEngine
    from conversation import MyceliumConversationLayer, ConversationType, SignalPriority, ChiefOfStaffMyceliumIntegration


@dataclass
class SubGoal:
    """A decomposed sub-goal assigned to a specialist."""
    sub_goal_id: str
    title: str
    description: str
    owner_node: str          # MYCELIUM node (e.g., "Marketing.Growth")
    specialist_name: str     # Specialist to execute (e.g., "marketing-brand")
    parent_goal_id: str
    priority: int = 1        # 1=high, 2=medium, 3=low
    dependencies: List[str] = field(default_factory=list)  # sub_goal_ids that must complete first
    success_criteria: List[Dict] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None


@dataclass
class CoordinationPlan:
    """Complete coordination plan from goal decomposition."""
    plan_id: str
    original_goal: str
    problem_id: str
    sub_goals: List[SubGoal]
    execution_order: List[List[str]]  # Batches of sub_goal_ids that can run in parallel
    created_at: str
    status: str = "planned"  # planned, executing, completed, failed


class ChiefOfStaff:
    """
    Chief of Staff Coordinator.
    
    The single coordinator that:
    - Receives high-level goals
    - Uses SACCADE to frame problems correctly
    - Decomposes into specialist-assigned sub-goals
    - Orchestrates parallel execution
    - Synthesizes results
    """
    
    def __init__(self):
        self.okr_engine = OKREngine() if 'OKREngine' in globals() else None
        self.execution_history: List[Dict] = []
        
        # Initialize Mycelium components for dept head decomposition
        if self.okr_engine:
            try:
                # Use PostgresNodeRegistry to match OKR engine
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mycelium" / "engine"))
                from postgres_registry import PostgresNodeRegistry
                self.registry = PostgresNodeRegistry()
                self.propagator = SignalPropagator(
                    edge_store_path="mycelium/engine/edges.json",
                    log_path="mycelium/log/signals.jsonl",
                    registry=self.registry
                )
                self.sentinel = SentinelEngine("mycelium")
                
                # Initialize Mycelium Conversation Layer
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
    
    def frame_problem(self, raw_record: str, context: Dict = None) -> Dict:
            """Stage 1: SACCADE - A Priori Problem Framing.

            Uses the SACCADE stage to sharpen the raw record into a structured Problem.
            This is the 'what is the actual question' step.

            Also checks SACCADE cache for similar previously-framed problems.
            """
            print(f"\n=== CHIEF OF STAFF: SACCADE FRAMING ===")
            print(f"Raw record: {raw_record[:200]}...")

            # Check SACCADE cache first if conversation layer available
            if self.chief_myelium:
                department = context.get('department', 'Marketing') if context else 'Marketing'
                constraints = context.get('constraints', []) if context else []
                assumptions = context.get('assumptions', []) if context else []
                unknowns = context.get('unknowns', []) if context else []

                cached = self.chief_myelium.check_saccade_cache(
                    goal=raw_record,
                    constraints=constraints,
                    assumptions=assumptions,
                    unknowns=unknowns,
                    department=department
                )
                if cached:
                    print(f"  🎯 Found cached SACCADE: {cached.problem_id} (used {cached.usage_count} times)")
                    return {
                        "problem_id": cached.problem_id,
                        "goal": cached.goal,
                        "constraints": cached.constraints,
                        "assumptions": cached.assumptions,
                        "unknowns": cached.unknowns
                    }

            # Use Chief of Staff's own SACCADE prompt (not a department specialist)
            dispatch = {
                "task_id": f"cos-saccade-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "raw_record": raw_record,
                **(context or {})
            }

            # Run just the SACCADE stage using Chief of Staff's own prompt
            specialist = load_specialist("marketing-brand")
            # Override to use the Chief of Staff SACCADE prompt
            specialist.stages["saccade"].prompt = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / "marketing-brand" / "prompts" / "01-saccade-cos.md")
            runner = PipelineRunner(specialist, dispatch)

            # Execute SACCADE only
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(run_saccade_stage(runner, dispatch, runner.context, "marketing"))
                problem = runner.context.stage_outputs.get("saccade", {})
            finally:
                loop.close()

            print(f"Problem framed: {problem.get('problem_id')} - {problem.get('goal')}")
            return problem
    
    def decompose_goal(self, problem: Dict, raw_record: str) -> CoordinationPlan:
            """
            Stage 2: Goal Decomposition - Department Level Only.

            Decomposes the framed problem into DEPARTMENT-LEVEL objectives.
            Each department head receives ONE objective and owns decomposition within their domain.
            Mycelium handles cross-department coordination.
            """
            print(f"\n=== CHIEF OF STAFF: DEPARTMENT-LEVEL DECOMPOSITION ===")

            problem_id = problem.get("problem_id", "UNKNOWN")
            goal = problem.get("goal", "")
            constraints = problem.get("constraints", [])
            assumptions = problem.get("assumptions", [])
            unknowns = problem.get("unknowns", [])

            # Dynamically discover all available specialists/departments
            specialists_dir = Path(__file__).parent.parent.parent / "kojiki" / "specialists"
            dept_head_mapping = self._get_dept_head_mapping()

            # Build department list from actual specialists
            dept_lines = []
            available_departments = {}
            for dept_name, spec_name in dept_head_mapping.items():
                spec_path = specialists_dir / spec_name
                if spec_path.exists():
                    try:
                        spec = load_specialist(spec_name)
                        prefix = spec.agent_prefix
                        desc = self._get_dept_description(dept_name)
                        dept_lines.append(f"- {dept_name} ({spec_name}): {desc}")
                        available_departments[dept_name] = spec_name
                    except:
                        dept_lines.append(f"- {dept_name} ({spec_name})")
                        available_departments[dept_name] = spec_name

            dept_list = "\n".join(dept_lines)

            # Build decomposition prompt for DEPARTMENT-LEVEL goals only
            decomp_prompt = f"""You are the Chief of Staff. Decompose this problem into DEPARTMENT-LEVEL objectives.

    PROBLEM: {goal}
    CONSTRAINTS: {constraints}
    ASSUMPTIONS: {assumptions}
    UNKNOWNS: {unknowns}

    DEPARTMENT HEADS (you delegate to these, they own decomposition within their domain):
    {dept_list}

    FOR EACH RELEVANT DEPARTMENT, specify:
    1. title: Clear, measurable department outcome (what this department must achieve)
    2. description: What this department needs to accomplish
    3. owner_node: Department head node (MUST BE EXACT NAME FROM LIST ABOVE - e.g., "Engineering" NOT "Engineering.Technology")
    4. specialist_name: Specialist for department head (auto-mapped, leave blank)
    5. priority: 1 (high), 2 (medium), 3 (low)
    6. dependencies: Other department objectives this depends on
    7. success_criteria: [{{name, metric, target, operator, weight}}] - Department-level KRs

    Return JSON array of DEPARTMENT OBJECTIVES (3-6 max). Each department head will further decompose into their team's OKRs.

    IMPORTANT: owner_node MUST match exactly one of the department head names listed above. Do not create sub-department names like "Engineering.Technology" - use "Engineering" instead. The department head will handle internal decomposition.
    """

            dispatch = {
                "task_id": f"cos-decomp-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "raw_record": decomp_prompt,
                "dept_head": "ChiefOfStaff"
            }

            # Run Chief of Staff's own decomposition (using marketing-brand as generic)
            specialist = load_specialist("marketing-brand")
            # Use Chief of Staff's own strategy prompt for decomposition
            specialist.stages["strategy"].prompt = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / "marketing-brand" / "prompts" / "04-strategy-cos.md")
            # Disable schema validation for Chief of Staff strategy (different output format)
            specialist.stages["strategy"].schema = None
            runner = PipelineRunner(specialist, dispatch)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(run_saccade_stage(runner, dispatch, runner.context, "marketing"))
                from kojiki.core.stages import run_evidence_stage, run_interpretation_stage, run_strategy_stage
                loop.run_until_complete(run_evidence_stage(runner, dispatch, runner.context, "marketing"))
                loop.run_until_complete(run_interpretation_stage(runner, dispatch, runner.context, "marketing"))
                # Run strategy stage with Chief of Staff's own prompt (real LLM will decompose the actual goal)
                loop.run_until_complete(run_strategy_stage(runner, dispatch, runner.context, "marketing"))

                strategy_output = runner.context.stage_outputs.get("strategy", {})
            finally:
                loop.close()

            # Parse the decomposition from strategy output
            sub_goals_data = strategy_output.get("actions", [])

            # Convert to SubGoal objects (department-level)
            sub_goals = []
            for i, action in enumerate(sub_goals_data):
                owner = action.get("owner", "Marketing")

                # Validate/correct owner_node to match department heads exactly
                owner = self._validate_owner_node(owner)

                sg = SubGoal(
                    sub_goal_id=f"SG-{problem_id}-{i+1:03d}",
                    title=action.get("description", f"Department objective {i+1}"),
                    description=action.get("description", ""),
                    owner_node=owner,
                    specialist_name=self._owner_to_specialist(owner),
                    parent_goal_id=problem_id,
                    priority=1,
                    dependencies=action.get("dependencies", []),
                    success_criteria=action.get("success_criteria", [])
                )
                sub_goals.append(sg)

            # NOW: Run each department's OWN SACCADE using their specialist
            print(f"\n=== DEPARTMENT HEAD SACCADE DECOMPOSITIONS ===")
            for sg in sub_goals:
                dept_name = sg.owner_node
                if dept_name in available_departments:
                    print(f"  📋 {dept_name} running their SACCADE...")
                    spec_name = available_departments[dept_name]
                    dept_specialist = load_specialist(spec_name)
                    dept_dispatch = {
                        "task_id": f"dh-saccade-{sg.sub_goal_id}",
                        "raw_record": sg.description,
                        "dept_objective": {"objective_id": sg.sub_goal_id, "title": sg.title},
                        "department": dept_name
                    }
                    # Override SACCADE prompt to use Chief of Staff's generic one (returns Problem objects)
                    dept_specialist.stages["saccade"].prompt = str(Path(__file__).parent.parent.parent / "kojiki" / "specialists" / "marketing-brand" / "prompts" / "01-saccade-cos.md")
                    dept_runner = PipelineRunner(dept_specialist, dept_dispatch)

                    dept_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(dept_loop)
                    try:
                        # Run SACCADE for this department head using generic prompt
                        dept_loop.run_until_complete(run_saccade_stage(dept_runner, dept_dispatch, dept_runner.context, dept_name))
                        dept_saccade = dept_runner.context.stage_outputs.get("saccade", {})
                        sg.description = f"DEPT SACCADE: {dept_saccade.get('goal', sg.description)}"
                        print(f"    ✅ {dept_name}: {dept_saccade.get('problem_id', 'N/A')} - {dept_saccade.get('goal', 'N/A')[:80]}")
                    finally:
                        dept_loop.close()
                else:
                    print(f"  ⚠️  {dept_name} specialist not found")

            # Build execution order (topological sort by dependencies)
            execution_order = self._build_execution_order(sub_goals)

            plan = CoordinationPlan(
                plan_id=f"PLAN-{problem_id}",
                original_goal=goal,
                problem_id=problem_id,
                sub_goals=sub_goals,
                execution_order=execution_order,
                created_at=datetime.utcnow().isoformat() + "Z"
            )

            print(f"Decomposed into {len(sub_goals)} DEPARTMENT OBJECTIVES across {len(execution_order)} execution batches")
            for batch_idx, batch in enumerate(execution_order):
                batch_names = [next(sg.title for sg in sub_goals if sg.sub_goal_id == sg_id) for sg_id in batch]
                print(f"  Batch {batch_idx + 1}: {batch_names}")

            return plan
    
    def _validate_owner_node(self, owner_node: str) -> str:
        """Validate and correct owner_node to match exact department head names.
        
        Maps common variations to exact department head names from MYCELIUM registry.
        """
        corrections = {
            "Marketing.Growth": "Marketing",
            "Marketing.Head": "Marketing",
            "Marketing.Brand": "Marketing",
            "Engineering.Referral": "Engineering",
            "Engineering": "Engineering",
            "Engineering.Head": "Engineering",
            "Engineering.Platform": "Engineering",
            "Engineering.Technology": "Engineering",
            "Sales.Outbound": "Sales",
            "Sales.Head": "Sales",
            "Finance.Budget": "Finance",
            "Finance.CFO": "Finance",
            "Product.Head": "Engineering",
            "Customer.Success": "Engineering",
            "Customer.Success.Head": "Engineering",
            "Operations.Head": "Operations",
            "Data.Analytics": "Technology Platform",
            "Data.Analytics.Head": "Technology Platform",
            "Business.Development": "Sales",
            "Business.Development.Head": "Sales",
            "Corporate.Development": "Sales",
            "Supply.Chain.Procurement": "Operations",
            "Supply.Chain.Procurement.Head": "Operations",
            "Corporate.Development": "Sales",
            "AI.Intelligence": "Technology Platform",
            "AI.Intelligence.Head": "Technology Platform",
            "Security": "Technology Platform",
            "Security.Head": "Technology Platform",
            "IT": "Technology Platform",
            "IT.Head": "Technology Platform",
            "People.HR": "People & Comms",
            "People.HR.Head": "People & Comms",
            "Communications.Public.Affairs": "People & Comms",
            "Communications.Public.Affairs.Head": "People & Comms",
            "Compliance.Risk": "Legal",
            "Compliance.Risk.Head": "Legal",
            "Legal.Head": "Legal",
            "Executive.Strategy": "Finance",  # fallback
            "Executive.Office.Chief.of.Staff": "Finance",  # fallback
        }
        
        return corrections.get(owner_node, owner_node)

    def _get_dept_description(self, dept_name: str) -> str:
        """Get description for a department head."""
        descriptions = {
            "Finance": "Budget, CAC, ROI, financial planning",
            "Marketing": "Brand, growth, referral, paid media",
            "Sales": "Pipeline, quota, outbound, enablement, partnerships, M&A, strategic investments",
            "Engineering": "Platform, APIs, infrastructure, product strategy, roadmap, features, retention, expansion, NPS",
            "Operations": "Process, vendors, logistics, procurement, supply chain",
            "Legal": "Contracts, regulatory, compliance, audit, controls, risk",
            "People & Comms": "Hiring, performance, culture, PR, internal comms",
            "Technology Platform": "AI strategy, models, governance, systems, identity, tools, InfoSec, privacy, risk, measurement, attribution, dashboards",
        }
        return descriptions.get(dept_name, "")

    def _get_dept_head_mapping(self) -> Dict[str, str]:
        """Return the department head to specialist mapping (8 consolidated departments)."""
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
        """Map MYCELIUM owner nodes to specialist names."""
        mapping = self._get_dept_head_mapping()
        return mapping.get(owner_node, "marketing-brand")
    
    def _build_execution_order(self, sub_goals: List[SubGoal]) -> List[List[str]]:
        """Topological sort for execution order based on dependencies."""
        # Simple: no dependencies = batch 1, with dependencies = batch 2
        no_deps = [sg.sub_goal_id for sg in sub_goals if not sg.dependencies]
        has_deps = [sg.sub_goal_id for sg in sub_goals if sg.dependencies]
        
        order = []
        if no_deps:
            order.append(no_deps)
        if has_deps:
            order.append(has_deps)
        return order
    
    async def execute_plan(self, plan: CoordinationPlan) -> Dict[str, Any]:
        """Execute the coordination plan in parallel batches."""
        print(f"\n=== CHIEF OF STAFF: EXECUTING PLAN {plan.plan_id} ===")
        
        results = {}
        plan.status = "executing"
        
        for batch_idx, batch in enumerate(plan.execution_order):
            print(f"\n--- Execution Batch {batch_idx + 1}/{len(plan.execution_order)} ---")
            
            batch_tasks = []
            for sg_id in batch:
                sg = next(sg for sg in plan.sub_goals if sg.sub_goal_id == sg_id)
                sg.status = "running"
                print(f"  ▶️ Starting {sg_id} ({sg.specialist_name}) for {sg.owner_node}")
                batch_tasks.append((sg_id, self._execute_sub_goal(sg, plan)))
            
            # Run batch in parallel
            batch_results = await asyncio.gather(*[t[1] for t in batch_tasks], return_exceptions=True)
            
            # Store results
            for (sg_id, _), result in zip(batch_tasks, batch_results):
                sg = next(sg for sg in plan.sub_goals if sg.sub_goal_id == sg_id)
                if isinstance(result, Exception):
                    sg.status = "failed"
                    sg.result = {"error": str(result)}
                    print(f"  ❌ {sg_id} failed: {result}")
                else:
                    sg.status = "completed"
                    sg.result = result
                    results[sg_id] = result
                    print(f"  ✅ {sg_id} completed")
        
        plan.status = "completed"
        
        # Synthesize results
        synthesis = self._synthesize_results(plan, results)
        
        return {
            "plan_id": plan.plan_id,
            "status": plan.status,
            "sub_goal_results": results,
            "synthesis": synthesis,
            "completed_at": datetime.utcnow().isoformat() + "Z"
        }
    
    async def _execute_sub_goal(self, sub_goal: SubGoal, plan: CoordinationPlan) -> Dict:
        """Execute a single sub-goal through its specialist's full pipeline."""
        dispatch = {
            "task_id": sub_goal.sub_goal_id,
            "raw_record": sub_goal.description,
            "parent_plan_id": plan.plan_id,
            "sub_goal_id": sub_goal.sub_goal_id,
            "success_criteria": sub_goal.success_criteria
        }
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                run_pipeline, 
                sub_goal.specialist_name, 
                dispatch
            )
            return result
        except Exception as e:
            return {"error": str(e), "sub_goal_id": sub_goal.sub_goal_id}
    
    def _synthesize_results(self, plan: CoordinationPlan, results: Dict) -> Dict:
        """Synthesize sub-goal results into coherent outcome."""
        print(f"\n=== CHIEF OF STAFF: SYNTHESIS ===")
        
        all_insights = []
        all_actions = []
        all_risks = []
        
        for sg_id, result in results.items():
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
                        "sub_goal": sg_id
                    }
                    for a in strategy.get("actions", [])
                ])
                all_risks.extend(strategy.get("risks", []))
        
        # Create OKRs if engine available
        if self.okr_engine:
            self._create_okrs_from_plan(plan)
        
        synthesis = {
            "plan_id": plan.plan_id,
            "original_goal": plan.original_goal,
            "total_sub_goals": len(plan.sub_goals),
            "completed": len([sg for sg in plan.sub_goals if sg.status == "completed"]),
            "failed": len([sg for sg in plan.sub_goals if sg.status == "failed"]),
            "key_insights": list(set(all_insights)),
            "consolidated_actions": all_actions,
            "consolidated_risks": all_risks,
            "overall_status": "completed" if all(sg.status == "completed" for sg in plan.sub_goals) else "partial"
        }
        
        print(f"Synthesis: {synthesis['completed']}/{synthesis['total_sub_goals']} sub-goals completed")
        print(f"Key insights: {len(synthesis['key_insights'])}")
        print(f"Consolidated actions: {len(synthesis['consolidated_actions'])}")
        
        return synthesis
    
    def _create_okrs_from_plan(self, plan: CoordinationPlan):
        """Create OKR objectives from the coordination plan.
        
        Creates:
        1. Corporate objective (owned by Finance)
        2. Department objectives (owned by department heads only)
        
        Department heads will further decompose into team/individual OKRs.
        """
        if not self.okr_engine:
            return
        
        # Create corporate objective from the original goal
        corp_objective = Objective(
            objective_id=f"OKR-{plan.problem_id}",
            title=plan.original_goal,
            description=f"Coordinated plan: {plan.plan_id}",
            level=OKRLevel.CORPORATE,
            owner_node="Finance",  # Corporate objective owned by Finance dept head (7-dept consolidation)
            key_results=[
                KeyResult(
                    kr_id=f"KR-{plan.problem_id}-{i+1:03d}",
                    objective_id=f"OKR-{plan.problem_id}",
                    description=f"Department objective: {sg.title}",
                    kr_type="metric",
                    target=100.0,
                    current=0.0,
                    unit="%",
                    weight=1.0,
                    source="chief_of_staff_tracking",
                    frequency="weekly",
                    confidence=0.7,
                    is_leading=True
                )
                for i, sg in enumerate(plan.sub_goals)
            ],
            status=OKRStatus.ACTIVE,
            start_date=datetime.utcnow().strftime("%Y-%m-%d"),
            end_date=(datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
            tags=["coordination", plan.plan_id]
        )
        self.okr_engine.create_objective(corp_objective)
        
        # Create DEPARTMENT-LEVEL objectives for each department head
        owner_nodes = set(sg.owner_node for sg in plan.sub_goals)
        for owner_node in owner_nodes:
            owner_sgs = [sg for sg in plan.sub_goals if sg.owner_node == owner_node]
            if not owner_sgs:
                continue
            
            dept_head_mapping = self._get_dept_head_mapping()
            if owner_node not in dept_head_mapping:
                print(f"  ⚠️ Skipping {owner_node} - not a valid department head")
                continue
            
            dept_objective = Objective(
                objective_id=f"OKR-{owner_node.replace('.', '-')}-{plan.problem_id}",
                title=f"{owner_node} contribution to {plan.original_goal}",
                description=f"Department objective for {owner_node}",
                level=OKRLevel.DEPARTMENT,
                owner_node=owner_node,
                parent_objective_id=f"OKR-{plan.problem_id}",
                key_results=[
                    KeyResult(
                        kr_id=f"KR-{owner_node.replace('.', '-')}-{plan.problem_id}-{i+1:03d}",
                        objective_id=f"OKR-{owner_node.replace('.', '-')}-{plan.problem_id}",
                        description=sg.title,
                        kr_type="metric",
                        target=100.0,
                        current=0.0,
                        unit="%",
                        weight=1.0,
                        source="chief_of_staff_tracking",
                        frequency="weekly",
                        confidence=0.8,
                        is_leading=True
                    )
                    for i, sg in enumerate(owner_sgs)
                ],
                status=OKRStatus.ACTIVE,
                start_date=datetime.utcnow().strftime("%Y-%m-%d"),
                end_date=(datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
                tags=["coordination", plan.plan_id, owner_node]
            )
            self.okr_engine.create_objective(dept_objective)
        
        print(f"  ✅ Created OKRs: 1 corporate + {len(owner_nodes)} department objectives")
        
        # Trigger department head decomposition for each department
        self._trigger_dept_head_decomposition(plan)
    
    def _trigger_dept_head_decomposition(self, plan: CoordinationPlan):
        """Trigger department head decomposition for each department objective."""
        if not self.okr_engine:
            return
        
        owner_nodes = set(sg.owner_node for sg in plan.sub_goals)
        
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from dept_head_base import get_dept_head
        
        for owner_node in owner_nodes:
            dept_head_mapping = self._get_dept_head_mapping()
            if owner_node not in dept_head_mapping:
                continue
            
            dept_objective_id = f"OKR-{owner_node.replace('.', '-')}-{plan.problem_id}"
            dept_objective = self.okr_engine.get_objective(dept_objective_id)
            if not dept_objective:
                continue
            
            dept_head = get_dept_head(
                owner_node,
                self.registry,
                self.propagator,
                self.sentinel,
                self.okr_engine
            )
            
            if dept_head:
                print(f"  🔄 Triggering {owner_node} decomposition...")
                try:
                    team_okrs = dept_head.decompose_objective(dept_objective)
                    print(f"  ✅ {owner_node} created {len(team_okrs)} team OKRs")
                except Exception as e:
                    print(f"  ❌ {owner_node} decomposition failed: {e}")
            else:
                print(f"  ⚠️ No dept head implementation for {owner_node}")
    
    def coordinate(self, raw_record: str, context: Dict = None) -> Dict[str, Any]:
        """
        Main entry point: Coordinate a high-level goal end-to-end.
        
        1. SACCADE framing (with cache check)
        2. Goal decomposition
        3. Parallel execution
        4. Synthesis
        5. Cache SACCADE for future reuse
        """
        print(f"\n{'='*60}")
        print(f"CHIEF OF STAFF COORDINATION STARTED")
        print(f"{'='*60}")
        
        # Stage 1: Frame the problem (with cache check)
        problem = self.frame_problem(raw_record, context)
        
        # Store SACCADE in cache for future reuse
        if self.chief_myelium and problem.get('problem_id'):
            department = context.get('department', 'Marketing') if context else 'Marketing'
            constraints = problem.get('constraints', [])
            assumptions = problem.get('assumptions', [])
            unknowns = problem.get('unknowns', [])
            
            self.chief_myelium.store_saccade(
                problem_id=problem['problem_id'],
                goal=problem['goal'],
                constraints=constraints,
                assumptions=assumptions,
                unknowns=unknowns,
                department=department
            )
        
        # Stage 2: Decompose into sub-goals
        plan = self.decompose_goal(problem, raw_record)
        
        # Stage 3: Execute plan
        execution_result = asyncio.run(self.execute_plan(plan))
        
        # Stage 4: Cross-department coordination via Mycelium (if multiple departments)
        if self.chief_myelium and len(plan.sub_goals) > 1:
            departments = list(set(sg.owner_node for sg in plan.sub_goals))
            self.chief_myelium.coordinate_cross_department(
                goal=raw_record,
                departments=departments,
                context={
                    "plan_id": plan.plan_id,
                    "problem_id": problem.get('problem_id'),
                    "sub_goals": [{"owner": sg.owner_node, "title": sg.title} for sg in plan.sub_goals]
                }
            )
        
        # Final result
        final_result = {
            "coordination_id": f"COS-{problem.get('problem_id', 'UNKNOWN')}",
            "problem": problem,
            "plan": asdict(plan),
            "execution": execution_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.execution_history.append(final_result)
        
        print(f"\n{'='*60}")
        print(f"CHIEF OF STAFF COORDINATION COMPLETED")
        print(f"{'='*60}")
        
        return final_result


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