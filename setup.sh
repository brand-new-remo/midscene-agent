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

# 创建并激活 Conda 环境
echo "🔧 环境设置..."
echo "检查 Conda 是否已安装..."

# 尝试各种方式查找 conda
echo "  尝试查找 conda..."
if command -v conda &> /dev/null; then
    echo -e "    ✓ 找到 conda (command -v)"
    CONDA_FOUND=true
elif command -v conda.exe &> /dev/null; then
    echo -e "    ✓ 找到 conda.exe (command -v)"
    CONDA_FOUND=true
else
    echo -e "    ✗ 未通过 command -v 找到 conda/conda.exe"
    CONDA_FOUND=false
fi

# 在 Git Bash 中，尝试通过 Windows 路径查找 conda
if [[ "$CONDA_FOUND" == "false" ]]; then
    echo ""
    echo "  尝试通过 Windows 路径查找..."
    for path in "/c/Users/$USERNAME/.conda/condabin/conda.bat" "/C/Users/$USERNAME/.conda/condabin/conda.bat" "/c/conda/condabin/conda.bat" "/C/conda/condabin/conda.bat"; do
        if [[ -f "$path" ]]; then
            echo -e "    ✓ 找到 conda.bat: $path"
            export PATH="$(dirname $path):$PATH"
            CONDA_FOUND=true
            break
        else
            echo -e "    - 不存在: $path"
        fi
    done

    # 检查其他可能的位置
    if [[ -d "/c/ProgramData/Anaconda3" ]] || [[ -d "/c/ProgramData/Miniconda3" ]]; then
        echo -e "    检测到 Anaconda/Miniconda 安装目录"
        if [[ -d "/c/ProgramData/Anaconda3" ]]; then
            conda_path="/c/ProgramData/Anaconda3"
        else
            conda_path="/c/ProgramData/Miniconda3"
        fi
        echo -e "    conda 安装在: $conda_path"
        export PATH="$conda_path/Scripts:$conda_path/condabin:$PATH"
        CONDA_FOUND=true
    fi

    if [[ -d "/c/Users/$USERNAME/Anaconda3" ]] || [[ -d "/c/Users/$USERNAME/Miniconda3" ]]; then
        echo -e "    检测到用户目录下的 Anaconda/Miniconda 安装"
        if [[ -d "/c/Users/$USERNAME/Anaconda3" ]]; then
            conda_path="/c/Users/$USERNAME/Anaconda3"
        else
            conda_path="/c/Users/$USERNAME/Miniconda3"
        fi
        echo -e "    conda 安装在: $conda_path"
        export PATH="$conda_path/Scripts:$conda_path/condabin:$PATH"
        CONDA_FOUND=true
    fi
fi

echo ""
# 最终检查
if ! command -v conda &> /dev/null && ! command -v conda.exe &> /dev/null; then
    echo -e "  ${RED}✗${NC} 未找到 Conda"
    echo -e "  ${YELLOW}请先安装 Conda 后重试${NC}"
    echo -e "  ${YELLOW}安装指南: https://docs.conda.io/en/latest/miniconda.html${NC}"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} 找到 Conda"

CONDA_ENV_NAME="midscene-312"

# 检查是否已激活该环境（在 Git Bash 中可能使用不同的变量名）
CURRENT_ENV="${CONDA_DEFAULT_ENV:-${CONDA_ENV:-}}"
if [[ "$CURRENT_ENV" == "$CONDA_ENV_NAME" ]]; then
    echo -e "  ${GREEN}✓${NC} 已激活 Conda 环境: $CONDA_ENV_NAME"
