# Midscene LangGraph Agent

一个 AI 驱动的网页自动化智能体，结合 **LangGraph** 进行智能编排、**DeepSeek LLM** 进行推理，以及 **Midscene** 进行基于视觉的网页交互。

## ✨ 主要特性

- **🚀 混合架构**: Node.js + Python 完美融合
- **🌐 HTTP + WebSocket**: 更稳定的通信协议
- **📡 流式响应**: 实时查看执行进度
- **🔧 完整功能**: 充分利用 Midscene.js 所有 API
- **📊 监控指标**: 内置 Prometheus 监控

## 功能特性

- 通过自然语言指令控制浏览器
- 支持点击、输入、滚动等网页操作
- 智能提取页面信息
- 支持多步骤复杂任务
- 基于视觉模型的元素定位
- 支持会话管理和复用
- 实时流式响应和进度反馈

## 架构

```
用户输入（自然语言）
         ↓
   LangGraph Agent（StateGraph + 流程控制）
         ↓
   DeepSeek LLM（推理引擎）
         ↓
   HTTP Client（Python）- 异步通信
         ↓
   Node.js Server（Express + WebSocket）
         ↓
   Midscene Orchestrator（会话管理）
         ↓
   Midscene.js + Playwright（浏览器自动化）
         ↓
   浏览器（Chrome/Chromium）
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

# 安装 Node.js 依赖
cd server
npm install
cd ..

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 添加你的 API 密钥
```

### 启动

```bash
# 启动 Node.js 服务
cd server
npm start
# 服务运行在 http://localhost:3000

# 新终端：运行 Python 示例
python examples/basic_usage.py
```

### 监控

```bash
# Prometheus 指标
curl http://localhost:3000/metrics
```

## 项目结构

```
midscene-agent/
├── src/
│   ├── agent.py          # LangGraph 智能体
│   ├── http_client.py    # HTTP 客户端
│   ├── config.py         # 配置管理
│   └── tools/            # 工具模块
├── server/               # Node.js 服务
│   ├── src/
│   │   ├── index.js      # 主服务器
│   │   ├── orchestrator.js # Midscene 协调器
│   │   └── metrics.js    # 监控指标
│   └── package.json      # Node.js 依赖
├── examples/
│   ├── basic_usage.py    # 基础示例
│   └── search_results_demo.py # 搜索结果演示
├── docs/                 # 文档
│   ├── architecture/     # 架构文档
│   ├── deployment/       # 部署文档
│   └── guides/           # 使用指南
├── run.py                # 交互式启动器
├── test.py               # 测试脚本
├── start.sh              # 快速启动脚本
├── requirements.txt      # Python 依赖
└── .env.example          # 环境变量模板
```

## 使用示例

### 基础用法

```python
import asyncio
from src.agent import MidsceneAgent

async def main():
    # 创建 Agent（基于 HTTP）
    agent = MidsceneAgent(
        deepseek_api_key="your-api-key",
        deepseek_base_url="https://api.deepseek.com/v1",
        midscene_server_url="http://localhost:3000",
        enable_websocket=True,  # 启用 WebSocket 流式响应
        tool_set="full"
    )

    async with agent:
        task = """访问 https://github.com 并执行以下操作：
        1. 导航到 GitHub 首页
        2. 在搜索框中搜索 "midscene"
        3. 等待搜索结果加载
        4. 截取一张屏幕截图
        """

        # 流式响应，显示执行进度
        async for event in agent.execute(task, stream=True):
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

### 完整工具集

| 类别 | 工具 | 说明 | 示例 |
|------|------|------|------|
| **导航** | `midscene_navigate` | 导航到 URL | `{"url": "https://example.com"}` |
| | `midscene_set_active_tab` | 切换标签页 | `{"tabId": "1"}` |
| **交互** | `midscene_aiTap` | AI 智能点击 | `{"locate": "登录按钮"}` |
| | `midscene_aiInput` | AI 智能输入 | `{"locate": "搜索框", "value": "Python"}` |
| | `midscene_aiScroll` | AI 智能滚动 | `{"direction": "down", "distance": 500}` |
| | `midscene_aiHover` | AI 悬停 | `{"locate": "用户头像"}` |
| | `midscene_aiKeyboardPress` | 按键操作 | `{"key": "Enter"}` |
| | `midscene_aiWaitFor` | 智能等待 | `{"assertion": "页面加载完成"}` |
| **查询** | `midscene_aiAssert` | AI 断言验证 | `{"assertion": "价格显示正确"}` |
| | `midscene_location` | 获取位置信息 | `{}` |
| | `midscene_screenshot` | 截取屏幕截图 | `{"name": "homepage", "fullPage": true}` |
| | `midscene_get_tabs` | 获取标签页列表 | `{}` |
| | `midscene_get_console_logs` | 获取控制台日志 | `{"msgType": "error"}` |
| **高级** | `midscene_aiQuery` | 结构化数据提取 | `{"dataDemand": "{name: string}"}` |
| | `midscene_aiAsk` | AI 问答 | `{"prompt": "页面主要内容"}` |
| | `midscene_aiBoolean` | 布尔值查询 | `{"prompt": "是否有登录按钮"}` |
| | `midscene_aiNumber` | 数值查询 | `{"prompt": "价格是多少"}` |
| | `midscene_aiString` | 字符串查询 | `{"prompt": "页面标题"}` |

## 配置

### 环境变量（.env）

```bash
# DeepSeek API（必需）
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Midscene 服务地址
MIDSCENE_SERVER_URL=http://localhost:3000

# 视觉模型（用于 Midscene）
OPENAI_API_KEY=your-vision-api-key
OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MIDSCENE_MODEL_NAME=doubao-seed-1.6-vision

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
| Node.js 服务无法启动 | 检查 Node.js 版本 >= 18，端口 3000 是否被占用 |
| Python 端无法连接 | 确保 Node.js 服务运行在 http://localhost:3000 |
| API 密钥错误 | 检查 `.env` 文件配置 |
| Chrome 未找到 | 安装 Chrome 浏览器或设置 `CHROME_PATH` |
| 操作超时 | 简化任务或增加超时时间 |

## 依赖

### Python 依赖
- langchain >= 1.0.0
- langgraph >= 1.0.0
- langchain-deepseek >= 1.0.0
- aiohttp >= 3.9.0
- pydantic >= 2.0.0
- python-dotenv >= 1.0.0

### Node.js 依赖
- @midscene/web >= 0.30.9
- express >= 5.2.1
- ws >= 8.18.3
- playwright >= 1.57.0
- winston >= 3.18.3
- prom-client >= 15.1.3

## 文档

- [架构概览](./docs/architecture/overview.md) - 详细架构说明
- [依赖修正记录](./docs/architecture/dependency-fixes.md) - 版本修正历史
- [清理日志](./docs/architecture/cleanup-log.md) - 代码清理记录
- [迁移指南](./docs/guides/migration.md) - 版本迁移说明

## 资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [DeepSeek API](https://platform.deepseek.com/docs)
- [Midscene 文档](https://midscenejs.com)

## 许可证

MIT License
