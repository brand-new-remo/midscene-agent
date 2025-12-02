"""
Configuration management for MidsceneAgent
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for MidsceneAgent"""

    # DeepSeek API Configuration
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0"))

    # Midscene Configuration
    MIDSCENE_MODEL: str = os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision")
    MIDSCENE_COMMAND: str = os.getenv("MIDSCENE_COMMAND", "npx")
    MIDSCENE_ARGS: list = os.getenv("MIDSCENE_ARGS", "-y @midscene/mcp").split()

    # Browser Configuration
    CHROME_PATH: Optional[str] = os.getenv("CHROME_PATH")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # Additional environment variables
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not cls.DEEPSEEK_API_KEY:
            print("⚠️  Warning: DEEPSEEK_API_KEY not set")
            return False
        return True

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "deepseek": {
                "api_key": cls.DEEPSEEK_API_KEY[:10] + "..." if cls.DEEPSEEK_API_KEY else "",
                "base_url": cls.DEEPSEEK_BASE_URL,
                "model": cls.DEEPSEEK_MODEL,
                "temperature": cls.DEEPSEEK_TEMPERATURE,
            },
            "midscene": {
                "model": cls.MIDSCENE_MODEL,
                "command": cls.MIDSCENE_COMMAND,
                "args": cls.MIDSCENE_ARGS,
            },
            "openai": {
                "api_key": cls.OPENAI_API_KEY[:10] + "..." if cls.OPENAI_API_KEY else "",
                "base_url": cls.OPENAI_BASE_URL,
            },
            "browser": {
                "headless": cls.HEADLESS,
                "chrome_path": cls.CHROME_PATH,
            },
        }

    @classmethod
    def print_config(cls):
        """Print current configuration (with sensitive data masked)."""
        import json
        print("\n📋 Configuration:")
        print(json.dumps(cls.to_dict(), indent=2))


# Default prompts for the agent
SYSTEM_PROMPT = """You are an expert AI-powered web automation agent. You can interact with web pages through natural language instructions.

Your capabilities:
1. Navigate to any website
2. Click on elements (buttons, links, images, etc.)
3. Fill in forms with text
4. Scroll through pages
5. Extract information from pages
6. Search for content
7. Wait for pages to load

Available tools:
- midscene_action: Execute actions on the webpage
- midscene_query: Query information from the webpage

Best practices:
1. Break complex tasks into simple steps
2. Be specific about what you want to do
3. Describe elements by their visual appearance (e.g., "the blue login button")
4. Wait for pages to load after navigation
5. Verify your actions by observing the results
6. Report what you see at each step

When you need to interact with a page:
1. Clearly describe the action (e.g., "Click the 'Search' button in the top right")
2. Wait for the action to complete
3. Observe the result
4. Proceed to the next step

Remember: You can see the page just like a human would. Describe what you see and take actions accordingly.
"""

EXAMPLE_TASKS = [
    {
        "name": "Search Test",
        "description": "Navigate to a search engine and perform a search",
        "instruction": """
        1. Navigate to https://www.google.com
        2. In the search box, type "artificial intelligence"
        3. Click the search button
        4. Tell me the title of the first result
        """,
    },
    {
        "name": "Form Filling",
        "description": "Fill out and submit a contact form",
        "instruction": """
        1. Navigate to https://httpbin.org/forms/post
        2. Fill in the name field with "Test User"
        3. Fill in the email field with "test@example.com"
        4. Fill in the comments field with "This is a test"
        5. Submit the form
        6. Show me the response
        """,
    },
    {
        "name": "E-commerce Browse",
        "description": "Browse products on an e-commerce site",
        "instruction": """
        1. Navigate to https://www.amazon.com
        2. Search for "laptop"
        3. List the first 3 products you see with their prices
        4. Click on the first product
        5. Tell me the product rating and number of reviews
        """,
    },
]
