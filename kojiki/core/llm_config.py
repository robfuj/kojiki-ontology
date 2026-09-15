#!/usr/bin/env python3
"""
LLM Configuration - Centralized settings for LLM calls.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class LLMConfig:
    """Configuration for LLM API calls."""
    
    # API credentials (set via environment variables)
    api_key: str = field(default_factory=lambda: os.environ.get("KOJIKI_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.environ.get("KOJIKI_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    model: str = field(default_factory=lambda: os.environ.get("KOJIKI_LLM_MODEL", "gpt-4o-mini"))
    
    # Generation parameters
    temperature: float = 0.2  # Low for provenance/consistency
    max_tokens: int = 3000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Timeouts
    request_timeout: float = 90.0  # seconds
    connect_timeout: float = 10.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 2.0  # seconds, exponential backoff
    
    # Cost budgets (per call)
    max_cost_per_call_usd: float = 0.50
    max_cost_per_day_usd: float = 50.00
    
    # Rate limiting (requests per minute)
    max_rpm: int = 60
    
    # Caching
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    
    # Prompt quality evaluation
    eval_temperature: float = 0.7  # Higher for eval
    eval_runs: int = 3
    
    def __post_init__(self):
        """Validate configuration."""
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
    
    @property
    def is_configured(self) -> bool:
        """Check if LLM is configured for production use."""
        return bool(self.api_key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return config as dict (without sensitive data)."""
        return {
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "max_cost_per_call_usd": self.max_cost_per_call_usd,
            "max_cost_per_day_usd": self.max_cost_per_day_usd,
            "max_rpm": self.max_rpm,
            "enable_cache": self.enable_cache,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }


# Global config instance
_config: Optional[LLMConfig] = None


def get_llm_config() -> LLMConfig:
    """Get the global LLM configuration."""
    global _config
    if _config is None:
        _config = LLMConfig()
    return _config


def set_llm_config(config: LLMConfig) -> None:
    """Set the global LLM configuration."""
    global _config
    _config = config


# Stage-specific temperature overrides
STAGE_TEMPERATURES = {
    "saccade": 0.1,      # A priori framing - maximum consistency
    "evidence": 0.1,     # Factual retrieval - deterministic
    "interpretation": 0.2,
    "strategy": 0.2,
    "output": 0.3,
    "deck": 0.3,
    "outcome": 0.1,      # Measurement - deterministic
    "learning": 0.2,
    "kaizen": 0.2,
}

# Stage-specific cost budgets (USD)
STAGE_COST_BUDGETS = {
    "saccade": 0.10,
    "evidence": 0.15,
    "interpretation": 0.10,
    "strategy": 0.10,
    "output": 0.05,
    "deck": 0.05,
    "outcome": 0.05,
    "learning": 0.10,
    "kaizen": 0.10,
}


def get_stage_config(stage_name: str) -> Dict[str, Any]:
    """Get stage-specific LLM parameters."""
    config = get_llm_config()
    return {
        "temperature": STAGE_TEMPERATURES.get(stage_name, config.temperature),
        "max_cost_usd": STAGE_COST_BUDGETS.get(stage_name, config.max_cost_per_call_usd),
        "max_tokens": config.max_tokens,
    }


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str = None) -> float:
    """Estimate cost in USD for a completion."""
    model = model or get_llm_config().model
    
    # Rough estimates per 1K tokens (input/output)
    pricing = {
        "gpt-4o": (0.005, 0.015),
        "gpt-4o-mini": (0.00015, 0.0006),
        "gpt-3.5-turbo": (0.0005, 0.0015),
        "groq/compound": (0.0001, 0.0001),
        "groq/compound-mini": (0.0001, 0.0001),
        "openai/gpt-oss-120b": (0.0001, 0.0001),
        "qwen/qwen3.8-27b": (0.0001, 0.0001),
    }
    
    input_price, output_price = pricing.get(model, (0.001, 0.002))
    
    return (prompt_tokens / 1000 * input_price) + (completion_tokens / 1000 * output_price)