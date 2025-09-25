#!/usr/bin/env python3
"""
调试字体加载过程
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.watermark import WatermarkProcessor

def debug_font_loading_process():
    """调试字体加载过程"""
    print("🔍 调试字体加载过程...")
    
    font_size = 72
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/System/Library/Fonts/Arial.ttf",      # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "C:/Windows/Fonts/arial.ttf"            # Windows
    ]
    
    print(f"📏 目标字体大小: {font_size}px")
    
    for font_path in font_paths:
        print(f"\n📁 测试字体路径: {font_path}")
        print(f"   文件存在: {os.path.exists(font_path)}")
        
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                print(f"   ✅ 加载成功: {font}")
                print(f"   字体大小: {font.size}")
                print(f"   字体路径: {font.path}")
                
                # 测试文本渲染
                temp_img = Image.new('RGBA', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                bbox = temp_draw.textbbox((0, 0), "2025-09-25", font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                print(f"   文本尺寸: {text_width} x {text_height}")
                
                break  # 成功加载，退出循环
                
            except Exception as e:
                print(f"   ❌ 加载失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ❌ 文件不存在")

def debug_watermark_processor_get_font():
    """调试水印处理器的get_font方法"""
    print("\n🔍 调试水印处理器的get_font方法...")
    
    processor = WatermarkProcessor()
    font_size = 72
    
    print(f"📏 请求字体大小: {font_size}px")
    
    # 手动模拟get_font方法的逻辑
    print("\n🔧 手动模拟get_font逻辑...")
    
    try:
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/System/Library/Fonts/Arial.ttf",      # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf"            # Windows
        ]
        
        font = None
        for font_path in font_paths:
            print(f"   尝试加载: {font_path}")
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"   ✅ 成功加载: {font}")
                    print(f"   字体大小: {font.size}")
                    break
                except Exception as e:
                    print(f"   ❌ 加载失败: {e}")
                    continue
            else:
                print(f"   ❌ 文件不存在")
        
        if not font:
            print("   ⚠️ 所有系统字体加载失败，使用默认字体")
            font = ImageFont.load_default()
            print(f"   默认字体: {font}")
            try:
                print(f"   默认字体大小: {font.size}")
            except:
                print("   无法获取默认字体大小")
        
        # 现在调用实际的get_font方法
        print(f"\n🎯 调用实际的get_font方法...")
        actual_font = processor.get_font(font_size=font_size)
        print(f"   实际返回的字体: {actual_font}")
        try:
            print(f"   实际字体大小: {actual_font.size}")
            print(f"   实际字体路径: {actual_font.path}")
        except:
            print("   无法获取实际字体详细信息")
        
        # 比较两个字体对象
        print(f"\n🔍 比较字体对象...")
        print(f"   手动创建 == 实际返回: {font == actual_font}")
        print(f"   手动创建 is 实际返回: {font is actual_font}")
        
    except Exception as e:
        print(f"❌ 调试过程异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🚀 开始调试字体加载过程...")
    print("=" * 60)
    
    debug_font_loading_process()
    debug_watermark_processor_get_font()
    
    print("\n" + "=" * 60)
    print("🎉 字体加载调试完成！")

if __name__ == "__main__":
    main()