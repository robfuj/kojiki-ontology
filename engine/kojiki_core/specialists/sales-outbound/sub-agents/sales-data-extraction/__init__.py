#!/usr/bin/env python3
"""Sales Data Extraction Agent - Excel monitoring, sales metric extraction."""

from ..base import SalesSubSpecialist


class SalesDataExtractionSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "sales-data-extraction"
    SUB_AGENT_DESCRIPTION = "Excel monitoring, sales metric extraction, MTD/YTD/Year End metrics"


specialist = SalesDataExtractionSpecialist()
