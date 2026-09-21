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
    output = call_model(prompt, stage_context, tools, schema=schema, stage_name="saccade", model=specialist.get_model())
    
    # Validate
    schema = specialist.get_schema("saccade")
    if schema:
        validate_against_schema(output, schema, "saccade")
    
    # Ensure valid problem_id format (P- + 10+ uppercase alphanumeric)
    import re
    problem_id = output.get("problem_id", "")
    if not re.match(r"^P-[A-Z0-9]{10,}$", problem_id):
        # Generate a valid problem_id from hash
        import hashlib
        hash_input = f"{output.get('goal', '')}{output.get('constraints', [])}{output.get('assumptions', [])}{output.get('unknowns', [])}"
        hash_suffix = hashlib.sha256(hash_input.encode()).hexdigest()[:10].upper()
        output["problem_id"] = f"P-{hash_suffix}"
        print(f"  Fixed problem_id format: {output['problem_id']}")
    
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