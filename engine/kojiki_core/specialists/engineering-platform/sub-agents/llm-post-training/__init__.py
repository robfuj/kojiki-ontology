#!/usr/bin/env python3
"""LLM Post-Training Engineer - SFT/DPO/GRPO/RLVR."""

from ..base import EngineeringSubSpecialist


class LLMPostTrainingSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "llm-post-training"
    SUB_AGENT_DESCRIPTION = "Post-training stack (SFT/DPO/GRPO/RLVR), experiment gating, checkpoint integrity"


specialist = LLMPostTrainingSpecialist()
