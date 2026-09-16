#!/usr/bin/env python3
"""Support Responder - Customer service, issue resolution."""

from ..base import PeopleSubSpecialist


class SupportResponderSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "support-responder"
    SUB_AGENT_DESCRIPTION = "Customer service, issue resolution, customer support, user experience"


specialist = SupportResponderSpecialist()
