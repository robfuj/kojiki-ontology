#!/usr/bin/env python3
"""
Kojiki Core Types - Unified type definitions for the entire pipeline.
Single source of truth for all dataclasses and type definitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Set
from abc import ABC, abstractmethod
from pathlib import Path


# ============================================================================
# Stage Configuration & Results
# ============================================================================

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
    enabled: bool = True


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


# ============================================================================
# Context Management
# ============================================================================

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


# ============================================================================
# Tool / Validator / Adapter Interfaces
# ============================================================================

class Tool(ABC):
    """Base class for stage tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, context: "ScopedContext", params: Dict[str, Any]) -> Any:
        pass


class Validator(ABC):
    """Base class for output validators."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate(self, output: Dict[str, Any], context: "ScopedContext") -> List[Dict[str, Any]]:
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


# ============================================================================
# Specialist Interface
# ============================================================================

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
    def stages(self) -> Dict[str, "StageConfig"]:
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
        import json
        config = self.stages.get(stage_name)
        if not config or not config.schema:
            return None

        # Schema path is already absolute from specialist config
        schema_path = Path(config.schema)
        if schema_path.exists():
            return json.loads(schema_path.read_text())
        return None


# ============================================================================
# Utility Functions
# ============================================================================

def hash_dict(d: Dict) -> str:
    """Stable hash for dict."""
    import json
    return json.dumps(d, sort_keys=True, separators=(',', ':'))


def load_specialist(specialist_name: str):
    """Dynamically load a specialist module."""
    import importlib.util
    spec_path = Path(__file__).parent.parent / "specialists" / specialist_name / "__init__.py"
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
# Stage Names (avoid circular import)
# ============================================================================

class StageName:
    """Stage names for the SYNAPSIS pipeline."""
    SACCADE = "saccade"
    EVIDENCE = "evidence"
    INTERPRETATION = "interpretation"
    STRATEGY = "strategy"
    OUTPUT = "output"
    DELEGATION = "delegation"
    HANDOFF = "handoff"
    MYCELIUM = "mycelium"
    DECK = "deck"
    OUTCOME = "outcome"
    LEARNING = "learning"


STAGE_NAMES = [
    "saccade", "evidence", "interpretation", "strategy",
    "output", "delegation", "handoff", "mycelium",
    "deck", "outcome", "learning"
]

STAGE_ORDER = {name: i for i, name in enumerate(STAGE_NAMES)}


class CausalChainRunner:
    """Placeholder for causal chain runner - actual implementation in causal_chain module."""
    def __init__(self, task_id: str = "", key_manager=None):
        self.task_id = task_id
        self.key_manager = key_manager
    
    def record_stage(self, stage, input_data, output_data, agent_id):
        pass
    
    def finalize(self, task_id: str):
        """Finalize and return a mock causal chain."""
        from dataclasses import dataclass
        from typing import Optional
        
        @dataclass
        class MockCausalChain:
            task_id: str
            stages: list
            signatures: dict
            
            def to_json(self):
                import json
                return json.dumps({
                    "task_id": self.task_id,
                    "stages": self.stages,
                    "signatures": self.signatures
                })
        
        return MockCausalChain(task_id=task_id, stages=[], signatures={})