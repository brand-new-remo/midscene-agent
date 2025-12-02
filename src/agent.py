"""
LangGraph Agent 与 Midscene 集成

本模块实现了一个基于 LangGraph 的智能体，使用 DeepSeek LLM
进行推理，使用 Midscene 进行网页自动化。
"""

import asyncio
import sys
from typing import List, Dict, Any, Optional, AsyncGenerator, Literal
from langchain_core.tools import BaseTool, tool
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from pydantic import SecretStr

# Import mcp_wrapper from the same directory
from mcp_wrapper import MidsceneMCPWrapper


def create_midscene_action_tool(mcp_wrapper: MidsceneMCPWrapper) -> BaseTool:
    """
    为 Midscene 操作执行创建 LangChain 工具。

    Args:
        mcp_wrapper: Midscene MCP 包装器实例

    Returns:
        用于执行网页操作的 LangChain BaseTool
    """

    @tool
    async def midscene_action(instruction: str) -> str:
        """
        使用 Midscene 的 AI 能力执行浏览器操作。

        该工具允许使用自然语言指令与网页进行交互。
        Midscene 将分析页面状态并执行请求的操作。

        Args:
            instruction: 要执行的清晰自然语言描述。
                        示例：
                        - "点击登录按钮"
                        - "在搜索框中输入 'hello world'"
                        - "向下滚动查看更多内容"
                        - "导航到 https://www.google.com"
                        - "填写表单 name='John Doe' 和 email='john@example.com'"

        Returns:
            详细描述执行内容和观察结果
        """
        try:
            result = await mcp_wrapper.call_tool("action", {"instruction": instruction})
            if hasattr(result, 'content') and result.content:
                # Extract text from TextContent array
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if hasattr(first_item, 'text'):
                        return first_item.text
                    else:
                        return str(first_item)
                else:
                    return str(content)
            return "操作执行成功"
        except Exception as e:
            return f"执行操作时出错: {str(e)}"

    return midscene_action


def create_midscene_query_tool(mcp_wrapper: MidsceneMCPWrapper) -> BaseTool:
    """
    为 Midscene 查询和信息提取创建 LangChain 工具。

    Args:
        mcp_wrapper: Midscene MCP 包装器实例

    Returns:
        用于查询页面信息的 LangChain BaseTool
    """

    @tool
    async def midscene_query(question: str) -> str:
        """
        使用 Midscene 的 AI 从当前网页提取信息。

        询问页面上可见的内容，Midscene 将分析截图并提供答案。

        Args:
            question: 关于页面内容的问题。
                     示例：
                     - "这个页面的标题是什么？"
                     - "列出所有导航菜单项"
                     - "显示的产品价格是多少？"
                     - "从页面中提取联系信息"
                     - "页面上可见哪些按钮或链接？"

        Returns:
            提取的信息或问题的答案
        """
        try:
            result = await mcp_wrapper.call_tool("query", {"question": question})
            if hasattr(result, 'content') and result.content:
                # Extract text from TextContent array
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if hasattr(first_item, 'text'):
                        return first_item.text
                    else:
                        return str(first_item)
                else:
                    return str(content)
            return "查询执行成功"
        except Exception as e:
            return f"执行查询时出错: {str(e)}"

    return midscene_query


