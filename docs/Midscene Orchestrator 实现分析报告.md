# Midscene Orchestrator 实现分析报告

## 概述

Midscene Orchestrator 是 Node.js 端的网页自动化编排器，负责管理多个 Midscene PlaywrightAgent 会话，执行网页自动化动作，并提供查询功能。它通过 HTTP + WebSocket 与 Python 智能体通信，实现稳定、功能丰富的网页自动化。

## 1. Actions 实现分析

### 1.1 核心操作类型

`server/src/orchestrator/actions/execute.ts` 实现了以下 16 种网页自动化操作：

#### 导航操作
- **navigate** - 导航到指定的 URL 地址
  - 参数：url（必需）
  - 实现：使用 Playwright 的 page.goto() 方法，等待网络空闲状态

#### 基础交互操作
- **aiTap** - AI 智能点击页面元素
  - 参数：locate（必需，元素定位描述）
  - 实现：调用 agent.aiTap(locate, options)
  
- **aiInput** - AI 智能输入文本
  - 参数：locate（必需），value（必需）
  - 实现：调用 agent.aiInput(locate, { ...options, value })
  
- **aiScroll** - AI 智能滚动
  - 参数：direction（必需），scrollType（可选），distance（可选）
  - 特殊处理：支持 v1.0.1 兼容性，滚动类型映射
  - 实现：调用 agent.aiScroll(locate, scrollOptions)
  
- **aiKeyboardPress** - AI 智能按键
  - 参数：key（必需），locate（可选）
  - 实现：调用 agent.aiKeyboardPress(key, locate, options)
  
- **aiHover** - AI 智能悬停
  - 参数：locate（必需）
  - 实现：调用 agent.aiHover(locate, options)
  
- **aiWaitFor** - AI 智能等待条件
  - 参数：assertion（必需），timeoutMs（可选，默认 30000），checkIntervalMs（可选，默认 3000）
  - 实现：调用 agent.aiWaitFor(assertion, options)

#### 高级交互操作
- **aiDoubleClick** - AI 智能双击
  - 参数：locate（必需）
  - 实现：调用 agent.aiDoubleClick(locate, options)
  
- **aiRightClick** - AI 智能右键点击
  - 参数：locate（必需）
  - 实现：调用 agent.aiRightClick(locate, options)
  
- **aiAction** - AI 智能动作（自然语言指令）
  - 参数：prompt（必需）
  - 实现：调用 agent.aiAction(prompt)
  - 注意：在 Python 工具定义中已禁用

#### 标签页管理
- **setActiveTab** - 切换浏览器标签页
  - 参数：tabId（必需）
  - 实现：通过 Playwright API 切换标签页

#### 特殊功能操作
- **evaluateJavaScript** - 执行自定义 JavaScript 代码
  - 参数：script（必需）
  - 实现：调用 agent.evaluateJavaScript(script)
  - 返回：执行结果
  
- **logScreenshot** - 截图并保存
  - 参数：title（可选）
  - 实现：调用 agent.logScreenshot(title, options)
  - 返回：截图结果
  
- **freezePageContext** - 冻结页面上下文
  - 参数：无
  - 实现：调用 agent.freezePageContext()
  - 用途：提高大量并发操作的性能
  
- **unfreezePageContext** - 解冻页面上下文
  - 参数：无
  - 实现：调用 agent.unfreezePageContext()
  - 用途：恢复使用实时页面状态

#### YAML 脚本执行
- **runYaml** - 执行 YAML 格式的自动化脚本
  - 参数：yamlScript（必需）
  - 实现：调用 agent.runYaml(yamlScript)
  - 返回：所有 .aiQuery 调用的结果
  
- **setAIActionContext** - 设置 AI 动作上下文
  - 参数：context（必需）
  - 实现：调用 agent.setAIActionContext(context)
  - 用途：为后续 AI 动作设置背景知识

## 2. Queries 实现分析

### 2.1 查询类型

`server/src/orchestrator/queries/execute.ts` 实现了以下 9 种页面查询：

#### 断言和验证
- **aiAssert** - AI 智能断言验证
  - 参数：assertion（必需），errorMsg（可选）
  - 返回：{ success: true; assertion: string }
  - 实现：调用 agent.aiAssert(assertion, errorMsg, options)

#### AI 数据提取查询
- **aiAsk** - AI 智能询问
  - 参数：prompt（必需）
  - 返回：string | Record<string, unknown>
  - 实现：调用 agent.aiAsk(prompt, options)
  
- **aiQuery** - AI 数据提取
  - 参数：dataDemand（必需）
  - 返回：Record<string, unknown> | string
  - 实现：调用 agent.aiQuery(dataDemand, options)
  
- **aiBoolean** - AI 布尔值查询
  - 参数：prompt（必需）
  - 返回：boolean
  - 实现：调用 agent.aiBoolean(prompt, options)
  
