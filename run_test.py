#!/usr/bin/env python3
"""
Simple test to capture the actual tool call error
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from mcp_wrapper import MidsceneMCPWrapper

async def test_tool_call():
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
        "CHROME_PATH": os.getenv("CHROME_PATH", ""),
    }

    wrapper = MidsceneMCPWrapper(
        midscene_command="npx",
        midscene_args=["-y", "@midscene/mcp"],
        env=midscene_env
    )

    try:
        await wrapper.start()
        print("✅ Connected to Midscene MCP Server")
        
        print("\n🔧 Testing tool call...")
        result = await wrapper.call_tool("midscene_action", {"instruction": "Navigate to https://www.bing.com"})
        print(f"\n✅ Success! Result: {result}")
        
    except Exception as e:
        print(f"\n❌ Error occurred:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {e}")
        import traceback
        print(f"\n📜 Full traceback:")
        traceback.print_exc()
    finally:
        await wrapper.stop()

if __name__ == "__main__":
    asyncio.run(test_tool_call())
