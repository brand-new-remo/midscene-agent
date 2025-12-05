# Midscene.js 完整 API 使用指南

## 📚 概述

本文档详细说明了项目中已实现的 **23 个 Midscene.js API** 的使用方法。所有 API 都可以通过 Python LangGraph Agent 调用。

---

## 🎯 核心 API (必须掌握)

### 1. `midscene_ai_action` - AI 自动规划执行 ⭐️⭐️⭐️

**最重要的 API** - 让 AI 自动规划并执行一系列 UI 动作。

```python
from src.agent import MidsceneAgent

agent = MidsceneAgent(...)

# 简单任务
await agent.execute(
    "访问 https://github.com，搜索 'midscene'，然后点击第一个结果"
)

# 复杂任务
await agent.execute(
    """
    执行以下操作：
    1. 访问 https://example.com
    2. 在搜索框输入 "Hello World"
    3. 点击搜索按钮
    4. 截取屏幕截图
    5. 告诉我搜索结果的数量
    """
)
```

**参数:**
- `prompt` (str): 自然语言描述的任务
- `cacheable` (bool, optional): 是否启用缓存，默认 True

---

## 🖱️ 交互 API

### 2. `midscene_navigate` - 导航

```python
await agent.tools['midscene_navigate'].ainvoke({
    "url": "https://example.com"
})
```

### 3. `midscene_aiTap` - 点击

```python
await agent.tools['midscene_aiTap'].ainvoke({
    "locate": "登录按钮"
})
```

### 4. `midscene_aiDoubleClick` - 双击

```python
await agent.tools['midscene_aiDoubleClick'].ainvoke({
    "locate": "文件图标"
})
```

### 5. `midscene_aiRightClick` - 右键点击

```python
await agent.tools['midscene_aiRightClick'].ainvoke({
    "locate": "图片"
})
```

### 6. `midscene_aiInput` - 输入文本

```python
await agent.tools['midscene_aiInput'].ainvoke({
    "locate": "搜索框",
    "value": "要输入的文本"
})
```

### 7. `midscene_aiScroll` - 滚动

```python
await agent.tools['midscene_aiScroll'].ainvoke({
    "direction": "down",  # up, down, left, right
    "scrollType": "once",  # once, untilBottom, untilTop
    "distance": 500
})
```

### 8. `midscene_aiKeyboardPress` - 按键

```python
await agent.tools['midscene_aiKeyboardPress'].ainvoke({
    "key": "Enter",  # Enter, Tab, Escape, 等
    "locate": "输入框"  # 可选
})
```

### 9. `midscene_aiHover` - 悬停

```python
await agent.tools['midscene_aiHover'].ainvoke({
    "locate": "菜单项"
})
```

### 10. `midscene_aiWaitFor` - 等待条件

```python
await agent.tools['midscene_aiWaitFor'].ainvoke({
    "assertion": "页面加载完成",
    "timeoutMs": 30000,  # 可选，默认 30000ms
    "checkIntervalMs": 1000  # 可选，默认 1000ms
})
```

---

## 🔍 查询和验证 API

### 11. `midscene_aiAssert` - 断言

```python
result = await agent.tools['midscene_aiAssert'].ainvoke({
    "assertion": "页面标题是 Example Domain"
})
```

### 12. `midscene_location` - 获取位置

```python
result = await agent.tools['midscene_location'].ainvoke({})
# 返回: { url, title }
```

### 13. `midscene_screenshot` - 截图

```python
await agent.tools['midscene_screenshot'].ainvoke({
    "name": "my_screenshot",  # 可选
    "fullPage": True  # 可选，默认 False
})
```

### 14. `midscene_log_screenshot` - 记录截图

```python
await agent.tools['midscene_log_screenshot'].ainvoke({
    "title": "登录页面",  # 可选
    "content": "用户登录操作截图"  # 可选
})
```

### 15. `midscene_get_tabs` - 获取标签页

```python
result = await agent.tools['midscene_get_tabs'].ainvoke({})
# 返回标签页列表
```

### 16. `midscene_get_console_logs` - 获取控制台日志

```python
result = await agent.tools['midscene_get_console_logs'].ainvoke({
    "msgType": "error"  # 可选：error, warn, info
})
```

### 17. `midscene_set_active_tab` - 切换标签页

```python
await agent.tools['midscene_set_active_tab'].ainvoke({
    "tabId": "标签页ID"
})
```

---

## 🚀 高级功能 API

### 18. `midscene_evaluate_javascript` - 执行 JavaScript

```python
result = await agent.tools['midscene_evaluate_javascript'].ainvoke({
    "script": "document.title"
})
# 返回: "页面标题"
```

### 19. `midscene_freeze_page_context` - 冻结页面上下文

```python
await agent.tools['midscene_freeze_page_context'].ainvoke({})
# 冻结后，所有后续操作复用相同的页面快照
# 提高大量并发操作的性能
```

### 20. `midscene_unfreeze_page_context` - 解冻页面上下文

```python
await agent.tools['midscene_unfreeze_page_context'].ainvoke({})
# 恢复使用实时页面状态
```

### 21. `midscene_run_yaml` - 运行 YAML 脚本

```python
yaml_script = """
tasks:
  - name: search_task
    flow:
      - ai: 输入 "测试" 在搜索框
      - sleep: 2000
      - aiQuery: "搜索结果，string"
"""
result = await agent.tools['midscene_run_yaml'].ainvoke({
    "yaml_script": yaml_script
})
```

