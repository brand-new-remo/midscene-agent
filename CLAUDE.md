# Midscene LangGraph Agent - Claude Code 记忆文件

## 📋 项目概览

**项目名称**: Midscene LangGraph Agent
**版本**: 现代化架构 (HTTP + WebSocket)
**最后更新**: 2025-12-05

一个 AI 驱动的网页自动化智能体，结合 LangGraph 进行智能编排、DeepSeek LLM 进行推理，以及 Midscene 进行基于视觉的网页交互。

## 🏗️ 当前架构

### 技术栈
- **Node.js 服务层**: Express + WebSocket + Midscene.js + Playwright
- **Python 客户端**: aiohttp + LangGraph + DeepSeek LLM
- **通信协议**: HTTP + WebSocket (替代不稳定的 MCP stdio)
- **浏览器自动化**: Midscene.js + Playwright
- **LLM**: DeepSeek Chat
- **流程编排**: LangGraph StateGraph

### 核心文件结构

```
midscene-agent/
├── src/                          # Python 源码
│   ├── agent.py                  # LangGraph Agent (主类: MidsceneAgent)
│   ├── http_client.py            # HTTP + WebSocket 客户端
│   ├── config.py                 # 配置管理
│   └── tools/                    # 工具模块
│       └── definitions.py        # 工具定义
├── server/                       # Node.js 服务
│   ├── src/
│   │   ├── index.js              # 主服务器 (Express + WebSocket)
│   │   ├── orchestrator.js       # Midscene 会话管理
│   │   └── metrics.js            # Prometheus 监控
│   └── package.json              # Node.js 依赖
├── examples/                     # 示例
│   ├── basic_usage.py            # 基础使用示例
│   └── search_results_demo.py    # 搜索演示
├── docs/                         # 文档
│   ├── architecture/             # 架构文档
│   ├── guides/                   # 使用指南
│   ├── FINAL_SUMMARY.md          # 重构总结
│   ├── PROJECT_STRUCTURE.md      # 项目结构
│   └── UPGRADE_GUIDE.md          # 升级指南
├── run.py                        # 交互式启动器
├── test.py                       # 测试脚本
├── start.sh                      # 快速启动脚本
├── requirements.txt              # Python 依赖
└── .env.example                  # 环境变量模板
```

## 🎯 核心特性

- **🚀 混合架构**: Node.js + Python 完美融合
- **🌐 HTTP + WebSocket**: 更稳定的通信协议
- **📡 流式响应**: 实时查看执行进度
- **🔧 完整功能**: 充分利用 Midscene.js 所有 API
- **📊 监控指标**: 内置 Prometheus 监控

## 🔧 关键设计决策

### 1. 从 MCP stdio 到 HTTP + WebSocket
- **原因**: MCP stdio 不稳定，限制功能
- **解决方案**: 使用 HTTP REST API + WebSocket 流式响应
- **优势**: 更稳定、功能更完整、更易调试

### 2. 混合架构 (Node.js + Python)
- **Node.js**: 处理浏览器自动化和会话管理
- **Python**: 处理 AI 推理和流程控制
- **通信**: HTTP + WebSocket

### 3. 移除版本标记
- **决策**: 不强调 V1.0 或 V2.0
- **原因**: 保持代码纯净，强调当下
- **实现**: 移除所有 "_V2" 后缀和版本引用

### 4. 简化部署
- **移除 Docker**: 当前阶段不需要容器化
- **直接运行**: 开发环境直接启动服务
- **原因**: 降低复杂度，更快迭代

## 📦 依赖管理

### Python 依赖 (requirements.txt)
```
langchain>=0.1.0
langchain-deepseek>=0.2.0
langgraph>=0.0.20
aiohttp>=3.9.0
python-dotenv>=1.0.0
```

