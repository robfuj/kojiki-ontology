#!/usr/bin/env python3
"""Pipeline Analyst - Forecasting, pipeline health, deal velocity, RevOps."""

from ..base import SalesSubSpecialist


class PipelineAnalystSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "pipeline-analyst"
    SUB_AGENT_DESCRIPTION = "Forecasting, pipeline health, deal velocity, RevOps"


specialist = PipelineAnalystSpecialist()
