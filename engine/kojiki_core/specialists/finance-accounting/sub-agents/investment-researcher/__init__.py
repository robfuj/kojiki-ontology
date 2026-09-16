#!/usr/bin/env python3
"""Investment Researcher - Due diligence, portfolio analysis, asset valuation."""

from ..base import FinanceSubSpecialist


class InvestmentResearcherSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "investment-researcher"
    SUB_AGENT_DESCRIPTION = "Due diligence, portfolio analysis, asset valuation, equity research"


specialist = InvestmentResearcherSpecialist()
