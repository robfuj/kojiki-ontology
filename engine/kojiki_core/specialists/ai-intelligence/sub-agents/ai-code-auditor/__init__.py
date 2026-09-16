#!/usr/bin/env python3
"""AI-Generated Code Security Auditor - Security review of AI/vibe-coded apps."""

from ..base import AISubSpecialist


class AICodeAuditorSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "ai-code-auditor"
    SUB_AGENT_DESCRIPTION = "Security review of AI/vibe-coded apps, hardcoded secrets, broken RLS, prompt-injection sinks"


specialist = AICodeAuditorSpecialist()
