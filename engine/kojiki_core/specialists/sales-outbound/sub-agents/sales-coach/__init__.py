#!/usr/bin/env python3
"""Sales Coach - Rep development, call coaching, pipeline review facilitation."""

from ..base import SalesSubSpecialist


class SalesCoachSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "sales-coach"
    SUB_AGENT_DESCRIPTION = "Rep development, call coaching, pipeline review facilitation"


specialist = SalesCoachSpecialist()
