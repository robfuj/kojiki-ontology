#!/usr/bin/env python3
"""Business Strategist - Management-consulting strategy."""

from ..base import OperationsSubSpecialist


class BusinessStrategistSpecialist(OperationsSubSpecialist):
    SUB_AGENT_NAME = "business-strategist"
    SUB_AGENT_DESCRIPTION = "Management-consulting strategy, competitive analysis, market entry, growth planning"


specialist = BusinessStrategistSpecialist()
