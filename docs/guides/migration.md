# Midscene Agent  迁移指南

本指南帮助您从 V1.0 迁移到 ，充分利用新架构的优势。

## 📋 迁移概览

### 主要变化

| 方面 | V1.0 |  |
|------|------|------|
| **通信协议** | MCP stdio | HTTP + WebSocket |
| **稳定性** | 中等 | 高 |
| **功能完整性** | 有限 | 完整 |
| **实时反馈** | 无 | 有 |
| **会话管理** | 无 | 有 |
| **监控能力** | 无 | 完整 |

### 迁移收益

✅ **更稳定**: HTTP 比 stdio 更可靠
✅ **更强大: 完整 Midscene.js API 支持
✅ **更智能: 实时流式响应
✅ **更易用: 会话管理和监控
✅ **更可扩展: 微服务架构

## 🚀 快速迁移

### 步骤 1: 安装 Node.js 服务

```bash
# 进入项目目录
cd /path/to/midscene-agent

# 安装 Node.js 依赖
cd server
npm install
cd ..
```

### 步骤 2: 更新代码

#### V1.0 旧代码
```python
from src.agent import MidsceneAgent

agent = MidsceneAgent(
    deepseek_api_key="your-api-key",
    deepseek_base_url="https://api.deepseek.com/v1",
)
```

####  新代码
```python
from src.agent_v2 import MidsceneAgent

agent = MidsceneAgent(
    deepseek_api_key="your-api-key",
    deepseek_base_url="https://api.deepseek.com/v1",
    midscene_server_url="http://localhost:3000",
    enable_websocket=True,
    tool_set="full"
)
```

### 步骤 3: 启动服务

```bash
# 终端 1: 启动 Node.js 服务
cd server
npm start
# 服务运行在 http://localhost:3000

# 终端 2: 运行您的应用
python your_app.py
```

## 📝 详细变更

### 1. Agent 类导入

```diff
- from src.agent import MidsceneAgent
+ from src.agent_v2 import MidsceneAgent
```

### 2. 实例化参数

```diff
agent = MidsceneAgent(
    deepseek_api_key="your-api-key",
    deepseek_base_url="https://api.deepseek.com/v1",
+   midscene_server_url="http://localhost:3000",
+   midscene_config={
+       "model": "doubao-seed-1.6-vision",
+       "headless": False
+   },
+   tool_set="full",
+   enable_websocket=True
)
```

### 3. API 保持兼容

 保持了 V1.0 的核心 API：

```python
async with agent:
    task = "访问 https://example.com 并搜索内容"
    async for event in agent.execute(task):
        if "messages" in event:
            print(event["messages"][-1].content)
```

## 🔧 新功能使用

### 1. WebSocket 流式响应

```python
# 启用 WebSocket 获得实时反馈
agent = MidsceneAgent(
    enable_websocket=True
)

async with agent:
    async for event in agent.execute(task, stream=True):
        # 实时接收执行进度
        if "messages" in event:
            print(f"📡 [实时] {event['messages'][-1].content}")
```

### 2. 会话管理

```python
# 获取会话信息
session_info = await agent.get_session_info()
print(f"活跃会话: {len(session_info['active_sessions'])}")
print(f"动作历史: {len(session_info['session_history'])}")

# 健康检查
health = await agent.health_check()
print(f"服务状态: {health['status']}")
```

### 3. 直接 HTTP 访问

```python
# 绕过 LangGraph，直接使用 HTTP 客户端
result = await agent.http_client.execute_action(
    "navigate",
    {"url": "https://example.com"}
)

# 查询页面信息
query_result = await agent.http_client.execute_query(
    "aiQuery",
    {
        "dataDemand": {"title": "string", "links": "string[]"},
        "options": {"domIncluded": True}
    }
)
```

### 4. 完整工具集

