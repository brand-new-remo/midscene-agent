"""
Midscene LangGraph Agent

A powerful AI-driven web automation system combining:
- LangGraph for intelligent orchestration
- DeepSeek LLM for reasoning
- Midscene for vision-based web interaction

Usage:
    from agent import MidsceneAgent

    async with MidsceneAgent(deepseek_api_key="your-key") as agent:
        async for event in agent.execute("Navigate to https://example.com"):
            print(event)
"""

from .agent import MidsceneAgent
from .mcp_wrapper import MidsceneMCPWrapper, MidsceneConnectionError, MidsceneToolError

__version__ = "1.0.0"
__author__ = "AI Automation Team"

__all__ = [
    "MidsceneAgent",
    "MidsceneMCPWrapper",
    "MidsceneConnectionError",
    "MidsceneToolError",
]
