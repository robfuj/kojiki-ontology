#!/usr/bin/env python3
"""Data Consolidation Agent - Sales data aggregation, dashboard reports."""

from ..base import SalesSubSpecialist


class DataConsolidationSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "data-consolidation"
    SUB_AGENT_DESCRIPTION = "Sales data aggregation, dashboard reports, territory summaries, rep performance"


specialist = DataConsolidationSpecialist()
