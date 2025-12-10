# LangGraph Dev 代码提取到 graph/ 目录实施计划

## 1. 项目概述

### 目标
将 langgraph dev 服务相关代码从 `runner/` 目录提取到根目录的 `graph/` 目录下，实现更好的模块化和代码组织。

### 提取范围
需要移动的5个文件：
1. `runner/langgraph.json` → `graph/langgraph.json`
2. `runner/langgraph_cli.py` → `graph/langgraph_cli.py`
3. `runner/agent/cli_adapter.py` → `graph/cli_adapter.py`
4. `runner/agent/tools/langgraph_adapter.py` → `graph/langgraph_adapter.py`
5. `runner/agent/tools/definitions.py` → `graph/definitions.py`

### 保留依赖
以下模块保留在 `runner/` 中，graph/ 模块通过导入访问：
- `runner/agent/http_client.py`
- `runner/agent/config.py`
- `runner/agent/agent.py`

## 2. 依赖关系分析

### 当前依赖图
```
langgraph.json (待移动)
  └─> langgraph_cli.py (待移动)
        └─> cli_adapter.py (待移动)
              ├─> agent.http_client (保留在 runner/)
              ├─> agent.config (保留在 runner/)
              └─> agent.agent (保留在 runner/)

langgraph_adapter.py (待移动)
  └─> definitions.py (待移动)
```

### 关键发现
1. `definitions.py` 是独立的工具定义模块，无外部依赖
2. `langgraph_adapter.py` 仅依赖 `definitions.py`（同目录）
3. `cli_adapter.py` 是核心适配器，依赖 runner/ 中的3个核心模块
4. `langgraph_cli.py` 仅依赖 `cli_adapter.py`
5. `langgraph.json` 是配置文件，指向 `langgraph_cli.py:graph`

## 3. 设计方案

### 3.1 目录结构设计

```
/Users/duangangqiang/github/midscene/
├── graph/                          # 新创建的 graph 目录
│   ├── __init__.py                 # graph 包初始化文件
│   ├── langgraph.json             # 配置文件
│   ├── langgraph_cli.py           # LangGraph CLI 入口点
│   ├── cli_adapter.py             # CLI 适配器
│   ├── langgraph_adapter.py       # 工具适配器
│   ├── definitions.py             # 工具定义
│   └── README.md                  # 使用说明文档
│
├── runner/                         # 保留原 runner 目录
│   ├── agent/
│   │   ├── http_client.py         # 保留
│   │   ├── config.py              # 保留
│   │   ├── agent.py               # 保留
│   │   └── ...                    # 其他文件保留
│   └── ...
│
└── ...
```

### 3.2 Python 包结构

**方案：使用绝对导入路径**

在 graph/ 模块中，通过绝对导入访问 runner/ 中的模块：

```python
# graph/cli_adapter.py 中的导入
from runner.agent.http_client import MidsceneHTTPClient, SessionConfig
from runner.agent.config import Config
from runner.agent.agent import MidsceneAgent
```

**替代方案对比：**

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 绝对导入 | 清晰、明确、无歧义 | 需要确保 runner/ 在 Python 路径中 | ⭐⭐⭐⭐⭐ |
| 相对导入 | 简洁 | 需处理复杂的相对路径 | ⭐⭐⭐ |
| 适配层 | 完全解耦 | 代码冗余 | ⭐⭐ |

**推荐：绝对导入方案**

原因：
1. 依赖关系清晰明确
2. 维护成本低
3. IDE 支持好
4. 符合 Python 最佳实践

## 4. 实施步骤

### 阶段1：准备工作

#### 步骤1.1：创建 graph/ 目录结构
```bash
# 创建目录
mkdir -p /Users/duangangqiang/github/midscene/graph

# 创建 __init__.py
touch /Users/duangangqiang/github/midscene/graph/__init__.py
```

#### 步骤1.2：复制文件到 graph/ 目录
```bash
# 复制5个文件
cp runner/langgraph.json graph/
cp runner/langgraph_cli.py graph/
cp runner/agent/cli_adapter.py graph/
cp runner/agent/tools/langgraph_adapter.py graph/
cp runner/agent/tools/definitions.py graph/
```

#### 步骤1.3：备份原文件（可选但推荐）
```bash
# 创建备份目录
mkdir -p /Users/duangangqiang/github/midscene/.backup/langgraph_extract

# 备份原文件
cp runner/langgraph.json .backup/langgraph_extract/
cp runner/langgraph_cli.py .backup/langgraph_extract/
cp runner/agent/cli_adapter.py .backup/langgraph_extract/
cp runner/agent/tools/langgraph_adapter.py .backup/langgraph_extract/
cp runner/agent/tools/definitions.py .backup/langgraph_extract/
```

