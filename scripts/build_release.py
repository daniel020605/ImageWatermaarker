#!/usr/bin/env python3
"""
ImageWatermarker Release Build Script
用于创建发布版本的打包脚本
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# 项目信息
PROJECT_NAME = "ImageWatermarker"
VERSION = "1.0.0"
AUTHOR = "CodeBuddy"

def create_release_package():
    """创建发布包"""
    print(f"🚀 开始构建 {PROJECT_NAME} v{VERSION} 发布包...")
    
    # 项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 创建发布目录
    release_dir = project_root / "releases"
    release_dir.mkdir(exist_ok=True)
    
    # 发布包名称
    release_name = f"{PROJECT_NAME}-v{VERSION}"
    release_path = release_dir / release_name
    
    # 清理旧的发布目录
    if release_path.exists():
        shutil.rmtree(release_path)
    
    release_path.mkdir()
    
    print(f"📁 创建发布目录: {release_path}")
    
    # 需要包含的文件和目录
    include_items = [
        "main.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "需求文档.md",
        "使用指南.md",
        "项目总结.md",
        "core/",
        "gui/",
        "utils/",
        "templates/",
        "test_images/",
        "test_watermark.py"
    ]
    
    # 复制文件到发布目录
    for item in include_items:
        src_path = project_root / item
        dst_path = release_path / item
        
        if src_path.exists():
            if src_path.is_file():
                # 复制文件
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                print(f"✅ 复制文件: {item}")
            elif src_path.is_dir():
                # 复制目录
                shutil.copytree(src_path, dst_path, ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', '*.pyo', '.DS_Store', 'Thumbs.db'
                ))
                print(f"✅ 复制目录: {item}")
        else:
            print(f"⚠️  文件不存在: {item}")
    
    # 创建启动脚本
    create_startup_scripts(release_path)
    
    # 创建安装说明
    create_install_guide(release_path)
    
    # 创建ZIP压缩包
    zip_path = release_dir / f"{release_name}.zip"
    create_zip_package(release_path, zip_path)
    
    print(f"🎉 发布包创建完成!")
    print(f"📦 发布目录: {release_path}")
    print(f"📦 压缩包: {zip_path}")
    
    return release_path, zip_path

def create_startup_scripts(release_path):
    """创建启动脚本"""
    print("📝 创建启动脚本...")
    
    # Windows 批处理文件
    bat_content = f"""@echo off
echo {PROJECT_NAME} v{VERSION}
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
echo 启动 {PROJECT_NAME}...
python main.py

pause
"""
    
    with open(release_path / "启动程序.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    # macOS/Linux Shell脚本
    sh_content = f"""#!/bin/bash
echo "{PROJECT_NAME} v{VERSION}"
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
echo "启动 {PROJECT_NAME}..."
python3 main.py
"""
    
    sh_path = release_path / "启动程序.sh"
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(sh_content)
    
    # 设置执行权限
    try:
        os.chmod(sh_path, 0o755)
    except:
        pass
    
    print("✅ 启动脚本创建完成")

def create_install_guide(release_path):
    """创建安装说明"""
    print("📝 创建安装说明...")
    
    install_guide = f"""# {PROJECT_NAME} v{VERSION} 安装说明

## 系统要求
- Python 3.8 或更高版本
- 支持的操作系统: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 快速开始

### Windows 用户
1. 双击运行 `启动程序.bat`
2. 程序会自动安装依赖并启动

### macOS/Linux 用户
1. 打开终端，进入程序目录
2. 运行: `./启动程序.sh`
3. 或者手动执行:
   ```bash
   pip3 install -r requirements.txt
   python3 main.py
   ```

## 手动安装步骤

1. **安装Python**
   - Windows: 从 https://www.python.org/downloads/ 下载安装
   - macOS: `brew install python3`
   - Ubuntu: `sudo apt install python3 python3-pip`

2. **安装依赖包**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python3 main.py
   ```

## 功能特点
- 🖼️ 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
- 🎨 文本水印自定义 (文字、大小、颜色、透明度)
- 📍 九宫格位置布局
- 👀 实时预览效果
- 📦 批量图片处理
- 💾 水印模板管理
- ⚙️ 灵活导出设置

## 使用帮助
详细使用说明请参考 `使用指南.md` 文件。

## 技术支持
如遇问题请查看:
1. `README.md` - 项目说明
2. `使用指南.md` - 详细使用方法
3. `需求文档.md` - 功能说明

---
{PROJECT_NAME} v{VERSION} - {datetime.now().strftime('%Y-%m-%d')}
"""
    
    with open(release_path / "安装说明.txt", "w", encoding="utf-8") as f:
        f.write(install_guide)
    
    print("✅ 安装说明创建完成")

def create_zip_package(release_path, zip_path):
    """创建ZIP压缩包"""
    print(f"📦 创建压缩包: {zip_path.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_path):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(release_path.parent)
                zipf.write(file_path, arc_path)
    
    # 显示压缩包信息
    zip_size = zip_path.stat().st_size
    print(f"✅ 压缩包创建完成 ({zip_size / 1024 / 1024:.1f} MB)")

def main():
    """主函数"""
    try:
        release_path, zip_path = create_release_package()
        
        print("\n" + "="*50)
        print("🎉 发布包构建完成!")
        print(f"📁 发布目录: {release_path}")
        print(f"📦 压缩包: {zip_path}")
        print("\n📋 下一步:")
        print("1. 测试发布包是否正常工作")
        print("2. 上传到GitHub Releases")
        print("3. 更新项目文档")
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())