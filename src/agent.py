"""
LangGraph Agent 与 Midscene 集成

本模块实现了一个基于 LangGraph 的智能体，使用 DeepSeek LLM
进行推理，使用 Midscene 进行网页自动化。
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from langchain_core.tools import BaseTool
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from pydantic import SecretStr
from .mcp_wrapper import MidsceneMCPWrapper


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
        env: Optional[Dict[str, Any]] = None,
        tool_set: str = "full",
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
            tool_set: 工具集选择：'basic'（基础）、'advanced'（高级）、'full'（完整）
        """
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_base_url = deepseek_base_url
        self.deepseek_model = deepseek_model
        self.temperature = temperature
        self.tool_set = tool_set

        self.mcp_wrapper = MidsceneMCPWrapper(
            midscene_command=midscene_command, midscene_args=midscene_args, env=env
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

            # 使用新的工具系统获取工具
            print(f"\n🔧 正在创建工具集: {self.tool_set}")
            tools = await self.mcp_wrapper.get_langchain_tools(tool_set=self.tool_set)
            print(f"✅ 为智能体创建了 {len(tools)} 个工具")

            # 初始化 LLM（绑定工具）
            self.llm = ChatDeepSeek(
                model=self.deepseek_model,
                api_key=SecretStr(self.deepseek_api_key),
                base_url=self.deepseek_base_url,
                temperature=self.temperature,
                streaming=True,
            ).bind_tools(tools)

            print(f"\n✅ 已初始化 DeepSeek LLM ({self.deepseek_model}) 并绑定 {len(tools)} 个工具")

            # 使用 StateGraph 创建智能体执行器
            from langgraph.prebuilt import ToolNode, tools_condition

            # 构建智能体图
            def agent_node(state: MessagesState) -> MessagesState:
                if self.llm is None:
                    raise RuntimeError("LLM 未初始化")

                # 简化的日志输出：只显示消息数量和工具调用
                num_messages = len(state['messages'])
                # print(f"🤖 Agent Node: {num_messages} messages")

                response = self.llm.invoke(state["messages"])

                # 只在有工具调用时显示详细信息
                if hasattr(response, "tool_calls") and response.tool_calls:
                    print(f"💬 LLM Response: {response.content}")
                    # print(f"🔧 Tool calls: {len(response.tool_calls)}")
                elif hasattr(response, "content") and response.content:
                    # 显示非工具调用的响应内容（截断）
                    content = str(response.content)
                    if len(content) > 100:
                        print(f"💬 LLM Response: {content[:100]}...")
                    else:
                        print(f"💬 LLM Response: {content}")

                return {"messages": state["messages"] + [response]}

            # 创建图
            builder = StateGraph(MessagesState)
            builder.add_node("agent", agent_node)
            builder.add_node("tools", ToolNode(tools))
            builder.add_edge(START, "agent")
            builder.add_conditional_edges(
                "agent", tools_condition, {"tools": "tools", "__end__": END}
            )
            builder.add_edge("tools", "agent")

            self.agent_executor = builder.compile(
                interrupt_before=[], interrupt_after=[]  # 可选：中断点  # 可选：中断点
            )
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

            # 配置最大递归次数以避免循环
            config = {"recursion_limit": 100}

            if stream:
                async for chunk in self.agent_executor.astream(
                    input_messages, config=config
                ):
                    # Yield each chunk as an event
                    yield chunk
            else:
                result = await self.agent_executor.ainvoke(
                    input_messages, config=config
                )
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
