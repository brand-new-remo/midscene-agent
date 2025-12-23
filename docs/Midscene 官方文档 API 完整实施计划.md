# Midscene 官方文档 API 完整实施计划

## 概述

基于对代码库的深入分析，当前系统已实现约 90% 的核心功能（25/28 个工具）。本计划将一次性实现所有缺失功能，支持 Midscene 官方文档中的所有 API 和参数。

## ### 1.实施范围总结

 缺失的工具（4个）
- midscene_aiDoubleClick - 双击操作
- midscene_aiRightClick - 右键点击操作  
- midscene_recordToReport - 记录截图到报告
- midscene_getLogContent - 获取日志内容（对应 _unstableLogContent）

### 2. 需要增强参数的现有工具
- 交互方法（aiTap, aiHover, aiInput, aiKeyboardPress, aiScroll, aiDoubleClick, aiRightClick）：添加 deepThink, xpath, cacheable 参数
- 查询方法（aiAsk, aiQuery, aiBoolean, aiNumber, aiString, aiAssert）：添加 domIncluded, screenshotIncluded 参数
- aiInput：添加 autoDismissKeyboard, mode ('replace' | 'clear' | 'append') 参数
- aiScroll：支持完整的滚动参数结构（direction, scrollType, distance）
- aiWaitFor：添加 timeoutMs, checkIntervalMs 参数

### 3. 特殊功能
- 图片作为提示词支持（prompt 参数可以接受包含 images 数组的对象）

## 分阶段实施计划

### 阶段 1: 修复 Python 工具定义（30分钟）

#### 1.1 更新 runner/agent/tools/definitions.py

任务清单：
1. 添加缺失的工具定义
   - 添加 midscene_aiDoubleClick 到 TOOL_DEFINITIONS
   - 添加 midscene_aiRightClick 到 TOOL_DEFINITIONS
   - 添加 midscene_recordToReport 到 TOOL_DEFINITIONS
   - 添加 midscene_getLogContent 到 TOOL_DEFINITIONS

2. 增强现有工具参数
   - 为所有交互方法添加 deepThink, xpath, cacheable 参数
   - 为所有查询方法添加 domIncluded, screenshotIncluded 参数
   - 为 aiInput 添加 autoDismissKeyboard, mode 参数
   - 为 aiWaitFor 添加 timeoutMs, checkIntervalMs 参数

3. 修复重复定义
   - 删除第70行的 midscene_aiWaitFor 重复定义

4. 更新工具分类
   - 更新 TOOL_CATEGORIES 中的交互工具列表

5. 更新推荐工具组合
   - 更新 RECOMMENDED_TOOL_SETS

### 阶段 2: 更新 Node.js TypeScript 类型定义（45分钟）

#### 2.1 更新 server/src/types/action.ts

任务清单：
1. 添加新的 ActionType
   - 添加 'aiDoubleClick'
   - 添加 'aiRightClick'
   - 添加 'recordToReport'
   - 添加 'getLogContent'

2. 增强 ActionParams 接口
   - 添加 autoDismissKeyboard?: boolean
   - 添加 mode?: 'replace' | 'clear' | 'append'
   - 为 options 添加详细类型定义

3. 增强 ScrollOptions 接口
   - 确保 direction, scrollType, distance 参数完整支持

#### 2.2 更新 server/src/types/query.ts

任务清单：
1. 添加新的 QueryType
   - 添加 'getLogContent'

2. 增强 QueryParams 接口
   - 为 options 添加详细类型定义，支持 domIncluded, screenshotIncluded

### 阶段 3: 实现 Node.js 动作处理（60分钟）

#### 3.1 更新 server/src/orchestrator/actions/execute.ts

任务清单：
1. 添加新动作处理器
   - 实现 handleRecordToReport 函数
   - 实现 handleGetLogContent 函数

2. 增强现有处理器
   - 增强 handleTap，支持 deepThink, xpath, cacheable 参数
   - 增强 handleHover，支持 deepThink, xpath, cacheable 参数
   - 增强 handleInput，支持 autoDismissKeyboard, mode 参数
   - 增强 handleScroll，确保完整参数支持
   - 增强 handleKeyboardPress，支持 deepThink, xpath, cacheable 参数
   - 增强 handleDoubleClick，支持 deepThink, xpath, cacheable 参数
   - 增强 handleRightClick，支持 deepThink, xpath, cacheable 参数

