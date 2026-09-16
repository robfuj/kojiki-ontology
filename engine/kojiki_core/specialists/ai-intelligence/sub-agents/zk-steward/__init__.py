#!/usr/bin/env python3
"""ZK Steward - Knowledge management, Zettelkasten, notes."""

from ..base import AISubSpecialist


class ZKStewardSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "zk-steward"
    SUB_AGENT_DESCRIPTION = "Knowledge management, Zettelkasten, notes, building connected, validated knowledge bases"


specialist = ZKStewardSpecialist()
