# Midscene LangGraph Agent

一个 AI 驱动的网页自动化智能体，结合 **LangGraph** 进行智能编排、**DeepSeek LLM** 进行推理，以及 **Midscene** 进行基于视觉的网页交互。

## 主要特性

- **混合架构**: Node.js + Python 完美融合
- **HTTP + WebSocket**: 更稳定的通信协议
- **流式响应**: 实时查看执行进度
- **完整功能**: 充分利用 Midscene.js 所有 API
- **双格式测试**: 支持 YAML 结构化测试和自然语言测试
- **XMind 转换工具**: 将思维导图转换为自然语言测试文件

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
   Midscene.js(豆包视觉模型) + Playwright（浏览器自动化）
         ↓
   浏览器（Chrome/Chromium）
```

### LangGraph CLI 集成

项目还提供了基于 **LangGraph CLI** 的可视化界面，支持通过自然语言与智能体对话：

```
graph/                          # LangGraph CLI 适配层
├── langgraph_cli.py           # CLI 适配层，提供 Agent Chat UI
├── cli_adapter.py             # CLI 适配器，处理消息流转换
├── langgraph.json             # CLI 配置文件（使用绝对路径）
└── langgraph_adapter.py       # 工具适配器（30+ 工具转换）
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

# 安装 Python 依赖 (使用 UV)
uv venv
source .venv/Scripts/activate  # Windows
# 或
source .venv/bin/activate       # Linux/macOS
uv pip install -e .

# 配置环境变量
# .env 文件已在项目根目录 (如需修改请编辑根目录的 .env 文件)

### 可选：启动 Agent Chat UI

如果您想使用可视化界面与智能体交互，可以启动 Chat UI：

```bash
# 安装依赖
cd chat
pnpm install

# 启动开发服务器
pnpm dev
# 或使用 npm
npm run dev
# Chat UI 运行在 http://localhost:3001
```

### 启动

```bash
# 启动 Node.js 服务
cd server
npm start
# 服务运行在 http://localhost:3000

# 新终端：运行交互式启动器 (从项目根目录)
source .venv/Scripts/activate  # Windows
# 或
source .venv/bin/activate       # Linux/macOS
midscene

# 或者直接使用 uv run
uv run midscene
```

### 使用 LangGraph CLI (Agent Chat UI)

项目还提供了基于 **LangGraph CLI** 的可视化界面，支持通过自然语言与智能体对话：

```bash
# 安装 LangGraph CLI
uv pip install langgraph-cli

# 在项目根目录运行
langgraph dev

# 访问 Agent Chat UI
# 浏览器打开: http://localhost:2024
```

**重要说明：langgraph.json 中的绝对路径**

`graph/langgraph.json` 文件中使用了**绝对路径**（而非相对路径），这是因为：

1. **LangGraph CLI 的工作目录问题**：LangGraph CLI 默认从当前工作目录查找配置文件，但如果从不同目录运行（如从 `runner/` 目录运行 Python 测试），相对路径会失效

2. **跨目录调用的稳定性**：项目支持多种运行方式：
   - 从根目录运行 `langgraph dev`（启动 Chat UI）
   - 从 `runner/` 目录运行 `python run.py`（交互式启动器）
   - 从任意位置执行测试文件

3. **配置文件的可移植性**：绝对路径确保无论在哪个工作目录下启动，LangGraph 都能正确找到配置文件和依赖

**langgraph.json 配置详解**：

```json
{
  "dependencies": [".", "/Users/duangangqiang/github/midscene"],
  "graphs": {
    "midscene_agent": "/Users/duangangqiang/github/midscene/graph/langgraph_cli.py:graph"
  },
  "env": "/Users/duangangqiang/github/midscene/runner/.env"
}
```

- `dependencies`: 定义了 Python 模块的搜索路径，确保能从 graph 模块导入 runner 包
- `graphs`: 映射了图名称到具体的图函数，使用绝对路径确保 CLI 能正确定位
- `env`: 指定环境变量文件路径，为 LangGraph 提供 DeepSeek API 等配置

**Agent Chat UI 功能**：

- ✅ **自然语言交互**：通过可视化界面直接与智能体对话
- ✅ **实时流式响应**：查看操作执行的实时进度
- ✅ **会话管理**：自动管理 Midscene 会话生命周期
- ✅ **完整工具集**：支持所有 30+ 网页自动化工具
- ✅ **错误处理**：友好的错误提示和异常捕获

## 项目结构

