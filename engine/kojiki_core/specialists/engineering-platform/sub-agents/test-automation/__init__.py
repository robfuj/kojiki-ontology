#!/usr/bin/env python3
"""Test Automation Engineer - Playwright/Cypress E2E, flake elimination."""

from ..base import EngineeringSubSpecialist


class TestAutomationSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "test-automation"
    SUB_AGENT_DESCRIPTION = "Playwright/Cypress E2E, flake elimination, CI parallelization"


specialist = TestAutomationSpecialist()
