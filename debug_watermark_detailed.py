#!/usr/bin/env python3
"""
详细调试水印处理器
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.watermark import WatermarkProcessor

def debug_watermark_processor():
    """详细调试水印处理器"""
    print("🔍 详细调试水印处理器...")
    
    processor = WatermarkProcessor()
    text = "2025-09-25"
    font_size = 72
    
    print(f"📝 测试文本: '{text}'")
    print(f"📏 测试字体大小: {font_size}px")
    print(f"🎨 默认字体大小: {processor.default_font_size}")
    
    # 直接调用get_font方法
    print("\n🔧 测试get_font方法...")
    font = processor.get_font(font_size=font_size)
    print(f"   字体对象: {font}")
    print(f"   字体类型: {type(font)}")
    
    # 手动测试文本尺寸
    print("\n📐 手动测试文本尺寸...")
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    
    try:
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        print(f"   文本边界框: {bbox}")
        print(f"   文本尺寸: {text_width} x {text_height}")
    except Exception as e:
        print(f"   ❌ 文本尺寸测量失败: {e}")
    
    # 测试create_text_watermark方法
    print("\n🎨 测试create_text_watermark方法...")
    try:
        watermark = processor.create_text_watermark(
            text=text,
            font_size=font_size,
            color=(0, 0, 0, 128)
        )
        
        if watermark:
            print(f"✅ 水印创建成功: {watermark.size}")
            print(f"   水印模式: {watermark.mode}")
            
            # 保存调试结果
            output_path = "test_images/_watermark/debug_detailed.png"
            watermark.save(output_path)
            print(f"   保存到: {output_path}")
        else:
            print("❌ 水印创建失败")
            
    except Exception as e:
        print(f"❌ 水印创建异常: {e}")
        import traceback
        traceback.print_exc()

def test_font_loading():
    """测试字体加载"""
    print("\n🔍 测试字体加载...")
    
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"\n📁 测试字体: {font_path}")
            
            for size in [16, 44, 72, 111]:
                try:
                    font = ImageFont.truetype(font_path, size)
                    print(f"   ✅ 大小 {size}: {font}")
                except Exception as e:
                    print(f"   ❌ 大小 {size}: {e}")

def main():
    """主测试函数"""
    print("🚀 开始详细调试...")
    print("=" * 60)
    
    test_font_loading()
    debug_watermark_processor()
    
    print("\n" + "=" * 60)
    print("🎉 详细调试完成！")

if __name__ == "__main__":
    main()