```
midscene-agent/
├── server/                  # Node.js HTTP/WebSocket 服务器
│   ├── src/
│   │   ├── index.ts         # 主服务器入口
│   │   ├── orchestrator/    # Midscene 编排器模块化实现
│   │   │   ├── index.ts         # 编排器主类
│   │   │   ├── session.ts       # 会话管理
│   │   │   ├── actions/         # 操作执行
│   │   │   │   └── execute.ts
│   │   │   ├── queries/         # 查询执行
│   │   │   │   └── execute.ts
│   │   │   ├── action-history.ts # 历史记录
│   │   │   ├── system.ts        # 系统功能
│   │   │   ├── config.ts        # 配置
│   │   │   └── types.ts         # 类型定义
│   │   ├── websocket/       # WebSocket 服务器
│   │   │   ├── index.ts
│   │   │   ├── connectionManager.ts
│   │   │   └── handlers.ts
│   │   ├── routes/          # HTTP 路由模块
│   │   │   ├── sessions.ts
│   │   │   ├── health.ts
│   │   │   └── index.ts
│   │   ├── middleware/      # Express 中间件
│   │   ├── server/          # 服务器控制
│   │   │   ├── start.ts
│   │   │   └── shutdown.ts
│   │   ├── config/          # 服务器配置
│   │   └── types/           # TypeScript 类型定义
│   └── package.json
├── pyproject.toml           # UV 项目配置
├── uv.lock                  # UV 锁定文件
├── .env                     # 环境变量
├── .venv/                   # UV 虚拟环境
├── runner/                  # Python LangGraph 智能体
│   ├── agent/
│   │   ├── agent.py         # LangGraph 智能体
│   │   ├── http_client.py   # HTTP 客户端
│   │   ├── config.py        # 配置管理
│   │   ├── tools/           # 工具模块
│   │   │   └── definitions.py
│   │   └── utils/           # 工具函数
│   ├── executor/            # 测试执行器
│   │   ├── yaml_executor.py # YAML 测试执行器
│   │   └── text_executor.py # 自然语言测试执行器
│   ├── modes/               # 交互式菜单模式
│   │   ├── yaml_mode.py     # YAML 测试模式
│   │   ├── text_mode.py     # 自然语言测试模式
│   │   └── custom_mode.py   # 自定义任务模式
│   ├── run.py               # 交互式启动器
│   ├── check_config.py      # 配置检查
│   └── requirements.txt     # Python 依赖
├── tests/                   # 测试文件
│   ├── yamls/               # YAML 测试文件
│   └── texts/               # 自然语言测试文件
├── converter/               # XMind 转换工具
│   ├── __init__.py
│   ├── cli.py               # 命令行接口
│   ├── models.py            # 数据模型
│   ├── xmind_parser.py      # XMind 文件解析器
│   ├── text_generator.py    # 自然语言文本生成器
│   ├── utils.py             # 工具函数
│   ├── exceptions.py        # 异常处理
│   └── requirements.txt     # 依赖列表
├── xmind/                   # XMind 源文件
│   └── V5.60测试用例.xmind   # 示例 XMind 测试用例
├── graph/                   # LangGraph CLI 适配层
│   ├── langgraph_cli.py     # CLI 适配层，提供 Agent Chat UI 支持
│   ├── cli_adapter.py       # CLI 适配器，处理消息流转换和会话管理
│   ├── langgraph.json       # CLI 配置文件（使用绝对路径）
│   ├── langgraph_adapter.py # 工具适配器（30+ 工具转换）
│   └── __init__.py          # 模块初始化
├── chat/                    # Agent Chat UI (Next.js)
│   ├── src/
│   │   ├── app/             # Next.js 应用
│   │   ├── components/      # React 组件
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── lib/             # 工具库
│   │   └── providers/       # React Providers
│   ├── public/              # 静态资源
│   ├── package.json
│   └── next.config.mjs
├── docs/                    # 文档
└── .env.example             # 环境变量模板
```

## 使用示例

### 交互式启动器

```bash
source .venv/Scripts/activate  # Windows
# 或
source .venv/bin/activate       # Linux/macOS
midscene

# 或者直接使用 uv run
uv run midscene
```

菜单选项:

1. 运行单个 YAML 测试
2. 运行所有 YAML 测试
3. 运行单个自然语言测试
4. 运行所有自然语言测试
5. 自定义任务模式
6. 检查配置

### 直接执行测试

```bash
# 执行 YAML 测试
python -m executor.yaml_executor tests/yamls/basic_usage.yaml

# 执行自然语言测试
python -m executor.text_executor tests/texts/basic_usage.txt
```

### 格式化代码

**⚠️ 重要**: 每次修改 Python 代码后，请务必运行格式化命令，保持代码风格一致！

```bash
# 格式化整个项目
uv run ./format.py

# 格式化指定文件或目录
uv run ./format.py runner/
```

### 类型检查

**⚠️ 重要**: 每次修改 Python 代码后，请务必运行类型检查，确保类型安全！

```bash
# 对整个项目进行类型检查
uv run ./typecheck.py
```

