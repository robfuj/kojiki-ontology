#!/usr/bin/env python3
"""
Stage 4: STRATEGY - Objective Decision Only
"""

from typing import Dict, Any
from engine.kojiki_core import ScopedContext, call_model, validate_against_schema, StageName


async def run_strategy_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """Execute STRATEGY stage."""
    print("\n--- STAGE 4: STRATEGY ---")

    specialist = runner.specialist
    stage_config = specialist.stages.get("strategy")

    allowed_keys = stage_config.inputs_allowed or ["accepted_interpretation"]
    stage_context = context.get_allowed_context(allowed_keys)
    # Also pass dispatch keys for LLM context (dept_head, task_id, etc.)
    stage_context.update(dispatch)

    prompt = specialist.get_prompt("strategy")
    tools = stage_config.tools

    schema = specialist.get_schema("strategy")
    output = call_model(prompt, stage_context, tools, schema=schema, stage_name="strategy")

    if schema:
        validate_against_schema(output, schema, "strategy")

    context.set_stage_output("strategy", output)

    # Store decision rights in registry
    if output.get("decision_rights") and runner.registry:
        dr = output["decision_rights"]
        if isinstance(dr, dict):
            own_node = dr.get("own")
            if own_node:
                # Pass decision_right as the 'own' value, and the full dict as decision_rights
                runner.registry.update_decision_rights(own_node, dr.get("own", "OWN"), dr)
                print(f"  Decision rights registered for {own_node}")
        elif isinstance(dr, str) and dr != "RECOMMEND":
            runner.registry.update_decision_rights(dr, dr, {"own": dr, "consult": [], "inform": []})
            print(f"  Decision rights registered for {dr}")

    if runner.chain_builder:
        agent_id = f"{specialist.agent_prefix}.Strategy"
        runner.chain_builder.record_stage(
            stage=StageName.STRATEGY,
            input_data=stage_context,
            output_data=output,
            agent_id=agent_id,
        )

    print(f"  Output: Strategy (owner: {output.get('decision_rights', {}).get('own', 'unknown')})")
    return output