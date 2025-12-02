# LangChain/LangGraph 1.0.0+ 升级指南

本项目已升级以兼容 **LangChain 1.0.0+** 和 **LangGraph 1.0.0+**。

## 🔄 关键变更

### 1. 依赖版本更新

**之前（0.x 版本）:**
```text
langchain>=0.2.0
langgraph>=0.1.0
```

**现在（1.0.0+ 版本）:**
```text
langchain>=1.0.0
langgraph>=1.0.0
```

### 2. 消息格式更新

**旧版本 (0.x):**
```python
{"messages": [("user", "Your message here")]}
```

**新版本 (1.0.0+):**
```python
from langchain_core.messages import HumanMessage

{"messages": [HumanMessage(content="Your message here")]}
```

### 3. 输出格式更新

**旧版本 (0.x):**
```python
message.pretty_print()
```

**新版本 (1.0.0+):**
```python
if hasattr(message, "content"):
    print(message.content)
else:
    print(message)
```

## ✅ 兼容性处理

本项目已自动处理所有兼容性变更：

1. **MCP Wrapper (`mcp_wrapper.py`)** - 无需修改
2. **Agent 核心 (`agent.py`)** - 已更新消息格式
3. **示例代码 (`examples/`)** - 已更新所有输出格式
4. **启动器 (`run.py`)** - 已更新所有输出格式

## 🚀 安装和运行

### 全新安装

```bash
# 1. 克隆项目
git clone <your-repo>
cd midscene

# 2. 安装 Python 依赖（最新版本）
pip install -r requirements.txt

# 3. 安装 Midscene
npm install -g @midscene/web

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 添加您的 DEEPSEEK_API_KEY

# 5. 运行
python run.py
```

### 从 0.x 版本升级

如果您之前使用的是 0.x 版本，需要：

```bash
# 1. 升级依赖
pip install --upgrade -r requirements.txt

# 2. 清理缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 3. 重新安装（如果使用了开发模式）
pip uninstall -y midscene-langgraph-agent
pip install -e .
```

## 🧪 测试兼容性

### 快速测试

```python
import asyncio
from agent import MidsceneAgent

async def test():
    agent = MidsceneAgent(deepseek_api_key="your-key")
    await agent.initialize()
    print("✅ 兼容性测试通过！")
    await agent.cleanup()

asyncio.run(test())
```

### 运行完整测试

```bash
python examples/basic_usage.py
```

## 📋 已更新的文件列表

- ✅ `agent.py` - 使用 HumanMessage 格式
- ✅ `examples/basic_usage.py` - 更新输出格式
- ✅ `examples/test_ecommerce.py` - 更新输出格式
- ✅ `run.py` - 更新输出格式
- ✅ `requirements.txt` - 升级到 1.0.0+

## ⚠️ 注意事项

1. **Python 版本**: LangChain 1.0.0+ 需要 Python >= 3.10
2. **API 密钥**: 确保您的 DeepSeek API 密钥有效
3. **浏览器**: Midscene 需要 Chrome 浏览器
4. **Node.js**: Midscene MCP Server 需要 Node.js >= 18

## 🔧 如果遇到问题

### 导入错误

```
ImportError: cannot import name 'tool' from 'langchain_core.tools'
```

**解决方案**: 确保已升级到 LangChain 1.0.0+

```bash
pip install --upgrade langchain langchain-core langchain-openai langgraph
```

### 消息格式错误

```
TypeError: expected string or bytes-like object
```

**解决方案**: 使用 `HumanMessage` 而不是元组格式

```python
from langchain_core.messages import HumanMessage

# ✅ 正确
messages = [HumanMessage(content="Your message")]

# ❌ 错误（0.x 格式）
messages = [("user", "Your message")]
```

### 打印错误

```
AttributeError: 'BaseMessage' object has no attribute 'pretty_print'
```

**解决方案**: 使用 `content` 属性

```python
# ✅ 正确
print(message.content)

# ❌ 错误（0.x 格式）
message.pretty_print()
```

## 📚 参考文档

- [LangChain 1.0 迁移指南](https://python.langchain.com/docs/versions/migrating_guidance/)
- [LangGraph 1.0 文档](https://langchain-ai.github.io/langgraph/)
- [Midscene 文档](https://midscene.org)

## 🎯 下一步

1. 运行 `python run.py` 体验新版本
2. 查看 `examples/` 中的更新示例
3. 阅读 `README.md` 了解完整功能
4. 根据需要自定义配置

---

**版本**: 1.0.0+ 兼容
**最后更新**: 2024-12-02
