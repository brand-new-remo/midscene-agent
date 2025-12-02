#!/usr/bin/env python3
"""
Quick launcher for MidsceneAgent examples

This script provides a convenient way to run various examples
without having to remember the full python paths.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory and src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from examples.basic_usage import basic_example, interactive_example, query_example
from examples.test_ecommerce import (
    test_product_search,
    test_form_filling,
    test_navigation,
    run_all_tests,
)


def print_banner():
    """Print the application banner."""
    print("\n" + "=" * 70)
    print("  🕷️  Midscene LangGraph Agent - Quick Launcher")
    print("=" * 70)
    print("\nA powerful AI-driven web automation system\n")


def print_menu():
    """Print the main menu."""
    print("Select an example to run:\n")
    print("Basic Examples:")
    print("  1. Basic web automation task")
    print("  2. Interactive multi-task example")
    print("  3. Page query example")
    print("\nE-commerce Testing:")
    print("  4. Product search test (Amazon)")
    print("  5. Form filling test (httpbin.org)")
    print("  6. Navigation test (Hacker News)")
    print("  7. Run all e-commerce tests")
    print("\nAdvanced:")
    print("  8. Custom task (enter your own)")
    print("\nOther:")
    print("  9. Check configuration")
    print("  0. Exit")
    print()


async def run_custom_task():
    """Run a custom task provided by the user."""
    from agent import MidsceneAgent

    print("\n" + "=" * 70)
    print("Custom Task Mode")
    print("=" * 70)
    print("\nEnter a natural language description of what you want to do.")
    print("Example: 'Go to https://google.com and search for AI news'\n")

    task = input("Your task: ").strip()

    if not task:
        print("❌ No task provided")
        return

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found in environment")
        print("Please set it in .env file or export it")
        return

    print("\n" + "=" * 70)
    print("Executing your task...")
    print("=" * 70 + "\n")

    # Prepare environment variables for Midscene MCP server
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        env=midscene_env,
    )

    try:
        async with agent:
            async for event in agent.execute(task):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(msg.content)
                    else:
                        print(msg)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def check_config():
    """Check and display configuration."""
    from config import Config

    print("\n" + "=" * 70)
    print("Configuration Check")
    print("=" * 70 + "\n")

    Config.print_config()

    print("\n" + "-" * 70)
    print("\n✅ Configuration Status:")
    if Config.validate():
        print("   ✓ DeepSeek API key configured")
        print("   ✓ Ready to use!")
    else:
        print("   ⚠️  Some configuration is missing")
        print("   Please check your .env file")

    print()


async def main():
    """Main entry point."""
    print_banner()

    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found")
        print("   Copy .env.example to .env and add your DEEPSEEK_API_KEY\n")

    while True:
        print_menu()

        try:
            choice = input("Enter your choice (0-9): ").strip()
            print()

            if choice == "0":
                print("👋 Goodbye!\n")
                sys.exit(0)

            elif choice == "1":
                print("🚀 Running basic web automation task...\n")
                await basic_example()

            elif choice == "2":
                print("🚀 Running interactive multi-task example...\n")
                await interactive_example()

            elif choice == "3":
                print("🚀 Running page query example...\n")
                await query_example()

            elif choice == "4":
                print("🛒 Running product search test...\n")
                await test_product_search()

            elif choice == "5":
                print("📝 Running form filling test...\n")
                await test_form_filling()

            elif choice == "6":
                print("🧭 Running navigation test...\n")
                await test_navigation()

            elif choice == "7":
                print("🧪 Running all e-commerce tests...\n")
                await run_all_tests()

            elif choice == "8":
                await run_custom_task()

            elif choice == "9":
                check_config()

            else:
                print("❌ Invalid choice. Please try again.\n")
                continue

            # Pause before showing menu again
            if choice != "9" and choice != "0":
                input("\n" + "=" * 70)
                input("Press Enter to return to menu...")

            print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!\n")
        sys.exit(0)
