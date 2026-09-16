#!/usr/bin/env python3
"""LLM Post-Training Engineer - SFT/DPO/GRPO/RLVR."""

from ..base import AISubSpecialist


class LLMPostTrainingSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "llm-post-training"
    SUB_AGENT_DESCRIPTION = "Post-training stack (SFT/DPO/GRPO/RLVR), evidence-based experiment gating, checkpoint integrity, failure classification"


specialist = LLMPostTrainingSpecialist()
