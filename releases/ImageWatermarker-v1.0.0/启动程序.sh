#!/bin/bash
echo "ImageWatermarker v1.0.0"
echo "================================"
echo "正在启动程序..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8或更高版本"
    echo "macOS: brew install python3"
    echo "Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

# 安装依赖
echo "正在检查依赖包..."
pip3 install -r requirements.txt

# 启动程序
echo "启动 ImageWatermarker..."
python3 main.py
