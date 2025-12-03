# Midscene LangGraph Agent 项目架构与现状分析

## 项目概述

**Midscene LangGraph Agent** 是一个 AI 驱动的网页自动化系统，结合了 LangGraph、DeepSeek LLM 和 Midscene 进行基于视觉的网页交互。

## 技术栈

- **核心框架**: LangGraph (StateGraph + ReAct)
- **LLM引擎**: DeepSeek (deepseek-chat)
- **浏览器自动化**: Midscene (基于 Playwright + 视觉模型)
- **协议层**: MCP (Model Context Protocol)
- **视觉模型**: 豆包视觉模型 (doubao-seed-1.6-vision)

## 当前架构 (3层桥接模式)

```
用户输入(自然语言)
    ↓
LangGraph Agent (src/agent.py)
    ↓
DeepSeek LLM (推理引擎)
    ↓
MCP 协议 (JSON-RPC over stdio)
    ↓
Midscene MCP 服务器 (@midscene/mcp - Node.js进程)
    ↓
Chrome 扩展桥接 (Midscene Extension)
    ↓
Chrome 浏览器 (实际控制)
    ↓
豆包视觉模型 (页面理解)
```

## 核心文件结构

### 主要组件
- `src/agent.py`: LangGraph 智能体实现，包含 `MidsceneAgent` 类
- `src/mcp_wrapper.py`: MCP 协议客户端包装器 (385行，复杂的指令解析逻辑)
- `src/config.py`: 配置管理，从 `.env` 加载环境变量
- `run.py`: 交互式启动器（9个菜单选项）
- `examples/basic_usage.py`: 基础使用示例
- `examples/test_ecommerce.py`: 电商测试场景

### 配置文件
- `.env`: 环境变量配置
- `.mcp.json`: Claude Code MCP 服务器配置
- `midscene_run/`: Midscene 运行时目录
  - `log/`: 运行日志
  - `report/`: 测试报告 (文件名格式: `page-over-chrome-extension-bridge-xxx.html`)

## 关键代码分析

### 1. 配置管理 (src/config.py)

```python
class Config:
    # DeepSeek API
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str
    DEEPSEEK_MODEL: str

    # Midscene 配置
    MIDSCENE_MODEL: str
    MIDSCENE_COMMAND: str = "npx"
    MIDSCENE_ARGS: list = ["-y", "@midscene/mcp"]

    # 浏览器配置
    CHROME_PATH: Optional[str]
    HEADLESS: bool = False  # 当前默认为 false

    # 视觉模型配置
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
```

### 2. 指令解析逻辑 (src/mcp_wrapper.py:130-290行)

复杂的 `if-elif` 解析逻辑：
- 解析导航指令 (`navigate to`)
- 解析点击操作 (`click` / `点击` / `按`)
- 解析输入操作 (`input` / `type` / `输入`)
- 解析滚动操作 (`scroll` / `滚动`)
- 解析按键操作 (`按回车键`)

**问题**: 130-290行有大量解析逻辑，性能低，代码冗余。

### 3. 工具函数 (src/agent.py)

```python
# 创建 Midscene 操作工具
midscene_action_tool = create_midscene_action_tool(mcp_wrapper)
# 创建 Midscene 查询工具
midscene_query_tool = create_midscene_query_tool(mcp_wrapper)
```

## 当前工作流程

### 启动步骤
1. **安装 Chrome 扩展**: 从 Chrome Web Store 安装 Midscene 扩展
2. **启动扩展**: 点击浏览器工具栏的扩展图标
3. **允许连接**: 在扩展弹窗中点击 "Allow connection" 按钮
4. **运行代码**: 执行 `python run.py`

### 执行流程
```
Python agent.py → mcp_wrapper.py
    ↓ (调用 call_tool)
Midscene MCP 服务器 (Node.js)
    ↓ (Chrome DevTools Protocol)
Midscene Chrome Extension
    ↓ (控制浏览器)
Chrome 浏览器
    ↓ (截图分析)
豆包视觉模型 (doubao-seed-1.6-vision)
```

