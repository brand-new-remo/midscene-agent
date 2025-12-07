# LangGraph CLI 集成实施计划

## 项目概述

将现有的 Midscene Agent 集成到 LangGraph CLI，支持通过 Agent Chat UI 进行自然语言对话，同时保持现有 `python run.py` 模式完全不变。

## 设计原则

- **零破坏性**：现有模式 100% 不变
- **轻量级适配**：最小化新增代码
- **最大复用**：复用 MidsceneAgent、工具系统、HTTP 客户端
- **独立运行**：两种模式完全解耦

## 实施步骤

### 阶段 1: 核心适配器开发

#### 1.1 创建 CLI 适配器
**文件**: `runner/agent/cli_adapter.py`

**功能**:
- 包装 MidsceneAgent，提供 LangGraph 标准接口
- 处理消息流转换（流式响应 → LangGraph 消息）
- 管理会话生命周期

**关键代码结构**:
```python
class MidsceneAgentAdapter:
    async def process(self, state: MessagesState) -> AsyncGenerator[BaseMessage]:
        """将 Midscene 流式响应转换为 LangGraph 标准响应"""
        
    async def _create_session(self) -> str:
        """创建 Midscene 会话（复用 http_client.py）"""
        
    async def _cleanup_session(self, session_id: str):
        """清理 Midscene 会话（复用 http_client.py）"""
```

#### 1.2 创建 CLI 入口
**文件**: `runner/langgraph_cli.py`

**功能**:
- 创建并导出 CompiledGraph
- 配置 StateGraph 和工具节点
- 集成适配器

**关键代码结构**:
```python
from agent.cli_adapter import MidsceneAgentAdapter
from langgraph.prebuilt import ToolNode

def create_midscene_graph():
    """创建 LangGraph CLI 兼容的编译图"""
    
    workflow = StateGraph(MessagesState)
    workflow.add_node("midscene_agent", MidsceneAgentAdapter().process)
    workflow.add_edge(START, "midscene_agent")
    workflow.add_edge("midscene_agent", END)
    
    return workflow.compile()

# 导出 CompiledGraph 变量（LangGraph CLI 要求）
midscene_graph = create_midscene_graph()
```

### 阶段 2: 工具系统集成

#### 2.1 创建工具适配器
**文件**: `runner/agent/tools/langgraph_adapter.py`

**功能**:
- 将现有 30+ 工具转换为 LangGraph 格式
- 复用现有的工具定义（`tools/definitions.py`）
- 创建 ToolNode

**关键代码结构**:
```python
from .definitions import TOOL_DEFINITIONS
from langchain_core.tools import tool

def create_langgraph_tools():
    """创建 LangGraph 兼容的工具列表"""
    tools = []
    
    for tool_name, tool_def in TOOL_DEFINITIONS.items():
        adapted_tool = _adapt_tool_signature(tool_def)
        tools.append(adapted_tool)
    
    return tools

def create_tool_node():
    """创建 ToolNode（复用现有工具逻辑）"""
    return ToolNode(tools=create_langgraph_tools())
```

### 阶段 3: CLI 配置

#### 3.1 创建 LangGraph 配置文件
**文件**: `runner/langgraph.json`

**配置内容**:
```json
{
  "dependencies": ["."],
  "graphs": {
    "midscene_agent": "./langgraph_cli.py:midscene_graph"
  },
  "env": ".env"
}
```

#### 3.2 验证依赖
**文件**: `runner/requirements.txt`

**状态**: ✅ 已包含 `langgraph>=1.0.0`，无需额外依赖

### 阶段 4: 测试与验证

#### 4.1 验证现有模式
```bash
cd runner
python run.py
```
**预期**: 交互式菜单正常显示，现有功能不受影响

#### 4.2 测试 CLI 模式
```bash
cd runner
langgraph dev
```
**预期**: 
- 显示 "API: http://localhost:2024/"
- 显示 "LangGraph Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"

#### 4.3 功能测试
- 在 Agent Chat UI 中测试基本对话
- 验证 30+ 工具调用
- 测试会话管理
- 验证流式响应

## 关键实现细节

### 会话管理
```python
class MidsceneAgentAdapter:
    def __init__(self):
        self.active_sessions = set()
    
    async def process(self, state):
        session_id = await self._create_session()
        self.active_sessions.add(session_id)
        
        try:
            async for chunk in self._execute(state, session_id):
                yield chunk
        finally:
            await self._cleanup_session(session_id)
            self.active_sessions.remove(session_id)
```

### 消息流转换
```python
async def process(self, state: MessagesState):
    user_input = state["messages"][-1].content
    
    # 复用现有的 agent.stream_execute
    async for chunk in self.agent.stream_execute(user_input, session_id):
        # 转换为 LangGraph 标准消息格式
        yield AIMessage(content=chunk)
```

### 工具定义转换
```python
@tool
async def adapted_tool(**kwargs):
    # 复用现有的工具执行逻辑
    return await register_tool(tool_def.name, **kwargs)
```

## 风险评估与应对

### 风险 1: 会话泄漏
**应对**: 实现 `finally` 块确保清理，添加会话池监控

### 风险 2: 配置冲突
**应对**: 完全复用同一 Config 类，使用同一 .env 文件

### 风险 3: 依赖版本冲突
**应对**: 现有 requirements.txt 已包含兼容版本

## 成功标准

- ✅ 现有模式：`python run.py` 正常工作
- ✅ CLI 模式：`langgraph dev` 正常启动
- ✅ 两种模式可同时运行
- ✅ 所有 30+ 工具在两种模式下都可用
- ✅ 会话管理正确，无泄漏
- ✅ 配置完全兼容

## 预期文件清单

### 新增文件
1. `runner/langgraph_cli.py` - CLI 入口，导出 CompiledGraph
2. `runner/langgraph.json` - CLI 配置文件
3. `runner/agent/cli_adapter.py` - 适配器核心
4. `runner/agent/tools/langgraph_adapter.py` - 工具适配

### 修改文件
- 无（完全零侵入式）

## 启动方式对比

### 现有模式（不变）
```bash
cd runner
python run.py
```

### 新增 CLI 模式
```bash
cd runner
langgraph dev
# 访问 http://localhost:2024 使用 Agent Chat UI
```

## 总结

这个方案确保了最小的工作量实现最大的功能，同时完全保证向后兼容性。通过复用现有的 MidsceneAgent、工具系统和会话管理，我们可以在不修改任何现有代码的情况下，为用户提供现代化的 Agent Chat UI 体验。
