#!/usr/bin/env python3
"""
直接测试字体渲染
"""

from PIL import Image, ImageDraw, ImageFont
import os

def test_direct_font_rendering():
    """直接测试字体渲染"""
    print("🔍 直接测试字体渲染...")
    
    text = "2025-09-25"
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    
    if not os.path.exists(font_path):
        print("❌ 字体文件不存在")
        return
    
    # 测试不同字体大小
    sizes = [16, 44, 72, 111]
    
    for size in sizes:
        print(f"\n📏 测试字体大小: {size}px")
        
        try:
            # 加载字体
            font = ImageFont.truetype(font_path, size)
            print(f"   字体对象: {font}")
            
            # 创建测试图像
            test_img = Image.new('RGBA', (1000, 200), (255, 255, 255, 255))
            draw = ImageDraw.Draw(test_img)
            
            # 测量文本
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            print(f"   文本边界框: {bbox}")
            print(f"   文本尺寸: {text_width} x {text_height}")
            
            # 绘制文本
            draw.text((10, 10), text, font=font, fill=(0, 0, 0, 255))
            
            # 保存结果
            output_path = f"test_images/_watermark/direct_test_{size}px.png"
            test_img.save(output_path)
            print(f"   保存到: {output_path}")
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

def test_font_info():
    """测试字体信息"""
    print("\n🔍 测试字体信息...")
    
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    
    if not os.path.exists(font_path):
        print("❌ 字体文件不存在")
        return
    
    try:
        # 测试不同大小的字体
        for size in [16, 44, 72, 111]:
            font = ImageFont.truetype(font_path, size)
            print(f"字体大小 {size}: {font}")
            
            # 尝试获取字体信息
            try:
                print(f"   字体路径: {font.path}")
                print(f"   字体大小: {font.size}")
            except AttributeError:
                print("   无法获取字体详细信息")
                
    except Exception as e:
        print(f"❌ 字体信息测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始直接字体测试...")
    print("=" * 60)
    
    test_font_info()
    test_direct_font_rendering()
    
    print("\n" + "=" * 60)
    print("🎉 直接字体测试完成！")

if __name__ == "__main__":
    main()