class MidsceneAgent:
    """
    用于 AI 驱动网页自动化的 LangGraph Agent。

    该智能体结合了：
    - DeepSeek LLM 用于推理和决策
    - Midscene 用于视觉驱动的网页交互
    - LangGraph 用于状态管理和执行流程
    """

    def __init__(
        self,
        deepseek_api_key: str,
        deepseek_base_url: str = "https://api.deepseek.com/v1",
        deepseek_model: str = "deepseek-chat",
        temperature: float = 0,
        midscene_command: str = "npx",
        midscene_args: Optional[List[str]] = None,
        env: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 Midscene 智能体。

        Args:
            deepseek_api_key: DeepSeek 的 API 密钥
            deepseek_base_url: DeepSeek API 的基础 URL
            deepseek_model: 要使用的模型名称
            temperature: LLM 响应的温度参数
            midscene_command: 运行 Midscene MCP 服务器的命令
            midscene_args: Midscene 命令的参数
            env: 环境变量
        """
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_base_url = deepseek_base_url
        self.deepseek_model = deepseek_model
        self.temperature = temperature

        self.mcp_wrapper = MidsceneMCPWrapper(
            midscene_command=midscene_command,
            midscene_args=midscene_args,
            env=env
        )

        self.llm: Optional[Any] = None
        self.agent_executor: Optional[Any] = None

    async def initialize(self) -> None:
        """
        初始化 LLM 和智能体执行器。

        Raises:
            RuntimeError: 如果初始化失败
        """
        try:
            # 初始化 MCP 连接
            await self.mcp_wrapper.start()

            # 创建工具
            tools = [
                create_midscene_action_tool(self.mcp_wrapper),
                create_midscene_query_tool(self.mcp_wrapper)
            ]
            print(f"🔧 为智能体创建了 {len(tools)} 个工具")

            # 初始化 LLM（绑定工具）
            self.llm = ChatDeepSeek(
                model=self.deepseek_model,
                api_key=SecretStr(self.deepseek_api_key),
                base_url=self.deepseek_base_url,
                temperature=self.temperature,
                streaming=True
            ).bind_tools(tools)

            print(f"✅ 已初始化 DeepSeek LLM ({self.deepseek_model}) 并绑定工具")

            # 使用 StateGraph 创建智能体执行器
            from langgraph.prebuilt import ToolNode, tools_condition

            # 构建智能体图
            def agent_node(state: MessagesState) -> MessagesState:
                if self.llm is None:
                    raise RuntimeError("LLM 未初始化")
                print(f"\n🤖 Agent Node: Processing {len(state['messages'])} messages")
                for i, msg in enumerate(state["messages"]):
                    print(f"  Message {i}: {type(msg).__name__}")
                    if hasattr(msg, 'content'):
                        content = str(msg.content)[:100]
                        print(f"    Content: {content}...")
                response = self.llm.invoke(state["messages"])
                print(f"\n💬 LLM Response: {type(response).__name__}")
                if hasattr(response, 'content'):
                    print(f"  Content: {response.content}")
                if hasattr(response, 'tool_calls'):
                    print(f"  Tool calls: {len(response.tool_calls) if response.tool_calls else 0}")
                return {"messages": state["messages"] + [response]}

            # 创建图
            builder = StateGraph(MessagesState)
            builder.add_node("agent", agent_node)
            builder.add_node("tools", ToolNode(tools))
            builder.add_edge(START, "agent")
            builder.add_conditional_edges(
                "agent",
                tools_condition,
                {"tools": "tools", "__end__": END}
            )
            builder.add_edge("tools", "agent")

            self.agent_executor = builder.compile()
            print("✅ 智能体执行器已初始化")

        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"初始化智能体失败: {e}")

    async def execute(self, user_input: str, stream: bool = True) -> AsyncGenerator:
        """
        使用智能体执行任务。

        Args:
            user_input: 任务的自然语言指令
            stream: 是否流式传输响应

        Yields:
            智能体执行的事件

        Raises:
            RuntimeError: 如果智能体未初始化
        """
        if not self.agent_executor:
            raise RuntimeError("智能体未初始化。请先调用 initialize()。")

        print(f"\n🚀 开始执行智能体")
        print(f"📝 任务: {user_input}\n")

        try:
            # 为 LangChain 1.0+ 使用 HumanMessage
            input_messages = {"messages": [HumanMessage(content=user_input)]}

            if stream:
                async for chunk in self.agent_executor.astream(input_messages):
                    # Yield each chunk as an event
                    yield chunk
            else:
                result = await self.agent_executor.ainvoke(input_messages)
                yield result
        except Exception as e:
            import traceback
            yield {"error": str(e), "traceback": traceback.format_exc()}

    async def cleanup(self) -> None:
        """清理资源。"""
        if self.mcp_wrapper:
            await self.mcp_wrapper.stop()

    async def __aenter__(self):
        """异步上下文管理器入口。"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口。"""
        await self.cleanup()

