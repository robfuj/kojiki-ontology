#!/usr/bin/env python3
"""RAG Pipeline Engineer - Production RAG pipelines."""

from ..base import EngineeringSubSpecialist


class RAGEngineerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "rag-engineer"
    SUB_AGENT_DESCRIPTION = "Production RAG pipelines, chunking, retrieval quality, hybrid search, re-ranking"


specialist = RAGEngineerSpecialist()
