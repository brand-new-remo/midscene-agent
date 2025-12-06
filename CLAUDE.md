# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概览

**Midscene LangGraph Agent** - 一个混合型 AI 驱动的网页自动化系统，结合 LangGraph 进行智能编排、DeepSeek LLM 进行推理，以及 Midscene.js 进行基于视觉的网页交互。

### 架构

本项目采用 **混合 Node.js + Python 架构**，使用 HTTP + WebSocket 通信：

```
┌─────────────────────────────────────────────────────────────┐
│  Python 层 (Agent)                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MidsceneAgent (LangGraph StateGraph)                  │ │
│  │  - 状态管理                                             │ │
│  │  - 工具编排                                             │ │
│  │  - DeepSeek LLM 集成                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↕ (HTTP + WebSocket)                │
┌─────────────────────────────────────────────────────────────┐
│  Node.js 层 (Server)                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MidsceneOrchestrator                                  │ │
│  │  - 会话管理                                             │ │
│  │  - 动作执行                                             │ │
│  │  - 查询处理                                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  Midscene.js + Playwright                                  │
│  - 浏览器自动化                                             │
│  - 基于视觉的元素检测                                       │
└─────────────────────────────────────────────────────────────┘
```

## 开发命令

### Node.js 服务器 (server/)

```bash
# 开发
cd server
npm run dev          # 启动开发模式，支持热重载
npm run build        # 使用 Vite 构建（输出到 dist/）
npm start            # 启动生产服务器

# 代码质量
npm run typecheck    # TypeScript 类型检查
npm run lint         # ESLint 检查
npm run lint:fix     # 自动修复 ESLint 问题
npm run format       # Prettier 代码格式化
npm run format:check # 检查格式化
npm run quality      # 运行 lint + format + typecheck
npm run quality:fix  # 修复所有质量问题

# 测试
npm test             # 运行 Jest 测试
npm run test:watch   # 监听模式测试
```

### Python Agent (agent/)

```bash
# 安装
pip install -r requirements.txt

# 运行示例
cd agent
python run.py                    # 交互式启动器
python examples/basic_usage.py   # 基础自动化示例
python examples/search_results_demo.py  # 搜索演示
python examples/ai_action_demo.py       # AI 动作演示
```

## 项目结构

### 核心目录