### 阶段2：修改导入路径

#### 步骤2.1：修改 `graph/cli_adapter.py`

**原导入：**
```python
from agent.http_client import MidsceneHTTPClient, SessionConfig
from agent.config import Config
from agent.agent import MidsceneAgent
```

**修改为：**
```python
from runner.agent.http_client import MidsceneHTTPClient, SessionConfig
from runner.agent.config import Config
from runner.agent.agent import MidsceneAgent
```

#### 步骤2.2：修改 `graph/langgraph_cli.py`

**原导入：**
```python
from agent.cli_adapter import MidsceneAgentAdapter
```

**修改为：**
```python
from graph.cli_adapter import MidsceneAgentAdapter
```

#### 步骤2.3：修改 `graph/langgraph_adapter.py`

**原导入：**
```python
from .definitions import TOOL_DEFINITIONS, ...
```

**修改为：**
```python
from graph.definitions import TOOL_DEFINITIONS, ...
```

### 阶段3：更新配置文件

#### 步骤3.1：更新 `graph/langgraph.json`

**原配置：**
```json
{
  "dependencies": ["."],
  "graphs": {
    "midscene_agent": "./langgraph_cli.py:graph"
  },
  "env": ".env"
}
```

**修改为：**
```json
{
  "dependencies": ["."],
  "graphs": {
    "midscene_agent": "./graph/langgraph_cli.py:graph"
  },
  "env": "./runner/.env"
}
```

**说明：**
- `graphs` 路径从 `./langgraph_cli.py` 更新为 `./graph/langgraph_cli.py`
- `env` 路径从 `.env` 更新为 `./runner/.env`（因为 runner/ 是 .env 文件的位置）

### 阶段4：创建文档

#### 步骤4.1：创建 `graph/README.md`

内容应包括：
1. graph/ 目录说明
2. 使用方法
3. 与 runner/ 的关系
4. 常见问题

### 阶段5：验证和测试

#### 步骤5.1：验证 Python 导入

```bash
# 在项目根目录运行
cd /Users/duangangqiang/github/midscene

# 测试导入
python -c "from graph.cli_adapter import MidsceneAgentAdapter; print('✅ 导入成功')"
python -c "from graph.langgraph_cli import graph; print('✅ LangGraph 导入成功')"
python -c "from graph.definitions import TOOL_DEFINITIONS; print('✅ 工具定义导入成功')"
```

#### 步骤5.2：验证 langgraph CLI

```bash
# 确保 runner/ 目录有 .env 文件
cd /Users/duangangqiang/github/midscene

# 启动 LangGraph 开发服务器
langgraph dev --config graph/langgraph.json

# 预期结果：
# - 无导入错误
# - 服务器启动成功
# - 访问 http://localhost:2024 可以看到 midscene_agent
```

#### 步骤5.3：功能测试

在 LangGraph Web UI 中测试：
1. 发送简单指令："打开 https://www.baidu.com"
2. 验证响应是否正常
3. 检查会话管理是否正常

### 阶段6：清理（可选）

#### 步骤6.1：从 runner/ 目录删除原文件

```bash
# 删除原文件
rm runner/langgraph.json
rm runner/langgraph_cli.py
rm runner/agent/cli_adapter.py
rm runner/agent/tools/langgraph_adapter.py
rm runner/agent/tools/definitions.py
```

**注意：**
- 建议先验证新位置工作正常后再删除
- 保留备份直到完全确认

## 5. 潜在问题和解决方案

### 问题1：Python 导入错误

**症状：**
```
ModuleNotFoundError: No module named 'runner'
```

**解决方案：**
确保 Python 能够找到 `runner` 模块：

1. **从项目根目录运行：**
   ```bash
   cd /Users/duangangqiang/github/midscene
   python graph/test_imports.py
   ```

2. **设置 PYTHONPATH：**
   ```bash
   export PYTHONPATH="/Users/duangangqiang/github/midscene:$PYTHONPATH"
   python -m graph.langgraph_cli
   ```

3. **使用绝对路径：**
   在代码中使用完整路径导入

### 问题2：LangGraph CLI 无法找到配置文件

**症状：**
```
FileNotFoundError: langgraph.json not found
```

**解决方案：**
明确指定配置文件路径：
```bash
langgraph dev --config graph/langgraph.json
```