else
    # 检查环境是否存在（Git Bash 中需要特殊处理）
    if conda env list 2>/dev/null | grep -q "^$CONDA_ENV_NAME " || \
       conda env list 2>/dev/null | grep -q "$CONDA_ENV_NAME"; then
        echo -e "  ${GREEN}✓${NC} 找到 Conda 环境: $CONDA_ENV_NAME"
        echo "激活 Conda 环境..."

        # Git Bash 中可能不需要 shell.bash hook
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            conda activate "$CONDA_ENV_NAME" 2>/dev/null || \
            eval "$(conda shell.bash hook)" && conda activate "$CONDA_ENV_NAME"
        else
            eval "$(conda shell.bash hook)"
            conda activate "$CONDA_ENV_NAME"
        fi

        CURRENT_ENV="${CONDA_DEFAULT_ENV:-${CONDA_ENV:-}}"
        if [[ "$CURRENT_ENV" == "$CONDA_ENV_NAME" ]]; then
            echo -e "  ${GREEN}✓${NC} Conda 环境激活成功"
        else
            # 在 Git Bash 中，如果激活失败但环境存在，可能已经是正确的环境
            echo -e "  ${YELLOW}⚠${NC} 无法自动激活，但环境已存在"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} 未找到 Conda 环境: $CONDA_ENV_NAME"
        echo ""
        read -p "是否创建 $CONDA_ENV_NAME 环境? (推荐) [y/N]: " create_env
        if [[ $create_env =~ ^[Yy]$ ]]; then
            echo "正在创建 Conda 环境 $CONDA_ENV_NAME (Python 3.12)..."
            conda create -n "$CONDA_ENV_NAME" python=3.12 -y
            echo -e "  ${GREEN}✓${NC} Conda 环境创建成功"

            echo "正在激活 Conda 环境..."
            if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
                conda activate "$CONDA_ENV_NAME" 2>/dev/null || \
                eval "$(conda shell.bash hook)" && conda activate "$CONDA_ENV_NAME"
            else
                eval "$(conda shell.bash hook)"
                conda activate "$CONDA_ENV_NAME"
            fi
            echo -e "  ${GREEN}✓${NC} Conda 环境激活成功"
        else
            echo -e "  ${YELLOW}⚠${NC} 使用当前 Python 环境"
        fi
    fi
fi
echo ""

# 检查 Python 版本
echo "🐍 检查 Python 环境..."
python_version=$(python --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 10 ]; then
    echo -e "  ${GREEN}✓${NC} Python 版本: $python_version (满足要求 >= 3.10)"
    echo -e "  ${GREEN}✓${NC} 当前环境: ${CONDA_DEFAULT_ENV:-系统环境}"
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
CHROME_FOUND=false
CHROME_PATH=""

# 检测各种可能的 Chrome 安装路径
if command -v google-chrome &> /dev/null; then
    CHROME_PATH=$(command -v google-chrome)
    echo -e "  ${GREEN}✓${NC} 找到 Google Chrome: $CHROME_PATH"
    CHROME_FOUND=true
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    echo -e "  ${GREEN}✓${NC} 找到 Google Chrome (macOS): $CHROME_PATH"
    CHROME_FOUND=true
elif [ -f "C:\Program Files\Google\Chrome\Application\chrome.exe" ]; then
    CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
    echo -e "  ${GREEN}✓${NC} 找到 Google Chrome (Windows): $CHROME_PATH"
    CHROME_FOUND=true
