"""
MidsceneAgent CLI 适配器

这个模块将 MidsceneAgent 适配为 LangGraph CLI 标准接口，
处理消息流转换和会话生命周期管理。
"""

from typing import Any, AsyncGenerator, Dict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from runner.agent.agent import MidsceneAgent
from runner.agent.config import Config
from runner.agent.http_client import SessionConfig

logger = __import__("logging").getLogger(__name__)


class MidsceneAgentAdapter:
    """
    MidsceneAgent 适配器

    职责：
    1. 包装 MidsceneAgent，提供 LangGraph 标准接口
    2. 处理消息流转换（流式响应 → LangGraph 消息）
    3. 管理会话生命周期
    """

    def __init__(self):
        """初始化适配器"""
        # 直接使用 Config 类属性（不需要实例化）
        self.config = Config

        # 初始化 MidsceneAgent
        self.agent = MidsceneAgent(
            deepseek_api_key=self.config.DEEPSEEK_API_KEY,
            deepseek_base_url=self.config.DEEPSEEK_BASE_URL,
            deepseek_model=self.config.DEEPSEEK_MODEL,
            temperature=0,
            midscene_server_url=self.config.MIDSCENE_SERVER_URL,
            tool_set="full",
            enable_websocket=True,
            timeout=300,
        )

        # 活跃会话池
        self.active_sessions: set[str] = set()

        # 最大并发会话数
        self.max_sessions = 50

        logger.info("🔧 MidsceneAgent 适配器初始化完成")

    async def process(self, state: Dict[str, Any]) -> AsyncGenerator[BaseMessage, None]:
        """
        处理 LangGraph 消息流

        Args:
            state: LangGraph 状态（包含 messages）

        Yields:
            BaseMessage: 转换后的消息

        Raises:
            RuntimeError: 当会话数超限时
        """
        # 检查会话数限制
        if len(self.active_sessions) >= self.max_sessions:
            error_msg = f"活跃会话数已达上限 ({self.max_sessions})"
            logger.error(error_msg)
            yield AIMessage(content=f"❌ {error_msg}")
            return

        # 获取最新用户消息
        if not state.get("messages"):
            yield AIMessage(content="❌ 未收到用户消息")
            return

        user_message = state["messages"][-1]
        if not isinstance(user_message, HumanMessage):
            yield AIMessage(content="❌ 只支持 HumanMessage")
            return

        user_input = user_message.content
        # 类型转换：确保 user_input 是字符串类型
        if isinstance(user_input, list):
            # 如果是列表，取第一个元素作为输入
            user_input = str(user_input[0]) if user_input else ""
        else:
            user_input = str(user_input)
        logger.info(f"📝 收到用户输入: {user_input[:100]}...")

        # 创建 Midscene 会话
        session_id = await self._create_session()
        self.active_sessions.add(session_id)

        try:
            # 初始化 MidsceneAgent（如果尚未初始化）
            if not self.agent.initialized:
                await self.agent.initialize()
                logger.info("✅ MidsceneAgent 初始化完成")

            # 执行用户输入
            async for chunk in self._execute(user_input, session_id):
                # 转换为 LangGraph 标准消息格式
                if isinstance(chunk, dict):
                    if "error" in chunk and isinstance(chunk.get("error"), str):
                        yield AIMessage(content=f"❌ {chunk.get('error')}")
                    else:
                        yield AIMessage(content=str(chunk))
                else:
                    yield AIMessage(content=str(chunk))

        except Exception as e:
            error_msg = f"❌ 执行失败: {str(e)}"
            logger.error(f"{error_msg}\n{__import__('traceback').format_exc()}")
            yield AIMessage(content=error_msg)

        finally:
            # 清理会话
            await self._cleanup_session(session_id)
            self.active_sessions.discard(session_id)
            logger.info(f"🧹 会话已清理: {session_id}")

    async def _create_session(self) -> str:
        """
        创建 Midscene 会话

        Returns:
            会话 ID

        Raises:
            RuntimeError: 如果创建会话失败
        """
        try:
            # 确保 HTTP 客户端已连接
            if not self.agent.http_client.session:
                await self.agent.http_client.connect()

            # 创建会话配置
            session_config = SessionConfig(
                headless=True,
                viewport_width=1920,
                viewport_height=1080,
            )

            # 创建会话
            session_id = await self.agent.http_client.create_session(session_config)

            logger.info(f"✅ 创建 Midscene 会话: {session_id}")
            return session_id

        except Exception as e:
            error_msg = f"创建会话失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def _cleanup_session(self, session_id: str):
        """
        清理 Midscene 会话

        Args:
            session_id: 会话 ID
        """
        try:
            if self.agent.http_client.session and session_id:
                # 删除会话
                delete_url = (
                    f"{self.agent.http_client.base_url}/api/sessions/{session_id}"
                )
                async with self.agent.http_client.session.delete(
                    delete_url
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ 删除会话成功: {session_id}")
                    else:
                        logger.warning(
                            f"⚠️ 删除会话失败 ({response.status}): {session_id}"
                        )
        except Exception as e:
            logger.error(f"清理会话时出错 {session_id}: {str(e)}")

    async def _execute(
        self, user_input: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        执行用户输入

        Args:
            user_input: 用户输入
            session_id: 会话 ID

        Yields:
            str: 执行结果的文本片段
        """
        try:
            # 调用 MidsceneAgent 执行任务
            async for chunk in self.agent.execute(user_input, stream=True):
                # 提取 chunk 中的内容
                if isinstance(chunk, dict):
                    # 处理来自 agent_executor.astream 的响应
                    if "messages" in chunk:
                        # 获取最新的 AI 消息
                        messages = chunk.get("messages", [])
                        if messages:
                            last_message = messages[-1]
                            if hasattr(last_message, "content"):
                                yield str(last_message.content)
                            else:
                                yield str(last_message)
                    elif "agent" in chunk:
                        # 处理 agent 节点输出
                        agent_output = chunk.get("agent", {})
                        if "messages" in agent_output:
                            for msg in agent_output["messages"]:
                                yield (
                                    str(msg.content)
                                    if hasattr(msg, "content")
                                    else str(msg)
                                )
                    else:
                        yield str(chunk)
                else:
                    yield str(chunk)

        except Exception as e:
            error_msg = f"执行失败: {str(e)}"
            logger.error(error_msg)
            yield error_msg
