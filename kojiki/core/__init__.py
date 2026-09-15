#!/usr/bin/env python3
"""
Kojiki Core - Shared Pipeline Engine

This is the single execution engine used by ALL specialists.
Specialists provide: prompts, tools, validators, adapters, schemas.
Core provides: stage execution, causal chain, decision rights, Kaizen loop.
"""

import json
import sys
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class StageConfig:
    """Configuration for a single pipeline stage."""
    name: str
    prompt: str
    tools: List[Callable] = field(default_factory=list)
    schema: str = ""
    validators: List[Callable] = field(default_factory=list)
    adapter: Optional[Callable] = None
    inputs_allowed: List[str] = field(default_factory=list)
    inputs_forbidden: List[str] = field(default_factory=list)


@dataclass
class StageResult:
    """Result of a stage execution."""
    stage_name: str
    output: Dict[str, Any]
    agent_id: str
    timestamp: str
    model_call_id: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    input_hash: str = ""
    output_hash: str = ""


class ScopedContext:
    """
    Enforces stage-scoped context isolation.
    This is the load-bearing component per thesis §III.3.
    """

    def __init__(self, dispatch: Dict[str, Any]):
        self.dispatch = dispatch
        self.stage_outputs: Dict[str, Dict] = {}
        self.artifacts: Dict[str, Any] = {}

    def get(self, key: str, default=None):
        """Get value from dispatch or previous stage outputs."""
        if key in self.dispatch:
            return self.dispatch[key]
        for stage_output in self.stage_outputs.values():
            if key in stage_output:
                return stage_output[key]
        return default

    def set_stage_output(self, stage: str, output: Dict[str, Any]):
        """Store stage output for later stages."""
        self.stage_outputs[stage] = output

    def get_allowed_context(self, allowed_keys: List[str]) -> Dict[str, Any]:
        """Return only allowed keys for this stage."""
        context = {}
        for key in allowed_keys:
            val = self.get(key)
            if val is not None:
                context[key] = val
        return context

    def get_all_context(self) -> Dict[str, Any]:
        """Return all accumulated context (for debugging)."""
        ctx = dict(self.dispatch)
        ctx.update({f"{k}_output": v for k, v in self.stage_outputs.items()})
        return ctx


class Tool(ABC):
    """Base class for stage tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, context: ScopedContext, params: Dict[str, Any]) -> Any:
        pass


class Validator(ABC):
    """Base class for output validators."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate(self, output: Dict[str, Any], context: ScopedContext) -> List[Dict[str, Any]]:
        """Return list of violations (empty = pass)."""
        pass


