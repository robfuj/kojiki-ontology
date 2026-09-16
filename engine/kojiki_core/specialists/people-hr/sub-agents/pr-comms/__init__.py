#!/usr/bin/env python3
"""PR & Communications Manager - PR, media relations & crisis comms."""

from ..base import PeopleSubSpecialist


class PRCommsSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "pr-comms"
    SUB_AGENT_DESCRIPTION = "PR, media relations & crisis comms, press releases, thought leadership, reputation"


specialist = PRCommsSpecialist()
