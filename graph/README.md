# LangGraph CLI 集成

本目录包含 Midscene Agent 项目的 LangGraph CLI 集成代码，提供基于自然语言的网页自动化开发环境。

## 概述

通过 LangGraph CLI，开发者可以使用自然语言与智能体交互，实现智能的网页自动化操作。系统集成了：
- **LangGraph** 用于 AI 智能体编排
- **DeepSeek LLM** 用于推理
- **Midscene.js** 用于 AI 驱动的视觉网页交互
- **Playwright** 用于浏览器自动化

## 目录结构

```
graph/
├── langgraph.json             # LangGraph CLI 配置文件
├── langgraph_cli.py           # CLI 入口点
├── cli_adapter.py             # CLI 适配器
├── langgraph_adapter.py       # 工具适配器
├── definitions.py             # 工具定义（30+ 工具）
└── README.md                  # 本文档
```

## 快速开始

### 1. 环境准备

确保已安装依赖：
```bash
# Python 依赖
cd runner
pip install -r requirements.txt

# Node.js 服务器
cd ../server
npm install
npm start
```

### 2. 配置环境变量

编辑 `runner/.env` 文件：
```bash
# DeepSeek LLM 配置 (必需)
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Midscene 服务器配置
MIDSCENE_SERVER_URL=http://localhost:3000
```

### 3. 启动 LangGraph 开发服务器

从项目根目录启动：
```bash
# 方法1: 使用绝对路径
langgraph dev --config graph/langgraph.json

# 方法2: 先切换到 graph 目录
cd graph/
langgraph dev
```

### 4. 访问 Web UI

启动后访问：**http://localhost:2024**

在界面中选择 `midscene_agent`，然后输入自然语言指令，例如：
- "打开 https://www.baidu.com"
- "在搜索框输入 '人工智能'"
- "点击搜索按钮"
- "验证搜索结果是否显示"

## 可用工具

系统提供 30+ 个网页自动化工具，分为以下类别：

### 导航工具 (4个)
- `midscene_navigate` - 导航到 URL
- `midscene_setActiveTab` - 切换标签页
- `midscene_goBack` - 返回上一页
- `midscene_reload` - 刷新页面

### 交互工具 (6个)
- `midscene_aiTap` - AI 智能点击
- `midscene_aiInput` - AI 智能输入
- `midscene_aiScroll` - AI 页面滚动
- `midscene_aiHover` - AI 悬停
- `midscene_aiKeyboardPress` - 键盘操作
- `midscene_aiWaitFor` - 智能等待

### 查询工具 (15个)
- `midscene_aiAssert` - 验证条件
- `midscene_aiQuery` - 提取数据
- `midscene_aiAsk` - AI 查询
- `midscene_aiBoolean` - 布尔值
- `midscene_aiString` - 字符串值
- `midscene_aiNumber` - 数值
- `midscene_aiLocate` - 元素位置
- `midscene_location` - 当前位置
- `midscene_screenshot` - 截图
- `midscene_getTabs` - 标签页列表
- `midscene_getConsoleLogs` - 控制台日志
- `midscene_getPageSource` - 页面源码
- `midscene_getPageTitle` - 页面标题
- `midscene_getUrl` - 当前 URL
- `midscene_waitForLoad` - 等待加载完成

### 测试工具 (5个)
- `midscene_runTest` - 运行测试
- `midscene_assertElement` - 断言元素
- `midscene_assertText` - 断言文本
- `midscene_assertVisible` - 断言可见
- `midscene_assertCount` - 断言数量

## 架构说明

### 核心组件

1. **langgraph_cli.py**
   - LangGraph CLI 入口点
   - 创建和配置 StateGraph
   - 定义 Midscene 节点处理逻辑

2. **cli_adapter.py**
   - CLI 适配器，包装 MidsceneAgent
   - 处理消息流转换（流式响应 ↔ LangGraph 消息）
   - 管理会话生命周期

3. **langgraph_adapter.py**
   - 工具适配器
   - 将 30+ 工具定义转换为 LangGraph 兼容格式
   - 创建 ToolNode

4. **definitions.py**
   - 声明式工具定义
   - 集中管理所有可用工具

### 执行流程

```
用户输入 → LangGraph CLI → MidsceneAgentAdapter → MidsceneAgent
                                    ↓
                              HTTP/WebSocket
                                    ↓
                              Node.js Server → Playwright → Browser
```

## 故障排除

### 端口 2024 被占用
```bash
# 查找占用进程
lsof -ti:2024 | xargs kill

# 或使用其他端口
langgraph dev --port 2025 --config graph/langgraph.json
```

### Python 导入错误
如果遇到 `ModuleNotFoundError: No module named 'runner'`：
```bash
# 确保从项目根目录运行
cd /Users/duangangqiang/github/midscene
langgraph dev --config graph/langgraph.json

# 或设置 PYTHONPATH
export PYTHONPATH=/Users/duangangqiang/github/midscene:$PYTHONPATH
langgraph dev --config graph/langgraph.json
```

### DeepSeek API 密钥无效
```bash
# 检查 .env 文件
cat runner/.env | grep DEEPSEEK_API_KEY

# 测试 API 连接
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     https://api.deepseek.com/v1/models
```

### Node.js 服务器未启动
```bash
# 检查服务器状态
curl http://localhost:3000/api/health

# 启动服务器
cd server
npm start
```

## 示例对话

```
用户: "打开百度首页"
助手:
✅ 正在导航到 https://www.baidu.com
📍 当前页面: https://www.baidu.com
📸 截图已保存

用户: "在搜索框输入 '人工智能'"
助手:
✅ 找到搜索框: "百度一下"
✅ 输入文本: "人工智能"
✅ 输入完成

用户: "点击搜索按钮"
助手:
✅ 找到按钮: "百度一下"
✅ 点击完成
🔍 等待搜索结果...

用户: "验证页面是否显示搜索结果"
助手:
✅ 找到搜索结果
✅ 验证通过: 页面包含多个搜索结果链接
✅ 搜索结果标题包括: "人工智能_百度百科"、"人工智能（Artificial Intelligence）"等
```

## 配置说明

### langgraph.json

```json
{
  "dependencies": ["."],
  "graphs": {
    "midscene_agent": "./graph/langgraph_cli.py:graph"
  },
  "env": "./runner/.env"
}
```

**配置说明**：
- `dependencies`: 依赖的 Python 包列表
- `graphs`: 定义的图对象映射
  - `midscene_agent`: 图名称
  - `"./graph/langgraph_cli.py:graph"`: 指向 langgraph_cli.py 中的 graph 变量
- `env`: 环境变量文件路径（相对于项目根目录）

## 开发指南

### 添加新工具

1. 在 `definitions.py` 中添加工具定义
2. 系统会自动转换为 LangGraph 格式
3. 重启 `langgraph dev` 使更改生效

### 自定义图配置

编辑 `langgraph.json`：
```json
{
  "dependencies": ["."],
  "graphs": {
    "my_agent": "./graph/langgraph_cli.py:my_graph"
  },
  "env": "./runner/.env"
}
```

## 相关文档

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [Midscene.js 文档](../server/README.md)
- [项目主文档](../README.md)

## 许可证

本项目遵循 MIT 许可证。
