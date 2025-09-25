#!/usr/bin/env python3
"""
逐步调试水印处理器
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.watermark import WatermarkProcessor

def debug_step_by_step():
    """逐步调试水印处理器的每一步"""
    print("🔍 逐步调试水印处理器...")
    
    processor = WatermarkProcessor()
    text = "2025-09-25"
    font_size = 72
    
    print(f"📝 测试参数:")
    print(f"   文本: '{text}'")
    print(f"   字体大小: {font_size}px")
    print(f"   默认字体大小: {processor.default_font_size}")
    
    # 步骤1: 测试get_font方法
    print(f"\n🔧 步骤1: 调用get_font方法...")
    font = processor.get_font(font_size=font_size)
    print(f"   返回的字体对象: {font}")
    print(f"   字体类型: {type(font)}")
    
    # 检查字体属性
    try:
        print(f"   字体路径: {font.path}")
        print(f"   字体大小: {font.size}")
    except AttributeError:
        print("   ⚠️ 无法获取字体详细信息（可能是默认字体）")
    
    # 步骤2: 手动测试文本尺寸
    print(f"\n📐 步骤2: 手动测试文本尺寸...")
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    print(f"   边界框: {bbox}")
    print(f"   文本尺寸: {text_width} x {text_height}")
    
    # 步骤3: 比较不同字体对象
    print(f"\n🔄 步骤3: 比较不同字体对象...")
    
    # 直接创建字体对象
    direct_font = None
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if os.path.exists(font_path):
        try:
            direct_font = ImageFont.truetype(font_path, font_size)
            print(f"   直接创建的字体: {direct_font}")
            
            # 测试直接创建的字体
            direct_bbox = temp_draw.textbbox((0, 0), text, font=direct_font)
            direct_width = direct_bbox[2] - direct_bbox[0]
            direct_height = direct_bbox[3] - direct_bbox[1]
            print(f"   直接字体文本尺寸: {direct_width} x {direct_height}")
            
        except Exception as e:
            print(f"   ❌ 直接创建字体失败: {e}")
    
    # 步骤4: 检查是否是默认字体问题
    print(f"\n🔍 步骤4: 检查字体类型...")
    default_font = ImageFont.load_default()
    print(f"   默认字体对象: {default_font}")
    print(f"   默认字体类型: {type(default_font)}")
    
    # 测试默认字体
    default_bbox = temp_draw.textbbox((0, 0), text, font=default_font)
    default_width = default_bbox[2] - default_bbox[0]
    default_height = default_bbox[3] - default_bbox[1]
    print(f"   默认字体文本尺寸: {default_width} x {default_height}")
    
    # 比较字体对象
    print(f"\n🔍 步骤5: 字体对象比较...")
    print(f"   processor.get_font() == default_font: {font == default_font}")
    print(f"   processor.get_font() is default_font: {font is default_font}")
    
    if direct_font:
        print(f"   processor.get_font() == direct_font: {font == direct_font}")
        print(f"   processor.get_font() is direct_font: {font is direct_font}")
    
    # 步骤6: 测试完整的create_text_watermark方法
    print(f"\n🎨 步骤6: 测试完整的create_text_watermark方法...")
    try:
        watermark = processor.create_text_watermark(
            text=text,
            font_size=font_size,
            color=(0, 0, 0, 128)
        )
        
        if watermark:
            print(f"✅ 水印创建成功: {watermark.size}")
            
            # 保存调试结果
            output_path = "test_images/_watermark/debug_step_by_step.png"
            watermark.save(output_path)
            print(f"   保存到: {output_path}")
        else:
            print("❌ 水印创建失败")
            
    except Exception as e:
        print(f"❌ 水印创建异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🚀 开始逐步调试...")
    print("=" * 60)
    
    debug_step_by_step()
    
    print("\n" + "=" * 60)
    print("🎉 逐步调试完成！")

if __name__ == "__main__":
    main()