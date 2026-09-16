#!/usr/bin/env python3
"""Document Generator - PDF, PPTX, DOCX, XLSX generation from code."""

from ..base import AISubSpecialist


class DocGeneratorSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "doc-generator"
    SUB_AGENT_DESCRIPTION = "PDF, PPTX, DOCX, XLSX generation from code, professional document creation, reports, data visualization"


specialist = DocGeneratorSpecialist()