- **server/src/** - Node.js TypeScript 服务器
  - `index.ts` - 主 Express 服务器 + WebSocket 处理器
  - `orchestrator.ts` - Midscene 会话和动作管理器
  - `types/` - TypeScript 类型定义

- **agent/src/** - Python LangGraph agent
  - `agent.py` - 带 StateGraph 的主 LangGraph agent
  - `http_client.py` - HTTP + WebSocket 客户端
  - `config.py` - 配置管理
  - `tools/definitions.py` - LangGraph 工具定义

- **agent/examples/** - 示例使用脚本
  - `basic_usage.py` - 基础自动化任务
  - `search_results_demo.py` - 网页搜索自动化
  - `ai_action_demo.py` - AI 驱动的动作

### 关键文件

- **server/package.json** - Node.js 依赖和脚本
- **server/tsconfig.json** - TypeScript 配置
- **server/vite.config.ts** - Vite 构建配置
- **agent/requirements.txt** - Python 依赖
- **agent/.env** - 环境变量（本地配置）

## 核心组件

### 1. MidsceneAgent (Python)

**文件**: `agent/src/agent.py`

- **LangGraph StateGraph**: 编排多步骤自动化任务
- **工具集成**: 将 Midscene 操作暴露为 LangChain 工具
- **DeepSeek LLM**: 主要推理引擎
- **WebSocket 支持**: 实时流式传输执行进度

**关键方法**:
- `execute(task, stream=False)` - 执行自动化任务
- `query(query_type, params)` - 查询页面信息
- 会话上下文管理器用于资源清理

### 2. MidsceneOrchestrator (Node.js)

**文件**: `server/src/orchestrator.ts`

- **会话管理**: 创建/管理 Playwright 浏览器会话
- **动作执行**: 将 LangGraph 工具映射到 Midscene 操作
- **查询处理**: 处理页面查询（aiAssert、aiQuery、aiAsk 等）
- **WebSocket 流式传输**: 实时向 Python 客户端推送进度更新

**支持的动作**:
- 导航: `navigate`, `setActiveTab`
- 交互: `aiTap`, `aiInput`, `aiScroll`, `aiHover`, `aiKeyboardPress`
- 查询: `aiAssert`, `aiQuery`, `aiAsk`, `aiBoolean`, `aiNumber`, `aiString`
- 工具: `logScreenshot`, `location`, `getTabs`, `getConsoleLogs`

### 3. HTTP 客户端 (Python)

**文件**: `agent/src/http_client.py`

- **异步 HTTP**: 基于 aiohttp 的 REST API 通信
- **WebSocket**: 实时事件流传输
- **会话管理**: 创建/管理服务器端会话
- **错误处理**: 连接重试和错误传播

### 4. 服务器 (Node.js)

**文件**: `server/src/index.ts`

- **Express REST API**: `/health`, `/sessions`, `/execute`, `/query`
- **WebSocket 服务器**: `/ws` 端点用于流式传输
- **CORS 支持**: 来自 Python 客户端的跨域请求
- **优雅关闭**: 进程终止时的清理

## TypeScript 类型定义

**目录**: `server/src/types/`

- `action.ts` - 动作类型和参数
- `query.ts` - 查询类型和响应
- `session.ts` - 会话状态管理
- `api.ts` - REST API 接口
- `websocket.ts` - WebSocket 消息类型
- `index.ts` - 中央导出中心

## 配置

### 环境变量 (.env)

**必需**:
- `DEEPSEEK_API_KEY` - DeepSeek LLM API 密钥
- `OPENAI_API_KEY` - 视觉模型 API 密钥
- `OPENAI_BASE_URL` - 视觉模型端点

**可选**:
- `DEEPSEEK_BASE_URL` - DeepSeek API 端点（默认: https://api.deepseek.com/v1）
- `DEEPSEEK_MODEL` - DeepSeek 模型（默认: deepseek-chat）
- `MIDSCENE_MODEL_NAME` - 视觉模型（默认: doubao-seed-1.6-vision）
- `MIDSCENE_SERVER_URL` - 服务器 URL（默认: http://localhost:3000）
- `HEADLESS` - 浏览器模式（默认: true 用于生产）

## 开发工作流

### 典型开发会话

```bash
# 1. 启动 Node.js 服务器（终端 1）
cd server
npm run dev  # 或 npm start 用于生产

# 2. 运行 Python 示例（终端 2）
cd agent
python run.py  # 从菜单选择示例

# 3. 或运行特定示例
python examples/basic_usage.py

# 4. 使用可见浏览器调试
# 编辑 examples/basic_usage.py: 设置 headless=False

# 5. 提交前检查代码质量
cd server
npm run quality:fix
```

### 测试更改

```bash
# 类型检查
cd server && npm run typecheck

# 格式化和检查
cd server && npm run quality:fix

# 运行示例并查看调试输出
cd agent && python examples/basic_usage.py
```

## 工具定义

**文件**: `agent/src/tools/definitions.py`

工具定义为 LangChain 兼容工具，包含:
- `name`: 工具标识符（例如，`midscene_aiTap`）
- `description`: 人类可读的描述
- `parameters`: 工具参数的 JSON Schema
- `execute`: 映射到 Midscene orchestrator 方法

## 关键实现细节

### 1. WebSocket 事件流

```
Python Agent                      Node.js Server
     │                                  │
     ├─ connect WebSocket ──────────────→
     │                                  │
     ├─ execute_action ----------------─→
     │                                  │ executeAction()
     │                                  │ send: action_start
     │←───────── action_start ──────────┤
     │                                  │
     │ (action execution)               │
     │                                  │
     │←──────── action_complete ────────┤
     │                                  │
```

### 2. 会话生命周期

```
createSession()
  ├─ Launch Chromium browser
  ├─ Create Playwright page
  ├─ Initialize Midscene PlaywrightAgent
  └─ Store in orchestrator.sessions Map

destroySession()
  ├─ Call agent.destroy()
  ├─ Close browser
  └─ Remove from sessions Map
```

### 3. StateGraph 工作流

```
START
  ↓
Agent receives task
  ↓
LLM plans steps + selects tools
  ↓
For each tool call:
  ├─ ToolNode executes
  ├─ HTTP POST to /execute
  ├─ Orchestrator performs action
  └─ Return result to LLM
  ↓
LLM determines if done
  ↓
END
```

## 构建系统

### Node.js (Vite)

- **ESM 模块系统**: package.json 中的 `"type": "module"`
- **Bundle 目标**: Node.js 18+
- **构建输出**: `server/dist/index.js`
- **TypeScript**: 启用严格模式
- **外部依赖**: 浏览器/服务器运行时库从 bundle 中排除

### Python

- **标准打包**: 无需构建步骤
- **直接导入**: `src/` 目录中的 Python 文件
- **示例**: 带有环境加载的自包含脚本

## 已知约束

1. **Node 版本**: 需要 Node.js >= 18（ES2022 特性）
2. **浏览器依赖**: 必须安装 Chrome/Chromium
3. **端口冲突**: 服务器默认使用端口 3000
4. **API 密钥**: 需要有效的 DeepSeek 和视觉模型 API 密钥
5. **无测试套件**: 虽然配置了 Jest，但不存在实际测试
6. **混合架构**: Node.js 和 Python 必须同时运行

## 常见问题与解决方案

### 端口已被占用
```bash
# 查找使用端口 3000 的进程
lsof -ti:3000

# 终止进程
kill -9 $(lsof -ti:3000)
```

### TypeScript 编译错误
```bash
cd server
npm run typecheck  # 检查错误
npm run quality:fix  # 修复格式化和 linting
```

### Python 导入错误
```bash
# 确保你在 agent 目录中
cd agent
python -c "import sys; print(sys.path)"
```

### 浏览器无法启动
```bash
# 安装 Playwright 浏览器
cd server
npx playwright install chromium
```

## 性能考虑

1. **会话重用**: 会话被缓存；尽可能重用
2. **无头模式**: 生产环境设置 `headless: true`
3. **连接池**: HTTP 客户端使用持久连接
4. **异步操作**: 所有 Python 操作都是 async/await
5. **WebSocket 流式传输**: 相比轮询减少延迟

## 架构决策

1. **HTTP + WebSocket vs. MCP**: 更稳定、更好的调试、完整功能支持
2. **混合 Node.js + Python**: 利用 Midscene.js (Node) 与 LangGraph (Python)
3. **LangGraph StateGraph**: 内置多步骤任务工作流编排
4. **Vite 构建**: 快速开发、摇树优化、目标 Node 18+
5. **TypeScript**: 跨 Node.js 边界的完整类型安全
