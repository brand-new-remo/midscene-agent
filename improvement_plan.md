# Midscene-Agent 重复执行问题改进计划

## 📋 项目概述

### 目标
解决Midscene-Agent执行过程中出现的**重复执行**问题，通过引入记忆机制和去重机制，减少80%的重复操作，提升执行效率和稳定性。

### 背景
- **问题**：AI在执行测试用例时重复执行相同操作，浪费时间和资源
- **根因**：缺乏记忆机制，每次执行都是全新调用，无法利用历史经验
- **影响**：执行效率低，用户体验差，系统资源浪费

---

## 🎯 改进目标与指标

### 核心指标
| 指标 | 当前值 | 目标值 | 改进幅度 |
|------|--------|--------|----------|
| 重复执行率 | ~15% | <3% | 80%↓ |
| 平均执行步数 | 15-20步 | 10-12步 | 30%↓ |
| 执行成功率 | 85% | 95% | 12%↑ |
| 用户满意度 | 7/10 | 9/10 | 28%↑ |

### 次要指标
- 内存占用：控制在合理范围内（<100MB）
- 执行延迟：增加控制在50ms以内
- 兼容性：100%向后兼容

---

## 📊 实施计划总览

### 三个阶段推进

```
阶段1: 快速修复 (2周)
├─ 方案1: Node.js去重中间件
└─ 方案2: Python简单记忆

阶段2: 系统优化 (4周)
├─ 方案3: LangGraph MemorySaver集成
└─ 方案4: 混合记忆架构

阶段3: 架构升级 (8周)
└─ 方案5: 统一状态管理
```

---

## 🚀 阶段1：快速修复 (2周)

### 目标
- 快速见效，减少80%重复执行
- 低风险，易于回滚
- 为后续优化打好基础

### 方案1：Node.js去重中间件 (1周)

#### 📁 文件变更
**新增文件**：`server/src/orchestrator/middleware/deduplication.ts`

#### 🔧 实现内容
```typescript
export class ActionDeduplicator {
  private actionCache: Map<string, CachedAction> = new Map();

  shouldExecute(sessionId: string, action: ActionType, params: ActionParams): boolean {
    const key = this.generateKey(action, params);
    const cached = this.actionCache.get(key);

    if (!cached) return true;

    // 5秒内相同操作直接跳过
    const timeDiff = Date.now() - cached.timestamp;
    return timeDiff > 5000;
  }

  record(sessionId: string, action: ActionType, params: ActionParams, result: ActionResult) {
    const key = this.generateKey(action, params);
    this.actionCache.set(key, {
      action,
      params,
      result,
      timestamp: Date.now()
    });
  }
}
```

#### 🎯 集成点
修改 `server/src/orchestrator/index.ts`：
```typescript
class MidsceneOrchestrator {
  private deduplicator = new ActionDeduplicator();

  async executeAction(...) {
    // 1. 检查重复
    if (!this.deduplicator.shouldExecute(sessionId, action, params)) {
      return this.deduplicator.getCachedResult(sessionId, action, params);
    }

    // 2. 执行操作
    const result = await this.performAction(...);

    // 3. 记录结果
    this.deduplicator.record(sessionId, action, params, result);

    return result;
  }
}
```

#### ✅ 验收标准
- [ ] 相同操作5秒内不重复执行
- [ ] 缓存命中率 > 70%
- [ ] 无性能回归（执行延迟<20ms）

---

### 方案2：Python简单记忆 (1周)

#### 📁 文件变更
**新增文件**：`runner/agent/memory/simple_memory.py`

#### 🔧 实现内容
```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time

@dataclass
class MemoryRecord:
    timestamp: float
    action: str
    params: Dict[str, Any]
    result: Any
    context: Dict[str, Any]

class SimpleMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.records: List[MemoryRecord] = []
        self.page_context: Dict[str, Any] = {}

    def add_record(self, action: str, params: Dict, result: Any, context: Optional[Dict] = None):
        record = MemoryRecord(
            timestamp=time.time(),
            action=action,
            params=params,
            result=result,
            context=context or self.page_context
        )
        self.records.append(record)

        # 保持大小限制
        if len(self.records) > self.max_size:
            self.records.pop(0)

    def get_recent_context(self, limit: int = 5) -> str:
        """构建历史上下文"""
        if not self.records:
            return "无历史操作记录"

        lines = ["=== 最近操作历史 ==="]
        for record in self.records[-limit:]:
            lines.append(f"[{record.action}] {record.params} → {record.result}")

        return "\n".join(lines)
```

