#!/usr/bin/env python3
"""Report Distribution Agent - Automated report delivery."""

from ..base import SalesSubSpecialist


class ReportDistributionSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "report-distribution"
    SUB_AGENT_DESCRIPTION = "Automated report delivery, territory-based report distribution, scheduled sends"


specialist = ReportDistributionSpecialist()
