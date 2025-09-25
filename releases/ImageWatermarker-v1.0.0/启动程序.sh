#!/bin/bash

# ImageWatermarker 启动脚本 (macOS/Linux)
# 自动检测Python环境并启动程序

echo "🚀 启动 ImageWatermarker..."

# 函数：检查Python和tkinter
check_python_tkinter() {
    local python_cmd=$1
    echo "🔍 检查 $python_cmd..."
    
    if ! command -v $python_cmd &> /dev/null; then
        echo "❌ $python_cmd 未找到"
        return 1
    fi
    
    # 检查tkinter
    if ! $python_cmd -c "import tkinter" 2>/dev/null; then
        echo "❌ $python_cmd 没有tkinter支持"
        return 1
    fi
    
    echo "✅ $python_cmd 可用且支持tkinter"
    return 0
}

# 尝试不同的Python命令
PYTHON_CMD=""

# 优先尝试系统Python3
if check_python_tkinter "python3"; then
    PYTHON_CMD="python3"
# 尝试系统Python
elif check_python_tkinter "python"; then
    PYTHON_CMD="python"
# 尝试Homebrew Python3
elif check_python_tkinter "/opt/homebrew/bin/python3"; then
    PYTHON_CMD="/opt/homebrew/bin/python3"
# 尝试MacPorts Python3
elif check_python_tkinter "/opt/local/bin/python3"; then
    PYTHON_CMD="/opt/local/bin/python3"
else
    echo ""
    echo "❌ 错误: 未找到支持tkinter的Python环境"
    echo ""
    echo "🔧 解决方案："
    echo "1. 安装支持tkinter的Python:"
    echo "   brew install python-tk"
    echo ""
    echo "2. 或者使用系统Python (如果可用):"
    echo "   /System/Library/Frameworks/Python.framework/Versions/3.*/bin/python3"
    echo ""
    echo "3. 或者从官网下载完整的Python安装包:"
    echo "   https://www.python.org/downloads/"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

echo ""
echo "🎯 使用Python: $PYTHON_CMD"

# 检查依赖
echo "📦 检查依赖包..."
if ! $PYTHON_CMD -c "import PIL" 2>/dev/null; then
    echo "⚠️  警告: 缺少Pillow包，正在尝试安装..."
    $PYTHON_CMD -m pip install Pillow --user
fi

echo ""
echo "🚀 启动程序..."
$PYTHON_CMD main.py

echo ""
echo "程序已退出"
read -p "按回车键关闭窗口..."