或在 `graph/langgraph.json` 中使用相对路径：
```json
{
  "graphs": {
    "midscene_agent": "./langgraph_cli.py:graph"
  }
}
```

### 问题3：环境变量文件路径错误

**症状：**
```
FileNotFoundError: .env file not found
```

**解决方案：**
在 `graph/langgraph.json` 中明确指定：
```json
{
  "env": "../runner/.env"
}
```

或复制 .env 文件到 graph/ 目录：
```bash
cp runner/.env graph/
```

### 问题4：循环依赖

**症状：**
```
ImportError: cannot import name 'X' from partially initialized module
```

**预防措施：**
1. 检查依赖关系，确保无循环导入
2. 使用延迟导入（在函数内部导入）

### 问题5：模块初始化问题

**症状：**
```
AttributeError: module 'graph' has no attribute 'cli_adapter'
```

**解决方案：**
确保 `graph/__init__.py` 正确导出模块：
```python
# graph/__init__.py
from .cli_adapter import MidsceneAgentAdapter
from .definitions import TOOL_DEFINITIONS

__all__ = ['MidsceneAgentAdapter', 'TOOL_DEFINITIONS']
```

## 6. 验证方法

### 6.1 导入验证

```python
# test_imports.py
import sys
sys.path.insert(0, '/Users/duangangqiang/github/midscene')

def test_imports():
    """测试所有导入"""
    try:
        from graph.definitions import TOOL_DEFINITIONS
        print("✅ definitions 导入成功")

        from graph.langgraph_adapter import create_langgraph_tools
        print("✅ langgraph_adapter 导入成功")

        from graph.cli_adapter import MidsceneAgentAdapter
        print("✅ cli_adapter 导入成功")

        from graph.langgraph_cli import graph
        print("✅ langgraph_cli 导入成功")

        print("\n🎉 所有导入测试通过！")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
```

### 6.2 功能验证

```python
# test_functionality.py
import asyncio
from graph.cli_adapter import MidsceneAgentAdapter

async def test_functionality():
    """测试基本功能"""
    try:
        adapter = MidsceneAgentAdapter()
        print("✅ MidsceneAgentAdapter 初始化成功")

        # 注意：这里只是测试初始化，不执行实际操作
        print("✅ 基本功能测试通过！")
        return True
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_functionality())
    sys.exit(0 if success else 1)
```

### 6.3 LangGraph CLI 验证

```bash
# 启动开发服务器
cd /Users/duangangqiang/github/midscene
langgraph dev --config graph/langgraph.json

# 检查：
# 1. 服务器启动无错误
# 2. 访问 http://localhost:2024
# 3. 可以看到 midscene_agent
# 4. 发送测试消息有响应
```

## 7. 回滚计划

如果提取过程中出现问题，可以按以下步骤回滚：

### 7.1 从备份恢复

```bash
# 从备份恢复文件
cp .backup/langgraph_extract/* runner/

# 删除 graph/ 目录
rm -rf graph/
```

### 7.2 验证恢复

```bash
# 测试原始配置
cd runner
python langgraph_cli.py
```

### 7.3 清理

```bash
# 删除备份
rm -rf .backup/langgraph_extract
```

## 8. 最佳实践

### 8.1 代码组织
1. 保持依赖关系清晰
2. 避免循环导入
3. 使用类型提示
4. 添加文档字符串

### 8.2 测试
1. 每个阶段后进行验证
2. 保留备份直到完全确认
3. 使用自动化测试脚本
4. 测试边界情况

### 8.3 文档
1. 更新 README.md
2. 添加使用示例
3. 记录依赖关系
4. 提供故障排除指南

## 9. 后续改进

### 9.1 优化导入
- 考虑使用 `__init__.py` 显式导出
- 使用 `from typing import TYPE_CHECKING` 优化性能

### 9.2 配置管理
- 考虑在 graph/ 目录中创建独立的 .env.example
- 统一配置管理

### 9.3 工具扩展
- 在 graph/ 目录中添加更多工具
- 优化工具分类和组织

## 10. 总结

本实施计划提供了一个完整的 langgraph dev 代码提取方案，包括：

1. **清晰的目录结构**：graph/ 和 runner/ 分离
2. **详细的步骤**：6个阶段，20+ 个具体步骤
3. **问题预防**：5个常见问题和解决方案
4. **验证方法**：3层验证确保正确性
5. **回滚计划**：确保安全可逆

通过遵循此计划，可以安全、高效地完成代码提取任务，实现更好的模块化和代码组织。

---

**文档版本：** 1.0
**创建日期：** 2025-12-10
**作者：** Claude Code
**状态：** 待实施