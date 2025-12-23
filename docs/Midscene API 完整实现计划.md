# Midscene API 完整实现计划

## 项目概述

本计划旨在让系统完全支持 Midscene 官方文档中定义的所有 API 和参数。当前系统已实现约 90% 的功能（25/28 个核心工具），需要补充剩余的 10%。

## 当前状态分析

### ✅ 已实现（约 90%）
- 25 个工具已定义（Python）
- 16 种操作已实现（Node.js）
- 9 种查询已实现（Node.js）
- 基础架构完整

### ❌ 需要实施（约 10%）

#### 1. 缺失的工具（4个）
- `midscene_aiDoubleClick` - 双击操作
- `midscene_aiRightClick` - 右键点击操作
- `midscene_recordToReport` - 记录截图到报告
- `midscene_getLogContent` - 获取日志内容（对应 _unstableLogContent）

#### 2. 需要增强参数的现有工具
**交互方法（aiTap, aiHover, aiInput, aiKeyboardPress, aiScroll, aiDoubleClick, aiRightClick）：**
- `deepThink?: boolean` - 是否启用深度思考模式
- `xpath?: string` - 可选的 XPath 定位
- `cacheable?: boolean` - 是否启用缓存

**查询方法（aiAsk, aiQuery, aiBoolean, aiNumber, aiString, aiAssert）：**
- `domIncluded?: boolean | 'visible-only'` - 是否包含 DOM 信息
- `screenshotIncluded?: boolean` - 是否包含截图

**aiInput 特殊参数：**
- `autoDismissKeyboard?: boolean` - 是否自动关闭键盘（Android/iOS）
- `mode?: 'replace' | 'clear' | 'append'` - 输入模式

**aiScroll 完整参数结构：**
- `direction?: 'down' | 'up' | 'left' | 'right'` - 滚动方向
- `scrollType?: 'singleAction' | 'scrollToBottom' | 'scrollToTop' | 'scrollToRight' | 'scrollToLeft'` - 滚动类型
- `distance?: number | null` - 滚动距离

**aiWaitFor 增强参数：**
- `timeoutMs?: number` - 超时时间（毫秒）
- `checkIntervalMs?: number` - 检查间隔（毫秒）

#### 3. 特殊功能
- 图片作为提示词支持（prompt 参数可接受包含 images 数组的对象）

## 实施计划

### 阶段 1: 修复 Python 工具定义
**文件：** `runner/agent/tools/definitions.py`
**耗时：** 30分钟

**任务：**
1. 添加 4 个缺失工具定义
2. 增强 15+ 现有工具参数
3. 修复重复定义（midscene_aiWaitFor）

**详细修改：**
- 添加 midscene_aiDoubleClick, midscene_aiRightClick
- 添加 midscene_recordToReport, midscene_getLogContent
- 为所有交互方法添加 deepThink, xpath, cacheable 参数
- 为所有查询方法添加 domIncluded, screenshotIncluded 参数
- 为 aiInput 添加 autoDismissKeyboard, mode 参数
- 为 aiScroll 添加完整的滚动参数结构
- 为 aiWaitFor 添加 timeoutMs, checkIntervalMs 参数

### 阶段 2: 更新 Node.js TypeScript 类型定义
**文件：** `server/src/types/action.ts`, `server/src/types/query.ts`
**耗时：** 45分钟

**任务：**
1. 添加新的 ActionType 和 QueryType
2. 增强 ActionParams 和 QueryParams 接口
3. 更新类型导出

**详细修改：**
- 在 ActionType 中添加 'aiDoubleClick', 'aiRightClick', 'recordToReport', 'getLogContent'
- 扩展 ActionParams 接口，添加所有新参数
- 扩展 QueryParams 接口，添加选项参数
- 更新类型导出列表

### 阶段 3: 实现 Node.js 动作处理
**文件：** `server/src/orchestrator/actions/execute.ts`
**耗时：** 60分钟

**任务：**
1. 实现 2 个新动作处理器（recordToReport, getLogContent）
2. 增强 7 个现有动作处理器
3. 更新 executeActionDirect switch 语句

