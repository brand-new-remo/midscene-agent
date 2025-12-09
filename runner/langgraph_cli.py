"""
LangGraph CLI 适配层

这个模块将现有的 MidsceneAgent 适配为 LangGraph CLI 兼容的格式，
支持通过 Agent Chat UI 进行自然语言对话。

使用方法:
    langgraph dev
    # 访问 http://localhost:2024 使用 Agent Chat UI
"""

from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, AIMessage
from agent.cli_adapter import MidsceneAgentAdapter

logger = __import__("logging").getLogger(__name__)


def create_midscene_graph():
    """
    创建 LangGraph CLI 兼容的编译图

    返回:
        CompiledStateGraph: 可执行的 LangGraph 图
    """
    logger.info("🔧 创建 Midscene LangGraph 图...")

    # 创建适配器
    adapter = MidsceneAgentAdapter()

    # 构建状态图
    workflow = StateGraph(MessagesState)

    # 添加节点：创建符合 LangGraph 规范的节点函数
    async def midscene_node(state: MessagesState) -> MessagesState:
        """
        LangGraph 节点函数：处理 Midscene 任务

        Args:
            state: LangGraph 消息状态

        Returns:
            更新后的消息状态
        """
        # 获取最新用户消息
        if not state.get("messages"):
            return {
                "messages": [AIMessage(content="❌ 未收到用户消息")]
            }

        user_message = state["messages"][-1]
        if not isinstance(user_message, HumanMessage):
            return {
                "messages": state["messages"] + [AIMessage(content="❌ 只支持 HumanMessage")]
            }

        user_input = str(user_message.content)
        logger.info(f"📝 收到用户输入: {user_input[:100]}...")

        # 创建 Midscene 会话
        session_id = await adapter._create_session()
        adapter.active_sessions.add(session_id)

        try:
            # 初始化 MidsceneAgent（如果尚未初始化）
            if not adapter.agent.initialized:
                await adapter.agent.initialize()
                logger.info("✅ MidsceneAgent 初始化完成")

            # 执行用户输入并收集结果
            all_outputs = []
            async for chunk in adapter._execute(user_input, session_id):
                if isinstance(chunk, dict):
                    if "error" in chunk:
                        all_outputs.append(f"❌ {chunk.get('error')}")
                    else:
                        all_outputs.append(str(chunk))
                else:
                    all_outputs.append(str(chunk))

            # 返回包含 AI 响应的状态
            response_message = "\n".join(all_outputs) if all_outputs else "执行完成"
            return {
                "messages": state["messages"] + [AIMessage(content=response_message)]
            }

        except Exception as e:
            error_msg = f"❌ 执行失败: {str(e)}"
            logger.error(f"{error_msg}\n{__import__('traceback').format_exc()}")
            return {
                "messages": state["messages"] + [AIMessage(content=error_msg)]
            }

        finally:
            # 清理会话
            try:
                await adapter._cleanup_session(session_id)
            except Exception as e:
                logger.error(f"清理会话时出错: {e}")
            finally:
                adapter.active_sessions.discard(session_id)

    # 添加节点
    workflow.add_node("midscene_agent", midscene_node)

    # 设置流程：入口 -> agent -> 结束
    workflow.add_edge(START, "midscene_agent")
    workflow.add_edge("midscene_agent", END)

    # 编译图
    graph = workflow.compile()

    logger.info("✅ Midscene LangGraph 图创建完成")
    return graph


# 导出 CompiledGraph 变量（LangGraph CLI 要求）
# 变量名必须是 'graph'
graph = create_midscene_graph()
