"""
Midscene MCP Client Wrapper

This module provides a Python wrapper for the Midscene MCP (Model Context Protocol) server,
allowing LangGraph agents to interact with Midscene's AI-powered web automation capabilities.
"""

import asyncio
import os
import json
from typing import Optional, Any, Dict, List
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class MidsceneMCPWrapper:
    """
    Wrapper for Midscene MCP Server

    This class manages the connection to Midscene's MCP server and provides
    tools for the LangGraph agent to interact with web pages through AI.
    """

    def __init__(
        self,
        midscene_command: str = "npx",
        midscene_args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Midscene MCP wrapper.

        Args:
            midscene_command: Command to run Midscene MCP server (default: "npx")
            midscene_args: Arguments for the Midscene command (default: ["-y", "@midscene/mcp"])
            env: Environment variables to pass to the MCP server
        """
        if midscene_args is None:
            midscene_args = ["-y", "@midscene/mcp"]

        # Set default environment variables
        default_env = os.environ.copy()
        default_env["MCP_SERVER_REQUEST_TIMEOUT"] = "800000"  # 800 seconds timeout
        if env:
            default_env.update(env)

        self.server_params = StdioServerParameters(
            command=midscene_command,
            args=midscene_args,
            env=default_env
        )

        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self._available_tools: List[str] = []

    async def start(self) -> None:
        """
        Start the connection to Midscene MCP Server.

        Raises:
            RuntimeError: If connection fails
        """
        try:
            self.exit_stack = AsyncExitStack()

            # Establish stdio connection
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(self.server_params)
            )
            read_stream, write_stream = stdio_transport

            # Create and initialize client session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # Initialize with a longer timeout for Midscene
            print("🔌 Connecting to Midscene MCP Server...")
            await asyncio.wait_for(self.session.initialize(), timeout=120)
            print("✅ Midscene MCP Server initialized")

            # Discover available tools
            tools_result = await self.session.list_tools()
            self._available_tools = [tool.name for tool in tools_result.tools]

            print(f"✅ Connected to Midscene MCP Server")
            print(f"🔧 Available tools: {', '.join(self._available_tools)}")

        except asyncio.TimeoutError:
            if self.exit_stack:
                await self.exit_stack.aclose()
            raise RuntimeError("Timeout connecting to Midscene MCP Server. The server may still be starting up. Try again.")
        except Exception as e:
            if self.exit_stack:
                await self.exit_stack.aclose()
            raise RuntimeError(f"Failed to connect to Midscene MCP Server: {e}")

    async def stop(self) -> None:
        """Close the connection to Midscene MCP Server."""
        if self.exit_stack:
            await self.exit_stack.aclose()
            print("🔌 Disconnected from Midscene MCP Server")

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call a tool on the Midscene MCP server.
        Maps abstract tool names to specific Midscene tools.

        Args:
            tool_name: Name of the tool to call ('action' or 'query')
            arguments: Arguments to pass to the tool

        Returns:
            The result from the MCP tool

        Raises:
            RuntimeError: If not connected or tool call fails
        """
        if not self.session:
            raise RuntimeError("Not connected to Midscene MCP Server")

        try:
            # Map abstract tool names to specific Midscene tools
            if tool_name in ("action", "midscene_action"):
                instruction = arguments.get("instruction", "") if arguments else ""

                # Parse the instruction to determine which tool to use
                if instruction.startswith("Navigate to") or instruction.startswith("navigate to"):
                    url = instruction.replace("Navigate to", "").replace("navigate to", "").strip()
                    if not url.startswith("http"):
                        url = "https://" + url
                    result = await self.session.call_tool("midscene_navigate", {"url": url})
                    return result
                elif "click" in instruction.lower():
                    # For clicks, use aiAssert to locate and click
                    target = instruction.replace("click", "").strip()
                    result = await self.session.call_tool("midscene_aiAssert", {"assertion": f"Click on the {target}"})
                    return result
                elif "input" in instruction.lower() or "type" in instruction.lower():
                    # Parse input instruction
                    # Format: "input text 'Hello' into search box" or "type 'Hello' in field"
                    import re
                    match = re.search(r"(?:input|type)\s+(?:text\s+)?['\"]([^'\"]+)['\"]", instruction, re.IGNORECASE)
                    text = match.group(1) if match else ""
                    # Extract target
                    target = instruction
                    if "into" in target.lower():
                        target = target.lower().split("into")[1].strip()
                    elif "in" in target.lower():
                        target = target.lower().split("in")[1].strip()
                    elif "on" in target.lower():
                        target = target.lower().split("on")[1].strip()

                    result = await self.session.call_tool("midscene_aiAssert", {
                        "assertion": f"Type '{text}' into the {target}"
                    })
                    return result
                elif "scroll" in instruction.lower():
                    direction = "down" if "down" in instruction.lower() else "up"
                    result = await self.session.call_tool("midscene_aiScroll", {
                        "direction": direction,
                        "scrollType": "once"
                    })
                    return result
                else:
                    # Default: use aiAssert for general actions
                    result = await self.session.call_tool("midscene_aiAssert", {
                        "assertion": instruction
                    })
                    return result

            elif tool_name in ("query", "midscene_query"):
                question = arguments.get("question", "") if arguments else ""
                result = await self.session.call_tool("midscene_aiAssert", {
                    "assertion": question
                })
                return result

            else:
                # Direct tool call
                result = await self.session.call_tool(tool_name, arguments or {})
                return result

        except Exception as e:
            import traceback
            error_details = {
                "tool_name": tool_name,
                "arguments": arguments,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"\n❌ Tool call failed:")
            print(f"   Tool: {tool_name}")
            print(f"   Error: {error_details['error_message']}")
            print(f"   Type: {error_details['error_type']}")
            raise RuntimeError(f"Failed to call tool '{tool_name}': {e}\nDetails: {json.dumps(error_details, indent=2)}")

    async def get_tools(self) -> List[str]:
        """
        Get list of available tools.

        Returns:
            List of tool names
        """
        return self._available_tools.copy()

    async def health_check(self) -> bool:
        """
        Check if the MCP server connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            if not self.session:
                return False

            # Try to list tools as a health check
            await self.session.list_tools()
            return True
        except Exception:
            return False


class MidsceneConnectionError(Exception):
    """Raised when connection to Midscene MCP server fails."""
    pass


class MidsceneToolError(Exception):
    """Raised when a tool call to Midscene fails."""
    pass