### Node.js 依赖 (server/package.json)
```json
{
  "@midscene/web": "^0.30.9",
  "playwright": "^1.57.0",
  "express": "^5.2.1",
  "ws": "^8.18.3",
  "winston": "^3.18.3",
  "prom-client": "^15.0.0"
}
```

**重要**: @midscene/web 版本必须是 ^0.30.9 (不存在 ^2.0.0)

## 🚀 快速启动

### 1. 安装依赖
```bash
# Node.js
cd server && npm install

# Python
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 添加 DEEPSEEK_API_KEY
```

### 3. 启动服务
```bash
# 终端 1: 启动 Node.js 服务
cd server && npm start

# 终端 2: 运行 Python 示例
python examples/basic_usage.py

# 或使用交互式启动器
python run.py
```

## 🧪 测试

### 运行测试
```bash
python test.py
```

### 测试覆盖
- ✅ Node.js 服务器健康检查
- ✅ HTTP 客户端功能
- ✅ Agent 执行流式响应
- ✅ 会话管理
- ✅ 错误处理

## 🔍 常用操作

### 1. 自定义任务
```python
from src.agent import MidsceneAgent

agent = MidsceneAgent(
    deepseek_api_key="your-key",
    midscene_server_url="http://localhost:3000",
    enable_websocket=True
)

async with agent:
    async for event in agent.execute("访问 https://example.com", stream=True):
        print(event)
```

### 2. 监控指标
```bash
# Prometheus 指标
curl http://localhost:3000/metrics
```

### 3. 查看日志
```bash
# Node.js 服务日志
cd server && npm start

# 日志包含:
# - HTTP 请求
# - WebSocket 连接
# - Midscene 操作
# - 错误信息
```

## ⚠️ 已知限制

1. **浏览器依赖**: 需要 Chrome/Chromium 浏览器
2. **网络要求**: 需要访问 DeepSeek API
3. **端口占用**: Node.js 服务默认使用 3000 端口
4. **会话管理**: 长任务可能需要超时设置

## 🔄 重构历史

### V1.0 (已移除)
- 使用 MCP stdio 通信
- 功能受限，不稳定
- 包含: agent.py, mcp_wrapper.py, run.py (旧版)

### 当前版本 (现代化架构)
- HTTP + WebSocket 通信
- 完整功能集
- 移除版本标记
- 移除 Docker (简化部署)

## 📚 相关文档

- **README.md**: 项目主要文档和快速开始
- **docs/architecture/overview.md**: 详细架构说明
- **docs/FINAL_SUMMARY.md**: 重构总结
- **docs/guides/migration.md**: 迁移指南
- **examples/basic_usage.py**: 基础使用示例

## 🛠️ 开发者提示

### 调试技巧
1. **启用详细日志**: 设置 `LOG_LEVEL=debug`
2. **WebSocket 监控**: 使用浏览器开发者工具 Network 面板
3. **浏览器可见**: 设置 `headless: False` 观察操作
4. **Prometheus 指标**: 监控 `/metrics` 端点

### 性能优化
1. **会话复用**: 避免频繁创建新会话
2. **连接池**: HTTP 客户端使用连接池
3. **异步处理**: 所有操作都是异步的
4. **流式响应**: 使用 WebSocket 减少延迟

### 常见问题
1. **端口占用**: 修改 `server/src/index.js` 中的端口
2. **API 密钥**: 确保 `.env` 文件正确配置
3. **浏览器启动**: 检查 Chrome/Chromium 安装
4. **网络问题**: 配置代理或使用国内 API 镜像

## 🎯 下一步计划

1. **生产部署**: 考虑重新引入 Docker (未来)
2. **性能测试**: 添加基准测试和性能监控
3. **更多示例**: 扩展示例用例
4. **文档完善**: 添加更多使用指南

## 📞 联系信息

- **项目**: Midscene LangGraph Agent
- **架构**: Node.js + Python 混合架构
- **最后更新**: 2025-12-05

---
*此文件由 Claude Code 自动生成和维护*
