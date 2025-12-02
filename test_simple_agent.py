#!/usr/bin/env python3
"""
Simple test without MCP to isolate the LangGraph issue
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

# Create a simple test tool
from langchain_core.tools import tool

@tool
def simple_tool(input: str) -> str:
    """A simple test tool"""
    return f"Tool executed with: {input}"

def create_simple_agent():
    """Create a simple agent without MCP to test LangGraph"""

    # Initialize LLM
    llm = ChatDeepSeek(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY", "")),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=0,
        streaming=True
    )

    # Create tools
    tools = [simple_tool]
    llm_with_tools = llm.bind_tools(tools)

    # Build the graph
    def agent_node(state: MessagesState):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": state["messages"] + [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", "end": END}
    )
    builder.add_edge("tools", "agent")

    graph = builder.compile()
    return graph

async def test_simple_agent():
    """Test the simple agent"""

    print("🧪 Testing Simple LangGraph Agent")
    print("=" * 60)

    graph = create_simple_agent()

    input_messages = {"messages": [HumanMessage(content="Call the simple tool with 'test input'")]}

    try:
        print("\n📤 Input:")
        print(f"  {input_messages['messages'][0].content}")

        print("\n📥 Streaming output:")
        event_count = 0
        async for event in graph.astream(input_messages):
            event_count += 1
            print(f"\n📦 Event {event_count}:")
            print(f"  Keys: {list(event.keys())}")

            if "messages" in event:
                for msg in event["messages"]:
                    print(f"\n  📝 Message:")
                    print(f"     Type: {type(msg).__name__}")
                    if hasattr(msg, 'content'):
                        print(f"     Content: {str(msg.content)[:100]}...")
                    if hasattr(msg, 'tool_calls'):
                        print(f"     Tool calls: {msg.tool_calls}")

        print(f"\n✅ Total events received: {event_count}")
        return True

    except Exception as e:
        print(f"\n❌ Exception:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_agent())
    exit(0 if success else 1)
