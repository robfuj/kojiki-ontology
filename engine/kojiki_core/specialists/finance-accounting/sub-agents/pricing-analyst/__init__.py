#!/usr/bin/env python3
"""Pricing Analyst - Pricing models & margin optimization."""

from ..base import FinanceSubSpecialist


class PricingAnalystSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "pricing-analyst"
    SUB_AGENT_DESCRIPTION = "Pricing models & margin optimization, competitor/cost analysis"


specialist = PricingAnalystSpecialist()