```python
# 使用完整工具集
agent = MidsceneAgent(tool_set="full")

# 所有工具都可用：
# - midscene_aiTap, midscene_aiInput, midscene_aiScroll
# - midscene_aiAssert, midscene_location, midscene_screenshot
# - midscene_aiQuery, midscene_aiAsk, midscene_aiBoolean
# - 等等...
```

## 🐳 Docker 部署

### 单服务部署

```bash
# 启动 Node.js 服务
docker-compose up midscene-server -d

# 运行 Python 应用
docker-compose up midscene-python -d
```

### 完整栈部署（带监控）

```bash
# 启动所有服务
docker-compose --profile monitoring up -d

# 访问
# - Python 应用: http://localhost:8000
# - Node.js 服务: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)
```

## 📊 监控指标

### Prometheus 指标

```bash
# 查看指标
curl http://localhost:3000/metrics

# 关键指标
# - midscene_actions_total: 动作执行总数
# - midscene_action_duration_seconds: 动作执行时间
# - midscene_active_sessions: 活跃会话数
# - midscene_http_requests_total: HTTP 请求数
```

### 日志查看

```bash
# Node.js 服务日志
docker-compose logs -f midscene-server

# Python 应用日志
docker-compose logs -f midscene-python
```

## 🧪 测试迁移

### 运行测试

```bash
# 运行  基础示例
python examples/basic_usage_v2.py

# 运行查询示例
python -c "
import asyncio
from examples.basic_usage_v2 import query_example
asyncio.run(query_example())
"
```

### 性能对比

```bash
# 对比测试
echo "V1.0 测试..."
python examples/test_ecommerce.py

echo " 测试..."
python examples/basic_usage_v2.py
```

## ⚠️ 注意事项

### 1. 端口冲突

确保 Node.js 服务端口（默认 3000）未被占用：

```bash
# 检查端口
lsof -i :3000

# 如果被占用，修改 docker-compose.yml
services:
  midscene-server:
    ports:
      - "3001:3000"  # 改为 3001
```

### 2. 环境变量

确保 `.env` 文件包含必要的变量：

```bash
# DeepSeek API（必需）
DEEPSEEK_API_KEY=your-key

# Midscene 视觉模型
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=your-url
MIDSCENE_MODEL_NAME=doubao-seed-1.6-vision

# 新增：Node.js 服务地址
MIDSCENE_SERVER_URL=http://localhost:3000
```

### 3. 向后兼容性

 完全向后兼容，您可以：

```python
# 使用别名保持现有代码不变
from src.agent_v2 import MidsceneAgent as MidsceneAgent

# 或者逐步迁移
from src.agent_v2 import MidsceneAgent  # 新功能
from src.agent import MidsceneAgent       # 旧功能
```

## 🔄 渐进式迁移策略

### 阶段 1: 并行运行
- 保持 V1.0 正常运行
- 启动  服务
- 在测试环境验证 

### 阶段 2: 双写模式
- 新旧版本同时处理请求
- 比较结果一致性
- 监控性能和稳定性

### 阶段 3: 完全迁移
- 切换到 
- 保留 V1.0 作为备用
- 逐步移除旧代码

## 📞 获取帮助

### 常见问题

**Q: Node.js 服务无法启动**
A: 检查 Node.js 版本（需要 >= 18）和端口占用

**Q: WebSocket 连接失败**
A: 确保 Node.js 服务正常运行，客户端会自动降级到 HTTP

**Q: 工具调用失败**
A: 检查 Midscene 配置和 API 密钥是否正确

### 资源

- 📖 [完整文档](./README.md)
- 🐛 [问题报告](https://github.com/your-repo/issues)
- 💬 [讨论区](https://github.com/your-repo/discussions)

## 🎉 迁移完成

恭喜！您已成功迁移到 。现在可以享受：

- ✅ 更稳定可靠的性能
- ✅ 更强大的功能
- ✅ 更好的监控和调试
- ✅ 更流畅的开发体验

欢迎使用 Midscene Agent ！ 🚀