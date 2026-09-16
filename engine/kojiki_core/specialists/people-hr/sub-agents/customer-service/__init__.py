#!/usr/bin/env python3
"""Customer Service - Omnichannel support, complaint handling, retention."""

from ..base import PeopleSubSpecialist


class CustomerServiceSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "customer-service"
    SUB_AGENT_DESCRIPTION = "Omnichannel support, complaint handling, retention, escalation, any industry"


specialist = CustomerServiceSpecialist()
