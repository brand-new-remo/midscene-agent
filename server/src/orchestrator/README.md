# Midscene Orchestrator

Midscene Orchestrator 负责管理多个 Midscene
PlaywrightAgent 会话，执行网页自动化动作，并提供查询功能。

## 目录结构

```
orchestrator/
├── index.ts              # 主入口文件，导出 MidsceneOrchestrator 类
├── types.ts              # 类型定义，重新导出所有类型
├── config.ts             # 配置和日志初始化
├── session.ts            # 会话管理（创建、验证、销毁）
├── action-history.ts     # 动作历史记录和错误处理
├── system.ts             # 系统管理（健康检查、关闭等）
├── actions/
│   └── execute.ts        # 动作执行逻辑
└── queries/
    └── execute.ts        # 查询执行逻辑
```

## 模块说明

### index.ts

主入口文件，包含 `MidsceneOrchestrator` 类的定义，该类实现了
`OrchestratorInterface` 接口。

### config.ts

提供日志初始化和目录确保功能：

- `initializeLogger()` - 创建和配置 winston 日志器
- `ensureLogDirectory()` - 确保日志目录存在

### session.ts

会话管理功能：

- `createSession()` - 创建新的 Midscene 会话
- `validateSession()` - 验证会话是否存在
- `destroySession()` - 销毁会话
- `getActiveSessions()` - 获取活跃会话列表

### action-history.ts

动作历史记录和错误处理：

- `recordActionHistory()` - 记录动作到历史
- `executeAndRecord()` - 执行动作并记录结果
- `handleActionError()` - 处理动作执行错误

### actions/execute.ts

所有网页自动化动作的执行逻辑：

- 导航动作 (navigate)
- 点击动作 (aiTap, aiDoubleClick, aiRightClick)
- 输入动作 (aiInput)
- 滚动动作 (aiScroll)
- 键盘动作 (aiKeyboardPress)
- 悬停动作 (aiHover)
- 等待动作 (aiWaitFor)
- AI 动作 (aiAction)
- 标签页操作 (setActiveTab)
- JavaScript 执行 (evaluateJavaScript)
- 截图 (logScreenshot)
- YAML 执行 (runYaml)
- 上下文设置 (setAIActionContext, freezePageContext, unfreezePageContext)

### queries/execute.ts

所有页面查询的执行逻辑：

- aiAssert - 断言查询
- aiAsk - AI 问答查询
- aiQuery - 结构化数据查询
- aiBoolean - 布尔值查询
- aiNumber - 数值查询
- aiString - 字符串查询
- aiLocate - 元素位置查询
- location - 页面位置信息
- getTabs - 标签页信息

### system.ts

系统管理功能：

- `getSessionHistory()` - 获取会话历史
- `healthCheck()` - 健康检查
- `shutdown()` - 优雅关闭

## 使用方式

```typescript
import MidsceneOrchestrator from './orchestrator/index.js';

const orchestrator = new MidsceneOrchestrator();

// 创建会话
const sessionId = await orchestrator.createSession({
  headless: false,
  viewport_width: 1920,
  viewport_height: 1080,
});

// 执行动作
await orchestrator.executeAction(sessionId, 'navigate', {
  url: 'https://example.com',
});

// 查询页面
const title = await orchestrator.executeQuery(sessionId, 'location');

// 销毁会话
await orchestrator.destroySession(sessionId);
```

## 设计原则

1. **单一职责原则** - 每个模块都有明确的职责
2. **关注点分离** - 动作、查询、会话管理分别放在不同模块
3. **可维护性** - 代码按逻辑分组，便于维护和扩展
4. **类型安全** - 所有模块使用 TypeScript 严格类型检查
5. **错误处理** - 统一的错误处理和日志记录机制
