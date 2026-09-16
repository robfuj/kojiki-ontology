#!/usr/bin/env python3
"""Prompt Engineer - LLM prompt design & optimization."""

from ..base import AISubSpecialist


class PromptEngineerSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "prompt-engineer"
    SUB_AGENT_DESCRIPTION = "LLM prompt design & optimization, turning vague instructions into reliable AI behaviors"


specialist = PromptEngineerSpecialist()