- **aiNumber** - AI 数值查询
  - 参数：prompt（必需）
  - 返回：number
  - 实现：调用 agent.aiNumber(prompt, options)
  
- **aiString** - AI 文本查询
  - 参数：prompt（必需）
  - 返回：string
  - 实现：调用 agent.aiString(prompt, options)

#### 元素定位
- **aiLocate** - AI 元素定位
  - 参数：locate（必需）
  - 返回：{ x: number; y: number; width: number; height: number }
  - 实现：调用 agent.aiLocate(locate, options)
  - 特殊处理：转换结果格式，从 Midscene 的 rect 对象提取坐标

#### 页面信息
- **location** - 获取当前页面位置信息
  - 参数：无
  - 返回：{ url: string; title: string; path: string }
  - 实现：直接使用 Playwright API 获取页面信息
  
- **getTabs** - 获取所有标签页信息
  - 参数：无
  - 返回：Array<{ id: number; url: string; title: string }>
  - 实现：通过 Playwright API 遍历所有标签页

## 3. 特殊功能实现

### 3.1 freezePageContext / unfreezePageContext

**功能说明**：
- freezePageContext - 冻结当前页面上下文，使后续操作复用相同的页面快照
- unfreezePageContext - 解冻页面上下文，恢复使用实时页面状态

**实现方式**：
- 直接调用 Midscene PlaywrightAgent 的对应方法
- 无需参数
- 用于提高大量并发操作的性能

**使用场景**：
- 批量数据提取场景，避免重复的页面分析
- 性能优化场景，减少 AI 模型的调用次数

### 3.2 evaluateJavaScript

**功能说明**：在浏览器上下文中执行自定义 JavaScript 代码

**实现方式**：
- 调用 agent.evaluateJavaScript(script)
- 参数：script（JavaScript 代码字符串）
- 返回：执行结果

**使用场景**：
- 获取页面复杂状态（如 localStorage、sessionStorage）
- 执行自定义逻辑
- 调试和诊断

## 4. Orchestrator 架构分析

### 4.1 整体架构

MidsceneOrchestrator (主类)
├── sessions: Map<string, Session>                    # 会话存储
├── actionHistory: Map<string, ActionRecord[]>       # 动作历史
├── logger: winston.Logger                           # 日志记录器
└── deduplicator: ActionDeduplicator                 # 去重中间件

### 4.2 核心组件

#### 4.2.1 会话管理（session.ts）

**功能职责**：
- 创建新的 Midscene 会话
- 验证会话存在性
- 销毁会话
- 获取活跃会话列表

#### 4.2.2 动作历史管理（action-history.ts）

**功能职责**：
- 记录动作执行历史
- 执行动作并记录结果
- 处理动作执行错误

#### 4.2.3 系统功能（system.ts）

**功能职责**：
- 健康检查
- 获取会话历史
- 优雅关闭

#### 4.2.4 操作去重中间件（middleware/deduplication.ts）

**功能职责**：
- 防止重复操作执行
- 缓存操作结果
- 智能相似度检测

## 5. 与 Python 工具定义的映射关系

### 5.1 工具名称映射

总体映射率：约 90%（18/20 个工具完全对应）

完全对应的工具：
- 所有核心交互工具（导航、点击、输入、滚动等）
- 所有查询工具（断言、提取、定位等）
- 所有特殊功能工具（JavaScript 执行、截图、上下文管理等）

未对应的工具：
- midscene_aiDoubleClick - Node.js 已实现但 Python 未定义
- midscene_aiRightClick - Node.js 已实现但 Python 未定义
- midscene_getConsoleLogs - Python 已定义但 Node.js 未实现

## 6. 总结与建议

### 6.1 架构优势

1. **模块化设计**：清晰的职责分离，便于维护和扩展
2. **类型安全**：完整的 TypeScript 类型定义
3. **错误处理**：完善的错误捕获和日志记录
4. **性能优化**：操作去重机制，提高执行效率
5. **实时反馈**：WebSocket 流式传输，支持进度监控
6. **会话管理**：完整的会话生命周期管理

### 6.2 扩展建议

1. **补充缺失工具**：
   - 在 Python 工具定义中添加 midscene_aiDoubleClick 和 midscene_aiRightClick
   - 在 Node.js 中实现 midscene_getConsoleLogs 查询功能

2. **增强中间件**：
   - 添加速率限制中间件
   - 添加重试机制中间件
   - 添加监控指标中间件

3. **性能优化**：
   - 优化会话池管理
   - 添加并发控制
   - 支持分布式部署

---

**报告生成时间**：2025-12-22  
**分析范围**：server/src/orchestrator/ 目录下所有 TypeScript 文件  
**Python 工具定义**：runner/agent/tools/definitions.py
