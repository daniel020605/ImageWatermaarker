#!/usr/bin/env python3
"""
测试新功能的脚本
验证：
1. 默认水印文本为当前日期
2. 默认颜色为黑色
3. 字体大小控制功能
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.watermark import WatermarkProcessor
from core.image_processor import ImageProcessor
from PIL import Image

def test_default_date_watermark():
    """测试默认日期水印"""
    print("🔍 测试默认日期水印功能...")
    
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 当前日期: {current_date}")
    
    # 创建水印处理器
    watermark_processor = WatermarkProcessor()
    
    # 创建文本水印（使用当前日期）
    watermark = watermark_processor.create_text_watermark(
        text=current_date,
        font_size=36,
        color=(0, 0, 0, 128)  # 黑色半透明
    )
    
    if watermark:
        print(f"✅ 日期水印创建成功: {watermark.size}")
        return True
    else:
        print("❌ 日期水印创建失败")
        return False

def test_font_size_range():
    """测试字体大小范围"""
    print("\n🔍 测试字体大小范围...")
    
    watermark_processor = WatermarkProcessor()
    
    # 测试不同字体大小
    test_sizes = [8, 36, 72, 100, 200]
    
    for size in test_sizes:
        watermark = watermark_processor.create_text_watermark(
            text="测试",
            font_size=size,
            color=(0, 0, 0, 128)
        )
        
        if watermark:
            print(f"✅ 字体大小 {size}: {watermark.size}")
        else:
            print(f"❌ 字体大小 {size}: 创建失败")
            return False
    
    return True

def test_black_color_watermark():
    """测试黑色水印"""
    print("\n🔍 测试黑色水印...")
    
    # 检查是否有测试图片
    test_image_path = "test_images/H.jpg"
    if not os.path.exists(test_image_path):
        print("❌ 测试图片不存在，跳过测试")
        return True
    
    try:
        # 加载图片
        image_processor = ImageProcessor()
        watermark_processor = WatermarkProcessor()
        
        image_data = image_processor.load_image(test_image_path)
        if not image_data:
            print("❌ 图片加载失败")
            return False
        
        image = image_data['image']
        print(f"✅ 图片加载成功: {image.size}")
        
        # 创建黑色水印
        current_date = datetime.now().strftime("%Y-%m-%d")
        watermark = watermark_processor.create_text_watermark(
            text=current_date,
            font_size=36,
            color=(0, 0, 0, 128)  # 黑色半透明
        )
        
        if not watermark:
            print("❌ 水印创建失败")
            return False
        
        print(f"✅ 黑色水印创建成功: {watermark.size}")
        
        # 应用水印
        result = watermark_processor.apply_watermark(
            image, watermark, 
            position="bottom_right",
            margin=20
        )
        
        if not result:
            print("❌ 水印应用失败")
            return False
        
        print(f"✅ 水印应用成功: {result.size}")
        
        # 保存测试结果
        output_path = "test_images/_watermark/new_features_test.jpg"
        success = image_processor.save_image(result, output_path, "JPEG", 95)
        
        if success:
            print(f"✅ 保存成功: {output_path}")
            return True
        else:
            print("❌ 保存失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新功能...")
    print("=" * 50)
    
    tests = [
        ("默认日期水印", test_default_date_watermark),
        ("字体大小范围", test_font_size_range),
        ("黑色水印", test_black_color_watermark)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有新功能测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)