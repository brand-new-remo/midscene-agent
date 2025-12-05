"""
Midscene Agent，使用 HTTP 客户端替代 MCP stdio

基于 LangGraph 的智能体，使用 DeepSeek LLM 进行推理，
通过 HTTP 协议与 Node.js Midscene 服务通信，
实现更稳定、功能更完整的网页自动化。
"""

import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from langchain_core.tools import BaseTool, tool
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr
from .http_client import (
    MidsceneHTTPClient,
    SessionConfig,
    MidsceneConnectionError,
)
from .tools.definitions import (
    get_tool_definition,
    TOOL_DEFINITIONS,
    get_recommended_tool_set,
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MidsceneAgent:
    """
    Midscene Agent，使用 HTTP 客户端与 Node.js 服务通信

    功能：
    1. 更稳定的 HTTP 通信
    2. 支持 WebSocket 流式响应
    3. 更好的错误处理和重试机制
    4. 利用完整的 Midscene.js 功能
    5. 原生支持会话管理和复用
    """

    def __init__(
        self,
        deepseek_api_key: str,
        deepseek_base_url: str = "https://api.deepseek.com/v1",
        deepseek_model: str = "deepseek-chat",
        temperature: float = 0,
        midscene_server_url: str = "http://localhost:3000",
        midscene_config: Optional[Dict[str, Any]] = None,
        tool_set: str = "full",
        enable_websocket: bool = True,
        timeout: int = 300,
    ):
        """
        初始化新版 Midscene Agent

        Args:
            deepseek_api_key: DeepSeek API 密钥
            deepseek_base_url: DeepSeek API 基础 URL
            deepseek_model: DeepSeek 模型名称
            temperature: LLM 温度参数
            midscene_server_url: Node.js Midscene 服务器地址
            midscene_config: Midscene 配置
            tool_set: 工具集选择：'basic'、'advanced'、'full'
            enable_websocket: 是否启用 WebSocket 流式响应
            timeout: 操作超时时间（秒）
        """
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_base_url = deepseek_base_url
        self.deepseek_model = deepseek_model
        self.temperature = temperature
        self.midscene_server_url = midscene_server_url
        self.midscene_config = midscene_config or {}
        self.tool_set = tool_set
        self.enable_websocket = enable_websocket
        self.timeout = timeout

        # 初始化 HTTP 客户端
        self.http_client = MidsceneHTTPClient(base_url=midscene_server_url)

        # 内部状态
        self.llm: Optional[Any] = None
        self.agent_executor: Optional[Any] = None
        self.tools: List[BaseTool] = []
        self.initialized = False

        logger.info("Midscene Agent initialized")

    async def initialize(self) -> None:
        """
        初始化智能体

        1. 创建 HTTP 客户端会话
        2. 创建 Midscene 会话
        3. 初始化 LLM
        4. 创建 LangGraph 执行器
        """
        try:
            logger.info("🚀 正在初始化 Midscene Agent...")

            # 1. 启动 HTTP 客户端
            logger.info("📡 启动 HTTP 客户端...")
            await self.http_client.connect()

            # 2. 健康检查
            logger.info("🔍 检查服务器健康状态...")
            health = await self.http_client.health_check()
            if health.get("status") not in ("ok", "healthy"):
                raise MidsceneConnectionError(f"服务器不健康: {health}")

            # 3. 创建 Midscene 会话
            logger.info("🌐 创建 Midscene 会话...")
            session_config = SessionConfig(
                model=self.midscene_config.get("model", "doubao-seed-1.6-vision"),
                base_url=self.midscene_config.get("base_url"),
                api_key=self.midscene_config.get("api_key"),
                headless=self.midscene_config.get("headless", True),
                viewport_width=self.midscene_config.get("viewport_width", 1920),
                viewport_height=self.midscene_config.get("viewport_height", 1080),
            )

            await self.http_client.create_session(session_config)

            # 4. 连接 WebSocket（如果启用）
            if self.enable_websocket:
                logger.info("🔌 连接 WebSocket...")
                connected = await self.http_client.connect_websocket()
                if connected:
                    logger.info("✅ WebSocket 连接成功")
                else:
                    logger.warning("⚠️ WebSocket 连接失败，使用 HTTP 模式")

            # 5. 创建工具
            logger.info(f"🔧 创建工具集: {self.tool_set}")
            self.tools = await self._create_tools()
            logger.info(f"✅ 创建了 {len(self.tools)} 个工具")

            # 6. 初始化 LLM
            logger.info("🤖 初始化 DeepSeek LLM...")
            self.llm = ChatDeepSeek(
                model=self.deepseek_model,
                api_key=SecretStr(self.deepseek_api_key),
                base_url=self.deepseek_base_url,
                temperature=self.temperature,
                streaming=True,
            ).bind_tools(self.tools)

            # 7. 创建 LangGraph 执行器
            logger.info("🔄 构建 LangGraph 执行器...")
            self.agent_executor = await self._build_graph()

            self.initialized = True
            logger.info("✅ Midscene Agent 初始化完成")

        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            await self.cleanup()
            raise RuntimeError(f"初始化智能体失败: {e}")

    async def _create_tools(self) -> List[BaseTool]:
        """创建 LangChain 工具"""
        tools = []

        # 获取要创建的工具列表
        if self.tool_set == "full":
            tool_names = list(TOOL_DEFINITIONS.keys())
        else:
            tool_names = get_recommended_tool_set(self.tool_set)

        # 为每个工具创建包装器
        for tool_name in tool_names:
            tool_def = get_tool_definition(tool_name)
            if not tool_def:
                logger.warning(f"⚠️ 跳过未定义的工具: {tool_name}")
                continue

            langchain_tool = await self._create_langchain_tool(tool_name, tool_def)
            if langchain_tool:
                tools.append(langchain_tool)

        return tools

    async def _create_langchain_tool(
        self, tool_name: str, tool_def: Dict[str, Any]
    ) -> BaseTool:
        """创建单个 LangChain 工具"""

        # 提取工具信息
        description = tool_def.get("description", "")
        params = tool_def.get("params", {})
        category = tool_def.get("category", "")

        # 构建参数文档
        param_docs = []
        for param_name, param_desc in params.items():
            optional = param_name.endswith("?")
            clean_name = param_name.rstrip("?")
            param_docs.append(
                f"    {clean_name}: {param_desc}" + (" (可选)" if optional else "")
            )

        full_description = f"""{description}

参数:
{chr(10).join(param_docs)}

分类: {category}"""

        # 使用 @tool 装饰器创建工具
        @tool
        async def midscene_tool_wrapper(**kwargs):
            """Midscene 工具包装器"""
            try:
                # 直接使用 Midscene 官方 API 名称
                # 移除映射，使用工具名直接作为 API 调用名
                midscene_api_name = tool_name.replace("midscene_", "")

                logger.info(f"🔧 执行工具: {tool_name}, 参数: {kwargs}")

                # 动作类 API - 通过 executeAction 调用
                action_apis = {
                    "navigate", "aiTap", "aiDoubleClick", "aiRightClick",
                    "aiInput", "aiScroll", "aiKeyboardPress", "aiHover",
                    "aiWaitFor", "aiAction", "setActiveTab",
                    "evaluateJavaScript", "logScreenshot", "freezePageContext",
                    "unfreezePageContext", "runYaml", "setAIActionContext"
                }

                # 查询类 API - 通过 executeQuery 调用
                query_apis = {
                    "aiAssert", "aiAsk", "aiQuery", "aiBoolean", "aiNumber", "aiString",
                    "aiLocate", "getTabs", "getConsoleLogs", "playwrightExample"
                }

                if midscene_api_name in action_apis:
                    # 动作操作
                    async for event in self.http_client.execute_action(
                        midscene_api_name, kwargs, stream=self.enable_websocket
                    ):
                        if "error" in event:
                            logger.error(f"工具执行错误: {event['error']}")
                            return f"执行失败: {event['error']}"
                        elif "result" in event:
                            result = event["result"]
                            break
                    else:
                        result = "执行完成"
                elif midscene_api_name in query_apis:
                    # 查询操作
                    result = await self.http_client.execute_query(
                        midscene_api_name, kwargs
                    )
                else:
                    return f"未知的工具: {tool_name}"

                logger.info(f"✅ 工具执行成功: {tool_name}")
                return result

            except Exception as e:
                error_msg = f"工具 '{tool_name}' 执行错误: {str(e)}"
                logger.error(error_msg)
                return error_msg

        # 设置工具属性
        midscene_tool_wrapper.name = tool_name
        midscene_tool_wrapper.description = full_description
        midscene_tool_wrapper.args_schema = self._generate_pydantic_model(
            tool_name, params
        )

        return midscene_tool_wrapper

    def _generate_pydantic_model(self, tool_name: str, params: Dict):
        """生成 Pydantic 模型"""
        from pydantic import BaseModel, Field
        from typing import Optional

        fields = {}
        annotations = {}

        for param_name, param_desc in params.items():
            optional = param_name.endswith("?")
            clean_name = param_name.rstrip("?")

            field_type = Optional[str] if optional else str
            default = None if optional else ...

            annotations[clean_name] = field_type
            fields[clean_name] = Field(default=default, description=param_desc)

        model_name = f"{tool_name.replace('midscene_', '').title()}Model"
        namespace = {**fields, "__annotations__": annotations}

        return type(model_name, (BaseModel,), namespace)

    async def _build_graph(self):
        """构建 LangGraph 执行器"""

        def agent_node(state: MessagesState) -> MessagesState:
            if self.llm is None:
                raise RuntimeError("LLM 未初始化")

            response = self.llm.invoke(state["messages"])

            # 记录工具调用
            if hasattr(response, "tool_calls") and response.tool_calls:
                logger.info(f"💬 LLM 调用了 {len(response.tool_calls)} 个工具")
                for tool_call in response.tool_calls:
                    logger.info(f"  - {tool_call['name']}: {tool_call['args']}")

            return {"messages": state["messages"] + [response]}

        builder = StateGraph(MessagesState)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", ToolNode(self.tools))
        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent", tools_condition, {"tools": "tools", "__end__": END}
        )
        builder.add_edge("tools", "agent")

        return builder.compile(interrupt_before=[], interrupt_after=[])

    async def execute(self, user_input: str, stream: bool = True) -> AsyncGenerator:
        """
        执行任务

        Args:
            user_input: 任务的自然语言指令
            stream: 是否流式传输响应

        Yields:
            智能体执行的事件

        Raises:
            RuntimeError: 如果智能体未初始化
        """
        if not self.initialized or not self.agent_executor:
            raise RuntimeError("智能体未初始化。请先调用 initialize()。")

        logger.info(f"\n🚀 开始执行任务")
        logger.info(f"📝 任务: {user_input}\n")

        try:
            input_messages = {"messages": [HumanMessage(content=user_input)]}
            config = {"recursion_limit": 100}

            if stream:
                async for chunk in self.agent_executor.astream(
                    input_messages, config=config
                ):
                    yield chunk
            else:
                result = await self.agent_executor.ainvoke(
                    input_messages, config=config
                )
                yield result

        except Exception as e:
            import traceback

            error_msg = f"执行任务失败: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            yield {"error": error_msg, "traceback": traceback.format_exc()}

    async def take_screenshot(self, **kwargs) -> Dict[str, Any]:
        """截取屏幕截图的便捷方法（使用 logScreenshot API）"""
        # 使用 logScreenshot action
        title = kwargs.get("name", "screenshot")
        options = {
            "fullPage": kwargs.get("fullPage", False),
            "content": kwargs.get("content")
        }

        async for event in self.http_client.execute_action(
            "logScreenshot", {"title": title, "options": options}, stream=False
        ):
            if "result" in event:
                return event["result"]
            elif "error" in event:
                raise RuntimeError(f"截图失败: {event['error']}")

        return {"success": True}

    async def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        sessions = await self.http_client.get_sessions()
        history = await self.http_client.get_session_history()
        return {"active_sessions": sessions, "session_history": history}

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return await self.http_client.health_check()

    async def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.http_client:
                await self.http_client.cleanup()
                logger.info("🔌 HTTP 客户端已清理")
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")

        self.initialized = False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()


class MidsceneAgentError(Exception):
    """Midscene Agent 错误"""

    pass
