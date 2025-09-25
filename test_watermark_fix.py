#!/usr/bin/env python3
"""
测试修复后的水印处理器
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def create_fixed_text_watermark(text: str, font_size: int = 36, color=(0, 0, 0, 128)):
    """
    修复版本的文本水印创建函数
    """
    print(f"🎨 创建水印: '{text}', 字体大小: {font_size}px")
    
    # 尝试加载系统字体
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/System/Library/Fonts/Arial.ttf",      # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "C:/Windows/Fonts/arial.ttf"            # Windows
    ]
    
    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                print(f"✅ 成功加载字体: {font_path}")
                break
            except Exception as e:
                print(f"❌ 字体加载失败 {font_path}: {e}")
                continue
    
    if not font:
        print("⚠️ 所有系统字体加载失败，使用默认字体")
        font = ImageFont.load_default()
    
    # 创建临时图像来测量文本尺寸
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # 计算文本边界框
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    print(f"📐 文本尺寸: {text_width} x {text_height}")
    
    # 创建水印图像
    padding = 10
    watermark_width = text_width + padding * 2
    watermark_height = text_height + padding * 2
    watermark = Image.new('RGBA', (watermark_width, watermark_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    
    # 绘制文本
    draw.text((padding, padding), text, font=font, fill=color)
    
    print(f"✅ 水印创建成功: {watermark.size}")
    return watermark

def test_fixed_watermark():
    """测试修复后的水印功能"""
    print("🚀 测试修复后的水印功能...")
    
    text = "2025-09-25"
    test_sizes = [16, 44, 72, 111, 200]
    
    for size in test_sizes:
        print(f"\n📏 测试字体大小: {size}px")
        
        try:
            watermark = create_fixed_text_watermark(text, size)
            
            if watermark:
                # 保存测试结果
                output_path = f"test_images/_watermark/fixed_test_{size}px.png"
                watermark.save(output_path)
                print(f"💾 保存到: {output_path}")
            else:
                print("❌ 水印创建失败")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

def test_with_real_image():
    """使用真实图片测试修复后的水印"""
    print("\n🖼️ 使用真实图片测试...")
    
    test_image_path = "test_images/H.jpg"
    if not os.path.exists(test_image_path):
        print("❌ 测试图片不存在")
        return
    
    try:
        # 加载图片
        image = Image.open(test_image_path)
        width, height = image.size
        min_dimension = min(width, height)
        
        # 计算自动字体大小
        auto_font_size = max(8, min(1000, int(min_dimension / 18)))
        
        print(f"📷 图片尺寸: {width}x{height}")
        print(f"📏 自动字体大小: {auto_font_size}px")
        
        # 创建水印
        watermark = create_fixed_text_watermark("2025-09-25", auto_font_size)
        
        if not watermark:
            print("❌ 水印创建失败")
            return
        
        # 应用水印到图片
        # 计算水印位置（右下角）
        margin = 20
        wm_x = width - watermark.size[0] - margin
        wm_y = height - watermark.size[1] - margin
        
        # 创建结果图像
        result = image.copy()
        result.paste(watermark, (wm_x, wm_y), watermark)
        
        # 保存结果
        output_path = "test_images/_watermark/fixed_real_test.jpg"
        result.save(output_path, "JPEG", quality=95)
        
        print(f"✅ 真实图片测试成功")
        print(f"💾 保存到: {output_path}")
        print(f"📝 使用字体大小: {auto_font_size}px")
        
    except Exception as e:
        print(f"❌ 真实图片测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🚀 开始测试修复后的水印功能...")
    print("=" * 60)
    
    test_fixed_watermark()
    test_with_real_image()
    
    print("\n" + "=" * 60)
    print("🎉 修复测试完成！")

if __name__ == "__main__":
    main()