# Midscene Agent 工具集合分析报告

## 概述

本报告分析了 `runner/agent/tools/definitions.py` 文件中定义的工具集合。该文件采用声明式的方式定义了所有可用的 Midscene MCP 工具，提供了一个集中管理工具定义的模块化架构。

## 1. 工具统计

### 总体统计
- **工具总数**: 25个（不含重复定义）
- **工具分类**: 4个主要类别
- **推荐工具组合**: 3套（基础、完整、高级）

### 分类统计
| 分类 | 工具数量 | 说明 |
|------|----------|------|
| 导航工具 (navigation) | 2 | 页面导航和标签页操作 |
| 交互工具 (interaction) | 7 | 页面元素交互操作 |
| 查询工具 (query) | 10 | 页面信息提取、验证和数据查询 |
| 测试工具 (test) | 7 | 自动化测试和调试 |

## 2. 工具详细列表

### 2.1 导航工具 (Navigation Tools)

| 工具名称 | 参数 | 功能描述 | 必填 |
|----------|------|----------|------|
| midscene_navigate | url: 要导航到的完整 URL 地址 | 导航到指定的 URL 地址 | ✓ |
| midscene_setActiveTab | tabId: 要切换到的标签页 ID | 切换到指定的浏览器标签页 | ✓ |

### 2.2 交互工具 (Interaction Tools)

| 工具名称 | 参数 | 功能描述 | 必填 |
|----------|------|----------|------|
| midscene_aiTap | locate: 要点击元素的自然语言描述 | 使用 AI 智能定位并点击页面元素 | ✓ |
| midscene_aiInput | value: 要输入的文本内容<br>locate: 输入框的自然语言描述 | 使用 AI 智能定位输入框并输入文本 | ✓ |
| midscene_aiScroll | direction: 滚动方向<br>scrollType: 滚动类型<br>distance?: 滚动距离 | 使用 AI 执行页面滚动操作 | ✓ |
| midscene_aiKeyboardPress | key: 按键名称<br>locate?: 指定按键操作的目标元素 | 使用 AI 执行键盘按键操作 | ✓ |
| midscene_aiHover | locate: 要悬停元素的自然语言描述 | 使用 AI 智能悬停在页面元素上 | ✓ |
| midscene_aiWaitFor | assertion: 等待条件的自然语言描述<br>timeoutMs?: 最大等待时间<br>checkIntervalMs?: 检查间隔时间 | 使用 AI 智能等待页面满足指定条件 | ✓ |

### 2.3 查询工具 (Query Tools)

| 工具名称 | 参数 | 功能描述 | 必填 |
|----------|------|----------|------|
| midscene_aiAssert | assertion: 关于页面内容的问题或验证条件 | 使用 AI 智能分析当前页面状态，提取信息或验证条件 | ✓ |
| midscene_location | locate: 用自然语言描述的元素定位<br>options?: 可选配置项 | 通过自然语言定位页面元素，获取元素的坐标和大小信息 | ✓ |
| midscene_getTabs | (无参数) | 获取所有浏览器标签页的信息 | ✗ |
| midscene_getConsoleLogs | msgType?: 日志类型过滤 | 获取浏览器控制台日志 | ✗ |
| midscene_aiAsk | prompt: 用自然语言描述的询问内容<br>options?: 可选配置项 | 使用 AI 模型对当前页面发起提问，获得字符串形式的回答 | ✓ |
| midscene_aiQuery | dataDemand: 描述预期的返回值和格式<br>options?: 可选配置项 | 直接从 UI 提取结构化数据 | ✓ |
| midscene_aiBoolean | prompt: 用自然语言描述的期望值<br>options?: 可选配置项 | 从 UI 中提取一个布尔值 | ✓ |
| midscene_aiNumber | prompt: 用自然语言描述的期望值<br>options?: 可选配置项 | 从 UI 中提取一个数字 | ✓ |
| midscene_aiString | prompt: 用自然语言描述的期望值<br>options?: 可选配置项 | 从 UI 中提取一个字符串 | ✓ |
| midscene_aiLocate | locate: 用自然语言描述的元素定位<br>options?: 可选配置项 | 通过自然语言定位页面元素，获取元素的坐标和大小信息 | ✓ |

### 2.4 测试工具 (Test Tools)

| 工具名称 | 参数 | 功能描述 | 必填 |
|----------|------|----------|------|
| midscene_playwright_example | (无参数) | 获取 Playwright 使用示例 | ✗ |
| midscene_evaluateJavaScript | script: 要执行的 JavaScript 代码 | 在当前页面上下文中执行 JavaScript 表达式 | ✓ |
| midscene_logScreenshot | title?: 截图的标题<br>content?: 截图的描述信息 | 截取当前页面的屏幕截图并在报告中记录 | ✗ |
| midscene_freezePageContext | (无参数) | 冻结当前页面上下文，提高性能 | ✗ |
| midscene_unfreezePageContext | (无参数) | 解冻页面上下文，恢复使用实时页面状态 | ✗ |
| midscene_runYaml | yaml_script: YAML 格式的自动化脚本内容 | 执行 YAML 格式的自动化脚本 | ✓ |
| midscene_setAIActionContext | context: 背景知识描述 | 设置 AI 动作上下文背景知识 | ✓ |

## 3. 主要 API 实现检查

### 3.1 文档中提到的核心 API

