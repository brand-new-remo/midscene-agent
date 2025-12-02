# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。
```

## 项目概览

**Midscene LangGraph Agent** 是一个 AI 驱动的网页自动化系统，结合了：
- **LangGraph** 使用 StateGraph 进行智能编排
- **DeepSeek LLM** 用于推理和决策
- **Midscene** 用于基于视觉的网页交互

该系统支持自然语言驱动的网页自动化，允许用户通过英语指令控制网页浏览器。

## 高层架构

```
用户输入（自然语言）
         ↓
   LangGraph Agent（StateGraph 与 ReAct）
         ↓
   DeepSeek LLM（推理引擎）
         ↓
   MCP 协议（基于 stdio 的 JSON-RPC）
         ↓
   Midscene MCP 服务器（视觉 + 浏览器自动化）
         ↓
   浏览器（Playwright + 豆包视觉模型）
```

### 核心组件

1. **src/agent.py** - 使用 StateGraph 模式的主要 LangGraph 智能体
   - `MidsceneAgent` 类，支持异步上下文管理器
   - 两个主要工具：`midscene_action`（执行操作）和 `midscene_query`（提取信息）
   - 使用 `StateGraph(MessagesState)` 进行智能体编排（LangGraph 1.0+）
   - 需要使用 `SecretStr` 包装的 API 密钥以兼容 LangChain 1.0+

2. **run.py** - 示例和自定义任务的交互式启动器
   - 包含 9 个选项的菜单驱动界面
   - 包括基础示例、电商测试和自定义任务模式

3. **src/config.py** - 配置管理
   - 从 .env 文件加载环境变量
   - 支持 DeepSeek API、Midscene 设置和浏览器选项

4. **src/mcp_wrapper.py** - MCP 协议客户端包装器
   - 通过 stdio 管理与 Midscene MCP 服务器的连接
   - 处理工具发现和 RPC 通信

5. **examples/** - 使用示例
   - `basic_usage.py` - 简单网页自动化
   - `test_ecommerce.py` - 电商测试场景

6. **tests/test_compatibility.py** - 兼容性测试脚本
   - 验证 LangChain/LangGraph 1.0+ 兼容性
   - 测试导入、API 更改和智能体实例化
   - 使用 `importlib.metadata` 进行安全的版本检查

## 开发命令

### 设置
```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境模板
cp .env.example .env
# 编辑 .env 并添加你的 DEEPSEEK_API_KEY
```

### 运行测试
```bash
# 运行兼容性测试
python tests/test_compatibility.py

# 应该输出：✅ 12/12 测试通过
```

### 运行示例
```bash
# 启动交互式菜单
python run.py

# 运行特定示例
python examples/basic_usage.py
```

### 开发工作流

1. **环境设置**
   - 在 `.env` 文件中设置 `DEEPSEEK_API_KEY`
   - 可选设置 `DEEPSEEK_BASE_URL`（默认为 https://api.deepseek.com）
   - 使用 `python tests/test_compatibility.py` 测试

2. **代码更改**
   - 所有智能体代码在 `agent.py` 中
   - 使用 LangGraph 1.0+ StateGraph 模式（不是已弃用的 `create_react_agent`）
   - 消息处理：使用 `MessagesState` 和 `HumanMessage` 兼容 LangChain 1.0+
   - API 密钥必须使用 `SecretStr` 包装

3. **测试更改**
   ```bash
   # 运行兼容性测试
   python tests/test_compatibility.py

   # 快速验证
   python -c "from src.agent import MidsceneAgent; print('OK')"
   ```

## 关键技术细节

### LangGraph 1.0+ 兼容性

代码使用新的 StateGraph 模式：
```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("agent", tools_condition, {...})
graph = builder.compile()
```

**旧模式（已弃用）：**
```python
from langgraph.prebuilt import create_react_agent  # ❌ 不要使用此方法
```

### 智能体工具系统

向智能体暴露两个主要工具：

1. **`midscene_action`** - 执行浏览器操作
   - 输入：自然语言指令
   - 示例："点击登录按钮"、"用 name='John' 填写表单"

2. **`midscene_query`** - 从页面提取信息
   - 输入：关于页面内容的问题
   - 示例："价格是多少？"、"提取联系信息"

### 配置

关键环境变量（通过 .env）：
- `DEEPSEEK_API_KEY` - 必需的 API 密钥
- `DEEPSEEK_BASE_URL` - API 基础 URL（默认：https://api.deepseek.com/v1）
- `DEEPSEEK_MODEL` - 模型名称（默认：deepseek-chat）
- `DEEPSEEK_TEMPERATURE` - 温度参数（默认：0）
- `OPENAI_API_KEY` - OpenAI 兼容 API 密钥（用于视觉模型）
- `OPENAI_BASE_URL` - OpenAI 兼容 API 基础 URL（用于视觉模型）
- `MIDSCENE_COMMAND` - Midscene 启动命令（默认：npx）
- `MIDSCENE_ARGS` - Midscene 参数（默认：@midscene/web@mcp）

## 常见模式

### 创建和使用智能体

```python
from src.agent import MidsceneAgent

async def main():
    agent = MidsceneAgent(
        deepseek_api_key="your-api-key",
        deepseek_base_url="https://api.deepseek.com/v1",
        deepseek_model="deepseek-chat"
    )

    async with agent:
        async for event in agent.execute("导航到 google.com"):
            if "messages" in event:
                print(event["messages"][-1].content)
```

### 错误处理

常见问题和解决方案：
1. **`AttributeError: module has no __version__`** - 使用 test_compatibility.py 中的 `get_package_version()`
2. **`SecretStr type error`** - 使用 `SecretStr()` 包装 API 密钥
3. **`create_react_agent deprecated`** - 使用 StateGraph 模式
4. **`Tool requires docstring`** - 为 `@tool` 装饰的函数添加文档字符串

## 工具类

- **src/utils/async_helpers.py** - 支持超时的异步工具
- **src/utils/logging_utils.py** - 日志配置

## 测试策略

`tests/test_compatibility.py` 脚本验证：
- Python 版本（>= 3.10）
- 包导入（LangChain、LangGraph、MCP、Pydantic、langchain-deepseek）
- API 兼容性（HumanMessage、@tool 装饰器、ChatDeepSeek）
- 智能体实例化
- StateGraph 创建

在更改前应通过所有测试以确保兼容性。

```

