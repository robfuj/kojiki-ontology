#!/usr/bin/env python3
"""M&A Integration Manager - Post-merger integration."""

from ..base import OperationsSubSpecialist


class MAIntegrationSpecialist(OperationsSubSpecialist):
    SUB_AGENT_NAME = "ma-integration"
    SUB_AGENT_DESCRIPTION = "Post-merger integration, Day 1/100-day plans, synergy tracking, TSA management"


specialist = MAIntegrationSpecialist()