3. 更新 executeActionDirect
   - 添加 'recordToReport' case
   - 添加 'getLogContent' case

### 阶段 4: 实现 Node.js 查询处理（30分钟）

#### 4.1 更新 server/src/orchestrator/queries/execute.ts

任务清单：
1. 添加新查询处理器
   - 实现 handleGetLogContent 查询处理器

2. 增强现有查询处理器
   - 增强所有查询处理器，支持 domIncluded, screenshotIncluded 参数

3. 更新 processQuery
   - 添加 'getLogContent' case

### 阶段 5: 测试和验证（45分钟）

#### 5.1 创建测试文件

任务清单：
1. 创建 Python 端测试
   - 创建 tests/texts/enhanced_parameters_test.txt
   - 测试所有新参数功能

2. 创建 Node.js 端测试
   - 在 server/src/orchestrator/__tests__/ 中添加新测试

#### 5.2 运行验证

任务清单：
1. Python 代码质量检查
   - 运行 uv run ./format.py 格式化 Python 代码
   - 运行 uv run ./typecheck.py 类型检查

2. Node.js 代码质量检查
   - 运行 npm run build TypeScript 构建
   - 运行 npm run typecheck 类型检查
   - 运行 npm run lint 代码规范检查

3. 功能验证测试
   - 启动 Node.js 服务器
   - 运行 Python 测试脚本
   - 验证所有新功能正常工作

## 文件修改清单

### 关键文件列表

1. runner/agent/tools/definitions.py - Python 工具定义
   - 添加 4 个缺失工具
   - 增强 15+ 现有工具参数
   - 修复重复定义

2. server/src/types/action.ts - 动作类型定义
   - 添加新 ActionType
   - 增强 ActionParams 接口

3. server/src/types/query.ts - 查询类型定义
   - 添加新 QueryType
   - 增强 QueryParams 接口

4. server/src/orchestrator/actions/execute.ts - 动作执行器
   - 实现 2 个新动作处理器
   - 增强 7 个现有动作处理器

5. server/src/orchestrator/queries/execute.ts - 查询执行器
   - 实现 1 个新查询处理器
   - 增强 6 个现有查询处理器

6. server/src/orchestrator/types.ts - 类型导出
   - 更新导出列表

## 依赖关系和执行顺序

### 执行顺序图

```
阶段 1 (Python) → 阶段 2 (TypeScript 类型) → 阶段 3 (Node.js Actions) → 阶段 4 (Node.js Queries) → 阶段 5 (测试)
     ↓                      ↓                         ↓                         ↓                ↓
  工具定义             类型定义                  动作实现                 查询实现          验证测试
```

### 关键依赖

1. Python 工具定义 → TypeScript 类型
   - 必须先更新 Python 定义以了解新工具结构

2. TypeScript 类型 → Node.js 实现
   - 必须先定义类型才能实现功能

3. 动作/查询实现 → 测试验证
   - 必须先实现功能才能测试

## 风险评估和缓解策略

### 高风险项

1. 参数兼容性
   - 风险：新增参数可能破坏现有调用
   - 缓解：所有新参数都是可选的，不会破坏现有代码

2. 类型安全
   - 风险：TypeScript 类型不匹配
   - 缓解：严格类型检查，分步实现

3. Midscene API 变更
   - 风险：Midscene 内部 API 可能变化
   - 缓解：参考官方文档，分阶段测试

### 中等风险项

1. Python/Node.js 同步
   - 风险：Python 和 Node.js 实现不一致
   - 缓解：统一参数命名，详细测试

### 低风险项

1. 代码格式化
   - 风险：格式化可能引入不必要的变更
   - 缓解：使用现有格式化工具

## 成功标准

### 功能完整性
- 所有 28 个工具定义完整
- 所有参数增强实现
- 图片提示词功能支持

### 代码质量
- Python 代码通过格式化和类型检查
- TypeScript 代码通过类型检查
- 所有测试通过

### 兼容性
- 现有功能不受影响
- 新参数向后兼容
- API 文档更新完成

## 后续维护

### 文档更新
- 更新 Midscene 文档链接
- 添加新工具使用示例
- 更新参数说明

### 监控指标
- 工具调用成功率
- 新参数使用率
- 错误日志分析

---

**计划创建时间**：2025-12-22  
**预计总耗时**：3.5 小时  
**优先级**：高  
**涉及文件**：6 个核心文件  
**测试覆盖**：新增 2 个测试文件
