# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概览

**Midscene LangGraph Agent** 是一个 AI 驱动的网页自动化系统，结合了：
- **LangGraph** 使用 StateGraph 进行智能编排
- **DeepSeek LLM** 用于推理和决策
- **Midscene** 用于基于视觉的网页交互

该系统支持自然语言驱动的网页自动化，允许用户通过自然语言指令控制网页浏览器。

## 高层架构

```
用户输入（自然语言）
         ↓
   LangGraph Agent（StateGraph + ReAct）
         ↓
   DeepSeek LLM（推理引擎）
         ↓
   MCP 协议（基于 stdio 的 JSON-RPC）
         ↓
   Midscene MCP 服务器（视觉 + 浏览器自动化）
         ↓
   浏览器（Playwright + 豆包视觉模型）
```

## 核心组件

| 文件 | 说明 |
|------|------|
| `src/agent.py` | LangGraph 智能体实现，包含 `MidsceneAgent` 类 |
| `src/mcp_wrapper.py` | MCP 协议客户端包装器 |
| `src/config.py` | 配置管理，从 `.env` 加载环境变量 |
| `run.py` | 交互式启动器（9个菜单选项） |
| `examples/basic_usage.py` | 基础使用示例 |
| `examples/test_ecommerce.py` | 电商测试场景 |

## 开发命令

### 环境设置
```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 添加 DEEPSEEK_API_KEY
```

### 运行
```bash
# 交互式菜单
python run.py

# 运行示例
python examples/basic_usage.py
```

### 快速验证
```bash
python -c "from src.agent import MidsceneAgent; print('OK')"
```

## 关键技术细节

### LangGraph 1.0+ StateGraph 模式

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
builder.add_edge("tools", "agent")
graph = builder.compile()
```

**注意**：不要使用已弃用的 `create_react_agent`。

### 智能体工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `midscene_action` | 执行浏览器操作 | "点击登录按钮"、"导航到 https://google.com" |
| `midscene_query` | 提取页面信息 | "价格是多少？"、"提取联系信息" |

### API 密钥处理

LangChain 1.0+ 要求使用 `SecretStr` 包装 API 密钥：
```python
from pydantic import SecretStr

llm = ChatDeepSeek(
    api_key=SecretStr(api_key),  # 必须包装
    ...
)
```

## 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `DEEPSEEK_API_KEY` | ✅ | - | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | - | `https://api.deepseek.com/v1` | API 基础 URL |
| `DEEPSEEK_MODEL` | - | `deepseek-chat` | 模型名称 |
| `OPENAI_API_KEY` | - | - | 视觉模型 API 密钥（豆包） |
| `OPENAI_BASE_URL` | - | - | 视觉模型 API URL |
| `MIDSCENE_MODEL` | - | `doubao-seed-1.6-vision` | Midscene 视觉模型 |

## 常见错误及解决方案

| 错误 | 解决方案 |
|------|----------|
| `SecretStr type error` | 使用 `SecretStr()` 包装 API 密钥 |
| `create_react_agent deprecated` | 使用 StateGraph 模式 |
| `Tool requires docstring` | 为 `@tool` 装饰的函数添加文档字符串 |
| `module has no __version__` | 使用 `importlib.metadata.version()` 获取版本 |

## 代码规范

1. 所有智能体代码在 `src/agent.py`
2. 使用 `MessagesState` 和 `HumanMessage` 处理消息
3. 工具函数必须有完整的 docstring
4. 异步操作使用 `async/await`
5. 使用异步上下文管理器管理智能体生命周期

## 使用示例

```python
from src.agent import MidsceneAgent

async def main():
    agent = MidsceneAgent(
        deepseek_api_key="your-api-key",
        deepseek_base_url="https://api.deepseek.com/v1",
    )

    async with agent:
        async for event in agent.execute("导航到 google.com"):
            if "messages" in event:
                print(event["messages"][-1].content)
```