## 当前问题

### 1. 桥接模式复杂性
- **多层桥接**: Python → MCP → 扩展 → 浏览器
- **手动操作**: 需要用户手动启动扩展并允许连接
- **启动慢**: ~3-5秒启动时间
- **不适合无头**: 桥接模式依赖可视化 Chrome 扩展界面

### 2. 指令解析冗余
- `mcp_wrapper.py` 130-290行有大量解析逻辑
- 重复的正则表达式匹配
- 中英文混合处理逻辑复杂

### 3. 性能问题
- 多个进程通信 (Python ↔ Node.js ↔ 扩展)
- 每次操作需要截图 → AI分析 → 坐标计算
- 内存占用高

## 可能的解决方案

### 方案A: 启用无头模式 (简单修改)
在 `.env` 中添加:
```bash
HEADLESS=true
PLAYWRIGHT_HEADLESS=true
```

**优点**: 最小修改
**缺点**: 仍需桥接模式，架构复杂

### 方案B: 简化指令解析 (中等修改)
修改 `mcp_wrapper.py`，删除复杂解析逻辑，直接传递指令给 MCP 服务器。

**优点**: 简化代码逻辑
**缺点**: 仍需桥接模式

### 方案C: 自定义 Playwright MCP 服务器 (推荐)
创建独立的 Playwright MCP 服务器:
```python
class PlaywrightDirectMCP:
    async def launch_browser(self):
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
```

**架构**:
```
Python → Playwright MCP → 无头浏览器 (1层桥接)
```

**优点**:
- 保持 MCP 架构 (支持后续扩展)
- 性能更好 (直接 Playwright)
- 支持无头模式
- 代码简洁

**缺点**:
- 需要开发新的 MCP 服务器
- 修改调用方代码

## 环境变量配置

### 必需变量
```bash
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=196a3ab3-4e8a-4c4c-9bcc-0d4bcdf2f813
OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 可选变量
```bash
HEADLESS=false  # 浏览器模式
CHROME_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
MIDSCENE_MODEL=ep-20251202151146-7fhck
```

## 工具调用

### Midscene 操作工具
- `midscene_action`: 执行浏览器操作
  - "导航到 https://google.com"
  - "点击登录按钮"
  - "在搜索框中输入 'hello'"
  - "向下滚动"

### Midscene 查询工具
- `midscene_query`: 提取页面信息
  - "价格是多少？"
  - "提取联系信息"
  - "显示所有导航菜单项"

## 关键技术细节

### LangGraph 1.0+ StateGraph 模式
```python
from langgraph.graph import StateGraph, MessagesState, START, END

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("agent", tools_condition, {
    "tools": "tools",
    "__end__": END
})
builder.add_edge("tools", "agent")
graph = builder.compile()
```

### API 密钥处理 (LangChain 1.0+)
```python
from pydantic import SecretStr

llm = ChatDeepSeek(
    api_key=SecretStr(api_key),  # 必须包装
    ...
)
```

## 日志和报告

### 日志位置
- `midscene_run/log/`: 各种日志文件
  - `agent.log`
  - `ai-call.log`
  - `web-tool-profile.log`
  - 等

### 报告位置
- `midscene_run/report/`: 测试报告
  - 命名格式: `page-over-chrome-extension-bridge-{timestamp}.html`
  - 证明当前使用桥接模式

## 用户需求

用户明确表达的需求:
1. **保持 MCP 架构** - 支持后续集成更多 MCP 服务器
2. **不使用桥接模式** - 避免 3 层桥接复杂性
3. **支持无头浏览器** - 后台运行，适合自动化
4. **简化调用逻辑** - 删除复杂指令解析
5. **提升性能** - 减少启动时间和内存占用

## 总结

这是一个功能完整但架构复杂的项目。当前使用桥接模式，通过 Chrome 扩展控制浏览器。虽然有效，但存在启动慢、不适合无头模式等问题。

最佳解决方案是创建自定义的 Playwright MCP 服务器，既保持 MCP 架构的优势，又获得直接控制的简洁性和性能。
