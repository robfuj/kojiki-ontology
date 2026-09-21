#!/usr/bin/env python3
"""
Stage 3: INTERPRETATION - Diagnosis Only
"""

from typing import Dict, Any
from engine.kojiki_core import ScopedContext, call_model, validate_against_schema, StageName


async def run_interpretation_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute INTERPRETATION stage."""
    print("\n--- STAGE 3: INTERPRETATION ---")

    specialist = runner.specialist
    stage_config = specialist.stages.get("interpretation")

    allowed_keys = stage_config.inputs_allowed or ["accepted_evidence"]
    stage_context = context.get_allowed_context(allowed_keys)

    prompt = specialist.get_prompt("interpretation")
    tools = stage_config.tools

    schema = specialist.get_schema("interpretation")
    output = call_model(prompt, stage_context, tools, schema=schema, stage_name="interpretation", model=specialist.get_model())

    if schema:
        validate_against_schema(output, schema, "interpretation")

    context.set_stage_output("interpretation", output)

    if runner.chain_builder:
        agent_id = f"{specialist.agent_prefix}.Interpretation"
        runner.chain_builder.record_stage(
            stage=StageName.INTERPRETATION,
            input_data=stage_context,
            output_data=output,
            agent_id=agent_id,
        )

    print(f"  Output: Interpretation {output.get('interpretation_id')}")
    return output