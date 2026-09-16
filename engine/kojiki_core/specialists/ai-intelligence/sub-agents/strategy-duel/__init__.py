#!/usr/bin/env python3
"""Strategy Duel Agent - Game theory & the 36 stratagems."""

from ..base import AISubSpecialist


class StrategyDuelSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "strategy-duel"
    SUB_AGENT_DESCRIPTION = "Game theory & the 36 stratagems, turn-based strategy duels, adversarial scenario simulation"


specialist = StrategyDuelSpecialist()
