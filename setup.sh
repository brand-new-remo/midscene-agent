#!/bin/bash

# Midscene LangGraph Agent - 快速初始化脚本
# 此脚本将自动设置环境并验证配置

set -e  # 遇到错误立即退出

echo "================================================"
echo "  🕷️  Midscene LangGraph Agent - 初始化向导"
echo "================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查操作系统
echo "📋 检查系统环境..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    echo -e "  ${GREEN}✓${NC} 检测到 Linux 系统"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    echo -e "  ${GREEN}✓${NC} 检测到 macOS 系统"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="Windows"
    echo -e "  ${YELLOW}⚠${NC} 检测到 Windows 系统（建议使用 WSL）"
else
    OS="Unknown"
    echo -e "  ${YELLOW}⚠${NC} 未识别的操作系统: $OSTYPE"
fi
echo ""

# 检查 Python 版本
echo "🐍 检查 Python 环境..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 10 ]; then
    echo -e "  ${GREEN}✓${NC} Python 版本: $python_version (满足要求 >= 3.10)"
else
    echo -e "  ${RED}✗${NC} Python 版本过低: $python_version"
    echo -e "  ${YELLOW}请升级到 Python 3.10 或更高版本${NC}"
    exit 1
fi
echo ""

# 检查 Node.js
echo "📦 检查 Node.js 环境..."
if command -v node &> /dev/null; then
    node_version=$(node --version | sed 's/v//')
    node_major=$(echo $node_version | cut -d. -f1)
    if [ "$node_major" -ge 18 ]; then
        echo -e "  ${GREEN}✓${NC} Node.js 版本: v$node_version (满足要求 >= 18)"
    else
        echo -e "  ${RED}✗${NC} Node.js 版本过低: v$node_version"
        echo -e "  ${YELLOW}请升级到 Node.js 18 或更高版本${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}✗${NC} 未找到 Node.js"
    echo -e "  ${YELLOW}请安装 Node.js: https://nodejs.org/${NC}"
    exit 1
fi
echo ""

# 检查 Chrome
echo "🌐 检查 Chrome 浏览器..."
if command -v google-chrome &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} 找到 Google Chrome"
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    echo -e "  ${GREEN}✓${NC} 找到 Google Chrome (macOS)"
elif command -v chromium-browser &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} 找到 Chromium"
else
    echo -e "  ${YELLOW}⚠${NC} 未找到 Chrome 浏览器"
    echo -e "  ${YELLOW}请安装 Google Chrome: https://www.google.com/chrome/${NC}"
fi
echo ""

# 创建虚拟环境（可选）
echo "🔧 环境设置..."
read -p "是否创建虚拟环境? (推荐) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
        echo -e "  ${GREEN}✓${NC} 虚拟环境创建完成"
    fi
    echo "激活虚拟环境..."
    source venv/bin/activate
    echo -e "  ${GREEN}✓${NC} 虚拟环境已激活"
else
    echo -e "  ${YELLOW}⚠${NC} 使用系统 Python 环境（可能会影响其他项目）"
fi
echo ""

# 安装 Python 依赖
echo "⬇️  安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "  ${GREEN}✓${NC} Python 依赖安装完成"
echo ""

# 安装 Midscene
echo "⬇️  安装 Midscene CLI..."
if npm list -g @midscene/web &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Midscene 已安装"
else
    echo "安装 Midscene CLI..."
    npm install -g @midscene/web
    echo -e "  ${GREEN}✓${NC} Midscene 安装完成"
fi
echo ""

# 配置环境变量
echo "⚙️  环境变量配置..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "  ${GREEN}✓${NC} 已创建 .env 文件"
    fi
fi

if grep -q "DEEPSEEK_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} DEEPSEEK_API_KEY 已配置"
else
    echo -e "  ${YELLOW}⚠${NC} 请编辑 .env 文件并添加您的 DEEPSEEK_API_KEY"
    echo -e "  ${YELLOW}获取 API Key: https://platform.deepseek.com/${NC}"
fi
echo ""

# 验证安装
echo "🔍 验证安装..."
echo "测试 Midscene CLI..."
if npx @midscene/web --version &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Midscene CLI 工作正常"
else
    echo -e "  ${RED}✗${NC} Midscene CLI 测试失败"
fi
echo ""

# 完成提示
echo "================================================"
echo "  ✅ 初始化完成！"
echo "================================================"
echo ""
echo "📚 接下来您可以："
echo ""
echo "1. 编辑 .env 文件添加您的 API Key:"
echo "   ${BLUE}nano .env${NC}"
echo ""
echo "2. 运行快速测试:"
echo "   ${BLUE}python run.py${NC}"
echo ""
echo "3. 查看示例代码:"
echo "   ${BLUE}python examples/basic_usage.py${NC}"
echo ""
echo "4. 阅读文档:"
echo "   ${BLUE}cat README.md${NC}"
echo ""
echo "================================================"
echo ""

# 询问是否立即测试
read -p "是否现在运行快速测试? [y/N]: " run_test
if [[ $run_test =~ ^[Yy]$ ]]; then
    echo ""
    echo "运行快速测试..."
    echo ""
    python run.py
fi
