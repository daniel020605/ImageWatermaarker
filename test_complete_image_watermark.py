#!/usr/bin/env python3
"""
完整的图片水印功能测试
"""

import os
import tkinter as tk
from gui.main_window_image_watermark import MainWindow

def test_complete_image_watermark():
    """测试完整的图片水印功能"""
    print("🚀 启动完整的图片水印功能测试...")
    print("=" * 60)
    print("📋 测试功能:")
    print("✅ 文本水印功能")
    print("✅ 图片水印功能")
    print("✅ 水印类型切换")
    print("✅ 实时预览")
    print("✅ 批量导出")
    print("=" * 60)
    print("🎯 使用说明:")
    print("1. 点击'导入图片'或'导入文件夹'添加图片")
    print("2. 选择'文本水印'或'图片水印'")
    print("3. 对于图片水印，点击'选择图片'选择水印图片")
    print("4. 调整水印参数（大小、透明度、位置）")
    print("5. 在预览区域查看效果")
    print("6. 选择输出目录并点击'批量导出'")
    print("=" * 60)
    
    # 创建主窗口
    root = tk.Tk()
    app = MainWindow(root)
    
    # 启动应用
    root.mainloop()

if __name__ == "__main__":
    test_complete_image_watermark()