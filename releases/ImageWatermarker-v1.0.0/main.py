#!/usr/bin/env python3
"""
ImageWatermarker - 图片水印工具
主程序入口

使用方法:
python main.py

功能特点:
- 支持批量添加文本水印
- 支持多种图片格式 (JPEG, PNG, BMP, TIFF)
- 实时预览效果
- 九宫格位置设置
- 模板保存和管理
- 灵活的导出设置

作者: CodeBuddy
版本: 1.0
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("错误: 无法导入tkinter模块")
    print("请确保Python安装时包含了tkinter支持")
    sys.exit(1)

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    print("错误: 无法导入Pillow模块")
    print("请运行以下命令安装依赖:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# 导入应用程序主窗口
try:
    from gui.main_window_complete import MainWindow
except ImportError as e:
    print(f"错误: 无法导入主窗口模块: {e}")
    print("请确保所有模块文件都存在")
    sys.exit(1)


def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    # 检查必需的模块
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        from PIL import Image, ImageTk, ImageDraw, ImageFont
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("缺少以下依赖项:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def create_directories():
    """创建必要的目录"""
    directories = [
        "templates",
        "temp",
        "logs"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)


def main():
    """主函数"""
    print("ImageWatermarker - 图片水印工具")
    print("=" * 40)
    
    # 检查依赖项
    if not check_dependencies():
        return 1
    
    # 创建必要的目录
    create_directories()
    
    try:
        # 创建并运行主窗口
        print("正在启动应用程序...")
        app = MainWindow()
        
        # 设置应用程序图标（如果存在）
        icon_path = project_root / "icon.ico"
        if icon_path.exists():
            try:
                app.root.iconbitmap(str(icon_path))
            except Exception:
                pass  # 忽略图标加载错误
        
        print("应用程序已启动")
        app.run()
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 0
    
    except Exception as e:
        print(f"程序运行时发生错误: {e}")
        
        # 显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror(
                "程序错误", 
                f"程序运行时发生错误:\n\n{str(e)}\n\n请检查控制台输出获取更多信息。"
            )
            root.destroy()
        except Exception:
            pass  # 如果连错误对话框都无法显示，就忽略
        
        return 1
    
    print("程序正常退出")
    return 0


if __name__ == "__main__":
    sys.exit(main())