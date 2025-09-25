#!/usr/bin/env python3
"""
验证默认水印文本是否为当天日期
"""

import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window_complete import MainWindow

def verify_default_date():
    """验证默认日期设置"""
    print("🔍 验证默认水印文本设置...")
    
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 当前日期: {current_date}")
    
    # 创建主窗口实例（不显示GUI）
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 创建MainWindow实例
        app = MainWindow()
        app.root.withdraw()  # 隐藏应用窗口
        
        # 获取默认水印文本
        default_text = app.var_watermark_text.get()
        print(f"🏷️  默认水印文本: '{default_text}'")
        
        # 验证是否匹配
        if default_text == current_date:
            print("✅ 验证成功：默认水印文本已正确设置为当天日期！")
            return True
        else:
            print(f"❌ 验证失败：期望 '{current_date}'，实际 '{default_text}'")
            return False
            
    except Exception as e:
        print(f"❌ 验证过程中出错: {str(e)}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def main():
    """主函数"""
    print("🚀 开始验证默认日期水印设置...")
    print("=" * 50)
    
    success = verify_default_date()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 验证完成：默认水印文本已正确设置为当天日期！")
        print(f"📝 当前设置: {datetime.now().strftime('%Y-%m-%d')}")
    else:
        print("⚠️  验证失败，请检查设置")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)