@echo off
echo ImageWatermarker v1.0.0
echo ================================
echo 正在启动程序...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 安装依赖
echo 正在检查依赖包...
pip install -r requirements.txt

REM 启动程序
echo 启动 ImageWatermarker...
python main.py

pause
