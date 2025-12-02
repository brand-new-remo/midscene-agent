# Midscene LangGraph Agent

一个 AI 驱动的网页自动化智能体，结合 **LangGraph** 进行智能编排、**DeepSeek LLM** 进行推理，以及 **Midscene** 进行基于视觉的网页交互。

## 功能特性

- 通过自然语言指令控制浏览器
- 支持点击、输入、滚动等网页操作
- 智能提取页面信息
- 支持多步骤复杂任务
- 基于视觉模型的元素定位

## 架构

```
用户（自然语言）
       ↓
LangGraph Agent（StateGraph + ReAct）
       ↓
DeepSeek LLM（推理引擎）
       ↓
MCP 协议（JSON-RPC over stdio）
       ↓
Midscene MCP 服务器（视觉分析 + Playwright）
       ↓
Chrome 浏览器
```

## 快速开始

### 前置要求

- **Node.js** >= 18
- **Python** >= 3.10
- **Chrome 浏览器**
- **DeepSeek API 密钥**（[获取](https://platform.deepseek.com)）

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd midscene-agent

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Midscene CLI
npm install -g @midscene/web

# 配置环境变量
cp .env.example .env
# 编辑 .env 添加你的 API 密钥
```

### 运行

```bash
# 交互式菜单
python run.py

# 或直接运行示例
python examples/basic_usage.py
```

## 项目结构

```
midscene-agent/
├── src/
│   ├── agent.py          # LangGraph 智能体
│   ├── mcp_wrapper.py    # MCP 客户端
│   ├── config.py         # 配置管理
│   └── utils/            # 工具模块
├── examples/
│   ├── basic_usage.py    # 基础示例
│   └── test_ecommerce.py # 电商测试
├── run.py                # 交互式启动器
├── requirements.txt      # Python 依赖
└── .env.example          # 环境变量模板
```

## 使用示例

### 基础用法

```python
import asyncio
from src.agent import MidsceneAgent

async def main():
    agent = MidsceneAgent(
        deepseek_api_key="your-api-key",
        deepseek_base_url="https://api.deepseek.com/v1",
    )

    async with agent:
        task = "导航到 https://www.google.com，搜索 'LangGraph'"
        async for event in agent.execute(task):
            if "messages" in event:
                print(event["messages"][-1].content)

asyncio.run(main())
```

### 多步骤任务

```python
async with agent:
    task = """
    1. 前往 https://news.ycombinator.com
    2. 点击第一个故事链接
    3. 用 2-3 句话总结文章内容
    """
    async for event in agent.execute(task):
        print(event)
```

## 可用工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `midscene_action` | 执行浏览器操作 | "点击登录按钮"、"输入 'hello'" |
| `midscene_query` | 提取页面信息 | "价格是多少？"、"列出所有链接" |

## 配置

### 环境变量（.env）

```bash
# DeepSeek API（必需）
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 视觉模型（用于 Midscene）
OPENAI_API_KEY=your-vision-api-key
OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MIDSCENE_MODEL=doubao-seed-1.6-vision

# 浏览器（可选）
CHROME_PATH=/path/to/chrome
HEADLESS=false
```

## 最佳实践

### 编写有效指令

**推荐**：
- "点击右上角的蓝色 '登录' 按钮"
- "在搜索框中输入 'Python tutorials' 并按回车"

**避免**：
- "点击按钮"（太模糊）
- "搜索某些东西"（没有具体内容）

### 任务结构

```python
task = """
1. 导航到 https://example.com
2. 使用 username='user' 登录
3. 点击 'Dashboard' 链接
4. 提取显示的关键数据
"""
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 连接 Midscene 失败 | 运行 `npm install -g @midscene/web` |
| API 密钥错误 | 检查 `.env` 文件配置 |
| Chrome 未找到 | 设置 `CHROME_PATH` 环境变量 |
| 操作超时 | 简化任务或增加超时时间 |

## 依赖

- langchain >= 1.0.0
- langgraph >= 1.0.0
- langchain-deepseek >= 1.0.0
- mcp >= 1.0.0
- pydantic >= 2.0.0

## 资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [DeepSeek API](https://platform.deepseek.com/docs)
- [Midscene 文档](https://midscene.org)

## 许可证

MIT License
