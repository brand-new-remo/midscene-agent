#!/bin/bash
# UV 迁移一键执行脚本

set -e  # 遇到错误立即退出

echo "========================================="
echo "  Midscene Agent UV 迁移脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在正确的目录
if [ ! -f "runner/run.py" ]; then
    print_error "请在项目根目录 (/e/code/midscene-agent) 运行此脚本"
    exit 1
fi

print_info "开始 UV 迁移过程..."
echo ""

# 步骤 1: 备份
print_info "步骤 1: 创建备份..."
git add .
git commit -m "feat: 迁移前备份" || true
print_info "✅ 备份完成"
echo ""

# 步骤 2: 创建 pyproject.toml
print_info "步骤 2: 创建 pyproject.toml..."
cat > pyproject.toml << 'PYPROJECT_EOF'
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
PYPROJECT_EOF

print_info "✅ pyproject.toml 创建完成"
echo ""

# 步骤 3: 移动 .env
print_info "步骤 3: 移动 .env 文件到根目录..."
if [ -f "runner/.env" ]; then
    mv runner/.env .env
    print_info "✅ .env 文件已移动到根目录"
else
    print_warning "未找到 runner/.env 文件，跳过"
fi
echo ""

# 步骤 4: 创建 runner/__init__.py
print_info "步骤 4: 创建 runner/__init__.py..."
cat > runner/__init__.py << 'INIT_EOF'
"""
Midscene Agent Runner Package

This package contains the core automation framework.
"""

__version__ = "1.0.0"
__author__ = "AI Automation Team"

from .agent import MidsceneAgent

__all__ = ["MidsceneAgent"]
INIT_EOF

print_info "✅ runner/__init__.py 创建完成"
echo ""

# 步骤 5: 更新 langgraph.json
print_info "步骤 5: 更新 langgraph.json..."
cat > graph/langgraph.json << 'LANGGRAPH_EOF'
{
  "dependencies": [".", "/e/code/midscene-agent"],
  "graphs": {
    "midscene_agent": "/e/code/midscene-agent/graph/langgraph_cli.py:graph"
  },
  "env": "/e/code/midscene-agent/.env"
}
LANGGRAPH_EOF

print_info "✅ langgraph.json 更新完成"
echo ""

# 步骤 6: 更新文件中的导入路径
print_info "步骤 6: 更新 Python 文件中的导入路径..."

# 更新 run.py
if [ -f "runner/run.py" ]; then
    sed -i.bak 's/sys\.path\.insert(0, os\.path\.dirname(os\.path\.abspath(__file__))))//' runner/run.py
    sed -i.bak 's/from check_config import check_config/from runner.check_config import check_config/' runner/run.py
    sed -i.bak 's/from modes import yaml_mode, text_mode, custom_mode/from runner.modes import yaml_mode, text_mode, custom_mode/' runner/run.py
    sed -i.bak 's/env_path = os\.path\.join(script_dir, "\.env")/env_path = os.path.join(os.path.dirname(script_dir), ".env")/' runner/run.py
    print_info "✅ run.py 更新完成"
fi

# 更新 executor/yaml_executor.py
if [ -f "runner/executor/yaml_executor.py" ]; then
    sed -i.bak '/# 添加 runner to sys\.path/,/sys\.path\.insert(0, runner_dir)/d' runner/executor/yaml_executor.py
    sed -i.bak 's/from agent\.agent import MidsceneAgent/from runner.agent.agent import MidsceneAgent/' runner/executor/yaml_executor.py
    sed -i.bak 's/from template\.engine import TemplateEngine/from runner.template.engine import TemplateEngine/' runner/executor/yaml_executor.py
    print_info "✅ yaml_executor.py 更新完成"
fi

# 更新 executor/text_executor.py
if [ -f "runner/executor/text_executor.py" ]; then
    sed -i.bak '/# 添加 runner to sys\.path/,/sys\.path\.insert(0, runner_dir)/d' runner/executor/text_executor.py
    sed -i.bak 's/from agent\.agent import MidsceneAgent/from runner.agent.agent import MidsceneAgent/' runner/executor/text_executor.py
    print_info "✅ text_executor.py 更新完成"
fi

# 更新 modes/*.py
for file in runner/modes/*.py; do
    if [ -f "$file" ]; then
        sed -i.bak 's/from utils\.path_utils import get_tests_dir/from runner.utils.path_utils import get_tests_dir/' "$file"
        print_info "✅ $(basename $file) 更新完成"
    fi
done

# 更新 check_config.py
if [ -f "runner/check_config.py" ]; then
    sed -i.bak 's/env_path = os\.path\.join(script_dir, "\.env")/env_path = os.path.join(os.path.dirname(script_dir), ".env")/' runner/check_config.py
    print_info "✅ check_config.py 更新完成"
fi

echo ""

# 步骤 7: 检查 UV 是否安装
print_info "步骤 7: 检查 UV 是否安装..."
if ! command -v uv &> /dev/null; then
    print_warning "UV 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    print_info "✅ UV 安装完成"
else
    print_info "✅ UV 已安装"
fi
echo ""

# 步骤 8: 安装项目
print_info "步骤 8: 安装项目为开发模式..."
uv pip install -e .
print_info "✅ 项目安装完成"
echo ""

# 步骤 9: 验证安装
print_info "步骤 9: 验证安装..."
if command -v midscene &> /dev/null; then
    print_info "✅ midscene 命令可用"
else
    print_error "❌ midscene 命令不可用"
fi

if command -v midscene-check &> /dev/null; then
    print_info "✅ midscene-check 命令可用"
else
    print_error "❌ midscene-check 命令不可用"
fi
echo ""

# 步骤 10: 测试导入
print_info "步骤 10: 测试 Python 导入..."
uv run python -c "from runner.agent import MidsceneAgent; print('✅ 导入成功')" || print_error "❌ 导入失败"
echo ""

print_info "========================================="
print_info "  🎉 UV 迁移完成！"
print_info "========================================="
echo ""
print_info "新命令使用方法:"
echo "  - 交互式启动器: midscene"
echo "  - 检查配置: midscene-check"
echo "  - 运行 YAML 测试: midscene-yaml test.yaml"
echo "  - 运行文本测试: midscene-text test.txt"
echo ""
print_info "详细文档: docs/UV_MIGRATION_COMPLETE.md"
echo ""
print_warning "如需回退，请运行: git checkout HEAD -- ."
echo ""

