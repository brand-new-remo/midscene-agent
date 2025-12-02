"""
Basic Usage Example

This example demonstrates how to use the MidsceneAgent to automate web tasks.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path - use absolute path for better reliability
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "..", "src")
sys.path.insert(0, os.path.abspath(src_path))

# Import the agent module directly
from agent import MidsceneAgent  # pyright: ignore

# Load environment variables
load_dotenv()


async def basic_example():
    """
    Basic example of using MidsceneAgent for web automation.
    """
    # Get configuration from environment
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found in environment")
        print("Please set it in .env file or export it as an environment variable")
        return

    # Prepare environment variables for Midscene MCP server
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    # Initialize the agent
    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0,
        env=midscene_env,
    )

    try:
        # Use the agent as an async context manager
        async with agent_instance:
            # Define the task
            task = """
            Please complete the following web automation task:
            1. Navigate to https://www.bing.com
            2. In the search box, type "LangGraph DeepSeek Midscene"
            3. Click the search button
            4. Wait for results to load
            5. Tell me the title of the first search result

            Please proceed step by step and report what you see at each step.
            """

            # Execute the task
            async for event in agent_instance.execute(task):
                if "messages" in event:
                    # Print the latest message
                    last_message = event["messages"][-1]
                    # LangChain 1.0+ compatible output
                    if hasattr(last_message, "content"):
                        print(last_message.content)
                    else:
                        print(last_message)
                elif "error" in event:
                    print(f"❌ Error: {event['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


async def interactive_example():
    """
    Interactive example - allows multiple tasks in one session.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found")
        return

    # Prepare environment variables for Midscene MCP server
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        env=midscene_env,
    )

    try:
        # Initialize once
        await agent_instance.initialize()

        # Execute multiple tasks in sequence
        tasks = [
            "Navigate to https://news.ycombinator.com and tell me the title of the page",
            "Look for a 'submit' button or link and describe where it is",
            "Scroll down to see more content on the page",
        ]

        for i, task in enumerate(tasks, 1):
            print(f"\n{'='*60}")
            print(f"Task {i}/{len(tasks)}")
            print(f"{'='*60}\n")

            async for event in agent_instance.execute(task):
                if "messages" in event:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, "content"):
                        print(last_message.content)
                    else:
                        print(last_message)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent_instance.cleanup()


async def query_example():
    """
    Example focused on querying information from pages.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found")
        return

    # Prepare environment variables for Midscene MCP server
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        env=midscene_env,
    )

    try:
        await agent_instance.initialize()

        # First, navigate to a page
        print("📄 Navigating to https://example.com...")
        async for event in agent_instance.execute("Navigate to https://example.com"):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content"):
                    print(msg.content)
                else:
                    print(msg)

        # Now query the page
        print("\n🔍 Querying page information...")
        async for event in agent_instance.execute(
            "What is this page about? Extract all visible text and list the main sections."
        ):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content"):
                    print(msg.content)
                else:
                    print(msg)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent_instance.cleanup()


if __name__ == "__main__":
    print("MidsceneAgent Basic Usage Examples\n")
    print("Select an example to run:")
    print("1. Basic web automation task")
    print("2. Interactive multi-task example")
    print("3. Page query example")
    print("\nPress Ctrl+C to exit\n")

    try:
        choice = input("Enter your choice (1-3): ").strip()
        print()

        if choice == "1":
            asyncio.run(basic_example())
        elif choice == "2":
            asyncio.run(interactive_example())
        elif choice == "3":
            asyncio.run(query_example())
        else:
            print("Invalid choice. Running basic example...")
            asyncio.run(basic_example())

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
