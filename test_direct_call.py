#!/usr/bin/env python3
"""
Direct test of the agent without streaming
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from agent import MidsceneAgent

async def test_direct():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found")
        return

    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0,
        env=midscene_env,
    )

    try:
        await agent_instance.initialize()
        
        print("\n🚀 Executing task (non-streaming)...\n")
        
        # Test without streaming
        result = await agent_instance.execute("Navigate to https://www.bing.com", stream=False)
        
        print("\n✅ Result:")
        print(result)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent_instance.cleanup()

if __name__ == "__main__":
    asyncio.run(test_direct())
