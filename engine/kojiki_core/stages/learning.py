#!/usr/bin/env python3
"""
Stage 8: LEARNING - Kaizen Loop Synthesis
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import re
from engine.kojiki_core import ScopedContext, call_model, validate_against_schema, StageName


async def run_learning_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute LEARNING stage with Kaizen synthesis."""
    print("\n--- STAGE 8: LEARNING (Kaizen Loop Synthesis) ---")
    
    specialist = runner.specialist
    stage_config = specialist.stages.get("learning")
    
    # Use Kaizen learning synthesis if available
    kaizen_learning = context.stage_outputs.get("kaizen_learning", {})
    if kaizen_learning:
        # Transform kaizen learning output to match schema
        experiences = kaizen_learning.get("experiences", [])
        # Ensure error_classification matches schema enum
        for exp in experiences:
            ec = exp.get("error_classification")
            if ec and ec not in ["L0_execution", "L1_reasoning", "L2_problem_representation", "L3_ontology", "L4_meta_strategy"]:
                # Map kaizen error types to schema enum
                mapping = {
                    "Information error": "L0_execution",
                    "Execution error": "L0_execution",
                    "Reasoning error": "L1_reasoning",
                    "Assumption error": "L2_problem_representation",
                    "Model/representation error": "L3_ontology",
                    "Meta error": "L4_meta_strategy",
                }
                exp["error_classification"] = mapping.get(ec, "L0_execution")
            elif not ec:
                exp["error_classification"] = "L0_execution"
        
        learning_output = {
            "learning_id": f"KL-{datetime.utcnow().strftime('%Y%m%d')}-{len(kaizen_learning.get('experiences', [])) + 1:03d}",
            "cycle_timestamp": datetime.utcnow().isoformat() + "Z",
            "experiences": experiences,
            "patterns": kaizen_learning.get("patterns", []),
            "reusable_insights": kaizen_learning.get("reusable_insights", []),
            "redefinitions": kaizen_learning.get("redefinitions", []),
            "outcome_score": kaizen_learning.get("outcome_score", 0),
            "confidence": kaizen_learning.get("confidence", 0.8),
            "kaizen_iteration": kaizen_learning.get("kaizen_iteration", 1),
            "period": kaizen_learning.get("period", ""),
        }
        print(f"  Kaizen Synthesis: {len(learning_output['experiences'])} cases, {len(learning_output['patterns'])} patterns")
    else:
        # Fallback to model call
        prompt = specialist.get_prompt("learning")
        learning_context = {
            "accepted_problem": context.stage_outputs.get("saccade", {}),
            "accepted_evidence": context.stage_outputs.get("evidence", {}),
            "accepted_interpretation": context.stage_outputs.get("interpretation", {}),
            "accepted_strategy": context.stage_outputs.get("strategy", {}),
            "accepted_output": context.stage_outputs.get("output", {}),
            "accepted_outcome": context.stage_outputs.get("outcome", {}),
            "accepted_deck": context.stage_outputs.get("deck", {}),
        }
        learning_tools = ["pattern_extraction", "experience_synthesis"]
        schema = specialist.get_schema("learning")
        learning_output = call_model(prompt, learning_context, learning_tools, schema=schema, stage_name="learning", model=specialist.get_model())
    
    schema = specialist.get_schema("learning")
    if schema:
        validate_against_schema(learning_output, schema, "learning")
    
    context.set_stage_output("learning", learning_output)
    
    if runner.chain_builder:
        agent_id = f"{specialist.agent_prefix}.Outcome"  # Learning is recorded by Outcome agent
        runner.chain_builder.record_stage(
            stage=StageName.LEARNING,
            input_data=context.stage_outputs.get("outcome", {}),
            output_data=learning_output,
            agent_id=agent_id,
        )
    
    print(f"  Output: Learning {learning_output.get('learning_id')}")
    return learning_output


async def finalize_causal_chain(runner, dispatch: Dict[str, Any]):
    """Save causal chain to file and PostgreSQL."""
    if not runner.chain_builder:
        return

    causal_chain = runner.chain_builder.finalize(dispatch.get('task_id', 'unknown'))
    task_id = dispatch.get('task_id', 'unknown')
    # Sanitize task_id for filename safety
    safe_task_id = re.sub(r'[^a-zA-Z0-9._-]', '_', task_id)
    # Save to specialist's causal_chains directory (2 parents up from stages/ -> kojiki_core/)
    specialist_dir = Path(__file__).parent.parent / "specialists" / runner.specialist.name
    chain_file = specialist_dir / "causal_chains" / f"{safe_task_id}_causal_chain.json"
    chain_file.parent.mkdir(exist_ok=True)
    chain_file.write_text(causal_chain.to_json())
    print(f"  Causal chain saved: {chain_file}")
    
    if runner.registry and hasattr(runner.registry, 'save_causal_chain'):
        import json
        chain_data = json.loads(causal_chain.to_json())
        runner.registry.save_causal_chain(chain_data)
        print(f"  Causal chain saved to PostgreSQL")


async def adjudicate(runner, dispatch: Dict[str, Any], department: str) -> Dict[str, Any]:
    """Final adjudication output."""
    from datetime import datetime
    
    adjudicated = {
        "problem": runner.context.stage_outputs.get("saccade"),
        "evidence": runner.context.stage_outputs.get("evidence"),
        "interpretation": runner.context.stage_outputs.get("interpretation"),
        "strategy": runner.context.stage_outputs.get("strategy"),
        "output": runner.context.stage_outputs.get("output"),
        "deck": runner.context.stage_outputs.get("deck"),
        "outcome": runner.context.stage_outputs.get("outcome"),
        "learning": runner.context.stage_outputs.get("learning"),
        "adjudication": "ACCEPTED",
        "adjudicator": f"{department.title()}.Brain",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    print("\n=== PIPELINE COMPLETE ===")
    return adjudicated