# UV 迁移快速参考

## 一键迁移

```bash
# 运行迁移脚本
./migrate_to_uv.sh
```

## 手动迁移步骤

### 1. 创建 pyproject.toml
```bash
cat > pyproject.toml << 'EOF'
[project]
name = "midscene-agent"
version = "1.0.0"
description = "AI-driven web automation framework"
requires-python = ">=3.10"
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
]

[project.scripts]
midscene = "runner.run:main"
midscene-check = "runner.check_config:check_config"
midscene-yaml = "runner.executor.yaml_executor:main"
midscene-text = "runner.executor.text_executor:main"
EOF
```

### 2. 移动 .env
```bash
mv runner/.env .env
```

### 3. 创建 runner/__init__.py
```bash
cat > runner/__init__.py << 'EOF'
"""
Midscene Agent Runner Package
"""
__version__ = "1.0.0"
from .agent import MidsceneAgent
__all__ = ["MidsceneAgent"]
EOF
```

### 4. 更新 langgraph.json
```bash
cat > graph/langgraph.json << 'EOF'
{
  "dependencies": [".", "/e/code/midscene-agent"],
  "graphs": {
    "midscene_agent": "/e/code/midscene-agent/graph/langgraph_cli.py:graph"
  },
  "env": "/e/code/midscene-agent/.env"
}
EOF
```

### 5. 更新导入路径

**runner/run.py**:
```python
# 移除: sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 更新导入:
from runner.check_config import check_config
from runner.modes import yaml_mode, text_mode, custom_mode
# 更新 .env 路径:
env_path = os.path.join(os.path.dirname(script_dir), ".env")
```

**runner/executor/*.py**:
```python
# 移除 sys.path 注入代码
# 更新导入:
from runner.agent.agent import MidsceneAgent
```

**runner/modes/*.py**:
```python
# 更新导入:
from runner.utils.path_utils import get_tests_dir
```

### 6. 安装
```bash
# 安装 UV (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目
uv pip install -e .
```

## 命令对照表

| 旧命令 | 新命令 |
|-------|-------|
| `cd runner && python run.py` | `midscene` |
| `cd runner && python check_config.py` | `midscene-check` |
| `python -m executor.yaml_executor test.yaml` | `midscene-yaml test.yaml` |
| `python -m executor.text_executor test.txt` | `midscene-text test.txt` |

## 验证

```bash
# 测试命令
midscene-check

# 测试导入
uv run python -c "from runner.agent import MidsceneAgent; print('OK')"
```

## 回退

```bash
# 如果有问题，可以回退
git checkout HEAD -- .
rm -rf .git
```

## 详细文档

- 完整迁移方案: `docs/UV_MIGRATION_COMPLETE.md`
- UV 使用指南: `docs/UV_USAGE_GUIDE.md`

