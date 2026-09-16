#!/usr/bin/env python3
"""
Kojiki Core Stage Base - Unified stage execution patterns.
Eliminates duplication across all stage implementations.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from engine.kojiki_core.types import ScopedContext, StageConfig, Specialist
from engine.kojiki_core.utils import (
    build_stage_context,
    run_stage_async,
    log_model_call,
    log_stage_start,
    log_stage_output,
    validate_required_fields,
    validate_schema,
    get_test_stub,
    is_test_mode,
    extract_task_id,
    hash_dict,
)


class StageRunner:
    """Base class for all pipeline stages - eliminates duplication."""

    def __init__(self, stage_name: str, specialist: Specialist, dispatch: Dict[str, Any],
                 context: ScopedContext, department: str):
        self.stage_name = stage_name
        self.specialist = specialist
        self.dispatch = dispatch
        self.context = context
        self.department = department
        self.stage_config = specialist.stages.get(stage_name)

    def execute(self) -> Dict[str, Any]:
        """Execute this stage - sync wrapper for async execution."""
        return asyncio.run(self._execute_async())

    async def _execute_async(self) -> Dict[str, Any]:
        """Execute stage asynchronously."""
        log_stage_start(self.stage_name, self.specialist.name)

        if not self.stage_config or not self.stage_config.enabled:
            print(f"  Stage {self.stage_name} disabled, skipping")
            return {"skipped": True, "reason": "Stage disabled"}

        # Build scoped context
        allowed = self.stage_config.inputs_allowed or []
        forbidden = self.stage_config.inputs_forbidden or []
        stage_context = build_stage_context(self.context, allowed, forbidden)
        stage_context.update(self.dispatch)  # Add dispatch keys

        # Get prompt
        prompt = self.specialist.get_prompt(self.stage_name)

        # Get tools
        tools = self.stage_config.tools or []

        # Get schema
        schema = self.specialist.get_schema(self.stage_name)

        # Call model
        output = await self._call_model(prompt, stage_context, tools, schema)

        # Validate if schema exists
        if schema:
            from kojiki.core.utils import validate_schema
            validate_schema(output, schema, self.stage_name)

        # Store in context
        self.context.set_stage_output(self.stage_name, output)

        log_stage_output(self.stage_name, output)
        return output

    async def _call_model(self, prompt: str, context: Dict[str, Any],
                          tools: List, schema: Optional[Dict]) -> Dict[str, Any]:
        """Call the model with proper context and schema."""
        # Extract task_id
        task_id = context.get('task_id', '') if isinstance(context, dict) else ''
        if not task_id:
            task_id = self.dispatch.get('task_id', '')

        # Prepare stage-specific context for prompt
        effective_stage_name = self.stage_name
        effective_schema = schema

        # Handle ScopedContext
        if hasattr(context, 'dispatch'):
            pass  # Already handled

        # Call real LLM if configured
        real_output = await self._call_real_llm(prompt, context, tools, schema, self.stage_name, task_id)
        if real_output is not None:
            return real_output

        # Test mode - use stubs
        if is_test_mode():
            return get_test_stub(self.stage_name, context)

        # Production: fail loud
        raise RuntimeError(
            "No LLM configured. Set KOJIKI_LLM_API_KEY, KOJIKI_LLM_BASE_URL, and KOJIKI_LLM_MODEL "
            "environment variables to configure a real LLM. "
            "For testing, set KOJIKI_TEST_MODE=true to enable test stubs."
        )

    async def _call_real_llm(self, prompt: str, context: Dict[str, Any], tools: List,
                             schema: Optional[Dict], stage_name: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Call real LLM API if configured via environment variables."""
        import os
        import httpx

        api_key = os.environ.get("KOJIKI_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("KOJIKI_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("KOJIKI_LLM_MODEL", "anthropic/claude-3-haiku:beta")

        if not api_key:
            return None

        try:
            # Build messages
            messages = self._build_messages(prompt, schema, context, stage_name)

            # Build tool definitions
            tool_defs = self._build_tool_defs(tools)

            payload = {
                "model": os.environ.get("KOJIKI_LLM_MODEL", "anthropic/claude-3-haiku:beta"),
                "messages": messages,
                "temperature": float(os.environ.get("KOJIKI_LLM_TEMPERATURE", "0.0")),
                "max_tokens": int(os.environ.get("KOJIKI_LLM_MAX_TOKENS", "4000")),
                "stream": False,
                "response_format": {"type": "json_object"},
            }

            if tool_defs:
                payload["tools"] = tool_defs
                payload["tool_choice"] = "auto"

            headers = {
                "Authorization": f"Bearer {os.environ.get('KOJIKI_LLM_API_KEY')}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{os.environ.get('KOJIKI_LLM_BASE_URL', 'https://openrouter.ai/api/v1')}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            return self._parse_response(data, tools, context)

        except Exception as e:
            print(f"  [LLM ERROR] {e}")
            return None

    def _build_messages(self, prompt: str, schema: Optional[Dict], context: Dict, stage_name: str) -> List[Dict]:
        """Build messages for LLM API call."""
        # Build system prompt with schema guidance
        schema_guidance = ""
        if schema:
            import json
            schema_guidance = f"\n\nRESPONSE MUST BE VALID JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\nReturn ONLY the JSON object, no markdown, no extra text, no explanation."

        system_prompt = prompt + schema_guidance + "\n\nCRITICAL: Your entire response must be a single valid JSON object. Do not include any explanation, reasoning, or markdown code fences. Start with { and end with }. NO PREAMBLE, NO ACKNOWLEDGMENT, NO CONVERSATION."

        # Build user message with context
        user_message = self._build_user_message(stage_name, context)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

    def _build_user_message(self, stage_name: str, context: Dict[str, Any]) -> str:
        """Build stage-specific user message with actual context."""
        if stage_name == "saccade":
            raw_record = context.get('raw_record', '')
            return f"RAW GOAL TO FRAME: {raw_record}\n\nGenerate the Problem JSON object for the SACCADE (A Priori Problem Framing) stage. Return ONLY the JSON with fields: problem_id, goal, constraints, assumptions, unknowns."

        elif stage_name == "evidence":
            problem = context.get('accepted_problem', {})
            problem_summary = f"Goal: {problem.get('goal', 'N/A')}\nConstraints: {problem.get('constraints', [])}\nAssumptions: {problem.get('assumptions', [])}\nUnknowns: {problem.get('unknowns', [])}"
            return f"PROBLEM TO GATHER EVIDENCE FOR:\n{problem_summary}\n\nGenerate the Evidence JSON object with fields: evidence_id, findings (array of source/finding/confidence/citations), evidence_gaps, collection_plan. Base findings on THIS specific problem."

        elif stage_name == "interpretation":
            problem = context.get('accepted_problem', {})
            evidence = context.get('accepted_evidence', context.get('evidence', {}))
            problem_summary = f"Goal: {problem.get('goal', 'N/A')}\nConstraints: {problem.get('constraints', [])}\nAssumptions: {problem.get('assumptions', [])}\nUnknowns: {problem.get('unknowns', [])}"
            evidence_summary = f"Findings: {evidence.get('findings', [])}\nEvidence Gaps: {evidence.get('evidence_gaps', [])}"
            return f"PROBLEM TO INTERPRET:\n{problem_summary}\n\nEVIDENCE TO SYNTHESIZE:\n{evidence_summary}\n\nGenerate the Interpretation JSON object with fields: interpretation_id, synthesis, confidence, key_insights, contradictions, evidence_gaps, department_requirements. Base output on THIS specific problem and evidence."

        elif stage_name == "strategy":
            problem = context.get('accepted_problem', {})
            evidence = context.get('accepted_evidence', context.get('evidence', {}))
            problem_summary = f"Goal: {problem.get('goal', 'N/A')}\nConstraints: {problem.get('constraints', [])}\nAssumptions: {problem.get('assumptions', [])}\nUnknowns: {problem.get('unknowns', [])}"
            evidence_summary = f"Findings: {evidence.get('findings', [])}"
            return f"PROBLEM TO DECOMPOSE:\n{problem_summary}\n\nEVIDENCE:\n{evidence_summary}\n\nGenerate the Strategy JSON object with fields: strategy_id, interpretation_ref, objective, rationale, timeline, success_criteria, escalation_conditions, actions (array of department objectives with owner, description, dependencies, success_criteria). Base actions on THIS specific problem."

        elif stage_name == "output":
            return "Generate the Output JSON object with fields: output_id, actions (array of specific actions with owner, description, due_date, dependencies), execution_plan. Return ONLY the JSON object."

        elif stage_name == "delegation":
            return "Generate the Delegation JSON object with fields: delegation_id, tasks (array of tasks with sub_agent, description, dependencies, priority), synthesis_plan. Return ONLY the JSON object."

        elif stage_name == "handoff":
            return "Generate the Handoff JSON object with fields: handoff_id, target_department, payload, trigger, schema_ref. Return ONLY the JSON object."

        elif stage_name == "mycelium":
            return "Generate the Mycelium signal JSON object with fields: signal_id, origin_kr, event, signal_kind, subgraph, diagnosed_cause, diagnosed_cause_category. Return ONLY the JSON object."

        elif stage_name == "deck":
            return "Generate the Deck JSON object with fields: deck_id, slides (array of slide objects), theme, format. Return ONLY the JSON object."

        elif stage_name == "outcome":
            return "Generate the Outcome JSON object with fields: outcome_id, evaluations (array of metric/actual/target/operator/weight), adjudication. Return ONLY the JSON object."

        elif stage_name == "learning":
            return "Generate the Learning JSON object with fields: learning_id, pattern, rule, confidence, applies_to. Return ONLY the JSON object."

        return f"Execute {stage_name} transformation. Return valid JSON only."

    def _build_tool_defs(self, tools: List) -> List[Dict]:
        """Build OpenAI-compatible tool definitions."""
        tool_defs = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_defs.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": getattr(tool, 'description', f"Execute {tool.name}"),
                        "parameters": {"type": "object", "properties": {}}
                    }
                })
        return tool_defs

    async def _parse_response(self, data: Dict, tools: List, context: Dict) -> Dict:
        """Parse and validate LLM response."""
        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content", "")

        # Handle tool calls
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                for tool in tools:
                    if hasattr(tool, 'name') and tool.name == fn_name:
                        # Execute tool - would need context
                        pass

        # Parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract from code blocks
            import re
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Try to find first valid JSON object
            for i in range(len(content)):
                if content[i] == '{':
                    for j in range(i+1, len(content)+1):
                        if content[j-1] == '}':
                            candidate = content[i:j]
                            try:
                                return json.loads(candidate)
                            except json.JSONDecodeError:
                                continue
            raise ValueError(f"Could not parse JSON from LLM response: {content[:200]}")


def call_model(prompt: str, context: Dict[str, Any], tools: List,
               schema: Dict = None, stage_name: str = "") -> Dict[str, Any]:
    """Sync wrapper for model calling - used by stages."""
    runner = None  # Would need a proper runner instance
    # This is a compatibility wrapper - stages should use StageRunner directly
    from engine.kojiki_core import call_model as core_call_model
    return core_call_model(prompt, context, tools, schema, stage_name)


def validate_against_schema(output: Dict[str, Any], schema: Dict, stage_name: str) -> bool:
    """Validate output against JSON schema."""
    from kojiki.core.utils import validate_output_schema
    return validate_output_schema(output, schema, stage_name)