### 22. `midscene_set_ai_action_context` - 设置 AI 上下文

```python
await agent.tools['midscene_set_ai_action_context'].ainvoke({
    "context": "如果存在 Cookie 同意对话框，请先关闭它"
})
# 设置后，在调用 aiAction 时会发送给 AI 模型
```

---

## 📦 完整使用示例

### 示例 1: 基础网页自动化

```python
import asyncio
from src.agent import MidsceneAgent

async def main():
    agent = MidsceneAgent(
        deepseek_api_key="your-api-key",
        midscene_server_url="http://localhost:3000"
    )

    async with agent:
        # 使用 aiAction 简化操作
        await agent.execute(
            "访问 https://example.com，点击页面标题，截取截图"
        )

asyncio.run(main())
```

### 示例 2: 复杂任务自动化

```python
async def complex_task():
    async with agent:
        # 设置上下文
        await agent.tools['midscene_set_ai_action_context'].ainvoke({
            "context": "处理任何弹窗或对话框"
        })

        # 执行复杂任务
        await agent.execute("""
        执行以下任务：
        1. 访问 https://github.com
        2. 点击 "Sign up" 按钮
        3. 填写注册表单
        4. 截取注册页面截图
        5. 验证注册按钮是否可见
        """)

        # 执行 JavaScript
        page_title = await agent.tools['midscene_evaluate_javascript'].ainvoke({
            "script": "document.title"
        })
        print(f"页面标题: {page_title}")
```

### 示例 3: 性能优化

```python
async def performance_optimized():
    async with agent:
        # 冻结上下文（提高性能）
        await agent.tools['midscene_freeze_page_context'].ainvoke({})

        # 并发执行多个查询
        tasks = [
            agent.tools['midscene_aiQuery'].ainvoke({
                "dataDemand": "页面标题，string"
            }),
            agent.tools['midscene_aiQuery'].ainvoke({
                "dataDemand": "页面描述，string"
            }),
            agent.tools['midscene_location'].ainvoke({})
        ]

        results = await asyncio.gather(*tasks)

        # 解冻上下文
        await agent.tools['midscene_unfreeze_page_context'].ainvoke({})

        print(results)
```

---

## 📊 工具集配置

### 基础工具集 (basic)

包含日常网页自动化所需的基础工具：
- 导航、点击、输入、断言

```python
agent = MidsceneAgent(..., tool_set="basic")
```

### 高级工具集 (advanced)

包含所有核心功能和高级交互工具：
- 所有交互 + 查询 + aiAction + 截图

```python
agent = MidsceneAgent(..., tool_set="advanced")
```

### 完整工具集 (full) ⭐️ 推荐

包含 **所有 22 个工具** 的完整集合。

```python
agent = MidsceneAgent(..., tool_set="full")
```

---

## 💡 最佳实践

### 1. 优先使用 `aiAction`

对于复杂任务，优先使用 `midscene_ai_action`，让 AI 自动规划执行。

```python
# ✅ 推荐
await agent.execute("访问页面，完成登录流程")

# ❌ 不推荐（手动步骤太多）
await agent.tools['midscene_navigate'].ainvoke({...})
await agent.tools['midscene_aiInput'].ainvoke({...})
await agent.tools['midscene_aiTap'].ainvoke({...})
```

### 2. 设置 AI 上下文

对于有特殊规则的任务，先设置上下文。

```python
await agent.tools['midscene_set_ai_action_context'].ainvoke({
    "context": "如果出现弹窗，请先关闭它"
})
```

### 3. 使用上下文冻结优化性能

对于大量并发查询，使用冻结上下文。

```python
await agent.tools['midscene_freeze_page_context'].ainvoke({})
# ... 并发执行多个查询
await agent.tools['midscene_unfreeze_page_context'].ainvoke({})
```

### 4. 合理使用缓存

对于重复的任务，可以启用缓存提高速度。

```python
# aiAction 默认启用缓存
# 对于其他操作，可以通过参数控制
```

---

## 🐛 常见错误

### 错误 1: 元素未找到

```
错误: Unable to locate element
解决: 使用更具体的元素描述，或使用 deepThink 选项
```

### 错误 2: 页面加载超时

```
错误: Navigation timeout
解决: 增加 timeoutMs 参数，或使用 aiWaitFor 等待页面加载
```

### 错误 3: AI 模型错误

```
错误: AI model response error
解决: 检查 API 密钥和网络连接，简化 prompt
```

---

## 📚 相关资源

- [Midscene.js 官方文档](https://midscenejs.com/api.html)
- [API 实现状态报告](./API_IMPLEMENTATION_STATUS.md)
- [aiAction 演示示例](../examples/ai_action_demo.py)
- [完整 API 测试脚本](../../test_all_apis.py)

---

## 🎉 总结

✅ **23/23 个 API 已全部实现 (100% 覆盖率)**

现在你拥有了 Midscene.js 的完整功能，可以：
- 🤖 让 AI 自动规划执行复杂任务
- 🖱️ 精确控制网页交互
- 🔍 智能提取页面信息
- ⚡ 优化性能
- 🧪 运行自动化测试

开始你的 AI 驱动网页自动化之旅吧！
