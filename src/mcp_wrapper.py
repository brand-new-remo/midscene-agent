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
        直接调用指定的 Midscene MCP 工具。

        Args:
            tool_name: MCP 工具名称（如 'midscene_navigate', 'midscene_aiTap' 等）
            arguments: 传递给工具的参数

        Returns:
            MCP 工具的结果

        Raises:
            RuntimeError: 如果未连接或工具调用失败
        """
        if not self.session:
            raise RuntimeError("未连接到 Midscene MCP 服务器")

        try:
            print(f"\n🔧 调用工具: {tool_name}")
            if arguments:
                print(f"参数: {json.dumps(arguments, indent=2, ensure_ascii=False)}")

            result = await self.session.call_tool(tool_name, arguments or {})

            print(f"\n📦 MCP 工具返回结果:")
            if hasattr(result, 'content'):
                if isinstance(result.content, list):
                    for item in result.content:
                        try:
                            # 尝试获取文本内容
                            text = getattr(item, 'text', None)
                            if text is not None:
                                print(f"   {text}")
                            else:
                                print(f"   {item}")
                        except Exception:
                            print(f"   {item}")
                else:
                    print(f"   {result.content}")
            else:
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

    async def create_langchain_tool(
        self,
        mcp_tool_name: str,
        langchain_tool_name: Optional[str] = None
    ):
        """
        将 MCP 工具包装为 LangChain 工具。

        Args:
            mcp_tool_name: MCP 工具名称
            langchain_tool_name: 可选的 LangChain 工具名称，默认与 MCP 工具名相同

        Returns:
            LangChain BaseTool 实例
        """
        from langchain_core.tools import tool
        from .tools.definitions import get_tool_definition

        if langchain_tool_name is None:
            langchain_tool_name = mcp_tool_name

        # 获取工具定义
        tool_def = get_tool_definition(mcp_tool_name)
        if not tool_def:
            raise ValueError(f"未找到工具定义: {mcp_tool_name}")

        # 生成工具描述
        description = tool_def.get("description", "")
        params = tool_def.get("params", {})
        category = tool_def.get("category", "")

        # 构建参数文档
        param_docs = []
        for param_name, param_desc in params.items():
            optional = param_name.endswith("?")
            clean_name = param_name.rstrip("?")
            param_docs.append(f"    {clean_name}: {param_desc}{' (可选)' if optional else ''}")

        # 完整的工具描述
        full_description = f"""{description}

参数:
{chr(10).join(param_docs)}

分类: {category}"""

        # 使用 @tool 装饰器创建 LangChain 工具
        @tool
        async def langchain_tool_wrapper(**kwargs):
            """LangChain 工具包装器"""
            try:
                result = await self.call_tool(mcp_tool_name, kwargs)
                # 提取结果文本
                if hasattr(result, 'content'):
                    content = result.content
                    if isinstance(content, list) and len(content) > 0:
                        first_item = content[0]
                        text = getattr(first_item, 'text', None)
                        if text is not None:
                            return text
                        else:
                            return str(first_item)
                    else:
                        return str(content)
                return str(result)
            except Exception as e:
                return f"执行工具 '{mcp_tool_name}' 时出错: {str(e)}"

        # 设置工具属性
        langchain_tool_wrapper.name = langchain_tool_name
        langchain_tool_wrapper.description = full_description
        langchain_tool_wrapper.args_schema = self._generate_pydantic_model(
            mcp_tool_name, params
        )

        return langchain_tool_wrapper

    def _generate_pydantic_model(self, tool_name: str, params: Dict):
        """
        为工具参数生成 Pydantic 模型。

        Args:
            tool_name: 工具名称
            params: 参数定义字典

        Returns:
            Pydantic BaseModel 类
        """
        from pydantic import BaseModel, Field
        from typing import Optional

        # 构建字段定义和注解
        fields = {}
        annotations = {}
        for param_name, param_desc in params.items():
            optional = param_name.endswith("?")
            clean_name = param_name.rstrip("?")

            # 确定字段类型
            if optional:
                field_type = Optional[str]
                default = None
            else:
                field_type = str
                default = ...

            # 在 annotations 中设置类型
            annotations[clean_name] = field_type

            # 创建字段
            fields[clean_name] = Field(
                default=default,
                description=param_desc
            )

        # 动态创建模型类
        model_name = f"{tool_name.replace('midscene_', '').title()}Model"

        # 在创建类时同时设置字段和注解
        namespace = {**fields, "__annotations__": annotations}
        model_class = type(model_name, (BaseModel,), namespace)

        return model_class

    async def get_langchain_tools(
        self,
        tool_names: Optional[List[str]] = None,
        tool_set: Optional[str] = None
    ) -> List:
        """
        获取 LangChain 工具列表。

        Args:
            tool_names: 要创建的工具名称列表
            tool_set: 预定义的工具集名称（'basic'、'advanced'、'full'）

        Returns:
            LangChain 工具列表
        """
        from .tools.definitions import (
            get_all_tool_names,
            get_recommended_tool_set,
            TOOL_DEFINITIONS
        )

        # 确定要创建的工具列表
        if tool_set:
            tools_to_create = get_recommended_tool_set(tool_set)
            print(f"\n📦 使用预定义工具集: {tool_set} ({len(tools_to_create)} 个工具)")
        elif tool_names:
            tools_to_create = tool_names
        else:
            # 默认使用基础工具集
            tools_to_create = get_recommended_tool_set("basic")
            print(f"\n📦 使用默认工具集: basic ({len(tools_to_create)} 个工具)")

        # 验证工具是否存在
        available_tools = get_all_tool_names()
        for tool_name in tools_to_create:
            if tool_name not in available_tools:
                print(f"⚠️ 警告: 工具 '{tool_name}' 未在定义中找到，跳过")
                tools_to_create.remove(tool_name)

        # 创建工具实例
        tools = []
        for tool_name in tools_to_create:
            try:
                langchain_tool = await self.create_langchain_tool(tool_name)
                tools.append(langchain_tool)
                print(f"✅ 已创建工具: {tool_name}")
            except Exception as e:
                print(f"❌ 创建工具 '{tool_name}' 失败: {e}")

        print(f"\n✨ 总计创建了 {len(tools)} 个工具")
        return tools


class MidsceneConnectionError(Exception):
    """当连接到 Midscene MCP 服务器失败时抛出。"""
    pass


class MidsceneToolError(Exception):
    """当调用 Midscene 工具失败时抛出。"""
    pass
