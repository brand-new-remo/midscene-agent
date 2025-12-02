"""
Midscene MCP 客户端包装器

本模块为 Midscene MCP（Model Context Protocol）服务器提供 Python 包装器，
允许 LangGraph 智能体与 Midscene 的 AI 驱动网页自动化功能交互。
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
    Midscene MCP 服务器包装器

    此类管理与 Midscene MCP 服务器的连接，并为 LangGraph 智能体提供
    通过 AI 与网页交互的工具。
    """

    def __init__(
        self,
        midscene_command: str = "npx",
        midscene_args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ):
        """
        初始化 Midscene MCP 包装器。

        Args:
            midscene_command: 运行 Midscene MCP 服务器的命令（默认："npx"）
            midscene_args: Midscene 命令的参数（默认：["-y", "@midscene/mcp"]）
            env: 传递给 MCP 服务器的环境变量
        """
        if midscene_args is None:
            midscene_args = ["-y", "@midscene/mcp"]

        # 设置默认环境变量
        default_env = os.environ.copy()
        default_env["MCP_SERVER_REQUEST_TIMEOUT"] = "800000"  # 800 秒超时
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
        启动与 Midscene MCP 服务器的连接。

        Raises:
            RuntimeError: 如果连接失败
        """
        try:
            self.exit_stack = AsyncExitStack()

            # 建立 stdio 连接
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(self.server_params)
            )
            read_stream, write_stream = stdio_transport

            # 创建并初始化客户端会话
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # 为 Midscene 使用更长的超时时间初始化
            print("🔌 正在连接到 Midscene MCP 服务器...")
            await asyncio.wait_for(self.session.initialize(), timeout=120)
            print("✅ Midscene MCP 服务器已初始化")

            # 发现可用工具
            tools_result = await self.session.list_tools()
            self._available_tools = [tool.name for tool in tools_result.tools]

            print(f"✅ 已连接到 Midscene MCP 服务器")
            print(f"🔧 可用工具: {', '.join(self._available_tools)}")

        except asyncio.TimeoutError:
            if self.exit_stack:
                await self.exit_stack.aclose()
            raise RuntimeError("连接到 Midscene MCP 服务器超时。服务器可能仍在启动中。请重试。")
        except Exception as e:
            if self.exit_stack:
                await self.exit_stack.aclose()
            raise RuntimeError(f"连接到 Midscene MCP 服务器失败: {e}")

    async def stop(self) -> None:
        """关闭与 Midscene MCP 服务器的连接。"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            print("🔌 已断开与 Midscene MCP 服务器的连接")

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        调用 Midscene MCP 服务器上的工具。
        将抽象工具名称映射到特定的 Midscene 工具。

        Args:
            tool_name: 要调用的工具名称（'action' 或 'query'）
            arguments: 传递给工具的参数

        Returns:
            MCP 工具的结果

        Raises:
            RuntimeError: 如果未连接或工具调用失败
        """
        if not self.session:
            raise RuntimeError("未连接到 Midscene MCP 服务器")

        try:
            # 将抽象工具名称映射到特定的 Midscene 工具
            if tool_name in ("action", "midscene_action"):
                instruction = arguments.get("instruction", "") if arguments else ""

                # 解析指令以确定使用哪个工具
                # 支持英文和中文导航指令
                if (instruction.startswith("Navigate to") or instruction.startswith("navigate to") or
                    instruction.startswith("导航到") or instruction.startswith("导航到 ")):
                    url = (instruction.replace("Navigate to", "").replace("navigate to", "")
                           .replace("导航到", "").strip())
                    if not url.startswith("http"):
                        url = "https://" + url
                    print(f"\n🔄 执行导航: {url}")
                    result = await self.session.call_tool("midscene_navigate", {"url": url})
                    print(f"✅ 导航结果: {result}")
                    return result
                elif "click" in instruction.lower():
                    # 对于点击，使用 aiAssert 定位并点击
                    target = instruction.replace("click", "").strip()
                    result = await self.session.call_tool("midscene_aiAssert", {"assertion": f"Click on the {target}"})
                    return result
                elif "input" in instruction.lower() or "type" in instruction.lower():
                    # 解析输入指令
                    # 格式："input text 'Hello' into search box" 或 "type 'Hello' in field"
                    import re
                    match = re.search(r"(?:input|type)\s+(?:text\s+)?['\"]([^'\"]+)['\"]", instruction, re.IGNORECASE)
                    text = match.group(1) if match else ""
                    # 提取目标
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
                    # 默认：使用 aiAssert 执行通用操作
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
                # 直接工具调用
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
            print(f"\n❌ 工具调用失败:")
            print(f"   工具: {tool_name}")
            print(f"   错误: {error_details['error_message']}")
            print(f"   类型: {error_details['error_type']}")
            raise RuntimeError(f"调用工具 '{tool_name}' 失败: {e}\n详细信息: {json.dumps(error_details, indent=2)}")

    async def get_tools(self) -> List[str]:
        """
        获取可用工具列表。

        Returns:
            工具名称列表
        """
        return self._available_tools.copy()

    async def health_check(self) -> bool:
        """
        检查 MCP 服务器连接是否健康。

        Returns:
            如果连接健康返回 True，否则返回 False
        """
        try:
            if not self.session:
                return False

            # 尝试列出工具作为健康检查
            await self.session.list_tools()
            return True
        except Exception:
            return False


class MidsceneConnectionError(Exception):
    """当连接到 Midscene MCP 服务器失败时抛出。"""
    pass


class MidsceneToolError(Exception):
    """当调用 Midscene 工具失败时抛出。"""
    pass