**⚠️ 重要提示**：每次修改 Python 代码后，请在**项目根目录**执行以下命令：
1. `uv run ./format.py` - 格式化代码（使用 black）
2. `uv run ./typecheck.py` - 类型检查（使用 pyright）

这两个命令能确保代码格式一致性和类型安全。

### XMind 转换工具

项目包含一个 **XMind 转换工具**，可以将 XMind 思维导图格式的测试用例转换为自然语言测试文件。

#### 使用方法

**转换单个 XMind 文件**:
```bash
python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/
```

**批量转换目录**:
```bash
uv run python -m converter.cli -i xmind/ -o tests/texts/
```

**详细输出模式**:
```bash
uv run python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/ --verbose
```

**使用 uv 调用**:
```bash
source .venv/Scripts/activate  # Windows
# 或
source .venv/bin/activate       # Linux/macOS
uv run python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/
```

#### 功能特点

- ✅ **XMind → 自然语言测试文件**：将 XMind 思维导图转换为 tests/texts/ 格式
- ✅ **模块化输出**：每个模块生成独立的 .txt 文件
- ✅ **占位符配置**：@web 配置使用占位符，便于后续填写
- ✅ **零依赖**：仅使用 Python 标准库
- ✅ **批量转换**：支持单个文件或目录批量转换

#### XMind 结构要求

```
根节点: 版本信息 (如: "V5.60测试用例")
└── 第1层: #模块名 (如: "#登录管理")
    └── 第2层: 用例名 (如: "交互验证")
        └── 第3层: 操作步骤 (多行，编号列表)
            └── 第4层: 验证步骤 (编号列表)
```

#### 生成的文件格式

转换后生成的文件遵循自然语言测试格式：

```txt
# 模块名

@web:
  url: https://example.com  # TODO: 请填写实际 URL
  headless: false
  viewportWidth: 1280
  viewportHeight: 768

@task: 用例名

1. 步骤内容
2. 步骤内容
3. 验证步骤
```

### 测试文件格式

#### YAML 测试 (位于 `tests/yamls/`)

```yaml
web:
  url: https://example.com
  headless: false
  viewportWidth: 1280
  viewportHeight: 768

tasks:
  - name: Example Task
    flow:
      - ai: Navigate and perform actions
      - aiAssert: Check result
      - logScreenshot: Capture result
      - aiQuery:
          name: "Data"
          prompt: "Extract information"
```

#### 自然语言测试 (位于 `tests/texts/`)

```
@web:
  url: https://example.com
  headless: false

@task: Example Task

1. 导航到页面并等待完全加载
2. 点击搜索按钮
3. 验证搜索结果是否显示
4. 截取当前页面的截图
```

## 可用工具

| 类别     | 工具                        | 说明           |
| -------- | --------------------------- | -------------- |
| **导航** | `midscene_navigate`         | 导航到 URL     |
|          | `midscene_set_active_tab`   | 切换标签页     |
| **交互** | `midscene_aiTap`            | AI 智能点击    |
|          | `midscene_aiInput`          | AI 智能输入    |
|          | `midscene_aiScroll`         | AI 智能滚动    |
|          | `midscene_aiHover`          | AI 悬停        |
|          | `midscene_aiKeyboardPress`  | 按键操作       |
|          | `midscene_aiWaitFor`        | 智能等待       |
| **查询** | `midscene_aiAssert`         | AI 断言验证    |
|          | `midscene_aiLocate`         | 获取元素位置   |
|          | `midscene_location`         | 获取位置信息   |
|          | `midscene_screenshot`       | 截取屏幕截图   |
|          | `midscene_get_tabs`         | 获取标签页列表 |
|          | `midscene_get_console_logs` | 获取控制台日志 |
| **高级** | `midscene_aiQuery`          | 结构化数据提取 |
|          | `midscene_aiAsk`            | AI 问答        |
|          | `midscene_aiBoolean`        | 布尔值查询     |
|          | `midscene_aiNumber`         | 数值查询       |
|          | `midscene_aiString`         | 字符串查询     |

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

| 问题                 | 解决方案                                      |
| -------------------- | --------------------------------------------- |
| Node.js 服务无法启动 | 检查 Node.js 版本 >= 18，端口 3000 是否被占用 |
| Python 端无法连接    | 确保 Node.js 服务运行在 http://localhost:3000 |
| API 密钥错误         | 检查 `.env` 文件配置                          |
| Chrome 未找到        | 安装 Chrome 浏览器或设置 `CHROME_PATH`        |
| 操作超时             | 简化任务或增加超时时间                        |

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

## 资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [DeepSeek API](https://platform.deepseek.com/docs)
- [Midscene 文档](https://midscenejs.com)

## 许可证

MIT License