**详细修改：**
- 实现 handleRecordToReport 函数
- 实现 handleGetLogContent 函数
- 增强 handleInput 函数，支持 autoDismissKeyboard 和 mode 参数
- 为所有动作处理器添加选项参数支持
- 更新 switch 语句，处理新动作类型

### 阶段 4: 实现 Node.js 查询处理
**文件：** `server/src/orchestrator/queries/execute.ts`
**耗时：** 30分钟

**任务：**
1. 实现 1 个新查询处理器（getLogContent）
2. 增强 6 个现有查询处理器
3. 更新 processQuery switch 语句

**详细修改：**
- 实现 handleGetLogContent 函数
- 增强所有查询处理器，添加选项参数支持
- 更新 processQuery switch 语句

### 阶段 5: 测试和验证
**文件：** `tests/texts/enhanced_parameters_test.txt`
**耗时：** 45分钟

**任务：**
1. 创建测试文件
2. 运行质量检查命令
3. 验证所有功能

**测试内容：**
- aiInput 增强参数测试
- 双击和右键点击测试
- 查询增强参数测试
- 记录截图到报告测试
- 获取控制台日志测试

## 文件修改清单

### 关键文件（按执行顺序）

1. **runner/agent/tools/definitions.py**（Python 工具定义）
   - 添加 4 个缺失工具
   - 增强 15+ 现有工具参数
   - 修复重复定义

2. **server/src/types/action.ts**（动作类型定义）
   - 添加新 ActionType（4个）
   - 增强 ActionParams 接口

3. **server/src/types/query.ts**（查询类型定义）
   - 添加新 QueryType（1个）
   - 增强 QueryParams 接口

4. **server/src/orchestrator/actions/execute.ts**（动作执行器）
   - 实现 2 个新动作处理器
   - 增强 7 个现有动作处理器

5. **server/src/orchestrator/queries/execute.ts**（查询执行器）
   - 实现 1 个新查询处理器
   - 增强 6 个现有查询处理器

6. **server/src/orchestrator/types.ts**（类型导出）
   - 更新导出列表

## 执行顺序和依赖关系

```
阶段 1 (Python 工具定义)
    ↓ [定义工具结构]
阶段 2 (TypeScript 类型)
    ↓ [定义类型接口]
阶段 3 (Node.js 动作)
    ↓ [实现动作逻辑]
阶段 4 (Node.js 查询)
    ↓ [实现查询逻辑]
阶段 5 (测试验证)
    ↓ [质量检查]
完成 ✅
```

## 风险评估和缓解策略

### 高风险项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 参数兼容性 | 可能破坏现有调用 | 所有新参数都是可选的，向后兼容 |
| 类型安全 | TypeScript 类型不匹配 | 严格类型检查，分步实现 |
| Midscene API 变更 | 内部 API 可能变化 | 参考官方文档，分阶段测试 |

### 中等风险项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Python/Node.js 同步 | 实现不一致 | 统一参数命名，详细测试 |

## 成功标准

### 功能完整性
- [x] 所有 28 个工具定义完整
- [x] 所有参数增强实现
- [x] 图片提示词功能支持

### 代码质量
- [x] Python 代码通过格式化和类型检查
- [x] TypeScript 代码通过类型检查
- [x] 所有测试通过

### 兼容性
- [x] 现有功能不受影响
- [x] 新参数向后兼容
- [x] API 文档更新完成

## 预计耗时

| 阶段 | 任务 | 耗时 |
|------|------|------|
| 阶段 1 | Python 工具定义 | 30分钟 |
| 阶段 2 | TypeScript 类型 | 45分钟 |
| 阶段 3 | Node.js 动作 | 60分钟 |
| 阶段 4 | Node.js 查询 | 30分钟 |
| 阶段 5 | 测试验证 | 45分钟 |
| **总计** | | **3.5 小时** |

## 实施建议

1. **分阶段执行**：严格按照顺序执行，确保依赖关系正确
2. **及时测试**：每个阶段完成后立即测试，避免问题累积
3. **保持代码风格**：使用现有格式化工具，保持代码风格一致
4. **详细日志**：添加必要的日志记录，便于调试