#### 🎯 集成点
修改 `runner/agent/agent.py`：
```python
class MidsceneAgent:
    def __init__(self, ...):
        # ... 现有代码
        self.memory = SimpleMemory(max_size=50)

    async def execute(self, user_input: str, stream: bool = True):
        # 1. 获取历史上下文
        memory_context = self.memory.get_recent_context()

        # 2. 构建增强输入
        enhanced_input = f"{memory_context}\n\n当前任务: {user_input}"

        # 3. 执行并记录
        async for chunk in self._execute_with_tracking(enhanced_input, stream):
            # 4. 解析结果并更新记忆
            self._update_memory_from_result(chunk)
            yield chunk
```

#### ✅ 验收标准
- [ ] AI能访问历史操作记录
- [ ] 上下文正确注入到LLM
- [ ] 重复操作明显减少

---

### 📅 阶段1时间表

| 周 | 任务 | 负责人 | 里程碑 |
|----|------|--------|--------|
| 第1周 | 实现Node.js去重中间件 | 待定 | 完成去重功能 |
| 第2周 | 实现Python简单记忆 | 待定 | 完成记忆机制 |

### 💰 阶段1工作量
- **开发时间**：2人周
- **测试时间**：1人周
- **文档时间**：0.5人周
- **总计**：3.5人周

---

## 🛠️ 阶段2：系统优化 (4周)

### 目标
- 建立完整的记忆体系
- 提升长期稳定性
- 为规模化应用做准备

### 方案3：LangGraph MemorySaver集成 (2周)

#### 🔧 实现内容
修改 `runner/agent/agent.py`：
```python
from langgraph.checkpoint.memory import MemorySaver

class MidsceneAgent:
    async def _build_graph(self):
        """构建带记忆的LangGraph"""
        # 添加MemorySaver
        checkpointer = MemorySaver()

        builder = StateGraph(MessagesState)
        builder.add_node("agent", self._agent_node)
        builder.add_node("tools", ToolNode(self.tools))
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", tools_condition, {...})

        # 编译时启用记忆
        return builder.compile(
            checkpointer=checkpointer,
            interrupt_before=[],
            interrupt_after=[]
        )

    async def execute(self, user_input: str, stream: bool = True):
        # 使用线程ID保持记忆连续性
        config = {
            "configurable": {"thread_id": self.session_id},
            "recursion_limit": 100
        }

        async for chunk in self.agent_executor.astream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        ):
            yield chunk
```

#### ✅ 验收标准
- [ ] 跨多次调用保持状态
- [ ] 线程模型正常工作
- [ ] 状态持久化稳定

---

### 方案4：混合记忆架构 (2周)

#### 🔧 实现内容
**新增文件**：`runner/agent/memory/hybrid_memory.py`

```python
class HybridMemory:
    """混合记忆：短期记忆 + 长期记忆"""

    def __init__(self, agent_instance):
        self.agent = agent_instance
        self.short_term = SimpleMemory(max_size=50)  # 会话内记忆
        self.long_term = PersistentMemory()  # 跨会话记忆

    async def sync_from_orchestrator(self):
        """从Node.js同步历史"""
        history = await self.agent.http_client.get_session_history()
        for record in history:
            self.short_term.add_record(
                action=record["action"],
                params=record["params"],
                result=record.get("result"),
                context={"url": record.get("url")}
            )

    async def get_enhanced_context(self) -> str:
        """获取增强上下文"""
        short_context = self.short_term.get_recent_context()
        long_context = self.long_term.get_relevant_history()

        return f"{long_context}\n\n{short_context}"
```

#### ✅ 验收标准
- [ ] 短期记忆正常工作
- [ ] 长期记忆持久化
- [ ] 上下文增强有效

---

### 📅 阶段2时间表

