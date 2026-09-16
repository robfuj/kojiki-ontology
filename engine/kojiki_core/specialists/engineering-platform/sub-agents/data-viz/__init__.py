#!/usr/bin/env python3
"""Data Visualization Engineer - Perceptually honest data viz."""

from ..base import EngineeringSubSpecialist


class DataVizSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "data-viz"
    SUB_AGENT_DESCRIPTION = "Perceptually honest data viz, chart-type selection, colorblind-safe palettes, D3/Vega"


specialist = DataVizSpecialist()
