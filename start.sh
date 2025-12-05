#!/bin/bash

# Midscene Agent V2.0 快速启动脚本

set -e

echo ""
echo "=========================================="
echo "🚀 Midscene Agent V2.0 启动脚本"
echo "=========================================="
echo ""

# 检查依赖
echo "🔍 检查依赖..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js >= 18"
    echo "   下载地址: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 版本过低 (当前: $(node -v))，需要 >= 18"
    exit 1
fi

echo "✅ Node.js 版本: $(node -v)"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python >= 3.10"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到 .env 文件，正在创建..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑并添加您的 API 密钥"
    echo ""
    echo "请在 .env 文件中设置以下变量:"
    echo "  - DEEPSEEK_API_KEY=your-deepseek-api-key"
    echo "  - OPENAI_API_KEY=your-vision-api-key (可选)"
    echo ""
    read -p "编辑完成后按 Enter 键继续..."
fi

# 安装依赖
echo ""
echo "📦 安装依赖..."

# 安装 Node.js 依赖
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo "安装 Node.js 依赖..."
    npm install --silent
    echo "✅ Node.js 依赖安装完成"
else
    echo "✅ Node.js 依赖已安装"
fi

# 检查 Python 依赖
echo "检查 Python 依赖..."
if ! python3 -c "import aiohttp" &> /dev/null; then
    echo "安装 Python 依赖..."
    pip3 install -q -r requirements.txt
    echo "✅ Python 依赖安装完成"
else
    echo "✅ Python 依赖已安装"
fi

echo ""
echo "=========================================="
echo "🚀 启动服务"
echo "=========================================="
echo ""

# 启动 Node.js 服务
echo "启动 Node.js 服务..."
echo "服务地址: http://localhost:3000"
echo "API 文档: http://localhost:3000"
echo "监控指标: http://localhost:3000/metrics"
echo ""

# 启动服务
npm start

echo ""
echo "✅ 服务已启动"
echo ""
echo "在新终端中运行 Python 示例:"
echo "  python3 examples/basic_usage_v2.py"
echo ""
echo "或运行测试:"
echo "  python3 test_v2.py"
echo ""
echo "按 Ctrl+C 停止服务"