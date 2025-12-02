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
                    print(f"\n📦 MCP 工具返回结果 [🔄 导航]:")
                    print(f"   {result}")
                    return result
                elif "click" in instruction.lower() or "点击" in instruction or "按" in instruction:
                    # 对于点击操作，支持英文 "click" 和中文 "点击"、"按"
                    # 处理不同格式：英文 "click search button"、中文 "点击搜索按钮"、"按搜索按钮"
                    target = instruction.lower()
                    # 移除各种点击相关的关键词
                    for keyword in ["click", "点击", "按"]:
                        target = target.replace(keyword, "").strip()
                    # 如果处理后为空，尝试使用原指令（可能是"按回车键"这样的特殊操作）
                    if not target or target == "":
                        target = instruction.strip()
                    print(f"\n🖱️ 执行点击: {target}")
                    result = await self.session.call_tool("midscene_aiTap", {"locate": target})
                    print(f"\n📦 MCP 工具返回结果 [🖱️ 点击]:")
                    print(f"   {result}")
                    return result
                elif "input" in instruction.lower() or "type" in instruction.lower() or "输入" in instruction:
                    # 解析输入指令 - 支持中英文格式
                    # 英文格式："input text 'Hello' into search box" 或 "type 'Hello' in field"
                    # 中文格式："在搜索框中输入 'Hello'" 或 "输入文本 'Hello'"
                    import re

                    # 尝试英文格式
                    match = re.search(r"(?:input|type)\s+(?:text\s+)?['\"]([^'\"]+)['\"]", instruction, re.IGNORECASE)
                    text = match.group(1) if match else ""

                    # 如果英文格式失败，尝试中文格式
                    if not text:
                        # 中文格式1："在搜索框中输入 'Hello'"
                        match = re.search(r"输入\s+['\"]([^'\"]+)['\"]", instruction)
                        text = match.group(1) if match else ""

                    # 如果仍然失败，尝试更灵活的中文格式
                    if not text:
                        # 中文格式2："输入文本 'Hello'" - 忽略"文本"这个词
                        match = re.search(r"输入(?:文本)?\s*['\"]([^'\"]+)['\"]", instruction)
                        text = match.group(1) if match else ""

                    # 如果仍然没有文本，尝试没有引号的格式
                    if not text:
                        # 尝试："在...输入..." 格式
                        match = re.search(r"输入\s*['\"]?([^'\"\s]+)['\"]?", instruction)
                        if match:
                            text = match.group(1)

                    # 提取目标元素
                    target = instruction

                    # 英文格式目标提取
                    if "into" in target.lower():
                        target = target.lower().split("into")[1].strip()
                    elif "in" in target.lower():
                        target = target.lower().split("in")[1].strip()
                    elif "on" in target.lower():
                        target = target.lower().split("on")[1].strip()

                    # 中文格式目标提取
                    if "搜索" in instruction or "search" in instruction.lower():
                        if not any(keyword in target.lower() for keyword in ["into", "in", "on", "输入"]):
                            target = "search box" if not text else target
                    elif "输入" in instruction:
                        # 提取"在"和"输入"之间的内容作为目标
                        match = re.search(r"在([^输入]+)输入", instruction)
                        if match:
                            target = match.group(1).strip()
                            # 清理目标描述
                            if "搜索框" in target:
                                target = "search box"
                            elif "搜索栏" in target:
                                target = "search bar"
                            elif "输入框" in target:
                                target = "input field"

                    # 如果目标仍然包含"输入"相关的词，尝试提取更合适的描述
                    if "输入" in target or "input" in target.lower():
                        if "搜索" in instruction:
                            target = "search box"

                    # 如果目标是空的，尝试智能猜测
                    if not target or target.strip() == "" or "输入" in target:
                        if "搜索" in instruction:
                            target = "search box"
                        else:
                            target = "input field"

                    print(f"\n⌨️ 执行输入: '{text}' 到 {target}")
                    result = await self.session.call_tool("midscene_aiInput", {
                        "value": text,
                        "locate": target
                    })
                    print(f"\n📦 MCP 工具返回结果 [⌨️ 输入]:")
                    print(f"   {result}")
                    return result
                elif "scroll" in instruction.lower() or "滚动" in instruction:
                    # 支持英文 "scroll" 和中文 "滚动"
                    direction = "down"
                    if ("down" in instruction.lower() or "下" in instruction):
                        direction = "down"
                    elif ("up" in instruction.lower() or "上" in instruction):
                        direction = "up"
                    print(f"\n📜 执行滚动: {direction}")
                    result = await self.session.call_tool("midscene_aiScroll", {
                        "direction": direction,
                        "scrollType": "once"
                    })
                    print(f"\n📦 MCP 工具返回结果 [📜 滚动]:")
                    print(f"   {result}")
                    return result
                elif ("按" in instruction and ("键" in instruction or "enter" in instruction.lower() or "return" in instruction.lower())):
                    # 识别键盘按键操作，如"按回车键"、"按Enter键"
                    key_name = "Enter"
                    # 提取按键名称
                    if "回车" in instruction:
                        key_name = "Enter"
                    elif "空格" in instruction or "space" in instruction.lower():
                        key_name = " "
                    elif "tab" in instruction.lower():
                        key_name = "Tab"
                    elif "esc" in instruction.lower():
                        key_name = "Escape"

                    print(f"\n⌨️ 执行按键: {key_name}")
                    result = await self.session.call_tool("midscene_aiKeyboardPress", {
                        "key": key_name
                    })
                    print(f"\n📦 MCP 工具返回结果 [⌨️ 按键]:")
                    print(f"   {result}")
                    return result
                else:
                    # 默认：对于未分类的操作，使用 aiAssert 进行验证（不执行操作）
                    print(f"\n⚠️ 无法识别的操作指令: {instruction}")
                    print("💡 支持的操作类型:")
                    print("   - 导航: 'navigate to' / '导航到' + URL")
                    print("   - 点击: 'click' / '点击' / '按' + 目标元素")
                    print("   - 输入: 'input' / 'type' / '输入' + 文本内容")
                    print("   - 滚动: 'scroll' / '滚动' + 'up'/'down'/'上'/'下'")
                    print("   - 按键: '按' + '回车键'/'空格键'/'Tab键'")
                    print(f"\n✅ 执行验证: {instruction[:100]}...")
                    result = await self.session.call_tool("midscene_aiAssert", {
                        "assertion": f"验证页面状态: {instruction}"
                    })
                    print(f"\n📦 MCP 工具返回结果 [✅ 验证]:")
                    print(f"   {result}")
                    return result

            elif tool_name in ("query", "midscene_query"):
                question = arguments.get("question", "") if arguments else ""

                # 优先尝试使用专门的查询工具
                try:
                    # 使用 aiAssert 进行信息提取
                    print(f"\n🔍 执行查询: {question[:100]}...")
                    result = await self.session.call_tool("midscene_aiAssert", {
                        "assertion": question
                    })
                    print(f"\n📦 MCP 工具返回结果 [🔍 查询]:")
                    print(f"   {result}")
                    return result
                except Exception as e:
                    print(f"⚠️ aiAssert 查询失败，尝试其他方法: {e}")

                    # 备用方案：使用截图 + 查询
                    try:
                        # 先截图
                        print(f"\n📸 执行查询 (策略2): 截图 + AI分析")
                        screenshot_result = await self.session.call_tool("midscene_screenshot", {
                            "name": "query_screenshot"
                        })
                        print(f"✅ 截图完成")

                        # 使用更详细的查询指令
                        detailed_query = f"{question}\n\n请仔细分析页面截图，提取准确的信息。"
                        result = await self.session.call_tool("midscene_aiAssert", {
                            "assertion": detailed_query
                        })
                        print(f"\n📦 MCP 工具返回结果 [🔍 查询 - 重试]:")
                        print(f"   {result}")
                        return result
                    except Exception as e2:
                        print(f"⚠️ 所有查询方法都失败: {e2}")
                        raise RuntimeError(f"无法执行查询 '{question}': {e2}")

            else:
                # 直接工具调用
                result = await self.session.call_tool(tool_name, arguments or {})
                print(f"\n📦 MCP 工具返回结果 [{tool_name}]:")
                print(f"   {result}")
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