| API 名称 | 实现状态 | 对应工具 | 备注 |
|----------|----------|----------|------|
| aiAct | ❌ 已禁用 | midscene_aiAction | 在定义中被注释掉，注释说明"通用工具容易卡住，使用具体工具代替" |
| aiTap | ✅ 已实现 | midscene_aiTap | 完全实现，支持自然语言描述 |
| aiInput | ✅ 已实现 | midscene_aiInput | 完全实现，支持自然语言定位 |
| aiQuery | ✅ 已实现 | midscene_aiQuery | 完全实现，支持结构化数据提取 |
| aiAssert | ✅ 已实现 | midscene_aiAssert | 完全实现，支持验证和条件检查 |

### 3.2 扩展 API

| API 类型 | 工具数量 | 说明 |
|----------|----------|------|
| 滚动操作 | 1 | midscene_aiScroll |
| 键盘操作 | 1 | midscene_aiKeyboardPress |
| 悬停操作 | 1 | midscene_aiHover |
| 等待操作 | 1 | midscene_aiWaitFor |
| 元素定位 | 2 | midscene_aiLocate, midscene_location |
| 数据类型提取 | 3 | midscene_aiBoolean, midscene_aiNumber, midscene_aiString |
| 页面查询 | 2 | midscene_aiAsk, midscene_aiQuery |
| 标签页管理 | 2 | midscene_getTabs, midscene_setActiveTab |
| 截图功能 | 1 | midscene_logScreenshot |
| 控制台日志 | 1 | midscene_getConsoleLogs |

## 4. 工具定义结构分析

### 4.1 定义模式

每个工具的定义包含以下标准字段：

```python
{
    "description": "工具功能描述",     # 详细的中文描述
    "params": {...},                   # 参数定义
    "category": "工具分类",             # 四大分类之一
    "required": true/false             # 是否必填
}
```

### 4.2 参数类型

工具参数分为三种类型：

1. **必填参数** (required: true)
   - 通过位置参数传递
   - 例如：url, locate, value, prompt 等

2. **可选参数** (参数名带?)
   - 通过选项对象传递
   - 例如：distance?, timeoutMs?, options? 等

3. **无参数** (params: {})
   - 不需要任何参数
   - 例如：midscene_getTabs, midscene_freezePageContext 等

### 4.3 命名规范

- 所有工具名称使用 `midscene_` 前缀
- 采用 `snake_case` 命名法
- 功能描述清晰，区分 ai 工具和普通工具
- ai 工具强调"智能"和"自然语言"特性

## 5. 推荐工具组合

### 5.1 基础工具集 (basic)
- midscene_navigate
- midscene_aiTap
- midscene_aiInput
- midscene_aiAssert

**适用场景**: 简单的网页自动化任务，如表单填写、按钮点击、基本验证

### 5.2 完整工具集 (full)
- 包含所有 25 个工具

**适用场景**: 复杂的自动化项目，需要所有功能支持

### 5.3 高级工具集 (advanced)
- 基础导航和交互工具
- 高级交互（hover、waitFor）
- 完整查询功能
- 调试和截图功能

**适用场景**: 复杂的用户交互场景，需要精确控制和时间管理

## 6. 问题与建议

### 6.1 发现的问题

1. **重复定义**
   - `midscene_aiWaitFor` 在文件中出现了两次（第70行和第165行）
   - 第一次定义参数更多，第二次定义更简洁
   - 建议保留更简洁的版本（第二次定义）

2. **未定义的工具**
   - 在 `RECOMMENDED_TOOL_SETS['advanced']` 中提到了 `midscene_aiDoubleClick` 和 `midscene_aiRightClick`
   - 但这两个工具在 `TOOL_DEFINITIONS` 中没有定义
   - 建议添加这两个工具或从推荐组合中移除

3. **aiAction 工具被禁用**
   - `midscene_aiAction` 是 Midscene 的核心 API，但被注释掉了
   - 注释说明"通用工具容易卡住，使用具体工具代替"
   - 这可能是设计决策，但限制了灵活性

### 6.2 改进建议

1. **统一 waitFor 定义**
   - 删除重复的 `midscene_aiWaitFor` 定义
   - 保留更简洁、参数更合理的版本

2. **补充缺失工具**
   - 添加 `midscene_aiDoubleClick`
   - 添加 `midscene_aiRightClick`
   - 或从推荐组合中移除这些工具

3. **考虑恢复 aiAction**
   - 可以增加额外的控制参数
   - 提供超时和重试机制
   - 在特定场景下仍然很有价值

4. **文档化参数模式**
   - 增加参数类型的详细说明
   - 提供参数示例
   - 说明可选参数的使用场景

## 7. 结论

当前工具集合已经非常完善，涵盖了网页自动化的主要需求：

✅ **优势**:
- 25个工具覆盖了导航、交互、查询、测试四大类别
- 所有核心 API（aiTap, aiInput, aiQuery, aiAssert）都已实现
- 工具定义结构清晰，易于维护
- 提供了三种推荐工具组合，满足不同场景需求
- 支持自然语言描述，降低使用门槛

⚠️ **需要改进**:
- 存在重复定义问题
- 推荐组合中包含未定义的工具
- 核心的 aiAction 工具被禁用

总体而言，这是一个设计良好、功能完整的工具集合，为 Midscene Agent 提供了强大的网页自动化能力。

---

*分析基于文件: runner/agent/tools/definitions.py*
*分析日期: 2025-12-22*
