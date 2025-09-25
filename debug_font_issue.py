#!/usr/bin/env python3
"""
调试字体大小问题
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_font_directly():
    """直接测试PIL字体功能"""
    print("🔍 直接测试PIL字体功能...")
    
    # 测试不同字体大小
    test_sizes = [16, 44, 72, 111]
    text = "2025-09-25"
    
    for size in test_sizes:
        print(f"\n📝 测试字体大小: {size}px")
        
        try:
            # 尝试系统字体路径
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Times.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf"  # Windows
            ]
            
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        print(f"✅ 成功加载字体: {font_path}")
                        break
                    except Exception as e:
                        print(f"❌ 字体加载失败 {font_path}: {e}")
                        continue
            
            if not font:
                print("⚠️ 使用默认字体")
                font = ImageFont.load_default()
            
            # 创建测试图像
            temp_img = Image.new('RGBA', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 测量文本尺寸
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            print(f"   文本尺寸: {text_width} x {text_height}")
            
            # 创建实际水印
            watermark = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            draw.text((10, 10), text, font=font, fill=(0, 0, 0, 128))
            
            print(f"   水印尺寸: {watermark.size}")
            
            # 保存测试结果
            output_path = f"test_images/_watermark/font_test_{size}px.png"
            watermark.save(output_path)
            print(f"   保存到: {output_path}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def test_watermark_processor():
    """测试水印处理器"""
    print("\n🔍 测试水印处理器...")
    
    from core.watermark import WatermarkProcessor
    
    processor = WatermarkProcessor()
    test_sizes = [16, 44, 72, 111]
    text = "2025-09-25"
    
    for size in test_sizes:
        print(f"\n📝 测试水印处理器字体大小: {size}px")
        
        try:
            watermark = processor.create_text_watermark(
                text=text,
                font_size=size,
                color=(0, 0, 0, 128)
            )
            
            if watermark:
                print(f"✅ 水印创建成功: {watermark.size}")
                
                # 保存测试结果
                output_path = f"test_images/_watermark/processor_test_{size}px.png"
                watermark.save(output_path)
                print(f"   保存到: {output_path}")
            else:
                print("❌ 水印创建失败")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始调试字体大小问题...")
    print("=" * 60)
    
    test_font_directly()
    test_watermark_processor()
    
    print("\n" + "=" * 60)
    print("🎉 字体调试完成！")

if __name__ == "__main__":
    main()