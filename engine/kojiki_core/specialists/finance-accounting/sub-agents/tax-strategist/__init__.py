#!/usr/bin/env python3
"""Tax Strategist - Tax optimization, multi-jurisdictional compliance."""

from ..base import FinanceSubSpecialist


class TaxStrategistSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "tax-strategist"
    SUB_AGENT_DESCRIPTION = "Tax optimization, multi-jurisdictional compliance, transfer pricing"


specialist = TaxStrategistSpecialist()
