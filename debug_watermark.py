#!/usr/bin/env python3
"""
水印功能调试脚本
"""

import sys
import os
sys.path.insert(0, '.')

from core.image_processor import ImageProcessor
from core.watermark import WatermarkProcessor, WatermarkPosition
from PIL import Image

def test_watermark():
    print("🔍 开始水印功能测试...")
    
    # 初始化处理器
    processor = ImageProcessor()
    watermark_proc = WatermarkProcessor()
    
    # 加载测试图片
    test_image_path = 'test_images/H.jpg'
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        return False
    
    try:
        image = Image.open(test_image_path)
        print(f"✅ 图片加载成功: {image.size}")
    except Exception as e:
        print(f"❌ 图片加载失败: {e}")
        return False
    
    try:
        # 创建文本水印
        print("📝 创建文本水印...")
        watermark_image = watermark_proc.create_text_watermark(
            text='DEBUG测试水印',
            font_size=60,
            color=(255, 0, 0, 200)  # 红色，较高透明度
        )
        print(f"✅ 文本水印创建成功: {watermark_image.size}")
        
        # 应用水印到图片
        print("🎨 应用水印到图片...")
        result_image = watermark_proc.apply_watermark(
            base_image=image,
            watermark=watermark_image,
            position=WatermarkPosition.MIDDLE_CENTER
        )
        print(f"✅ 水印应用成功: {result_image.size}")
        
        # 保存结果 - 转换为RGB模式以支持JPEG格式
        output_path = 'test_images/_watermark/debug_watermark_test.jpg'
        if result_image.mode == 'RGBA':
            # 创建白色背景
            rgb_image = Image.new('RGB', result_image.size, (255, 255, 255))
            rgb_image.paste(result_image, mask=result_image.split()[-1])  # 使用alpha通道作为mask
            result_image = rgb_image
        elif result_image.mode != 'RGB':
            result_image = result_image.convert('RGB')
        
        result_image.save(output_path, 'JPEG', quality=95)
        print(f"✅ 保存成功: {output_path}")
        
        # 检查文件
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            original_size = os.path.getsize(test_image_path)
            print(f"📊 原图大小: {original_size:,} bytes")
            print(f"📊 水印图大小: {size:,} bytes")
            print(f"📊 大小变化: {size - original_size:+,} bytes")
            
            # 验证图片可以正常打开
            test_img = Image.open(output_path)
            print(f"✅ 输出图片验证成功: {test_img.size} - {test_img.format}")
            return True
        else:
            print("❌ 输出文件未创建")
            return False
            
    except Exception as e:
        print(f"❌ 水印处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_watermark()
    if success:
        print("\n🎉 水印功能测试成功！")
    else:
        print("\n❌ 水印功能测试失败！")
    
    print("\n请检查输出文件: test_images/_watermark/debug_watermark_test.jpg")