elif [ -f "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ]; then
    CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    echo -e "  ${GREEN}✓${NC} 找到 Google Chrome (Windows): $CHROME_PATH"
    CHROME_FOUND=true
elif command -v chromium-browser &> /dev/null; then
    CHROME_PATH=$(command -v chromium-browser)
    echo -e "  ${GREEN}✓${NC} 找到 Chromium: $CHROME_PATH"
    CHROME_FOUND=true
fi

# 如果自动检测失败，询问用户
if [ "$CHROME_FOUND" == "false" ]; then
    echo -e "  ${YELLOW}⚠${NC} 未找到 Chrome 浏览器"
    echo ""
    echo -e "  ${YELLOW}提示：${NC}"
    echo -e "  如果你已经安装了 Chrome，请按以下步骤找到正确的路径："
    echo -e "  1. 找到桌面上的 Chrome 快捷方式"
    echo -e "  2. 右键点击 -> 属性"
    echo -e "  3. 在「快捷方式」标签页中，找到「目标」字段"
    echo -e "  4. 复制该路径"
    echo ""
    echo "  或者直接安装 Google Chrome: https://www.google.com/chrome/"
    echo ""
    read -p "请输入 Chrome 浏览器的完整路径 (或留空跳过): " user_chrome_path

    if [ -n "$user_chrome_path" ]; then
        # 转换路径格式（处理反斜杠转义）
        if [[ "$user_chrome_path" == *\\* ]]; then
            # Windows 路径，转为 Unix 风格
            user_chrome_path=$(echo "$user_chrome_path" | sed 's/\\/\//g' | sed 's/^C\//\/c\//' | sed 's/^D\//\/d\//')
        fi

        if [ -f "$user_chrome_path" ]; then
            # 验证是否是 Chrome
            if echo "$user_chrome_path" | grep -qi "chrome"; then
                CHROME_PATH="$user_chrome_path"
                CHROME_FOUND=true
                echo -e "  ${GREEN}✓${NC} 验证通过，Chrome 路径: $CHROME_PATH"
            else
                echo -e "  ${RED}✗${NC} 路径不包含 chrome，可能不是 Chrome 浏览器"
            fi
        else
            echo -e "  ${RED}✗${NC} 文件不存在: $user_chrome_path"
        fi
    fi

    if [ "$CHROME_FOUND" == "false" ]; then
        echo -e "  ${YELLOW}⚠${NC} 跳过 Chrome 配置，请稍后手动在 .env 中设置 CHROME_PATH"
    fi
fi

# 如果找到了 Chrome，写入到 .env 文件
if [ "$CHROME_FOUND" == "true" ]; then
    # 转换路径为 Windows 风格（如果需要）
    if [[ "$CHROME_PATH" == /* ]]; then
        # Unix 路径转换为 Windows 路径，单个反斜杠
        CHROME_PATH=$(echo "$CHROME_PATH" | sed 's|^\/c\/|C:\\\\|g' | sed 's|^\/d\/|D:\\\\|g' | sed 's|/|\\\\|g')
        # 替换四个反斜杠为两个（因为转义问题）
        CHROME_PATH=$(echo "$CHROME_PATH" | sed 's|\\\\|\\|g')
    fi
    echo ""
    echo "正在配置 .env 文件..."
    echo "Chrome 路径: $CHROME_PATH"
    if [ -f ".env" ]; then
        # 检查是否已有 CHROME_PATH 配置
        if grep -q "^CHROME_PATH=" .env; then
            # 更新现有配置
            if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
                sed -i "s|^CHROME_PATH=.*|CHROME_PATH=$CHROME_PATH|" .env
            else
                sed -i '' "s|^CHROME_PATH=.*|CHROME_PATH=$CHROME_PATH|" .env
            fi
            echo -e "  ${GREEN}✓${NC} 已更新 .env 中的 CHROME_PATH"
        else
            # 添加新配置
            echo "CHROME_PATH=$CHROME_PATH" >> .env
            echo -e "  ${GREEN}✓${NC} 已添加 CHROME_PATH 到 .env"
        fi
    else
        echo "CHROME_PATH=$CHROME_PATH" > .env
        echo -e "  ${GREEN}✓${NC} 已创建 .env 并添加 CHROME_PATH"
    fi
fi

# 安装 Python 依赖
echo "⬇️  安装 Python 依赖..."
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

# 检查 DEEPSEEK_API_KEY 配置
if grep -q "DEEPSEEK_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} DEEPSEEK_API_KEY 已配置"
else
    echo -e "  ${YELLOW}⚠${NC} 请编辑 .env 文件并添加您的 DEEPSEEK_API_KEY"
    echo -e "  ${YELLOW}获取 API Key: https://platform.deepseek.com/${NC}"
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