| 周 | 任务 | 负责人 | 里程碑 |
|----|------|--------|--------|
| 第3周 | 实现LangGraph MemorySaver | 待定 | 状态持久化 |
| 第4周 | 测试MemorySaver集成 | 待定 | 功能验证 |
| 第5周 | 实现混合记忆架构 | 待定 | 架构设计 |
| 第6周 | 测试和优化 | 待定 | 性能达标 |

### 💰 阶段2工作量
- **开发时间**：4人周
- **测试时间**：2人周
- **文档时间**：1人周
- **总计**：7人周

---

## 🏗️ 阶段3：架构升级 (8周)

### 目标
- 打造企业级记忆系统
- 实现智能化状态管理
- 为大规模应用优化

### 方案5：统一状态管理 (8周)

#### 🔧 实现内容
**新增文件**：`runner/agent/state/unified_state_manager.py`

```python
class UnifiedStateManager:
    """统一状态管理器"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state_history: List[StateRecord] = []

    def update_page_state(self, url: str, title: str, elements: List[Dict]):
        """更新页面状态"""
        record = StateRecord(
            id=f"page_{int(time.time())}",
            type=StateType.PAGE,
            timestamp=time.time(),
            data={"url": url, "title": title, "elements": elements}
        )
        self._store(record)

    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        current_page = self._get_latest(StateType.PAGE)
        recent_actions = self._get_recent(StateType.ACTION, limit=10)

        return {
            "page": current_page.data if current_page else None,
            "actions": [a.data for a in recent_actions],
            "timestamp": time.time()
        }
```

#### 🎯 核心功能
1. **页面状态管理**：跟踪URL、标题、元素变化
2. **操作历史记录**：记录所有操作及结果
3. **状态查询**：快速获取当前状态
4. **状态恢复**：支持状态回滚

#### ✅ 验收标准
- [ ] 状态管理稳定可靠
- [ ] 查询性能 < 10ms
- [ ] 内存占用合理
- [ ] 支持状态回滚

---

### 📅 阶段3时间表

| 周 | 任务 | 负责人 | 里程碑 |
|----|------|--------|--------|
| 第7-8周 | 设计状态管理架构 | 待定 | 架构设计 |
| 第9-10周 | 实现核心功能 | 待定 | 功能完成 |
| 第11-12周 | 集成测试 | 待定 | 测试通过 |
| 第13-14周 | 性能优化 | 待定 | 性能达标 |

### 💰 阶段3工作量
- **开发时间**：8人周
- **测试时间**：4人周
- **文档时间**：2人周
- **总计**：14人周

---

## 🔍 质量保证

### 测试策略

#### 单元测试
- **SimpleMemory**：测试记忆存储、检索、清理
- **ActionDeduplicator**：测试去重逻辑、缓存命中
- **StateManager**：测试状态更新、查询、回滚

#### 集成测试
- **端到端测试**：使用basic_usage.txt验证改进效果
- **性能测试**：对比改进前后的执行效率
- **压力测试**：长时间运行稳定性

#### 回归测试
- **现有测试**：确保不影响现有功能
- **兼容性测试**：确保向后兼容

### 测试文件
```
tests/test_memory/
├── test_simple_memory.py
├── test_deduplication.py
├── test_state_manager.py
└── test_e2e_reduction.py
```

---

## ⚠️ 风险评估

### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 记忆机制引入性能问题 | 中 | 中 | 限制记忆大小，优化查询 |
| 状态同步不一致 | 高 | 低 | 增加同步检查，完善日志 |
| 内存泄漏 | 高 | 低 | 定期清理，设置上限 |
| 向后兼容性问题 | 中 | 低 | 充分测试，渐进迁移 |

### 进度风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 开发进度延迟 | 中 | 中 | 预留缓冲时间，分阶段交付 |
| 测试发现重大问题 | 高 | 中 | 增加测试覆盖，早期发现 |
| 依赖库版本冲突 | 中 | 低 | 版本锁定，兼容性测试 |

### 资源风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 开发人力不足 | 高 | 低 | 合理安排优先级，分阶段实施 |
| 测试环境不稳定 | 中 | 中 | 准备备用环境，容器化部署 |

---

## 📈 成功指标

