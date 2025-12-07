# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个**混合 Node.js + Python 网页自动化框架**，结合了：
- **LangGraph** 用于 AI 智能体编排
- **DeepSeek LLM** 用于推理
- **Midscene.js** 用于 AI 驱动的视觉网页交互
- **Playwright** 用于浏览器自动化

此外，还包含 **XMind 转换工具**，可以将 XMind 思维导图格式的测试用例转换为自然语言测试文件。

该架构使用 Python 和 Node.js 组件之间的 HTTP + WebSocket 通信，实现稳定、功能丰富的网页自动化。

## 高层架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Python Agent (runner/)                    │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ LangGraph    │  │ DeepSeek LLM │  │ HTTP Client  │   │
│   │ Agent        │  │              │  │              │   │
│   └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │                                    │
        │ HTTP/WebSocket                     │
        ↓                                    ↓
┌─────────────────────────────────────────────────────────────┐
│                 Node.js Server (server/)                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │ Express API  │  │ WebSocket    │  │ Orchestrator │   │
│   │              │  │ Server       │  │              │   │
│   └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                           │
                                           ↓
                                  ┌──────────────────┐
                                  │ Midscene.js +    │
                                  │ Playwright       │
                                  │ (Browser Control)│
                                  └──────────────────┘
```

### 关键组件

**Python 端 (runner/):**
- `agent/agent.py` - 基于 LangGraph 的智能体，集成了 DeepSeek LLM
- `agent/http_client.py` - 用于与 Node.js 通信的异步 HTTP/WebSocket 客户端
- `agent/config.py` - 配置管理
- `agent/tools/definitions.py` - 网页自动化操作的工具定义
- `executor/yaml_executor.py` - YAML 测试文件执行器
- `executor/text_executor.py` - 自然语言测试文件执行器
- `converter/` - XMind 转换工具，将思维导图转换为自然语言测试文件
- `modes/` - 交互式菜单的模式模块
- `run.py` - 带有菜单的交互式启动器

**Node.js 端 (server/):**
- `src/index.ts` - 主服务器入口，集成 Express + WebSocket
- `src/orchestrator/` - Midscene 编排器模块化实现
  - `index.ts` - 编排器主类，会话管理
  - `session.ts` - 会话生命周期管理
  - `actions/execute.ts` - 网页操作执行器
  - `queries/execute.ts` - 页面查询执行器
  - `action-history.ts` - 操作历史记录
  - `system.ts` - 系统功能（健康检查、关闭等）
  - `config.ts` - 编排器配置
  - `types.ts` - 类型定义
- `src/websocket/` - WebSocket 服务器实现
  - `index.ts` - WebSocket 服务器创建
  - `connectionManager.ts` - 连接管理器
  - `handlers.ts` - 消息处理器
- `src/routes/` - HTTP 路由模块
  - `sessions.ts` - 会话管理路由
  - `health.ts` - 健康检查路由
  - `root.ts` - 根路由
- `src/middleware/` - Express 中间件
- `src/server/` - 服务器启动和关闭
- `src/config/` - 服务器配置
- `src/types/` - API 契约的 TypeScript 类型定义

**通信协议:**
- REST API 用于有状态操作（创建会话、执行操作/查询）
- WebSocket 用于实时流式传输操作进度
- 基于会话的状态管理

## 常用命令

### Node.js 服务器 (server/ 目录)

```bash
# 开发
npm run dev          # 启动带热重载的开发服务器 (使用 vite-node)
npm start            # 启动生产服务器

# 构建
npm run build        # 将 TypeScript 构建到 dist/

# 代码质量
npm run lint         # 运行 ESLint
npm run lint:fix     # 修复 ESLint 问题
npm run format       # 使用 Prettier 格式化
npm run format:check # 检查 Prettier 格式

# 类型检查
npm run typecheck    # TypeScript 类型检查

# 测试 (Jest)
npm test             # 运行 Jest 测试
npm run test:watch   # 以监视模式运行测试

# 综合质量检查
npm run quality      # lint + format:check + typecheck
npm run quality:fix  # lint:fix + format:write + typecheck
```

### Python 运行器 (runner/ 目录)

```bash
# 带有菜单的交互式启动器
python run.py

# 直接执行 YAML 测试
python -m executor.yaml_executor tests/yamls/basic_usage.yaml

# 直接执行自然语言测试
python -m executor.text_executor tests/texts/basic_usage.txt

# XMind 转换工具
python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/
python -m converter.cli -i xmind/ -o tests/texts/  # 批量转换目录

# 检查配置
python check_config.py
```

### Chat UI (chat/ 目录)

```bash
# 安装依赖 (推荐使用 pnpm)
cd chat
pnpm install

# 或使用 npm
npm install

# 开发模式
pnpm dev
# 或
npm run dev

# 生产构建
pnpm build
# 或
npm run build

