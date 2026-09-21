#!/usr/bin/env python3
"""
Stage 5: OUTPUT - Intervention Design Only
"""

from typing import Dict, Any
from engine.kojiki_core import ScopedContext, call_model, validate_against_schema, StageName


async def run_output_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute OUTPUT stage."""
    print("\n--- STAGE 5: OUTPUT ---")

    specialist = runner.specialist
    stage_config = specialist.stages.get("output")

    allowed_keys = stage_config.inputs_allowed or ["accepted_strategy"]
    stage_context = context.get_allowed_context(allowed_keys)

    prompt = specialist.get_prompt("output")
    tools = stage_config.tools

    schema = specialist.get_schema("output")
    output = call_model(prompt, stage_context, tools, schema=schema, stage_name="output", model=specialist.get_model())

    if schema:
        validate_against_schema(output, schema, "output")

    context.set_stage_output("output", output)

    if runner.chain_builder:
        agent_id = f"{specialist.agent_prefix}.Output"
        runner.chain_builder.record_stage(
            stage=StageName.OUTPUT,
            input_data=stage_context,
            output_data=output,
            agent_id=agent_id,
        )

    print(f"  Output: Output {output.get('output_id')}")
    return output