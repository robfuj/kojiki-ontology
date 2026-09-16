#!/usr/bin/env python3
"""
Stage 1: SACCADE - A Priori Problem Framing
"""

from typing import Dict, Any, List
from engine.kojiki_core import ScopedContext, call_model, validate_against_schema, StageName
import hashlib


async def run_saccade_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute SACCADE stage."""
    print("\n--- STAGE 1: SACCADE ---")
    
    specialist = runner.specialist
    stage_config = specialist.stages.get("saccade")
    
    # Build scoped context
    allowed_keys = stage_config.inputs_allowed or ["raw_record"]
    stage_context = context.get_allowed_context(allowed_keys)
    stage_context.update(dispatch)
    
    # Load prompt
    prompt = specialist.get_prompt("saccade")
    
    # Get tools
    tools = stage_config.tools
    
    # Call model
    schema = specialist.get_schema("saccade")
    output = call_model(prompt, stage_context, tools, schema=schema, stage_name="saccade")
    
    # Validate
    schema = specialist.get_schema("saccade")
    if schema:
        validate_against_schema(output, schema, "saccade")
    
    # Store
    context.set_stage_output("saccade", output)
    
    # Causal chain
    if runner.chain_builder:
        agent_id = f"{specialist.agent_prefix}.Saccade"
        runner.chain_builder.record_stage(
            stage=StageName.SACCADE,
            input_data=stage_context,
            output_data=output,
            agent_id=agent_id,
        )
    
    print(f"  Output: Problem {output.get('problem_id', output.get('id'))}")
    return output