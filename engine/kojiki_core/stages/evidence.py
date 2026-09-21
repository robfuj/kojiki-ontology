#!/usr/bin/env python3
"""
Stage 2: EVIDENCE - Verified Extracts Only
"""

from typing import Dict, Any
from engine.kojiki_core import ScopedContext, call_model, validate_against_schema, StageName


async def run_evidence_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute EVIDENCE stage."""
    print("\n--- STAGE 2: EVIDENCE ---")

    specialist = runner.specialist
    stage_config = specialist.stages.get("evidence")

    allowed_keys = stage_config.inputs_allowed or ["raw_source", "prior_accepted_evidence"]
    stage_context = context.get_allowed_context(allowed_keys)
    stage_context.update(dispatch)

    prompt = specialist.get_prompt("evidence")
    tools = stage_config.tools

    schema = specialist.get_schema("evidence")
    output = call_model(prompt, stage_context, tools, schema=schema, stage_name="evidence", model=specialist.get_model())

    if schema:
        validate_against_schema(output, schema, "evidence")

    context.set_stage_output("evidence", output)
    dispatch["full_evidence"] = output

    if runner.chain_builder:
        agent_id = f"{specialist.agent_prefix}.Evidence"
        runner.chain_builder.record_stage(
            stage=StageName.EVIDENCE,
            input_data=stage_context,
            output_data=output,
            agent_id=agent_id,
        )

    print(f"  Output: {len(output.get('findings', []))} findings")
    return output