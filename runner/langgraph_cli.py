"""
LangGraph CLI 适配层

这个模块将现有的 MidsceneAgent 适配为 LangGraph CLI 兼容的格式，
支持通过 Agent Chat UI 进行自然语言对话。

使用方法:
    langgraph dev
    # 访问 http://localhost:2024 使用 Agent Chat UI
"""

from langgraph.graph import StateGraph, MessagesState, START, END
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

    # 添加节点：使用适配器包装现有 agent
    workflow.add_node(
        "midscene_agent",
        adapter.process
    )

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
