#!/usr/bin/env python3
"""MCP Builder - Model Context Protocol servers, AI agent tooling."""

from ..base import AISubSpecialist


class MCPBuilderSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "mcp-builder"
    SUB_AGENT_DESCRIPTION = "Model Context Protocol servers, AI agent tooling, building MCP servers that extend AI agent capabilities"


specialist = MCPBuilderSpecialist()