# 代码质量检查
npm run lint
npm run lint:fix
npm run format
npm run format:check

# 类型检查
npm run typecheck
```

### 环境设置

```bash
# 1. 安装 Node.js 依赖
cd server
npm install

# 2. 安装 Python 依赖
cd ../runner
pip install -r requirements.txt

# 3. (可选) 安装 Chat UI 依赖
cd ../chat
pnpm install

# 4. 配置环境
cp .env.example .env
# 使用您的 API 密钥编辑 .env:
# - DEEPSEEK_API_KEY (必需)
# - OPENAI_API_KEY (用于 Midscene 视觉模型)
# - OPENAI_BASE_URL (用于 Midscene 视觉模型)
# - MIDSCENE_SERVER_URL (默认: http://localhost:3000)

# 5. 启动服务器
cd ../server
npm start

# 6. (可选) 启动 Chat UI
cd ../chat
pnpm dev

# 7. 在另一个终端运行测试
cd ../runner
python run.py
```

## 开发工作流

### 运行单个测试

```bash
# 方法 1: 使用交互式启动器
cd runner
python run.py
# 选择选项 1 或 3，然后选择特定测试

# 方法 2: 直接执行 YAML 测试
python -m executor.yaml_executor tests/yamls/basic_usage.yaml

# 方法 3: 直接执行自然语言测试
python -m executor.text_executor tests/texts/basic_usage.txt

# 方法 4: 自定义任务
python run.py
# 选择选项 5，输入自然语言指令
```

### 开发周期

1. **启动 Node.js 服务器** (在 `server/` 目录中):
   ```bash
   npm run dev
   ```

2. **运行/测试 Python 代码** (在 `runner/` 目录中):
   ```bash
   python -m executor.yaml_executor tests/yamls/your_test.yaml
   ```

3. **检查代码质量** (在 `server/` 目录中):
   ```bash
   npm run quality
   ```

### 会话管理

- 每个浏览器自动化任务都在一个**会话**中运行
- 会话通过 `POST /api/sessions` 创建
- 会话维护 Playwright 页面状态
- 会话可以在多个操作中重复使用
- 使用 `DELETE /api/sessions/:sessionId` 清理

### 可用工具

智能体提供以下工具类别:

**导航:**
- `midscene_navigate` - 导航到 URL
- `midscene_setActiveTab` - 切换浏览器标签页

**交互:**
- `midscene_aiTap` - AI 驱动的点击
- `midscene_aiInput` - AI 驱动的文本输入
- `midscene_aiScroll` - AI 驱动的滚动
- `midscene_aiHover` - 悬停在元素上
- `midscene_aiKeyboardPress` - 键盘操作
- `midscene_aiWaitFor` - 智能等待条件

**查询/断言:**
- `midscene_aiAssert` - 验证页面条件
- `midscene_aiQuery` - 提取结构化数据
- `midscene_aiAsk` - 使用 AI 查询页面
- `midscene_aiBoolean` - 获取布尔值答案
- `midscene_aiString` - 获取字符串值
- `midscene_aiNumber` - 获取数值
- `midscene_aiLocate` - 获取元素位置信息
- `midscene_location` - 获取当前 URL/标题
- `midscene_screenshot` - 截屏
- `midscene_getTabs` - 获取标签页列表
- `midscene_getConsoleLogs` - 获取控制台日志

## 配置

关键配置文件:
- `runner/.env` - Python 环境变量 (API 密钥、服务器 URL)
- `server/.env` - Node.js 环境变量 (端口、模型配置)
- `chat/.env.local` - Chat UI 环境变量 (可选)
- `.claude/settings.json` - Claude Code MCP 服务器配置

## 测试

### 测试格式

项目支持两种测试格式:

#### YAML 测试格式 (tests/yamls/)

结构化的测试定义，支持明确的操作类型:

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

#### 自然语言测试格式 (tests/texts/)

使用自然语言描述的测试，AI 自动规划执行:

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

### 测试文件

**YAML 测试** (位于 `tests/yamls/`):
- `basic_usage.yaml` - 基础自动化示例
- `github_interaction.yaml` - GitHub 自动化
- `baidu_query_demo.yaml` - 搜索查询演示
- `search_results_demo.yaml` - 搜索结果处理
- `httpbin_interaction.yaml` - HTTP 测试

**自然语言测试** (位于 `tests/texts/`):
- `basic_usage.txt` - 基础自动化示例
- `github_interaction.txt` - GitHub 自动化
- `baidu_query_demo.txt` - 搜索查询演示
- `search_results_demo.txt` - 搜索结果处理
- `httpbin_interaction.txt` - HTTP 测试

### XMind 转换工具

项目包含一个 **XMind 转换工具**，可以将 XMind 思维导图格式的测试用例转换为自然语言测试文件。

#### 功能特点

- ✅ **XMind → 自然语言测试文件**：将 XMind 思维导图转换为 tests/texts/ 格式
- ✅ **模块化输出**：每个模块生成独立的 .txt 文件
- ✅ **占位符配置**：@web 配置使用占位符，便于后续填写
- ✅ **零依赖**：仅使用 Python 标准库
- ✅ **批量转换**：支持单个文件或目录批量转换

#### 使用方法

**转换单个 XMind 文件**:
```bash
python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/
```

**批量转换目录**:
```bash
python -m converter.cli -i xmind/ -o tests/texts/
```

**详细输出模式**:
```bash
python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/ --verbose
```

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

## 关键 API 端点

**HTTP 路由 (server/src/index.ts):**
- `GET /api/health` - 健康检查
- `POST /api/sessions` - 创建会话
- `GET /api/sessions` - 列出活动会话
- `POST /api/sessions/:id/action` - 执行操作
- `POST /api/sessions/:id/query` - 查询页面
- `GET /api/sessions/:id/history` - 获取会话历史
- `DELETE /api/sessions/:id` - 销毁会话

**WebSocket:**
- `ws://localhost:3000` - 用于流式传输的 WebSocket 端点
- 消息类型: `subscribe`, `action`, `unsubscribe`

