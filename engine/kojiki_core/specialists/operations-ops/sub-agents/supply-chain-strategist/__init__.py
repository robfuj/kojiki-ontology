#!/usr/bin/env python3
"""Supply Chain Strategist - Supply chain management, procurement strategy."""

from ..base import OperationsSubSpecialist


class SupplyChainStrategistSpecialist(OperationsSubSpecialist):
    SUB_AGENT_NAME = "supply-chain-strategist"
    SUB_AGENT_DESCRIPTION = "Supply chain management, procurement strategy, optimization and procurement planning"


specialist = SupplyChainStrategistSpecialist()
