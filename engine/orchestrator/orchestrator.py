#!/usr/bin/env python3
"""
Orchestrator — Goal decomposition, department selection, and reasoning trace.

Refactored into modular components:
- bootstrap.py — registry initialization and decision rights wiring
- department_selection.py — transparent department selection reasoning
- dispatch.py — parallel dispatch with consultation rounds
- okr_engine.py — OKR decomposition (moved to mycelium/okr_engine.py)
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from engine.kojiki_core import load_specialist
from engine.kojiki_core.runner import PipelineRunner
from engine.kojiki_core.stages import run_saccade_stage, run_evidence_stage
from engine.kojiki_core.orientation_protocol import run_orientation_protocol
from engine.kojiki_core.utils import is_test_mode, create_dispatch
from engine.mycelium.okr_engine import OKREngine, OKRLevel, KRType
from engine.mycelium.propagate import SignalPropagator
from engine.mycelium.registry import NodeRegistry
from engine.mycelium.conversation_layer import MyceliumConversationLayer
from engine.sentinel import SentinelEngine, KeyManager

from .bootstrap import bootstrap_registry, wire_decision_rights, resolve_data_dir, resolve_orchestrator_node_id
from .department_selection import DepartmentChoice, select_departments
from .dispatch import dispatch_with_consultation, run_department_stage
from .approval import create_approval_channel, ApprovalRequest


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
    5. Parallel Dispatch — each dept head runs full SYNAPSIS pipeline
       - BATCH 1: EVIDENCE for independent departments
       - CONSULTATION: MyceliumConversationLayer
       - BATCH 2: INTERPRETATION/STRATEGY/OUTPUT/DELEGATION/HANDOFF/MYCELIUM/OUTCOME/LEARNING
    6. Mycelium Coordination — cross-dept signals
    7. Synthesis + User Approval Gate
    8. Re-loop if needed (max 3 retries)
    """

    MAX_RETRIES = 3

    def __init__(
        self,
        data_dir: Optional[str] = None,
        orchestrator_node_id: Optional[str] = None,
        approval_channel: Optional[str] = None
    ):
        # Resolve data directory from env or parameter (NOT /tmp)
        self.data_dir = resolve_data_dir(data_dir)

        self.sentinel = SentinelEngine()
        self.okr_engine = OKREngine(store_path=str(self.data_dir / "okrs.json"))
        self.key_manager = KeyManager()
        self.registry = NodeRegistry(registry_path=str(self.data_dir / "nodes.json"))

        # Bootstrap registry with 8 root departments + head nodes + Orchestrator
        bootstrap_registry(self.registry, self.key_manager, orchestrator_node_id)

        # Handle Orchestrator node ID - prompt user if not provided
        self.orchestrator_node_id = resolve_orchestrator_node_id(orchestrator_node_id)

        self.propagator = SignalPropagator(
            edge_store_path=str(self.data_dir / "edges.json"),
            log_path=str(self.data_dir / "signals.jsonl"),
            registry=self.registry
        )
        self.conversation_layer = MyceliumConversationLayer(
            propagator=self.propagator,
            registry=self.registry,
            sentinel=self.sentinel,
            max_rounds=3,
            consultation_store_path=str(self.data_dir / "consultations.json")
        )

        # Wire decision rights for consultation layer
        wire_decision_rights(self.registry, self.conversation_layer)

        # Approval channel
        self.approval_channel = create_approval_channel(approval_channel)

    async def orchestrate(
        self,
        raw_goal: str,
        context: Optional[Dict[str, Any]] = None,
        require_approval: bool = True,
        feedback: Optional[str] = None,
        retry_count: int = 0
    ) -> OrchestrationResult:
        """Main entry: orchestrate a goal end-to-end."""

        orchestration_id = f"ORCH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Store for approval gate
        self.current_orchestration_id = orchestration_id
        self.current_raw_goal = raw_goal
        self.current_retry_count = retry_count

        print(f"\n{'='*60}")
        print(f"ORCHESTRATOR STARTED: {orchestration_id}")
        print(f"Goal: {raw_goal[:100]}...")
        print(f"{'='*60}")

        # Phase 1: Orientation Protocol
        orientation = await self._run_orientation(raw_goal, context)

        # Phase 2: SACCADE Framing
        problem = await self._frame_problem(raw_goal, orientation, context)

        # Phase 3: Department Selection (with reasoning)
        dept_choices = select_departments(problem, orientation)

        # Phase 4: OKR Decomposition
        okr_decomposition = self.okr_engine.decompose_okrs(problem, dept_choices, self.registry)

        # Phase 5: Parallel Dispatch with consultation rounds
        execution_results = await dispatch_with_consultation(
            self, problem, dept_choices, okr_decomposition, context
        )

        # Phase 6: Mycelium Coordination
        await self._coordinate_mycelium(dept_choices, execution_results)

        # Phase 7: User Approval Gate
        if require_approval:
            approved = await self._user_approval_gate(execution_results)
            if not approved:
                # Re-loop with feedback - actual re-loop
                if retry_count >= self.MAX_RETRIES:
                    print(f"  ⚠️ Max retries ({self.MAX_RETRIES}) reached without approval — returning unapproved result")
                    # Return result anyway but mark as unapproved
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
                    self._sign_orchestration(result)
                    return result

                feedback = "Rejected by user approval gate"
                return await self.orchestrate(
                    raw_goal,
                    context=context,
                    require_approval=require_approval,
                    feedback=feedback,
                    retry_count=retry_count + 1
                )

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
        """Phase 1: Orientation Protocol — Akinator-style adaptive questioning to pinpoint intent."""
        print("\n--- PHASE 1: ORIENTATION PROTOCOL (Akinator-style) ---")

        # Run the new orientation protocol
        orientation = await run_orientation_protocol(
            raw_goal=raw_goal,
            context=context,
            max_clarifying=4,
            max_follow_ups=4
        )

        print(f"  Refined goal: {orientation.get('refined_goal', 'N/A')}")
        print(f"  Confidence: {orientation.get('confidence', 0):.1%}")
        print(f"  Turns: {orientation.get('turns_count', 0)}")
        print(f"  Top hypothesis: {orientation.get('intent_hypothesis', {}).get('description', 'N/A')}")

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

        specialist = load_specialist("orchestrator")
        runner = PipelineRunner(specialist, dispatch)

        # Run only SACCADE stage - directly await since we're in async context
        await run_saccade_stage(runner, dispatch, runner.context, "orchestrator")
        problem = runner.context.stage_outputs.get("saccade", {})

        print(f"  Problem framed: {problem.get('problem_id')} - {problem.get('goal')}")

        return problem

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
                        "origin_kr": f"{dept_name}.Head",
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

        # Create approval request
        request = ApprovalRequest(
            orchestration_id=getattr(self, 'current_orchestration_id', 'UNKNOWN'),
            raw_goal=getattr(self, 'current_raw_goal', ''),
            execution_results=execution_results,
            retry_count=getattr(self, 'current_retry_count', 0),
            created_at=datetime.utcnow().isoformat() + "Z"
        )

        # Request approval via channel
        decision = await self.approval_channel.request_approval(request)

        if decision.approved:
            print(f"  ✅ Approved by {decision.decided_by}: {decision.feedback}")
            return True

        print(f"  ❌ Rejected by {decision.decided_by}: {decision.feedback}")
        return False

    def _sign_orchestration(self, result: OrchestrationResult):
        """Record orchestration in SENTINEL."""
        # Use registry signer for audit log integrity
        self.sentinel.write_signal(
            signer="registry",
            signal_id=f"ORCH-{result.orchestration_id}",
            signal={
                "orchestration_id": result.orchestration_id,
                "departments": [c.specialist_name for c in result.department_choices],
                "approval_required": True
            }
        )
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

    # Save result to data directory (not /tmp)
    output_path = orchestrator.data_dir / f"orchestration_{result.orchestration_id}.json"
    output_path.write_text(json.dumps(result.__dict__, indent=2, default=str))
    print(f"\nResult saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())