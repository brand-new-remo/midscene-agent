# Midscene Agent UV 迁移方案 - 完整版

## 目录
1. [概述](#概述)
2. [当前状态](#当前状态)
3. [迁移步骤](#迁移步骤)
4. [关键文件修改](#关键文件修改)
5. [命令对照表](#命令对照表)
6. [验证方法](#验证方法)
7. [回退方案](#回退方案)

---

## 概述

本方案将项目从 `runner/` 子目录运行模式迁移到使用 UV 包管理器的根目录运行模式。

### 迁移收益
- ✅ 现代化的包管理方式
- ✅ 更快的依赖安装（比 pip 快 10-100 倍）
- ✅ 简化的命令执行
- ✅ CLI 入口点支持
- ✅ 100% 向后兼容

---

## 当前状态

### 目录结构
```
/e/code/midscene-agent/
├── runner/                      # Python 代码位置
│   ├── run.py                   # 交互式启动器
│   ├── check_config.py          # 配置检查
│   ├── executor/                # 测试执行器
│   ├── modes/                   # 交互模式
│   ├── agent/                   # 核心智能体
│   ├── utils/                   # 工具函数
│   ├── requirements.txt         # Python 依赖
│   └── .env                     # 环境变量
├── graph/
│   ├── langgraph.json          # LangGraph 配置
│   └── cli_adapter.py          # 导入 runner 模块
└── ...
```

### 导入关系
- run.py: 使用 sys.path 注入 + 相对导入
- executor/*.py: 使用 sys.path 注入 + 绝对导入
- modes/*.py: 相对导入
- cli_adapter.py: 绝对导入 `from runner.agent...`


---

## 迁移步骤

### 步骤 1: 创建 pyproject.toml

**位置**: `/e/code/midscene-agent/pyproject.toml`

```toml
[project]
name = "midscene-agent"
version = "1.0.0"
description = "AI-driven web automation framework"
requires-python = ">=3.10"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "AI Automation Team", email = "team@example.com"}
]
keywords = ["automation", "web", "ai", "langgraph"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "langchain>=1.0.0",
    "langchain-core>=1.0.0",
    "langgraph>=1.0.0",
    "langchain-deepseek>=1.0.0",
    "aiohttp>=3.9.0",
    "asyncio-throttle>=1.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
midscene = "runner.run:main"
midscene-check = "runner.check_config:check_config"
midscene-yaml = "runner.executor.yaml_executor:main"
midscene-text = "runner.executor.text_executor:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]
```

### 步骤 2: 移动 .env 文件
```bash
mv runner/.env .env
```

### 步骤 3: 创建 runner/__init__.py
```python
"""
Midscene Agent Runner Package

This package contains the core automation framework.
"""

__version__ = "1.0.0"
__author__ = "AI Automation Team"

from .agent import MidsceneAgent

__all__ = ["MidsceneAgent"]
```

### 步骤 4: 更新 langgraph.json
```json
{
  "dependencies": [".", "/e/code/midscene-agent"],
  "graphs": {
    "midscene_agent": "/e/code/midscene-agent/graph/langgraph_cli.py:graph"
  },
  "env": "/e/code/midscene-agent/.env"
}
```


---

## 关键文件修改

### 1. runner/run.py

**修改前**:
```python
# 将当前目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_config import check_config
from modes import yaml_mode, text_mode, custom_mode

# .env 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
```

**修改后**:
```python
# 移除 sys.path 注入

from runner.check_config import check_config
from runner.modes import yaml_mode, text_mode, custom_mode

# .env 路径 - 指向根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(script_dir), ".env")
```

### 2. runner/executor/yaml_executor.py

**修改前**:
```python
# 添加 runner 到 sys.path
runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if runner_dir not in sys.path:
    sys.path.insert(0, runner_dir)

from agent.agent import MidsceneAgent
from template.engine import TemplateEngine
```

**修改后**:
```python
# 移除 sys.path 注入

from runner.agent.agent import MidsceneAgent
from runner.template.engine import TemplateEngine
```

### 3. runner/executor/text_executor.py

**修改前**:
```python
# 添加 runner 到 sys.path
runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if runner_dir not in sys.path:
    sys.path.insert(0, runner_dir)

from agent.agent import MidsceneAgent
```

**修改后**:
```python
# 移除 sys.path 注入

from runner.agent.agent import MidsceneAgent
```

### 4. runner/modes/yaml_mode.py

**修改前**:
```python
from utils.path_utils import get_tests_dir
```

**修改后**:
```python
from runner.utils.path_utils import get_tests_dir
```

### 5. runner/modes/text_mode.py

**修改前**:
```python
from utils.path_utils import get_tests_dir
```

**修改后**:
```python
from runner.utils.path_utils import get_tests_dir
```

### 6. runner/modes/custom_mode.py

**修改前**:
```python
from utils.path_utils import get_tests_dir
```

**修改后**:
```python
from runner.utils.path_utils import get_tests_dir
```

### 7. runner/check_config.py

**修改前**:
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
```

**修改后**:
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(script_dir), ".env")
```


---

## 命令对照表

### 传统方式 vs UV 方式

| 功能 | 传统方式 | UV 方式 |
|------|---------|--------|
| 交互式启动器 | `cd runner && python run.py` | `midscene` |
| 检查配置 | `cd runner && python check_config.py` | `midscene-check` |
| 运行 YAML 测试 | `cd runner && python -m executor.yaml_executor test.yaml` | `midscene-yaml test.yaml` |
| 运行文本测试 | `cd runner && python -m executor.text_executor test.txt` | `midscene-text test.txt` |
| 任意 Python 代码 | `cd runner && python -c "..."` | `uv run python -c "..."` |
| 安装依赖 | `cd runner && pip install -r requirements.txt` | `uv pip install -e .` |

### 安装步骤

```bash
# 1. 安装 UV (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安装项目为开发模式
cd /e/code/midscene-agent
uv pip install -e .

# 3. 验证安装
midscene-check

# 4. 运行交互式启动器
midscene
```

### LangGraph Chat UI

```bash
# 仍然使用标准方式
langgraph dev
# 访问 http://localhost:2024
```

---

## 验证方法

### 1. 验证安装
```bash
# 检查命令是否可用
midscene --help
midscene-check --help
midscene-yaml --help
midscene-text --help
```

### 2. 验证导入
```bash
# 测试 Python 导入
uv run python -c "from runner.agent import MidsceneAgent; print('✅ 导入成功')"
uv run python -c "from runner.utils.path_utils import get_tests_dir; print('✅ 导入成功')"
```

### 3. 验证功能
```bash
# 运行配置检查
echo "6" | midscene

# 检查配置文件
cat .env | grep DEEPSEEK
```

### 4. 验证 LangGraph
```bash
# 检查 langgraph.json 路径
cat graph/langgraph.json | grep "/e/code/midscene-agent"
```

---

## 回退方案

如果迁移出现问题，可以快速回退:

### 回退步骤

```bash
# 1. 恢复 .env 文件
mv .env runner/.env

# 2. 恢复 sys.path 注入代码
# (从 git 历史中恢复或手动还原)

# 3. 恢复 langgraph.json
git checkout HEAD -- graph/langgraph.json

# 4. 卸载 UV 安装
uv pip uninstall midscene-agent

# 5. 使用传统方式
cd runner
python run.py
```

### 验证回退
```bash
# 确认回退成功
cd runner
python -c "from agent.agent import MidsceneAgent; print('✅ 回退成功')"
```

---

## 风险评估

### 低风险
- ✅ 包结构保持不变
- ✅ 导入路径兼容
- ✅ 可选使用（传统方式仍可用）

### 中等风险
- ⚠️ .env 文件位置变更
  - **解决方案**: 脚本自动处理新路径
- ⚠️ LangGraph 配置路径变更
  - **解决方案**: 使用实际路径替换硬编码路径

### 高风险
- 无高风险项目

---

## 文档更新

### 需要更新的文档

1. **CLAUDE.md**
   - 更新所有 Python 命令示例
   - 添加 UV 使用说明

2. **README.md**
   - 添加 UV 安装指南
   - 添加快速开始部分

3. **docs/** 目录
   - 创建 UV_USAGE_GUIDE.md
   - 更新迁移指南

---

## 总结

### 迁移收益
- 🚀 更快的依赖安装
- 📦 现代化的包管理
- 🎯 简化的命令执行
- 🔧 CLI 入口点支持
- ♻️ 100% 向后兼容

### 迁移成本
- ⏱️ 预计时间: 30-60 分钟
- 💼 涉及文件: 10-15 个
- 🔄 风险等级: 低

### 建议
立即执行迁移。收益远大于成本，且有完整的回退方案。

