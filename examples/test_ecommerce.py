"""
E-commerce Testing Example

This example demonstrates testing an e-commerce website using natural language.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path - use absolute path for better reliability
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

# Import the agent module directly
from agent import MidsceneAgent  # pyright: ignore

load_dotenv()


async def test_product_search():
    """
    Test the product search functionality on an e-commerce site.
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

    # Test product search on Amazon
    task = """
    Let's test the product search functionality:

    1. Navigate to https://www.amazon.com
    2. Search for "wireless headphones"
    3. Wait for search results to load
    4. Report how many search results are shown
    5. What is the price and rating of the first product shown?
    6. Click on the first product to view details
    7. What are the key features listed for this product?

    Take your time and verify each step before moving to the next.
    """

    print("🛒 E-commerce Product Search Test")
    print("=" * 60)

    try:
        async with agent_instance:
            async for event in agent_instance.execute(task):
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


async def test_form_filling():
    """
    Test form filling functionality.
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

        # Test form filling
        task = """
        Let's test form filling:

        1. Navigate to https://httpbin.org/forms/post (this is a test form)
        2. Fill in the form with the following information:
           - Custname: "John Doe"
           - Custtel: "123-456-7890"
           - Custemail: "john.doe@example.com"
           - Comments: "This is a test submission"
        3. Submit the form
        4. Report the response from the server

        Describe what you see at each step and confirm the form fields are filled correctly.
        """

        print("📝 Form Filling Test")
        print("=" * 60)

        async for event in agent_instance.execute(task):
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
    finally:
        await agent_instance.cleanup()


async def test_navigation():
    """
        Test navigation and page state verification.
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

        # Test navigation
        task = """
        Let's test website navigation:

        1. Navigate to https://news.ycombinator.com
        2. What is the title of the page?
        3. List all the navigation links in the header
        4. Click on the "new" link (or similar)
        5. Wait for the page to load and describe what's visible
        6. Go back to the previous page
        7. Verify you're back on the main page

        Pay attention to the page structure and report any changes.
        """

        print("🧭 Navigation Test")
        print("=" * 60)

        async for event in agent_instance.execute(task):
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
    finally:
        await agent_instance.cleanup()


async def run_all_tests():
    """
    Run all e-commerce tests in sequence.
    """
    print("🧪 E-commerce Test Suite")
    print("=" * 60)
    print("\nThis will run multiple test scenarios:")
    print("1. Product Search Test")
    print("2. Form Filling Test")
    print("3. Navigation Test")
    print("\nEach test will be run sequentially. Press Ctrl+C to skip remaining tests.\n")

    tests = [
        ("Product Search", test_product_search),
        ("Form Filling", test_form_filling),
        ("Navigation", test_navigation),
    ]

    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}\n")

        try:
            await test_func()
            print(f"\n✅ {name} completed successfully")
        except KeyboardInterrupt:
            print(f"\n⚠️  Skipping remaining tests")
            break
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)
        input("Press Enter to continue to next test...")
        print()

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    print("E-commerce Testing Examples\n")

    try:
        choice = input(
            "Select test to run:\n"
            "1. Product Search Test\n"
            "2. Form Filling Test\n"
            "3. Navigation Test\n"
            "4. Run All Tests\n\n"
            "Enter choice (1-4): "
        ).strip()

        print()

        if choice == "1":
            asyncio.run(test_product_search())
        elif choice == "2":
            asyncio.run(test_form_filling())
        elif choice == "3":
            asyncio.run(test_navigation())
        elif choice == "4":
            asyncio.run(run_all_tests())
        else:
            print("Running product search test...")
            asyncio.run(test_product_search())

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
