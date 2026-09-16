#!/usr/bin/env python3
"""Code Reviewer - Constructive code review, security, maintainability."""

from ..base import EngineeringSubSpecialist


class CodeReviewerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "code-reviewer"
    SUB_AGENT_DESCRIPTION = "Constructive code review, security, maintainability, mentoring"


specialist = CodeReviewerSpecialist()
