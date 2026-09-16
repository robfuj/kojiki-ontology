#!/usr/bin/env python3
"""Secrets & Credential Hygiene Engineer - Secrets & credential lifecycle."""

from ..base import AISubSpecialist


class SecretsHygieneSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "secrets-hygiene"
    SUB_AGENT_DESCRIPTION = "Secrets & credential lifecycle, detection, vaulting, rotation, leak response"


specialist = SecretsHygieneSpecialist()
