#!/usr/bin/env python3
"""
Test with detailed logging to debug the __end__ issue
"""

import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from agent import MidsceneAgent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

async def test_with_logging():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found")
        return

    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
        "CHROME_PATH": os.getenv("CHROME_PATH", ""),
    }

    agent = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0,
        env=midscene_env,
    )

    try:
        await agent.initialize()

        print("\n" + "=" * 60)
        print("Testing LLM directly...")
        print("=" * 60)

        # Test LLM directly first
        system_msg = SystemMessage(content="""You are a helpful assistant.
You have access to tools to interact with web pages.
When you need to interact with a web page, use the tool by including a Tool call in your response.
Always use the tools when you need to perform actions or get information about web pages.

Available tools:
- midscene_action: Execute browser actions (click, input, scroll, navigate, etc.)
- midscene_query: Query information from the current page

If you don't need to use any tools, you can respond directly.""")

        user_msg = HumanMessage(content="Navigate to https://www.bing.com")

        print("\n📤 Sending messages to LLM:")
        print(f"  System: {system_msg.content[:100]}...")
        print(f"  User: {user_msg.content}")

        response = await agent.llm.ainvoke([system_msg, user_msg])

        print("\n📥 LLM Response:")
        print(f"  Type: {type(response)}")
        print(f"  Content: {response.content}")

        # Check if response has tool calls
        if hasattr(response, 'tool_calls'):
            print(f"  Tool calls: {response.tool_calls}")
        else:
            print("  ❌ No tool_calls attribute found!")

        print("\n" + "=" * 60)
        print("Testing Agent execution...")
        print("=" * 60)

        # Now test the agent
        task = "Navigate to https://www.bing.com"
        print(f"\n🚀 Starting agent execution for task: {task}")

        event_count = 0
        async for event in agent.execute(task):
            event_count += 1
            print(f"\n📦 Event {event_count}:")
            print(f"  Keys: {list(event.keys())}")

            if "messages" in event:
                for msg in event["messages"]:
                    print(f"\n  📝 Message:")
                    print(f"     Type: {type(msg).__name__}")
                    if hasattr(msg, 'content'):
                        print(f"     Content: {msg.content}")
                    if hasattr(msg, 'tool_calls'):
                        print(f"     Tool calls: {msg.tool_calls}")

            if "tool" in event:
                print(f"\n  🔧 Tool result:")
                print(f"     Tool: {event['tool']}")
                if hasattr(event['tool'], 'content'):
                    print(f"     Content: {event['tool'].content}")

            if "error" in event:
                print(f"\n  ❌ Error: {event['error']}")
                # Print full error details
                import traceback
                print("  Full traceback:")
                traceback.print_exc()

        print(f"\n✅ Total events received: {event_count}")

    except Exception as e:
        print(f"\n❌ Exception occurred:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_with_logging())
