#!/usr/bin/env python3
"""
Test script to debug Midscene MCP connection issues
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import MCP wrapper directly
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from mcp_wrapper import MidsceneMCPWrapper

async def test_mcp_connection():
    """Test direct connection to Midscene MCP server"""

    print("🧪 Testing Midscene MCP Server Connection\n")
    print("=" * 60)

    # Prepare environment variables for Midscene MCP server
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    print("\n📋 Configuration:")
    print(f"  Command: npx")
    print(f"  Args: -y @midscene/mcp")
    print(f"  Environment variables:")
    for key, value in midscene_env.items():
        print(f"    {key} = {value if value else '(not set)'}")

    # Create MCP wrapper
    wrapper = MidsceneMCPWrapper(
        midscene_command="npx",
        midscene_args=["-y", "@midscene/mcp"],
        env=midscene_env
    )

    try:
        print("\n🔌 Attempting to connect to Midscene MCP Server...")
        print("  (This may take 30-60 seconds on first run)\n")

        await wrapper.start()

        print("\n✅ Successfully connected to Midscene MCP Server!")
        tools = await wrapper.get_tools()
        print(f"🔧 Available tools: {', '.join(tools)}")

        # Test a simple query
        print("\n🧪 Testing simple query tool...")
        try:
            result = await wrapper.call_tool("query", {"question": "What is on the current page?"})
            print(f"✅ Query test successful: {result}")
        except Exception as e:
            print(f"⚠️  Query test failed (but connection works): {e}")

        await wrapper.stop()
        print("\n✅ Test completed successfully!")
        return True

    except asyncio.TimeoutError:
        print("\n❌ TIMEOUT: Could not connect to Midscene MCP Server")
        print("   This usually means:")
        print("   - The server is taking too long to start (first run can take several minutes)")
        print("   - Node.js/npm is not properly installed")
        print("   - Network issues downloading the @midscene/mcp package")
        print("\n💡 Try running: npm install -g @midscene/mcp")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to Midscene MCP Server")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {e}")
        print("\n🔍 Full traceback:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    exit(0 if success else 1)
