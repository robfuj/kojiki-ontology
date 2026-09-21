#!/usr/bin/env python3
"""
Kojiki Core Utilities - Shared utilities across the pipeline.
Consolidates common patterns to avoid duplication.
"""

import json
import os
import hashlib
import re
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Any
from datetime import datetime


# ============================================================================
# JSON & Serialization
# ============================================================================

def stable_json_dumps(obj: Any) -> str:
    """Stable JSON serialization for hashing/comparison."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def stable_hash(obj: Any) -> str:
    """Stable hash for any JSON-serializable object."""
    return hashlib.sha256(stable_json_dumps(obj).encode()).hexdigest()


def short_hash(obj: Any, length: int = 16) -> str:
    """Short stable hash for IDs."""
    return stable_hash(obj)[:length]


# ============================================================================
# Dynamic Module Loading
# ============================================================================

def load_module_from_path(module_name: str, file_path: Path):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load spec from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_subclass(module, base_class, exclude_base=True):
    """Find a subclass of base_class in a module."""
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, base_class):
            if exclude_base and attr is base_class:
                continue
            return attr
    return None


# ============================================================================
# Prompt & Schema Loading
# ============================================================================

def load_prompt(prompt_path: str, base_dir: Optional[Path] = None) -> str:
    """Load prompt from file with fallback."""
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent
    prompt_file = base_dir / prompt_path
    if prompt_file.exists():
        return prompt_file.read_text()
    return "# Stage\n\nExecute transformation."


def load_schema(schema_path: str, base_dir: Optional[Path] = None) -> Optional[Dict]:
    """Load JSON schema from file."""
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent
    schema_file = base_dir / schema_path
    if schema_file.exists():
        import json
        return json.loads(schema_file.read_text())
    return None


# ============================================================================
# Schema Validation
# ============================================================================

def validate_schema(output: Dict[str, Any], schema: Dict, stage_name: str = "") -> bool:
    """Validate output against JSON schema."""
    try:
        import jsonschema
        jsonschema.validate(instance=output, schema=schema)
        return True
    except ImportError:
        return True  # Skip if jsonschema not installed
    except jsonschema.ValidationError as e:
        print(f"  [SCHEMA VALIDATION FAILED] {stage_name}: {e.message}")
        return False


# ============================================================================
# Specialist Loading
# ============================================================================

def load_specialist(specialist_name: str):
    """Dynamically load a specialist module."""
    import importlib.util
    from pathlib import Path
    from ..types import Specialist
    # Find project root: utils -> kojiki_core -> engine
    project_root = Path(__file__).parent.parent.parent
    spec_path = project_root / "kojiki_core" / "specialists" / specialist_name / "__init__.py"
    if not spec_path.exists():
        raise ValueError(f"Specialist not found: {specialist_name}")

    spec = importlib.util.spec_from_file_location(f"specialist_{specialist_name}", spec_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load spec for {specialist_name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find Specialist subclass
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, Specialist) and attr is not Specialist:
            return attr()

    raise ValueError(f"No Specialist subclass found in {specialist_name}")


# ============================================================================
# LLM Configuration
# ============================================================================

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration from environment variables."""
    return {
        "provider": os.environ.get("KOJIKI_LLM_PROVIDER", "openrouter"),
        "base_url": os.environ.get("KOJIKI_LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        "api_key": os.environ.get("KOJIKI_LLM_API_KEY", ""),
        "model": os.environ.get("KOJIKI_LLM_MODEL", "anthropic/claude-3-haiku:beta"),
        "temperature": float(os.environ.get("KOJIKI_LLM_TEMPERATURE", "0.0")),
        "max_tokens": int(os.environ.get("KOJIKI_LLM_MAX_TOKENS", "4000")),
    }


def is_test_mode() -> bool:
    """Check if running in test mode."""
    return os.environ.get("KOJIKI_TEST_MODE", "").lower() == "true"


def build_stage_context(context: Any, allowed_keys: List[str], forbidden_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Build context for a stage with allowed/forbidden keys."""
    forbidden = set(forbidden_keys or [])
    result = {}
    for key in allowed_keys:
        if key not in forbidden:
            val = context.get(key)
            if val is not None:
                result[key] = val
    return result


def run_stage_async(stage_func, runner, dispatch, context, department):
    """Run an async stage function with proper event loop handling."""
    import asyncio
    import concurrent.futures
    try:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, stage_func(runner, dispatch, context, department))
            return future.result(timeout=120)
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(stage_func(runner, dispatch, context, department))


# ============================================================================
# Model Calling (Compatibility Wrapper)
# ============================================================================

def call_model(prompt: str, context: Dict[str, Any], tools: List, schema: Dict = None, stage_name: str = "", model: str = None) -> Dict[str, Any]:
    """Call the model with scoped context. In production, calls the actual LLM."""
    # For test mode, return stubs
    if is_test_mode():
        return get_test_stub(stage_name, context)
    
    # Production: call real LLM
    import asyncio
    import os
    import httpx
    import json
    import re
    
    # Get LLM config from environment, with optional model override
    api_key = os.environ.get("KOJIKI_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("KOJIKI_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = model or os.environ.get("KOJIKI_LLM_MODEL", "anthropic/claude-3-haiku:beta")
    temperature = float(os.environ.get("KOJIKI_LLM_TEMPERATURE", "0.0"))
    max_tokens = int(os.environ.get("KOJIKI_LLM_MAX_TOKENS", "4000"))
    
    if not api_key:
        return {"error": "No LLM configured. Set KOJIKI_LLM_API_KEY, KOJIKI_LLM_BASE_URL, and KOJIKI_LLM_MODEL environment variables."}
    
    # Build messages with schema guidance
    schema_guidance = ""
    if schema:
        schema_guidance = "\n\nRESPONSE MUST BE VALID JSON matching this schema:\n" + json.dumps(schema, indent=2) + "\n\nReturn ONLY the JSON object, no markdown, no extra text, no explanation."

    system_prompt = prompt + schema_guidance + "\n\nCRITICAL: Your entire response must be a single valid JSON object. Do not include any explanation, reasoning, or markdown code fences. Start with { and end with }. NO PREAMBLE, NO ACKNOWLEDGMENT, NO CONVERSATION.\n\nEXAMPLE CORRECT OUTPUT:\n{\"key\": \"value\", \"array\": [\"item1\", \"item2\"]}\n\nEXAMPLE INCORRECT OUTPUT:\nHere is the JSON: {\"key\": \"value\"}\n\nIf you output anything other than a single JSON object, the system will fail."
    
    # Build user message with context
    user_message = ""
    if isinstance(context, dict):
        if stage_name == "orientation_research":
            user_message = "Research the field for this goal using live web search.\n\nRAW GOAL: " + context.get('raw_goal', '') + "\n\nCLARIFIED CONTEXT:\n" + context.get('research_context', '') + "\n\nSearch for and synthesize current information on FOUR areas. Return JSON with:\n1. market_scan: Market size, growth direction, forces moving it, key players\n2. competitive_landscape: Who competes, how positioned, where gaps are\n3. regulatory_considerations: Compliance exposure, naming regimes that apply\n4. key_risks: Top 3-5 risks most likely to derail this goal\n5. sources: URLs cited inline as [n] and listed at end\n\nBe specific and current; prefer named companies, figures, regulations over generalities.\nIf web search unavailable, reason from knowledge and leave sources empty."
        elif stage_name == "follow_up_generation":
            user_message = "Generate 3-4 specific follow-up questions based on this research.\n\nRAW GOAL: " + context.get('raw_goal', '') + "\n\nRESEARCH FINDINGS:\nMarket: " + context.get('market_scan', '')[:500] + "\nCompetition: " + context.get('competitive_landscape', '')[:500] + "\nRegulation: " + context.get('regulatory_considerations', '')[:500] + "\nRisks: " + str(context.get('key_risks', [])) + "\n\nGenerate questions that:\n1. Are SPECIFIC to this goal (not generic)\n2. Reference concrete research findings\n3. Resolve ambiguities that would change the plan\n4. Have clear \"why\" tied to research\n\nReturn JSON array of: {\"id\": \"\", \"prompt\": \"\", \"why\": \"\", \"research_basis\": \"\", \"category\": \"\"}"
        elif stage_name == "goal_synthesis":
            user_message = "Synthesize a precise, actionable goal statement.\n\nRAW GOAL: " + context.get('raw_goal', '') + "\n\nCLARIFYING ANSWERS:\n" + json.dumps([{"q": a.question, "a": a.user_response[:200]} for a in context.get('clarifying_answers', [])], indent=2) + "\n\nRESEARCH KEY FINDINGS:\n- Market: " + context.get('market_scan', '')[:200] + "\n- Competition: " + context.get('competitive_landscape', '')[:200] + "\n- Regulation: " + context.get('regulatory_considerations', '')[:200] + "\n- Risks: " + str(context.get('key_risks', [])) + "\n\nFOLLOW-UP ANSWERS:\n" + json.dumps([{"q": a.question, "a": a.user_response[:200]} for a in context.get('follow_up_answers', [])], indent=2) + "\n\nWrite a refined goal that is:\n1. Specific and measurable\n2. Includes constraints and success criteria\n3. Identifies key stakeholders\n4. Notes boundaries/out-of-scope\n5. One paragraph, professional tone"
        elif stage_name == "orientation_simulation":
            user_message = "Simulate a realistic user responding to this question.\n\nGOAL: " + context.get('raw_goal', '') + "\nQUESTION: " + context.get('question', '') + "\n\nGenerate a realistic, specific response (2-4 sentences) with concrete details."
        elif stage_name == "think_aloud":
            user_message = 'User answered: "' + context.get('user_response', '') + '"\nQuestion: ' + context.get('question', '') + "\n\nGenerate brief think-aloud (1-2 sentences)."
        else:
            user_message = "Execute " + stage_name + " transformation. Return valid JSON only."
    else:
        user_message = "Execute " + stage_name + " transformation. Return valid JSON only."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
        "response_format": {"type": "json_object"},
    }
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    
    try:
        async def _call():
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    base_url + "/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            # We're in a running loop, need to create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _call())
                data = future.result(timeout=120)
        else:
            data = asyncio.run(_call())
        
        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content", "")
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            for i in range(len(content)):
                if content[i] == '{':
                    for j in range(i+1, len(content)+1):
                        if content[j-1] == '}':
                            candidate = content[i:j]
                            try:
                                return json.loads(candidate)
                            except json.JSONDecodeError:
                                continue
            raise ValueError("Could not parse JSON from LLM response: " + content[:200])
    except Exception as e:
        print("  [LLM ERROR] " + str(e))
        return {"error": "LLM call failed: " + str(e)}

# ============================================================================
# Test Stubs (imported from test fixtures in test mode)
# ============================================================================

def get_test_stub(stage_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Get test stub for a stage."""
    if is_test_mode():
        try:
            from tests.fixtures.test_stubs import get_test_stub as _get_test_stub
            return _get_test_stub(stage_name, context)
        except ImportError:
            pass
    return {"error": f"No stub for stage: {stage_name}"}


# ============================================================================
# Dispatch Helpers
# ============================================================================

def create_dispatch(task_id: str, raw_record: str = "", **kwargs) -> Dict[str, Any]:
    """Create a standard dispatch dictionary."""
    return {
        "task_id": task_id,
        "raw_record": raw_record,
        "raw_source": kwargs.get("raw_source", {}),
        "prior_accepted_evidence": kwargs.get("prior_accepted_evidence", []),
        **kwargs
    }


def extract_task_id(context: Any) -> str:
    """Extract task_id from various context types."""
    if hasattr(context, 'dispatch') and isinstance(context.dispatch, dict):
        return str(context.dispatch.get('task_id', ''))
    elif isinstance(context, dict):
        return str(context.get('task_id', ''))
    elif hasattr(context, 'get'):
        return str(context.get('task_id', ''))
    return ""


# ============================================================================
# File Path Helpers
# ============================================================================

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_specialists_dir() -> Path:
    """Get the specialists directory."""
    return get_project_root() / "kojiki" / "specialists"


def get_schemas_dir() -> Path:
    """Get the shared schemas directory."""
    return get_project_root() / "shared" / "schemas"


# ============================================================================
# Logging Helpers
# ============================================================================

def log_model_call(stage_name: str, context_keys: List[str], tools: List[str], task_id: str = ""):
    """Log model call for debugging."""
    print(f"  [MODEL CALL] Stage: {stage_name} | Context keys: {context_keys} | Tools: {tools} | task_id: {task_id}")


def log_stage_start(stage_name: str, specialist_name: str = ""):
    """Log stage start."""
    prefix = f" [{specialist_name}]" if specialist_name else ""
    print(f"\n--- STAGE: {stage_name.upper()}{prefix} ---")


def log_stage_output(stage_name: str, output: Dict[str, Any]):
    """Log stage output summary."""
    keys = list(output.keys()) if isinstance(output, dict) else []
    print(f"  Output keys: {keys}")


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_required_fields(obj: Dict[str, Any], required: List[str], context: str = "") -> List[str]:
    """Validate required fields in dict. Returns list of missing fields."""
    missing = [field for field in required if field not in obj or obj[field] is None]
    if missing:
        print(f"  [VALIDATION ERROR] {context}: Missing required fields: {missing}")
    return missing


def validate_enum_field(obj: Dict[str, Any], field: str, valid_values: List[str], context: str = "") -> bool:
    """Validate field value against enum."""
    val = obj.get(field)
    if val is not None and val not in valid_values:
        print(f"  [VALIDATION ERROR] {context}: {field} must be one of {valid_values}, got {val}")
        return False
    return True


# ============================================================================
# Retry Helpers
# ============================================================================

def with_retry(func, max_retries: int = 3, backoff: float = 1.0, exceptions: tuple = (Exception,)):
    """Execute function with retry logic."""
    import time
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
    if last_exception:
        raise last_exception


# ============================================================================
# Hash Utilities
# ============================================================================

def hash_dict(d: Dict) -> str:
    """Stable hash for dict."""
    return json.dumps(d, sort_keys=True, separators=(',', ':'))


# ============================================================================
# Export
# ============================================================================

__all__ = [
    # JSON/Serialization
    "stable_json_dumps", "stable_hash", "short_hash",
    # Module Loading
    "load_module_from_path", "find_subclass",
    # Prompt/Schema
    "load_prompt", "load_schema",
    # Schema Validation
    "validate_schema",
    # Specialist Loading
    "load_specialist",
    # LLM Config
    "get_llm_config", "is_test_mode",
    # Model Calling
    "call_model",
    # Stage Helpers
    "build_stage_context", "run_stage_async",
    # Test Stubs
    "get_test_stub",
    # Dispatch
    "create_dispatch", "extract_task_id",
    # Paths
    "get_project_root", "get_specialists_dir", "get_schemas_dir",
    # Logging
    "log_model_call", "log_stage_start", "log_stage_output",
    # Validation
    "validate_required_fields", "validate_enum_field",
    # Retry
    "with_retry",
    # Hash
    "hash_dict",
]