class Adapter(ABC):
    """Base class for measurement adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fetch_metrics(self, metrics: List[str], window: Dict[str, str]) -> Dict[str, float]:
        pass


class Specialist(ABC):
    """
    Specialist interface - each department/bot implements this.
    Provides domain-specific: prompts, tools, validators, adapters, schemas.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique specialist identifier (e.g., 'marketing-brand')."""
        pass

    @property
    @abstractmethod
    def agent_prefix(self) -> str:
        """Prefix for agent IDs (e.g., 'marketing' → marketing.Saccade)."""
        pass

    @property
    @abstractmethod
    def decision_rights_node(self) -> str:
        """Node that owns decisions from this specialist."""
        pass

    @property
    @abstractmethod
    def stages(self) -> Dict[str, StageConfig]:
        """Stage configurations. Keys: saccade, evidence, interpretation, strategy, output, deck, outcome, learning."""
        pass

    def get_prompt(self, stage_name: str) -> str:
        """Load prompt file for stage."""
        config = self.stages.get(stage_name)
        if not config or not config.prompt:
            return f"# {stage_name.upper()} Stage\n\nExecute {stage_name} transformation."

        prompt_path = Path(__file__).parent.parent.parent / config.prompt
        if prompt_path.exists():
            return prompt_path.read_text()
        return f"# {stage_name.upper()} Stage\n\nExecute {stage_name} transformation."

    def get_schema(self, stage_name: str) -> Optional[Dict]:
        """Load JSON schema for stage."""
        config = self.stages.get(stage_name)
        if not config or not config.schema:
            return None

        schema_path = Path(__file__).parent.parent.parent / config.schema
        if schema_path.exists():
            return json.loads(schema_path.read_text())
        return None


def load_specialist(specialist_name: str) -> Specialist:
    """Dynamically load a specialist module."""
    spec_path = Path(__file__).parent.parent / "specialists" / specialist_name / "__init__.py"
    if not spec_path.exists():
        raise ValueError(f"Specialist not found: {specialist_name}")

    spec = importlib.util.spec_from_file_location(f"specialist_{specialist_name}", spec_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find Specialist subclass
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, Specialist) and attr is not Specialist:
            return attr()

    raise ValueError(f"No Specialist subclass found in {specialist_name}")


def hash_dict(d: Dict) -> str:
    """Stable hash for dict."""
    return json.dumps(d, sort_keys=True, separators=(',', ':'))


# Utility functions used by stages
def call_model(prompt: str, context: Dict[str, Any], tools: List, schema: Dict = None, stage_name: str = "") -> Dict[str, Any]:
    """
    Call the model with scoped context.
    In production, this calls the actual LLM. Raises if no LLM configured.
    """
    print(f"  [MODEL CALL] Context keys: {list(context.keys())}")
    print(f"  [MODEL CALL] Tools allowed: {[t.name if hasattr(t, 'name') else t for t in tools] if tools else []}")

    # Execute tools if any
    tool_results = {}
    for tool in tools:
        try:
            # Handle both Tool objects and string tool names
            if hasattr(tool, 'name'):
                tool_name = tool.name
                result = tool.execute(context, {})
            else:
                tool_name = tool
                # For string tool names, we can't execute - just log
                result = f"[Tool: {tool} - not implemented]"
            tool_results[tool_name] = result
        except Exception as e:
            print(f"  [TOOL ERROR] {tool}: {e}")

    # Try real LLM call if configured
    # Use the passed stage_name parameter, fallback to context
    effective_stage_name = stage_name
    effective_schema = schema
    if hasattr(context, 'get') and callable(getattr(context, 'get', None)):
        # Check for stage-specific schema
        if not effective_stage_name:
            effective_stage_name = context.get('_stage_name', '')
        if not effective_schema and effective_stage_name and hasattr(context, '_schema'):
            effective_schema = context.get('_schema')

    real_output = _call_real_llm(prompt, context, tools, tool_results, effective_schema, effective_stage_name)
    if real_output is not None:
        return real_output

    # No LLM configured and no real output - fail loud in production
    import os
    if os.environ.get("KOJIKI_TEST_MODE", "").lower() == "true":
        # Test mode: return structured stubs (imported from test fixtures)
        from tests.fixtures.stubs import get_stub
        stub = get_stub(prompt, context)
        if stub is not None:
            return stub
        # Fallback for unmatched prompts in test mode
        print(f"  [STUB WARNING] No stub matched for prompt: {prompt[:100]}")
        return {"error": "No stub available for this prompt in test mode"}

    # Production: fail loud if no LLM configured
    raise RuntimeError(
        "No LLM configured. Set KOJIKI_LLM_API_KEY, KOJIKI_LLM_BASE_URL, and KOJIKI_LLM_MODEL "
        "environment variables to configure a real LLM. "
        "For testing, set KOJIKI_TEST_MODE=true to enable test stubs."
    )


def _call_real_llm(prompt: str, context: Dict[str, Any], tools: List, tool_results: Dict, schema: Dict = None, stage_name: str = "") -> Optional[Dict[str, Any]]:
    """Call real LLM API if configured via environment variables."""
    import os
    import json

    # Check for OpenAI-compatible API configuration
    api_key = os.environ.get("KOJIKI_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("KOJIKI_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("KOJIKI_LLM_MODEL", "gpt-4o-mini")

    if not api_key:
        return None  # No API key configured, use stubs

    # Chief of Staff strategy - skip hardcoded stub, let real LLM handle it
    task_id = str(context.get("task_id", ""))
    if (context.get("dept_head") == "ChiefOfStaff" or "cos-decomp" in task_id or "cos-saccade" in task_id) and stage_name == "strategy":
        # Fall through to real LLM
        pass
    # SACCADE prompts now fixed to return single Problem objects, not arrays
    try:
        import httpx

        # Build system prompt with schema guidance
        schema_guidance = ""
        if schema:
            schema_guidance = f"\n\nRESPONSE MUST BE VALID JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\nReturn ONLY the JSON object, no markdown, no extra text, no explanation."

        # Build messages
        system_prompt = prompt + schema_guidance + "\n\nCRITICAL: Your entire response must be a single valid JSON object. Do not include any explanation, reasoning, or markdown code fences. Start with { and end with }."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(context, default=str)[:6000]}
        ]

        # Build tool definitions for function calling
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

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 3000,
        }

        if tool_defs:
            payload["tools"] = tool_defs
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=90.0) as client:
            response = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        message = choice["message"]

        # Handle tool calls
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                # Execute the tool
                for tool in tools:
                    if hasattr(tool, 'name') and tool.name == fn_name:
                        tool_results[fn_name] = tool.execute(context, fn_args)
                        break

        # Parse response as JSON
        content = message.get("content", "{}")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Try to find the first valid JSON object in the response
            for i in range(len(content)):
                if content[i] == '{':
                    for j in range(i+1, len(content)+1):
                        if content[j-1] == '}':
                            candidate = content[i:j]
                            try:
                                return json.loads(candidate)
                            except json.JSONDecodeError:
                                continue
            print(f"  [LLM PARSE ERROR] Could not parse JSON from: {content[:200]}")
            return None

    except Exception as e:
        print(f"  [LLM ERROR] {e}")
        return None


def validate_against_schema(output: Dict[str, Any], schema: Dict, stage_name: str) -> bool:
    """Validate output against JSON schema."""
    try:
        import jsonschema
        jsonschema.validate(instance=output, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"  [SCHEMA VALIDATION FAILED] {stage_name}: {e.message}")
        return False
    except ImportError:
        print(f"  [SCHEMA VALIDATION SKIPPED] jsonschema not installed")
        return True


# Import StageName from causal_chain (avoid circular import)
CAUSAL_CHAIN_PATH = Path(__file__).parent.parent.parent / "00-kojiki-ontology" / "synapsis" / "causal_chain.py"
if CAUSAL_CHAIN_PATH.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("causal_chain", CAUSAL_CHAIN_PATH)
    causal_chain_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal_chain_module)
    StageName = causal_chain_module.StageName
    CausalChainRunner = causal_chain_module.CausalChainRunner
else:
    StageName = None
    CausalChainRunner = None