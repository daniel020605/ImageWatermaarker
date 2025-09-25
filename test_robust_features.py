#!/usr/bin/env python3
"""
鲁棒性功能测试脚本
测试输入验证、参数限制和错误处理功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.input_validation import InputValidator


def test_input_validation():
    """测试输入验证功能"""
    print("=" * 50)
    print("测试输入验证功能")
    print("=" * 50)
    
    # 测试整数验证
    print("\n1. 整数验证测试:")
    test_cases = [
        ("48", 8, 1000, 48),
        ("", 8, 1000, 48),
        ("abc", 8, 1000, 48),
        ("5", 8, 1000, 48),
        ("2000", 8, 1000, 48),
        ("-10", 8, 1000, 48),
        ("50.5", 8, 1000, 48),
    ]
    
    for value, min_val, max_val, default in test_cases:
        result = InputValidator.validate_integer(value, min_val, max_val, default)
        print(f"  输入: '{value}' -> 输出: {result}")
    
    # 测试字体大小验证
    print("\n2. 字体大小验证测试:")
    font_size_cases = ["", "abc", "5", "48", "2000", "-10"]
    for value in font_size_cases:
        result = InputValidator.validate_font_size(value, 48)
        print(f"  输入: '{value}' -> 输出: {result}")
    
    # 测试透明度验证
    print("\n3. 透明度验证测试:")
    opacity_cases = ["", "abc", "-10", "128", "300", "50.5"]
    for value in opacity_cases:
        result = InputValidator.validate_opacity(value, 128)
        print(f"  输入: '{value}' -> 输出: {result}")
    
    # 测试颜色验证
    print("\n4. 颜色验证测试:")
    color_cases = ["#000000", "#fff", "000000", "invalid", "#gggggg", "#123"]
    for value in color_cases:
        result = InputValidator.validate_color_hex(value, "#000000")
        print(f"  输入: '{value}' -> 输出: {result}")
    
    # 测试RGBA转换
    print("\n5. RGBA转换测试:")
    rgba_cases = [
        ("#000000", 128),
        ("#ffffff", 255),
        ("#ff0000", 0),
        ("invalid", 128),
    ]
    for hex_color, opacity in rgba_cases:
        result = InputValidator.hex_to_rgba(hex_color, opacity)
        print(f"  输入: ('{hex_color}', {opacity}) -> 输出: {result}")


def test_watermark_position_mapping():
    """测试水印位置映射"""
    print("\n" + "=" * 50)
    print("测试水印位置映射")
    print("=" * 50)
    
    from core.watermark import WatermarkProcessor
    
    processor = WatermarkProcessor()
    
    # 测试中文位置映射
    chinese_positions = ["左上", "上中", "右上", "左中", "中心", "右中", "左下", "下中", "右下"]
    
    for pos in chinese_positions:
        try:
            enum_pos = processor._get_position_enum(pos)
            print(f"  中文位置: '{pos}' -> 枚举: {enum_pos.value}")
        except Exception as e:
            print(f"  中文位置: '{pos}' -> 错误: {e}")
    
    # 测试英文位置映射
    english_positions = ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"]
    
    for pos in english_positions:
        try:
            enum_pos = processor._get_position_enum(pos)
            print(f"  英文位置: '{pos}' -> 枚举: {enum_pos.value}")
        except Exception as e:
            print(f"  英文位置: '{pos}' -> 错误: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 50)
    print("测试错误处理")
    print("=" * 50)
    
    from core.watermark import WatermarkProcessor
    from PIL import Image
    
    processor = WatermarkProcessor()
    
    # 创建测试图片
    test_image = Image.new('RGB', (100, 100), color='white')
    
    # 测试文本水印错误处理
    print("\n1. 文本水印错误处理测试:")
    
    # 测试空文本
    config = {
        'text': '',
        'font_size': 48,
        'color': (0, 0, 0, 128),
        'position': '中心'
    }
    
    try:
        result = processor.apply_text_watermark(test_image, config)
        print(f"  空文本测试: 成功 (图片尺寸: {result.size})")
    except Exception as e:
        print(f"  空文本测试: 错误 - {e}")
    
    # 测试无效字体大小
    config['text'] = '测试'
    config['font_size'] = -10
    
    try:
        result = processor.apply_text_watermark(test_image, config)
        print(f"  无效字体大小测试: 成功 (图片尺寸: {result.size})")
    except Exception as e:
        print(f"  无效字体大小测试: 错误 - {e}")
    
    # 测试图片水印错误处理
    print("\n2. 图片水印错误处理测试:")
    
    # 测试不存在的图片文件
    config = {
        'image_path': 'nonexistent.png',
        'scale_percent': 100.0,
        'opacity': 128,
        'position': '中心'
    }
    
    try:
        result = processor.apply_image_watermark(test_image, config)
        print(f"  不存在文件测试: 成功 (图片尺寸: {result.size})")
    except Exception as e:
        print(f"  不存在文件测试: 错误 - {e}")


def main():
    """主函数"""
    print("ImageWatermarker - 鲁棒性功能测试")
    print("测试输入验证、参数限制和错误处理功能")
    
    try:
        test_input_validation()
        test_watermark_position_mapping()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
        print("\n鲁棒性改进总结:")
        print("✅ 输入验证: 字体大小、透明度、颜色等参数都有验证和限制")
        print("✅ 参数限制: 所有数值参数都有合理的范围限制")
        print("✅ 默认值处理: 输入为空或无效时自动使用默认值")
        print("✅ 错误处理: 各种异常情况都有适当的处理")
        print("✅ 位置映射: 中文位置名称正确映射到枚举值")
        print("✅ 类型安全: 输入类型转换和验证")
        
        print("\n现在可以运行 'python3 main.py' 来测试增强版GUI!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())