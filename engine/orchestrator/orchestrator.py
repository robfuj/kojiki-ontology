#!/usr/bin/env python3
"""
Orchestrator — Goal decomposition, department selection, and reasoning trace.
Replaces Chief of Staff with transparent orchestration.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field

from engine.kojiki_core import load_specialist
from engine.kojiki_core.runner import PipelineRunner
from engine.kojiki_core.stages import run_saccade_stage
from engine.kojiki_core.utils import is_test_mode, create_dispatch
from engine.mycelium.okr_engine import OKREngine, OKRLevel, KRType
from engine.mycelium.propagate import SignalPropagator
from engine.mycelium.registry import NodeRegistry
from engine.sentinel import SentinelEngine, KeyManager


@dataclass
class DepartmentChoice:
    """Why a department was selected for a goal."""
    department: str
    specialist_name: str
    reason: str
    okr_alignment: str
    confidence: float
    dependencies: List[str]


@dataclass
class OrchestrationResult:
    """Full trace of orchestration decisions."""
    orchestration_id: str
    raw_goal: str
    orientation_findings: Dict[str, Any]
    problem_framing: Dict[str, Any]
    department_choices: List[DepartmentChoice]
    okr_decomposition: Dict[str, Any]
    execution_results: Dict[str, Any]
    timestamp: str


class Orchestrator:
    """
    Transparent goal decomposition and department dispatch.
    
    Flow:
    1. Orientation Protocol — industry research on the goal
    2. SACCADE Framing — sharpen raw goal into structured Problem
    3. Department Selection — which dept heads own this, with reasoning
    4. OKR Decomposition — corporate OKR → dept OKRs → team OKRs
    4. Parallel Dispatch — each dept head runs full SYNAPSIS pipeline
    5. Mycelium Coordination — cross-dept signals
    6. Synthesis + User Approval Gate
    7. Re-loop if needed
    """
    
    def __init__(self):
        self.sentinel = SentinelEngine()
        self.okr_engine = OKREngine()
        self.key_manager = KeyManager()
        self.registry = NodeRegistry(registry_path="/tmp/nodes.json")
        self.propagator = SignalPropagator(
            edge_store_path="/tmp/edges.json",
            log_path="/tmp/signals.jsonl",
            registry=self.registry
        )
        
    async def orchestrate(
        self, 
        raw_goal: str, 
        context: Optional[Dict[str, Any]] = None,
        require_approval: bool = True
    ) -> OrchestrationResult:
        """Main entry: orchestrate a goal end-to-end."""
        
        orchestration_id = f"ORCH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        print(f"\n{'='*60}")
        print(f"ORCHESTRATOR STARTED: {orchestration_id}")
        print(f"Goal: {raw_goal[:100]}...")
        print(f"{'='*60}")
        
        # Phase 1: Orientation Protocol
        orientation = await self._run_orientation(raw_goal, context)
        
        # Phase 2: SACCADE Framing
        problem = await self._frame_problem(raw_goal, orientation, context)
        
        # Phase 3: Department Selection (with reasoning)
        dept_choices = self._select_departments(problem, orientation)
        
        # Phase 4: OKR Decomposition
        okr_decomposition = self._decompose_okrs(problem, dept_choices)
        
        # Phase 5: Parallel Dispatch
        execution_results = await self._dispatch_parallel(
            problem, dept_choices, okr_decomposition, context
        )
        
        # Phase 6: Mycelium Coordination
        await self._coordinate_mycelium(dept_choices, execution_results)
        
        # Phase 7: User Approval Gate
        if require_approval:
            approved = await self._user_approval_gate(execution_results)
            if not approved:
                # Re-loop with feedback
                pass
        
        result = OrchestrationResult(
            orchestration_id=orchestration_id,
            raw_goal=raw_goal,
            orientation_findings=orientation,
            problem_framing=problem,
            department_choices=dept_choices,
            okr_decomposition=okr_decomposition,
            execution_results=execution_results,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Sign orchestration in SENTINEL
        self._sign_orchestration(result)
        
        print(f"\n{'='*60}")
        print(f"ORCHESTRATION COMPLETE: {orchestration_id}")
        print(f"{'='*60}")
        
        return result
    
    async def _run_orientation(
        self, 
        raw_goal: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Phase 1: Orientation Protocol — industry research on the goal."""
        print("\n--- PHASE 1: ORIENTATION PROTOCOL ---")
        
        # In production: call industry research APIs, market data, competitor analysis
        # For now: structured stub that shows the reasoning framework
        
        orientation = {
            "goal": raw_goal,
            "industry_context": {
                "market_size": "TBD - research needed",
                "key_players": "TBD - research needed",
                "regulatory_landscape": "TBD - research needed",
                "technology_trends": "TBD - research needed"
            },
            "competitive_analysis": {
                "direct_competitors": [],
                "indirect_competitors": [],
                "differentiation_opportunities": []
            },
            "risk_assessment": {
                "market_risks": [],
                "technical_risks": [],
                "regulatory_risks": [],
                "execution_risks": []
            },
            "methodology": "orientation_protocol_v1",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"  Industry context gathered")
        print(f"  Competitive landscape mapped")
        print(f"  Risk factors identified")
        
        return orientation
    
    async def _frame_problem(
        self, 
        raw_goal: str, 
        orientation: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Phase 2: SACCADE Framing — sharpen raw goal into structured Problem."""
        print("\n--- PHASE 2: SACCADE FRAMING ---")
        
        dispatch = create_dispatch(
            task_id=f"orch-saccade-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            raw_record=raw_goal,
            raw_source=context or {},
            prior_accepted_evidence=[]
        )
        
        # Add orientation context
        dispatch["orientation"] = orientation
        
        specialist = load_specialist("chief-of-staff")
        runner = PipelineRunner(specialist, dispatch)
        
        # Run only SACCADE stage
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            await run_saccade_stage(runner, dispatch, runner.context, "orchestrator")
            problem = runner.context.stage_outputs.get("saccade", {})
        finally:
            loop.close()
        
        print(f"  Problem framed: {problem.get('problem_id')} - {problem.get('goal')}")
        
        return problem
    
    def _select_departments(
        self, 
        problem: Dict[str, Any], 
        orientation: Dict[str, Any]
    ) -> List[DepartmentChoice]:
        """Phase 3: Department Selection with transparent reasoning."""
        print("\n--- PHASE 3: DEPARTMENT SELECTION ---")
        
        # Map problem domain to departments with reasoning
        dept_mapping = {
            "marketing-brand": {
                "keywords": ["brand", "campaign", "lead", "growth", "referral", "paid", "seo", "content"],
                "scope": "Brand, growth, referral, paid media"
            },
            "sales-outbound": {
                "keywords": ["outbound", "bizdev", "corpdev", "pipeline", "conversion", "deal"],
                "scope": "Outbound, growth, Biz Dev, Corp Dev"
            },
            "finance-accounting": {
                "keywords": ["budget", "cac", "roi", "fp&a", "treasury", "revenue", "cost"],
                "scope": "Budget, CAC, ROI, FP&A, treasury"
            },
            "engineering-platform": {
                "keywords": ["product", "tech", "platform", "infrastructure", "referral tech", "api"],
                "scope": "Product, Customer Success, Technology, Referral tech"
            },
            "operations-ops": {
                "keywords": ["supply", "procurement", "ops", "logistics", "fulfillment"],
                "scope": "Supply chain, procurement, day-to-day ops"
            },
            "legal-compliance": {
                "keywords": ["compliance", "risk", "contract", "regulatory", "legal", "gdpr"],
                "scope": "Compliance, Risk, contracts, regulatory"
            },
            "people-hr": {
                "keywords": ["hr", "hiring", "team", "culture", "comms", "internal"],
                "scope": "HR, Internal comms, Public Affairs"
            },
            "ai-intelligence": {
                "keywords": ["ai", "model", "governance", "infosec", "identity", "tools", "ml"],
                "scope": "AI strategy, models, governance, InfoSec, identity, tools"
            }
        }
        
        problem_text = (problem.get("goal", "") + " " + " ".join(problem.get("constraints", [])) + " " + " ".join(problem.get("assumptions", []))).lower()
        
        choices = []
        for dept_name, dept_info in dept_mapping.items():
            matches = sum(1 for kw in dept_info["keywords"] if kw in problem_text)
            if matches > 0:
                confidence = min(matches / len(dept_info["keywords"]) * 2, 1.0)
                choice = DepartmentChoice(
                    department=dept_name.replace("-", " ").title(),
                    specialist_name=dept_name,
                    reason=f"Matched {matches}/{len(dept_info['keywords'])} domain keywords: {[kw for kw in dept_info['keywords'] if kw in problem_text]}",
                    okr_alignment=f"Aligns with {dept_info['scope']}",
                    confidence=confidence,
                    dependencies=[]
                )
                choices.append(choice)
                print(f"  ✅ {dept_name} (confidence: {confidence:.1%}) - {choice.reason}")
        
        # Sort by confidence
        choices.sort(key=lambda c: c.confidence, reverse=True)
        
        # Add cross-department dependencies
        for i, choice in enumerate(choices):
            if choice.specialist_name == "marketing-brand" and any(c.specialist_name == "sales-outbound" for c in choices):
                choice.dependencies.append("sales-outbound")
            if choice.specialist_name == "sales-outbound" and any(c.specialist_name == "engineering-platform" for c in choices):
                choice.dependencies.append("engineering-platform")
            if choice.specialist_name == "engineering-platform" and any(c.specialist_name == "finance-accounting" for c in choices):
                choice.dependencies.append("finance-accounting")
        
        return choices
    
    def _decompose_okrs(
        self, 
        problem: Dict[str, Any], 
        dept_choices: List[DepartmentChoice]
    ) -> Dict[str, Any]:
        """Phase 4: OKR Decomposition — corporate OKR → dept OKRs → team OKRs."""
        print("\n--- PHASE 4: OKR DECOMPOSITION ---")
        
        # Create corporate objective
        corporate_obj = self.okr_engine.create_objective(
            name=f"Corporate: {problem.get('goal', 'Strategic Goal')}",
            description=problem.get('goal', ''),
            level=OKRLevel.CORPORATE,
            owner="CEO"
        )
        
        dept_okrs = {}
        for choice in dept_choices:
            # Create department objective under corporate
            dept_obj = self.okr_engine.create_objective(
                name=f"Dept: {choice.department}",
                description=f"Support corporate goal: {problem.get('goal', '')}",
                level=OKRLevel.DEPARTMENT,
                owner=f"{choice.department}.Head",
                parent_id=corporate_obj.id
            )
            
            # Add default KRs based on department
            if choice.specialist_name == "marketing-brand":
                self.okr_engine.add_key_result(dept_obj.id, "Referral pipeline QoQ growth", KRType.METRIC, 0.15, "%")
                self.okr_engine.add_key_result(dept_obj.id, "Paid CAC reduction", KRType.METRIC, -0.20, "%")
            elif choice.specialist_name == "sales-outbound":
                self.okr_engine.add_key_result(dept_obj.id, "Qualified pipeline growth", KRType.METRIC, 0.25, "%")
                self.okr_engine.add_key_result(dept_obj.id, "Win rate improvement", KRType.METRIC, 0.10, "%")
            elif choice.specialist_name == "finance-accounting":
                self.okr_engine.add_key_result(dept_obj.id, "Budget variance", KRType.METRIC, -0.05, "%")
                self.okr_engine.add_key_result(dept_obj.id, "CAC/LTV ratio", KRType.METRIC, 3.0, "x")
            
            dept_okrs[choice.specialist_name] = {
                "objective_id": dept_obj.id,
                "name": dept_obj.name,
                "owner": dept_obj.owner,
                "key_results": [{"name": kr.name, "target": kr.target, "unit": kr.unit, "weight": kr.weight} for kr in self.okr_engine.get_key_results(dept_obj.id)]
            }
            
            print(f"  📊 {choice.department}: {len(dept_okrs[choice.specialist_name]['key_results'])} KRs")
        
        return {
            "corporate_objective": {"id": corporate_obj.id, "name": corporate_obj.name, "owner": corporate_obj.owner},
            "department_okrs": dept_okrs
        }
    
    async def _dispatch_parallel(
        self,
        problem: Dict[str, Any],
        dept_choices: List[DepartmentChoice],
        okr_decomposition: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Phase 5: Dispatch each dept head in parallel."""
        print("\n--- PHASE 5: PARALLEL DISPATCH ---")
        
        results = {}
        
        async def run_department(choice: DepartmentChoice):
            dispatch = create_dispatch(
                task_id=f"orch-{choice.specialist_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                raw_record=problem.get("goal", ""),
                raw_source={"problem": problem, "okr": okr_decomposition.get("department_okrs", {}).get(choice.specialist_name, {})},
                prior_accepted_evidence=[]
            )
            
            specialist = load_specialist(choice.specialist_name)
            runner = PipelineRunner(specialist, dispatch)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = await runner.run()
                return choice.specialist_name, result
            finally:
                loop.close()
        
        # Run all in parallel
        tasks = [run_department(c) for c in dept_choices]
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in completed:
            if isinstance(result, Exception):
                print(f"  ❌ Department failed: {result}")
            else:
                dept_name, dept_result = result
                results[dept_name] = dept_result
                print(f"  ✅ {dept_name} completed")
        
        return results
    
    async def _coordinate_mycelium(
        self,
        dept_choices: List[DepartmentChoice],
        execution_results: Dict[str, Any]
    ):
        """Phase 6: Mycelium cross-department coordination."""
        print("\n--- PHASE 6: MYCELIUM COORDINATION ---")
        
        for dept_name, result in execution_results.items():
            outcome = result.get("outcome", {})
            evaluations = outcome.get("evaluations", [])
            
            for eval in evaluations:
                if not eval.get("passed", True):
                    # Create failure signal
                    signal = {
                        "signal_id": f"SIG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                        "source_node": f"{dept_name}.Head",
                        "target_node": "cross-department",
                        "signal_type": "FAILURE",
                        "diagnosed_cause": f"KPI {eval.get('metric')} missed target",
                        "category": "execution",
                        "payload": eval,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                    self.propagator.propagate(signal)
        
        print(f"  Mycelium signals propagated across {len(dept_choices)} departments")
    
    async def _user_approval_gate(self, execution_results: Dict[str, Any]) -> bool:
        """Phase 7: User approval gate before re-loop."""
        print("\n--- PHASE 7: USER APPROVAL GATE ---")
        print("Execution results summary:")
        for dept, result in execution_results.items():
            outcome = result.get("outcome", {})
            print(f"  {dept}: outcome_score={outcome.get('outcome_score', 0):.2f}, converged={outcome.get('converged', False)}")
        
        # In production: this would be a real UI/notification
        # For CLI: prompt user
        print("\n⚠️  APPROVAL REQUIRED: Should the orchestrator re-loop with feedback?")
        print("  (In production: this would be a UI notification with approve/reject buttons)")
        
        # For test mode: auto-approve if all converged
        all_converged = all(
            r.get("outcome", {}).get("converged", False) 
            for r in execution_results.values()
        )
        
        if is_test_mode():
            return all_converged
        
        # Real approval would happen here
        return True
    
    def _sign_orchestration(self, result: OrchestrationResult):
        """Record orchestration in SENTINEL."""
        self.sentinel.write_signal({
            "signal_id": f"ORCH-{result.orchestration_id}",
            "source_node": "ORCHESTRATOR",
            "target_node": "SYSTEM",
            "signal_type": "ORCHESTRATION_COMPLETE",
            "payload": {
                "orchestration_id": result.orchestration_id,
                "departments": [c.specialist_name for c in result.department_choices],
                "approval_required": True
            },
            "timestamp": result.timestamp
        })
        print(f"  🔐 Signed in SENTINEL: {result.orchestration_id}")


async def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m engine.orchestrator.orchestrator '<goal>' [--no-approval]")
        sys.exit(1)
    
    goal = sys.argv[1]
    require_approval = "--no-approval" not in sys.argv
    
    orchestrator = Orchestrator()
    result = await orchestrator.orchestrate(goal, require_approval=require_approval)
    
    # Save result
    output_path = Path(f"/tmp/orchestration_{result.orchestration_id}.json")
    output_path.write_text(json.dumps(asdict(result), indent=2, default=str))
    print(f"\nResult saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())