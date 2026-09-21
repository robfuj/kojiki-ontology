#!/usr/bin/env python3
"""
Dispatch module for Orchestrator — parallel dispatch with consultation rounds.

Handles:
- Topological batching by dependencies
- EVIDENCE stage execution in parallel
- MyceliumConversationLayer consultation rounds
- Full SYNAPSIS pipeline per department after consultation
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from engine.kojiki_core import load_specialist
from engine.kojiki_core.runner import PipelineRunner
from engine.kojiki_core.stages import run_evidence_stage
from engine.kojiki_core.utils import create_dispatch
from engine.mycelium.conversation_layer import MyceliumConversationLayer
from engine.mycelium.okr_engine import OKREngine, OKRLevel, KRType

from .department_selection import DepartmentChoice


async def run_evidence_batch(
    batch: List[DepartmentChoice],
    problem: Dict[str, Any],
    okr_decomposition: Dict[str, Any],
    context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Run EVIDENCE stage for a batch of departments in parallel."""
    print(f"    🔍 Running EVIDENCE for {len(batch)} departments...")

    evidence_outputs = {}

    async def run_evidence(choice: DepartmentChoice):
        dispatch = create_dispatch(
            task_id=f"orch-{choice.specialist_name}-evidence-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            raw_record=problem.get("goal", ""),
            raw_source={"problem": problem, "okr": okr_decomposition.get("department_okrs", {}).get(choice.specialist_name, {})},
            prior_accepted_evidence=[]
        )

        specialist = load_specialist(choice.specialist_name)
        runner = PipelineRunner(specialist, dispatch)

        # Run only EVIDENCE stage - directly await since we're in async context
        await run_evidence_stage(runner, dispatch, runner.context, "orchestrator")
        evidence = runner.context.stage_outputs.get("evidence", {})
        return choice.specialist_name, evidence

    tasks = [run_evidence(c) for c in batch]
    completed = await asyncio.gather(*tasks, return_exceptions=True)

    for result in completed:
        if isinstance(result, BaseException):
            print(f"    ❌ EVIDENCE failed: {result}")
        else:
            dept_name, evidence = result
            evidence_outputs[dept_name] = evidence
            print(f"    ✅ {dept_name} EVIDENCE complete")

    return evidence_outputs


def topological_batches(dept_choices: List[DepartmentChoice]) -> List[List[DepartmentChoice]]:
    """Batch departments by dependency layer (topological sort)."""
    remaining = {c.specialist_name: c for c in dept_choices}
    done = set()
    batches = []

    while remaining:
        ready = [c for c in remaining.values() if all(d in done for d in c.dependencies)]
        if not ready:
            # Circular or unresolvable dependency — break the cycle rather than hang
            ready = list(remaining.values())
        batches.append(ready)
        for c in ready:
            done.add(c.specialist_name)
            del remaining[c.specialist_name]

    return batches


async def run_consultation_rounds(
    conversation_layer: MyceliumConversationLayer,
    batch: List[DepartmentChoice],
    evidence_outputs: Dict[str, Any],
    problem: Dict[str, Any],
    context: Optional[Dict[str, Any]],
    run_department_stage
) -> Dict[str, Any]:
    """Open consultation window and run consultation rounds."""
    # Step 2: Open consultation window
    session = conversation_layer.open_consultation(
        batch_departments=[c.specialist_name for c in batch],
        evidence_outputs=evidence_outputs,
        problem_context=problem
    )

    # Step 3: Run consultation rounds
    consultation_contexts = await conversation_layer.run_consultation_round(
        session=session,
        run_department_stage=run_department_stage,
        problem=problem,
        context=context
    )

    return consultation_contexts


async def run_department_full_pipeline(
    choice: DepartmentChoice,
    problem: Dict[str, Any],
    okr_decomposition: Dict[str, Any],
    context: Optional[Dict[str, Any]],
    consultation_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Run full SYNAPSIS pipeline for a department (after consultation)."""
    dispatch = create_dispatch(
        task_id=f"orch-{choice.specialist_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        raw_record=problem.get("goal", ""),
        raw_source={
            "problem": problem,
            "okr": okr_decomposition.get("department_okrs", {}).get(choice.specialist_name, {}),
            "consultation": consultation_context
        },
        prior_accepted_evidence=[]
    )

    specialist = load_specialist(choice.specialist_name)
    runner = PipelineRunner(specialist, dispatch)

    # Run full pipeline - directly await since we're in async context
    result = await runner.run()
    return result


async def run_department_stage(
    dept: str,
    stage_name: str,
    consultation_context: Dict[str, Any],
    problem: Dict[str, Any],
    context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Run a specific stage for a department (used during consultation)."""
    # This is called by MyceliumConversationLayer during consultation rounds
    # The department can respond to consultation requests, ask questions, etc.
    # Returns consultation_output with possible "consultation_requests" and "continue_consultation"

    # Check if there are consultation requests addressed to this department
    addressed_turns = consultation_context.get("addressed_to_me", [])
    consultation_requests = []
    continue_consultation = False

    for turn in addressed_turns:
        if turn.get("kind") == "consultation_request":
            content = turn.get("content", {})
            question = content.get("question", "")
            requires_response = content.get("requires_response", True)

            if requires_response:
                # In production, this would call the actual department's consultation handling
                # For now, generate a basic response acknowledging the question
                consultation_requests.append({
                    "target_department": turn.get("from", "").split(".")[0],
                    "question": f"Response to: {question}",
                    "context": {"original_question": question},
                    "urgency": "normal",
                    "requires_response": False
                })
                continue_consultation = True

    return {
        "consultation_requests": consultation_requests,
        "continue_consultation": continue_consultation,
        "consultation_notes": f"{dept} processed {len(addressed_turns)} consultation turns"
    }


async def dispatch_with_consultation(
    orchestrator,
    problem: Dict[str, Any],
    dept_choices: List[DepartmentChoice],
    okr_decomposition: Dict[str, Any],
    context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Phase 5: Dispatch with consultation rounds.

    Flow:
    1. Batch departments by dependencies
    2. For each batch:
       a. Run EVIDENCE for all departments in batch (parallel)
       b. Open MyceliumConversationLayer consultation
       c. Run INTERPRETATION/STRATEGY/OUTPUT/DELEGATION/HANDOFF/MYCELIUM/OUTCOME/LEARNING
    """
    print("\n--- PHASE 5: PARALLEL DISPATCH WITH CONSULTATION ---")

    results = {}
    batches = topological_batches(dept_choices)

    for batch_idx, batch in enumerate(batches):
        print(f"\n  📦 Batch {batch_idx + 1}/{len(batches)}: {[c.specialist_name for c in batch]}")

        # Step 1: Run EVIDENCE for all departments in this batch
        evidence_outputs = await run_evidence_batch(batch, problem, okr_decomposition, context)

        # Step 2-3: Open consultation window and run consultation rounds
        consultation_contexts = await run_consultation_rounds(
            orchestrator.conversation_layer,
            batch,
            evidence_outputs,
            problem,
            context,
            run_department_stage
        )

        # Step 4: Run remaining stages for each department with consultation context
        for choice in batch:
            dept_name = choice.specialist_name
            dept_result = await run_department_full_pipeline(
                choice, problem, okr_decomposition, context, consultation_contexts.get(dept_name, {})
            )
            results[dept_name] = dept_result
            print(f"  ✅ {dept_name} completed full pipeline")

    return results