"""
Midscene LangGraph Agent

A powerful AI-driven web automation system combining:
- LangGraph for intelligent orchestration
- DeepSeek LLM for reasoning
- Midscene for vision-based web interaction

Usage:
    from agent.src.agent import MidsceneAgent

    async with MidsceneAgent(deepseek_api_key="your-key") as agent:
        async for event in agent.execute("Navigate to https://example.com"):
            print(event)
"""

from .src.agent import MidsceneAgent

__version__ = "1.0.0"
__author__ = "AI Automation Team"

__all__ = [
    "MidsceneAgent",
]
