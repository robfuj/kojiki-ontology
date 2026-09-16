#!/usr/bin/env python3
"""RAG Pipeline Engineer - Production RAG pipelines."""

from ..base import AISubSpecialist


class RAGPipelineSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "rag-pipeline"
    SUB_AGENT_DESCRIPTION = "Production RAG pipelines, chunking, retrieval quality, hybrid search, re-ranking, eval-driven iteration"


specialist = RAGPipelineSpecialist()
