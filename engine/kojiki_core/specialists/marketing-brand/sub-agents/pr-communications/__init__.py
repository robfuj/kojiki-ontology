#!/usr/bin/env python3
"""PR Communications - PR, media relations, crisis communications."""

from ..base import MarketingSubSpecialist


class PRCommunicationsSpecialist(MarketingSubSpecialist):
    SUB_AGENT_NAME = "pr-communications"
    SUB_AGENT_DESCRIPTION = "PR, media relations, crisis communications, thought leadership"


specialist = PRCommunicationsSpecialist()
