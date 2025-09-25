#!/usr/bin/env python3
"""
测试字体大小自动调整功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.image_processor import ImageProcessor
from core.watermark import WatermarkProcessor
from PIL import Image

def test_auto_font_size():
    """测试自动字体大小计算"""
    print("🔍 测试字体大小自动调整功能...")
    
    # 测试不同尺寸的图片
    test_cases = [
        ("小图片", (400, 300)),
        ("中等图片", (1200, 800)),
        ("大图片", (3000, 2000)),
        ("超大图片", (6000, 4000)),
        ("竖向图片", (800, 1200)),
        ("方形图片", (1000, 1000))
    ]
    
    watermark_processor = WatermarkProcessor()
    
    for name, size in test_cases:
        width, height = size
        min_dimension = min(width, height)
        
        # 模拟自动字体大小计算逻辑
        auto_font_size = max(8, min(1000, int(min_dimension / 18)))
        
        print(f"📐 {name} ({width}x{height}):")
        print(f"   - 最小边: {min_dimension}px")
        print(f"   - 自动字体大小: {auto_font_size}px")
        print(f"   - 字体大小占比: {auto_font_size/min_dimension*100:.1f}%")
        
        # 测试创建水印
        try:
            watermark = watermark_processor.create_text_watermark(
                text="2025-09-25",
                font_size=auto_font_size,
                color=(0, 0, 0, 128)
            )
            if watermark:
                print(f"   ✅ 水印创建成功: {watermark.size}")
            else:
                print(f"   ❌ 水印创建失败")
        except Exception as e:
            print(f"   ❌ 水印创建异常: {e}")
        
        print()

def test_font_size_limits():
    """测试字体大小限制"""
    print("🔍 测试字体大小限制...")
    
    watermark_processor = WatermarkProcessor()
    
    # 测试边界值
    test_sizes = [1, 8, 50, 100, 500, 1000, 1500]
    
    for size in test_sizes:
        try:
            watermark = watermark_processor.create_text_watermark(
                text="测试",
                font_size=size,
                color=(0, 0, 0, 128)
            )
            if watermark:
                print(f"✅ 字体大小 {size}: 成功 - {watermark.size}")
            else:
                print(f"❌ 字体大小 {size}: 失败")
        except Exception as e:
            print(f"❌ 字体大小 {size}: 异常 - {e}")

def test_with_real_image():
    """使用真实图片测试"""
    print("🔍 使用真实图片测试...")
    
    test_image_path = "test_images/H.jpg"
    if not os.path.exists(test_image_path):
        print("❌ 测试图片不存在，跳过真实图片测试")
        return
    
    try:
        # 加载图片
        image_processor = ImageProcessor()
        watermark_processor = WatermarkProcessor()
        
        image_data = image_processor.load_image(test_image_path)
        if not image_data:
            print("❌ 图片加载失败")
            return
        
        image = image_data['image']
        width, height = image.size
        min_dimension = min(width, height)
        
        # 计算自动字体大小
        auto_font_size = max(8, min(1000, int(min_dimension / 18)))
        
        print(f"📷 真实图片测试:")
        print(f"   - 图片尺寸: {width}x{height}")
        print(f"   - 最小边: {min_dimension}px")
        print(f"   - 自动字体大小: {auto_font_size}px")
        
        # 创建水印
        watermark = watermark_processor.create_text_watermark(
            text="2025-09-25",
            font_size=auto_font_size,
            color=(0, 0, 0, 128)
        )
        
        if not watermark:
            print("❌ 水印创建失败")
            return
        
        print(f"✅ 水印创建成功: {watermark.size}")
        
        # 应用水印
        result = watermark_processor.apply_watermark(
            image, watermark, 
            position="bottom_right",
            margin=20
        )
        
        if not result:
            print("❌ 水印应用失败")
            return
        
        print(f"✅ 水印应用成功: {result.size}")
        
        # 保存测试结果
        output_path = "test_images/_watermark/auto_font_size_test.jpg"
        success = image_processor.save_image(result, output_path, "JPEG", 95)
        
        if success:
            print(f"✅ 保存成功: {output_path}")
            print(f"📝 字体大小: {auto_font_size}px")
        else:
            print("❌ 保存失败")
            
    except Exception as e:
        print(f"❌ 真实图片测试失败: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试字体大小自动调整功能...")
    print("=" * 60)
    
    test_auto_font_size()
    print("=" * 60)
    test_font_size_limits()
    print("=" * 60)
    test_with_real_image()
    
    print("\n" + "=" * 60)
    print("🎉 字体大小自动调整功能测试完成！")

if __name__ == "__main__":
    main()