### 技术指标
- [ ] 重复执行率 < 3%
- [ ] 执行效率提升 > 30%
- [ ] 内存占用 < 100MB
- [ ] 向后兼容性 100%

### 业务指标
- [ ] 用户满意度 > 9/10
- [ ] 支持测试用例数量增长 50%
- [ ] 减少人工干预 80%
- [ ] 提升系统稳定性 20%

### 过程指标
- [ ] 代码覆盖率 > 80%
- [ ] 缺陷密度 < 0.5/KLOC
- [ ] 文档完整度 100%
- [ ] 培训覆盖率 100%

---

## 💰 资源需求

### 人力资源
| 角色 | 人数 | 工作时间 | 技能要求 |
|------|------|----------|----------|
| Python开发 | 1 | 全程 | Python, LangGraph, AI |
| Node.js开发 | 1 | 阶段1 | TypeScript, Express |
| 测试工程师 | 1 | 阶段2-3 | 自动化测试, 性能测试 |
| 技术文档 | 0.5 | 全程 | 技术写作, API文档 |

### 环境资源
- **开发环境**：2台高配开发机器
- **测试环境**：1套完整测试环境
- **监控工具**：日志分析、性能监控
- **第三方服务**：无（仅使用现有依赖）

### 预算估算
- **人力成本**：24.5人周 × ¥8000/人周 = ¥196,000
- **设备成本**：¥20,000
- **总计**：¥216,000

---

## 📚 文档计划

### 技术文档
1. **设计文档**：架构设计、API文档
2. **开发文档**：编码规范、测试指南
3. **运维文档**：部署指南、故障排查

### 用户文档
1. **使用手册**：新功能使用指南
2. **最佳实践**：记忆机制使用建议
3. **常见问题**：FAQ和解决方案

### 交付清单
- [ ] 设计文档（20页）
- [ ] API文档（完整）
- [ ] 测试报告（每阶段）
- [ ] 用户手册（10页）
- [ ] 运维指南（15页）

---

## 🎬 项目里程碑

### 里程碑1：阶段1完成
**时间**：第2周结束
**交付物**：
- Node.js去重中间件
- Python简单记忆
- 阶段1测试报告
- 初步改进效果报告

**验收标准**：
- 重复执行率降低至5%
- 性能无明显下降
- 现有功能正常

### 里程碑2：阶段2完成
**时间**：第6周结束
**交付物**：
- LangGraph MemorySaver集成
- 混合记忆架构
- 阶段2测试报告
- 性能对比报告

**验收标准**：
- 重复执行率 < 3%
- 状态持久化稳定
- 内存占用合理

### 里程碑3：阶段3完成
**时间**：第14周结束
**交付物**：
- 统一状态管理系统
- 完整技术文档
- 最终测试报告
- 项目总结报告

**验收标准**：
- 所有指标达标
- 文档完整
- 用户培训完成

---

## 🔄 持续改进

### 监控指标
- **重复执行率**：每周统计
- **执行性能**：实时监控
- **内存使用**：定期检查
- **错误率**：实时告警

### 反馈机制
- **用户反馈**：定期收集
- **代码审查**：每次提交
- **性能基准**：每月对比
- **技术分享**：双周会议

### 后续优化
- **智能记忆**：基于AI的记忆优化
- **自适应阈值**：动态调整去重参数
- **分布式记忆**：多实例状态同步
- **预测性执行**：基于历史预测操作

---

## 📞 联系方式

### 项目组
- **项目经理**：[待定]
- **技术负责人**：[待定]
- **测试负责人**：[待定]

### 汇报机制
- **周报**：每周五提交
- **月报**：每月最后一个工作日
- **里程碑报告**：每个里程碑结束后3天

---

## 📝 附录

### A. 相关文档
1. [Midscene-Agent重复执行问题深度分析报告](./analysis_plan.md)
2. [技术设计文档](./design_doc.md)
3. [测试计划](./test_plan.md)

### B. 参考资料
1. LangGraph MemorySaver文档
2. Python内存管理最佳实践
3. Node.js缓存策略

### C. 变更日志
| 版本 | 日期 | 修改内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2025-12-21 | 初始版本 | 待定 |

---

**计划批准**：[待签名]
**计划日期**：2025-12-21
**版本**：v1.0