## 故障排除

**端口 3000 被占用:**
```bash
lsof -ti:3000 | xargs kill
```

**Node.js 版本:**
- 需要 Node.js >= 18 (使用 `node --version` 检查)

**Python 版本:**
- 需要 Python >= 3.10

**Chrome/Chromium:**
- Playwright 需要
- 安装 Chrome 或在 .env 中设置 `CHROME_PATH`

## 重要提示

- 服务器必须在执行 Python 测试**之前**运行
- Chat UI 是可选的，提供可视化界面与智能体交互
- 每个测试创建自己的 Midscene 会话
- WebSocket 流式传输在智能体配置中默认启用
- 会话是隔离的 - 一个会话中的操作不会影响其他会话
- 日志写入 `server/logs/` (error.log, combined.log)

## 项目结构

```
midscene-agent/
├── server/                  # Node.js HTTP/WebSocket 服务器
│   ├── src/
│   │   ├── index.ts         # 主服务器入口
│   │   ├── orchestrator/    # Midscene 编排器
│   │   │   ├── index.ts         # 编排器主类
│   │   │   ├── session.ts       # 会话管理
│   │   │   ├── actions/         # 操作执行
│   │   │   │   └── execute.ts
│   │   │   ├── queries/         # 查询执行
│   │   │   │   └── execute.ts
│   │   │   ├── action-history.ts # 历史记录
│   │   │   ├── system.ts        # 系统功能
│   │   │   ├── config.ts        # 配置
│   │   │   └── types.ts         # 类型
│   │   ├── websocket/       # WebSocket 支持
│   │   │   ├── index.ts
│   │   │   ├── connectionManager.ts
│   │   │   └── handlers.ts
│   │   ├── routes/          # HTTP 路由
│   │   │   ├── sessions.ts
│   │   │   ├── health.ts
│   │   │   └── index.ts
│   │   ├── middleware/      # Express 中间件
│   │   ├── server/          # 服务器控制
│   │   │   ├── start.ts
│   │   │   └── shutdown.ts
│   │   ├── config/          # 服务器配置
│   │   └── types/           # TypeScript 定义
│   ├── package.json
│   └── dist/                # 构建输出
├── runner/                  # Python LangGraph 智能体
│   ├── agent/
│   │   ├── agent.py         # 主智能体
│   │   ├── http_client.py   # HTTP 客户端
│   │   ├── config.py        # 配置管理
│   │   ├── tools/           # 工具定义
│   │   │   └── definitions.py
│   │   └── utils/           # 工具函数
│   ├── executor/            # 测试执行器
│   │   ├── yaml_executor.py # YAML 测试执行器
│   │   └── text_executor.py # 自然语言测试执行器
│   ├── converter/           # XMind 转换工具
│   │   ├── __init__.py
│   │   ├── cli.py           # 命令行接口
│   │   ├── models.py        # 数据模型
│   │   ├── xmind_parser.py  # XMind 文件解析器
│   │   ├── text_generator.py # 自然语言文本生成器
│   │   ├── utils.py         # 工具函数
│   │   └── exceptions.py    # 异常处理
│   ├── modes/               # 交互式菜单模式
│   │   ├── yaml_mode.py     # YAML 测试模式
│   │   ├── text_mode.py     # 自然语言测试模式
│   │   └── custom_mode.py   # 自定义任务模式
│   ├── yamls/               # YAML 测试文件
│   ├── texts/               # 自然语言测试文件
│   ├── run.py               # 交互式启动器
│   ├── check_config.py      # 配置检查器
│   └── requirements.txt     # Python 依赖
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
├── .claude/
│   └── settings.json        # MCP 服务器配置
└── README.md                # 项目文档
```
