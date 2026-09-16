#!/usr/bin/env python3
"""
Kojiki Core - Shared Pipeline Engine

This is the single execution engine used by ALL specialists.
Specialists provide: prompts, tools, validators, adapters, schemas.
Core provides: stage execution, causal chain, decision rights, Kaizen loop.
"""

from .types import (
    StageConfig,
    StageResult,
    ScopedContext,
    Tool,
    Validator,
    Adapter,
    Specialist,
    STAGE_NAMES,
    STAGE_ORDER,
    StageName,
    CausalChainRunner,
)
from .utils import (
    load_specialist,
    call_model,
    validate_schema as validate_against_schema,
    hash_dict,
    get_llm_config,
    is_test_mode,
    get_test_stub,
)

__all__ = [
    # Types
    "StageConfig",
    "StageResult", 
    "ScopedContext",
    "Tool",
    "Validator",
    "Adapter",
    "Specialist",
    "STAGE_NAMES",
    "STAGE_ORDER",
    # Utils
    "load_specialist",
    "call_model",
    "validate_schema",
    "hash_dict",
    "get_llm_config",
    "is_test_mode",
    "get_test_stub",
]