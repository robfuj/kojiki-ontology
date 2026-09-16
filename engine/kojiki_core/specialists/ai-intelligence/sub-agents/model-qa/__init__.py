#!/usr/bin/env python3
"""Model QA Specialist - ML audits, feature analysis, interpretability."""

from ..base import AISubSpecialist


class ModelQASpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "model-qa"
    SUB_AGENT_DESCRIPTION = "ML audits, feature analysis, interpretability, end-to-end QA for machine learning models"


specialist = ModelQASpecialist()
